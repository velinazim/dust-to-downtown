"""Traces the New Danube channel (dug 1972–1988) and the Danube Island strip from the real water in geo.json.
Used by _build.py; returns (new_danube_poly, island_strip_poly) or (None, None) without geo.json."""
import base64, json, math, os
import numpy as np

KZ = 110.574


def trace(geo_path):
    if not os.path.exists(geo_path):
        return None, None
    G = json.load(open(geo_path)); lat0, lon0 = G['origin']; KX = 111.32 * math.cos(math.radians(lat0))
    lay = lambda g: np.frombuffer(base64.b64decode(g['sd_b64']), '<i2').reshape(g['nz'], g['nx'])
    def runs(g, a, j):
        row = a[j] < 0; out = []; i = 0
        while i < g['nx']:
            if row[i]:
                k = i
                while k < g['nx'] and row[k]: k += 1
                lo0 = lon0 + (g['x0'] + (i - 0.5) * g['cell_km']) / KX; lo1 = lon0 + (g['x0'] + (k - 0.5) * g['cell_km']) / KX
                out.append((lo0, lo1)); i = k
            else:
                i += 1
        return out
    lat_of = lambda g, j: lat0 - (g['z0'] + j * g['cell_km']) / KZ
    core, full = G['core'], G
    ac, af = lay(core), lay(full)
    left, right, mid = [], [], []          # ND west edge, ND east edge, main Danube east edge
    clat_hi, clat_lo = lat_of(core, 0), lat_of(core, core['nz'] - 1)
    # full layer north of the core: combined band, ND = its eastern 0.0034° (≈250 m across the row)
    for j in range(full['nz']):
        la = lat_of(full, j)
        if not (clat_hi < la < 48.297): continue
        rs = [r for r in runs(full, af, j) if 16.33 < (r[0] + r[1]) / 2 < 16.40 and r[1] - r[0] > 0.004]
        if not rs: continue
        r = max(rs, key=lambda r: r[1] - r[0])
        right.append((la, r[1] + 0.0004)); left.append((la, r[1] - 0.0034)); mid.append((la, r[0] + 0.0045))
    # core layer: main channel = first wide run, ND = the next run to the east
    for j in range(0, core['nz'], 3):
        la = lat_of(core, j)
        rs = [r for r in runs(core, ac, j) if r[1] - r[0] > 0.0012 and r[0] > 16.36]
        if len(rs) < 2: continue
        m, nd = rs[0], rs[1]
        if nd[0] - m[1] > 0.006 or (nd[1] - nd[0]) > 0.006: continue
        right.append((la, nd[1] + 0.0004)); left.append((la, nd[0] - 0.0004)); mid.append((la, m[1] + 0.0002))
    clo_hi = lon0 + (core['x0'] + (core['nx'] - 1) * core['cell_km']) / KX
    # full layer south-east of the core
    for j in range(full['nz']):
        la = lat_of(full, j)
        if not (48.162 < la < 48.212): continue
        rs = [r for r in runs(full, af, j) if 16.42 < (r[0] + r[1]) / 2 < 16.53 and r[1] - r[0] > 0.004]
        if not rs: continue
        r = max(rs, key=lambda r: r[1] - r[0])
        if r[1] < clo_hi and la > clat_lo: continue
        right.append((la, r[1] + 0.0004)); left.append((la, r[1] - 0.0036)); mid.append((la, r[0] + 0.0050))
    order = lambda pts: sorted(pts, key=lambda p: -p[0])
    left, right, mid = order(left), order(right), order(mid)
    # smooth (running mean over 5) to remove cell steps
    def smooth(pts):
        out = []
        for i in range(len(pts)):
            w = pts[max(0, i - 2): i + 3]
            out.append((pts[i][0], sum(p[1] for p in w) / len(w)))
        return out[::2] + ([out[-1]] if len(out) % 2 == 0 else [])
    left, right, mid = smooth(left), smooth(right), smooth(mid)
    nd = [(round(a, 5), round(b, 5)) for a, b in left + list(reversed(right))]
    isl = [(round(a, 5), round(b, 5)) for a, b in mid + list(reversed(right))]
    return nd, isl
