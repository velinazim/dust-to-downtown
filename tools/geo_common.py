"""Shared helpers for building cities/<slug>/geo.json.

geo.json format (read by engine/index.html):
  origin   [lat, lon]   projection origin (engine x = east km, z = south km)
  x0, z0   km           position of grid cell (0,0)
  cell_km  km           grid spacing
  nx, nz                grid size
  elev_b64              int16 little-endian, meters above sea level (row-major, z rows)
  sd_b64                int16, signed distance to the shoreline in meters (+ land, - water)
"""
import base64, json, math
import numpy as np
from scipy import ndimage

KZ = 110.574


def kx(lat0):
    return 111.32 * math.cos(math.radians(lat0))


def make_grid(bbox, origin, cell_km):
    s, w, n, e = bbox
    lat0, lon0 = origin
    x_w, x_e = (w - lon0) * kx(lat0), (e - lon0) * kx(lat0)
    z_n, z_s = -(n - lat0) * KZ, -(s - lat0) * KZ
    nx = int(math.ceil((x_e - x_w) / cell_km)) + 1
    nz = int(math.ceil((z_s - z_n) / cell_km)) + 1
    xs = x_w + np.arange(nx) * cell_km
    zs = z_n + np.arange(nz) * cell_km
    lons = lon0 + xs / kx(lat0)
    lats = lat0 - zs / KZ
    return dict(x0=x_w, z0=z_n, nx=nx, nz=nz, xs=xs, zs=zs, lons=lons, lats=lats)


def signed_distance(land_mask, cell_km):
    """+ meters inside land, - meters in water."""
    cell_m = cell_km * 1000
    d_in = ndimage.distance_transform_edt(land_mask) * cell_m
    d_out = ndimage.distance_transform_edt(~land_mask) * cell_m
    sd = np.where(land_mask, d_in - cell_m * 0.5, -(d_out - cell_m * 0.5))
    # soften the raster staircase so the shoreline renders as a smooth curve
    return ndimage.gaussian_filter(sd, sigma=1.1)


def write_geo(path, origin, grid, cell_km, elev_m, sd_m, meta=None):
    e = np.clip(np.round(elev_m), -500, 4000).astype('<i2')
    d = np.clip(np.round(sd_m), -32000, 32000).astype('<i2')
    out = dict(origin=list(origin), x0=float(grid['x0']), z0=float(grid['z0']), cell_km=cell_km,
               nx=int(grid['nx']), nz=int(grid['nz']),
               elev_b64=base64.b64encode(e.tobytes()).decode(), sd_b64=base64.b64encode(d.tobytes()).decode(),
               meta=meta or {})
    with open(path, 'w') as f:
        json.dump(out, f, separators=(',', ':'))
    return out


def rasterize(polys_ll, grid, origin):
    """polys_ll: list of [[lat,lon],...] rings -> bool mask (nz, nx), even-odd fill."""
    from PIL import Image, ImageDraw
    lat0, lon0 = origin
    img = Image.new('L', (grid['nx'], grid['nz']), 0)
    dr = ImageDraw.Draw(img)
    c = grid['xs'][1] - grid['xs'][0]
    for ring in polys_ll:
        pts = [(((lon - lon0) * kx(lat0) - grid['x0']) / c, (-(lat - lat0) * KZ - grid['z0']) / c) for lat, lon in ring]
        if len(pts) >= 3:
            dr.polygon(pts, fill=1)
    return np.array(img, dtype=bool)
