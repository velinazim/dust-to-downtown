"""One-off: the elevation tiles leave 0–3 m 'land' stripes in the Pacific along the whole coast (preview round 1).
Find cells that are low (≤ 3 m) and mostly surrounded by water, and write them as water polygons to _coast_fix.json
(used as geo_edits by _build.py). Run once against the first geo.json: python3 cities/los-angeles/_coast_fix.py"""
import base64, json, math, os
import numpy as np
from scipy import ndimage
from shapely.geometry import box
from shapely.ops import unary_union
HERE = os.path.dirname(os.path.abspath(__file__))
g = json.load(open(os.path.join(HERE, 'geo.json')))
nx, nz, c = g['nx'], g['nz'], g['cell_km']
el = np.frombuffer(base64.b64decode(g['elev_b64']), '<i2').reshape(nz, nx).astype(float)
sd = np.frombuffer(base64.b64decode(g['sd_b64']), '<i2').reshape(nz, nx)
water = sd <= 0
ocean = np.zeros_like(water)
lab, n = ndimage.label(water); big = np.argmax(np.bincount(lab.ravel())[1:]) + 1; ocean = lab == big
f = ndimage.uniform_filter(water.astype(float), 9)
near = ndimage.binary_dilation(ocean, iterations=30)
fix = near & (el <= 3) & (f > 0.25)
fix = ndimage.binary_closing(fix | ocean, iterations=2) & (el <= 3) & near
fix = ndimage.binary_opening(fix, iterations=1) & ~water
lat0, lon0 = g['origin']; k = 111.32 * math.cos(math.radians(lat0))
boxes = []
for j in range(nz):
    row = fix[j]; i = 0
    while i < nx:
        if row[i]:
            s = i
            while i < nx and row[i]: i += 1
            x0 = g['x0'] + (s - 0.5) * c; x1 = g['x0'] + (i - 0.5) * c
            z0 = g['z0'] + (j - 0.5) * c; z1 = g['z0'] + (j + 0.5) * c
            boxes.append(box(lon0 + x0 / k, lat0 - z1 / 110.574, lon0 + x1 / k, lat0 - z0 / 110.574))
        else:
            i += 1
u = unary_union(boxes).buffer(0.0002).buffer(-0.0001).simplify(0.0003)
parts = [u] if u.geom_type == 'Polygon' else list(u.geoms)
polys = []
for p in parts:
    if p.area < 2e-6: continue
    polys.append([[round(y, 5), round(x, 5)] for x, y in p.exterior.coords][:-1])
json.dump(polys, open(os.path.join(HERE, '_coast_fix.json'), 'w'))
print('cells fixed', int(fix.sum()), 'polys', len(polys), 'pts', sum(len(p) for p in polys))
new = (~water) & ~fix
from PIL import Image
Image.fromarray(np.where(new, 200, 40).astype(np.uint8)).resize((nx * 2, nz * 2), Image.NEAREST).save('/tmp/claude-0/la/land2.png')
