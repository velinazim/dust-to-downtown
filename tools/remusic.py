#!/usr/bin/env python3
"""Swap the soundtrack of already-uploaded but not-yet-public videos for the current tools/music.py style.

  python3 tools/remusic.py <repo>          # runs inside the "Re-music scheduled videos" action (needs YT + GH tokens)
  python3 tools/remusic.py <repo> --dry    # only list what would be replaced

Owner request 9.11.2026: the old ambient pad music was grating; every scheduled (private) video gets the new soft
piano. No re-render: the finished video is taken from the episode-<slug> / shorts-<slug> artifact (kept 30 days),
the audio track is replaced (video stream copied), and the result is uploaded as a NEW private video with the SAME
publish time, playlist and thumbnail. Only after the upload succeeded is the old video taken off the schedule (it stays
private; the owner deletes it in Studio). Shorts get their "Full episode" link pointed at the new long video.

Order: soonest publish time first, so a long episode is always swapped before its Shorts. Videos going live within
the next 60 minutes are left alone. On a quota / upload-limit error the run stops cleanly; the daily schedule
continues the next day. Every swap is committed to uploads.json right away (marker "music": MUSIC_TAG).
"""
import datetime as dt, glob, json, os, shutil, subprocess, sys, zipfile
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import music, yt_api  # noqa: E402

MUSIC_TAG = 'piano-2026-11-09'
GH = 'https://api.github.com'
WORK = os.environ.get('REMUSIC_WORK', '/tmp/remusic')


def utc(s):
    return dt.datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=dt.timezone.utc)


def pending(uploads, now):
    out = []
    for u in uploads:
        if u.get('music') == MUSIC_TAG or u['key'].endswith(':replaced') or u.get('deleted') or not u.get('publish_at'):
            continue
        if utc(u['publish_at']) > now + dt.timedelta(minutes=60):
            out.append(u)
    return sorted(out, key=lambda u: u['publish_at'])


def artifact_dir(repo_slug, name):
    """Download + unzip the newest non-expired artifact <name> (once per run)."""
    d = os.path.join(WORK, name)
    if os.path.isdir(d):
        return d
    h = {'Authorization': f'Bearer {os.environ["GH_TOKEN"]}', 'Accept': 'application/vnd.github+json'}
    arts = requests.get(f'{GH}/repos/{repo_slug}/actions/artifacts', params={'name': name, 'per_page': 20}, headers=h, timeout=60).json()['artifacts']
    arts = sorted((a for a in arts if not a['expired']), key=lambda a: a['created_at'], reverse=True)
    if not arts:
        raise RuntimeError(f'artifact {name} not found or expired')
    os.makedirs(WORK, exist_ok=True)
    z = os.path.join(WORK, name + '.zip')
    with requests.get(arts[0]['archive_download_url'], headers=h, stream=True, timeout=3600) as r:
        r.raise_for_status()
        with open(z, 'wb') as f:
            for chunk in r.iter_content(1 << 22):
                f.write(chunk)
    with zipfile.ZipFile(z) as zf:   # only the English uploads are needed
        zf.extractall(d, [m for m in zf.namelist() if '/en/' in '/' + m])
    os.remove(z)
    print(f'artifact {name}: run {arts[0]["workflow_run"]["id"]} ({arts[0]["created_at"]})', flush=True)
    return d


def episode_dir(repo, repo_slug, u):
    if u['kind'] == 'long':
        return os.path.join(artifact_dir(repo_slug, f'episode-{u["slug"]}'), 'en')
    sid = u['key'].split(':short:')[1]
    return os.path.join(artifact_dir(repo_slug, f'shorts-{u["slug"]}'), sid, 'en')


def seed_for(repo, u):
    city = json.load(open(os.path.join(repo, 'cities', u['slug'], 'city.json')))
    if u['kind'] == 'long':
        return city.get('seed', 7)
    shorts = json.load(open(os.path.join(repo, 'cities', u['slug'], 'shorts.json')))['shorts']
    sid = u['key'].split(':short:')[1]
    i, sh = next((i, s) for i, s in enumerate(shorts) if s['id'] == sid)
    return sh.get('seed', city.get('seed', 7) * 10 + i + 1)


def duration(path):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path],
                                check=True, capture_output=True, text=True).stdout)


def rebuild(src_dir, out_dir, seed, uploads):
    meta = json.load(open(os.path.join(src_dir, 'meta.json')))
    os.makedirs(out_dir, exist_ok=True)
    src = os.path.join(src_dir, meta['file'])
    dur = duration(src)
    wav = os.path.join(out_dir, 'music.wav')
    music.main(dur + 1, wav, seed)
    dst = os.path.join(out_dir, 'video.mp4')
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', src, '-i', wav, '-map', '0:v', '-map', '1:a', '-c:v', 'copy',
                    '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', dst], check=True)
    os.remove(wav)
    d2 = duration(dst)
    if abs(d2 - dur) > 1.0:
        raise RuntimeError(f'duration changed {dur:.1f} -> {d2:.1f}')
    a = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'a', '-show_entries', 'stream=codec_name', '-of', 'csv=p=0', dst],
                       capture_output=True, text=True).stdout.strip()
    if not a:
        raise RuntimeError('no audio stream in rebuilt video')
    # links to long videos that were swapped (a Short's "Full episode" line) -> the new video
    txt = json.dumps(meta, ensure_ascii=False)
    for old in uploads:
        if old.get('replaced_by') and old['kind'] == 'long':
            txt = txt.replace(f'https://youtu.be/{old["video_id"]}', f'https://youtu.be/{old["replaced_by"]}')
    meta = json.loads(txt)
    meta['file'] = 'video.mp4'
    if meta.get('thumb') and os.path.exists(os.path.join(src_dir, meta['thumb'])):
        shutil.copy(os.path.join(src_dir, meta['thumb']), os.path.join(out_dir, meta['thumb']))
    json.dump(meta, open(os.path.join(out_dir, 'meta.json'), 'w'), indent=1, ensure_ascii=False)
    print(f'  rebuilt {dur:.1f}s, audio {a}', flush=True)
    return meta


def git(repo, *args):
    return subprocess.run(['git', '-C', repo, *args]).returncode == 0


def save(repo, msg, apply, line):
    """Apply the change on top of the newest main and push (other workflows also write uploads.json)."""
    up_path = os.path.join(repo, 'uploads.json')
    for attempt in range(6):
        git(repo, 'fetch', '-q', 'origin', 'main'); git(repo, 'reset', '-q', '--hard', 'origin/main')
        uploads = json.load(open(up_path))
        apply(uploads)
        json.dump(uploads, open(up_path, 'w'), indent=1, ensure_ascii=False)
        log_line(repo, line)
        git(repo, 'add', 'uploads.json', 'remusic_log.md')
        git(repo, '-c', 'user.name=Dust to Downtown bot', '-c', 'user.email=velinazim0776@gmail.com', 'commit', '-qm', msg)
        if git(repo, 'push', '-q', 'origin', 'HEAD:main'):
            return True
        subprocess.run(['sleep', str(5 + 5 * attempt)])
    print('WARNING: could not push the record for', msg)
    return False


def log_line(repo, line):
    p = os.path.join(repo, 'remusic_log.md')
    new = not os.path.exists(p)
    with open(p, 'a') as f:
        if new:
            f.write('# Müzik değişimi (yeni piyano) — yapılan değişimler\n\n')
        f.write(line + '\n')


def free_artifacts(rest):
    need = {(f'episode-{u["slug"]}' if u['kind'] == 'long' else f'shorts-{u["slug"]}') for u in rest}
    for d in glob.glob(os.path.join(WORK, '*-*')):
        if os.path.isdir(d) and os.path.basename(d) not in need and os.path.basename(d) != 'out':
            shutil.rmtree(d, ignore_errors=True)


def main(repo, dry=False):
    up_path = os.path.join(repo, 'uploads.json')
    uploads = json.load(open(up_path))
    now = dt.datetime.now(dt.timezone.utc)
    todo = pending(uploads, now)
    print(f'{len(todo)} scheduled video(s) still have the old music:')
    for u in todo:
        print(' ', u['publish_at'], u['key'], u['video_id'])
    if dry or not todo:
        return
    repo_slug = os.environ.get('GITHUB_REPOSITORY', 'velinazim/dust-to-downtown')
    tok = yt_api.token()
    yt_api.check_channel(tok, repo)
    done_n = 0
    for u0 in todo:
        uploads = json.load(open(up_path))
        u = next(x for x in uploads if x['key'] == u0['key'] and x['video_id'] == u0['video_id'])
        if utc(u['publish_at']) <= dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=60):
            print('too close to going live, left as is:', u['key']); continue
        print(f'== {u["key"]} ({u["video_id"]}, live {u["publish_at"]})', flush=True)
        try:
            src = episode_dir(repo, repo_slug, u)
            out = os.path.join(WORK, 'out', u['key'].replace(':', '_'))
            meta = rebuild(src, out, seed_for(repo, u), uploads)
        except Exception as e:
            print('  SKIPPED (could not rebuild):', e, flush=True)
            continue
        try:
            vid = yt_api.upload_video(tok, os.path.join(out, 'video.mp4'), meta, u['publish_at'])
        except RuntimeError as e:
            msg = str(e)
            print('  upload failed:', msg[:300], flush=True)
            if 'quota' in msg.lower() or 'uploadLimitExceeded' in msg or 'rateLimit' in msg:
                print('STOP: YouTube daily limit reached; the next scheduled run continues.')
                break
            continue
        print('  uploaded new video', vid, flush=True)
        r = requests.put(f'{yt_api.API}/videos', params={'part': 'status'}, headers=yt_api.H(tok, **{'Content-Type': 'application/json'}),
                         data=json.dumps({'id': u['video_id'], 'status': {'privacyStatus': 'private', 'selfDeclaredMadeForKids': False}}), timeout=30)
        unsched = r.status_code == 200
        print('  old video unscheduled:', r.status_code, '' if unsched else r.text[:300], flush=True)
        th = yt_api.set_thumb(tok, vid, os.path.join(out, meta['thumb'])) if meta.get('thumb') and os.path.exists(os.path.join(out, meta['thumb'])) else 'none'
        pl = yt_api.playlist(tok, vid, meta['playlist'], meta.get('playlist_desc', '')) if meta.get('playlist') else 'none'
        link = f'https://youtu.be/{vid}' if u['kind'] == 'long' else f'https://youtube.com/shorts/{vid}'
        old = dict(u, key=u['key'] + ':replaced', replaced_by=vid, unscheduled=unsched, reason='old music (remusic)')
        new = {k: v for k, v in u.items() if k not in ('replaced_by', 'unscheduled', 'note')}
        new.update({'video_id': vid, 'link': link, 'uploaded': dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                    'thumbnail': th, 'playlist': pl, 'replaces': u['video_id'], 'music': MUSIC_TAG})

        def apply(ups, u=u, old=old, new=new):
            ups[:] = [x for x in ups if not (x['key'] == u['key'] and x['video_id'] == u['video_id'])] + [old, new]

        line = f'- {u["publish_at"][:10]} {new["title"]} → {link} (eski {u["video_id"]} {"takvimden alındı, gizli" if unsched else "TAKVİMDEN ALINAMADI — Studio’da elle gizle/sil"})'
        if u['kind'] == 'short':
            le = next((x for x in uploads if x['key'] == f'{u["slug"]}:long'), None)
            if le:
                line += f' · ilgili video: {le["title"]} ({le["link"]})'
        save(repo, f'remusic: {u["key"]}', apply, line)
        print('  done:', link, 'thumbnail', th, 'playlist', pl, flush=True)
        done_n += 1
        shutil.rmtree(out, ignore_errors=True)
        free_artifacts(todo[todo.index(u0) + 1:])
    print(f'swapped {done_n} video(s) this run')


if __name__ == '__main__':
    main(sys.argv[1], '--dry' in sys.argv)
