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
from geo_common import make_grid, signed_distance, write_geo, rasterize

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
    q = f"""[out:json][timeout:240];
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
            r = requests.post(url, data={'data': q}, headers=UA, timeout=300)
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
    return hashlib.sha1(json.dumps([city['geo'], city.get('geo_edits', [])], sort_keys=True).encode()).hexdigest()[:12]


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
    cell_km = g.get('cell_m', 60) / 1000
    grid = make_grid(bbox, origin, cell_km)
    print(f'grid {grid["nx"]}x{grid["nz"]} @ {cell_km * 1000:.0f} m')
    elev = elevation(grid, cell_km, origin[0])
    sea_level = g.get('sea_level_m', 0.0)
    land = elev > sea_level
    if g.get('osm_water', True):
        outer, inner = osm_water(bbox)
        wmask = rasterize(outer, grid, origin) & ~rasterize(inner, grid, origin)
        land &= ~wmask
    for ed in city.get('geo_edits', []):
        m = rasterize([ed['poly']], grid, origin)
        land = (land | m) if ed['op'] == 'land' else (land & ~m)
    # remove specks
    land = ndimage.binary_opening(land, iterations=1) | (ndimage.binary_erosion(land, iterations=2))
    sd = signed_distance(land, cell_km)
    elev = np.where(land, np.maximum(elev, 0.5), np.minimum(elev, -1))
    out = write_geo(os.path.join(city_dir, 'geo.json'), origin, grid, cell_km, elev, sd,
                    meta=dict(source='AWS terrain tiles (terrarium) + OpenStreetMap water (ODbL)', bbox=bbox, geo_hash=geo_hash(city)))
    print('wrote geo.json', out['nx'], 'x', out['nz'])


if __name__ == '__main__':
    main(sys.argv[1], '--if-needed' in sys.argv)
