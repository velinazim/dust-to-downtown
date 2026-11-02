"""Builds cities/amsterdam/city.json. Every on-screen date/figure is from research.md (sources listed there).
Run: python3 cities/amsterdam/_build.py

Water: Amsterdam lies below sea level, so the DEM cannot separate land and water (geo.sea_level_m is set far below
the polders and every cell starts as land). Water comes from OpenStreetMap river/lake polygons, from geo_edits for the
open IJ, and from timed_water for the canals, which are drawn at their digging dates (canals are not in the OSM query).
Reclaimed land (Haarlemmermeer, Diemermeer, the Eastern Islands, the station islands, the Eastern Docklands, IJburg) is
timed_water "fill": water until its year, then land. Fill zones are clipped to the modern land of geo.json when it
exists; without geo.json they are left out (first preview run only builds the modern map). Canal lines, district
outlines and fill zones are simplified traces (marked ≈ in research.md)."""
import json, math, os

T = lambda en, tr: {"en": en, "tr": tr}
HERE = os.path.dirname(os.path.abspath(__file__))
LAT0 = 52.372
KX = 111.32 * math.cos(math.radians(LAT0)); KZ = 110.574
rect = lambda s, w, n, e: [(s, w), (n, w), (n, e), (s, e)]


def L(pts):
    return [[round(a, 5), round(b, 5)] for a, b in pts]


def band(path, width_m):
    """Polyline -> polygon of the given width (canals)."""
    from shapely.geometry import LineString
    ls = LineString([((b - 4.9) * KX * 1000, (a - LAT0) * KZ * 1000) for a, b in path])
    p = ls.buffer(width_m / 2, cap_style=2, join_style=1).simplify(2)
    return [(LAT0 + y / KZ / 1000, 4.9 + x / KX / 1000) for x, y in list(p.exterior.coords)[:-1]]


# ------------------------------------------------------------------ canals and water (≈ traces, see research.md)
DAMRAK = [(52.3772, 4.8962), (52.3760, 4.8952), (52.3748, 4.8942)]
ROKIN = [(52.3702, 4.8922), (52.3688, 4.8925), (52.3676, 4.8930), (52.3668, 4.8940)]
AMSTEL_IN = [(52.3668, 4.8940), (52.3664, 4.8965), (52.3660, 4.8990), (52.3652, 4.9010), (52.3636, 4.9022),
             (52.3615, 4.9027), (52.3598, 4.9035), (52.3578, 4.9045),
             (52.3555, 4.9070), (52.3530, 4.9095), (52.3500, 4.9120), (52.3475, 4.9135)]
SINGEL = [(52.3786, 4.8942), (52.3778, 4.8922), (52.3762, 4.8907), (52.3745, 4.8898), (52.3725, 4.8893), (52.3705, 4.8892),
          (52.3688, 4.8895), (52.3676, 4.8910), (52.3669, 4.8935)]
KLOV = [(52.3671, 4.8968), (52.3690, 4.8975), (52.3710, 4.8990), (52.3725, 4.9002), (52.3742, 4.9010), (52.3757, 4.9018),
        (52.3765, 4.9023)]
OUDESCHANS = [(52.3700, 4.9040), (52.3715, 4.9052), (52.3735, 4.9068), (52.3755, 4.9080)]
HEREN_W = [(52.3808, 4.8912), (52.3788, 4.8895), (52.3765, 4.8882), (52.3740, 4.8875), (52.3715, 4.8874), (52.3692, 4.8878),
           (52.3675, 4.8884)]
HEREN_S = [(52.3675, 4.8884), (52.3662, 4.8892), (52.3655, 4.8912), (52.3653, 4.8940), (52.3654, 4.8975), (52.3656, 4.9005)]
KEIZ_W = [(52.3815, 4.8890), (52.3795, 4.8873), (52.3770, 4.8860), (52.3745, 4.8853), (52.3720, 4.8852), (52.3690, 4.8858),
          (52.3668, 4.8864)]
KEIZ_S = [(52.3668, 4.8864), (52.3650, 4.8874), (52.3638, 4.8896), (52.3634, 4.8930), (52.3633, 4.8970), (52.3632, 4.9015)]
PRINS_W = [(52.3822, 4.8868), (52.3800, 4.8851), (52.3775, 4.8838), (52.3750, 4.8831), (52.3725, 4.8829), (52.3690, 4.8838),
           (52.3662, 4.8848)]
PRINS_S = [(52.3662, 4.8848), (52.3645, 4.8860), (52.3626, 4.8883), (52.3617, 4.8915), (52.3612, 4.8960), (52.3610, 4.9025)]
SINGELGR_W = [(52.3848, 4.8828), (52.3820, 4.8800), (52.3790, 4.8782), (52.3755, 4.8772), (52.3720, 4.8775), (52.3690, 4.8785),
              (52.3660, 4.8800), (52.3640, 4.8815)]
SINGELGR_S = [(52.3640, 4.8815), (52.3626, 4.8835), (52.3616, 4.8860), (52.3606, 4.8895), (52.3598, 4.8930), (52.3594, 4.8975), (52.3590, 4.9030),
              (52.3600, 4.9090), (52.3615, 4.9150), (52.3630, 4.9200), (52.3655, 4.9240), (52.3685, 4.9255)]

# historic IJ shore before the station islands (≈): water north of this line (see fills)
OLD_SHORE = [(52.3800, 4.8880), (52.3790, 4.8915), (52.3780, 4.8945), (52.3772, 4.8970), (52.3768, 4.8995), (52.3766, 4.9030),
             (52.3770, 4.9070), (52.3765, 4.9110)]

# ------------------------------------------------------------------ fill zones (name, year it becomes land, zone)
ZONES = [
    ("Diemermeer / Watergraafsmeer (≈ outline)", 1629, [(52.3560, 4.9300), (52.3600, 4.9420), (52.3560, 4.9560), (52.3480, 4.9590),
                                                      (52.3420, 4.9500), (52.3440, 4.9340), (52.3500, 4.9280)]),
    ("Eastern Islands: Kattenburg, Wittenburg, Oostenburg (≈)", 1661, [(52.3730, 4.9130), (52.3790, 4.9120), (52.3800, 4.9230),
                                                                      (52.3765, 4.9300), (52.3710, 4.9270)]),
    ("Haarlemmermeer (≈ outline of the polder)", 1852, [(52.3400, 4.7700), (52.3330, 4.7350), (52.3330, 4.6700), (52.3200, 4.6300),
                                                       (52.2900, 4.6100), (52.2500, 4.5950), (52.2250, 4.6000), (52.2150, 4.6250),
                                                       (52.2300, 4.6700), (52.2550, 4.7100), (52.2800, 4.7500), (52.3000, 4.7800),
                                                       (52.3200, 4.7950), (52.3350, 4.7900)]),
    ("Station islands (≈)", 1884, [(52.3830, 4.8880), (52.3830, 4.9110)] + OLD_SHORE[::-1]),
    ("Eastern Docklands, inner (≈)", 1895, rect(52.3740, 4.9150, 52.3830, 4.9330)),
    ("Eastern Docklands, outer: KNSM and Java (≈)", 1915, rect(52.3740, 4.9330, 52.3830, 4.9500)),
    ("IJburg (≈)", 2004, rect(52.3500, 4.9820, 52.3660, 5.0350)),
]


def build_fill():
    gp = os.path.join(HERE, 'geo.json')
    if not os.path.exists(gp):
        return [], False
    import base64
    import numpy as np
    from shapely.geometry import Polygon, box
    from shapely.ops import unary_union
    g = json.load(open(gp)); lat0, lon0 = g['origin']
    k = 111.32 * math.cos(math.radians(lat0))
    def layer_land(c):
        el = np.frombuffer(base64.b64decode(c['elev_b64']), dtype='<i2').reshape(c['nz'], c['nx'])
        return c, el >= 0
    layers = [layer_land(g['core'])] if 'core' in g else []
    layers.append(layer_land(g))
    def land_in(geom):
        mnx, mny, mxx, mxy = geom.bounds
        for c, land in layers:
            cell = c['cell_km']
            gx0 = lon0 + (c['x0']) / k; gx1 = lon0 + (c['x0'] + c['nx'] * cell) / k
            gy1 = lat0 - c['z0'] / KZ; gy0 = lat0 - (c['z0'] + c['nz'] * cell) / KZ
            if not (mnx >= gx0 and mxx <= gx1 and mny >= gy0 and mxy <= gy1):
                continue
            i0 = max(0, int(((mnx - lon0) * k - c['x0']) / cell) - 1); i1 = min(c['nx'] - 1, int(((mxx - lon0) * k - c['x0']) / cell) + 1)
            j0 = max(0, int((-(mxy - lat0) * KZ - c['z0']) / cell) - 1); j1 = min(c['nz'] - 1, int((-(mny - lat0) * KZ - c['z0']) / cell) + 1)
            boxes = []
            for j in range(j0, j1 + 1):
                row = land[j, i0:i1 + 1]; i = 0
                while i < len(row):
                    if row[i]:
                        s0 = i
                        while i < len(row) and row[i]: i += 1
                        x0 = c['x0'] + (i0 + s0 - 0.5) * cell; x1 = c['x0'] + (i0 + i - 1 + 0.5) * cell
                        z0 = c['z0'] + (j - 0.5) * cell; z1 = c['z0'] + (j + 0.5) * cell
                        boxes.append(box(lon0 + x0 / k, lat0 - z1 / KZ, lon0 + x1 / k, lat0 - z0 / KZ))
                    else:
                        i += 1
            return unary_union(boxes).intersection(geom) if boxes else None
        return None
    out, taken = [], unary_union([])
    for name, year, zp in ZONES:
        z0 = Polygon([(b, a) for a, b in zp]).buffer(0)
        z = z0.difference(taken); taken = taken.union(z0)
        geom = land_in(z)
        if geom is None or geom.is_empty:
            continue
        geom = geom.buffer(0.0003).buffer(-0.0003).simplify(0.00006)
        parts = [geom] if geom.geom_type == 'Polygon' else list(getattr(geom, 'geoms', []))
        for i, p in enumerate(parts):
            if p.geom_type != 'Polygon' or p.area < 4e-7: continue
            ring = [(round(y, 5), round(x, 5)) for x, y in p.exterior.coords][:-1]
            out.append({"name": name + (f" #{i + 1}" if len(parts) > 1 else ""), "fill": True, "from": 1000, "to": year, "poly": L(ring)})
    return out, True


FILL, HAVE_GEO = build_fill()


def canal(name, path, frm, w=32):
    return {"name": name, "poly": L(band(path, w)), "from": frm, "to": None}


CANALS = [
    canal("Amstel: Damrak (≈)", DAMRAK, 1000, 60),
    canal("Amstel: Rokin (≈)", ROKIN, 1000, 50),
    canal("Amstel in the city (≈)", AMSTEL_IN, 1000, 70),
    canal("Singel (moat of 1425)", SINGEL, 1425, 34),
    canal("Kloveniersburgwal and Geldersekade (1425)", KLOV, 1425, 34),
    canal("Oudeschans (1515–1518)", OUDESCHANS, 1516, 34),
    canal("Herengracht, west (from 1613)", HEREN_W, 1614, 32),
    canal("Keizersgracht, west (from 1613)", KEIZ_W, 1616, 32),
    canal("Prinsengracht, west (from 1613)", PRINS_W, 1618, 32),
    canal("Singelgracht, west (1613)", SINGELGR_W, 1615, 40),
    canal("Herengracht, south (from about 1660)", HEREN_S, 1662, 32),
    canal("Keizersgracht, south (from about 1660)", KEIZ_S, 1664, 32),
    canal("Prinsengracht, south (from about 1660)", PRINS_S, 1666, 32),
    canal("Singelgracht, south and east (1657–c.1663)", SINGELGR_S, 1659, 40),
]

# open IJ in front of the city (≈), in case OSM maps it as a canal (then it is not in the river query)
GEO_EDITS = [
    {"op": "water", "poly": L([(52.3900, 4.8350), (52.3860, 4.8550), (52.3835, 4.8700), (52.3822, 4.8820), (52.3814, 4.8920),
                               (52.3812, 4.9050), (52.3815, 4.9150), (52.3808, 4.9250), (52.3805, 4.9400), (52.3790, 4.9550),
                               (52.3780, 4.9680), (52.3855, 4.9680), (52.3862, 4.9500), (52.3852, 4.9300), (52.3853, 4.9100),
                               (52.3857, 4.8950), (52.3872, 4.8800), (52.3900, 4.8650), (52.3950, 4.8450), (52.3980, 4.8350)])},
    # IJburg islands (≈): OSM's IJmeer polygon is used without its inner rings, so the islands are put back as land
    {"op": "land", "poly": L([(52.3600, 4.9800), (52.3640, 4.9880), (52.3620, 5.0050), (52.3560, 5.0200), (52.3500, 5.0180),
                              (52.3480, 5.0050), (52.3530, 4.9900)])},
]

# ------------------------------------------------------------------ built-up areas (≈ traces from the historical maps
# described in research.md: the town inside the Singel/Kloveniersburgwal, the 1585 and 1613 and 1657 expansions, the
# 19th-century belt, Plan Zuid, the western garden cities, the Bijlmermeer, IJburg)
DAM_VILLAGE = [(52.3768, 4.8950), (52.3745, 4.8925), (52.3720, 4.8918), (52.3705, 4.8925), (52.3712, 4.8960), (52.3740, 4.8985),
               (52.3762, 4.8995)]
MEDIEVAL = [(52.3784, 4.8935), (52.3770, 4.8915), (52.3745, 4.8903), (52.3715, 4.8898), (52.3688, 4.8900), (52.3672, 4.8925),
            (52.3672, 4.8962), (52.3700, 4.8980), (52.3730, 4.9000), (52.3760, 4.9015), (52.3766, 4.8995), (52.3772, 4.8970)]
LASTAGE = [(52.3762, 4.9025), (52.3742, 4.9015), (52.3705, 4.8992), (52.3690, 4.9030), (52.3705, 4.9045), (52.3740, 4.9070),
           (52.3762, 4.9075)]
EXP_1585 = [(52.3790, 4.8915), (52.3765, 4.8890), (52.3725, 4.8885), (52.3690, 4.8888), (52.3676, 4.8905), (52.3682, 4.8892),
            (52.3698, 4.8885), (52.3740, 4.8882), (52.3770, 4.8892), (52.3795, 4.8905)]
RING_W = [(52.3822, 4.8880), (52.3800, 4.8845), (52.3770, 4.8830), (52.3725, 4.8825), (52.3680, 4.8835), (52.3660, 4.8850),
          (52.3672, 4.8890), (52.3690, 4.8888), (52.3725, 4.8888), (52.3765, 4.8893), (52.3792, 4.8912), (52.3810, 4.8920)]
JORDAAN = [(52.3850, 4.8835), (52.3820, 4.8805), (52.3790, 4.8790), (52.3755, 4.8780), (52.3720, 4.8782), (52.3690, 4.8792),
           (52.3664, 4.8808), (52.3662, 4.8842), (52.3690, 4.8833), (52.3725, 4.8824), (52.3770, 4.8828), (52.3800, 4.8842),
           (52.3825, 4.8865)]
RING_S = [(52.3664, 4.8848), (52.3640, 4.8835), (52.3610, 4.8875), (52.3602, 4.8920), (52.3600, 4.8975), (52.3598, 4.9030),
          (52.3640, 4.9030), (52.3660, 4.9010), (52.3666, 4.8960), (52.3668, 4.8920), (52.3676, 4.8885)]
EAST_1660 = [(52.3690, 4.9040), (52.3660, 4.9040), (52.3610, 4.9045), (52.3610, 4.9100), (52.3630, 4.9190), (52.3680, 4.9240),
             (52.3720, 4.9250), (52.3730, 4.9130), (52.3740, 4.9080)]
OLD_CITY = [(52.3850, 4.8830), (52.3790, 4.8780), (52.3720, 4.8770), (52.3640, 4.8810), (52.3595, 4.8900), (52.3592, 4.9030),
            (52.3620, 4.9170), (52.3685, 4.9255), (52.3730, 4.9250), (52.3765, 4.9110), (52.3780, 4.8950), (52.3810, 4.8890)]
BELT_19 = [(52.3900, 4.8650), (52.3800, 4.8580), (52.3650, 4.8600), (52.3520, 4.8750), (52.3480, 4.8950), (52.3520, 4.9150),
           (52.3600, 4.9350), (52.3680, 4.9450), (52.3740, 4.9400), (52.3780, 4.9150), (52.3830, 4.8850)]
PLAN_ZUID = [(52.3550, 4.8550), (52.3460, 4.8600), (52.3420, 4.8800), (52.3430, 4.9000), (52.3480, 4.9100), (52.3520, 4.9000),
             (52.3520, 4.8800)]
NOORD = [(52.4100, 4.8800), (52.4150, 4.9300), (52.4000, 4.9600), (52.3880, 4.9550), (52.3880, 4.9100), (52.3890, 4.8800)]
WEST_GARDEN = [(52.3850, 4.7900), (52.3850, 4.8350), (52.3700, 4.8450), (52.3500, 4.8450), (52.3450, 4.8200), (52.3500, 4.7850),
               (52.3700, 4.7800)]
BUITENVELDERT = [(52.3380, 4.8450), (52.3380, 4.9050), (52.3250, 4.9050), (52.3250, 4.8500)]
BIJLMER = [(52.3250, 4.9400), (52.3250, 4.9900), (52.3000, 4.9900), (52.2950, 4.9500), (52.3100, 4.9350)]
ZUIDAS = [(52.3400, 4.8600), (52.3400, 4.8850), (52.3355, 4.8850), (52.3355, 4.8600)]
SUBURBS = [(52.4600, 4.6500), (52.4700, 5.0000), (52.4300, 5.0800), (52.3300, 5.0600), (52.2600, 4.9800), (52.2600, 4.8300),
           (52.3200, 4.6300), (52.4000, 4.6100)]
IJBURG = [(52.3600, 4.9850), (52.3620, 5.0050), (52.3540, 5.0180), (52.3480, 5.0050), (52.3500, 4.9850)]
DOCKLANDS = [(52.3800, 4.9200), (52.3810, 4.9480), (52.3760, 4.9480), (52.3755, 4.9200)]
OOSTENBURG = [(52.3785, 4.9135), (52.3790, 4.9220), (52.3765, 4.9280), (52.3725, 4.9255), (52.3735, 4.9140)]


def D(name, style, poly, frm, to, dens, grain, grow, **kw):
    d = {"name": name, "style": style, "poly": L(poly), "from": frm, "to": to, "density": dens, "grain_m": grain, "grow_from": list(grow)}
    d.update(kw); return d


districts = [
 D("Dam village (≈)", "medieval", DAM_VILLAGE, 1270, 1320, 0.55, 45, (52.3735, 4.8935)),
 D("Medieval town (≈)", "medieval", MEDIEVAL, 1300, 1450, 0.75, 42, (52.3735, 4.8940), holes=[L(DAM_VILLAGE)]),
 D("Rebuilt in brick after 1452", "stone", MEDIEVAL, 1453, 1500, 0.8, 40, (52.3735, 4.8940)),
 D("Lastage (≈)", "medieval", LASTAGE, 1500, 1590, 0.6, 48, (52.3745, 4.9030)),
 D("1585 expansion (≈)", "stone", EXP_1585, 1585, 1605, 0.75, 42, (52.3740, 4.8890)),
 D("Canal ring, west (1613 →)", "stone", RING_W, 1614, 1650, 0.8, 42, (52.3760, 4.8860), holes=[L(EXP_1585)]),
 D("Jordaan (≈)", "medieval", JORDAAN, 1614, 1660, 0.85, 38, (52.3760, 4.8805)),
 D("Canal ring, south (1660s →)", "stone", RING_S, 1662, 1720, 0.75, 44, (52.3640, 4.8900)),
 D("Eastern expansion (≈)", "stone", EAST_1660, 1660, 1720, 0.55, 50, (52.3680, 4.9080)),
 D("Eastern Islands shipyards", "industrial", OOSTENBURG, 1661, 1700, 0.55, 60, (52.3765, 4.9200)),
 D("19th-century belt (≈)", "victorian", BELT_19, 1877, 1914, 0.85, 52, (52.3700, 4.8900), holes=[L(OLD_CITY), L(PLAN_ZUID)]),
 D("Eastern Docklands (≈)", "industrial", DOCKLANDS, 1896, 1927, 0.6, 70, (52.3780, 4.9300)),
 D("Plan Zuid (≈)", "georgian", PLAN_ZUID, 1917, 1940, 0.8, 55, (52.3520, 4.8850), grid_deg=10),
 D("Amsterdam-Noord (≈)", "suburb", NOORD, 1910, 1970, 0.6, 75, (52.3920, 4.9050)),
 D("Western garden cities (≈)", "modern", WEST_GARDEN, 1950, 1970, 0.6, 90, (52.3650, 4.8350)),
 D("Buitenveldert and Amstelveen (≈)", "suburb", BUITENVELDERT, 1958, 1975, 0.6, 90, (52.3350, 4.8800)),
 D("Bijlmermeer (≈)", "highrise", BIJLMER, 1966, 1980, 0.35, 170, (52.3150, 4.9550)),
 D("Region towns and suburbs (≈)", "suburb", SUBURBS, 1900, 1995, 0.4, 160, (52.3700, 4.8900),
   holes=[L(OLD_CITY), L(BELT_19), L(PLAN_ZUID), L(NOORD), L(WEST_GARDEN), L(BUITENVELDERT), L(BIJLMER), L(IJBURG)]),
 D("Docklands rebuilt (≈)", "modern", DOCKLANDS, 1990, 2010, 0.6, 75, (52.3780, 4.9350)),
 D("Zuidas (≈)", "highrise", ZUIDAS, 1998, 2022, 0.5, 90, (52.3380, 4.8730)),
 D("IJburg (≈)", "modern", IJBURG, 2003, 2025, 0.6, 85, (52.3540, 4.9950)),
]

# ------------------------------------------------------------------ landmarks (Wikipedia / latlong.net coordinates)
landmarks = [
 {"type": "church", "name": T("Oude Kerk", "Oude Kerk"), "at": [52.3744, 4.8980], "built": 1300, "rise_s": 5, "size_m": [70, 40, 30],
  "rot_deg": 60, "colors": {"wall": "#b8aa92", "roof": "#5f666f"}, "scale": 1.3},
 {"type": "church", "name": T("Nieuwe Kerk", "Nieuwe Kerk"), "at": [52.3739, 4.8917], "built": 1385, "rise_s": 6, "size_m": [80, 40, 30],
  "rot_deg": 0, "colors": {"wall": "#b8aa92", "roof": "#5f666f"}, "scale": 1.3},
 {"type": "tower", "name": T("Schreierstoren", "Schreierstoren"), "at": [52.37644, 4.90227], "built": 1485, "rise_s": 3, "size_m": [14, 14, 14],
  "colors": {"wall": "#8a5a44"}},
 {"type": "castle", "name": T("Sint Antoniespoort (Waag)", "Sint Antoniespoort (Waag)"), "at": [52.372746, 4.900323], "built": 1488, "rise_s": 4,
  "size_m": [26, 22, 22], "colors": {"wall": "#8a5a44", "roof": "#4f565f"}},
 {"type": "tower", "name": T("Regulierspoort", "Regulierspoort"), "at": [52.367001, 4.893151], "built": 1480, "removed": 1618.4, "rise_s": 3,
  "size_m": [16, 16, 20], "colors": {"wall": "#8a5a44"}},
 {"type": "clocktower", "name": T("Munttoren", "Munttoren"), "at": [52.367001, 4.893151], "built": 1619.5, "rise_s": 5, "size_m": [12, 12, 40],
  "colors": {"wall": "#8a5a44", "roof": "#3f4a46"}},
 {"type": "tower", "name": T("Montelbaanstoren (≈ height before 1606)", "Montelbaanstoren"), "at": [52.3720583, 4.9056833], "built": 1516,
  "removed": 1606, "rise_s": 4, "size_m": [12, 12, 22], "colors": {"wall": "#8a5a44"}},
 {"type": "clocktower", "name": T("Montelbaanstoren", "Montelbaanstoren"), "at": [52.3720583, 4.9056833], "built": 1606, "rise_s": 2,
  "size_m": [12, 12, 48], "colors": {"wall": "#8a5a44", "roof": "#3f4a46"}},
 {"type": "church", "name": T("Westerkerk", "Westerkerk"), "at": [52.37444, 4.88361], "built": 1620, "rise_s": 10, "size_m": [58, 29, 24],
  "rot_deg": 90, "colors": {"wall": "#a4513a", "roof": "#4f565f"}, "scale": 1.2},
 {"type": "clocktower", "name": T("Westerkerk tower (west end, ≈)", "Westerkerk kulesi"), "at": [52.37446, 4.88320], "built": 1620.5, "rise_s": 10,
  "size_m": [11, 11, 87], "colors": {"wall": "#a4513a", "roof": "#3f4a46"}},
 {"type": "palace", "name": T("Town Hall (Royal Palace)", "Belediye Sarayı (Kraliyet Sarayı)"), "at": [52.37317, 4.89136], "built": 1652.6,
  "rise_s": 8, "size_m": [80, 60, 33], "rot_deg": 0, "colors": {"wall": "#d8cdb5", "roof": "#5f666f"}, "scale": 1.2},
 {"type": "palace", "name": T("Rijksmuseum", "Rijksmuseum"), "at": [52.360001, 4.885278], "built": 1876.8, "rise_s": 10, "size_m": [140, 70, 30],
  "rot_deg": 0, "colors": {"wall": "#a4513a", "roof": "#4f565f"}},
 {"type": "box", "name": T("Concertgebouw", "Concertgebouw"), "at": [52.3563, 4.8791], "built": 1883, "rise_s": 6, "size_m": [70, 45, 25],
  "colors": {"wall": "#b8694f", "roof": "#4f565f"}},
 {"type": "station", "name": T("Centraal Station", "Merkez İstasyonu"), "at": [52.37833, 4.90000], "built": 1882, "rise_s": 10,
  "size_m": [310, 80, 30], "rot_deg": -5, "colors": {"wall": "#a4513a", "roof": "#59656a"}},
 {"type": "stadium", "name": T("Olympic Stadium", "Olimpiyat Stadı"), "at": [52.34333, 4.85417], "built": 1927, "rise_s": 5,
  "size_m": [230, 160, 20], "colors": {"wall": "#8f4a37"}},
]

walls = [
 {"name": "Brick wall, west (1482–1494)", "path": L(SINGEL[:-1] + [(52.3670, 4.8930)]), "built": 1482, "removed": 1610, "height": "mid",
  "towers_m": 110, "draw_s": 3.0},
 {"name": "Brick wall, east (1482–1494)", "path": L([(52.3672, 4.8962)] + KLOV[1:]), "built": 1482, "removed": 1610, "height": "mid",
  "towers_m": 110, "draw_s": 3.0},
 {"name": "Bastioned rampart, 1585 (≈ east)", "path": L(OUDESCHANS), "built": 1585, "removed": 1660, "height": "low", "towers_m": 0, "draw_s": 2.0},
 {"name": "Bastioned rampart, west (1613)", "path": L(SINGELGR_W), "built": 1615, "removed": 1848, "height": "low", "towers_m": 160,
  "draw_s": 3.0, "double_side": -1},
 {"name": "Bastioned rampart, south and east (1657–c.1663)", "path": L(SINGELGR_S), "built": 1659, "removed": 1848, "height": "low",
  "towers_m": 160, "draw_s": 4.0, "double_side": -1},
]

bridges = [
 {"name": "Magere Brug (≈ site)", "path": [[52.3636, 4.9012], [52.3632, 4.9035]], "built": 1691, "style": "wood", "width_m": 10},
]

roads = [
 {"name": "Haarlem railway (1839, ≈)", "path": L([(52.3800, 4.8800), (52.3830, 4.8500), (52.3860, 4.8000), (52.3820, 4.7200),
  (52.3800, 4.6500)]), "from": 1839, "kind": "rail", "width_m": 18},
 {"name": "Railway along the IJ to Centraal (1889, ≈)", "path": L([(52.3800, 4.8800), (52.3795, 4.8900), (52.3793, 4.9000),
  (52.3785, 4.9150), (52.3720, 4.9350), (52.3600, 4.9500)]), "from": 1889, "kind": "rail", "width_m": 20},
]

# ------------------------------------------------------------------ timeline
def seg(frm, to, sec, era, city, title=None, sub=None, pop=None, cam=None, chapter=None):
    d = {"from": frm, "to": to, "seconds": sec, "era": era, "city_name": city}
    if title: d["title"] = title; d["sub"] = sub
    if pop is not None: d["population"] = pop
    if cam: d["camera"] = {"center": [cam[0], cam[1]], "dist_km": cam[2]}
    if chapter: d["chapter"] = chapter
    return d


MED = T("Middle Ages", "Orta Çağ"); GOLD = T("Golden Age", "Altın Çağ"); REP = T("Dutch Republic", "Hollanda Cumhuriyeti")
FR = T("French Period", "Fransız Dönemi"); IND = T("Industrial Age", "Sanayi Çağı"); MOD = T("20th Century", "20. Yüzyıl")
WAR = T("Occupation", "İşgal"); TODAY = T("Today", "Bugün")
AMS = T("Amsterdam", "Amsterdam"); AMD = T("Amestelledamme", "Amestelledamme"); AMSTEL = T("Amstel", "Amstel")

# sourced anchors (year, people) — research.md; log-interpolated between them (1300→1600 is an interpolation, see notes)
ANCH = [(1300, 1000), (1600, 50000), (1622, 105000), (1666, 200000), (1675, 195000), (1700, 210000), (1750, 219000), (1775, 209000),
        (1800, 195000), (1815, 180179), (1825, 196000), (1850, 225000), (1866, 264498), (1876, 281944), (1884, 361326), (1900, 523557),
        (1919, 647120), (1936, 859000), (1959, 872000), (1970, 807095), (1990, 695221), (2001, 752624), (2011, 797795), (2016, 852196),
        (2021, 893783), (2024, 931298), (2026, 942504)]


def P(y):
    for (y0, p0), (y1, p1) in zip(ANCH, ANCH[1:]):
        if y0 <= y <= y1:
            u = (y - y0) / (y1 - y0); v = math.exp(math.log(p0) + (math.log(p1) - math.log(p0)) * u)
            return int(round(v, -2 if v < 100000 else -3))
    raise ValueError(y)


PI = lambda a, b: [P(a), P(b)]
C = (52.3735, 4.8950)
S = [
 seg(1000, 1269, 18, MED, AMSTEL, T("Peat Bog on the Amstel", "Amstel Kıyısında Turbalık"),
     T("Around 1000: the first farmers settle the wet peat land where the Amstel meets the IJ",
       "1000 civarı: ilk çiftçiler Amstel'in IJ ile buluştuğu ıslak turbalığa yerleşir"),
     cam=(52.3745, 4.8945, 3.2), chapter=T("A Dam on the Amstel", "Amstel'de Bir Bent")),
 seg(1270, 1299, 18, MED, AMD, T("A Dam in the Amstel", "Amstel'e Bir Bent"),
     T("27 October 1275: a toll privilege gives the oldest record of the name Amestelledamme",
       "27 Ekim 1275: bir gümrük ayrıcalığı, Amestelledamme adının bilinen en eski kaydıdır"),
     cam=(52.3740, 4.8940, 2.4)),
 seg(1300, 1344, 17, MED, AMS, T("City Rights", "Şehir Hakları"),
     T("1306: Amsterdam receives city rights, and its stone church, the Oude Kerk, is consecrated",
       "1306: Amsterdam şehir hakları alır; ilk taş kilisesi Oude Kerk takdis edilir"),
     pop=PI(1300, 1344), cam=(52.3742, 4.8955, 2.4)),
 seg(1345, 1384, 15, MED, AMS, T("A Pilgrim Town", "Bir Hac Kasabası"),
     T("1345: a reported miracle draws pilgrims; a chapel, the Heilige Stede, follows in 1347",
       "1345: anlatılan bir mucize hacıları çeker; 1347'de Heilige Stede şapeli yapılır"),
     pop=PI(1345, 1384), cam=(52.3738, 4.8945, 2.6)),
 seg(1385, 1420, 16, MED, AMS, T("The Nieuwe Kerk", "Nieuwe Kerk"),
     T("1385: new walls and moats ring the town; a second parish church is consecrated in 1409",
       "1385: kasabayı yeni surlar ve hendekler çevirir; ikinci bölge kilisesi 1409'da takdis edilir"),
     pop=PI(1385, 1420), cam=(52.3738, 4.8930, 2.6)),
 seg(1421, 1424, 14, MED, AMS, T("The Fire of 1421", "1421 Yangını"),
     T("1421: a fire destroys about a third of the wooden town",
       "1421: bir yangın ahşap kasabanın yaklaşık üçte birini yok eder"),
     pop=PI(1421, 1424), cam=(52.3735, 4.8945, 2.4)),
 seg(1425, 1451, 15, MED, AMS, T("A New Moat", "Yeni Bir Hendek"),
     T("1425: a moat is dug around the town, today's Singel, Kloveniersburgwal and Geldersekade",
       "1425: kasabanın çevresine bugünkü Singel, Kloveniersburgwal ve Geldersekade kazılır"),
     pop=PI(1425, 1451), cam=(52.3725, 4.8955, 3.0)),
 seg(1452, 1480, 16, MED, AMS, T("The Great Fire of 1452", "1452 Büyük Yangını"),
     T("1452: fire destroys three quarters of Amsterdam; new houses must be built of stone",
       "1452: yangın Amsterdam'ın dörtte üçünü yok eder; yeni evler taştan yapılmak zorundadır"),
     pop=PI(1452, 1480), cam=(52.3735, 4.8950, 2.6)),
 seg(1481, 1514, 17, MED, AMS, T("A Wall of Brick", "Tuğladan Bir Sur"),
     T("1482–1494: a brick wall 5–6 m high rises with towers like the Schreierstoren of c. 1487",
       "1482–1494: Schreierstoren (1487 civarı) gibi kulelerle 5–6 m yüksekliğinde tuğla sur yükselir"),
     pop=PI(1481, 1514), cam=(52.3725, 4.8960, 2.8), chapter=T("The Walled Town", "Surlu Kasaba")),
 seg(1515, 1577, 15, MED, AMS, T("The Montelbaanstoren", "Montelbaanstoren"),
     T("1515–1518: a new moat guards the shipyards of the Lastage; a watchtower rises c. 1516",
       "1515–1518: yeni bir hendek Lastage tersanelerini korur; 1516 civarı bir gözcü kulesi yükselir"),
     pop=PI(1515, 1577), cam=(52.3730, 4.9010, 2.4)),
 seg(1578, 1584, 15, MED, AMS, T("The Alteratie", "Alteratie"),
     T("1578: Amsterdam changes sides in the Dutch Revolt without bloodshed and joins the rebels",
       "1578: Amsterdam, Hollanda İsyanı'nda kan dökülmeden taraf değiştirir ve isyancılara katılır"),
     pop=PI(1578, 1584), cam=(52.3730, 4.8950, 3.0)),
 seg(1585, 1601, 17, GOLD, AMS, T("Merchants from Antwerp", "Antwerpenli Tüccarlar"),
     T("1585: Antwerp falls, its merchants move north, and Amsterdam builds new walls with 11 bastions",
       "1585: Antwerpen düşer, tüccarları kuzeye göçer; Amsterdam 11 burçlu yeni surlar yapar"),
     pop=PI(1585, 1601), cam=(52.3730, 4.8960, 3.4), chapter=T("Golden Age", "Altın Çağ")),
 seg(1602, 1612, 16, GOLD, AMS, T("The East India Company", "Doğu Hindistan Şirketi"),
     T("1602: the VOC is founded and Amsterdam's stock exchange begins; about 50,000 people live here",
       "1602: VOC kurulur ve Amsterdam borsası başlar; şehirde yaklaşık 50.000 kişi yaşar"),
     pop=PI(1602, 1612), cam=(52.3740, 4.8970, 3.4)),
 seg(1613, 1619, 18, GOLD, AMS, T("The Canal Ring", "Kanal Kuşağı"),
     T("1613: digging begins on the Herengracht, Keizersgracht and Prinsengracht, finished c. 1625",
       "1613: Herengracht, Keizersgracht ve Prinsengracht kazılmaya başlar; 1625 civarı tamamlanır"),
     pop=PI(1613, 1619), cam=(52.3745, 4.8870, 3.0)),
 seg(1620, 1628, 15, GOLD, AMS, T("The Munttoren", "Munttoren"),
     T("1620: the burnt Regulierspoort gate gets a new tower by Hendrick de Keyser",
       "1620: yanmış Regulierspoort kapısına Hendrick de Keyser yeni bir kule tasarlar"),
     pop=PI(1620, 1628), cam=(52.3690, 4.8930, 2.6)),
 seg(1629, 1630, 14, GOLD, AMS, T("Draining the Diemermeer", "Diemermeer Kurutuluyor"),
     T("1629: the Diemermeer lake east of the city is drained; today it is the Watergraafsmeer",
       "1629: şehrin doğusundaki Diemermeer gölü kurutulur; bugün Watergraafsmeer'dir"),
     pop=PI(1629, 1630), cam=(52.3600, 4.9300, 7.0)),
 seg(1631, 1647, 16, GOLD, AMS, T("The Westerkerk", "Westerkerk"),
     T("1631: the Westerkerk opens in the new canal district; its tower is 87 m tall",
       "1631: Westerkerk yeni kanal semtinde açılır; kulesi 87 m yüksekliğindedir"),
     pop=PI(1631, 1647), cam=(52.3740, 4.8860, 2.4)),
 seg(1648, 1651, 15, GOLD, AMS, T("A New Town Hall", "Yeni Bir Belediye Binası"),
     T("1648: work begins on a vast town hall on the Dam, standing on 13,659 wooden piles",
       "1648: Dam Meydanı'nda 13.659 ahşap kazık üzerinde dev bir belediye binası başlar"),
     pop=PI(1648, 1651), cam=(52.3730, 4.8925, 2.0)),
 seg(1652, 1656, 15, GOLD, AMS, T("The Old Town Hall Burns", "Eski Belediye Yanıyor"),
     T("7 July 1652: the old town hall burns down; the new one is inaugurated in July 1655",
       "7 Temmuz 1652: eski belediye binası yanar; yenisi Temmuz 1655'te açılır"),
     pop=PI(1652, 1656), cam=(52.3730, 4.8925, 2.0)),
 seg(1657, 1662, 18, GOLD, AMS, T("The Great Expansion", "Büyük Genişleme"),
     T("1657–c.1663: a rampart with 26 bastions rings the city; harbour islands rise in the east",
       "1657–1663 civarı: 26 burçlu yeni bir sur şehri sarar; doğuda liman adaları yapılır"),
     pop=PI(1657, 1662), cam=(52.3700, 4.9000, 4.4)),
 seg(1663, 1666, 15, GOLD, AMS, T("Plague", "Veba"),
     T("1663–1666: bubonic plague; in 1664 alone 24,148 people are buried",
       "1663–1666: veba salgını; yalnızca 1664'te 24.148 kişi gömülür"),
     pop=PI(1663, 1666), cam=(52.3720, 4.8950, 3.4)),
 seg(1667, 1671, 15, GOLD, AMS, T("Canals to the Amstel", "Kanallar Amstel'e"),
     T("From about 1660 the three canals are extended to the Amstel, giving the city its crescent",
       "1660 civarından itibaren üç kanal Amstel'e uzatılır ve şehir hilal biçimini alır"),
     pop=PI(1667, 1671), cam=(52.3660, 4.8950, 2.6)),
 seg(1672, 1699, 15, REP, AMS, T("The Disaster Year", "Felaket Yılı"),
     T("1672: France invades the Republic; the flooded Water Line stops it before Amsterdam",
       "1672: Fransa Cumhuriyet'i işgal eder; su baskını hattı onu Amsterdam'dan önce durdurur"),
     pop=PI(1672, 1699), cam=(52.3700, 4.8950, 5.0)),
 seg(1700, 1779, 16, REP, AMS, T("A Rich, Quiet Century", "Zengin, Sakin Bir Yüzyıl"),
     T("1700–1775: Amsterdam stays near 210,000 people as its wealth stops growing",
       "1700–1775: refahı artmayı bırakırken Amsterdam yaklaşık 210.000 kişide kalır"),
     pop=PI(1700, 1779), cam=(52.3700, 4.8960, 4.0), chapter=T("Decline and French Rule", "Gerileme ve Fransız Yönetimi")),
 seg(1780, 1794, 14, REP, AMS, T("War with Britain", "İngiltere ile Savaş"),
     T("1780–1784: the Fourth Anglo-Dutch War hits Amsterdam hard",
       "1780–1784: Dördüncü İngiliz-Hollanda Savaşı Amsterdam'ı ağır vurur"),
     pop=PI(1780, 1794), cam=(52.3740, 4.9050, 3.6)),
 seg(1795, 1809, 15, FR, AMS, T("The French Arrive", "Fransızlar Geliyor"),
     T("1795: France takes the Netherlands; in 1808 the town hall becomes a royal palace",
       "1795: Fransa Hollanda'yı alır; 1808'de belediye binası kraliyet sarayı olur"),
     pop=PI(1795, 1809), cam=(52.3730, 4.8925, 2.2)),
 seg(1810, 1838, 15, FR, AMS, T("Capital Again", "Yeniden Başkent"),
     T("1810: annexed by France; the French leave on 16 November 1813 and Amsterdam is capital in 1814",
       "1810: Fransa'ya katılır; Fransızlar 16 Kasım 1813'te çekilir, Amsterdam 1814'te başkent olur"),
     pop=PI(1810, 1838), cam=(52.3720, 4.8950, 3.6)),
 seg(1839, 1847, 15, IND, AMS, T("The First Railway", "İlk Demiryolu"),
     T("1839: the Haarlem line opens, and from 1839 to 1848 the old ramparts are pulled down",
       "1839: Haarlem hattı açılır; 1839–1848 arasında eski surlar yıkılır"),
     pop=PI(1839, 1847), cam=(52.3740, 4.8700, 6.0), chapter=T("Industrial Amsterdam", "Sanayi Amsterdamı")),
 seg(1848, 1852, 15, IND, AMS, T("Haarlemmermeer Pumped Dry", "Haarlemmermeer Kurutuluyor"),
     T("1849–1852: three steam pumping stations drain the Haarlemmermeer, about 180 km² of lake",
       "1849–1852: üç buharlı pompa istasyonu yaklaşık 180 km²'lik Haarlemmermeer'i kurutur"),
     pop=PI(1848, 1852), cam=(52.3200, 4.7600, 22.0)),
 seg(1853, 1864, 7, IND, AMS, pop=PI(1853, 1864), cam=(52.3650, 4.8800, 10.0)),
 seg(1865, 1875, 16, IND, AMS, T("The North Sea Canal", "Kuzey Denizi Kanalı"),
     T("1865: digging starts on a canal to the sea; by 1872 the main reclamations of the IJ are done",
       "1865: denize bir kanal kazılmaya başlar; 1872'de IJ'deki büyük kurutmalar tamamlanır"),
     pop=PI(1865, 1875), cam=(52.3790, 4.9000, 5.5)),
 seg(1876, 1881, 15, IND, AMS, T("A Shortcut to the Sea", "Denize Kestirme"),
     T("1 November 1876: the North Sea Canal opens; new docks follow east of the city",
       "1 Kasım 1876: Kuzey Denizi Kanalı açılır; şehrin doğusunda yeni rıhtımlar yapılır"),
     pop=PI(1876, 1881), cam=(52.3780, 4.9150, 5.0)),
 seg(1882, 1888, 15, IND, AMS, T("The Rijksmuseum", "Rijksmuseum"),
     T("13 July 1885: the Rijksmuseum opens; the Concertgebouw follows on 11 April 1888",
       "13 Temmuz 1885: Rijksmuseum açılır; Concertgebouw 11 Nisan 1888'de onu izler"),
     pop=PI(1882, 1888), cam=(52.3600, 4.8840, 2.8)),
 seg(1889, 1899, 16, IND, AMS, T("Centraal Station", "Merkez İstasyonu"),
     T("15 October 1889: Centraal Station opens on three artificial islands in the IJ",
       "15 Ekim 1889: Merkez İstasyonu, IJ'de üç yapay ada üzerinde açılır"),
     pop=PI(1889, 1899), cam=(52.3770, 4.8990, 2.4)),
 seg(1900, 1916, 15, MOD, AMS, T("Half a Million", "Yarım Milyon"),
     T("1900: Amsterdam has 523,557 people; new quarters now ring the old canal city",
       "1900: Amsterdam'ın nüfusu 523.557'dir; yeni mahalleler eski kanal şehrini çevreler"),
     pop=PI(1900, 1916), cam=(52.3680, 4.8950, 7.0), chapter=T("Modern Amsterdam", "Modern Amsterdam")),
 seg(1917, 1927, 15, MOD, AMS, T("Plan Zuid", "Güney Planı"),
     T("1917: building starts on Plan Zuid; in 1921 the city grows from 4,630 to 17,455 hectares",
       "1917: Güney Planı'nın inşası başlar; 1921'de şehir 4.630'dan 17.455 hektara büyür"),
     pop=PI(1917, 1927), cam=(52.3550, 4.8850, 6.0)),
 seg(1928, 1939, 15, MOD, AMS, T("The 1928 Olympics", "1928 Olimpiyatları"),
     T("17 May 1928: the Olympic Stadium opens for the Summer Games",
       "17 Mayıs 1928: Olimpiyat Stadı Yaz Oyunları için açılır"),
     pop=PI(1928, 1939), cam=(52.3480, 4.8650, 4.0)),
 seg(1940, 1943, 17, WAR, AMS, T("Occupation", "İşgal"),
     T("1940: German occupation begins; in February 1941 workers strike against the persecution of Jews",
       "1940: Alman işgali başlar; Şubat 1941'de işçiler Yahudilere zulme karşı grev yapar"),
     pop=P(1940), cam=(52.3720, 4.8900, 3.6), chapter=T("War", "Savaş")),
 seg(1944, 1945.4, 17, WAR, AMS, T("Persecution and Hunger", "Zulüm ve Açlık"),
     T("Three quarters of Dutch Jews are deported and murdered; famine follows in winter 1944–45",
       "Hollanda Yahudilerinin dörtte üçü sürgün edilip öldürülür; 1944–45 kışında kıtlık baş gösterir"),
     pop=P(1944), cam=(52.3720, 4.8900, 4.4)),
 seg(1945.4, 1965, 16, MOD, AMS, T("Garden Cities", "Bahçe Şehirler"),
     T("1950s–1960s: following the 1935 expansion plan, garden cities rise in the west",
       "1950'ler–1960'lar: 1935 genişleme planına göre batıda bahçe şehirler yükselir"),
     pop=[P(1946), P(1965)], cam=(52.3650, 4.8500, 9.0), chapter=T("The Growing Metropolis", "Büyüyen Metropol")),
 seg(1966, 1976, 15, MOD, AMS, T("The Bijlmermeer", "Bijlmermeer"),
     T("1968: the Bijlmermeer, a district of high-rise blocks, opens southeast of the city",
       "1968: yüksek bloklardan oluşan Bijlmermeer semti şehrin güneydoğusunda açılır"),
     pop=PI(1966, 1976), cam=(52.3300, 4.9300, 10.0)),
 seg(1977, 1996, 15, MOD, AMS, T("Metro and the Old City", "Metro ve Eski Şehir"),
     T("1977: the metro opens; after the 1975 Nieuwmarkt riots, a city motorway plan is dropped",
       "1977: metro açılır; 1975 Nieuwmarkt olaylarından sonra merkezden geçecek otoyoldan vazgeçilir"),
     pop=PI(1977, 1996), cam=(52.3700, 4.9000, 5.0)),
 seg(1997, 2009, 15, TODAY, AMS, T("Islands in the IJmeer", "IJmeer'de Adalar"),
     T("1997: work begins on IJburg, a new district built on artificial islands",
       "1997: yapay adalar üzerine kurulan yeni bir semt olan IJburg'ün yapımı başlar"),
     pop=PI(1997, 2009), cam=(52.3600, 4.9700, 8.0), chapter=T("Amsterdam Today", "Bugünün Amsterdamı")),
 seg(2010, 2019, 15, TODAY, AMS, T("World Heritage", "Dünya Mirası"),
     T("1 August 2010: the 17th-century canal ring becomes a UNESCO World Heritage Site",
       "1 Ağustos 2010: 17. yüzyıl kanal kuşağı UNESCO Dünya Mirası Listesi'ne girer"),
     pop=PI(2010, 2019), cam=(52.3700, 4.8900, 3.6)),
 seg(2020, 2026, 22, TODAY, AMS, T("Amsterdam Today", "Bugünün Amsterdamı"),
     T("From a dam on the Amstel to 942,504 Amsterdammers, a record, in January 2026",
       "Amstel'deki bir bentten Ocak 2026'da rekor seviyedeki 942.504 Amsterdamlıya"),
     pop=PI(2020, 2026), cam=(52.3600, 4.8950, 16.0)),
]
SCALE_T, SCALE_Q = 1.2, 1.1
for s_ in S:
    s_["seconds"] = round(s_["seconds"] * (SCALE_T if s_.get("title") else SCALE_Q))

FIRE_1421 = [(52.3760, 4.8960), (52.3745, 4.8930), (52.3725, 4.8925), (52.3725, 4.8955), (52.3745, 4.8980)]

city = {
 "slug": "amsterdam", "seed": 1275, "long_ok": True,
 "name": T("Amsterdam", "Amsterdam"), "intro": T("1,000 Years in 15 Minutes", "15 Dakikada 1.000 Yıl"), "intro_seconds": 4.5,
 "geo": {"bbox": [52.19, 4.56, 52.50, 5.16], "cell_m": 100, "core_bbox": [52.335, 4.835, 52.400, 5.025], "core_cell_m": 30,
         "sea_level_m": -30},
 "geo_edits": GEO_EDITS,
 "view": {"azimuth_deg": 0, "pitch_deg": 46, "fov": 34},
 "render": {"vertical_exaggeration": 3.0},
 "segments": S,
 "timed_water": CANALS + FILL,
 "districts": districts,
 "walls": walls, "bridges": bridges, "roads": roads, "landmarks": landmarks,
 "fires": [
  {"year": 1421.5, "poly": L(FIRE_1421), "duration_s": 5, "plumes": 4},
  {"year": 1452.4, "poly": L(MEDIEVAL), "duration_s": 6, "plumes": 7},
  {"year": 1652.52, "poly": L(rect(52.3728, 4.8905, 52.3736, 4.8922)), "duration_s": 3, "plumes": 2},
 ],
 "smoke": [],
 "camps": [],
 "open_spaces": [
  {"name": "Vondelpark (≈)", "poly": L([(52.3610, 4.8780), (52.3590, 4.8650), (52.3560, 4.8580), (52.3545, 4.8600), (52.3575, 4.8700),
                                       (52.3595, 4.8790)])},
  {"name": "Dam square", "poly": L(rect(52.3726, 4.8925, 52.3734, 4.8945))},
 ],
 "labels": [
  {"text": T("THE IJ", "IJ"), "at": [52.3850, 4.9050], "kind": "water"},
  {"text": T("AMSTEL", "AMSTEL"), "at": [52.3560, 4.9060], "kind": "water", "to": 1700},
  {"text": T("ZUIDERZEE", "ZUIDERZEE"), "at": [52.3750, 5.0600], "kind": "water", "from": 1840, "to": 1931},
  {"text": T("IJMEER", "IJMEER"), "at": [52.3750, 5.0600], "kind": "water", "from": 1997},
  {"text": T("Dam", "Dam"), "at": [52.3731, 4.8930], "kind": "place", "from": 1270, "to": 1299, "lift_m": 15},
  {"text": T("Oude Kerk", "Oude Kerk"), "at": [52.3744, 4.8980], "from": 1306, "to": 1344, "lift_m": 50},
  {"text": T("Nieuwe Kerk", "Nieuwe Kerk"), "at": [52.3739, 4.8917], "from": 1405, "to": 1420, "lift_m": 50},
  {"text": T("Singel", "Singel"), "at": [52.3715, 4.8893], "kind": "place", "from": 1426, "to": 1451, "lift_m": 10},
  {"text": T("Schreierstoren", "Schreierstoren"), "at": [52.37644, 4.90227], "from": 1488, "to": 1514, "lift_m": 30},
  {"text": T("Montelbaanstoren", "Montelbaanstoren"), "at": [52.3720583, 4.9056833], "from": 1517, "to": 1577, "lift_m": 45},
  {"text": T("Herengracht", "Herengracht"), "at": [52.3765, 4.8882], "kind": "place", "from": 1614, "to": 1619, "lift_m": 10},
  {"text": T("Prinsengracht", "Prinsengracht"), "at": [52.3725, 4.8829], "kind": "place", "from": 1618, "to": 1619, "lift_m": 10},
  {"text": T("Munttoren", "Munttoren"), "at": [52.367001, 4.893151], "from": 1621, "to": 1628, "lift_m": 55},
  {"text": T("Watergraafsmeer", "Watergraafsmeer"), "at": [52.3510, 4.9440], "kind": "place", "from": 1629.5, "to": 1630},
  {"text": T("Westerkerk", "Westerkerk"), "at": [52.37444, 4.88361], "from": 1631, "to": 1647, "lift_m": 110},
  {"text": T("Town Hall", "Belediye Binası"), "at": [52.37317, 4.89136], "from": 1655.5, "to": 1656, "lift_m": 50},
  {"text": T("Oostenburg", "Oostenburg"), "at": [52.3755, 4.9220], "kind": "place", "from": 1661, "to": 1662},
  {"text": T("Royal Palace", "Kraliyet Sarayı"), "at": [52.37317, 4.89136], "from": 1808, "to": 1809, "lift_m": 50},
  {"text": T("HAARLEMMERMEER", "HAARLEMMERMEER"), "at": [52.2900, 4.6900], "kind": "water", "from": 1839, "to": 1851},
  {"text": T("Haarlemmermeer", "Haarlemmermeer"), "at": [52.2900, 4.6900], "kind": "region", "from": 1852, "to": 1852.9},
  {"text": T("Haarlem", "Haarlem"), "at": [52.3810, 4.6370], "kind": "place", "from": 1839, "to": 1847},
  {"text": T("Rijksmuseum", "Rijksmuseum"), "at": [52.360001, 4.885278], "from": 1885.5, "to": 1888, "lift_m": 50},
  {"text": T("Concertgebouw", "Concertgebouw"), "at": [52.3563, 4.8791], "from": 1888.3, "to": 1888.9, "lift_m": 40},
  {"text": T("Centraal Station", "Merkez İstasyonu"), "at": [52.37833, 4.90000], "from": 1889.8, "to": 1899, "lift_m": 45},
  {"text": T("Plan Zuid", "Güney Planı"), "at": [52.3500, 4.8850], "kind": "region", "from": 1920, "to": 1927},
  {"text": T("Olympic Stadium", "Olimpiyat Stadı"), "at": [52.34333, 4.85417], "from": 1928.4, "to": 1939, "lift_m": 40},
  {"text": T("Dam Square", "Dam Meydanı"), "at": [52.3731, 4.8930], "kind": "place", "from": 1940, "to": 1945.4, "lift_m": 20},
  {"text": T("Nieuw-West", "Nieuw-West"), "at": [52.3650, 4.8100], "kind": "region", "from": 1955, "to": 1965},
  {"text": T("Bijlmermeer", "Bijlmermeer"), "at": [52.3150, 4.9650], "kind": "region", "from": 1968, "to": 1976},
  {"text": T("Nieuwmarkt", "Nieuwmarkt"), "at": [52.37250, 4.90056], "kind": "place", "from": 1977, "to": 1996, "lift_m": 25},
  {"text": T("IJburg", "IJburg"), "at": [52.3550, 5.0000], "kind": "region", "from": 2004, "to": 2009},
  {"text": T("CANAL RING", "KANAL KUŞAĞI"), "at": [52.3700, 4.8850], "kind": "region", "from": 2010, "to": 2019},
  {"text": T("Schiphol", "Schiphol"), "at": [52.3000, 4.7650], "kind": "place", "from": 2020},
  {"text": T("NOORD", "NOORD"), "at": [52.3950, 4.9200], "kind": "region", "from": 2020},
  {"text": T("ZUID", "ZUID"), "at": [52.3450, 4.8700], "kind": "region", "from": 2020},
 ],
 "youtube": {
  "title": T("Amsterdam: 1,000 Years in 15 Minutes (3D Timelapse)", "Amsterdam: 15 Dakikada 1.000 Yıl (3D Timelapse)"),
  "description": T(
   "Around the year 1000 farmers settled a wet peat bog where the Amstel meets the IJ. Watch Amsterdam grow from a dam of "
   "about 1270 into a walled medieval town, burn in 1421 and 1452, become the busiest port of the Golden Age and dig its "
   "famous canal ring from 1613. Then the bastions fall, lakes are pumped dry, the North Sea Canal and Centraal Station "
   "arrive, and new quarters, garden cities and islands spread across the polders, with the year and the population on screen.",
   "1000 yılı civarında çiftçiler Amstel'in IJ ile buluştuğu ıslak bir turbalığa yerleşti. Amsterdam'ın 1270 civarındaki bir "
   "bentten surlu bir Orta Çağ kasabasına dönüşmesini, 1421 ve 1452'de yanmasını, Altın Çağ'ın en işlek limanı olmasını ve "
   "1613'ten itibaren ünlü kanal kuşağını kazmasını izleyin. Ardından burçlar yıkılır, göller kurutulur, Kuzey Denizi Kanalı ve "
   "Merkez İstasyonu gelir; yeni mahalleler, bahçe şehirler ve adalar polderlere yayılır. Yıl ve nüfus ekranda."),
  "tags": ["amsterdam history", "history of amsterdam", "amsterdam canals", "canal ring", "3d timelapse", "city evolution",
           "how amsterdam grew", "amsterdam timelapse", "dutch golden age", "grachtengordel", "urban history", "netherlands history"],
  "hashtags": ["#Amsterdam", "#History", "#Timelapse"],
  "playlist": T("Cities of Europe", "Avrupa Şehirleri"),
  "thumb": {"line1": T("Amsterdam", "Amsterdam"), "line2": T("1,000 YEARS", "1.000 YIL"), "line3": T("From a dam to a city of canals", "Bir bentten kanallar şehrine"),
            "extra": "&mood=golden&pitch=30&az=0&cam=52.3700,4.8920,4.5"},
 },
 "sources": [],
}
total = sum(s_["seconds"] for s_ in S)
mins = round(total / 60)
city["intro"] = T(f"1,000 Years in {mins} Minutes", f"{mins} Dakikada 1.000 Yıl")
city["youtube"]["title"] = T(f"Amsterdam: 1,000 Years in {mins} Minutes (3D Timelapse)", f"Amsterdam: {mins} Dakikada 1.000 Yıl (3D Timelapse)")
city["sources"] = json.load(open(os.path.join(HERE, "_sources.json")))
json.dump(city, open(os.path.join(HERE, "city.json"), "w"), ensure_ascii=False, indent=1)
print("segments", len(S), "duration", total, "s =", f"{total // 60}:{total % 60:02d}", "| fill polys", len(FILL),
      "(geo.json present)" if HAVE_GEO else "(no geo.json yet: fills left out)")
