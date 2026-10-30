#!/usr/bin/env python3
"""Vertical Shorts cut from an episode. Each Short is a stretch of the episode's timeline played faster, rendered
again in 1080x1920 with a vertical layout (the engine's ?short=<id> mode). Defined in cities/<slug>/shorts.json:

  {"shorts": [
    {"id": "whole", "from_year": -50, "to_year": 2026, "seconds": 50,
     "hook": {"line1": {"en": "London", "tr": "Londra"}, "line2": {"en": "2,000 years in 50 seconds", "tr": "50 saniyede 2.000 yıl"}},
     "title": {"en": "London: 2,000 Years in 50 Seconds #shorts", "tr": "..."},
     "description": {"en": "...", "tr": "..."},
     "tags": ["london history", ...]}
  ]}

Optional per Short: "from_t"/"to_t" (episode seconds instead of years), "hold" (seconds frozen on the last frame,
default 2.5 — the end card "full episode on the channel" shows there), "fov" (default 52), "dist_mult" (default 1.5),
"end" {"line1", "line2"}, "seed" (music).

  python3 tools/shorts.py info  <slug>                 # resolved times / speed / frames for every Short
  python3 tools/shorts.py plan  <slug> [fps]           # render matrix for the Shorts that get a slot (JSON)
  python3 tools/shorts.py assemble <slug> <chunks_dir> <out_dir>   # out_dir/<id>/<lang>/video.mp4 + meta.json
"""
import datetime as dt, glob, json, math, os, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DAYS = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']


def load(slug):
    city = json.load(open(os.path.join(ROOT, 'cities', slug, 'city.json')))
    p = os.path.join(ROOT, 'cities', slug, 'shorts.json')
    shorts = json.load(open(p)).get('shorts', []) if os.path.exists(p) else []
    return city, shorts


def segs(city):
    acc, out = 0.0, []
    for s in city['segments']:
        out.append((acc, acc + s['seconds'], s['from'], s['to']))
        acc += s['seconds']
    return out, acc


def t_of(city, y):
    """Same as tOf() in engine/index.html: episode time at which year y is reached."""
    S, dur = segs(city)
    if y <= S[0][2]:
        return 0.0
    for i, (t0, t1, a, b) in enumerate(S):
        if a <= y <= b:
            return t0 if b == a else t0 + (y - a) / (b - a) * (t1 - t0)
        if i + 1 < len(S) and b < y < S[i + 1][2]:
            return S[i + 1][0]
    return dur


def resolve(city, sh, fps=30):
    S, dur = segs(city)
    t0 = float(sh['from_t']) if 'from_t' in sh else t_of(city, sh['from_year'])
    t1 = float(sh['to_t']) if 'to_t' in sh else (dur if sh['to_year'] >= S[-1][3] else t_of(city, sh['to_year']))
    if t1 < dur:
        t1 -= 0.001         # stop just before the next segment starts, so the counter shows to_year, not the year after
    t0, t1 = max(0.0, t0), min(dur, t1)
    if t1 <= t0:
        raise SystemExit(f'short {sh["id"]}: empty range {t0}..{t1}')
    secs = float(sh.get('seconds', 50)); hold = float(sh.get('hold', 2.5))
    spd = (t1 - t0) / secs
    total = secs + hold
    if total > 59.5:
        raise SystemExit(f'short {sh["id"]}: {total:.1f} s is too long (seconds + hold must be ≤ 59)')
    return {'id': sh['id'], 't0': round(t0, 3), 't1': round(t1, 3), 'spd': round(spd, 4), 'seconds': secs, 'hold': hold,
            'total': total, 'frames': int(round(total * fps))}


def frame_time(r, f, fps):
    """Episode time and Short time (seconds) of output frame f."""
    rt = f / fps
    return min(r['t1'], r['t0'] + rt * r['spd']), rt


def utc(s):
    return dt.datetime.strptime(s, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=dt.timezone.utc)


def long_entry(slug):
    p = os.path.join(ROOT, 'uploads.json')
    ups = json.load(open(p)) if os.path.exists(p) else []
    return next((u for u in ups if u.get('key') == f'{slug}:long'), None), ups


def slot_budget(slug):
    """How many Shorts of this episode fit between its own long slot and the next long slot
    (Friday episode → Sat, Sun, Mon = 3; Tuesday episode → Wed, Thu = 2). None = no limit known."""
    le, _ = long_entry(slug)
    if not le or not le.get('publish_at'):
        return None
    cfg = json.load(open(os.path.join(ROOT, 'config', 'schedule.json')))
    start = utc(le['publish_at'])
    def slots(kind, days):
        for add in range(days):
            d = (start + dt.timedelta(days=add)).date()
            for sl in cfg[kind]['slots_utc']:
                wd, hm = sl.split()
                if DAYS.index(wd) == d.weekday():
                    h, m = map(int, hm.split(':'))
                    yield dt.datetime(d.year, d.month, d.day, h, m, tzinfo=dt.timezone.utc)
    nxt = min((a for a in slots('long', 9) if a > start + dt.timedelta(hours=1)), default=start + dt.timedelta(days=7))
    return sum(1 for a in slots('short', 9) if start < a < nxt)


def chosen(slug):
    city, shorts = load(slug)
    n = slot_budget(slug)
    _, ups = long_entry(slug)
    done = {u['key'] for u in ups}
    pick = [s for s in shorts if f'{slug}:short:{s["id"]}' not in done]
    if n is not None:
        pick = pick[:max(0, n - (len(shorts) - len(pick)))]
    return city, pick


def T(o, lang):
    return o if isinstance(o, str) else (o or {}).get(lang) or (o or {}).get('en', '')


def describe(city, sh, lang, long_link):
    yt = city.get('youtube', {})
    lines = [T(sh.get('description', ''), lang).strip()]
    if long_link:
        lines += ['', ('▶ Full episode: ' if lang == 'en' else '▶ Tam bölüm: ') + long_link]
    lines += ['', {'en': 'Buildings are simplified symbols placed from historical maps and research; population figures before '
                         'modern censuses are scholarly estimates. Terrain: AWS Terrain Tiles; water: © OpenStreetMap contributors. Music: original.',
                   'tr': 'Binalar tarihî harita ve araştırmalara göre yerleştirilmiş sade sembollerdir; modern sayımlardan önceki nüfuslar '
                         'akademik tahminlerdir. Arazi: AWS Terrain Tiles; su: © OpenStreetMap katkıcıları. Müzik: özgün.'}[lang]]
    tags = sh.get('hashtags') or (yt.get('hashtags', []) + ['#Shorts'])
    lines += ['', ' '.join(tags)]
    return '\n'.join(lines)[:4900]


def assemble(slug, chunks, out):
    city, shorts = load(slug)
    le, _ = long_entry(slug)
    long_link = le['link'] if le else None
    for i, sh in enumerate(shorts):
        d0 = os.path.join(chunks, sh['id'])
        if not os.path.isdir(d0):
            continue
        r = resolve(city, sh)
        music = os.path.join(out, f'music_{sh["id"]}.wav'); os.makedirs(out, exist_ok=True)
        subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'music.py'), str(r['total'] + 1), music,
                        str(sh.get('seed', city.get('seed', 7) * 10 + i + 1))], check=True)
        langs = sorted({os.path.basename(p).split('_')[1] for p in glob.glob(os.path.join(d0, '**', 'chunk_*_*.mp4'), recursive=True)})
        for lang in langs:
            parts = sorted(glob.glob(os.path.join(d0, '**', f'chunk_{lang}_*.mp4'), recursive=True), key=lambda p: int(p.rsplit('_', 1)[1].split('.')[0]))
            d = os.path.join(out, sh['id'], lang); os.makedirs(d, exist_ok=True)
            with open(os.path.join(d, 'list.txt'), 'w') as f:
                for p in parts:
                    f.write(f"file '{os.path.abspath(p)}'\n")
            subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', os.path.join(d, 'list.txt'), '-i', music,
                            '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart',
                            os.path.join(d, 'video.mp4')], check=True)
            os.remove(os.path.join(d, 'list.txt'))
            other = 'tr' if lang == 'en' else 'en'
            meta = {'slug': slug, 'kind': 'short', 'key': f'{slug}:short:{sh["id"]}', 'lang': lang, 'file': 'video.mp4', 'thumb': None,
                    'title': T(sh['title'], lang)[:100], 'description': describe(city, sh, lang, long_link),
                    'tags': sh.get('tags', city.get('youtube', {}).get('tags', [])),
                    'playlist': {'en': 'Cities in 60 Seconds', 'tr': '60 Saniyede Şehirler'}[lang],
                    'playlist_desc': {'en': 'How great cities grew — each in under a minute.', 'tr': 'Büyük şehirler nasıl büyüdü — her biri bir dakikadan kısa.'}[lang],
                    'localizations': {other: {'title': T(sh['title'], other)[:100], 'description': describe(city, sh, other, long_link)}},
                    'not_before': le.get('publish_at') if le else None, 'duration_s': r['total']}
            json.dump(meta, open(os.path.join(d, 'meta.json'), 'w'), indent=1, ensure_ascii=False)
            print('assembled', sh['id'], lang, len(parts), 'chunks', os.path.getsize(os.path.join(d, 'video.mp4')) // 1e6, 'MB')
        os.remove(music)


def main():
    cmd, slug = sys.argv[1], sys.argv[2]
    if cmd == 'info':
        city, shorts = load(slug)
        for sh in shorts:
            print(json.dumps(resolve(city, sh)))
        print('slot budget:', slot_budget(slug))
    elif cmd == 'plan':
        fps = int(sys.argv[3]) if len(sys.argv) > 3 else 30
        city, pick = chosen(slug)
        mx = []
        for sh in pick:
            r = resolve(city, sh, fps)
            n = max(1, math.ceil(r['frames'] / 300)); size = math.ceil(r['frames'] / n)
            mx += [{'id': sh['id'], 'start': a, 'end': min(r['frames'], a + size)} for a in range(0, r['frames'], size)]
        print(json.dumps({'slug': slug, 'shorts': [s['id'] for s in pick], 'chunks': mx}))
    elif cmd == 'assemble':
        assemble(slug, sys.argv[3], sys.argv[4])


if __name__ == '__main__':
    main()
