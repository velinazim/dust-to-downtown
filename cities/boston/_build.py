"""Builds cities/boston/city.json. Every date/figure is from research.md (sources listed there).
Run: python3 cities/boston/_build.py
Landfill: the modern map is land where Boston has made land since 1630. Each fill zone below is the modern land
inside a rough zone polygon minus the 1630 land (SHAWMUT, CHARLESTOWN, ...), so only the 1630 shorelines need to be
traced carefully. Zones are clipped against geo.json (modern land) when it exists; without geo.json they are left out
(first preview run only builds the modern map)."""
import json, math, os

T = lambda en, tr: {"en": en, "tr": tr}
HERE = os.path.dirname(os.path.abspath(__file__))
rect = lambda s, w, n, e: [(s, w), (n, w), (n, e), (s, e)]


def L(pts):
    return [[round(a, 5), round(b, 5)] for a, b in pts]


# ------------------------------------------------------------------ 1630 land (≈ traced from the 1630-shoreline maps
# described in research.md, between sourced points: Neck at Dover St, Dock Square, Fort Hill, Copp's Hill ...)
SHAWMUT = [
    # Neck, west shore, going north
    (42.3315, -71.0815), (42.3360, -71.0762), (42.3400, -71.0712), (42.3439, -71.0670), (42.3468, -71.0655),
    (42.3492, -71.0660), (42.3508, -71.0672), (42.3520, -71.0690), (42.3540, -71.0701), (42.3563, -71.0704),
    (42.3585, -71.0699), (42.3602, -71.0693), (42.3617, -71.0688), (42.3630, -71.0679), (42.3642, -71.0667),
    (42.3652, -71.0651), (42.3656, -71.0634),
    # North Cove (Mill Pond) shore
    (42.3648, -71.0627), (42.3638, -71.0620), (42.3629, -71.0609), (42.3623, -71.0597), (42.3629, -71.0589),
    (42.3645, -71.0587), (42.3660, -71.0585), (42.3672, -71.0583),
    # Copp's Hill and the North End
    (42.3681, -71.0566), (42.3683, -71.0546), (42.3676, -71.0528), (42.3663, -71.0519), (42.3649, -71.0522),
    (42.3637, -71.0532), (42.3627, -71.0546), (42.3617, -71.0559), (42.3608, -71.0568),
    # Town Cove, King Street, Fort Hill
    (42.3598, -71.0563), (42.3590, -71.0555), (42.3582, -71.0548), (42.3572, -71.0539), (42.3562, -71.0530),
    (42.3551, -71.0533), (42.3545, -71.0548), (42.3539, -71.0566),
    # South Cove and the Neck, east shore
    (42.3529, -71.0580), (42.3517, -71.0592), (42.3504, -71.0605), (42.3489, -71.0616), (42.3468, -71.0630),
    (42.3439, -71.0652), (42.3400, -71.0690), (42.3360, -71.0738), (42.3318, -71.0785),
]
CHARLESTOWN = [(42.3718, -71.0627), (42.3736, -71.0662), (42.3765, -71.0690), (42.3800, -71.0716), (42.3828, -71.0750),
               (42.3846, -71.0772), (42.3862, -71.0722), (42.3832, -71.0660), (42.3800, -71.0602), (42.3770, -71.0572),
               (42.3745, -71.0566), (42.3728, -71.0587)]
SOUTHBOSTON = [(42.3418, -71.0565), (42.3410, -71.0500), (42.3401, -71.0420), (42.3392, -71.0350), (42.3381, -71.0280),
               (42.3376, -71.0212), (42.3350, -71.0185), (42.3322, -71.0250), (42.3311, -71.0350), (42.3300, -71.0450),
               (42.3286, -71.0530), (42.3290, -71.0575), (42.3335, -71.0590)]
NODDLE = [(42.3648, -71.0372), (42.3700, -71.0402), (42.3760, -71.0412), (42.3810, -71.0392), (42.3842, -71.0332),
          (42.3812, -71.0288), (42.3760, -71.0298), (42.3700, -71.0300), (42.3655, -71.0310), (42.3640, -71.0336)]
CASTLE_ISLAND = rect(42.3360, -71.0132, 42.3393, -71.0083)
ORIGINAL = [SHAWMUT, CHARLESTOWN, SOUTHBOSTON, NODDLE, CASTLE_ISLAND]

# ------------------------------------------------------------------ fill zones: (name, to_year, rough zone polygon)
# to_year = when the zone is shown as land. Sourced: Mill Pond 1807–c.1828 (MHC); South Cove 1833–1845; Back Bay
# 1857–1882 east→west, to Massachusetts Ave by 1881, Kenmore 1890, Fens 1900; South End 1830s–1870s; Atlantic Ave late
# 1860s + 1872 rubble; Long Wharf 1710–1721; Mill Dam 1821; railroad causeways 1834–1835; Logan 1923 + 1940s–1950s;
# Castle Island joined 1928. Zones marked ≈ in research.md are reconstructions inside a sourced range.
def strip(a, b, half_m=22):
    (la, oa), (lb, ob) = a, b
    k = 111.32 * math.cos(math.radians(42.355)); dx, dy = (ob - oa) * k, (lb - la) * 110.574
    n = math.hypot(dx, dy); px, py = -dy / n * half_m / 1000, dx / n * half_m / 1000
    o = (px / k, py / 110.574)
    return [(la + o[1], oa + o[0]), (lb + o[1], ob + o[0]), (lb - o[1], ob - o[0]), (la - o[1], oa - o[0])]


def lon_strip(w, e, s=42.3420, n=42.3640):
    return rect(s, w, n, e)


ZONES = [
    # ---- Shawmut: north and west
    ("Mill Pond (south half)", 1817, rect(42.3615, -71.0645, 42.3641, -71.0580)),
    ("Mill Pond (north half)", 1828, [(42.3641, -71.0650), (42.3656, -71.0652), (42.3664, -71.0620), (42.3672, -71.0590),
                                     (42.3672, -71.0580), (42.3641, -71.0580)]),
    ("North Station flats ≈", 1850, [(42.3656, -71.0652), (42.3700, -71.0670), (42.3712, -71.0600), (42.3680, -71.0575),
                                    (42.3672, -71.0590), (42.3664, -71.0620)]),
    ("West Cove / West End ≈", 1830, [(42.3600, -71.0693), (42.3600, -71.0735), (42.3700, -71.0735), (42.3700, -71.0670),
                                     (42.3656, -71.0652)]),
    ("Charles St and Public Garden ≈", 1830, rect(42.3505, -71.0735, 42.3600, -71.0690)),
    ("Bay Village / Park Square ≈", 1830, rect(42.3470, -71.0735, 42.3505, -71.0640)),
    # ---- Back Bay, east → west (linear between the sourced 1857 start and "to Massachusetts Ave by 1881")
    ("Back Bay to Berkeley St", 1861, lon_strip(-71.0742, -71.0735, 42.3470, 42.3640)),
    ("Back Bay to Dartmouth St", 1866, lon_strip(-71.0778, -71.0742, 42.3470, 42.3640)),
    ("Back Bay to Fairfield St", 1871, lon_strip(-71.0815, -71.0778, 42.3470, 42.3640)),
    ("Back Bay to Hereford St", 1876, lon_strip(-71.0850, -71.0815, 42.3470, 42.3640)),
    ("Back Bay to Massachusetts Ave", 1881, lon_strip(-71.0885, -71.0850, 42.3470, 42.3640)),
    ("Kenmore / Bay State Road", 1890, [(42.3465, -71.0885), (42.3560, -71.0885), (42.3530, -71.1220), (42.3515, -71.1220),
                                        (42.3500, -71.1100), (42.3490, -71.1040), (42.3465, -71.1000)]),
    ("Back Bay south (rail yards) ≈", 1882, [(42.3470, -71.0735), (42.3470, -71.0885), (42.3420, -71.0885), (42.3420, -71.0800)]),
    ("Fens and Roxbury flats", 1900, [(42.3465, -71.1030), (42.3465, -71.0885), (42.3420, -71.0885), (42.3420, -71.0800),
                                     (42.3360, -71.0790), (42.3355, -71.0860), (42.3380, -71.0960), (42.3420, -71.1030)]),
    # ---- South End (1830s–1870s), north half first
    ("South End (north)", 1850, [(42.3470, -71.0735), (42.3470, -71.0580), (42.3430, -71.0580), (42.3420, -71.0800)]),
    ("South End (south)", 1870, [(42.3430, -71.0580), (42.3420, -71.0800), (42.3360, -71.0790), (42.3330, -71.0700),
                                 (42.3360, -71.0620), (42.3400, -71.0590)]),
    ("South Bay ≈", 1900, [(42.3400, -71.0590), (42.3360, -71.0620), (42.3330, -71.0700), (42.3270, -71.0700),
                          (42.3260, -71.0580), (42.3335, -71.0575)]),
    # ---- Shawmut: east (Town Cove, waterfront, South Cove)
    ("Town Cove inner wharves ≈", 1760, [(42.3640, -71.0560), (42.3640, -71.0545), (42.3580, -71.0545), (42.3570, -71.0545),
                                        (42.3580, -71.0570), (42.3610, -71.0575)]),
    ("Quincy Market land", 1825, rect(42.3593, -71.0560, 42.3612, -71.0528)),
    ("North End waterfront ≈", 1840, [(42.3700, -71.0600), (42.3700, -71.0470), (42.3640, -71.0470), (42.3640, -71.0545),
                                     (42.3672, -71.0580), (42.3680, -71.0575)]),
    ("Atlantic Avenue waterfront", 1873, [(42.3640, -71.0545), (42.3640, -71.0470), (42.3520, -71.0470), (42.3520, -71.0535),
                                         (42.3570, -71.0545), (42.3580, -71.0545)]),
    ("South Cove (north)", 1840, rect(42.3500, -71.0610, 42.3545, -71.0530)),
    ("South Cove (south)", 1845, [(42.3500, -71.0610), (42.3500, -71.0540), (42.3470, -71.0560), (42.3470, -71.0640)]),
    # ---- South Boston
    ("Fort Point (inner)", 1860, rect(42.3418, -71.0545, 42.3530, -71.0500)),
    ("Fort Point (outer)", 1880, rect(42.3400, -71.0500, 42.3530, -71.0450)),
    ("Commonwealth Flats ≈", 1900, rect(42.3392, -71.0450, 42.3560, -71.0340)),
    ("Outer South Boston flats ≈", 1915, rect(42.3375, -71.0340, 42.3560, -71.0200)),
    ("Castle Island link", 1928, rect(42.3300, -71.0200, 42.3420, -71.0050)),
    # ---- Charlestown, Cambridge, East Boston
    ("Charlestown waterfront ≈", 1880, [(42.3700, -71.0740), (42.3720, -71.0560), (42.3760, -71.0450), (42.3880, -71.0560),
                                       (42.3880, -71.0760), (42.3846, -71.0790)]),
    ("East Cambridge ≈", 1850, [(42.3760, -71.0760), (42.3700, -71.0740), (42.3640, -71.0760), (42.3640, -71.0882),
                               (42.3655, -71.0880), (42.3690, -71.0870), (42.3720, -71.0840), (42.3760, -71.0790)]),
    ("Cambridge riverbank (MIT site) ≈", 1895, [(42.3640, -71.0760), (42.3560, -71.0760), (42.3520, -71.1180), (42.3575, -71.1180),
                                               (42.3575, -71.1080), (42.3590, -71.1030), (42.3605, -71.0960), (42.3630, -71.0900),
                                               (42.3640, -71.0882)]),
    ("East Boston waterfront ≈", 1870, [(42.3620, -71.0450), (42.3880, -71.0450), (42.3880, -71.0340), (42.3640, -71.0330)]),
    ("Boston Airport (1923)", 1923, [(42.3655, -71.0310), (42.3700, -71.0300), (42.3700, -71.0230), (42.3610, -71.0230),
                                     (42.3600, -71.0320)]),
    ("Logan Airport (1940s)", 1950, [(42.3700, -71.0300), (42.3785, -71.0290), (42.3785, -71.0100), (42.3600, -71.0100),
                                     (42.3610, -71.0230), (42.3700, -71.0230)]),
    ("Logan Airport (1950s)", 1960, [(42.3785, -71.0290), (42.3790, -71.0100), (42.3790, -70.9850), (42.3550, -70.9850),
                                     (42.3550, -71.0100), (42.3785, -71.0100)]),
]
# made-land strips that appear first (they then split the zones around them)
STRIPS = [
    ("Long Wharf", 1716, strip((42.3596, -71.0553), (42.3601, -71.0465), 20)),
    ("Mill Dam (Beacon Street)", 1821, strip((42.3560, -71.0702), (42.3489, -71.0955), 22)),
    ("Boston and Providence causeway", 1835, strip((42.3503, -71.0683), (42.3364, -71.0890), 18)),
    ("Boston and Worcester causeway", 1835, strip((42.3478, -71.0655), (42.3473, -71.0760), 18) ),
    ("Boston and Worcester causeway (west)", 1835, strip((42.3473, -71.0760), (42.3482, -71.0990), 18)),
]


def build_fill():
    """Fill zones clipped to the modern land in geo.json (minus the 1630 land and minus the strips)."""
    gp = os.path.join(HERE, 'geo.json')
    if not os.path.exists(gp):
        return [], False
    import base64
    import numpy as np
    from shapely.geometry import Polygon, box
    from shapely.ops import unary_union
    g = json.load(open(gp)); c = g['core']; lat0, lon0 = g['origin']
    k = 111.32 * math.cos(math.radians(lat0)); KZ = 110.574
    from scipy import ndimage
    from PIL import Image, ImageDraw
    el = np.frombuffer(base64.b64decode(c['elev_b64']), dtype='<i2').reshape(c['nz'], c['nx'])
    # modern land = above SEA_M (rounded DEM metres; rivers are carved to -1), minus the extra channels, shrunk ~1 cell
    land = el >= round(SEA_M + 0.4)
    cell = c['cell_km']
    img = Image.new('L', (c['nx'], c['nz']), 0); dr = ImageDraw.Draw(img)
    for ed in GEO_EDITS:
        if ed['op'] == 'river':
            pts = [(((b_ - lon0) * k - c['x0']) / cell, (-(a_ - lat0) * KZ - c['z0']) / cell) for a_, b_ in ed['path']]
            dr.line(pts, fill=1, width=max(1, int(round(ed['width_m'] / 1000 / cell))))
    land &= ~np.array(img, dtype=bool)
    land = ndimage.binary_erosion(land, iterations=1)
    def cell_poly(j, i0, i1):
        x0 = c['x0'] + (i0 - 0.5) * cell; x1 = c['x0'] + (i1 + 0.5) * cell
        z0 = c['z0'] + (j - 0.5) * cell; z1 = c['z0'] + (j + 0.5) * cell
        return box(lon0 + x0 / k, lat0 - z1 / KZ, lon0 + x1 / k, lat0 - z0 / KZ)
    def to_xy(poly):  # (lat, lon) -> shapely in (lon, lat)
        return Polygon([(b, a) for a, b in poly])
    orig = unary_union([to_xy(p).buffer(0) for p in ORIGINAL])
    strips = [(n, y, to_xy(p)) for n, y, p in STRIPS]
    strip_u = unary_union([s for _, _, s in strips])
    def land_in(geom):
        mnx, mny, mxx, mxy = geom.bounds
        i0 = max(0, int(((mnx - lon0) * k - c['x0']) / cell) - 1); i1 = min(c['nx'] - 1, int(((mxx - lon0) * k - c['x0']) / cell) + 1)
        j0 = max(0, int((-(mxy - lat0) * KZ - c['z0']) / cell) - 1); j1 = min(c['nz'] - 1, int((-(mny - lat0) * KZ - c['z0']) / cell) + 1)
        boxes = []
        for j in range(j0, j1 + 1):
            row = land[j, i0:i1 + 1]; i = 0
            while i < len(row):
                if row[i]:
                    s0 = i
                    while i < len(row) and row[i]: i += 1
                    boxes.append(cell_poly(j, i0 + s0, i0 + i - 1))
                else:
                    i += 1
        return unary_union(boxes).intersection(geom) if boxes else None
    out, taken, cores = [], unary_union([]), []
    smooth = lambda g: g.buffer(0.00012).buffer(-0.00024).buffer(0.00012) if g is not None and not g.is_empty else None
    for name, year, s in strips:
        cores.append((name, year, smooth(land_in(s.difference(orig)))))
    for name, year, zp in ZONES:
        z = to_xy(zp).buffer(0).difference(orig).difference(strip_u).difference(taken)
        taken = taken.union(to_xy(zp).buffer(0))
        cores.append((name, year, smooth(land_in(z))))
    cores = [(n, y, g) for n, y, g in cores if g is not None and not g.is_empty]
    for idx, (name, year, g) in enumerate(cores):
        # grow ~45 m over the water and over unclaimed slivers (so no modern shore rim shows), never onto 1630 land
        # or onto another zone's own land
        others = unary_union([g2 for j, (_, _, g2) in enumerate(cores) if j != idx])
        geom = g.buffer(0.0005).difference(orig).difference(others).union(g).simplify(0.00005)
        parts = [geom] if geom.geom_type == 'Polygon' else list(getattr(geom, 'geoms', []))
        for i, p in enumerate(parts):
            if p.geom_type != 'Polygon' or p.area < 2e-7: continue
            ring = [(round(y, 5), round(x, 5)) for x, y in p.exterior.coords][:-1]
            out.append({"name": name + (f" #{i + 1}" if len(parts) > 1 else ""), "fill": True, "from": 1600, "to": year, "poly": L(ring)})
    return out, True


SEA_M = 0.6   # the DEM gives the harbour 0–1 m, so the sea line is raised (geo.sea_level_m)
GEO_EDITS = [
 {"op": "river", "path": L([(42.3562, -71.0500), (42.3532, -71.0514), (42.3502, -71.0529), (42.3472, -71.0548), (42.3442, -71.0563),
                            (42.3415, -71.0575)]), "width_m": 70},
]
FILL, HAVE_GEO = build_fill()

# ------------------------------------------------------------------ other geography (≈, see research.md)
COMMON = [(42.3566, -71.0622), (42.3578, -71.0631), (42.3561, -71.0702), (42.3523, -71.0689), (42.3524, -71.0644)]
PUBLIC_GARDEN = [(42.3560, -71.0705), (42.3557, -71.0727), (42.3518, -71.0715), (42.3521, -71.0692)]
FENS = [(42.3440, -71.0940), (42.3460, -71.0915), (42.3420, -71.0880), (42.3390, -71.0920), (42.3400, -71.0960)]
EARLY_TOWN = [(42.3628, -71.0560), (42.3612, -71.0582), (42.3592, -71.0602), (42.3570, -71.0606), (42.3558, -71.0588),
              (42.3570, -71.0560), (42.3592, -71.0560), (42.3608, -71.0568)]
NORTH_END = [(42.3672, -71.0582), (42.3681, -71.0558), (42.3666, -71.0526), (42.3642, -71.0530), (42.3624, -71.0552),
             (42.3628, -71.0582), (42.3655, -71.0588)]
SOUTH_TOWN = [(42.3572, -71.0610), (42.3558, -71.0590), (42.3543, -71.0560), (42.3528, -71.0585), (42.3510, -71.0603),
              (42.3495, -71.0617), (42.3505, -71.0638), (42.3540, -71.0630), (42.3562, -71.0626)]
WEST_END = [(42.3652, -71.0650), (42.3640, -71.0670), (42.3617, -71.0686), (42.3600, -71.0672), (42.3608, -71.0640), (42.3630, -71.0615)]
BEACON_HILL = [(42.3602, -71.0692), (42.3585, -71.0699), (42.3566, -71.0703), (42.3578, -71.0632), (42.3600, -71.0645)]
OLD_BOSTON = SHAWMUT
CHAS_VILLAGE = [(42.3722, -71.0628), (42.3740, -71.0600), (42.3762, -71.0610), (42.3772, -71.0650), (42.3745, -71.0666)]
CHAS_TOWN = [(42.3710, -71.0660), (42.3725, -71.0550), (42.3790, -71.0540), (42.3840, -71.0640), (42.3800, -71.0715), (42.3740, -71.0690)]
ROX_VILLAGE = [(42.3330, -71.0900), (42.3330, -71.0850), (42.3290, -71.0830), (42.3270, -71.0870), (42.3290, -71.0910)]
CAMB_VILLAGE = [(42.3760, -71.1220), (42.3760, -71.1160), (42.3720, -71.1160), (42.3715, -71.1220)]
SB = SOUTHBOSTON
EB = NODDLE
BACK_BAY = [(42.3562, -71.0712), (42.3540, -71.0790), (42.3515, -71.0885), (42.3478, -71.0885), (42.3470, -71.0790), (42.3505, -71.0712)]
SOUTH_END = [(42.3478, -71.0712), (42.3425, -71.0800), (42.3365, -71.0778), (42.3385, -71.0690), (42.3440, -71.0615), (42.3478, -71.0628)]
FIN_DIST = [(42.3598, -71.0590), (42.3592, -71.0540), (42.3555, -71.0525), (42.3532, -71.0558), (42.3548, -71.0598)]
SEAPORT = [(42.3532, -71.0480), (42.3502, -71.0390), (42.3455, -71.0395), (42.3470, -71.0490)]
FORT_POINT = [(42.3530, -71.0525), (42.3515, -71.0480), (42.3440, -71.0490), (42.3450, -71.0530)]
INNER = [(42.4150, -71.1500), (42.4200, -71.0700), (42.4000, -71.0000), (42.3600, -70.9950), (42.3200, -71.0200),
         (42.2900, -71.0400), (42.2800, -71.0900), (42.2900, -71.1400), (42.3300, -71.1700), (42.3800, -71.1700)]
OUTER = [(42.4700, -71.2300), (42.4800, -71.0500), (42.4400, -70.9700), (42.3000, -70.9900), (42.2400, -71.0300),
         (42.2300, -71.1300), (42.2600, -71.2400), (42.3500, -71.2700), (42.4200, -71.2700)]
LOGAN = [(42.3800, -71.0290), (42.3880, -71.0200), (42.3800, -70.9850), (42.3550, -70.9850), (42.3550, -71.0100),
         (42.3610, -71.0230), (42.3600, -71.0320), (42.3655, -71.0310)]
MADE_CORE = [(42.3720, -71.0700), (42.3720, -71.0560), (42.3660, -71.0500), (42.3560, -71.0490), (42.3500, -71.0510),
             (42.3420, -71.0560), (42.3330, -71.0640), (42.3330, -71.0800), (42.3400, -71.0950), (42.3480, -71.1000),
             (42.3540, -71.0900), (42.3600, -71.0740), (42.3680, -71.0730)]
CORE_HOLES = [L(SHAWMUT), L(CHAS_TOWN), L(SB), L(EB), L(LOGAN), L(BACK_BAY), L(SOUTH_END), L(FENS), L(SEAPORT), L(FORT_POINT)]


# ------------------------------------------------------------------ timeline
def seg(frm, to, sec, era, city, title=None, sub=None, pop=None, cam=None, chapter=None):
    d = {"from": frm, "to": to, "seconds": sec, "era": era, "city_name": city}
    if title: d["title"] = title; d["sub"] = sub
    if pop is not None: d["population"] = pop
    if cam: d["camera"] = {"center": [cam[0], cam[1]], "dist_km": cam[2]}
    if chapter: d["chapter"] = chapter
    return d

NAT = T("Before the Colony", "Koloni Öncesi"); COL = T("Colonial Era", "Koloni Dönemi")
PROV = COL; REV = T("American Revolution", "Amerikan Devrimi")
EARLY = T("Early Republic", "Erken Cumhuriyet"); IND = T("Industrial Age", "Sanayi Çağı"); MOD = T("20th Century", "20. Yüzyıl")
TODAY = T("Today", "Bugün")
SHAW = T("Shawmut", "Shawmut"); BOS = T("Boston", "Boston")

# sourced anchors (year, people) — see research.md; log-interpolated between them
ANCH = [(1640, 1200), (1680, 4500), (1690, 7000), (1700, 6700), (1710, 9000), (1722, 10567), (1742, 16382), (1760, 15631),
        (1765, 15520), (1780, 10000), (1790, 18320), (1800, 24937), (1810, 33787), (1820, 43298), (1830, 61392), (1840, 93383),
        (1850, 136881), (1860, 177840), (1870, 250526), (1880, 362839), (1890, 448477), (1900, 560892), (1910, 670585),
        (1920, 748060), (1930, 781188), (1940, 770816), (1950, 801444), (1960, 697197), (1970, 641071), (1980, 562994),
        (1990, 574283), (2000, 589141), (2010, 617594), (2020, 675647), (2025, 672973)]
def P(y):
    for (y0, p0), (y1, p1) in zip(ANCH, ANCH[1:]):
        if y0 <= y <= y1:
            u = (y - y0) / (y1 - y0); v = math.exp(math.log(p0) + (math.log(p1) - math.log(p0)) * u)
            return int(round(v, -2 if v < 100000 else -3))
    raise ValueError(y)
PI = lambda a, b: [P(a), P(b)]

C_DOWN = (42.3585, -71.0590)
S = [
 seg(1625, 1629, 18, NAT, SHAW, T("The Shawmut Peninsula", "Shawmut Yarımadası"),
     T("1625: an English settler, William Blaxton, lives alone on a hilly peninsula called Shawmut",
       "1625: İngiliz yerleşimci William Blaxton, Shawmut adlı tepelik bir yarımadada tek başına yaşar"),
     cam=(42.3570, -71.0620, 3.4), chapter=T("Shawmut", "Shawmut")),
 seg(1630, 1633, 18, COL, BOS, T("Boston Is Founded", "Boston Kuruluyor"),
     T("7 September 1630: Puritans led by John Winthrop name their new town Boston",
       "7 Eylül 1630: John Winthrop önderliğindeki Püritenler yeni kasabalarına Boston adını verir"),
     cam=(42.3590, -71.0600, 3.0), chapter=T("Puritan Boston", "Püriten Boston")),
 seg(1634, 1642, 17, COL, BOS, T("The Common", "Common"),
     T("1634: the town buys land from Blaxton for a common; today it is the oldest US city park",
       "1634: kasaba ortak alan için Blaxton'dan arazi alır; bugün ABD'nin en eski şehir parkı"),
     cam=(42.3575, -71.0630, 3.0)),
 seg(1643, 1657, 17, COL, BOS, T("The Mill Pond", "Değirmen Göleti"),
     T("1643: investors dam the North Cove to drive tidal corn mills; it becomes the Mill Pond",
       "1643: yatırımcılar gelgit değirmenleri için Kuzey Koyu'nu bentle kapatır: Değirmen Göleti"),
     pop=PI(1643, 1657), cam=(42.3620, -71.0600, 2.8)),
 seg(1658, 1679, 16, COL, BOS, T("The Town House", "Belediye Binası"),
     T("1658: the first Town House is built where the Old State House stands today",
       "1658: ilk belediye binası, bugünkü Eski Eyalet Binası'nın yerinde inşa edilir"),
     pop=PI(1658, 1679), cam=(42.3590, -71.0585, 2.6)),
 seg(1680, 1709, 17, PROV, BOS, T("A Seaport Grows", "Bir Liman Büyüyor"),
     T("1680–1710: Boston grows from about 4,500 to 9,000 people as wharves push into the harbor",
       "1680–1710: rıhtımlar limana uzarken Boston yaklaşık 4.500'den 9.000 kişiye çıkar"),
     pop=PI(1680, 1709), cam=(42.3600, -71.0580, 3.4), chapter=T("Colonial Seaport", "Koloni Limanı")),
 seg(1710, 1712, 15, PROV, BOS, T("The Fire of 1711", "1711 Yangını"),
     T("October 1711: a fire burns the first Town House; a brick one replaces it in 1713",
       "Ekim 1711: bir yangın ilk belediye binasını yakar; 1713'te yerine tuğla bir bina yapılır"),
     pop=PI(1710, 1712), cam=(42.3590, -71.0580, 2.6)),
 seg(1713, 1720, 17, PROV, BOS, T("The Long Wharf", "Uzun Rıhtım"),
     T("1710–1721: Long Wharf is built out from King Street, about a third of a mile into the harbor",
       "1710–1721: Uzun Rıhtım, King Caddesi'nden limana doğru yaklaşık yarım kilometre uzatılır"),
     pop=PI(1713, 1720), cam=(42.3595, -71.0545, 2.6)),
 seg(1721, 1722, 15, PROV, BOS, T("Smallpox", "Çiçek Hastalığı"),
     T("1721–1722: smallpox strikes 5,889 of about 10,500 people; 844 die",
       "1721–1722: çiçek hastalığı yaklaşık 10.500 kişiden 5.889'una bulaşır; 844 kişi ölür"),
     pop=[P(1721), 10567], cam=(42.3610, -71.0580, 3.4)),
 seg(1723, 1741, 16, PROV, BOS, T("Old North and Old South", "Old North ve Old South"),
     T("1723: Christ Church, the Old North, rises in the North End; the Old South follows in 1729",
       "1723: Kuzey Yakası'nda Old North kilisesi yükselir; Old South 1729'da onu izler"),
     pop=PI(1723, 1741), cam=(42.3625, -71.0570, 2.8)),
 seg(1742, 1759, 15, PROV, BOS, T("Faneuil Hall", "Faneuil Hall"),
     T("10 September 1742: Faneuil Hall opens, a market below and a meeting hall above",
       "10 Eylül 1742: Faneuil Hall açılır; altta pazar, üstte toplantı salonu"),
     pop=PI(1742, 1759), cam=(42.3600, -71.0570, 2.4)),
 seg(1760, 1761, 16, PROV, BOS, T("The Great Fire of 1760", "1760 Büyük Yangını"),
     T("20 March 1760: a fire from Cornhill burns 349 buildings down to Fort Hill; no one dies",
       "20 Mart 1760: Cornhill'de çıkan yangın Fort Hill'e kadar 349 binayı yakar; ölen olmaz"),
     pop=[15631, P(1761)], cam=(42.3570, -71.0570, 2.4)),
 seg(1762, 1767, 6, PROV, BOS, pop=[P(1762), 15520], cam=(42.3590, -71.0590, 3.2)),
 seg(1768, 1772, 17, REV, BOS, T("The Boston Massacre", "Boston Katliamı"),
     T("5 March 1770: British soldiers fire into a crowd by the Town House, killing five people",
       "5 Mart 1770: İngiliz askerleri belediye binası önündeki kalabalığa ateş açar, beş kişi ölür"),
     pop=15520, cam=(42.3585, -71.0590, 2.6), chapter=T("Revolution", "Devrim")),
 seg(1773, 1774, 17, REV, BOS, T("The Boston Tea Party", "Boston Çay Partisi"),
     T("16 December 1773: protesters dump 342 chests of tea into the harbor at Griffin's Wharf",
       "16 Aralık 1773: protestocular Griffin İskelesi'nde 342 sandık çayı denize döker"),
     pop=15520, cam=(42.3555, -71.0550, 2.4)),
 seg(1775, 1775.45, 16, REV, BOS, T("The Siege of Boston", "Boston Kuşatması"),
     T("19 April 1775: after Lexington and Concord, militia surround the British army in Boston",
       "19 Nisan 1775: Lexington ve Concord'dan sonra milisler Boston'daki İngiliz ordusunu kuşatır"),
     cam=(42.3560, -71.0750, 9.0)),
 seg(1775.46, 1776.1, 16, REV, BOS, T("Bunker Hill", "Bunker Tepesi"),
     T("17 June 1775: British troops take Breed's Hill in Charlestown, at a heavy cost",
       "17 Haziran 1775: İngiliz askerleri Charlestown'daki Breed's Tepesi'ni ağır kayıpla alır"),
     cam=(42.3700, -71.0620, 3.6)),
 seg(1776.11, 1776.5, 16, REV, BOS, T("The British Leave", "İngilizler Gidiyor"),
     T("March 1776: cannon on Dorchester Heights force the British to sail away on the 17th",
       "Mart 1776: Dorchester Tepeleri'ne kurulan toplar İngilizleri 17'sinde denize açılmaya zorlar"),
     cam=(42.3480, -71.0520, 5.0)),
 seg(1777, 1793, 16, EARLY, BOS, T("Bridging the Charles", "Charles'a Köprü"),
     T("1786: the Charles River Bridge links Boston and Charlestown; Cambridge follows in 1793",
       "1786: Charles Nehri Köprüsü Boston'u Charlestown'a bağlar; 1793'te Cambridge'e köprü"),
     pop=PI(1780, 1793), cam=(42.3640, -71.0640, 4.0), chapter=T("A Growing City", "Büyüyen Şehir")),
 seg(1794, 1806, 16, EARLY, BOS, T("The State House", "Eyalet Meclisi"),
     T("1795–1798: Charles Bulfinch's State House rises on Beacon Hill; its dome is gilded in 1874",
       "1795–1798: Bulfinch'in Eyalet Meclisi Beacon Tepesi'nde yükselir; kubbesi 1874'te yaldızlanır"),
     pop=PI(1794, 1806), cam=(42.3585, -71.0640, 2.6)),
 seg(1807, 1820, 18, EARLY, BOS, T("Hills into the Sea", "Tepeler Denize"),
     T("1807–c.1828: earth from Beacon Hill and Copp's Hill fills the 50-acre Mill Pond",
       "1807–1828 civarı: Beacon ve Copp's tepelerinin toprağı 50 dönümlük Değirmen Göleti'ni doldurur"),
     pop=PI(1807, 1820), cam=(42.3630, -71.0620, 3.0), chapter=T("Making Land", "Toprak Yaratmak")),
 seg(1821, 1823, 16, EARLY, BOS, T("A Dam and a City", "Bir Bent ve Bir Şehir"),
     T("1821: a mill dam, today's Beacon Street, closes off the Back Bay; Boston becomes a city in 1822",
       "1821: bugünkü Beacon Caddesi olan bent Back Bay'i kapatır; Boston 1822'de şehir olur"),
     pop=PI(1821, 1823), cam=(42.3540, -71.0780, 4.6)),
 seg(1824, 1832, 15, EARLY, BOS, T("Quincy Market", "Quincy Pazarı"),
     T("1824–1826: Quincy Market is built on new land just east of Faneuil Hall",
       "1824–1826: Quincy Pazarı, Faneuil Hall'ün hemen doğusundaki yeni toprakta inşa edilir"),
     pop=PI(1824, 1832), cam=(42.3605, -71.0560, 2.4)),
 seg(1833, 1835, 15, IND, BOS, T("Railroads Cross the Bay", "Demiryolu Körfezi Geçiyor"),
     T("1834–1835: lines to Providence and Worcester cross the Back Bay on causeways",
       "1834–1835: Providence ve Worcester hatları Back Bay'i set yollar üzerinden geçer"),
     pop=PI(1833, 1835), cam=(42.3490, -71.0720, 4.4), chapter=T("Industrial Boston", "Sanayi Bostonu")),
 seg(1836, 1844, 15, IND, BOS, T("Filling the South Cove", "Güney Koyu Dolduruluyor"),
     T("1833–1845: new land fills the South Cove, where much of Chinatown stands today",
       "1833–1845: bugünkü Çin Mahallesi'nin büyük kısmının bulunduğu Güney Koyu doldurulur"),
     pop=PI(1836, 1844), cam=(42.3510, -71.0590, 3.2)),
 seg(1845, 1856, 15, IND, BOS, T("Famine Ships", "Kıtlık Gemileri"),
     T("1845–1849: the Irish potato famine drives a wave of Irish Catholic immigration",
       "1845–1849: İrlanda patates kıtlığı büyük bir İrlandalı Katolik göç dalgası getirir"),
     pop=PI(1845, 1856), cam=(42.3560, -71.0600, 4.8)),
 seg(1857, 1867, 18, IND, BOS, T("Filling the Back Bay", "Back Bay Dolduruluyor"),
     T("From 1857 trains bring gravel from Needham to fill the Back Bay, block by block",
       "1857'den itibaren trenler Needham'dan çakıl getirip Back Bay'i blok blok doldurur"),
     pop=PI(1857, 1867), cam=(42.3510, -71.0790, 4.6)),
 seg(1868, 1871, 15, IND, BOS, T("Annexing the Suburbs", "Banliyöler Katılıyor"),
     T("1868–1870: Boston annexes Roxbury and Dorchester; by 1870 it has 250,526 people",
       "1868–1870: Boston, Roxbury ve Dorchester'ı katar; 1870'te nüfusu 250.526'dır"),
     pop=PI(1868, 1871), cam=(42.3400, -71.0700, 9.0)),
 seg(1872, 1873, 16, IND, BOS, T("The Great Fire of 1872", "1872 Büyük Yangını"),
     T("9–10 November 1872: in about 16 hours, fire burns 65 acres and 776 buildings downtown",
       "9–10 Kasım 1872: yaklaşık 16 saatte yangın şehir merkezinde 65 dönüm ve 776 binayı yakar"),
     pop=PI(1872, 1873), cam=(42.3555, -71.0570, 2.6)),
 seg(1874, 1876, 14, IND, BOS, T("Charlestown Joins", "Charlestown Katılıyor"),
     T("1874: Boston annexes Charlestown, Brighton and West Roxbury",
       "1874: Boston, Charlestown, Brighton ve West Roxbury'yi katar"),
     pop=PI(1874, 1876), cam=(42.3560, -71.0700, 11.0)),
 seg(1877, 1887, 15, IND, BOS, T("Trinity Church", "Trinity Kilisesi"),
     T("1872–1877: H. H. Richardson's Trinity Church rises on new land in Copley Square",
       "1872–1877: H. H. Richardson'ın Trinity Kilisesi Copley Meydanı'nın yeni toprağında yükselir"),
     pop=PI(1877, 1887), cam=(42.3510, -71.0760, 3.0)),
 seg(1888, 1896, 15, IND, BOS, T("The Back Bay Is Done", "Back Bay Tamamlanıyor"),
     T("By 1882 the Back Bay is filled; the fill reaches Kenmore Square in 1890 and the Fens by 1900",
       "Back Bay 1882'de dolar; dolgu 1890'da Kenmore Meydanı'na, 1900'de Fens'e ulaşır"),
     pop=PI(1888, 1896), cam=(42.3500, -71.0820, 5.0)),
 seg(1897, 1898, 15, IND, BOS, T("America's First Subway", "Amerika'nın İlk Metrosu"),
     T("1 September 1897: the Tremont Street subway opens, the first in North America",
       "1 Eylül 1897: Tremont Caddesi metrosu açılır; Kuzey Amerika'nın ilk metrosu"),
     pop=PI(1897, 1898), cam=(42.3560, -71.0620, 3.2)),
 seg(1899, 1911, 15, MOD, BOS, T("South Station", "South Station"),
     T("1 January 1899: South Station opens on Dewey Square, with one of the largest train sheds",
       "1 Ocak 1899: South Station, dünyanın en büyük tren hangarlarından biriyle açılır"),
     pop=PI(1899, 1911), cam=(42.3510, -71.0540, 3.6), chapter=T("Modern Boston", "Modern Boston")),
 seg(1912, 1918, 15, MOD, BOS, T("Custom House Tower", "Gümrük Kulesi"),
     T("1915: a 496 ft tower tops the Custom House; Fenway Park has opened in 1912",
       "1915: Gümrük Binası'na 151 m'lik bir kule eklenir; Fenway Park 1912'de açılmıştır"),
     pop=PI(1912, 1918), cam=(42.3560, -71.0640, 5.6)),
 seg(1919, 1922, 15, MOD, BOS, T("The Molasses Flood", "Pekmez Seli"),
     T("15 January 1919: a tank bursts in the North End; a wave of molasses kills 21 people",
       "15 Ocak 1919: Kuzey Yakası'nda bir tank patlar; pekmez dalgası 21 kişinin ölümüne yol açar"),
     pop=PI(1919, 1922), cam=(42.3660, -71.0560, 2.4)),
 seg(1923, 1939, 15, MOD, BOS, T("Boston Airport", "Boston Havalimanı"),
     T("8 September 1923: an airport opens in East Boston; the Sumner Tunnel follows in 1934",
       "8 Eylül 1923: Doğu Boston'da bir havalimanı açılır; 1934'te Sumner Tüneli gelir"),
     pop=PI(1923, 1939), cam=(42.3640, -71.0300, 6.0)),
 seg(1940, 1950, 15, MOD, BOS, T("Peak Boston", "Zirvedeki Boston"),
     T("1950: the census counts 801,444 people, Boston's highest count so far",
       "1950: sayım 801.444 kişi sayar; Boston'un bugüne kadarki en yüksek nüfusu"),
     pop=PI(1940, 1950), cam=(42.3540, -71.0500, 12.0)),
 seg(1951, 1962, 15, MOD, BOS, T("The Central Artery", "Central Artery"),
     T("1951–1959: an elevated highway cuts through downtown; the West End is razed from 1958",
       "1951–1959: yükseltilmiş bir otoyol şehir merkezini böler; Batı Yakası 1958'den itibaren yıkılır"),
     pop=PI(1951, 1962), cam=(42.3610, -71.0600, 3.4)),
 seg(1963, 1970, 15, MOD, BOS, T("Prudential and City Hall", "Prudential ve Belediye"),
     T("1964: the 749 ft Prudential Tower rises; in 1968 City Hall opens where Scollay Square stood",
       "1964: 228 m'lik Prudential Kulesi yükselir; 1968'de Scollay Meydanı'nın yerinde belediye açılır"),
     pop=PI(1963, 1970), cam=(42.3540, -71.0700, 4.8)),
 seg(1971, 1990, 15, MOD, BOS, T("The Hancock Tower", "Hancock Kulesi"),
     T("1976: I. M. Pei's 790 ft Hancock Tower becomes New England's tallest building",
       "1976: I. M. Pei'nin 241 m'lik Hancock Kulesi New England'ın en yüksek binası olur"),
     pop=PI(1971, 1990), cam=(42.3500, -71.0740, 4.0)),
 seg(1991, 2007, 17, TODAY, BOS, T("The Big Dig", "Big Dig"),
     T("1991–2007: the highway goes underground; the elevated Central Artery comes down from 2004",
       "1991–2007: otoyol yerin altına iner; yükseltilmiş Central Artery 2004'ten itibaren sökülür"),
     pop=PI(1991, 2007), cam=(42.3600, -71.0570, 3.6), chapter=T("Boston Today", "Bugünün Bostonu")),
 seg(2008, 2019, 16, TODAY, BOS, T("Made Land", "Yapay Toprak"),
     T("More than two-thirds of inner Boston stands on land that did not exist in 1630",
       "İç Boston'un üçte ikisinden fazlası, 1630'da var olmayan topraklar üzerinde durur"),
     pop=PI(2008, 2019), cam=(42.3540, -71.0600, 7.0)),
 seg(2020, 2026, 22, TODAY, BOS, T("Boston Today", "Bugünün Bostonu"),
     T("From one settler on Shawmut to about 673,000 Bostonians, nearly 400 years on",
       "Shawmut'taki tek bir yerleşimciden yaklaşık 673.000 Bostonluya, yaklaşık 400 yıl sonra"),
     pop=[675647, 672973], cam=(42.3560, -71.0620, 11.0)),
]
SCALE_T, SCALE_Q = 1.2, 1.15
for s_ in S:
    s_["seconds"] = round(s_["seconds"] * (SCALE_T if s_.get("title") else SCALE_Q))


def wall(name, path, built, removed=None, height="low", towers=0, draw=2.0, **kw):
    d = {"name": name, "path": L(path), "built": built, "height": height, "towers_m": towers, "draw_s": draw}
    if removed is not None: d["removed"] = removed
    d.update(kw); return d


FIRE_1760 = [(42.3580, -71.0590), (42.3586, -71.0560), (42.3578, -71.0546), (42.3565, -71.0535), (42.3552, -71.0538),
             (42.3553, -71.0570), (42.3565, -71.0592)]
FIRE_1872 = [(42.3568, -71.0588), (42.3575, -71.0560), (42.3570, -71.0537), (42.3548, -71.0527), (42.3530, -71.0545),
             (42.3533, -71.0580), (42.3548, -71.0593)]

districts = [
 {"name": "First town (≈)", "style": "medieval", "poly": L(EARLY_TOWN), "from": 1630, "to": 1665, "density": 0.55, "grain_m": 45,
  "grow_from": [42.3595, -71.0580]},
 {"name": "North End (≈)", "style": "medieval", "poly": L(NORTH_END), "from": 1640, "to": 1700, "density": 0.75, "grain_m": 45,
  "grow_from": [42.3635, -71.0560]},
 {"name": "Charlestown village (≈)", "style": "medieval", "poly": L(CHAS_VILLAGE), "from": 1630, "to": 1680, "density": 0.55, "grain_m": 50,
  "grow_from": [42.3735, -71.0620]},
 {"name": "Roxbury village (≈)", "style": "medieval", "poly": L(ROX_VILLAGE), "from": 1631, "to": 1700, "density": 0.4, "grain_m": 60,
  "grow_from": [42.3305, -71.0870]},
 {"name": "Cambridge village (≈)", "style": "medieval", "poly": L(CAMB_VILLAGE), "from": 1631, "to": 1700, "density": 0.45, "grain_m": 55,
  "grow_from": [42.3740, -71.1190]},
 {"name": "South town (≈)", "style": "medieval", "poly": L(SOUTH_TOWN), "from": 1660, "to": 1730, "density": 0.7, "grain_m": 45,
  "grow_from": [42.3560, -71.0600]},
 {"name": "West End (≈)", "style": "georgian", "poly": L(WEST_END), "from": 1700, "to": 1790, "density": 0.7, "grain_m": 50,
  "grow_from": [42.3630, -71.0625]},
 {"name": "Brick downtown", "style": "georgian", "poly": L(EARLY_TOWN + []), "from": 1712, "to": 1760, "density": 0.85, "grain_m": 42,
  "grow_from": [42.3590, -71.0580]},
 {"name": "Beacon Hill", "style": "georgian", "poly": L(BEACON_HILL), "holes": [L(COMMON)], "from": 1795, "to": 1840, "density": 0.8,
  "grain_m": 45, "grow_from": [42.3582, -71.0640]},
 {"name": "Shawmut, filled out", "style": "georgian", "poly": L(SHAWMUT), "holes": [L(COMMON), L(BEACON_HILL)], "from": 1760, "to": 1830,
  "density": 0.7, "grain_m": 55, "grow_from": [42.3590, -71.0590]},
 {"name": "Charlestown", "style": "georgian", "poly": L(CHAS_TOWN), "from": 1776.6, "to": 1850, "density": 0.65, "grain_m": 60,
  "grow_from": [42.3735, -71.0620]},
 {"name": "Bulfinch Triangle and North Station", "style": "georgian", "poly": L([(42.3615, -71.0650), (42.3700, -71.0660), (42.3705, -71.0590),
  (42.3615, -71.0585)]), "from": 1815, "to": 1870, "density": 0.75, "grain_m": 55, "grow_from": [42.3635, -71.0610]},
 {"name": "South Cove", "style": "industrial", "poly": L([(42.3545, -71.0600), (42.3545, -71.0540), (42.3470, -71.0560), (42.3470, -71.0640)]),
  "from": 1838, "to": 1870, "density": 0.75, "grain_m": 60, "grow_from": [42.3520, -71.0590]},
 {"name": "South Boston", "style": "victorian", "poly": L(SB), "from": 1805, "to": 1890, "density": 0.8, "grain_m": 62,
  "grow_from": [42.3370, -71.0500]},
 {"name": "East Boston", "style": "victorian", "poly": L(EB), "from": 1835, "to": 1890, "density": 0.8, "grain_m": 60,
  "grow_from": [42.3700, -71.0380]},
 {"name": "South End", "style": "victorian", "poly": L(SOUTH_END), "from": 1840, "to": 1885, "density": 0.85, "grain_m": 55,
  "grow_from": [42.3460, -71.0660], "grid_deg": 50},
 {"name": "Back Bay", "style": "victorian", "poly": L(BACK_BAY), "holes": [L(PUBLIC_GARDEN)], "from": 1859, "to": 1905, "density": 0.85,
  "grain_m": 50, "grow_from": [42.3530, -71.0712], "grid_deg": 22},
 {"name": "Fort Point warehouses", "style": "industrial", "poly": L(FORT_POINT), "from": 1880, "to": 1915, "density": 0.75, "grain_m": 70,
  "grow_from": [42.3500, -71.0520]},
 {"name": "South Boston waterfront", "style": "industrial", "poly": L([(42.3540, -71.0480), (42.3490, -71.0330), (42.3420, -71.0280),
  (42.3405, -71.0450), (42.3440, -71.0490)]), "from": 1900, "to": 1950, "density": 0.4, "grain_m": 110, "grow_from": [42.3480, -71.0450]},
 {"name": "Made land, inner Boston (≈, follows each fill)", "style": "victorian", "poly": L(MADE_CORE),
  "holes": [L(COMMON), L(PUBLIC_GARDEN), L(FENS), L(SHAWMUT)], "from": 1830, "to": 1915, "density": 0.75, "grain_m": 60,
  "grow_from": [42.3580, -71.0600]},
 {"name": "South Boston waterfront (dense)", "style": "industrial", "poly": L([(42.3540, -71.0480), (42.3490, -71.0330), (42.3420, -71.0280),
  (42.3405, -71.0450), (42.3440, -71.0490)]), "from": 1905, "to": 1960, "density": 0.55, "grain_m": 80, "grow_from": [42.3480, -71.0450]},
 {"name": "Inner suburbs", "style": "suburb", "poly": L(INNER), "holes": CORE_HOLES, "from": 1850, "to": 1930,
  "density": 0.6, "grain_m": 95, "grow_from": [42.3560, -71.0620]},
 {"name": "Outer suburbs", "style": "suburb", "poly": L(OUTER), "holes": [L(INNER)], "from": 1900, "to": 1990, "density": 0.4,
  "grain_m": 170, "grow_from": [42.3560, -71.0620]},
 {"name": "Downtown offices", "style": "modern", "poly": L(FIN_DIST), "from": 1873, "to": 1930, "density": 0.85, "grain_m": 55,
  "grow_from": [42.3560, -71.0570]},
 {"name": "West End towers", "style": "modern", "poly": L(WEST_END), "from": 1959, "to": 1965, "density": 0.35, "grain_m": 90,
  "grow_from": [42.3640, -71.0660]},
 {"name": "Financial District towers", "style": "highrise", "poly": L(FIN_DIST), "from": 1965, "to": 2020, "density": 0.55, "grain_m": 90,
  "grow_from": [42.3560, -71.0560]},
 {"name": "Seaport", "style": "modern", "poly": L(SEAPORT), "from": 2005, "to": 2024, "density": 0.75, "grain_m": 85, "grid_deg": 30,
  "grow_from": [42.3520, -71.0470]},
]

landmarks = [
 {"type": "box", "name": T("First Town House", "İlk Belediye Binası"), "at": [42.35875, -71.05747], "built": 1658, "removed": 1711.8,
  "rise_s": 3, "size_m": [24, 14, 12], "colors": {"wall": "#8a6a48", "roof": "#5d4a38"}},
 {"type": "church", "name": T("Town House (Old State House)", "Eski Eyalet Binası"), "at": [42.35875, -71.05747], "built": 1713, "rise_s": 3,
  "size_m": [34, 17, 16], "rot_deg": 0, "colors": {"wall": "#a4513a", "roof": "#4f565f"}},
 {"type": "church", "name": T("Old North Church", "Old North Kilisesi"), "at": [42.3663, -71.0545], "built": 1723, "rise_s": 4,
  "size_m": [30, 16, 18], "rot_deg": 145, "colors": {"wall": "#a4513a", "roof": "#e8e3d8"}, "scale": 1.3},
 {"type": "church", "name": T("Old South Meeting House", "Old South"), "at": [42.35694, -71.05861], "built": 1729, "rise_s": 4,
  "size_m": [33, 20, 18], "rot_deg": 0, "colors": {"wall": "#a4513a", "roof": "#e8e3d8"}, "scale": 1.3},
 {"type": "box", "name": T("Faneuil Hall", "Faneuil Hall"), "at": [42.36000, -71.05611], "built": 1742, "removed": 1806, "rise_s": 3,
  "size_m": [30, 23, 14], "colors": {"wall": "#a4513a", "roof": "#4f565f"}},
 {"type": "box", "name": T("Faneuil Hall (enlarged)", "Faneuil Hall (büyütülmüş)"), "at": [42.36000, -71.05611], "built": 1806, "rise_s": 1,
  "size_m": [31, 30, 20], "colors": {"wall": "#a4513a", "roof": "#4f565f"}},
 {"type": "box", "name": T("Quincy Market", "Quincy Pazarı"), "at": [42.36008, -71.05480], "built": 1824.5, "rise_s": 4,
  "size_m": [163, 16, 14], "rot_deg": 0, "colors": {"wall": "#d8cdb5", "roof": "#59656a"}},
 {"type": "domechurch", "name": T("State House", "Eyalet Meclisi"), "at": [42.3582, -71.0637], "built": 1795.5, "removed": 1874, "rise_s": 8,
  "size_m": [52, 40, 20], "colors": {"wall": "#a4513a", "dome": "#8f969c", "lantern": True}},
 {"type": "domechurch", "name": T("State House (gilded dome)", "Eyalet Meclisi (yaldızlı)"), "at": [42.3582, -71.0637], "built": 1874, "rise_s": 0.3,
  "size_m": [52, 40, 20], "colors": {"wall": "#a4513a", "dome": "#d6b04a", "lantern": True}},
 {"type": "obelisk", "name": T("Bunker Hill Monument", "Bunker Hill Anıtı"), "at": [42.376361, -71.060778], "built": 1825.5, "rise_s": 12,
  "size_m": [10, 10, 67], "colors": {"wall": "#d6d1c4"}},
 {"type": "box", "name": T("Custom House", "Gümrük Binası"), "at": [42.3591, -71.0534], "built": 1837, "rise_s": 6, "size_m": [45, 30, 22],
  "colors": {"wall": "#ddd6c4", "roof": "#7a8a8a"}},
 {"type": "clocktower", "name": T("Custom House Tower", "Gümrük Kulesi"), "at": [42.3591, -71.0534], "built": 1913, "rise_s": 10,
  "size_m": [26, 26, 151], "colors": {"wall": "#ddd6c4", "roof": "#6f8c86"}},
 {"type": "church", "name": T("Trinity Church", "Trinity Kilisesi"), "at": [42.3500, -71.0756], "built": 1872.5, "rise_s": 10,
  "size_m": [50, 36, 22], "rot_deg": 0, "colors": {"wall": "#b98b6a", "roof": "#8a4a3a"}, "scale": 1.3},
 {"type": "station", "name": T("South Station", "South Station"), "at": [42.35194, -71.05528], "built": 1898.6, "rise_s": 6,
  "size_m": [220, 140, 28], "rot_deg": 30, "colors": {"wall": "#d6cdb8", "roof": "#6c7a80"}},
 {"type": "stadium", "name": T("Fenway Park", "Fenway Park"), "at": [42.34639, -71.09778], "built": 1911.8, "rise_s": 4,
  "size_m": [170, 150, 22], "colors": {"wall": "#3f6b4f"}},
 {"type": "skyscraper", "name": T("Prudential Tower", "Prudential Kulesi"), "at": [42.3472, -71.0825], "built": 1960.5, "rise_s": 8,
  "size_m": [50, 50, 228], "colors": {"wall": "#8b8f93"}},
 {"type": "box", "name": T("Boston City Hall", "Boston Belediyesi"), "at": [42.3603222, -71.0579667], "built": 1963.5, "rise_s": 6,
  "size_m": [90, 80, 38], "colors": {"wall": "#bdb6a8"}},
 {"type": "skyscraper", "name": T("Hancock Tower", "Hancock Kulesi"), "at": [42.349278, -71.074778], "built": 1968.5, "rise_s": 10,
  "size_m": [90, 32, 241], "rot_deg": 30, "colors": {"wall": "#7fa3bf"}},
 {"type": "fort", "name": T("Castle William", "Castle William"), "at": [42.3376, -71.0106], "built": 1634.5, "removed": 1776.3, "rise_s": 3,
  "size_m": [90, 80, 10], "colors": {"wall": "#bfb39b"}},
 {"type": "fort", "name": T("Fort Independence", "Fort Independence"), "at": [42.3376, -71.0106], "built": 1833, "rise_s": 5,
  "size_m": [120, 110, 12], "colors": {"wall": "#cfc6b1"}},
]

bridges = [
 {"name": "Charles River Bridge (≈ site)", "path": [[42.3676, -71.0586], [42.3717, -71.0624]], "built": 1786, "removed": 1900, "style": "wood", "width_m": 14},
 {"name": "Charlestown Bridge (≈ site)", "path": [[42.3676, -71.0586], [42.3717, -71.0624]], "built": 1900, "style": "iron", "width_m": 26},
 {"name": "West Boston Bridge (≈ site)", "path": [[42.3612, -71.0715], [42.3626, -71.0785]], "built": 1793, "removed": 1907, "style": "wood", "width_m": 14},
 {"name": "Longfellow Bridge (≈ ends)", "path": [[42.3612, -71.0715], [42.3626, -71.0785]], "built": 1907, "style": "stone", "width_m": 32},
 {"name": "Zakim Bridge (≈ ends)", "path": [[42.3670, -71.0622], [42.3707, -71.0646]], "built": 2002.5, "style": "modern", "width_m": 56, "draw_s": 4},
]

roads = [
 {"name": "Orange St / Washington St over the Neck", "path": L([(42.3580, -71.0590), (42.3545, -71.0610), (42.3500, -71.0627), (42.3439, -71.0660),
  (42.3400, -71.0700), (42.3360, -71.0750), (42.3300, -71.0840)]), "from": 1630, "kind": "road", "width_m": 10},
 {"name": "Central Artery (elevated)", "path": L([(42.3690, -71.0620), (42.3655, -71.0600), (42.3628, -71.0565), (42.3603, -71.0545),
  (42.3570, -71.0535), (42.3530, -71.0560), (42.3480, -71.0590), (42.3420, -71.0612), (42.3330, -71.0610)]), "from": 1951, "to": 2004.5,
  "kind": "motorway", "width_m": 40},
 {"name": "Massachusetts Turnpike extension", "path": L([(42.3495, -71.0610), (42.3478, -71.0660), (42.3472, -71.0760), (42.3482, -71.0990),
  (42.3530, -71.1300), (42.3540, -71.1700)]), "from": 1965, "kind": "motorway", "width_m": 40},
 {"name": "Boston and Providence Railroad", "path": L([(42.3503, -71.0683), (42.3364, -71.0890), (42.3100, -71.1150)]), "from": 1835, "kind": "rail", "width_m": 18},
 {"name": "Boston and Worcester Railroad", "path": L([(42.3478, -71.0655), (42.3473, -71.0760), (42.3482, -71.0990), (42.3530, -71.1400)]),
  "from": 1835, "kind": "rail", "width_m": 18},
 {"name": "Commonwealth Avenue (≈ from 1865)", "path": L([(42.3536, -71.0715), (42.3505, -71.0870), (42.3489, -71.0953)]), "from": 1865,
  "kind": "avenue", "width_m": 24},
]

city = {
 "slug": "boston", "seed": 1630, "long_ok": True,
 "name": T("Boston", "Boston"), "intro": T("400 Years in 15 Minutes", "15 Dakikada 400 Yıl"), "intro_seconds": 4.5,
 "geo": {"bbox": [42.20, -71.32, 42.52, -70.84], "cell_m": 90, "core_bbox": [42.315, -71.125, 42.395, -70.975], "core_cell_m": 30,
         "rivers_keep": ["Charles", "Mystic", "Neponset", "Chelsea", "Fort Point", "Reserved", "Malden", "Island End", "Muddy"],
         "sea_level_m": SEA_M},
 "geo_edits": GEO_EDITS,
 "view": {"azimuth_deg": 0, "pitch_deg": 46, "fov": 34},
 "render": {"vertical_exaggeration": 3.0},
 "segments": S,
 "timed_water": FILL,
 "districts": districts,
 "walls": [wall("Boston Neck gate and earthwork (≈)", [(42.34405, -71.06745), (42.34375, -71.06505)], 1631, 1830, height="low", draw=1.5,
                moat=True)],
 "bridges": bridges, "roads": roads, "landmarks": landmarks,
 "fires": [
  {"year": 1711.8, "poly": L(rect(42.3580, -71.0585, 42.3595, -71.0560)), "duration_s": 4, "plumes": 3},
  {"year": 1760.22, "poly": L(FIRE_1760), "duration_s": 6, "plumes": 5},
  {"year": 1872.86, "poly": L(FIRE_1872), "duration_s": 6, "plumes": 6},
 ],
 "smoke": [
  {"at": [42.3764, -71.0608], "from": 1775.46, "to": 1775.6, "scale": 1.2},
  {"at": [42.3328, -71.0464], "from": 1776.17, "to": 1776.21, "scale": 0.8},
  {"at": [42.3685, -71.0558], "from": 1919.04, "to": 1919.1, "scale": 0.6},
 ],
 "camps": [
  {"poly": L(rect(42.3530, -71.0690, 42.3560, -71.0650)), "from": 1768.8, "to": 1776.2, "count": 60},
  {"poly": L(rect(42.3700, -71.1250, 42.3800, -71.1050)), "from": 1775.3, "to": 1776.2, "count": 160},
  {"poly": L(rect(42.3200, -71.0950, 42.3290, -71.0780)), "from": 1775.3, "to": 1776.2, "count": 140},
  {"poly": L(rect(42.3310, -71.0500, 42.3345, -71.0430)), "from": 1776.17, "to": 1776.22, "count": 50},
 ],
 "open_spaces": [
  {"name": "Boston Common", "poly": L(COMMON)},
  {"name": "Public Garden", "poly": L(PUBLIC_GARDEN)},
  {"name": "Back Bay Fens", "poly": L(FENS)},
 ],
 "labels": [
  {"text": T("CHARLES RIVER", "CHARLES NEHRİ"), "at": [42.3640, -71.0850], "kind": "water"},
  {"text": T("BOSTON HARBOR", "BOSTON LİMANI"), "at": [42.3560, -71.0380], "kind": "water", "to": 1880},
  {"text": T("BOSTON HARBOR", "BOSTON LİMANI"), "at": [42.3560, -71.0250], "kind": "water", "from": 1880, "to": 1940},
  {"text": T("BACK BAY", "BACK BAY"), "at": [42.3490, -71.0820], "kind": "water", "from": 1625, "to": 1856},
  {"text": T("BACK BAY", "BACK BAY"), "at": [42.3500, -71.0810], "kind": "region", "from": 1880, "to": 1900},
  {"text": T("SHAWMUT", "SHAWMUT"), "at": [42.3575, -71.0610], "kind": "region", "from": 1625, "to": 1633},
  {"text": T("Boston Neck", "Boston Boynu"), "at": [42.3439, -71.0660], "kind": "place", "from": 1625, "to": 1660, "lift_m": 20},
  {"text": T("Charlestown", "Charlestown"), "at": [42.3770, -71.0640], "kind": "place", "from": 1630, "to": 1642},
  {"text": T("Boston Common", "Boston Common"), "at": [42.3550, -71.0660], "kind": "place", "from": 1634, "to": 1642, "lift_m": 15},
  {"text": T("Mill Pond", "Değirmen Göleti"), "at": [42.3640, -71.0610], "kind": "water", "from": 1643, "to": 1657},
  {"text": T("Town House", "Belediye Binası"), "at": [42.35875, -71.05747], "from": 1659, "to": 1679, "lift_m": 30},
  {"text": T("Long Wharf", "Uzun Rıhtım"), "at": [42.3600, -71.0500], "kind": "place", "from": 1716, "to": 1720, "lift_m": 15},
  {"text": T("Old North", "Old North"), "at": [42.3663, -71.0545], "from": 1724, "to": 1741, "lift_m": 60},
  {"text": T("Faneuil Hall", "Faneuil Hall"), "at": [42.36000, -71.05611], "from": 1742.7, "to": 1759, "lift_m": 30},
  {"text": T("Fort Hill", "Fort Hill"), "at": [42.3560, -71.0540], "kind": "place", "from": 1760, "to": 1761, "lift_m": 20},
  {"text": T("Town House", "Belediye Binası"), "at": [42.35875, -71.05747], "from": 1768, "to": 1772, "lift_m": 40},
  {"text": T("Griffin's Wharf", "Griffin İskelesi"), "at": [42.3536, -71.0525], "kind": "place", "from": 1773, "to": 1774, "lift_m": 10},
  {"text": T("Cambridge", "Cambridge"), "at": [42.3760, -71.1150], "kind": "place", "from": 1775, "to": 1775.45},
  {"text": T("Roxbury", "Roxbury"), "at": [42.3270, -71.0870], "kind": "place", "from": 1775, "to": 1775.45},
  {"text": T("Breed's Hill", "Breed's Tepesi"), "at": [42.3764, -71.0608], "kind": "place", "from": 1775.46, "to": 1776.1, "lift_m": 20},
  {"text": T("Dorchester Heights", "Dorchester Tepeleri"), "at": [42.3328, -71.0464], "kind": "place", "from": 1776.11, "to": 1776.5, "lift_m": 20},
  {"text": T("State House", "Eyalet Meclisi"), "at": [42.3582, -71.0637], "from": 1797, "to": 1806, "lift_m": 60},
  {"text": T("Mill Pond", "Değirmen Göleti"), "at": [42.3640, -71.0610], "kind": "water", "from": 1807, "to": 1820},
  {"text": T("Mill Dam", "Değirmen Bendi"), "at": [42.3530, -71.0820], "kind": "place", "from": 1821, "to": 1823, "lift_m": 10},
  {"text": T("Quincy Market", "Quincy Pazarı"), "at": [42.36008, -71.05480], "from": 1826, "to": 1832, "lift_m": 30},
  {"text": T("SOUTH COVE", "GÜNEY KOYU"), "at": [42.3500, -71.0570], "kind": "water", "from": 1833, "to": 1840},
  {"text": T("Copley Square", "Copley Meydanı"), "at": [42.3500, -71.0770], "kind": "place", "from": 1877, "to": 1887, "lift_m": 50},
  {"text": T("Kenmore Square", "Kenmore Meydanı"), "at": [42.3489, -71.0953], "kind": "place", "from": 1888, "to": 1896},
  {"text": T("Park Street", "Park Street"), "at": [42.3564, -71.0624], "kind": "place", "from": 1897, "to": 1898, "lift_m": 10},
  {"text": T("South Station", "South Station"), "at": [42.35194, -71.05528], "from": 1899, "to": 1911, "lift_m": 40},
  {"text": T("Custom House", "Gümrük Binası"), "at": [42.3591, -71.0534], "from": 1915, "to": 1918, "lift_m": 170},
  {"text": T("Fenway Park", "Fenway Park"), "at": [42.34639, -71.09778], "kind": "place", "from": 1912, "to": 1918, "lift_m": 30},
  {"text": T("North End", "Kuzey Yakası"), "at": [42.3650, -71.0545], "kind": "place", "from": 1919, "to": 1922, "lift_m": 20},
  {"text": T("East Boston", "Doğu Boston"), "at": [42.3750, -71.0360], "kind": "place", "from": 1923, "to": 1939},
  {"text": T("Logan Airport", "Logan Havalimanı"), "at": [42.3650, -71.0120], "kind": "place", "from": 1940, "to": 1950},
  {"text": T("West End", "Batı Yakası"), "at": [42.3640, -71.0660], "kind": "place", "from": 1958, "to": 1962, "lift_m": 20},
  {"text": T("Prudential", "Prudential"), "at": [42.3472, -71.0825], "from": 1964.2, "to": 1970, "lift_m": 250},
  {"text": T("City Hall", "Belediye"), "at": [42.3603222, -71.0579667], "from": 1968, "to": 1970, "lift_m": 50},
  {"text": T("Hancock Tower", "Hancock Kulesi"), "at": [42.349278, -71.074778], "from": 1976, "to": 1990, "lift_m": 260},
  {"text": T("Zakim Bridge", "Zakim Köprüsü"), "at": [42.36889, -71.06333], "from": 2003, "to": 2007, "lift_m": 40},
  {"text": T("BACK BAY", "BACK BAY"), "at": [42.3500, -71.0810], "kind": "region", "from": 2020},
  {"text": T("SOUTH BOSTON", "GÜNEY BOSTON"), "at": [42.3350, -71.0400], "kind": "region", "from": 2020},
  {"text": T("CHARLESTOWN", "CHARLESTOWN"), "at": [42.3780, -71.0610], "kind": "region", "from": 2020},
 ],
 "youtube": {
  "title": T("Boston: 400 Years in 15 Minutes (3D Timelapse)", "Boston: 15 Dakikada 400 Yıl (3D Timelapse)"),
  "description": T(
   "In 1625 one English settler lived on the Shawmut Peninsula. Watch Boston grow from a Puritan town of 1630 into a colonial seaport, "
   "the city of the Tea Party and the Siege of 1775–1776, and then a city that built itself new land: the Mill Pond, the South Cove, "
   "the Back Bay, the South Boston flats and Logan Airport were all once water. With the Long Wharf, Faneuil Hall, the State House, "
   "the Great Fires of 1760 and 1872, America's first subway, the Central Artery and the Big Dig, and the year and the population on screen.",
   "1625'te Shawmut Yarımadası'nda tek bir İngiliz yerleşimci yaşıyordu. Boston'un 1630'un Püriten kasabasından bir koloni limanına, "
   "Çay Partisi'nin ve 1775–1776 kuşatmasının şehrine, sonra kendine yeni toprak yaratan bir şehre dönüşmesini izleyin: Değirmen Göleti, "
   "Güney Koyu, Back Bay, Güney Boston sığlıkları ve Logan Havalimanı bir zamanlar denizdi. Uzun Rıhtım, Faneuil Hall, Eyalet Meclisi, "
   "1760 ve 1872 büyük yangınları, Amerika'nın ilk metrosu, Central Artery ve Big Dig; yıl ve nüfus ekranda."),
  "tags": ["boston history", "history of boston", "boston landfill", "back bay", "3d timelapse", "city evolution", "how boston grew",
           "boston timelapse", "boston tea party", "siege of boston", "made land", "big dig", "urban history", "massachusetts history"],
  "hashtags": ["#Boston", "#History", "#Timelapse"],
  "playlist": T("Cities of North America", "Kuzey Amerika Şehirleri"),
  "playlist_desc": T("North American cities rebuilt in 3D, from the first house to the skyline.", "Kuzey Amerika şehirleri 3D olarak, ilk evden siluete."),
  "thumb": {"line1": T("Boston", "Boston"), "line2": T("400 YEARS", "400 YIL"), "line3": T("A city built on new land", "Yeni toprak üzerine kurulan şehir"),
            "extra": "&mood=golden&pitch=30&az=0&cam=42.3560,-71.0640,6.0"},
 },
 "sources": [],
}
total = sum(s_["seconds"] for s_ in S)
mins = round(total / 60)
city["intro"] = T(f"400 Years in {mins} Minutes", f"{mins} Dakikada 400 Yıl")
city["youtube"]["title"] = T(f"Boston: 400 Years in {mins} Minutes (3D Timelapse)", f"Boston: {mins} Dakikada 400 Yıl (3D Timelapse)")
city["sources"] = json.load(open(os.path.join(HERE, "_sources.json")))
json.dump(city, open(os.path.join(HERE, "city.json"), "w"), ensure_ascii=False, indent=1)
print("segments", len(S), "duration", total, "s =", f"{total // 60}:{total % 60:02d}", "| fill polys", len(FILL), "(geo.json present)" if HAVE_GEO else "(no geo.json yet: fills left out)")
