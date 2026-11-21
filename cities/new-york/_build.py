"""Builds cities/new-york/city.json. Every date/figure is from research.md (sources listed there).
Run: python3 cities/new-york/_build.py
Landfill (as cities/boston): lower Manhattan's East River strips (Water St 1730, Front St 1780, South St 1800), the
Battery (1855) and Battery Park City (1976) are modern land inside rough zone polygons, clipped against geo.json
(modern land, core grid). Without geo.json (first preview run) the fills are left out."""
import json, math, os

T = lambda en, tr: {"en": en, "tr": tr}
HERE = os.path.dirname(os.path.abspath(__file__))
LAT0, LON0 = 40.7033, -74.0170          # Battery: origin of the Manhattan axis frame
KX, KY = 111.32 * math.cos(math.radians(LAT0)), 110.574
AX = math.radians(29)                    # Manhattan grid: 29° east of true north (CP1811)


def L(pts):
    return [[round(a, 5), round(b, 5)] for a, b in pts]


def km(p):
    return ((p[1] - LON0) * KX, (p[0] - LAT0) * KY)


def ll(x, y):
    return (LAT0 + y / KY, LON0 + x / KX)


# ------------------------------------------------------------------ Manhattan outline (≈, to mid-river; buildings are
# only placed on land, so the outline just has to stay off the opposite shores)
MAN_W = [(40.6990, -74.0230), (40.7150, -74.0215), (40.7350, -74.0150), (40.7550, -74.0090), (40.7750, -73.9980),
         (40.8000, -73.9790), (40.8300, -73.9610), (40.8600, -73.9440), (40.8780, -73.9310)]
MAN_E = [(40.8740, -73.9110), (40.8500, -73.9250), (40.8300, -73.9330), (40.8050, -73.9300), (40.7900, -73.9370),
         (40.7750, -73.9440), (40.7600, -73.9550), (40.7450, -73.9680), (40.7300, -73.9700), (40.7120, -73.9740),
         (40.7100, -73.9850), (40.7060, -73.9960), (40.7010, -74.0050), (40.6990, -74.0120)]
MANHATTAN = MAN_W + MAN_E


def band(u0, u1, poly=MANHATTAN):
    """Part of poly between two cross-lines u0..u1 km along the Manhattan axis (perpendicular to the avenues)."""
    from shapely.geometry import Polygon
    P = Polygon([km(p) for p in poly]).buffer(0)
    ca, sa = math.cos(AX), math.sin(AX)
    ax = (sa, ca); cr = (ca, -sa)        # axis unit (east, north) and cross unit
    W = 6.0
    q = [(ax[0] * u + cr[0] * v, ax[1] * u + cr[1] * v) for u, v in [(u0, -W), (u1, -W), (u1, W), (u0, W)]]
    g = P.intersection(Polygon(q))
    if g.geom_type != 'Polygon':
        g = max(g.geoms, key=lambda x: x.area)
    return [ll(x, y) for x, y in list(g.exterior.coords)[:-1]]


# ------------------------------------------------------------------ landfill
PEARL = [(40.7020, -74.0150), (40.7030, -74.0138), (40.7034, -74.0113), (40.7046, -74.0094), (40.7058, -74.0076),
         (40.7068, -74.0057), (40.7079, -74.0037), (40.7088, -74.0020), (40.7102, -74.0005)]
EAST_STRIPS = [("Water Street fill (≈)", 1730, 0.0, 0.08), ("Front Street fill (≈)", 1780, 0.08, 0.14),
               ("South Street fill (≈)", 1800, 0.14, 0.45)]
BATTERY = [(40.7022, -74.0128), (40.7048, -74.0150), (40.7062, -74.0172), (40.7062, -74.0240), (40.6985, -74.0240),
           (40.6985, -74.0128)]
BPC = [(40.7062, -74.0172), (40.7065, -74.0160), (40.7090, -74.0148), (40.7120, -74.0140), (40.7160, -74.0131),
       (40.7195, -74.0126), (40.7195, -74.0240), (40.7062, -74.0240)]


def build_fill():
    gp = os.path.join(HERE, 'geo.json')
    if not os.path.exists(gp):
        return [], False
    import base64
    import numpy as np
    from shapely.geometry import Polygon, LineString, box
    from shapely.ops import unary_union
    g = json.load(open(gp)); c = g['core']; lat0, lon0 = g['origin']
    k = 111.32 * math.cos(math.radians(lat0))
    sd = np.frombuffer(base64.b64decode(c['sd_b64']), dtype='<i2').reshape(c['nz'], c['nx'])
    land = sd > 0
    cell = c['cell_km']
    def cell_poly(j, i0, i1):   # in (lon, lat)
        x0 = c['x0'] + (i0 - 0.5) * cell; x1 = c['x0'] + (i1 + 0.5) * cell
        z0 = c['z0'] + (j - 0.5) * cell; z1 = c['z0'] + (j + 0.5) * cell
        return box(lon0 + x0 / k, lat0 - z1 / KY, lon0 + x1 / k, lat0 - z0 / KY)
    def land_in(geom):
        mnx, mny, mxx, mxy = geom.bounds
        i0 = max(0, int(((mnx - lon0) * k - c['x0']) / cell) - 1); i1 = min(c['nx'] - 1, int(((mxx - lon0) * k - c['x0']) / cell) + 1)
        j0 = max(0, int((-(mxy - lat0) * KY - c['z0']) / cell) - 1); j1 = min(c['nz'] - 1, int((-(mny - lat0) * KY - c['z0']) / cell) + 1)
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
    to_xy = lambda poly: Polygon([(b, a) for a, b in poly]).buffer(0)
    # one-sided offsets of the Pearl St line (SE side = right side) in km, back to lon/lat
    line_km = LineString([km(p) for p in PEARL])
    def side(d):
        if d <= 0: return None
        p = line_km.buffer(-d, single_sided=True)
        return Polygon([(ll(x, y)[1], ll(x, y)[0]) for x, y in p.exterior.coords])
    zones, taken = [], unary_union([])
    for name, year, d0, d1 in EAST_STRIPS:
        z = side(d1)
        if d0 > 0: z = z.difference(side(d0))
        z = z.difference(taken); taken = taken.union(side(d1))
        zones.append((name, year, z))
    zones.append(("Battery fill (≈)", 1855, to_xy(BATTERY).difference(taken))); taken = taken.union(to_xy(BATTERY))
    zones.append(("Battery Park City", 1976, to_xy(BPC).difference(taken)))
    out = []
    for name, year, z in zones:
        gz = land_in(z)
        if gz is None or gz.is_empty: continue
        gz = gz.buffer(0.00015).intersection(z.buffer(0.0004)).simplify(0.00004)   # spill a little over the old water edge
        parts = [gz] if gz.geom_type == 'Polygon' else list(getattr(gz, 'geoms', []))
        for i, p in enumerate(parts):
            if p.geom_type != 'Polygon' or p.area < 1e-7: continue
            ring = [(round(y, 5), round(x, 5)) for x, y in p.exterior.coords][:-1]
            out.append({"name": name + (f" #{i + 1}" if len(parts) > 1 else ""), "fill": True, "from": 1600, "to": year, "poly": L(ring)})
    return out, True


FILL, HAVE_GEO = build_fill()


def oval(c, a_m, b_m, rot_deg=0, n=14):
    out = []
    for i in range(n):
        t = 2 * math.pi * i / n; x, y = a_m * math.cos(t), b_m * math.sin(t)
        r = math.radians(rot_deg); x, y = x * math.cos(r) - y * math.sin(r), x * math.sin(r) + y * math.cos(r)
        out.append((c[0] + y / 1000 / KY, c[1] + x / 1000 / KX))
    return out


def strip(a, b, half_m):
    (xa, ya), (xb, yb) = km(a), km(b)
    n = math.hypot(xb - xa, yb - ya); px, py = -(yb - ya) / n * half_m / 1000, (xb - xa) / n * half_m / 1000
    return [ll(xa + px, ya + py), ll(xb + px, yb + py), ll(xb - px, yb - py), ll(xa - px, ya - py)]


COLLECT = oval((40.7163, -74.0019), 520, 380, rot_deg=-20)                 # ≈ 48 acres ≈ 0.19 km² … drawn ≈ 0.6 km² so it reads
HEERE_GRACHT = strip((40.7030, -74.0111), (40.7062, -74.0110), 13)
CENTRAL_PARK = [(40.7644, -73.9730), (40.7681, -73.9819), (40.8006, -73.9581), (40.7968, -73.9493)]
WASH_SQ = oval((40.73083, -73.99750), 110, 90, n=10)

# ------------------------------------------------------------------ timeline
def seg(frm, to, sec, era, city, title=None, sub=None, pop=None, cam=None, chapter=None):
    d = {"from": frm, "to": to, "seconds": sec, "era": era, "city_name": city}
    if title: d["title"] = title; d["sub"] = sub
    if pop is not None: d["population"] = pop
    if cam: d["camera"] = {"center": [cam[0], cam[1]], "dist_km": cam[2]}
    if chapter: d["chapter"] = chapter
    return d


LEN = T("Lenape Land", "Lenape Toprakları"); DUT = T("New Netherland", "Yeni Hollanda"); ENG = T("English Colony", "İngiliz Kolonisi")
REV = T("American Revolution", "Amerikan Devrimi"); EARLY = T("Early Republic", "Erken Cumhuriyet")
IND = T("Industrial Age", "Sanayi Çağı"); MOD = T("20th Century", "20. Yüzyıl"); TODAY = T("Today", "Bugün")
MANA = T("Mannahatta", "Mannahatta"); NAM = T("New Amsterdam", "Yeni Amsterdam"); NY = T("New York", "New York")
NOR = T("New Orange", "Yeni Orange")

# sourced anchors (year, people) — research.md; log-interpolated. Old city to 1890, five boroughs from 1900.
OLD = [(1628, 270), (1655, 1500), (1664, 2000), (1698, 4937), (1712, 5840), (1723, 7248), (1737, 10664), (1746, 11717),
       (1756, 13046), (1771, 21863), (1790, 33131), (1800, 60515), (1810, 96373), (1820, 123706), (1830, 202589),
       (1840, 312710), (1850, 515547), (1860, 813669), (1870, 942292), (1880, 1206299), (1890, 1515301), (1897.99, 1515301)]
NEW = [(1900, 3437202), (1910, 4766883), (1920, 5620048), (1930, 6930446), (1940, 7454995), (1950, 7891957),
       (1960, 7783314), (1970, 7894798), (1980, 7071639), (1990, 7322564), (2000, 8008278), (2010, 8175133),
       (2020, 8804190), (2024, 8478072), (2025, 8584629), (2026, 8584629)]


def P(y):
    A = OLD if y < 1898 else NEW
    for (y0, p0), (y1, p1) in zip(A, A[1:]):
        if y0 <= y <= y1:
            u = (y - y0) / (y1 - y0); v = math.exp(math.log(p0) + (math.log(p1) - math.log(p0)) * u)
            return int(round(v, -1 if v < 10000 else (-2 if v < 100000 else -3)))
    raise ValueError(y)


PI = lambda a, b: [P(a), P(b)]
C_TIP = (40.7060, -74.0110)
S = [
 seg(1600, 1608, 12, LEN, MANA, T("Mannahatta", "Mannahatta"),
     T("Before 1609: the island is Mannahatta, Lenape land in their homeland, Lenapehoking",
       "1609 öncesi: ada Mannahatta'dır; Lenapelerin yurdu Lenapehoking'in bir parçası"),
     cam=(40.7150, -74.0000, 7.0), chapter=T("Lenape Mannahatta", "Lenape Mannahatta'sı")),
 seg(1609, 1623, 11, LEN, MANA, T("The Half Moon", "Halve Maen"),
     T("11 September 1609: Henry Hudson's Half Moon, sailing for the Dutch, enters the bay",
       "11 Eylül 1609: Hollandalılar adına yola çıkan Henry Hudson'ın Halve Maen gemisi körfeze girer"),
     cam=(40.6950, -74.0250, 9.0)),
 seg(1624, 1624.9, 11, DUT, NAM, T("Noten Eylandt", "Noten Eylandt"),
     T("20 May 1624: about thirty Dutch families land on Noten Eylandt, today's Governors Island",
       "20 Mayıs 1624: otuz kadar Hollandalı aile bugünkü Governors Island'a, Noten Eylandt'a çıkar"),
     cam=(40.6980, -74.0140, 4.0), chapter=T("New Amsterdam", "Yeni Amsterdam")),
 seg(1625, 1625.9, 11, DUT, NAM, T("Fort Amsterdam", "Amsterdam Kalesi"),
     T("1625: the Dutch stake out Fort Amsterdam at the island's tip, beside today's Bowling Green",
       "1625: Hollandalılar adanın ucunda, bugünkü Bowling Green'in yanında Amsterdam Kalesi'ni kurar"),
     cam=(40.7040, -74.0130, 2.8)),
 seg(1626, 1646, 11, DUT, NAM, T("A Trade for an Island", "Bir Ada Takası"),
     T("1626: Peter Minuit trades goods worth 60 guilders for the island; 270 people live here by 1628",
       "1626: Peter Minuit ada için 60 lonca değerinde mal verir; 1628'de burada 270 kişi yaşar"),
     pop=[270, P(1646)], cam=(40.7050, -74.0120, 3.0)),
 seg(1646.1, 1652, 11, DUT, NAM, T("Breuckelen", "Breuckelen"),
     T("1646: the village of Breuckelen is founded across the East River, in today's Brooklyn Heights",
       "1646: East River'ın karşısında, bugünkü Brooklyn Heights'ta Breuckelen köyü kurulur"),
     pop=PI(1646.1, 1652), cam=(40.7020, -74.0030, 3.6)),
 seg(1653, 1659, 12, DUT, NAM, T("The Wall", "Sur"),
     T("1653: a 2,340 ft wall of planks and earth is built across the island — today's Wall Street",
       "1653: adanın bir ucundan öbürüne 710 m'lik ahşap ve toprak bir sur yapılır: bugünkü Wall Street"),
     pop=PI(1653, 1659), cam=(40.7060, -74.0100, 2.6)),
 seg(1660, 1663.9, 11, DUT, NAM, T("Nieuw Haarlem", "Nieuw Haarlem"),
     T("1660: under Peter Stuyvesant, the village of Nieuw Haarlem is founded far up the island",
       "1660: Peter Stuyvesant yönetiminde adanın kuzeyinde Nieuw Haarlem köyü kurulur"),
     pop=PI(1660, 1663.9), cam=(40.7450, -73.9800, 14.0)),
 seg(1664, 1672, 12, ENG, NY, T("New Amsterdam Becomes New York", "Yeni Amsterdam New York Oluyor"),
     T("September 1664: four English frigates arrive; Stuyvesant surrenders and the town is renamed",
       "Eylül 1664: dört İngiliz fırkateyni gelir; Stuyvesant teslim olur ve kasabanın adı değişir"),
     pop=PI(1664, 1672), cam=(40.7050, -74.0110, 3.2), chapter=T("English New York", "İngiliz New York'u")),
 seg(1673, 1675, 11, DUT, NOR, T("New Orange", "Yeni Orange"),
     T("August 1673: the Dutch retake the town as New Orange; it is English again in November 1674",
       "Ağustos 1673: Hollandalılar kasabayı Yeni Orange adıyla geri alır; Kasım 1674'te yine İngiliz"),
     pop=PI(1673, 1675), cam=(40.7045, -74.0120, 2.8)),
 seg(1676, 1697, 11, ENG, NY, T("The Canal Is Filled", "Kanal Dolduruluyor"),
     T("1676: the Heere Gracht canal is filled in; it becomes Broad Street",
       "1676: Heere Gracht kanalı doldurulur; burası Broad Street olur"),
     pop=PI(1676, 1697), cam=(40.7050, -74.0110, 2.6)),
 seg(1698, 1729, 12, ENG, NY, T("Trinity Church", "Trinity Kilisesi"),
     T("1698: the first Trinity Church rises on Broadway; the old wall comes down in 1699",
       "1698: Broadway'de ilk Trinity Kilisesi yükselir; eski sur 1699'da yıkılır"),
     pop=PI(1698, 1729), cam=(40.7075, -74.0110, 3.0)),
 seg(1730, 1770, 11, ENG, NY, T("Pushing Out the Shore", "Kıyı İleri Itiliyor"),
     T("By 1730 landfill has moved the East River shore out to today's Water Street",
       "1730'a kadar dolgu, East River kıyısını bugünkü Water Street'e taşır"),
     pop=PI(1730, 1770), cam=(40.7070, -74.0060, 3.2)),
 seg(1771, 1776.6, 6, ENG, NY, pop=PI(1771, 1776.6), cam=(40.7080, -74.0060, 5.0)),
 seg(1776.61, 1776.7, 11, REV, NY, T("The Battle of Long Island", "Long Island Muharebesi"),
     T("27 August 1776: the British defeat Washington's army in Brooklyn",
       "27 Ağustos 1776: İngilizler Brooklyn'de Washington'ın ordusunu yener"),
     pop=PI(1776.61, 1776.7), cam=(40.6950, -73.9950, 7.0), chapter=T("Revolution", "Devrim")),
 seg(1776.71, 1776.9, 12, REV, NY, T("The Great Fire of 1776", "1776 Büyük Yangını"),
     T("21 September 1776: fire burns 10–25% of the city's buildings, Trinity Church among them",
       "21 Eylül 1776: yangın şehrin binalarının %10–25'ini yakar; Trinity Kilisesi de yanar"),
     pop=PI(1776.71, 1776.9), cam=(40.7090, -74.0110, 2.8)),
 seg(1777, 1788, 11, REV, NY, T("Front Street", "Front Street"),
     T("By 1780 the East River landfill reaches today's Front Street",
       "1780'e kadar East River dolgusu bugünkü Front Street'e ulaşır"),
     pop=PI(1777, 1788), cam=(40.7075, -74.0060, 3.2)),
 seg(1789, 1789.9, 12, EARLY, NY, T("Washington Takes the Oath", "Washington Yemin Ediyor"),
     T("30 April 1789: George Washington is sworn in as president at Federal Hall on Wall Street",
       "30 Nisan 1789: George Washington, Wall Street'teki Federal Hall'da başkan olarak yemin eder"),
     pop=PI(1789, 1789.9), cam=(40.7072, -74.0103, 2.4), chapter=T("Capital and Port", "Başkent ve Liman")),
 seg(1790, 1807, 11, EARLY, NY, T("The First Census", "İlk Nüfus Sayımı"),
     T("1790: the first US census counts 33,131 New Yorkers; South Street is filled by 1800",
       "1790: ilk ABD sayımı 33.131 New Yorklu sayar; South Street 1800'e kadar doldurulur"),
     pop=PI(1790, 1807), cam=(40.7090, -74.0060, 3.6)),
 seg(1808, 1810.9, 11, EARLY, NY, T("Castle Clinton", "Castle Clinton"),
     T("1808–1811: a round fort, today's Castle Clinton, is built on a small island off the Battery",
       "1808–1811: Battery açığındaki adacığa yuvarlak bir kale, bugünkü Castle Clinton yapılır"),
     pop=PI(1808, 1810.9), cam=(40.7045, -74.0150, 2.4)),
 seg(1811, 1824, 12, EARLY, NY, T("The Grid", "Izgara"),
     T("1811: a street grid is planned from Houston to 155th Street; the Collect Pond is filled",
       "1811: Houston'dan 155. Sokak'a kadar bir sokak ızgarası planlanır; Collect Gölü doldurulur"),
     pop=PI(1811, 1824), cam=(40.7300, -73.9900, 8.0), chapter=T("The Grid", "Izgara")),
 seg(1825, 1833, 12, IND, NY, T("The Erie Canal", "Erie Kanalı"),
     T("1825: the Erie Canal links the Hudson to the Great Lakes and makes New York the top US port",
       "1825: Erie Kanalı Hudson'ı Büyük Göller'e bağlar; New York ABD'nin bir numaralı limanı olur"),
     pop=PI(1825, 1833), cam=(40.7150, -74.0000, 6.0)),
 seg(1834, 1835.9, 11, IND, NY, T("The City of Brooklyn", "Brooklyn Şehri"),
     T("1834: Brooklyn, across the East River, becomes a city of 23,310 people",
       "1834: East River'ın karşısındaki Brooklyn, 23.310 kişilik bir şehir olur"),
     pop=PI(1834, 1835.9), cam=(40.7020, -73.9930, 4.5)),
 seg(1835.95, 1836.5, 12, IND, NY, T("The Great Fire of 1835", "1835 Büyük Yangını"),
     T("16 December 1835: fire destroys 530–700 buildings on 17 blocks near the East River",
       "16 Aralık 1835: yangın East River yakınında 17 blokta 530–700 binayı yok eder"),
     pop=PI(1835.95, 1836.5), cam=(40.7055, -74.0080, 2.4)),
 seg(1836.6, 1846, 11, IND, NY, T("Trinity Rises Again", "Trinity Yeniden"),
     T("1846: the third Trinity Church is finished; its 281 ft spire tops the city until 1890",
       "1846: üçüncü Trinity Kilisesi tamamlanır; 86 m'lik kulesi 1890'a dek şehrin en yükseğidir"),
     pop=PI(1836.6, 1846), cam=(40.7080, -74.0120, 2.6)),
 seg(1847, 1856, 11, IND, NY, T("Castle Garden", "Castle Garden"),
     T("1855: Castle Clinton becomes the immigrant depot; by 1860 nearly half the city is foreign-born",
       "1855: Castle Clinton göçmen merkezi olur; 1860'ta şehrin neredeyse yarısı yabancı doğumludur"),
     pop=PI(1847, 1856), cam=(40.7080, -74.0050, 4.5), chapter=T("Immigrant City", "Göçmen Şehri")),
 seg(1857, 1869, 12, IND, NY, T("Central Park", "Central Park"),
     T("1857–1858: Seneca Village is cleared and Olmsted and Vaux design the 843-acre Central Park",
       "1857–1858: Seneca Village boşaltılır; Olmsted ve Vaux 341 hektarlık Central Park'ı tasarlar"),
     pop=PI(1857, 1869), cam=(40.7700, -73.9700, 9.0)),
 seg(1870, 1882, 11, IND, NY, T("Building the Bridge", "Köprü Yapılıyor"),
     T("1870: work begins on John A. Roebling's bridge over the East River to Brooklyn",
       "1870: John A. Roebling'in East River üzerinden Brooklyn'e uzanan köprüsünde çalışma başlar"),
     pop=PI(1870, 1882), cam=(40.7090, -73.9980, 4.0)),
 seg(1883, 1885.9, 12, IND, NY, T("The Brooklyn Bridge", "Brooklyn Köprüsü"),
     T("24 May 1883: the Brooklyn Bridge opens, then the longest suspension bridge in the world",
       "24 Mayıs 1883: Brooklyn Köprüsü açılır; o zamanın dünyadaki en uzun asma köprüsü"),
     pop=PI(1883, 1885.9), cam=(40.7060, -73.9960, 3.2)),
 seg(1886, 1891.9, 12, IND, NY, T("The Statue of Liberty", "Özgürlük Heykeli"),
     T("28 October 1886: the Statue of Liberty is dedicated on Bedloe's Island in the harbor",
       "28 Ekim 1886: Özgürlük Heykeli limandaki Bedloe Adası'nda açılır"),
     pop=PI(1886, 1891.9), cam=(40.6950, -74.0300, 5.0)),
 seg(1892, 1897.9, 11, IND, NY, T("Ellis Island", "Ellis Adası"),
     T("1 January 1892: Ellis Island opens; about 12 million immigrants pass through by 1954",
       "1 Ocak 1892: Ellis Adası açılır; 1954'e kadar yaklaşık 12 milyon göçmen buradan geçer"),
     pop=PI(1892, 1897.9), cam=(40.7000, -74.0300, 5.0)),
 seg(1898, 1900, 12, MOD, NY, T("Five Boroughs, One City", "Beş İlçe, Tek Şehir"),
     T("1 January 1898: Manhattan, Brooklyn, Queens, the Bronx and Staten Island become one city",
       "1 Ocak 1898: Manhattan, Brooklyn, Queens, Bronx ve Staten Island tek şehir olur"),
     pop=[1515301, 3437202], cam=(40.7100, -73.9700, 24.0), chapter=T("Greater New York", "Büyük New York")),
 seg(1901, 1908, 11, MOD, NY, T("The Subway", "Metro"),
     T("27 October 1904: the first subway line opens, from City Hall to 145th Street",
       "27 Ekim 1904: ilk metro hattı City Hall'dan 145. Sokak'a kadar açılır"),
     pop=PI(1901, 1908), cam=(40.7600, -73.9700, 14.0)),
 seg(1909, 1912, 11, MOD, NY, T("Bridges to Queens and Brooklyn", "Queens'e ve Brooklyn'e Köprüler"),
     T("1909: the Queensboro and Manhattan bridges open; the Williamsburg Bridge came in 1903",
       "1909: Queensboro ve Manhattan köprüleri açılır; Williamsburg Köprüsü 1903'te gelmişti"),
     pop=PI(1909, 1912), cam=(40.7300, -73.9700, 9.0)),
 seg(1913, 1929, 11, MOD, NY, T("Grand Central", "Grand Central"),
     T("2 February 1913: Grand Central Terminal opens on 42nd Street",
       "2 Şubat 1913: Grand Central Terminali 42. Sokak'ta açılır"),
     pop=PI(1913, 1929), cam=(40.7528, -73.9772, 4.0)),
 seg(1930, 1931.5, 12, MOD, NY, T("The Race to the Sky", "Gökyüzü Yarışı"),
     T("1930–1931: the Chrysler Building (1,046 ft) and the Empire State Building (1,454 ft) open",
       "1930–1931: Chrysler Binası (319 m) ve Empire State Binası (443 m) açılır"),
     pop=PI(1930, 1931.5), cam=(40.7500, -73.9800, 4.0), chapter=T("Skyline", "Silüet")),
 seg(1931.6, 1949, 11, MOD, NY, T("George Washington Bridge", "George Washington Köprüsü"),
     T("25 October 1931: the George Washington Bridge spans the Hudson to New Jersey",
       "25 Ekim 1931: George Washington Köprüsü Hudson'ı aşarak New Jersey'e uzanır"),
     pop=PI(1931.6, 1949), cam=(40.8200, -73.9500, 12.0)),
 seg(1950, 1963, 6, MOD, NY, pop=PI(1950, 1963), cam=(40.7300, -73.9600, 22.0)),
 seg(1964, 1972, 11, MOD, NY, T("The Verrazzano-Narrows", "Verrazzano-Narrows"),
     T("21 November 1964: the Verrazzano-Narrows Bridge links Staten Island and Brooklyn",
       "21 Kasım 1964: Verrazzano-Narrows Köprüsü Staten Island'ı Brooklyn'e bağlar"),
     pop=PI(1964, 1972), cam=(40.6400, -74.0300, 14.0)),
 seg(1973, 1975, 11, MOD, NY, T("The Twin Towers", "İkiz Kuleler"),
     T("4 April 1973: the World Trade Center opens, briefly the tallest buildings in the world",
       "4 Nisan 1973: Dünya Ticaret Merkezi açılır; kısa bir süre dünyanın en yüksek binaları"),
     pop=PI(1973, 1975), cam=(40.7100, -74.0100, 4.0)),
 seg(1976, 1990, 11, MOD, NY, T("Battery Park City", "Battery Park City"),
     T("By 1976 a 92-acre landfill, partly from the World Trade Center dig, extends the Hudson shore",
       "1976'ya dek kısmen DTM kazısından gelen 37 hektarlık dolgu Hudson kıyısını ileri taşır"),
     pop=PI(1976, 1990), cam=(40.7100, -74.0120, 3.6)),
 seg(1991, 2001.6, 11, TODAY, NY, T("Shrinking and Growing", "Küçülme ve Büyüme"),
     T("1970–1980: the city loses about 820,000 people; by 2000 it passes 8 million",
       "1970–1980: şehir yaklaşık 820.000 kişi kaybeder; 2000'de 8 milyonu aşar"),
     pop=PI(1991, 2001.6), cam=(40.7300, -73.9600, 20.0), chapter=T("New York Today", "Bugünün New York'u")),
 seg(2001.7, 2013, 11, TODAY, NY, T("11 September 2001", "11 Eylül 2001"),
     T("11 September 2001: two hijacked planes destroy the Twin Towers in a terrorist attack",
       "11 Eylül 2001: kaçırılan iki uçak bir terör saldırısında İkiz Kuleler'i yıkar"),
     pop=PI(2001.7, 2013), cam=(40.7110, -74.0120, 3.6)),
 seg(2014, 2019, 11, TODAY, NY, T("One World Trade Center", "One World Trade Center"),
     T("3 November 2014: One World Trade Center opens, 1,776 feet tall",
       "3 Kasım 2014: 541 m yüksekliğindeki One World Trade Center açılır"),
     pop=PI(2014, 2019), cam=(40.7130, -74.0130, 4.5)),
 seg(2020, 2026, 16, TODAY, NY, T("New York Today", "Bugünün New York'u"),
     T("From thirty families on Noten Eylandt to about 8.6 million New Yorkers, 400 years on",
       "Noten Eylandt'taki otuz aileden yaklaşık 8,6 milyon New Yorkluya, 400 yıl sonra"),
     pop=[8804190, 8584629], cam=(40.7300, -73.9700, 16.0)),
]

for s_ in S:   # pacing: titled segments a little longer (target ≈ 540 s with the cold open)
    if s_.get("title"): s_["seconds"] = round(s_["seconds"] * 1.05 * 2) / 2

# ------------------------------------------------------------------ geography of growth (≈ reconstructions, research.md)
MAN = MANHATTAN
DUTCH_TOWN = band(0.0, 0.62)                      # south of the wall
ENG_TOWN = band(0.0, 1.6)                         # to the Collect (≈ Chambers St) by 1776
TO_HOUSTON = band(0.0, 3.0)
TO_14TH = band(0.0, 4.25)
TO_42ND = band(0.0, 6.25)
TO_59TH = band(0.0, 7.7)
UPTOWN = band(7.7, 12.0)
HARLEM_V = oval((40.80889, -73.94833), 600, 450)
UPPER = band(12.0, 21.0)
BREUCK = oval((40.6990, -73.9930), 450, 350)
BROOKLYN_CITY = [(40.7060, -73.9990), (40.7120, -73.9650), (40.7000, -73.9450), (40.6750, -73.9500), (40.6650, -73.9900),
                 (40.6800, -74.0100), (40.6950, -74.0050)]
LONG_ISLAND = [(40.8000, -73.9300), (40.8050, -73.7700), (40.7400, -73.7000), (40.6400, -73.7300), (40.5700, -73.7400),
               (40.5550, -73.9500), (40.5700, -74.0400), (40.6400, -74.0450), (40.7000, -74.0100), (40.7450, -73.9700),
               (40.7800, -73.9350)]
BRONX = [(40.8050, -73.9280), (40.8350, -73.9320), (40.8750, -73.9080), (40.9150, -73.9100), (40.9150, -73.7800),
         (40.8300, -73.7800), (40.8000, -73.8800)]
STATEN = [(40.6480, -74.0800), (40.6400, -74.1800), (40.6300, -74.2000), (40.5550, -74.2150), (40.5050, -74.2550),
          (40.4950, -74.2400), (40.5400, -74.1300), (40.5900, -74.0600), (40.6200, -74.0650), (40.6450, -74.0700)]
NJ = [(40.6550, -74.0700), (40.6900, -74.0550), (40.7150, -74.0310), (40.7400, -74.0230), (40.7600, -74.0130),
      (40.7900, -73.9960), (40.8500, -73.9650), (40.8500, -74.0300), (40.7900, -74.0700), (40.7000, -74.1100), (40.6550, -74.1200)]
HOLES_OUT = [L(MAN), L(BREUCK)]
FIN_DIST = band(0.0, 1.5)
MIDTOWN = band(5.6, 7.7)


def D(name, style, poly, frm, to, dens, grain, grow, **kw):
    d = {"name": name, "style": style, "poly": L(poly), "from": frm, "to": to, "density": dens, "grain_m": grain,
         "grow_from": list(grow)}
    d.update(kw); return d


districts = [
 D("Lenape planting grounds (≈)", "celtic", oval((40.7200, -73.9950), 400, 250), 1600, 1601, 0.12, 120, (40.72, -73.995),
   fade=[1640, 1660, 0.0]),
 D("Dutch town (≈)", "medieval", DUTCH_TOWN, 1625, 1660, 0.75, 40, (40.7040, -74.0125)),
 D("Breuckelen (≈)", "medieval", BREUCK, 1646, 1680, 0.35, 70, (40.7020, -73.9935)),
 D("Nieuw Haarlem (≈)", "medieval", HARLEM_V, 1660, 1700, 0.3, 80, (40.80889, -73.94833)),
 D("English town (≈)", "georgian", ENG_TOWN, 1665, 1775, 0.8, 42, (40.7050, -74.0110)),
 D("Rebuilt town and Houston St (≈)", "georgian", TO_HOUSTON, 1777, 1830, 0.82, 45, (40.7080, -74.0080)),
 D("Brooklyn town (≈)", "georgian", BROOKLYN_CITY, 1790, 1860, 0.65, 70, (40.7000, -73.9920), holes=[L(BREUCK)]),
 D("Grid to 14th St (≈)", "victorian", TO_14TH, 1825, 1850, 0.85, 50, (40.7200, -74.0000), holes=[L(TO_HOUSTON), L(WASH_SQ)],
   grid_deg=29),
 D("Grid to 42nd St (≈)", "victorian", TO_42ND, 1845, 1870, 0.85, 55, (40.7350, -73.9900), holes=[L(TO_14TH)], grid_deg=29),
 D("Grid to 59th St (≈)", "victorian", TO_59TH, 1860, 1885, 0.8, 60, (40.7530, -73.9820), holes=[L(TO_42ND)], grid_deg=29),
 D("Upper East and West Side (≈)", "victorian", UPTOWN, 1875, 1905, 0.8, 65, (40.7650, -73.9750), holes=[L(CENTRAL_PARK)],
   grid_deg=29),
 D("Harlem and Washington Heights (≈)", "victorian", UPPER, 1880, 1920, 0.75, 75, (40.8000, -73.9550), holes=[L(HARLEM_V)],
   grid_deg=29),
 D("Brooklyn (≈)", "victorian", BROOKLYN_CITY, 1860, 1900, 0.75, 75, (40.6950, -73.9900)),
 D("Downtown offices (≈)", "modern", FIN_DIST, 1880, 1930, 0.7, 70, (40.7070, -74.0100)),
 D("Midtown (≈)", "modern", MIDTOWN, 1900, 1935, 0.7, 85, (40.7550, -73.9800), grid_deg=29),
 D("Outer boroughs, inner ring (≈)", "suburb", LONG_ISLAND, 1890, 1940, 0.55, 150, (40.7000, -73.9700),
   holes=HOLES_OUT + [L(BROOKLYN_CITY)]),
 D("The Bronx (≈)", "suburb", BRONX, 1890, 1940, 0.55, 150, (40.8100, -73.9200)),
 D("Staten Island (≈)", "suburb", STATEN, 1900, 1990, 0.4, 190, (40.6400, -74.0800)),
 D("Hudson County, New Jersey (≈, outside the city)", "suburb", NJ, 1870, 1950, 0.4, 170, (40.7200, -74.0400)),
 D("Financial District towers", "highrise", FIN_DIST, 1960, 2015, 0.45, 110, (40.7070, -74.0110)),
 D("Midtown towers", "highrise", MIDTOWN, 1950, 2020, 0.4, 120, (40.7550, -73.9800), grid_deg=29),
 D("Battery Park City", "modern", BPC, 1980, 2000, 0.65, 70, (40.7100, -74.0160)),
]

landmarks = [
 {"type": "fort", "name": T("Fort Amsterdam", "Amsterdam Kalesi"), "at": [40.70417, -74.01361], "built": 1625.3, "removed": 1790,
  "rise_s": 4, "size_m": [95, 85, 9], "colors": {"wall": "#9b8a6a"}},
 {"type": "palace", "name": T("U.S. Custom House", "ABD Gümrük Binası"), "at": [40.70417, -74.01361], "built": 1902, "rise_s": 5,
  "size_m": [110, 80, 26], "colors": {"wall": "#d9d2c2", "roof": "#6e767c"}},
 {"type": "church", "name": T("Trinity Church (1698)", "Trinity Kilisesi (1698)"), "at": [40.70806, -74.01222], "built": 1698,
  "removed": 1776.72, "rise_s": 4, "size_m": [36, 18, 18], "rot_deg": 61, "colors": {"wall": "#d8d0bf", "roof": "#5f666f"}, "scale": 1.3},
 {"type": "church", "name": T("Trinity Church (1790)", "Trinity Kilisesi (1790)"), "at": [40.70806, -74.01222], "built": 1788,
  "removed": 1839, "rise_s": 4, "size_m": [40, 20, 22], "rot_deg": 61, "colors": {"wall": "#d8d0bf", "roof": "#5f666f"}, "scale": 1.3},
 {"type": "cathedral", "name": T("Trinity Church", "Trinity Kilisesi"), "at": [40.70806, -74.01222], "built": 1841.4, "rise_s": 10,
  "size_m": [55, 24, 86], "rot_deg": 61, "colors": {"wall": "#8f7f6f", "roof": "#4f565f"}, "scale": 1.2},
 {"type": "box", "name": T("City Hall (Wall Street)", "Belediye (Wall Street)"), "at": [40.70722, -74.01028], "built": 1700,
  "removed": 1812, "rise_s": 4, "size_m": [30, 18, 16], "colors": {"wall": "#b8694f", "roof": "#4f565f"}},
 {"type": "temple", "name": T("Federal Hall", "Federal Hall"), "at": [40.70722, -74.01028], "built": 1840, "rise_s": 5,
  "size_m": [40, 27, 20], "rot_deg": 61, "colors": {"wall": "#e3ddd0", "roof": "#bdb6a8"}},
 {"type": "palace", "name": T("City Hall", "Belediye Sarayı"), "at": [40.7127, -74.0059], "built": 1803.4, "rise_s": 8,
  "size_m": [65, 32, 20], "rot_deg": 0, "colors": {"wall": "#e8e2d4", "roof": "#6d7a80"}},
 {"type": "fort", "name": T("Castle Clinton", "Castle Clinton"), "at": [40.7035, -74.0168], "built": 1808, "rise_s": 6,
  "size_m": [60, 60, 9], "colors": {"wall": "#b8907a"}},
 {"type": "box", "name": T("Ellis Island station", "Ellis Adası istasyonu"), "at": [40.69944, -74.03972], "built": 1891.5, "rise_s": 4,
  "size_m": [100, 50, 24], "colors": {"wall": "#a4513a", "roof": "#8d9aa0"}},
 {"type": "column", "name": T("Statue of Liberty", "Özgürlük Heykeli"), "at": [40.68917, -74.04444], "built": 1886.5, "rise_s": 6,
  "size_m": [26, 26, 93], "colors": {"wall": "#6fae9a"}, "scale": 1.3},
 {"type": "station", "name": T("Grand Central Terminal", "Grand Central Terminali"), "at": [40.7528, -73.9772], "built": 1910,
  "rise_s": 6, "size_m": [200, 90, 34], "rot_deg": 29, "colors": {"wall": "#d6cdb8", "roof": "#6f8c86"}},
 {"type": "spire_tower", "name": T("Chrysler Building", "Chrysler Binası"), "at": [40.75167, -73.97528], "built": 1929.1, "rise_s": 8,
  "size_m": [55, 55, 319], "colors": {"wall": "#c9cdd2"}},
 {"type": "skyscraper", "name": T("Empire State Building", "Empire State Binası"), "at": [40.7483, -73.9856], "built": 1930.2,
  "rise_s": 10, "size_m": [60, 45, 443], "rot_deg": 29, "colors": {"wall": "#b9b2a6"}},
 {"type": "skyscraper", "name": T("WTC North Tower", "DTM Kuzey Kulesi"), "at": [40.7117, -74.0131], "built": 1968, "removed": 2001.7,
  "rise_s": 8, "size_m": [63, 63, 417], "rot_deg": 29, "colors": {"wall": "#9aa6ae"}},
 {"type": "skyscraper", "name": T("WTC South Tower", "DTM Güney Kulesi"), "at": [40.7106, -74.0132], "built": 1969, "removed": 2001.7,
  "rise_s": 8, "size_m": [63, 63, 415], "rot_deg": 29, "colors": {"wall": "#9aa6ae"}},
 {"type": "spire_tower", "name": T("One World Trade Center", "One World Trade Center"), "at": [40.71306, -74.01333], "built": 2010,
  "rise_s": 10, "size_m": [62, 62, 541], "colors": {"wall": "#8fb2c8"}},
]

bridges = [
 {"name": "Brooklyn Bridge (≈ ends)", "path": [[40.7092, -74.0015], [40.7022, -73.9913]], "built": 1883.39, "style": "tower", "width_m": 26, "draw_s": 4},
 {"name": "Williamsburg Bridge (≈ ends)", "path": [[40.7160, -73.9800], [40.7110, -73.9640]], "built": 1903.97, "style": "iron", "width_m": 36},
 {"name": "Queensboro Bridge (≈ ends)", "path": [[40.7600, -73.9610], [40.7538, -73.9484]], "built": 1909.24, "style": "iron", "width_m": 28},
 {"name": "Manhattan Bridge (≈ ends)", "path": [[40.7115, -73.9945], [40.7025, -73.9865]], "built": 1909.99, "style": "iron", "width_m": 37},
 {"name": "George Washington Bridge (≈ ends)", "path": [[40.8540, -73.9625], [40.8494, -73.9430]], "built": 1931.81, "style": "modern", "width_m": 36, "draw_s": 4},
 {"name": "Verrazzano-Narrows Bridge (≈ ends)", "path": [[40.6040, -74.0590], [40.6088, -74.0321]], "built": 1964.89, "style": "modern", "width_m": 31, "draw_s": 4},
]

roads = [
 {"name": "Broadway (Heeren Wegh, ≈)", "path": L([(40.7046, -74.0136), (40.7081, -74.0114), (40.7127, -74.0080), (40.7190, -74.0030),
  (40.7255, -73.9965), (40.7359, -73.9906)]), "from": 1625, "kind": "road", "width_m": 12},
]

FIRE_1776 = [(40.7040, -74.0140), (40.7058, -74.0128), (40.7085, -74.0113), (40.7125, -74.0085), (40.7145, -74.0100), (40.7120, -74.0135),
             (40.7080, -74.0150), (40.7050, -74.0160)]
FIRE_1835 = [(40.7083, -74.0079), (40.7062, -74.0093), (40.7045, -74.0105), (40.7032, -74.0107), (40.7028, -74.0093), (40.7045, -74.0064),
             (40.7062, -74.0042), (40.7074, -74.0036), (40.7079, -74.0056)]

def lab(en, tr, at, frm=None, to=None, kind="place", now=None, lift=None):
    d = {"text": T(en, tr), "at": list(at), "kind": kind}
    if frm is not None: d["from"] = frm
    if to is not None: d["to"] = to
    if now: d["now"] = T(*now)
    if lift: d["lift_m"] = lift
    return d


labels = [
 lab("HUDSON RIVER", "HUDSON NEHRİ", (40.7400, -74.0200), kind="water", to=1897.9),
 lab("EAST RIVER", "EAST RIVER", (40.7300, -73.9690), kind="water", to=1897.9),
 lab("UPPER BAY", "YUKARI KÖRFEZ", (40.6750, -74.0450), kind="water", frm=1609, to=1660),
 lab("MANNAHATTA", "MANNAHATTA", (40.7400, -73.9900), kind="region", to=1623),
 lab("Noten Eylandt", "Noten Eylandt", (40.69139, -74.01611), 1624, 1645, now=("Governors Island", "Governors Island")),
 lab("Fort Amsterdam", "Amsterdam Kalesi", (40.70417, -74.01361), 1625, 1663.9, now=("U.S. Custom House site", "ABD Gümrük Binası'nın yeri"), lift=30),
 lab("Breuckelen", "Breuckelen", (40.696, -73.995), 1646.1, 1652, now=("Brooklyn Heights", "Brooklyn Heights")),
 lab("Heere Gracht", "Heere Gracht", (40.7050, -74.0116), 1653, 1659, now=("Broad Street", "Broad Street"), lift=10),
 lab("The Wall", "Sur", (40.7072, -74.0090), 1653, 1659, now=("Wall Street", "Wall Street"), lift=20),
 lab("Nieuw Haarlem", "Nieuw Haarlem", (40.80889, -73.94833), 1660, 1663.9, now=("Harlem", "Harlem")),
 lab("The Wall", "Sur", (40.7072, -74.0090), 1664, 1697, now=("Wall Street", "Wall Street"), lift=20),
 lab("Broad Street", "Broad Street", (40.7050, -74.0116), 1676, 1697, lift=10),
 lab("Trinity Church", "Trinity Kilisesi", (40.70806, -74.01222), 1698, 1729, lift=40),
 lab("Water Street", "Water Street", (40.7055, -74.0060), 1730, 1770, lift=10),
 lab("Collect Pond", "Collect Gölü", (40.7163, -74.0019), 1730, 1776.6, kind="water", now=("Collect Pond Park", "Collect Pond Park")),
 lab("Brooklyn", "Brooklyn", (40.6800, -73.9800), 1776.61, 1776.7),
 lab("Front Street", "Front Street", (40.7050, -74.0050), 1777, 1788, lift=10),
 lab("Federal Hall", "Federal Hall", (40.70722, -74.01028), 1789, 1789.9, lift=40),
 lab("Potter's field", "Kimsesizler mezarlığı", (40.73083, -73.99750), 1797, 1824, now=("Washington Square Park", "Washington Square Park")),
 lab("West Battery", "West Battery", (40.7035, -74.0168), 1808, 1810.9, now=("Castle Clinton", "Castle Clinton"), lift=20),
 lab("Collect Pond", "Collect Gölü", (40.7163, -74.0019), 1811, 1824, now=("Collect Pond Park", "Collect Pond Park")),
 lab("Seneca Village", "Seneca Village", (40.784002, -73.968892), 1825, 1856, now=("Central Park", "Central Park")),
 lab("Brooklyn", "Brooklyn", (40.6930, -73.9900), 1834, 1835.9),
 lab("Castle Garden", "Castle Garden", (40.7035, -74.0168), 1847, 1856, now=("Castle Clinton", "Castle Clinton"), lift=20),
 lab("Five Points", "Five Points", (40.714861, -73.999861), 1847, 1856, now=("Columbus Park", "Columbus Park"), lift=15),
 lab("Central Park", "Central Park", (40.7800, -73.9650), 1857, 1869),
 lab("Bedloe's Island", "Bedloe Adası", (40.68917, -74.04444), 1886, 1891.9, now=("Liberty Island", "Liberty Island"), lift=110),
 lab("Ellis Island", "Ellis Adası", (40.69944, -74.03972), 1892, 1897.9, lift=30),
 lab("MANHATTAN", "MANHATTAN", (40.7850, -73.9650), 1898, 1900, kind="region"),
 lab("BROOKLYN", "BROOKLYN", (40.6500, -73.9500), 1898, 1900, kind="region"),
 lab("QUEENS", "QUEENS", (40.7100, -73.8200), 1898, 1900, kind="region"),
 lab("THE BRONX", "BRONX", (40.8450, -73.8650), 1898, 1900, kind="region"),
 lab("STATEN ISLAND", "STATEN ISLAND", (40.5800, -74.1500), 1898, 1900, kind="region"),
 lab("City Hall", "City Hall", (40.7127, -74.0059), 1901, 1908, lift=30),
 lab("Harlem", "Harlem", (40.80889, -73.94833), 1901, 1908),
 lab("Long Island City", "Long Island City", (40.7450, -73.9450), 1909, 1912),
 lab("Williamsburg", "Williamsburg", (40.7100, -73.9550), 1909, 1912),
 lab("Grand Central", "Grand Central", (40.7528, -73.9772), 1913, 1929, lift=60),
 lab("Chrysler", "Chrysler", (40.75167, -73.97528), 1930.4, 1931.5, lift=340),
 lab("Empire State", "Empire State", (40.7483, -73.9856), 1931.3, 1931.5, lift=460),
 lab("NEW JERSEY", "NEW JERSEY", (40.8300, -74.0100), 1931.6, 1949, kind="region"),
 lab("Staten Island", "Staten Island", (40.6100, -74.0900), 1964, 1972),
 lab("Bay Ridge", "Bay Ridge", (40.6250, -74.0300), 1964, 1972),
 lab("World Trade Center", "Dünya Ticaret Merkezi", (40.71167, -74.0125), 1973.3, 1975, lift=440),
 lab("Battery Park City", "Battery Park City", (40.713, -74.016), 1976, 1990, lift=20),
 lab("One World Trade Center", "One World Trade Center", (40.71306, -74.01333), 2014.8, 2019, lift=560),
 lab("MANHATTAN", "MANHATTAN", (40.7850, -73.9650), 2020, kind="region"),
 lab("BROOKLYN", "BROOKLYN", (40.6500, -73.9500), 2020, kind="region"),
 lab("QUEENS", "QUEENS", (40.7100, -73.8200), 2020, kind="region"),
 lab("THE BRONX", "BRONX", (40.8450, -73.8650), 2020, kind="region"),
 lab("Harlem", "Harlem", (40.80889, -73.94833), 2020),
 lab("Financial District", "Financial District", (40.7075, -74.0090), 2020, lift=40),
 lab("Midtown", "Midtown", (40.7549, -73.9840), 2020, lift=40),
 lab("Brooklyn Heights", "Brooklyn Heights", (40.696, -73.995), 2020),
]
labels.append(lab("Trinity Church", "Trinity Kilisesi", (40.70806, -74.01222), 1836.6, 1846, lift=100))

# Collect Pond as a fill (water until 1811, then buildable); the Heere Gracht is only a label (a strip of water
# would block buildings forever and would show before it was dug)
timed_water = FILL + [{"name": "Collect Pond (≈ outline)", "fill": True, "poly": L(COLLECT), "from": 1600, "to": 1811}]

city = {
 "slug": "new-york", "seed": 1624, "long_ok": True,
 "name": T("New York", "New York"),
 "intro": T("400 Years in 9 Minutes", "9 Dakikada 400 Yıl"), "intro_seconds": 3,
 "cold_open": {"seconds": 7, "hold": 4.5, "kicker": T("400 years · from New Amsterdam to megacity", "400 yıl · Yeni Amsterdam'dan megakente"),
               "camera": {"center": [40.7250, -73.9900], "dist_km": 12.0}},
 "people_notes": True,
 "closing_question": T("When did your family's story in New York begin?", "Ailenizin New York hikâyesi hangi yıl başladı?"),
 "music": {"style": "eras"},
 "geo": {"bbox": [40.47, -74.32, 40.97, -73.62], "cell_m": 120, "core_bbox": [40.685, -74.035, 40.765, -73.94], "core_cell_m": 30,
         "rivers_keep": ["Hudson", "East River", "Harlem", "Bronx", "Newtown", "Gowanus", "Flushing", "Hackensack", "Passaic",
                         "Kill", "Spuyten", "Hutchinson"],
         "lakes_from": 1860},
 "view": {"azimuth_deg": 0, "pitch_deg": 46, "fov": 34},
 "render": {"vertical_exaggeration": 2.5},
 "segments": S,
 "timed_water": timed_water,
 "districts": districts,
 "walls": [{"name": "The Wall (Het Cingel, ≈ course along Wall Street)", "path": L([(40.7084, -74.0130), (40.70806, -74.01222),
            (40.70722, -74.01028), (40.7060, -74.0075)]), "built": 1653, "removed": 1699, "height": "low", "towers_m": 0, "draw_s": 3.0}],
 "bridges": bridges, "roads": roads, "landmarks": landmarks,
 "fires": [
  {"year": 1776.72, "poly": L(FIRE_1776), "duration_s": 6, "plumes": 6},
  {"year": 1835.96, "poly": L(FIRE_1835), "duration_s": 6, "plumes": 5},
 ],
 "smoke": [
  {"at": [40.6750, -73.9850], "from": 1776.64, "to": 1776.68, "scale": 1.0},
  {"at": [40.7110, -74.0130], "from": 2001.7, "to": 2001.75, "scale": 1.4},
 ],
 "camps": [
  {"poly": L([(40.6700, -73.9950), (40.6850, -73.9950), (40.6850, -73.9750), (40.6700, -73.9750)]), "from": 1776.6, "to": 1776.67, "count": 140},
 ],
 "open_spaces": [
  {"name": "Central Park (≈ outline)", "poly": L(CENTRAL_PARK)},
  {"name": "Washington Square (≈)", "poly": L(WASH_SQ)},
  {"name": "City Hall Park (≈)", "poly": L(oval((40.7124, -74.0068), 140, 90, rot_deg=30, n=10))},
 ],
 "labels": labels,
 "youtube": {
  "title": T("New York: 400 Years in 9 Minutes (3D Timelapse, No AI)", "New York: 9 Dakikada 400 Yıl (3D Timelapse, Yapay Zekâ Yok)"),
  "description": T(
   "In 1624 about thirty Dutch families landed on Noten Eylandt, at the edge of Lenape Mannahatta. Watch New Amsterdam build a fort "
   "and a wall that became Wall Street, turn into English New York in 1664, burn in 1776, see Washington sworn in on Wall Street and "
   "push its shore out into the East River. Then the 1811 grid marches up Manhattan, the Erie Canal makes it the nation's port, "
   "immigrants arrive through Castle Garden and Ellis Island, the Brooklyn Bridge, the Statue of Liberty and the subway appear, five "
   "boroughs become one city in 1898, and the skyline climbs from Trinity's spire to the Empire State Building, the Twin Towers and "
   "One World Trade Center — with the year and the population on screen.",
   "1624'te otuz kadar Hollandalı aile, Lenapelerin Mannahatta'sının kıyısındaki Noten Eylandt'a çıktı. Yeni Amsterdam'ın bir kale ve "
   "Wall Street'e adını veren bir sur kurmasını, 1664'te İngiliz New York'una dönüşmesini, 1776'da yanmasını, Washington'ın Wall "
   "Street'te yemin etmesini ve kıyısını East River'a doğru ilerletmesini izleyin. Ardından 1811 ızgarası Manhattan'ı kaplar, Erie "
   "Kanalı onu ülkenin limanı yapar, göçmenler Castle Garden ve Ellis Adası'ndan gelir, Brooklyn Köprüsü, Özgürlük Heykeli ve metro "
   "ortaya çıkar, beş ilçe 1898'de tek şehir olur ve silüet Trinity'nin kulesinden Empire State'e, İkiz Kuleler'e ve One World Trade "
   "Center'a yükselir; yıl ve nüfus ekranda."),
  "tags": ["new york history", "history of new york city", "new amsterdam", "manhattan history", "3d timelapse", "city evolution",
           "how new york grew", "new york timelapse", "wall street history", "brooklyn bridge", "ellis island", "manhattan grid",
           "nyc history", "urban history", "no ai"],
  "hashtags": ["#NewYork", "#History", "#Timelapse"],
  "playlist": T("Cities of North America", "Kuzey Amerika Şehirleri"),
  "playlist_desc": T("North American cities rebuilt in 3D, from the first house to the skyline.", "Kuzey Amerika şehirleri 3D olarak, ilk evden siluete."),
  "thumb": {"line1": T("New York", "New York"), "line2": T("1624 → TODAY", "1624 → BUGÜN"), "line3": T("From New Amsterdam to megacity", "Yeni Amsterdam'dan megakente"),
            "extra": "&pitch=34&az=0&cam=40.7150,-74.0050,7.0", "style": "v2"},
 },
 "sources": [],
}
total = sum(s_["seconds"] for s_ in S) + city["cold_open"]["seconds"]
mins = round(total / 60)
city["intro"] = T(f"400 Years in {mins} Minutes", f"{mins} Dakikada 400 Yıl")
city["youtube"]["title"] = T(f"New York: 400 Years in {mins} Minutes (3D Timelapse, No AI)",
                             f"New York: {mins} Dakikada 400 Yıl (3D Timelapse, Yapay Zekâ Yok)")
city["sources"] = json.load(open(os.path.join(HERE, "_sources.json")))
json.dump(city, open(os.path.join(HERE, "city.json"), "w"), ensure_ascii=False, indent=1)
print("segments", len(S), "duration", total, "s =", f"{int(total) // 60}:{int(total) % 60:02d}", "| fill polys", len(FILL),
      "(geo.json present)" if HAVE_GEO else "(no geo.json yet: fills left out)")
