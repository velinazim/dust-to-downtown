"""Builds cities/istanbul/city.json. Every on-screen date/figure is from research.md (sources listed there).
Run: python3 cities/istanbul/_build.py

Land and water come from the real map (elevation + OpenStreetMap). Walls, district outlines, fire and camp areas are
simplified traces between known points (gates, landmarks, shore), marked ≈ in research.md. When geo.json exists, the
sea walls and the wall ends are snapped onto the real shoreline (a strip 25–70 m inland), so they run on land and end
at the water; without geo.json (first preview run) the hand traces are used as they are."""
import json, math, os

T = lambda en, tr: {"en": en, "tr": tr}
HERE = os.path.dirname(os.path.abspath(__file__))
KZ = 110.574
rect = lambda s, w, n, e: [(s, w), (n, w), (n, e), (s, e)]


def L(pts):
    return [[round(a, 5), round(b, 5)] for a, b in pts]


# ------------------------------------------------------------------ shoreline snapping (needs geo.json)
GEO = None
gp = os.path.join(HERE, 'geo.json')
if os.path.exists(gp):
    import base64
    import numpy as np
    _g = json.load(open(gp))
    _lat0, _lon0 = _g['origin']
    _k = 111.32 * math.cos(math.radians(_lat0))
    _layers = []
    for c in ([_g['core']] if 'core' in _g else []) + [_g]:
        sd = np.frombuffer(base64.b64decode(c['sd_b64']), dtype='<i2').reshape(c['nz'], c['nx']).astype(float)
        _layers.append((c, sd))
    GEO = True


def _cell(c, lat, lon):
    x = (lon - _lon0) * _k; z = -(lat - _lat0) * KZ
    return int(round((x - c['x0']) / c['cell_km'])), int(round((z - c['z0']) / c['cell_km']))


def sd_at(lat, lon):
    for c, sd in _layers:
        i, j = _cell(c, lat, lon)
        if 0 <= i < c['nx'] and 0 <= j < c['nz']:
            return sd[j, i]
    return None


def snap(lat, lon, lo=25, hi=70, r_m=700):
    """Move a point to the nearest cell that is land, lo..hi m from the shore (core layer)."""
    if not GEO:
        return (lat, lon)
    c, sd = _layers[0]
    i0, j0 = _cell(c, lat, lon)
    r = int(r_m / 1000 / c['cell_km'])
    best = None
    for j in range(max(0, j0 - r), min(c['nz'], j0 + r + 1)):
        for i in range(max(0, i0 - r), min(c['nx'], i0 + r + 1)):
            if lo <= sd[j, i] <= hi:
                d = (i - i0) ** 2 + (j - j0) ** 2
                if best is None or d < best[0]:
                    best = (d, i, j)
    if best is None:
        return (lat, lon)
    _, i, j = best
    x = c['x0'] + i * c['cell_km']; z = c['z0'] + j * c['cell_km']
    return (_lat0 - z / KZ, _lon0 + x / _k)


def shore_path(pts, step_m=120):
    """Densify a hand trace and snap every point to the shore strip (for sea walls)."""
    out = []
    for (a1, b1), (a2, b2) in zip(pts, pts[1:]):
        dist = math.hypot((a2 - a1) * KZ, (b2 - b1) * 111.32 * math.cos(math.radians(a1))) * 1000
        n = max(1, int(dist / step_m))
        for t in range(n):
            u = t / n
            out.append(snap(a1 + (a2 - a1) * u, b1 + (b2 - b1) * u, 30, 60, 500))
    out.append(snap(*pts[-1], 30, 60, 500))
    clean = [out[0]]
    for p in out[1:]:
        if abs(p[0] - clean[-1][0]) + abs(p[1] - clean[-1][1]) > 2e-5:
            clean.append(p)
    return clean


def land_wall(pts):
    """Snap only the two ends of a land wall to the shore."""
    return [snap(*pts[0])] + list(pts[1:-1]) + [snap(*pts[-1])]


# ------------------------------------------------------------------ walls (≈ traces, see research.md)
ARCHAIC = [(41.0160, 28.9768), (41.0122, 28.9766), (41.0088, 28.9774), (41.0052, 28.9792)]
SEVERAN = [(41.0172, 28.9712), (41.0132, 28.9702), (41.0103, 28.9705), (41.0068, 28.9715), (41.0042, 28.9730),
           (41.0028, 28.9748)]
CONSTANTINIAN = [(41.0228, 28.9598), (41.0205, 28.9545), (41.0170, 28.9505), (41.0120, 28.9472), (41.0070, 28.9456),
                 (41.0012, 28.9450)]
# Theodosian land walls, Marmara (Marble Tower) -> Golden Horn (Blachernae); gates ≈ from Yedikule (WP coords) and
# the gate sequence Belgradkapı, Silivrikapı, Mevlanakapı, Topkapı, Edirnekapı, Tekfur Sarayı, Ayvansaray
THEODOSIAN = [(40.9912, 28.9212), (40.99335, 28.92309), (40.9990, 28.9218), (41.0058, 28.9205), (41.0118, 28.9194),
              (41.0192, 28.9203), (41.0245, 28.9262), (41.0297, 28.9343), (41.0336, 28.9404), (41.0378, 28.9418),
              (41.0412, 28.9433)]
SEA_GH = [(41.0412, 28.9433), (41.0352, 28.9468), (41.0303, 28.9500), (41.0262, 28.9550), (41.0226, 28.9610),
          (41.0178, 28.9705), (41.0170, 28.9790), (41.0162, 28.9858)]
SEA_MARMARA = [(41.0162, 28.9858), (41.0120, 28.9872), (41.0040, 28.9822), (41.0026, 28.9700), (41.0020, 28.9640)]
# Yenikapı: the modern shore is a 2010s landfill, so the wall keeps a hand trace along the old shore (≈) here
SEA_YENIKAPI = [(41.0020, 28.9640), (41.0030, 28.9580), (41.0032, 28.9520), (41.0022, 28.9470), (41.0005, 28.9420), (40.9992, 28.9340)]
SEA_MARMARA_W = [(40.9992, 28.9340), (40.9945, 28.9290), (40.9912, 28.9212)]
YENIKAPI_FILL = [(41.0028, 28.9425), (41.0040, 28.9650), (40.9950, 28.9650), (40.9950, 28.9425)]
GALATA_WALL = [(41.0228, 28.9670), (41.0248, 28.9705), (41.02566, 28.97416), (41.0262, 28.9775), (41.0252, 28.9805),
               (41.0240, 28.9815)]

walls = [
 {"name": "Walls of Byzantion (≈ course)", "path": L(land_wall(ARCHAIC)), "built": -640, "removed": 196.3, "height": "low",
  "towers_m": 110, "draw_s": 3.0},
 {"name": "Severan wall (≈ course)", "path": L(land_wall(SEVERAN)), "built": 203, "removed": 400, "height": "mid", "towers_m": 120,
  "draw_s": 3.0},
 {"name": "Constantinian wall (≈ course)", "path": L(land_wall(CONSTANTINIAN)[:-1] + [(41.0020, 28.9452)]), "built": 324.5, "removed": 900, "height": "mid",
  "towers_m": 130, "draw_s": 4.0},
 {"name": "Theodosian land walls", "path": L(land_wall(THEODOSIAN)), "built": 412.8, "height": "high", "towers_m": 60,
  "double": True, "double_side": 1, "moat": True, "draw_s": 6.0},
 {"name": "Sea walls, Golden Horn (≈ shore)", "path": L(shore_path(SEA_GH) if GEO else SEA_GH), "built": 439, "height": "low",
  "towers_m": 55, "draw_s": 5.0},
 {"name": "Sea walls, Marmara (≈ shore)", "path": L((shore_path(SEA_MARMARA)[:-1] + SEA_YENIKAPI + shore_path(SEA_MARMARA_W)[1:]) if GEO else SEA_MARMARA + SEA_YENIKAPI[1:] + SEA_MARMARA_W[1:]), "built": 439, "height": "low",
  "towers_m": 50, "draw_s": 5.0},
 {"name": "Genoese walls of Galata (≈ course)", "path": L(land_wall(GALATA_WALL)), "built": 1300, "removed": 1870, "height": "mid",
  "towers_m": 80, "draw_s": 3.0},
]

# ------------------------------------------------------------------ built-up areas (≈ traces)
BYZANTION = [(41.0168, 28.9775), (41.0130, 28.9768), (41.0090, 28.9778), (41.0055, 28.9798), (41.0060, 28.9840),
             (41.0100, 28.9885), (41.0140, 28.9890), (41.0172, 28.9870)]
CHALCEDON = [(40.9945, 29.0215), (40.9945, 29.0330), (40.9870, 29.0330), (40.9860, 29.0240)]
SEVERAN_CITY = [(41.0175, 28.9705), (41.0130, 28.9695), (41.0100, 28.9698), (41.0062, 28.9710), (41.0030, 28.9740),
                (41.0030, 28.9800), (41.0060, 28.9850), (41.0100, 28.9890), (41.0150, 28.9895), (41.0175, 28.9860)]
CONST_CITY = [(41.0232, 28.9595), (41.0205, 28.9540), (41.0170, 28.9500), (41.0120, 28.9466), (41.0070, 28.9450),
              (41.0000, 28.9445), (41.0000, 28.9600), (41.0020, 28.9700), (41.0062, 28.9710), (41.0100, 28.9698),
              (41.0175, 28.9705), (41.0200, 28.9660)]
THEO_CITY = [(40.9910, 28.9220), (40.9990, 28.9225), (41.0058, 28.9212), (41.0118, 28.9200), (41.0192, 28.9210),
             (41.0245, 28.9268), (41.0297, 28.9350), (41.0336, 28.9410), (41.0412, 28.9440), (41.0352, 28.9475),
             (41.0262, 28.9555), (41.0232, 28.9595), (41.0170, 28.9500), (41.0120, 28.9466), (41.0000, 28.9445),
             (40.9960, 28.9330)]
INSIDE_WALLS = THEO_CITY[:12] + [(41.0178, 28.9705), (41.0170, 28.9790), (41.0162, 28.9870), (41.0120, 28.9885),
                                 (41.0035, 28.9825), (41.0010, 28.9600), (40.9960, 28.9330)]
GALATA = [(41.0225, 28.9668), (41.0248, 28.9702), (41.0258, 28.9742), (41.0262, 28.9778), (41.0250, 28.9810),
          (41.0230, 28.9800), (41.0218, 28.9740)]
EYUP = [(41.0525, 28.9300), (41.0525, 28.9390), (41.0450, 28.9390), (41.0450, 28.9300)]
USKUDAR = [(41.0300, 29.0080), (41.0300, 29.0250), (41.0180, 29.0280), (41.0150, 29.0150), (41.0200, 29.0080)]
PERA = [(41.0262, 28.9730), (41.0300, 28.9700), (41.0370, 28.9760), (41.0370, 28.9880), (41.0300, 28.9900),
        (41.0262, 28.9810)]
BOSPHORUS_EU = [(41.0300, 28.9900), (41.0450, 29.0000), (41.0500, 29.0300), (41.0700, 29.0420), (41.0880, 29.0560),
                (41.0880, 29.0500), (41.0700, 29.0350), (41.0500, 29.0200), (41.0420, 28.9950)]
BOSPHORUS_AS = [(41.0300, 29.0250), (41.0450, 29.0420), (41.0700, 29.0620), (41.0850, 29.0700), (41.0850, 29.0780),
                (41.0700, 29.0700), (41.0450, 29.0500), (41.0300, 29.0330)]
KADIKOY_19 = [(41.0000, 29.0150), (41.0050, 29.0400), (40.9900, 29.0550), (40.9750, 29.0450), (40.9800, 29.0250)]
SISLI = [(41.0370, 28.9760), (41.0700, 28.9800), (41.0750, 29.0050), (41.0450, 29.0000), (41.0370, 28.9880)]
WEST_SHORE = [(40.9950, 28.9150), (40.9850, 28.8800), (40.9750, 28.8300), (40.9850, 28.8100), (41.0050, 28.8500),
              (41.0150, 28.9000), (41.0100, 28.9180)]
ASIA_SHORE = [(40.9900, 29.0550), (40.9750, 29.1000), (40.9500, 29.1400), (40.9150, 29.1800), (40.8900, 29.2400),
              (40.8700, 29.3000), (40.8950, 29.3100), (40.9300, 29.2400), (40.9700, 29.1700), (41.0050, 29.1100),
              (41.0200, 29.0500), (41.0050, 29.0400)]
LEVENT = [(41.0750, 29.0000), (41.1150, 29.0150), (41.1150, 29.0300), (41.0750, 29.0200)]
ATASEHIR = [(40.9950, 29.1100), (40.9950, 29.1300), (40.9800, 29.1300), (40.9800, 29.1100)]
OLD_CORE = INSIDE_WALLS
METRO = [(41.2000, 28.6000), (41.1700, 28.8000), (41.2000, 28.9500), (41.1800, 29.0400), (41.1400, 29.1000),
         (41.1500, 29.2000), (41.0800, 29.3000), (40.9200, 29.3800), (40.8600, 29.3500), (40.9000, 29.2000),
         (40.9600, 29.0900), (40.9800, 28.8500), (40.9700, 28.6500), (41.0100, 28.5800)]


def yenikapi_fill():
    """Yenikapı landfill (≈ outline, 2010s): water until 2013, then land; clipped to the modern land of geo.json."""
    if not GEO:
        return []
    from shapely.geometry import Polygon, box
    from shapely.ops import unary_union
    c, sd = _layers[0]
    old_shore = [(a - 0.0002, b) for a, b in SEA_YENIKAPI]
    zone = Polygon([(b, a) for a, b in old_shore + [(40.9930, 28.9330), (40.9950, 28.9640)][::-1]]).buffer(0)
    mnx, mny, mxx, mxy = zone.bounds
    i0, j1 = _cell(c, mny, mnx); i1, j0 = _cell(c, mxy, mxx)
    boxes = []
    for j in range(max(0, j0 - 1), min(c['nz'], j1 + 2)):
        for i in range(max(0, i0 - 1), min(c['nx'], i1 + 2)):
            if sd[j, i] > 0:
                x = c['x0'] + i * c['cell_km']; z = c['z0'] + j * c['cell_km']; h = c['cell_km'] / 2
                boxes.append(box(_lon0 + (x - h) / _k, _lat0 - (z + h) / KZ, _lon0 + (x + h) / _k, _lat0 - (z - h) / KZ))
    if not boxes:
        return []
    g = unary_union(boxes).intersection(zone).buffer(0.0002).buffer(-0.0002).simplify(0.00005)
    parts = [g] if g.geom_type == 'Polygon' else list(getattr(g, 'geoms', []))
    out = []
    for n, p in enumerate(parts):
        if p.geom_type != 'Polygon' or p.area < 2e-7:
            continue
        ring = [(y, x) for x, y in p.exterior.coords][:-1]
        out.append({"name": f"Yenikapı landfill (≈, 2010s) #{n + 1}", "fill": True, "from": -700, "to": 2013, "poly": L(ring)})
    return out


def D(name, style, poly, frm, to, dens, grain, grow, **kw):
    d = {"name": name, "style": style, "poly": L(poly), "from": frm, "to": to, "density": dens, "grain_m": grain, "grow_from": list(grow)}
    d.update(kw); return d


MODERN_HOLES = [L(INSIDE_WALLS), L(GALATA), L(PERA), L(USKUDAR), L(KADIKOY_19), L(SISLI), L(LEVENT), L(ATASEHIR)]
districts = [
 D("Byzantion (≈)", "ancient", BYZANTION, -660, -560, 0.6, 50, (41.0115, 28.9830)),
 D("Chalcedon (≈)", "ancient", CHALCEDON, -680, -580, 0.45, 60, (40.9910, 29.0270)),
 D("Byzantion rebuilt by Severus (≈)", "roman", SEVERAN_CITY, 203, 240, 0.65, 55, (41.0100, 28.9800)),
 D("Constantine's city (≈)", "roman", CONST_CITY, 326, 380, 0.65, 55, (41.0110, 28.9650)),
 D("Theodosian city (≈)", "roman", THEO_CITY, 413, 520, 0.45, 60, (41.0110, 28.9450), fade=[541, 560, 0.55]),
 D("Late Byzantine decline (≈)", "medieval", THEO_CITY + [], 1205, 1215, 0.2, 70, (41.0250, 28.9500), fade=[1205, 1262, 0.35]),
 D("Genoese Galata (≈)", "medieval", GALATA, 1267, 1360, 0.75, 45, (41.0245, 28.9745)),
 D("Ottoman Istanbul (≈)", "ottoman", INSIDE_WALLS, 1454, 1560, 0.7, 52, (41.0110, 28.9700)),
 D("Eyüp (≈)", "ottoman", EYUP, 1458, 1520, 0.55, 60, (41.0480, 28.9340)),
 D("Üsküdar (≈)", "ottoman", USKUDAR, 1460, 1580, 0.6, 55, (41.0250, 29.0150)),
 D("Pera (≈)", "ottoman", PERA, 1500, 1620, 0.6, 52, (41.0300, 28.9770)),
 D("Rebuilt after the 1660 fire (≈)", "ottoman", rect(41.0090, 28.9580, 41.0225, 28.9760), 1661, 1690, 0.75, 52, (41.0160, 28.9680)),
 D("Bosphorus villages, European shore (≈)", "ottoman", BOSPHORUS_EU, 1600, 1850, 0.4, 60, (41.0420, 29.0050)),
 D("Bosphorus villages, Asian shore (≈)", "ottoman", BOSPHORUS_AS, 1600, 1850, 0.4, 60, (41.0400, 29.0350)),
 D("Pera rebuilt after 1870 (≈)", "victorian", PERA, 1871, 1900, 0.8, 50, (41.0330, 28.9780)),
 D("Kadıköy and Moda (≈)", "victorian", KADIKOY_19, 1860, 1920, 0.55, 60, (40.9900, 29.0300)),
 D("Şişli and Nişantaşı (≈)", "georgian", SISLI, 1880, 1950, 0.6, 60, (41.0480, 28.9870)),
 D("Western shore suburbs (≈)", "modern", WEST_SHORE, 1950, 1975, 0.5, 80, (41.0000, 28.8800)),
 D("Asian shore suburbs (≈)", "modern", ASIA_SHORE, 1955, 1990, 0.45, 85, (40.9800, 29.0700)),
 D("Greater Istanbul (≈)", "suburb", METRO, 1960, 2015, 0.5, 190, (41.0300, 28.9800), holes=MODERN_HOLES + [L(WEST_SHORE), L(ASIA_SHORE)]),
 D("Levent and Maslak (≈)", "highrise", LEVENT, 1990, 2020, 0.5, 110, (41.0800, 29.0100)),
 D("Ataşehir (≈)", "highrise", ATASEHIR, 2005, 2022, 0.45, 110, (40.9880, 29.1200)),
]

# ------------------------------------------------------------------ landmarks (Wikipedia / Kültür Envanteri coordinates)
landmarks = [
 {"type": "temple", "name": T("Acropolis of Byzantion (≈)", "Byzantion Akropolü"), "at": [41.0128, 28.9840], "built": -620,
  "removed": 1459, "rise_s": 5, "size_m": [40, 22, 14], "rot_deg": 0, "colors": {"wall": "#d9d0bb", "roof": "#9c6b4e"}},
 {"type": "circus", "name": T("Hippodrome", "Hipodrom"), "at": [41.00639, 28.97583], "built": 203, "removed": 1500, "rise_s": 8,
  "size_m": [450, 130, 14], "rot_deg": -58, "colors": {"wall": "#cfc4ac"}},
 {"type": "column", "name": T("Column of Constantine", "Çemberlitaş"), "at": [41.00861, 28.97111], "built": 328, "rise_s": 4,
  "size_m": [6, 6, 50], "colors": {"wall": "#a58a6a"}},
 {"type": "church", "name": T("Great Church (first Hagia Sophia)", "Büyük Kilise (ilk Ayasofya)"), "at": [41.00833, 28.98000],
  "built": 355, "removed": 532.04, "rise_s": 5, "size_m": [80, 45, 30], "rot_deg": 0, "colors": {"wall": "#d6cdb8", "roof": "#7d6a58"}},
 {"type": "domechurch", "name": T("Hagia Sophia", "Ayasofya"), "at": [41.00833, 28.98000], "built": 532.15, "rise_s": 10,
  "size_m": [82, 73, 55], "rot_deg": 0, "scale": 1.4, "colors": {"wall": "#c9a98a", "roof": "#8c939a"},
  "additions": [{"type": "minarets", "year": 1577, "count": 4, "spread_m": 62, "height_m": 60}]},
 {"type": "box", "name": T("Aqueduct of Valens", "Bozdoğan Kemeri"), "at": [41.015944, 28.95556], "built": 368, "rise_s": 5,
  "size_m": [921, 10, 29], "rot_deg": -12, "colors": {"wall": "#b39a7a"}},
 {"type": "castle", "name": T("Golden Gate", "Altınkapı"), "at": [40.99335, 28.92309], "built": 410, "rise_s": 4,
  "size_m": [45, 25, 22], "colors": {"wall": "#d8cdb5", "roof": "#7c7468"}},
 {"type": "fort", "name": T("Yedikule Fortress", "Yedikule Hisarı"), "at": [40.99335, 28.92309], "built": 1458, "rise_s": 4,
  "size_m": [170, 130, 25], "colors": {"wall": "#cfc4ac"}},
 {"type": "tower", "name": T("Galata Tower", "Galata Kulesi"), "at": [41.0256556, 28.9741556], "built": 1348, "rise_s": 5,
  "size_m": [16, 16, 63], "colors": {"wall": "#b7aa95", "roof": "#5f666f"}},
 {"type": "fort", "name": T("Anadoluhisarı", "Anadoluhisarı"), "at": [41.081944, 29.066944], "built": 1393, "rise_s": 5,
  "size_m": [80, 60, 22], "colors": {"wall": "#b8aa92"}, "scale": 1.5},
 {"type": "fort", "name": T("Rumelihisarı", "Rumelihisarı"), "at": [41.084722, 29.056111], "built": 1452.29, "rise_s": 6,
  "size_m": [250, 130, 28], "rot_deg": 90, "colors": {"wall": "#b8aa92"}, "scale": 1.3},
 {"type": "palace", "name": T("Topkapı Palace", "Topkapı Sarayı"), "at": [41.013, 28.984], "built": 1459, "rise_s": 10,
  "size_m": [300, 200, 16], "rot_deg": -30, "colors": {"wall": "#ece4d2", "roof": "#8a8f95"}},
 {"type": "box", "name": T("Grand Bazaar", "Kapalıçarşı"), "at": [41.0105806, 28.9679333], "built": 1456, "rise_s": 6,
  "size_m": [200, 150, 12], "rot_deg": -10, "colors": {"wall": "#d2c5aa", "roof": "#8a8f95"}},
 {"type": "mosque", "name": T("Eyüp Sultan Mosque", "Eyüp Sultan Camii"), "at": [41.0479472, 28.9337861], "built": 1458, "rise_s": 5,
  "size_m": [40, 40, 16], "colors": {"wall": "#ece6d8", "minarets": 2}},
 {"type": "mosque", "name": T("Fatih Mosque", "Fatih Camii"), "at": [41.01972, 28.94972], "built": 1463, "removed": 1766.39, "rise_s": 8,
  "size_m": [60, 60, 22], "colors": {"wall": "#ece6d8", "minarets": 2}, "scale": 1.3},
 {"type": "mosque", "name": T("Fatih Mosque (rebuilt)", "Fatih Camii (yeniden)"), "at": [41.01972, 28.94972], "built": 1767, "rise_s": 8,
  "size_m": [60, 60, 22], "colors": {"wall": "#ece6d8", "minarets": 2}, "scale": 1.3},
 {"type": "mosque", "name": T("Süleymaniye Mosque", "Süleymaniye Camii"), "at": [41.01611, 28.96389], "built": 1550, "rise_s": 10,
  "size_m": [70, 60, 26], "colors": {"wall": "#ece6d8", "minarets": 4}, "scale": 1.4},
 {"type": "mosque", "name": T("Sultan Ahmed Mosque", "Sultanahmet Camii"), "at": [41.0053851, 28.9768247], "built": 1609, "rise_s": 10,
  "size_m": [73, 65, 24], "colors": {"wall": "#ece6d8", "minarets": 6}, "scale": 1.4},
 {"type": "palace", "name": T("Dolmabahçe Palace", "Dolmabahçe Sarayı"), "at": [41.0390472, 29.0005035], "built": 1843, "rise_s": 12,
  "size_m": [280, 70, 22], "rot_deg": -50, "colors": {"wall": "#efe9dc", "roof": "#7d8790"}},
 {"type": "station", "name": T("Sirkeci Station", "Sirkeci Garı"), "at": [41.015, 28.977222], "built": 1888.1, "rise_s": 6,
  "size_m": [110, 30, 18], "rot_deg": 0, "colors": {"wall": "#d7c3a5", "roof": "#59656a"}},
]

def span(c, bearing_deg, fallback):
    """Bridge ends: walk from the published centre along the bridge direction to the first land >= 30 m from shore."""
    if not GEO:
        return fallback
    k = 111.32 * math.cos(math.radians(c[0]))
    ends = []
    for sgn in (-1, 1):
        dx, dz = math.sin(math.radians(bearing_deg)) * sgn, math.cos(math.radians(bearing_deg)) * sgn
        p = None
        for st in range(1, 400):
            d = st * 0.01
            lat, lon = c[0] + dz * d / KZ, c[1] + dx * d / k
            v = sd_at(lat, lon)
            if v is not None and v >= 30:
                p = [round(lat, 5), round(lon, 5)]; break
        ends.append(p)
    return ends if all(ends) else fallback


bridges = [
 {"name": "Hayratiye Bridge (pontoon, ≈ ends)", "path": span((41.024194, 28.965306), 40, [[41.0218, 28.9625], [41.0262, 28.9682]]), "built": 1836.67, "removed": 1936,
  "style": "wood", "width_m": 14},
 {"name": "Atatürk Bridge (≈ ends)", "path": span((41.024194, 28.965306), 40, [[41.0218, 28.9625], [41.0262, 28.9682]]), "built": 1940, "style": "iron", "width_m": 25},
 {"name": "Galata Bridge, wooden (≈ ends)", "path": span((41.02000, 28.97306), 12, [[41.0172, 28.9724], [41.0228, 28.9742]]), "built": 1845, "removed": 1875,
  "style": "wood", "width_m": 14},
 {"name": "Galata Bridge, 1875 and 1912 (≈ ends)", "path": span((41.02000, 28.97306), 12, [[41.0172, 28.9724], [41.0228, 28.9742]]), "built": 1875, "removed": 1992,
  "style": "iron", "width_m": 25},
 {"name": "Galata Bridge, 1994 (≈ ends)", "path": span((41.02000, 28.97306), 12, [[41.0172, 28.9724], [41.0228, 28.9742]]), "built": 1994, "style": "modern", "width_m": 42},
 {"name": "Bosphorus Bridge (≈ ends from centre)", "path": span((41.04528, 29.03444), 112, [[41.0478, 29.0262], [41.0428, 29.0428]]), "built": 1973.6, "style": "modern",
  "width_m": 40},
 {"name": "Fatih Sultan Mehmet Bridge (≈ ends from centre)", "path": span((41.0913, 29.062), 97, [[41.0920, 29.0540], [41.0905, 29.0700]]), "built": 1988.4,
  "style": "modern", "width_m": 40},
 {"name": "Yavuz Sultan Selim Bridge (≈ ends from centre)", "path": span((41.2031, 29.1117), 95, [[41.2040, 29.0980], [41.2022, 29.1255]]), "built": 2016.05,
  "style": "modern", "width_m": 58},
]

roads = [
 {"name": "Mese, Severan town (≈)", "path": L([(41.0080, 28.9782), (41.00861, 28.97111)]), "from": 203, "kind": "roman", "width_m": 22},
 {"name": "Mese to the Golden Gate (≈)", "path": L([(41.00861, 28.97111), (41.0098, 28.9640), (41.0085, 28.9550), (41.0060, 28.9460),
                                 (41.0010, 28.9330), (40.99400, 28.9240)]), "from": 330, "kind": "roman", "width_m": 22},
 {"name": "Mese, northern branch (≈)", "path": L([(41.0085, 28.9550), (41.0140, 28.9480), (41.0200, 28.9420), (41.0260, 28.9370),
                                                  (41.0297, 28.9343)]), "from": 413, "kind": "roman", "width_m": 18},
 {"name": "Railway along the Marmara (≈)", "path": L([(41.0150, 28.9772), (41.0160, 28.9840), (41.0110, 28.9862), (41.0042, 28.9815),
  (41.0030, 28.9700), (41.0040, 28.9550), (40.9995, 28.9400), (40.9950, 28.9300), (40.9940, 28.9150), (40.9850, 28.8800),
  (40.9780, 28.8500)]), "from": 1872, "kind": "rail", "width_m": 18},
]

# ------------------------------------------------------------------ timeline
def seg(frm, to, sec, era, city, title=None, sub=None, pop=None, cam=None, chapter=None):
    d = {"from": frm, "to": to, "seconds": sec, "era": era, "city_name": city}
    if title: d["title"] = title; d["sub"] = sub
    if pop is not None: d["population"] = pop
    if cam: d["camera"] = {"center": [cam[0], cam[1]], "dist_km": cam[2]}
    if chapter: d["chapter"] = chapter
    return d


GR = T("Greek", "Yunan"); RO = T("Roman", "Roma"); BY = T("Byzantine", "Bizans"); LAT = T("Latin Empire", "Latin İmparatorluğu")
OT = T("Ottoman", "Osmanlı"); LOT = T("Late Ottoman", "Geç Osmanlı"); REP = T("Republic of Türkiye", "Türkiye Cumhuriyeti")
TODAY = T("Today", "Bugün")
BYZ = T("Byzantion", "Byzantion"); CON = T("Constantinople", "Konstantinopolis"); IST = T("Istanbul", "İstanbul")

# sourced anchors (year, people) — research.md; log-interpolated between them. None = no figure ("—").
ANCH = [(193, 15000), (324, 20000), (368, 150000), (393, 200000), (540, 500000), (545, 350000)]
ANCH2 = [(1150, 400000), (1203, 400000), (1261, 35000), (1282, 70000), (1348, 80000), (1453, 50000), (1481, 80000),
         (1535, 350000), (1600, 400000), (1690, 400000), (1800, 500000), (1860, 715000), (1890, 874000), (1900, 942900),
         (1914, 1125000), (1927, 794444), (1935, 883599), (1940, 991237), (1945, 1078399), (1950, 1166477), (1955, 1533822),
         (1960, 1882092), (1965, 2293823), (1970, 3019032), (1975, 3904588), (1980, 4741890), (1985, 5842985), (1990, 7309190),
         (1997, 9198809), (2000, 10018735), (2007, 12573836), (2010, 13255685), (2013, 14160467), (2016, 14804116),
         (2018, 15067724), (2020, 15462452), (2022, 15907951), (2024, 15701602), (2025, 15754053), (2026, 15754053)]


def P(y):
    for anch in (ANCH, ANCH2):
        for (y0, p0), (y1, p1) in zip(anch, anch[1:]):
            if y0 <= y <= y1:
                u = (y - y0) / (y1 - y0); v = math.exp(math.log(p0) + (math.log(p1) - math.log(p0)) * u)
                if y1 >= 1927 and y0 >= 1927 and u in (0, 1):
                    return int(v)
                return int(round(v, -3 if v < 1000000 else -4))
    raise ValueError(y)


PI = lambda a, b: [P(a), P(b)]
S = [
 seg(-667, -514, 18, GR, BYZ, T("Byzantion Is Founded", "Byzantion Kuruluyor"),
     T("7th century BC: Greeks from Megara settle the point between the Golden Horn and the sea",
       "MÖ 7. yüzyıl: Megaralı Yunanlar, Haliç ile deniz arasındaki burna yerleşir"),
     cam=(41.0105, 28.9830, 3.2), chapter=T("Greek Byzantion", "Yunan Byzantion")),
 seg(-513, -480, 15, GR, BYZ, T("Persian Rule", "Pers Egemenliği"),
     T("513 BC: Darius I of Persia takes the city during his campaign against the Scythians",
       "MÖ 513: Pers kralı I. Darius, İskitlere karşı seferinde şehri alır"),
     cam=(41.0060, 29.0050, 6.0)),
 seg(-479, -341, 15, GR, BYZ, T("Sparta Drives Out Persia", "Sparta Persleri Kovuyor"),
     T("479 BC: after the Battle of Plataea, the Spartans take Byzantion from the Persians",
       "MÖ 479: Plataea Savaşı'ndan sonra Spartalılar Byzantion'u Perslerden alır"),
     cam=(41.0100, 28.9820, 3.4)),
 seg(-340, -339, 15, GR, BYZ, T("Philip of Macedon's Siege", "Makedonyalı Filip Kuşatıyor"),
     T("340 BC: Philip II besieges Byzantion; a sudden bright light foils his night attack",
       "MÖ 340: II. Filip Byzantion'u kuşatır; ani bir ışık onun gece saldırısını boşa çıkarır"),
     cam=(41.0100, 28.9780, 3.6)),
 seg(-338, 195, 9, GR, BYZ, cam=(41.0100, 28.9800, 3.4)),
 seg(196, 202, 15, RO, BYZ, T("Razed by Severus", "Severus Yerle Bir Ediyor"),
     T("AD 196: Byzantion backs the wrong emperor; Septimius Severus takes it and razes it",
       "MS 196: Byzantion yanlış imparatoru destekler; Septimius Severus şehri alıp yıkar"),
     pop=P(196), cam=(41.0100, 28.9800, 3.0), chapter=T("Roman City", "Roma Şehri")),
 seg(203, 323, 16, RO, BYZ, T("A Hippodrome and a Main Street", "Bir Hipodrom ve Ana Cadde"),
     T("203: Severus rebuilds the city with a hippodrome and the Mese, its main street",
       "203: Severus şehri bir hipodrom ve ana cadde Mese ile yeniden kurar"),
     pop=PI(203, 323), cam=(41.0085, 28.9760, 3.0)),
 seg(324, 329, 17, RO, T("Nova Roma", "Nova Roma"), T("Constantine's New Rome", "Konstantin'in Yeni Roma'sı"),
     T("324: Constantine chooses Byzantion as his new capital and begins a wall far to the west",
       "324: Konstantin Byzantion'u yeni başkenti seçer ve çok batıda bir sur başlatır"),
     pop=PI(324, 329), cam=(41.0110, 28.9640, 4.4), chapter=T("Constantinople", "Konstantinopolis")),
 seg(330, 359, 16, RO, CON, T("Constantinople", "Konstantinopolis"),
     T("11 May 330: the new capital is dedicated; a column about 50 m tall marks Constantine's forum",
       "11 Mayıs 330: yeni başkent açılır; Konstantin forumunu 50 m kadar yüksek bir sütun süsler"),
     pop=PI(330, 359), cam=(41.0095, 28.9720, 3.0)),
 seg(360, 367, 15, RO, CON, T("The First Hagia Sophia", "İlk Ayasofya"),
     T("15 February 360: the Great Church, the first Hagia Sophia, is consecrated",
       "15 Şubat 360: Büyük Kilise, yani ilk Ayasofya, takdis edilir"),
     pop=PI(360, 367), cam=(41.0085, 28.9790, 2.4)),
 seg(368, 412, 16, RO, CON, T("The Aqueduct of Valens", "Bozdoğan Kemeri"),
     T("368: an aqueduct up to 29 m high carries water across the valley to the growing capital",
       "368: 29 m'ye varan bir su kemeri, büyüyen başkente vadinin üstünden su taşır"),
     pop=PI(368, 412), cam=(41.0140, 28.9580, 3.0)),
 seg(413, 446, 18, BY, CON, T("The Theodosian Walls", "Theodosius Surları"),
     T("413: new land walls 5.7 km long close the peninsula from the Marmara to the Golden Horn",
       "413: 5,7 km uzunluğunda yeni kara surları yarımadayı Marmara'dan Haliç'e kadar kapatır"),
     pop=PI(413, 446), cam=(41.0150, 28.9350, 7.0), chapter=T("The Great Walls", "Büyük Surlar")),
 seg(447, 531, 16, BY, CON, T("Rebuilt in 60 Days", "60 Günde Yeniden"),
     T("447: earthquakes bring down the walls; 16,000 workers rebuild them in 60 days",
       "447: depremler surları yıkar; 16.000 işçi onları 60 günde yeniden yapar"),
     pop=PI(447, 531), cam=(41.0120, 28.9300, 5.0)),
 seg(532, 536, 16, BY, CON, T("The Nika Riots", "Nika Ayaklanması"),
     T("January 532: riots start in the Hippodrome; Hagia Sophia burns and about 30,000 people die",
       "Ocak 532: Hipodrom'da ayaklanma çıkar; Ayasofya yanar, yaklaşık 30.000 kişi ölür"),
     pop=PI(532, 536), cam=(41.0075, 28.9775, 2.4), chapter=T("Justinian", "Justinianus")),
 seg(537, 540, 17, BY, CON, T("A New Hagia Sophia", "Yeni Ayasofya"),
     T("27 December 537: Justinian inaugurates the new Hagia Sophia, its dome 55 m high",
       "27 Aralık 537: Justinianus, kubbesi 55 m yükseklikteki yeni Ayasofya'yı açar"),
     pop=PI(537, 540), cam=(41.0085, 28.9800, 2.0)),
 seg(541, 625, 16, BY, CON, T("The Plague of Justinian", "Justinianus Vebası"),
     T("541–542: plague kills between a fifth and two fifths of the people",
       "541–542: veba, halkın beşte biri ile beşte ikisi arasında bir kısmını öldürür"),
     pop=[500000, 350000], cam=(41.0110, 28.9550, 5.0)),
 seg(626, 673, 15, BY, CON, T("Avars and Persians", "Avarlar ve Persler"),
     T("626: Avars, Slavs and Persians besiege Constantinople; the walls hold",
       "626: Avarlar, Slavlar ve Persler Konstantinopolis'i kuşatır; surlar dayanır"),
     cam=(41.0150, 28.9250, 7.0)),
 seg(674, 716, 15, BY, CON, T("The Arab Sieges", "Arap Kuşatmaları"),
     T("674–678: an Umayyad siege fails; the walls and Greek fire help save the city",
       "674–678: Emevi kuşatması başarısız olur; surlar ve Grejuva ateşi şehri kurtarır"),
     cam=(41.0100, 28.9400, 9.0)),
 seg(717, 739, 14, BY, CON, T("The Second Arab Siege", "İkinci Arap Kuşatması"),
     T("717–718: a second Umayyad army and fleet besiege the city, and fail again",
       "717–718: ikinci bir Emevi ordusu ve donanması şehri kuşatır ve yine başarısız olur"),
     cam=(41.0150, 28.9300, 8.0)),
 seg(740, 1142, 9, BY, CON, cam=(41.0150, 28.9500, 6.0)),
 seg(1143, 1203, 16, BY, CON, T("A Medieval Metropolis", "Bir Orta Çağ Metropolü"),
     T("Mid-12th century: about 400,000 people live here, among them 60,000–80,000 foreigners",
       "12. yüzyıl ortası: burada 60.000–80.000'i yabancı olmak üzere yaklaşık 400.000 kişi yaşar"),
     pop=[400000, 400000], cam=(41.0170, 28.9550, 5.0), chapter=T("Crusaders and Genoese", "Haçlılar ve Cenevizliler")),
 seg(1204, 1260, 17, LAT, CON, T("The Fourth Crusade", "Dördüncü Haçlı Seferi"),
     T("12 April 1204: crusaders storm the city from the Golden Horn and sack it",
       "12 Nisan 1204: Haçlılar şehre Haliç'ten saldırır ve onu yağmalar"),
     pop=PI(1204, 1260), cam=(41.0230, 28.9550, 4.4)),
 seg(1261, 1266, 15, BY, CON, T("The Byzantines Return", "Bizanslılar Geri Dönüyor"),
     T("25 July 1261: Byzantine forces retake the city; only about 35,000 people remain",
       "25 Temmuz 1261: Bizans kuvvetleri şehri geri alır; yalnızca 35.000 kadar kişi kalmıştır"),
     pop=PI(1261, 1266), cam=(41.0150, 28.9500, 5.0)),
 seg(1267, 1347, 15, BY, CON, T("Genoese Galata", "Ceneviz Galatası"),
     T("1267: Genoa founds a colony in Galata, across the Golden Horn",
       "1267: Cenova, Haliç'in karşı yakasındaki Galata'da bir koloni kurar"),
     pop=PI(1267, 1347), cam=(41.0230, 28.9740, 2.4)),
 seg(1348, 1392, 15, BY, CON, T("The Galata Tower", "Galata Kulesi"),
     T("1348: the Genoese build the Galata Tower, 63 m tall, at the top of their walled town",
       "1348: Cenevizliler, surlu kasabalarının en yüksek yerine 63 m'lik Galata Kulesi'ni yapar"),
     pop=PI(1348, 1392), cam=(41.0240, 28.9745, 2.0)),
 seg(1393, 1451, 15, BY, CON, T("Ottomans on the Bosphorus", "Boğaz'da Osmanlılar"),
     T("1393–1394: Ottoman sultan Bayezid I builds Anadoluhisarı on the Asian shore",
       "1393–1394: Osmanlı padişahı Yıldırım Bayezid, Anadolu yakasında Anadoluhisarı'nı yaptırır"),
     pop=PI(1393, 1451), cam=(41.0800, 29.0620, 3.4), chapter=T("The Conquest", "Fetih")),
 seg(1452, 1453.25, 16, BY, CON, T("Rumelihisarı", "Rumelihisarı"),
     T("15 April 1452: Mehmed II begins a fortress opposite, on the European shore",
       "15 Nisan 1452: II. Mehmed karşı kıyıda, Avrupa yakasında bir hisar inşasına başlar"),
     pop=P(1452), cam=(41.0830, 29.0600, 2.6)),
 seg(1453.26, 1453.30, 18, BY, CON, T("The Siege Begins", "Kuşatma Başlıyor"),
     T("6 April 1453: the Ottoman army, about 70 cannons with it, begins its assault on the land walls",
       "6 Nisan 1453: yaklaşık 70 topu olan Osmanlı ordusu kara surlarına saldırıya başlar"),
     pop=P(1453), cam=(41.0170, 28.9300, 5.0)),
 seg(1453.31, 1453.40, 16, BY, CON, T("Ships Over the Hill", "Gemiler Karadan"),
     T("22 April 1453: Ottoman ships are dragged over the hill behind Galata into the Golden Horn",
       "22 Nisan 1453: Osmanlı gemileri Galata'nın arkasındaki tepeden Haliç'e indirilir"),
     pop=P(1453), cam=(41.0290, 28.9650, 4.0)),
 seg(1453.41, 1458, 19, OT, IST, T("The Fall of Constantinople", "İstanbul'un Fethi"),
     T("29 May 1453: Mehmed II takes the city after a 53-day siege; Hagia Sophia becomes a mosque",
       "29 Mayıs 1453: II. Mehmed 53 günlük kuşatmanın ardından şehri alır; Ayasofya camiye çevrilir"),
     pop=PI(1453, 1458), cam=(41.0170, 28.9350, 5.0)),
 seg(1459, 1469, 16, OT, IST, T("Topkapı Palace", "Topkapı Sarayı"),
     T("1459: work begins on Topkapı Palace on the point where Byzantion once stood",
       "1459: bir zamanlar Byzantion'un bulunduğu burunda Topkapı Sarayı'nın inşasına başlanır"),
     pop=PI(1459, 1469), cam=(41.0110, 28.9810, 2.2), chapter=T("Ottoman Capital", "Osmanlı Başkenti")),
 seg(1470, 1508, 16, OT, IST, T("The City Fills Again", "Şehir Yeniden Doluyor"),
     T("1470: the Fatih Mosque is finished; by 1481 about 80,000 people live in the city",
       "1470: Fatih Camii tamamlanır; 1481'e gelindiğinde şehirde yaklaşık 80.000 kişi yaşar"),
     pop=PI(1470, 1508), cam=(41.0150, 28.9600, 4.4)),
 seg(1509, 1549, 15, OT, IST, T("The Earthquake of 1509", "1509 Depremi"),
     T("10 September 1509: an earthquake brings down 1,070 homes and damages 49 towers of the walls",
       "10 Eylül 1509: bir deprem 1.070 evi yıkar ve surların 49 kulesine zarar verir"),
     pop=PI(1509, 1549), cam=(41.0140, 28.9450, 5.5)),
 seg(1550, 1608, 17, OT, IST, T("The Süleymaniye", "Süleymaniye"),
     T("1550–1557: the architect Sinan builds the Süleymaniye Mosque, its dome 53 m high",
       "1550–1557: Mimar Sinan, kubbesi 53 m yüksekliğindeki Süleymaniye Camii'ni inşa eder"),
     pop=PI(1550, 1608), cam=(41.0145, 28.9640, 2.4)),
 seg(1609, 1659, 16, OT, IST, T("The Blue Mosque", "Sultanahmet Camii"),
     T("1609–1617: the Sultan Ahmed Mosque rises by the old Hippodrome with six minarets",
       "1609–1617: Sultanahmet Camii altı minaresiyle eski Hipodrom'un yanında yükselir"),
     pop=PI(1609, 1659), cam=(41.0060, 28.9770, 2.0)),
 seg(1660, 1662, 16, OT, IST, T("The Great Fire of 1660", "1660 Büyük Yangını"),
     T("24 July 1660: a fire burns for about two days and destroys some two thirds of the city",
       "24 Temmuz 1660: yaklaşık iki gün süren bir yangın şehrin üçte ikisi kadarını yok eder"),
     pop=PI(1660, 1662), cam=(41.0140, 28.9620, 3.6)),
 seg(1663, 1765, 10, OT, IST, pop=PI(1663, 1765), cam=(41.0300, 28.9900, 8.0)),
 seg(1766, 1835, 15, OT, IST, T("The Earthquake of 1766", "1766 Depremi"),
     T("22 May 1766: an earthquake destroys the Fatih Mosque; a new one is finished in 1771",
       "22 Mayıs 1766: bir deprem Fatih Camii'ni yıkar; yenisi 1771'de tamamlanır"),
     pop=PI(1766, 1835), cam=(41.0190, 28.9500, 2.8)),
 seg(1836, 1844, 15, LOT, IST, T("Bridging the Golden Horn", "Haliç'e Köprü"),
     T("1836: a pontoon bridge, the first across the Golden Horn, opens at Unkapanı",
       "1836: Haliç'in ilk köprüsü olan bir duba köprü Unkapanı'nda açılır"),
     pop=PI(1836, 1844), cam=(41.0230, 28.9640, 2.6), chapter=T("A Modern City", "Modernleşen Şehir")),
 seg(1845, 1855, 15, LOT, IST, T("The Galata Bridge", "Galata Köprüsü"),
     T("1845: a wooden bridge joins Eminönü and Karaköy at the mouth of the Golden Horn",
       "1845: ahşap bir köprü Haliç'in ağzında Eminönü ile Karaköy'ü birleştirir"),
     pop=PI(1845, 1855), cam=(41.0200, 28.9730, 2.2)),
 seg(1856, 1869, 15, LOT, IST, T("Dolmabahçe Palace", "Dolmabahçe Sarayı"),
     T("1856: the new Dolmabahçe Palace on the Bosphorus is finished and the court moves there",
       "1856: Boğaz kıyısındaki yeni Dolmabahçe Sarayı tamamlanır ve saray oraya taşınır"),
     pop=PI(1856, 1869), cam=(41.0350, 28.9960, 2.8)),
 seg(1870, 1872, 14, LOT, IST, T("The Fire of Pera", "Pera Yangını"),
     T("5 June 1870: a great fire sweeps through Pera, north of the Golden Horn",
       "5 Haziran 1870: büyük bir yangın Haliç'in kuzeyindeki Pera'yı silip süpürür"),
     pop=PI(1870, 1872), cam=(41.0300, 28.9790, 2.4)),
 seg(1873, 1889, 15, LOT, IST, T("Trains and the Tünel", "Tren ve Tünel"),
     T("1873: trains reach a station at Sirkeci; the Tünel funicular opens in 1875",
       "1873: trenler Sirkeci'deki bir istasyona ulaşır; Tünel füniküleri 1875'te açılır"),
     pop=PI(1873, 1889), cam=(41.0120, 28.9500, 5.0)),
 seg(1890, 1913, 15, LOT, IST, T("End of the Line", "Hattın Sonu"),
     T("1890: the new Sirkeci station opens, the terminus of the Orient Express",
       "1890: yeni Sirkeci Garı açılır; Orient Express'in son durağıdır"),
     pop=PI(1890, 1913), cam=(41.0150, 28.9760, 2.2)),
 seg(1914, 1922, 15, LOT, IST, T("Over a Million", "Bir Milyonu Aşkın"),
     T("1914: about 1,125,000 people live here, and electric trams begin to run",
       "1914: burada yaklaşık 1.125.000 kişi yaşar ve elektrikli tramvaylar çalışmaya başlar"),
     pop=PI(1914, 1922), cam=(41.0200, 28.9800, 7.0), chapter=T("Republic", "Cumhuriyet")),
 seg(1923, 1949, 16, REP, IST, T("Ankara Becomes the Capital", "Ankara Başkent Oluyor"),
     T("13 October 1923: the capital moves to Ankara; the 1927 census counts 794,444 people",
       "13 Ekim 1923: başkent Ankara'ya taşınır; 1927 sayımı 794.444 kişi sayar"),
     pop=PI(1923, 1949), cam=(41.0200, 28.9800, 8.0)),
 seg(1950, 1972, 16, REP, IST, T("Boom Years", "Patlama Yılları"),
     T("1950–1970: the population of the province grows from 1.17 to 3 million",
       "1950–1970: ilin nüfusu 1,17 milyondan 3 milyona çıkar"),
     pop=PI(1950, 1972), cam=(41.0300, 28.9800, 16.0)),
 seg(1973, 1987, 16, REP, IST, T("The Bosphorus Bridge", "Boğaziçi Köprüsü"),
     T("30 October 1973: the first bridge across the Bosphorus joins Europe and Asia",
       "30 Ekim 1973: Boğaz'ın ilk köprüsü Avrupa ile Asya'yı birleştirir"),
     pop=PI(1973, 1987), cam=(41.0400, 29.0330, 5.5), chapter=T("Modern Istanbul", "Modern İstanbul")),
 seg(1988, 1999, 15, REP, IST, T("The Second Bridge", "İkinci Köprü"),
     T("3 July 1988: the Fatih Sultan Mehmet Bridge opens beside Rumelihisarı",
       "3 Temmuz 1988: Fatih Sultan Mehmet Köprüsü Rumelihisarı'nın yanında açılır"),
     pop=PI(1988, 1999), cam=(41.0800, 29.0600, 5.0)),
 seg(2000, 2012, 15, REP, IST, T("Ten Million", "On Milyon"),
     T("2000: the census counts 10,018,735 people in the province of Istanbul",
       "2000: sayım İstanbul ilinde 10.018.735 kişi sayar"),
     pop=PI(2000, 2012), cam=(41.0400, 28.9900, 24.0)),
 seg(2013, 2015, 15, TODAY, IST, T("A Tunnel Under the Bosphorus", "Boğaz'ın Altında Tünel"),
     T("29 October 2013: Marmaray opens, a railway 60 m below sea level under the Bosphorus",
       "29 Ekim 2013: Boğaz'ın altından deniz seviyesinin 60 m altında geçen Marmaray açılır"),
     pop=PI(2013, 2015), cam=(41.0150, 29.0000, 5.0)),
 seg(2016, 2017, 15, TODAY, IST, T("The Third Bridge", "Üçüncü Köprü"),
     T("26 August 2016: the Yavuz Sultan Selim Bridge opens near the Black Sea",
       "26 Ağustos 2016: Yavuz Sultan Selim Köprüsü Karadeniz'e yakın açılır"),
     pop=PI(2016, 2017), cam=(41.1980, 29.1110, 6.0)),
 seg(2018, 2024, 15, TODAY, IST, T("Istanbul Airport", "İstanbul Havalimanı"),
     T("29 October 2018: a new airport opens near Lake Terkos, on the Black Sea coast",
       "29 Ekim 2018: Terkos Gölü yakınında, Karadeniz kıyısında yeni bir havalimanı açılır"),
     pop=PI(2018, 2024), cam=(41.1500, 28.8500, 28.0)),
 seg(2025, 2026, 22, TODAY, IST, T("Istanbul Today", "Bugünün İstanbulu"),
     T("From a Greek colony on a point of land to 15,754,053 people at the end of 2025",
       "Bir burundaki Yunan kolonisinden 2025 sonunda 15.754.053 kişiye"),
     pop=[15754053, 15754053], cam=(41.0300, 28.9900, 34.0)),
]
SCALE_T, SCALE_Q = 1.06, 1.0
for s_ in S:
    s_["seconds"] = round(s_["seconds"] * (SCALE_T if s_.get("title") else SCALE_Q))

# ------------------------------------------------------------------ fires, camps, smoke
FIRE_1660 = [(41.0225, 28.9580), (41.0175, 28.9720), (41.0140, 28.9760), (41.0080, 28.9700), (41.0050, 28.9560),
             (41.0090, 28.9450), (41.0180, 28.9470)]
fires = [
 {"year": 196.3, "poly": L(BYZANTION), "duration_s": 6, "plumes": 5},
 {"year": 532.04, "poly": L(rect(41.0045, 28.9730, 41.0110, 28.9830)), "duration_s": 6, "plumes": 5},
 {"year": 1204.28, "poly": L([(41.0235, 28.9580), (41.0180, 28.9700), (41.0130, 28.9680), (41.0170, 28.9520), (41.0230, 28.9480)]),
  "duration_s": 7, "plumes": 6, "plume_scale": 1.5},
 {"year": 1660.56, "poly": L(FIRE_1660), "duration_s": 10, "plumes": 9, "plume_scale": 1.8},
 {"year": 1870.43, "poly": L(rect(41.0290, 28.9740, 41.0350, 28.9840)), "duration_s": 6, "plumes": 5},
]
camps = [
 {"poly": L(rect(41.0080, 28.9600, 41.0160, 28.9700)), "from": -340, "to": -339.2, "count": 120},
 {"poly": L(rect(41.0000, 28.8950, 41.0350, 28.9120)), "from": 626, "to": 627, "count": 260},
 {"poly": L(rect(41.0000, 28.8950, 41.0350, 28.9120)), "from": 717, "to": 718.6, "count": 260},
 {"poly": L(rect(40.9950, 28.9000, 41.0380, 28.9150)), "from": 1453.25, "to": 1453.42, "count": 400},
 {"poly": L(rect(41.0300, 28.9600, 41.0420, 28.9750)), "from": 1453.25, "to": 1453.42, "count": 120},
]
smoke = [
 {"at": [41.0200, 28.9195], "from": 1453.26, "to": 1453.41, "scale": 1.4},
 {"at": [41.0300, 28.9330], "from": 1453.27, "to": 1453.41, "scale": 1.2},
]

labels = [
 {"text": T("GOLDEN HORN", "HALİÇ"), "at": [41.0300, 28.9560], "kind": "water"},
 {"text": T("BOSPHORUS", "BOĞAZİÇİ"), "at": [41.0620, 29.0450], "kind": "water"},
 {"text": T("SEA OF MARMARA", "MARMARA DENİZİ"), "at": [40.9850, 28.9800], "kind": "water"},
 {"text": T("BLACK SEA", "KARADENİZ"), "at": [41.2700, 29.0500], "kind": "water", "from": 1950},
 {"text": T("Byzantion", "Byzantion"), "at": [41.0115, 28.9830], "kind": "place", "from": -660, "to": -341, "lift_m": 20},
 {"text": T("Chalcedon", "Kalkedon"), "at": [40.9910, 29.0270], "kind": "place", "from": -660, "to": -480},
 {"text": T("EUROPE", "AVRUPA"), "at": [41.0500, 28.9300], "kind": "region", "from": -513, "to": -480},
 {"text": T("ASIA", "ASYA"), "at": [41.0200, 29.0700], "kind": "region", "from": -513, "to": -480},
 {"text": T("Hippodrome", "Hipodrom"), "at": [41.00639, 28.97583], "from": 204, "to": 323, "lift_m": 20},
 {"text": T("Constantine's wall", "Konstantin Suru"), "at": [41.0120, 28.9472], "kind": "place", "from": 325, "to": 329, "lift_m": 20},
 {"text": T("Column of Constantine", "Çemberlitaş"), "at": [41.00861, 28.97111], "from": 330, "to": 359, "lift_m": 60},
 {"text": T("Hagia Sophia", "Ayasofya"), "at": [41.00833, 28.98000], "from": 361, "to": 367, "lift_m": 40},
 {"text": T("Aqueduct of Valens", "Bozdoğan Kemeri"), "at": [41.015944, 28.95556], "from": 369, "to": 412, "lift_m": 40},
 {"text": T("Golden Gate", "Altınkapı"), "at": [40.99335, 28.92309], "from": 414, "to": 446, "lift_m": 30},
 {"text": T("Hippodrome", "Hipodrom"), "at": [41.00639, 28.97583], "from": 532, "to": 536, "lift_m": 20},
 {"text": T("Hagia Sophia", "Ayasofya"), "at": [41.00833, 28.98000], "from": 537.9, "to": 540, "lift_m": 80},
 {"text": T("Galata", "Galata"), "at": [41.0240, 28.9760], "kind": "place", "from": 1204, "to": 1347, "lift_m": 15},
 {"text": T("Galata Tower", "Galata Kulesi"), "at": [41.0256556, 28.9741556], "from": 1349, "to": 1392, "lift_m": 80},
 {"text": T("Anadoluhisarı", "Anadoluhisarı"), "at": [41.081944, 29.066944], "from": 1394, "to": 1453.25, "lift_m": 40},
 {"text": T("Rumelihisarı", "Rumelihisarı"), "at": [41.084722, 29.056111], "from": 1452.4, "to": 1453.25, "lift_m": 40},
 {"text": T("Galata", "Galata"), "at": [41.0250, 28.9760], "kind": "place", "from": 1453.31, "to": 1453.40, "lift_m": 15},
 {"text": T("Topkapı Palace", "Topkapı Sarayı"), "at": [41.013, 28.984], "from": 1460, "to": 1469, "lift_m": 40},
 {"text": T("Fatih Mosque", "Fatih Camii"), "at": [41.01972, 28.94972], "from": 1470, "to": 1508, "lift_m": 60},
 {"text": T("Süleymaniye", "Süleymaniye"), "at": [41.01611, 28.96389], "from": 1556, "to": 1608, "lift_m": 90},
 {"text": T("Sultan Ahmed Mosque", "Sultanahmet Camii"), "at": [41.0053851, 28.9768247], "from": 1616, "to": 1659, "lift_m": 90},
 {"text": T("Fatih Mosque", "Fatih Camii"), "at": [41.01972, 28.94972], "from": 1771, "to": 1835, "lift_m": 60},
 {"text": T("Unkapanı", "Unkapanı"), "at": [41.0215, 28.9610], "kind": "place", "from": 1836.7, "to": 1844, "lift_m": 15},
 {"text": T("Eminönü", "Eminönü"), "at": [41.0165, 28.9725], "kind": "place", "from": 1845, "to": 1855, "lift_m": 15},
 {"text": T("Karaköy", "Karaköy"), "at": [41.0235, 28.9765], "kind": "place", "from": 1845, "to": 1855, "lift_m": 15},
 {"text": T("Dolmabahçe Palace", "Dolmabahçe Sarayı"), "at": [41.0390472, 29.0005035], "from": 1856, "to": 1869, "lift_m": 40},
 {"text": T("Pera", "Pera"), "at": [41.0330, 28.9780], "kind": "place", "from": 1870, "to": 1872, "lift_m": 15},
 {"text": T("Sirkeci", "Sirkeci"), "at": [41.015, 28.977222], "kind": "place", "from": 1873, "to": 1913, "lift_m": 30},
 {"text": T("Ankara →", "Ankara →"), "at": [40.9900, 29.1500], "kind": "region", "from": 1923.8, "to": 1935},
 {"text": T("EUROPE", "AVRUPA"), "at": [41.0700, 28.9900], "kind": "region", "from": 1973, "to": 1987},
 {"text": T("ASIA", "ASYA"), "at": [41.0300, 29.0800], "kind": "region", "from": 1973, "to": 1987},
 {"text": T("Rumelihisarı", "Rumelihisarı"), "at": [41.084722, 29.056111], "from": 1988, "to": 1999, "lift_m": 40},
 {"text": T("Levent", "Levent"), "at": [41.0800, 29.0100], "kind": "place", "from": 2000, "to": 2012, "lift_m": 30},
 {"text": T("Kadıköy", "Kadıköy"), "at": [40.9910, 29.0270], "kind": "place", "from": 2000, "to": 2012},
 {"text": T("Yenikapı", "Yenikapı"), "at": [41.0040, 28.9510], "kind": "place", "from": 2013, "to": 2015, "lift_m": 15},
 {"text": T("Üsküdar", "Üsküdar"), "at": [41.0260, 29.0160], "kind": "place", "from": 2013, "to": 2015, "lift_m": 15},
 {"text": T("Istanbul Airport", "İstanbul Havalimanı"), "at": [41.26222, 28.72778], "kind": "place", "from": 2018.8},
 {"text": T("HISTORIC PENINSULA", "TARİHİ YARIMADA"), "at": [41.0100, 28.9500], "kind": "region", "from": 2025},
]

city = {
 "slug": "istanbul", "seed": 667, "long_ok": True,
 "name": T("Istanbul", "İstanbul"), "intro": T("2,700 Years in 15 Minutes", "15 Dakikada 2.700 Yıl"), "intro_seconds": 4.5,
 "geo": {"bbox": [40.80, 28.55, 41.32, 29.45], "cell_m": 120, "core_bbox": [40.970, 28.890, 41.100, 29.090], "core_cell_m": 30},
 "view": {"azimuth_deg": 0, "pitch_deg": 46, "fov": 34},
 "render": {"vertical_exaggeration": 2.2},
 "segments": S,
 "timed_water": yenikapi_fill(),
 "districts": districts,
 "walls": walls, "bridges": bridges, "roads": roads, "landmarks": landmarks,
 "fires": fires, "camps": camps, "smoke": smoke,
 "open_spaces": [
  {"name": "Hippodrome square (Atmeydanı)", "poly": L([(41.0075, 28.9765), (41.0045, 28.9735), (41.0040, 28.9745), (41.0070, 28.9775)])},
  {"name": "Topkapı gardens / Gülhane (≈)", "poly": L([(41.0165, 28.9800), (41.0130, 28.9795), (41.0110, 28.9810), (41.0125, 28.9840), (41.0160, 28.9845)])},
  {"name": "Belgrad Forest (≈)", "poly": L([(41.2200, 28.9000), (41.2200, 29.0100), (41.1500, 29.0100), (41.1500, 28.9000)])},
 ],
 "labels": labels,
 "youtube": {
  "title": T("Istanbul: 2,700 Years in 15 Minutes (3D Timelapse)", "İstanbul: 15 Dakikada 2.700 Yıl (3D Timelapse)"),
  "description": T(
   "In the 7th century BC Greek colonists settled the point of land between the Golden Horn and the Sea of Marmara. Watch "
   "Byzantion become Constantine's Constantinople, rise behind the Theodosian Walls, build Hagia Sophia and survive siege "
   "after siege, until the crusaders sack it in 1204 and Mehmed II takes it in 1453. Then Ottoman Istanbul fills the "
   "peninsula with mosques, burns and rebuilds, bridges the Golden Horn and the Bosphorus, and grows into a city of over "
   "15 million people on two continents, with the year and the population on screen.",
   "MÖ 7. yüzyılda Yunan kolonistler Haliç ile Marmara Denizi arasındaki buruna yerleşti. Byzantion'un Konstantin'in "
   "Konstantinopolis'ine dönüşmesini, Theodosius Surları'nın ardında büyümesini, Ayasofya'yı inşa etmesini ve kuşatma "
   "üstüne kuşatma atlatmasını izleyin; ta ki Haçlılar 1204'te onu yağmalayana ve II. Mehmed 1453'te fethedene kadar. "
   "Ardından Osmanlı İstanbul'u yarımadayı camilerle doldurur, yanar ve yeniden kurulur, Haliç'e ve Boğaz'a köprüler kurar "
   "ve iki kıtada 15 milyonu aşkın insanın yaşadığı bir şehre dönüşür. Yıl ve nüfus ekranda."),
  "tags": ["istanbul history", "history of istanbul", "constantinople", "byzantium", "3d timelapse", "city evolution",
           "how istanbul grew", "istanbul timelapse", "fall of constantinople", "theodosian walls", "hagia sophia", "ottoman empire",
           "byzantine empire", "urban history"],
  "hashtags": ["#Istanbul", "#History", "#Timelapse"],
  "playlist": T("Cities of Europe", "Avrupa Şehirleri"),
  "thumb": {"line1": T("Istanbul", "İstanbul"), "line2": T("2,700 YEARS", "2.700 YIL"),
            "line3": T("From Byzantion to megacity", "Byzantion'dan megakente"),
            "extra": "&mood=golden&pitch=30&az=0&cam=41.0120,28.9700,5.0"},
 },
 "sources": [],
}
total = sum(s_["seconds"] for s_ in S)
mins = round(total / 60)
city["intro"] = T(f"2,700 Years in {mins} Minutes", f"{mins} Dakikada 2.700 Yıl")
city["youtube"]["title"] = T(f"Istanbul: 2,700 Years in {mins} Minutes (3D Timelapse)", f"İstanbul: {mins} Dakikada 2.700 Yıl (3D Timelapse)")
city["sources"] = json.load(open(os.path.join(HERE, "_sources.json")))
json.dump(city, open(os.path.join(HERE, "city.json"), "w"), ensure_ascii=False, indent=1)
print("segments", len(S), "duration", total, "s =", f"{total // 60}:{total % 60:02d}",
      "(geo.json present: walls snapped to shore)" if GEO else "(no geo.json yet: hand traces)")
