"""Build cities/<slug>/geo.json from real data (runs in GitHub Actions, which has open internet).

Sources:
  - Elevation + bathymetry: AWS Terrain Tiles (terrarium PNG), public, no key.
  - Rivers/lakes: OpenStreetMap water polygons via the Overpass API.
  - Optional historical edits from city.json "geo_edits": [{"op": "water"|"land", "poly": [[lat,lon],...]}]

usage: python3 tools/prepare_geo.py cities/<slug>
"""
import io, json, math, os, sys, time
import numpy as np
import requests
from PIL import Image
from scipy import ndimage
sys.path.insert(0, os.path.dirname(__file__))
from geo_common import make_grid, signed_distance, write_geo, rasterize, kx, KZ

UA = {'User-Agent': 'dust-to-downtown/1.0 (github.com/velinazim/dust-to-downtown)'}
TILE = 'https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png'
OVERPASS = ['https://overpass-api.de/api/interpreter', 'https://overpass.kumi.systems/api/interpreter',
            'https://maps.mail.ru/osm/tools/overpass/api/interpreter']


def deg2tile(lat, lon, z):
    n = 2 ** z
    x = (lon + 180) / 360 * n
    y = (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n
    return x, y


def fetch(url, tries=4, **kw):
    for i in range(tries):
        try:
            r = requests.get(url, headers=UA, timeout=120, **kw)
            if r.status_code == 200:
                return r
            print('  http', r.status_code, url[:90])
        except Exception as e:
            print('  err', e)
        time.sleep(3 * (i + 1))
    raise RuntimeError('failed: ' + url)


def elevation(grid, cell_km, lat_c):
    # tile pixel ~ cell/2
    z = int(np.clip(round(math.log2(156543.0 * math.cos(math.radians(lat_c)) / (cell_km * 500))), 8, 13))
    lats, lons = grid['lats'], grid['lons']
    xa, ya = deg2tile(lats.max(), lons.min(), z)
    xb, yb = deg2tile(lats.min(), lons.max(), z)
    tx0, tx1, ty0, ty1 = int(xa), int(xb), int(ya), int(yb)
    print(f'elevation: zoom {z}, tiles {tx1 - tx0 + 1}x{ty1 - ty0 + 1}')
    mosaic = np.zeros(((ty1 - ty0 + 1) * 256, (tx1 - tx0 + 1) * 256), dtype=np.float32)
    for ty in range(ty0, ty1 + 1):
        for tx in range(tx0, tx1 + 1):
            im = np.array(Image.open(io.BytesIO(fetch(TILE.format(z=z, x=tx, y=ty)).content)).convert('RGB'), dtype=np.float32)
            e = im[..., 0] * 256 + im[..., 1] + im[..., 2] / 256 - 32768
            mosaic[(ty - ty0) * 256:(ty - ty0 + 1) * 256, (tx - tx0) * 256:(tx - tx0 + 1) * 256] = e
    LON, LAT = np.meshgrid(lons, lats)
    px, py = deg2tile(LAT, LON, z)
    px = (px - tx0) * 256 - 0.5
    py = (py - ty0) * 256 - 0.5
    return ndimage.map_coordinates(mosaic, [py, px], order=1, mode='nearest')


def osm_water(bbox):
    s, w, n, e = bbox
    q = f"""[out:json][timeout:600][maxsize:1073741824];
(
  way["natural"="water"]({s},{w},{n},{e});
  relation["natural"="water"]({s},{w},{n},{e});
  way["waterway"="riverbank"]({s},{w},{n},{e});
  relation["waterway"="riverbank"]({s},{w},{n},{e});
  way["natural"="bay"]({s},{w},{n},{e});
  way["landuse"="basin"]({s},{w},{n},{e});
  way["waterway"="dock"]({s},{w},{n},{e});
);
out geom;"""
    last = None
    for url in OVERPASS:
        try:
            r = requests.post(url, data={'data': q}, headers=UA, timeout=700)
            if r.status_code == 200:
                data = r.json()
                break
            last = f'{url} -> {r.status_code}'
        except Exception as ex:
            last = f'{url} -> {ex}'
        print('  overpass retry:', last)
        time.sleep(10)
    else:
        print('WARNING: Overpass unavailable, rivers/lakes skipped:', last)
        return [], []
    outer, inner = [], []
    for el in data.get('elements', []):
        if el['type'] == 'way' and 'geometry' in el:
            ring = [[p['lat'], p['lon']] for p in el['geometry']]
            if len(ring) >= 3:
                outer.append(ring)
        elif el['type'] == 'relation':
            # stitch member ways by role
            for role, dest in (('outer', outer), ('inner', inner)):
                segs = [[[p['lat'], p['lon']] for p in m['geometry']] for m in el.get('members', []) if m.get('role') == role and 'geometry' in m]
                dest.extend(stitch(segs))
    print(f'osm water: {len(outer)} outer rings, {len(inner)} inner rings')
    return outer, inner


def stitch(segs):
    rings, segs = [], [s[:] for s in segs if len(s) >= 2]
    while segs:
        cur = segs.pop(0)
        changed = True
        while changed and cur[0] != cur[-1]:
            changed = False
            for i, s in enumerate(segs):
                if s[0] == cur[-1]:
                    cur += s[1:]; segs.pop(i); changed = True; break
                if s[-1] == cur[-1]:
                    cur += s[::-1][1:]; segs.pop(i); changed = True; break
        if len(cur) >= 3:
            rings.append(cur)
    return rings


def geo_hash(city):
    import hashlib
    return hashlib.sha1(json.dumps([city['geo'], city.get('geo_edits', []), [t['poly'] for t in city.get('timed_water', [])]],
                                   sort_keys=True).encode()).hexdigest()[:12]


def river_mask(path_ll, width_m, grid, origin):
    """Thick polyline -> bool mask (fallback for rivers OSM maps as coastline or lines only)."""
    from PIL import Image, ImageDraw
    lat0, lon0 = origin
    c = grid['xs'][1] - grid['xs'][0]
    img = Image.new('L', (grid['nx'], grid['nz']), 0)
    pts = [(((lon - lon0) * kx(lat0) - grid['x0']) / c, (-(lat - lat0) * KZ - grid['z0']) / c) for lat, lon in path_ll]
    w = max(1, int(round(width_m / 1000 / c)))
    ImageDraw.Draw(img).line(pts, fill=1, width=w, joint='curve')
    for x, y in pts:
        r = w / 2
        ImageDraw.Draw(img).ellipse((x - r, y - r, x + r, y + r), fill=1)
    return np.array(img, dtype=bool)


def build_layer(city, bbox, origin, cell_km, water_rings):
    g = city['geo']
    grid = make_grid(bbox, origin, cell_km)
    print(f'grid {grid["nx"]}x{grid["nz"]} @ {cell_km * 1000:.0f} m')
    elev = elevation(grid, cell_km, origin[0])
    land = elev > g.get('sea_level_m', 0.0)
    if water_rings is not None:
        outer, inner = water_rings
        land &= ~(rasterize(outer, grid, origin) & ~rasterize(inner, grid, origin))
    for ed in city.get('geo_edits', []):
        if ed['op'] == 'river':
            land &= ~river_mask(ed['path'], ed.get('width_m', 200), grid, origin)
            continue
        m = rasterize([ed['poly']], grid, origin)
        land = (land | m) if ed['op'] == 'land' else (land & ~m)
    # docks/lakes dug later are land in the base map; the engine floods them at their year
    for tw in city.get('timed_water', []):
        land |= rasterize([tw['poly']], grid, origin)
    land = ndimage.binary_opening(land, iterations=1)
    sd = signed_distance(land, cell_km)
    elev = np.where(land, np.maximum(elev, 0.5), np.minimum(elev, -1))
    return grid, elev, sd, land


def main(city_dir, if_needed=False):
    city = json.load(open(os.path.join(city_dir, 'city.json')))
    g = city['geo']
    gp = os.path.join(city_dir, 'geo.json')
    if g.get('manual') and os.path.exists(gp):
        print('geo.json is hand-made (geo.manual = true); not regenerated'); return
    if if_needed and os.path.exists(gp):
        try:
            if json.load(open(gp)).get('meta', {}).get('geo_hash') == geo_hash(city):
                print('geo.json up to date'); return
        except Exception:
            pass
    bbox = g['bbox']                     # [south, west, north, east]
    origin = g.get('origin') or [(bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2]
    rings = osm_water(bbox) if g.get('osm_water', True) else None
    grid, elev, sd, land = build_layer(city, bbox, origin, g.get('cell_m', 60) / 1000, rings)
    meta = dict(source='AWS terrain tiles (terrarium) + OpenStreetMap water (ODbL)', bbox=bbox, geo_hash=geo_hash(city),
                land_fraction=round(float(land.mean()), 4))
    out = write_geo(gp, origin, grid, g.get('cell_m', 60) / 1000, elev, sd, meta=meta)
    if g.get('core_bbox'):
        ccell = g.get('core_cell_m', 30) / 1000
        cgrid, celev, csd, cland = build_layer(city, g['core_bbox'], origin, ccell, rings)
        tmp = gp + '.core'
        core = write_geo(tmp, origin, cgrid, ccell, celev, csd, meta={'bbox': g['core_bbox'], 'land_fraction': round(float(cland.mean()), 4)})
        os.remove(tmp)
        out['core'] = {k: core[k] for k in ('x0', 'z0', 'cell_km', 'nx', 'nz', 'elev_b64', 'sd_b64', 'meta')}
        with open(gp, 'w') as f:
            json.dump(out, f, separators=(',', ':'))
        print('core layer', cgrid['nx'], 'x', cgrid['nz'])
    print('wrote geo.json', out['nx'], 'x', out['nz'])


if __name__ == '__main__':
    main(sys.argv[1], '--if-needed' in sys.argv)
