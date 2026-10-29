"""Check a city.json before rendering.  python3 tools/validate.py <slug>
Prints problems (ERROR stops the render; WARN should be looked at) and a building-count estimate."""
import json, math, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KZ = 110.574
STYLE_GRAIN = {'ancient': 60, 'roman': 60, 'celtic': 70, 'medieval': 55, 'stone': 60, 'ottoman': 55, 'georgian': 60, 'industrial': 90,
               'victorian': 65, 'suburb': 70, 'modern': 110, 'highrise': 150}
LM_TYPES = {'temple', 'church', 'cathedral', 'domechurch', 'mosque', 'castle', 'fort', 'tower', 'clocktower', 'palace', 'parliament', 'amphitheatre',
            'circus', 'stadium', 'forum', 'column', 'obelisk', 'skyscraper', 'spire_tower', 'wheel', 'dome_arena', 'station', 'harbor', 'box'}
errs, warns = [], []


def E(m): errs.append(m)
def Wn(m): warns.append(m)


def bil(o, where, maxlen=None):
    if o is None:
        return
    if isinstance(o, str) or not isinstance(o, dict) or not o.get('en') or not o.get('tr'):
        E(f'{where}: needs both "en" and "tr" text')
        return
    if maxlen:
        for k in ('en', 'tr'):
            if len(o[k]) > maxlen:
                Wn(f'{where}.{k} is {len(o[k])} chars (> {maxlen}); may not fit on screen')


def main(slug):
    c = json.load(open(os.path.join(ROOT, 'cities', slug, 'city.json')))
    s0, w0, n0, e0 = c['geo']['bbox']
    lat0 = (s0 + n0) / 2
    kx = 111.32 * math.cos(math.radians(lat0))
    def inside(p, where):
        if not (s0 <= p[0] <= n0 and w0 <= p[1] <= e0):
            E(f'{where}: point {p} outside geo.bbox (remember [lat, lon])')
    def area_km2(poly):
        pts = [((lon - w0) * kx, (lat - s0) * KZ) for lat, lon in poly]
        return abs(sum(pts[i][0] * pts[i - 1][1] - pts[i - 1][0] * pts[i][1] for i in range(len(pts)))) / 2
    bil(c.get('name'), 'name'); bil(c.get('intro'), 'intro', 60)
    segs = c['segments']; total = sum(s['seconds'] for s in segs)
    prev_to = -1e9
    for i, s in enumerate(segs):
        w = f'segments[{i}]'
        if s['from'] > s['to']: E(f'{w}: from > to')
        if s['from'] < prev_to: E(f'{w}: years go backwards ({s["from"]} < previous {prev_to})')
        prev_to = s['to']
        if s['seconds'] < 2: Wn(f'{w}: very short ({s["seconds"]}s)')
        if s.get('title'):
            bil(s['title'], w + '.title', 34); bil(s.get('sub'), w + '.sub', 95)
            if s['seconds'] < 7: Wn(f'{w}: titled segment shorter than 7s is hard to read')
        bil(s.get('era'), w + '.era', 28); bil(s.get('city_name'), w + '.city_name', 28)
        if s.get('camera'):
            inside(s['camera']['center'], w + '.camera')
        if s.get('chapter') is not None and not isinstance(s['chapter'], (str, dict)):
            E(f'{w}.chapter must be text')
    if not segs[0].get('camera'): E('segments[0] needs a camera')
    est = 0
    for i, d in enumerate(c.get('districts', [])):
        for p in d['poly']: inside(p, f'districts[{i}]')
        g = (d.get('grain_m') or STYLE_GRAIN.get(d['style'], 60)) / 1000
        if d['style'] not in STYLE_GRAIN: E(f'districts[{i}]: unknown style {d["style"]}')
        n = area_km2(d['poly']) / (g * g) * d.get('density', 0.85) * 0.8
        est += n
        if n > 15000: Wn(f'districts[{i}] "{d.get("name")}" ≈{int(n)} buildings; raise grain_m')
    for i, l in enumerate(c.get('landmarks', [])):
        inside(l['at'], f'landmarks[{i}]')
        if l['type'] not in LM_TYPES: E(f'landmarks[{i}]: unknown type {l["type"]}')
    for k in ('walls', 'roads', 'bridges'):
        for i, x in enumerate(c.get(k, [])):
            for p in x['path']: inside(p, f'{k}[{i}]')
    for i, l in enumerate(c.get('labels', [])):
        inside(l['at'], f'labels[{i}]'); bil(l['text'], f'labels[{i}].text', 40)
    yt = c.get('youtube', {})
    bil(yt.get('title'), 'youtube.title', 100); bil(yt.get('description'), 'youtube.description')
    if len(c.get('sources', [])) < 6: Wn('fewer than 6 sources listed')
    if not (780 <= total <= 1080) and not c.get('test'): Wn(f'duration {total}s; target is 13–18 min (780–1080 s)')
    print(f'duration {total}s ({total / 60:.1f} min), segments {len(segs)}, ≈{int(est)} buildings')
    if est > 70000: E(f'≈{int(est)} buildings is too many (limit ~70k); use larger grain_m for modern areas')
    for m in warns: print('WARN ', m)
    for m in errs: print('ERROR', m)
    print('OK' if not errs else f'{len(errs)} error(s)')
    sys.exit(1 if errs else 0)


if __name__ == '__main__':
    main(sys.argv[1])
