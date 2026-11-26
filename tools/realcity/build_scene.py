"""Turn fetched OSM data into render inputs: building rings + heights + appear times, and a ground texture.

  python3 tools/realcity/build_scene.py <osm.json> <outdir>

Outputs <outdir>/scene.npz, ground.png (colour), water.png (water mask), meta.json.
Footprints are real (OSM). Heights come from height / building:levels tags when present, otherwise a
typical value for the building type (logged in meta.json as the share of estimated heights).
Appear order: start_date when tagged, otherwise outward from the old town with noise (a visual growth, not a dated record).
"""
import json, math, os, sys
import numpy as np
from PIL import Image, ImageDraw
from shapely.geometry import LineString, Point, Polygon, box
from shapely.ops import linemerge, polygonize, unary_union

R = 6371008.8


def main():
    src, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    d = json.load(open(src))
    cfg = d['config']
    lat0, lon0 = cfg['center']
    kx = math.radians(1) * R * math.cos(math.radians(lat0))
    ky = math.radians(1) * R
    old = cfg.get('old_town', cfg['center'])
    ox, oy = (old[1] - lon0) * kx, (old[0] - lat0) * ky
    BH = cfg['build_half_km'] * 1000
    GH = cfg['ground_half_km'] * 1000
    rng = np.random.default_rng(7)

    def P(g):
        return [((p['lon'] - lon0) * kx, (p['lat'] - lat0) * ky) for p in g]

    def ways_polys(els):
        polys = []
        for e in els:
            if e['type'] == 'way' and 'geometry' in e and len(e['geometry']) >= 4:
                pts = P(e['geometry'])
                if pts[0] == pts[-1] or math.dist(pts[0], pts[-1]) < 0.5:
                    polys.append((Polygon(pts), e.get('tags', {})))
            elif e['type'] == 'relation':
                outers = [LineString(P(m['geometry'])) for m in e.get('members', [])
                          if m.get('role') == 'outer' and m.get('geometry') and len(m['geometry']) >= 2]
                if outers:
                    for pg in polygonize(linemerge(unary_union(outers))):
                        polys.append((pg, e.get('tags', {})))
        return polys

    # ---------------- buildings
    def parse_h(t):
        for k in ('height', 'building:height'):
            v = t.get(k)
            if v:
                try:
                    return float(v.replace('m', '').replace(',', '.').strip()), True
                except ValueError:
                    pass
        v = t.get('building:levels')
        if v:
            try:
                return float(v.split(';')[0].replace(',', '.')) * 3.1 + 1.0, True
            except ValueError:
                pass
        return None, False

    def year(t):
        v = t.get('start_date', '') or t.get('construction_date', '')
        digits = ''.join(ch if ch.isdigit() else ' ' for ch in v).split()
        for s in digits:
            if len(s) == 4 and 100 < int(s) <= 2026:
                return int(s)
        return None

    clip_b = box(-BH, -BH, BH, BH)
    rings, offs, H, A, walls, roofs = [], [0], [], [], [], []
    n_tag_h = n_year = 0
    WALL = np.array([[236, 228, 212], [242, 236, 224], [226, 214, 190], [232, 222, 206], [218, 206, 186],
                     [240, 230, 214], [214, 200, 178], [228, 220, 210]]) / 255.0
    OLDW = np.array([[222, 196, 160], [206, 176, 140], [232, 210, 176], [196, 166, 128]]) / 255.0
    for pg, t in ways_polys(d['buildings']):
        if t.get('building') in ('roof', 'construction', 'ruins', 'no') or not pg.is_valid:
            pg = pg.buffer(0) if not pg.is_valid else pg
            if t.get('building') in ('roof', 'construction', 'ruins', 'no'):
                continue
        if pg.is_empty or not clip_b.contains(pg.representative_point()):
            continue
        if pg.geom_type != 'Polygon':
            pg = max(pg.geoms, key=lambda g: g.area) if hasattr(pg, 'geoms') else pg
            if pg.geom_type != 'Polygon':
                continue
        if pg.area < 15:
            continue
        pg = pg.simplify(0.4)
        ring = list(pg.exterior.coords)[:-1]
        if len(ring) < 3:
            continue
        # counter-clockwise so walls face outward
        area2 = sum(ring[i][0] * ring[(i + 1) % len(ring)][1] - ring[(i + 1) % len(ring)][0] * ring[i][1]
                    for i in range(len(ring)))
        if area2 < 0:
            ring = ring[::-1]
        c = pg.centroid
        dist = math.hypot(c.x - ox, c.y - oy)
        kind = t.get('building', 'yes')
        h, tagged = parse_h(t)
        if tagged:
            n_tag_h += 1
        else:
            if kind in ('house', 'detached', 'bungalow', 'shed', 'garage', 'garages', 'hut', 'kiosk', 'service'):
                h = rng.uniform(3.5, 7.5)
            elif kind in ('mosque', 'church'):
                h = 14.0
            elif dist < 450:  # Kaleiçi: low historic houses
                h = rng.uniform(5.0, 9.0)
            elif pg.area > 2500:
                h = rng.uniform(10, 18)
            else:  # typical Antalya 4-6 storey apartment
                h = float(rng.choice([9.5, 12.5, 15.5, 18.5], p=[0.2, 0.35, 0.3, 0.15]) + rng.uniform(-0.8, 0.8))
        h = float(np.clip(h, 2.5, 180))
        y = year(t)
        if y:
            n_year += 1
            a = float(np.clip((y - 1300) / (2026 - 1300), 0, 1)) ** 1.6
        else:
            a = (dist / (BH * 1.25)) ** 0.85 * 0.82 + rng.normal(0, 0.06)
            if dist < 450 and h < 10:
                a = rng.uniform(0.0, 0.08)
            if h > 30:
                a += 0.12
        A.append(float(np.clip(a, 0, 1)))
        H.append(h)
        rings.extend(ring)
        offs.append(len(rings))
        if dist < 450 and h < 10:
            walls.append(OLDW[rng.integers(len(OLDW))] * rng.uniform(0.95, 1.03))
            roofs.append(np.array([178, 92, 62]) / 255.0 * rng.uniform(0.85, 1.08))
        else:
            walls.append(WALL[rng.integers(len(WALL))] * rng.uniform(0.96, 1.02))
            g = rng.uniform(0.66, 0.80)
            roofs.append(np.array([g, g * 0.98, g * 0.95]) if rng.random() > 0.12 else np.array([176, 96, 66]) / 255.0)
    nb = len(H)
    np.savez_compressed(os.path.join(out, 'scene.npz'), ring=np.array(rings, np.float32), off=np.array(offs, np.int64),
                        h=np.array(H, np.float32), appear=np.array(A, np.float32),
                        wall=np.clip(np.array(walls), 0, 1).astype(np.float32),
                        roof=np.clip(np.array(roofs), 0, 1).astype(np.float32))

    # ---------------- ground texture
    S = 4096
    def px(x, y):
        return ((x + GH) / (2 * GH) * S, (GH - y) / (2 * GH) * S)
    LAND, SEA, GREEN, ROAD = (214, 204, 182), (38, 104, 132), (150, 168, 112), (236, 232, 222)
    img = Image.new('RGB', (S, S), LAND)
    wm = Image.new('L', (S, S), 0)
    dr, dw = ImageDraw.Draw(img), ImageDraw.Draw(wm)
    clip_g = box(-GH, -GH, GH, GH)

    def fill(geom, col, mask=None):
        gs = getattr(geom, 'geoms', [geom])
        for g in gs:
            if g.geom_type != 'Polygon' or g.is_empty:
                continue
            dr.polygon([px(*p) for p in g.exterior.coords], fill=col)
            if mask is not None:
                dw.polygon([px(*p) for p in g.exterior.coords], fill=mask)
            for hole in g.interiors:
                dr.polygon([px(*p) for p in hole.coords], fill=LAND)
                if mask is not None:
                    dw.polygon([px(*p) for p in hole.coords], fill=0)

    # sea from the coastline: land is on the left of OSM coastline ways
    coast = [LineString(P(e['geometry'])) for e in d['coastline'] if len(e.get('geometry', [])) >= 2]
    sea_area = 0.0
    if coast:
        lines = unary_union(coast).intersection(clip_g.buffer(1))
        faces = list(polygonize(unary_union([clip_g.boundary, lines])))
        segs = []
        for cl in coast:
            cs = list(cl.coords)
            segs += [(cs[i], cs[i + 1]) for i in range(len(cs) - 1)]
        sa = np.array([s[0] for s in segs]); sb = np.array([s[1] for s in segs])
        for f in faces:
            p = f.representative_point(); q = np.array([p.x, p.y])
            ab = sb - sa; t = np.clip(((q - sa) * ab).sum(1) / np.maximum((ab * ab).sum(1), 1e-9), 0, 1)
            near = sa + ab * t[:, None]
            i = int(np.argmin(((near - q) ** 2).sum(1)))
            cross = ab[i, 0] * (q[1] - sa[i, 1]) - ab[i, 1] * (q[0] - sa[i, 0])
            if cross < 0:  # right of the coastline -> sea
                fill(f, SEA, 255); sea_area += f.area
    for pg, t in ways_polys(d['green']):
        col = (222, 210, 170) if t.get('natural') in ('beach', 'sand') else GREEN
        fill(pg.intersection(clip_g) if pg.is_valid else pg.buffer(0).intersection(clip_g), col)
    for e in d['water']:
        if e['type'] == 'way' and e.get('tags', {}).get('waterway') and 'geometry' in e:
            dr.line([px(*p) for p in P(e['geometry'])], fill=SEA, width=6); dw.line([px(*p) for p in P(e['geometry'])], fill=255, width=6)
    for pg, t in ways_polys([e for e in d['water'] if not e.get('tags', {}).get('waterway')]):
        fill(pg if pg.is_valid else pg.buffer(0), SEA, 255)
    W = {'motorway': 14, 'trunk': 13, 'primary': 11, 'secondary': 9, 'tertiary': 8, 'residential': 5,
         'unclassified': 5, 'living_street': 4, 'pedestrian': 4, 'service': 3}
    for e in sorted(d['roads'], key=lambda e: W.get(e.get('tags', {}).get('highway'), 3)):
        if 'geometry' not in e:
            continue
        w = W.get(e.get('tags', {}).get('highway'), 3) * S / (2 * GH) * 1.0
        dr.line([px(*p) for p in P(e['geometry'])], fill=ROAD, width=max(1, int(round(w))), joint='curve')
    img.save(os.path.join(out, 'ground.png')); wm.save(os.path.join(out, 'water.png'))
    meta = {'buildings': nb, 'tagged_height_share': round(n_tag_h / max(nb, 1), 3), 'dated_share': round(n_year / max(nb, 1), 3),
            'ground_half_m': GH, 'build_half_m': BH, 'sea_km2': round(sea_area / 1e6, 2), 'center': cfg['center'],
            'old_town_xy': [ox, oy], 'camera': cfg.get('camera', {})}
    json.dump(meta, open(os.path.join(out, 'meta.json'), 'w'), indent=1)
    print(json.dumps(meta))


if __name__ == '__main__':
    main()
