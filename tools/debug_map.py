"""2D check map of a city: real land/water from geo.json with every feature from city.json drawn on top.

  python3 tools/debug_map.py <slug> [outdir]

Writes map_full.png (whole area) and map_core.png (old-city close-up) so coordinates can be checked against the
real shoreline before any 3D render: walls must sit on land and end at the water, bridges must cross it, etc.
"""
import base64, json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KZ = 110.574
STYLE_COL = {'ancient': (214, 120, 70), 'roman': (220, 90, 60), 'celtic': (150, 110, 60), 'medieval': (170, 80, 160), 'stone': (120, 120, 140),
             'ottoman': (200, 140, 60), 'georgian': (190, 60, 60), 'industrial': (90, 60, 50), 'victorian': (160, 50, 90), 'suburb': (230, 170, 120),
             'modern': (90, 110, 160), 'highrise': (40, 70, 200)}


def font(sz):
    for p in ['/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', '/usr/share/fonts/dejavu/DejaVuSans.ttf']:
        if os.path.exists(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()


def layer(g):
    sd = np.frombuffer(base64.b64decode(g['sd_b64']), '<i2').reshape(g['nz'], g['nx'])
    return sd


def render(city, geo, bounds, size, out):
    lat0, lon0 = geo['origin']
    kx = 111.32 * math.cos(math.radians(lat0))
    x0, x1, z0, z1 = bounds
    W = size; H = int(size * (z1 - z0) / (x1 - x0))
    sx = W / (x1 - x0)
    P = lambda lat, lon: (((lon - lon0) * kx - x0) * sx, (-(lat - lat0) * KZ - z0) * sx)
    img = Image.new('RGB', (W, H), (30, 60, 80))
    # land/water: sample the finest layer available per pixel
    xs = x0 + (np.arange(W) + 0.5) / sx
    zs = z0 + (np.arange(H) + 0.5) / sx
    X, Z = np.meshgrid(xs, zs)
    land = np.zeros((H, W), bool)
    for g in [geo] + ([geo['core']] if geo.get('core') else []):
        sd = layer(g)
        gi = np.clip(((X - g['x0']) / g['cell_km']).round().astype(int), 0, g['nx'] - 1)
        gj = np.clip(((Z - g['z0']) / g['cell_km']).round().astype(int), 0, g['nz'] - 1)
        inside = (X >= g['x0']) & (X <= g['x0'] + (g['nx'] - 1) * g['cell_km']) & (Z >= g['z0']) & (Z <= g['z0'] + (g['nz'] - 1) * g['cell_km'])
        land = np.where(inside, sd[gj, gi] > 0, land)
    rgb = np.where(land[..., None], np.array([200, 205, 175], np.uint8), np.array([95, 160, 190], np.uint8))
    img = Image.fromarray(rgb.astype(np.uint8))
    d = ImageDraw.Draw(img, 'RGBA'); f = font(max(10, W // 120)); fs = font(max(9, W // 150))
    for o in city.get('open_spaces', []):
        d.polygon([P(*p) for p in o['poly']], fill=(80, 150, 70, 110), outline=(40, 110, 40, 255))
    for t in city.get('timed_water', []):
        d.polygon([P(*p) for p in t['poly']], fill=(40, 90, 200, 140), outline=(20, 40, 160, 255))
        d.text(P(*t['poly'][0]), f"{t.get('name', 'water')} {t['from']}", fill=(10, 20, 120), font=fs)
    for dd in city.get('districts', []):
        c = STYLE_COL.get(dd['style'], (0, 0, 0))
        pts = [P(*p) for p in dd['poly']]
        d.polygon(pts, fill=c + (45,), outline=c + (255,))
        cx = sum(p[0] for p in pts) / len(pts); cy = sum(p[1] for p in pts) / len(pts)
        d.text((cx, cy), f"{dd.get('name', '')} {dd['from']}", fill=c + (255,), font=fs, anchor='mm')
    for fi in city.get('fires', []):
        d.polygon([P(*p) for p in fi['poly']], outline=(255, 120, 0, 255), width=3)
        d.text(P(*fi['poly'][0]), f"FIRE {fi['year']}", fill=(220, 90, 0), font=f)
    for r in city.get('roads', []):
        d.line([P(*p) for p in r['path']], fill=(120, 100, 60, 220), width=2)
    for w in city.get('walls', []):
        d.line([P(*p) for p in w['path']], fill=(255, 255, 255, 255), width=3)
        d.line([P(*p) for p in w['path']], fill=(60, 50, 40, 255), width=1)
        d.text(P(*w['path'][0]), f"{w.get('name', 'wall')} {w['built']}", fill=(40, 30, 20), font=fs)
    for b in city.get('bridges', []):
        d.line([P(*p) for p in b['path']], fill=(250, 220, 40, 255), width=4)
        d.text(P(*b['path'][0]), f"{b.get('name', '')} {b['built']}", fill=(120, 90, 0), font=fs)
    for l in city.get('landmarks', []):
        x, y = P(*l['at']); d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=(200, 0, 0, 255))
        n = l.get('name'); n = n.get('en') if isinstance(n, dict) else (n or l['type'])
        d.text((x + 6, y - 6), f"{n} {l['built']}", fill=(150, 0, 0), font=fs)
    for l in city.get('labels', []):
        x, y = P(*l['at']); t = l['text']['en'] if isinstance(l['text'], dict) else l['text']
        d.text((x, y), t, fill=(0, 0, 0, 200) if l.get('kind') != 'water' else (0, 40, 120, 230), font=fs, anchor='mm')
    for s in city.get('segments', []):
        if s.get('camera'):
            x, y = P(*s['camera']['center']); r = 5
            d.rectangle((x - r, y - r, x + r, y + r), outline=(0, 0, 0, 255))
    # 1 km scale bar
    d.line((20, H - 20, 20 + sx, H - 20), fill=(0, 0, 0), width=3); d.text((20, H - 40), '1 km', fill=(0, 0, 0), font=f)
    img.save(out)


def main(slug, outdir=None):
    cdir = os.path.join(ROOT, 'cities', slug)
    city = json.load(open(os.path.join(cdir, 'city.json')))
    geo = json.load(open(os.path.join(cdir, 'geo.json')))
    outdir = outdir or os.path.join(cdir, 'preview'); os.makedirs(outdir, exist_ok=True)
    full = (geo['x0'], geo['x0'] + (geo['nx'] - 1) * geo['cell_km'], geo['z0'], geo['z0'] + (geo['nz'] - 1) * geo['cell_km'])
    render(city, geo, full, 2400, os.path.join(outdir, 'map_full.png'))
    if geo.get('core'):
        g = geo['core']
        core = (g['x0'], g['x0'] + (g['nx'] - 1) * g['cell_km'], g['z0'], g['z0'] + (g['nz'] - 1) * g['cell_km'])
    else:
        cw = (full[1] - full[0]) / 4; ch = (full[3] - full[2]) / 4; cx = (full[0] + full[1]) / 2; cz = (full[2] + full[3]) / 2
        core = (cx - cw, cx + cw, cz - ch, cz + ch)
    render(city, geo, core, 2400, os.path.join(outdir, 'map_core.png'))
    print('maps written to', outdir)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
