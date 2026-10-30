#!/usr/bin/env python3
"""YouTube API for Dust to Downtown. Runs only inside GitHub Actions with secrets
YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN (never paste them anywhere else).

  python3 tools/yt_api.py whoami                       # prints the channel the token belongs to
  python3 tools/yt_api.py upload <episode_dir> <repo>  # upload video.mp4 (+ thumb.jpg) from meta.json, schedule it
  python3 tools/yt_api.py list                         # every video on the channel with privacy / schedule
  python3 tools/yt_api.py publish <repo>               # handle requests/publish/*.json (make public now / at a time)

Safety: every upload first checks that the token's channel title equals config/channel.json "title".
A token made for the wrong channel (e.g. The Before Atlas) stops the run before anything is uploaded.
"""
import datetime as dt, json, os, sys, time
import requests

TOKEN_URL = 'https://oauth2.googleapis.com/token'
API = 'https://www.googleapis.com/youtube/v3'
UPLOAD = 'https://www.googleapis.com/upload/youtube/v3/videos'
THUMB = 'https://www.googleapis.com/upload/youtube/v3/thumbnails/set'


def token():
    for k in ('YT_CLIENT_ID', 'YT_CLIENT_SECRET', 'YT_REFRESH_TOKEN'):
        if not os.environ.get(k):
            sys.exit(f'missing secret {k} — see SETUP.md')
    r = requests.post(TOKEN_URL, data={'client_id': os.environ['YT_CLIENT_ID'], 'client_secret': os.environ['YT_CLIENT_SECRET'],
                                       'refresh_token': os.environ['YT_REFRESH_TOKEN'], 'grant_type': 'refresh_token'}, timeout=30)
    if r.status_code != 200:
        sys.exit(f'token refresh failed ({r.status_code}): {r.text[:300]}')
    return r.json()['access_token']


def H(tok, **kw):
    return {'Authorization': f'Bearer {tok}', **kw}


def channel(tok):
    r = requests.get(f'{API}/channels', params={'part': 'snippet', 'mine': 'true'}, headers=H(tok), timeout=30)
    items = r.json().get('items', [])
    if not items:
        sys.exit(f'no channel for this token ({r.status_code}): {r.text[:200]}')
    return items[0]['id'], items[0]['snippet']['title']


def check_channel(tok, repo):
    want = json.load(open(os.path.join(repo, 'config', 'channel.json')))['title']
    cid, title = channel(tok)
    if title.strip().lower() != want.strip().lower():
        sys.exit(f'WRONG CHANNEL: token belongs to "{title}" ({cid}), expected "{want}". Nothing uploaded. '
                 f'Create the refresh token again and pick "{want}" in the account chooser.')
    print(f'channel ok: {title} ({cid})')
    return cid


def next_slot(cfg, taken, now=None):
    """First weekly slot (e.g. "TUE 15:00" UTC) at least min_lead_hours away that is not already taken."""
    now = now or dt.datetime.now(dt.timezone.utc)
    days = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']
    taken = set(taken)
    for add in range(0, 60):
        d = (now + dt.timedelta(days=add)).date()
        for slot in sorted(cfg['slots_utc']):
            wd, hm = slot.split()
            if days.index(wd) != d.weekday():
                continue
            h, m = map(int, hm.split(':'))
            at = dt.datetime(d.year, d.month, d.day, h, m, tzinfo=dt.timezone.utc)
            iso = at.strftime('%Y-%m-%dT%H:%M:%SZ')
            if at < now + dt.timedelta(hours=cfg.get('min_lead_hours', 3)) or iso in taken:
                continue
            return iso
    return None


def upload_video(tok, path, meta, publish_at):
    body = {'snippet': {'title': meta['title'][:100], 'description': meta['description'][:5000], 'tags': meta.get('tags', [])[:30],
                        'categoryId': '27', 'defaultLanguage': meta.get('lang', 'en')},
            'status': {'privacyStatus': 'private', 'selfDeclaredMadeForKids': False, 'embeddable': True, 'containsSyntheticMedia': False}}
    if publish_at:
        body['status']['publishAt'] = publish_at
    if meta.get('localizations'):
        body['localizations'] = meta['localizations']
    size = os.path.getsize(path)
    # Starting a resumable session creates nothing on the channel, so when YouTube rejects the metadata we can
    # drop optional fields one by one and say which one it disliked.
    drops = [None, ('status', 'containsSyntheticMedia'), ('', 'localizations'),
             ('snippet', 'tags'), ('status', 'embeddable')]
    for d in drops:
        if d:
            (body.get(d[0]) if d[0] else body).pop(d[1], None)
        parts = 'snippet,status' + (',localizations' if 'localizations' in body else '')
        r = requests.post(f'{UPLOAD}?uploadType=resumable&part={parts}', headers=H(tok, **{'Content-Type': 'application/json',
                          'X-Upload-Content-Type': 'video/mp4', 'X-Upload-Content-Length': str(size)}), data=json.dumps(body), timeout=60)
        if r.status_code == 200:
            if d:
                print('metadata accepted after dropping:', d)
            break
        print(f'start upload {r.status_code} (dropped so far up to {d}): {r.text[:300]}')
        if r.status_code != 400:
            break
    if r.status_code != 200:
        raise RuntimeError(f'start upload {r.status_code}: {r.text[:400]}')
    url = r.headers['Location']
    for attempt in range(6):
        with open(path, 'rb') as f:
            r = requests.put(url, headers={'Content-Type': 'video/mp4', 'Content-Length': str(size)}, data=f, timeout=3600)
        if r.status_code in (200, 201):
            return r.json()['id']
        if r.status_code in (500, 502, 503, 504):
            time.sleep(15 * (attempt + 1)); continue
        raise RuntimeError(f'upload {r.status_code}: {r.text[:400]}')
    raise RuntimeError('upload failed after retries')


def set_thumb(tok, vid, path):
    with open(path, 'rb') as f:
        r = requests.post(f'{THUMB}?videoId={vid}', headers=H(tok, **{'Content-Type': 'image/jpeg'}), data=f, timeout=120)
    return 'ok' if r.status_code == 200 else f'thumbnail not set ({r.status_code}): {r.text[:200]} — custom thumbnails need a phone-verified channel'


def playlist(tok, vid, name, desc):
    r = requests.get(f'{API}/playlists', params={'part': 'snippet', 'mine': 'true', 'maxResults': 50}, headers=H(tok), timeout=30).json()
    pid = next((p['id'] for p in r.get('items', []) if p['snippet']['title'] == name), None)
    if not pid:
        r = requests.post(f'{API}/playlists', params={'part': 'snippet,status'}, headers=H(tok, **{'Content-Type': 'application/json'}),
                          data=json.dumps({'snippet': {'title': name[:150], 'description': desc}, 'status': {'privacyStatus': 'public'}}), timeout=30)
        if r.status_code != 200:
            return f'playlist error {r.status_code}'
        pid = r.json()['id']
    r = requests.post(f'{API}/playlistItems', params={'part': 'snippet'}, headers=H(tok, **{'Content-Type': 'application/json'}),
                      data=json.dumps({'snippet': {'playlistId': pid, 'resourceId': {'kind': 'youtube#video', 'videoId': vid}}}), timeout=30)
    return 'added' if r.status_code == 200 else f'not added ({r.status_code})'


def cmd_upload(ep, repo):
    tok = token()
    check_channel(tok, repo)
    meta = json.load(open(os.path.join(ep, 'meta.json')))
    up_path = os.path.join(repo, 'uploads.json')
    uploads = json.load(open(up_path)) if os.path.exists(up_path) else []
    key = meta['slug'] + ':' + meta['kind']
    done = next((u for u in uploads if u['key'] == key), None)
    rj = os.path.join(repo, 'cities', meta['slug'], 'render.json')
    replace = done and os.path.exists(rj) and json.load(open(rj)).get('replace') == done['video_id']
    if replace:
        # A corrected render replaces a scheduled, not-yet-public upload: the new video takes its slot (or the next
        # free one) and only after the new upload succeeded is the old one taken off the schedule (kept private).
        now = dt.datetime.now(dt.timezone.utc)
        old_at = dt.datetime.strptime(done['publish_at'], '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=dt.timezone.utc) if done.get('publish_at') else None
        if old_at and old_at <= now:
            print('NOT REPLACED: the old video', done['link'], 'is already public; nothing uploaded'); return
        cfg = json.load(open(os.path.join(repo, 'config', 'schedule.json')))
        at = done['publish_at'] if old_at and old_at > now + dt.timedelta(minutes=30) else \
            next_slot(cfg['long'], [u.get('publish_at') for u in uploads if u.get('kind') == meta['kind'] and u is not done])
        vid = upload_video(tok, os.path.join(ep, meta['file']), meta, at)
        r = requests.put(f'{API}/videos', params={'part': 'status'}, headers=H(tok, **{'Content-Type': 'application/json'}),
                         data=json.dumps({'id': done['video_id'], 'status': {'privacyStatus': 'private', 'selfDeclaredMadeForKids': False}}), timeout=30)
        print('old video unscheduled (stays private):', done['video_id'], r.status_code, '' if r.status_code == 200 else r.text[:300])
        th = set_thumb(tok, vid, os.path.join(ep, meta['thumb'])) if meta.get('thumb') and os.path.exists(os.path.join(ep, meta['thumb'])) else 'none'
        pl = playlist(tok, vid, meta['playlist'], meta.get('playlist_desc', '')) if meta.get('playlist') else 'none'
        uploads.remove(done)
        done.update({'key': key + ':replaced', 'replaced_by': vid, 'unscheduled': r.status_code == 200})
        uploads.append(done)
        uploads.append({'key': key, 'slug': meta['slug'], 'kind': meta['kind'], 'video_id': vid, 'link': f'https://youtu.be/{vid}',
                        'title': meta['title'], 'publish_at': at, 'uploaded': now.strftime('%Y-%m-%dT%H:%M:%SZ'), 'thumbnail': th,
                        'playlist': pl, 'replaces': done['video_id']})
        json.dump(uploads, open(up_path, 'w'), indent=1, ensure_ascii=False)
        print(f'replaced {key}: https://youtu.be/{vid} publish_at={at} thumbnail={th} playlist={pl}')
        return
    if done:
        print('already uploaded:', key, done['link'])
        if done.get('thumbnail') != 'ok' and meta.get('thumb') and os.path.exists(os.path.join(ep, meta['thumb'])):
            done['thumbnail'] = set_thumb(tok, done['video_id'], os.path.join(ep, meta['thumb']))
            json.dump(uploads, open(up_path, 'w'), indent=1, ensure_ascii=False)
            print('thumbnail retry:', done['thumbnail'][:120])
        return
    cfg = json.load(open(os.path.join(repo, 'config', 'schedule.json')))
    slots = cfg['long'] if meta['kind'] == 'long' else cfg['short']
    at = next_slot(slots, [u.get('publish_at') for u in uploads if u.get('kind') == meta['kind']]) if slots.get('auto', True) else None
    vid = upload_video(tok, os.path.join(ep, meta['file']), meta, at)
    th = set_thumb(tok, vid, os.path.join(ep, meta['thumb'])) if meta.get('thumb') and os.path.exists(os.path.join(ep, meta['thumb'])) else 'none'
    pl = playlist(tok, vid, meta['playlist'], meta.get('playlist_desc', '')) if meta.get('playlist') else 'none'
    link = f'https://youtu.be/{vid}' if meta['kind'] == 'long' else f'https://youtube.com/shorts/{vid}'
    uploads.append({'key': key, 'slug': meta['slug'], 'kind': meta['kind'], 'video_id': vid, 'link': link, 'title': meta['title'],
                    'publish_at': at, 'uploaded': dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), 'thumbnail': th, 'playlist': pl})
    json.dump(uploads, open(up_path, 'w'), indent=1, ensure_ascii=False)
    print(f'uploaded {key} {link} publish_at={at} thumbnail={th} playlist={pl}')


def cmd_publish(repo):
    tok = token()
    check_channel(tok, repo)
    req_dir, done_dir = os.path.join(repo, 'requests', 'publish'), os.path.join(repo, 'requests', 'done')
    os.makedirs(done_dir, exist_ok=True)
    for fn in sorted(os.listdir(req_dir)) if os.path.isdir(req_dir) else []:
        if not fn.endswith('.json'):
            continue
        rq = json.load(open(os.path.join(req_dir, fn)))
        res = []
        for vid in rq['video_ids']:
            st = {'privacyStatus': 'private', 'publishAt': rq['at']} if rq.get('at') else {'privacyStatus': 'public'}
            st['selfDeclaredMadeForKids'] = False
            r = requests.put(f'{API}/videos', params={'part': 'status'}, headers=H(tok, **{'Content-Type': 'application/json'}),
                             data=json.dumps({'id': vid, 'status': st}), timeout=30)
            res.append({'video_id': vid, 'ok': r.status_code == 200, 'status': st, 'error': None if r.status_code == 200 else r.text[:300]})
        rq['result'] = res
        json.dump(rq, open(os.path.join(done_dir, fn), 'w'), indent=1)
        os.remove(os.path.join(req_dir, fn))
        print(fn, res)


def cmd_setup(repo):
    """Channel settings that the mobile app can't change. Reads the current branding first and only adds/changes
    keywords, default language, country (only if empty), made-for-kids = no, and the watermark. Description, name,
    logo and banner are left exactly as the owner set them."""
    tok = token()
    cid = check_channel(tok, repo)
    cfg = json.load(open(os.path.join(repo, 'config', 'channel_setup.json')))
    r = requests.get(f'{API}/channels', params={'part': 'brandingSettings,status', 'id': cid}, headers=H(tok), timeout=30).json()['items'][0]
    ch = r.get('brandingSettings', {}).get('channel', {})
    print('before:', json.dumps({k: ch.get(k) for k in ('keywords', 'defaultLanguage', 'country')}, ensure_ascii=False),
          '| description chars:', len(ch.get('description', '')))
    ch['keywords'] = ' '.join(f'"{k}"' if ' ' in k else k for k in cfg['keywords'])[:500]
    ch['defaultLanguage'] = cfg.get('defaultLanguage', 'en')
    if not ch.get('country') and cfg.get('country'):
        ch['country'] = cfg['country']
    body = {'id': cid, 'brandingSettings': {'channel': ch}}
    r2 = requests.put(f'{API}/channels', params={'part': 'brandingSettings'}, headers=H(tok, **{'Content-Type': 'application/json'}),
                      data=json.dumps(body), timeout=30)
    print('branding update:', r2.status_code, '' if r2.status_code == 200 else r2.text[:300])
    if r2.status_code == 200:
        after = r2.json()['brandingSettings']['channel']
        print('after:', json.dumps({k: after.get(k) for k in ('keywords', 'defaultLanguage', 'country')}, ensure_ascii=False),
              '| description chars:', len(after.get('description', '')))
    r3 = requests.put(f'{API}/channels', params={'part': 'status'}, headers=H(tok, **{'Content-Type': 'application/json'}),
                      data=json.dumps({'id': cid, 'status': {'selfDeclaredMadeForKids': False}}), timeout=30)
    print('made-for-kids = no:', r3.status_code, '' if r3.status_code == 200 else r3.text[:300])
    wm = os.path.join(repo, cfg.get('watermark', 'branding/watermark_150.png'))
    if os.path.exists(wm):
        meta = {'timing': {'type': 'offsetFromStart', 'offsetMs': 0}, 'position': {'type': 'corner', 'cornerPosition': 'topRight'}}
        boundary = 'd2dwm'
        payload = (f'--{boundary}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n{json.dumps(meta)}\r\n'
                   f'--{boundary}\r\nContent-Type: image/png\r\n\r\n').encode() + open(wm, 'rb').read() + f'\r\n--{boundary}--'.encode()
        r4 = requests.post('https://www.googleapis.com/upload/youtube/v3/watermarks/set', params={'channelId': cid, 'uploadType': 'multipart'},
                           headers=H(tok, **{'Content-Type': f'multipart/related; boundary={boundary}'}), data=payload, timeout=60)
        print('watermark:', r4.status_code, '' if r4.status_code in (200, 204) else r4.text[:300])


if __name__ == '__main__':
    c = sys.argv[1]
    if c == 'whoami':
        tk = token(); cid, title = channel(tk)
        st = requests.get(f'{API}/channels', params={'part': 'status', 'id': cid}, headers=H(tk), timeout=30).json()['items'][0]['status']
        print((cid, title), 'longUploadsStatus=' + str(st.get('longUploadsStatus')))
    elif c == 'list':
        tk = token(); cid, title = channel(tk)
        up = requests.get(f'{API}/channels', params={'part': 'contentDetails', 'id': cid}, headers=H(tk), timeout=30).json()['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        items = requests.get(f'{API}/playlistItems', params={'part': 'contentDetails', 'playlistId': up, 'maxResults': 50}, headers=H(tk), timeout=30).json().get('items', [])
        ids = [i['contentDetails']['videoId'] for i in items]
        print(f'{title}: {len(ids)} video(s)')
        if ids:
            vs = requests.get(f'{API}/videos', params={'part': 'snippet,status,contentDetails,processingDetails', 'id': ','.join(ids)}, headers=H(tk), timeout=30).json().get('items', [])
            for v in vs:
                st = v['status']
                print(v['id'], '|', v['snippet']['title'], '|', st.get('privacyStatus'), '| publishAt', st.get('publishAt'), '| upload', st.get('uploadStatus'),
                      st.get('rejectionReason') or st.get('failureReason') or '', '| duration', v['contentDetails'].get('duration'),
                      '| processing', v.get('processingDetails', {}).get('processingStatus'))
    elif c == 'upload':
        cmd_upload(sys.argv[2], sys.argv[3])
    elif c == 'setup':
        cmd_setup(sys.argv[2])
    elif c == 'publish':
        cmd_publish(sys.argv[2])
