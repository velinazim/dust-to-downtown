"""Builds cities/toronto/city.json. Every on-screen date/figure is from research.md (sources listed there).
Run: python3 cities/toronto/_build.py
Street lines, district outlines, the 1793 shoreline, fill zones, open spaces and fire areas are simplified traces
(marked ≈ in research.md). Toronto's street grid is turned ~16° anticlockwise from true north; positions marked ≈ are
given in a local grid frame (u metres along King Street, v metres along Yonge Street, origin at King & Yonge ≈).
Landfill: the modern lakefront south of the 1793 shore is made land. Fill zones are clipped against geo.json (modern
land) when it exists; without geo.json they are left out (the first preview run only builds the modern map)."""
import json, math, os

T = lambda en, tr: {"en": en, "tr": tr}
HERE = os.path.dirname(os.path.abspath(__file__))

# ------------------------------------------------------------------ local grid frame (≈)
O = (43.6490, -79.3779)          # King & Yonge (≈)
TH = math.radians(16.0)          # grid turned ~16° anticlockwise
KX = 111320 * math.cos(math.radians(O[0])); KZ = 110574


def G(u, v):
    e = u * math.cos(TH) - v * math.sin(TH); n = u * math.sin(TH) + v * math.cos(TH)
    return (O[0] + n / KZ, O[1] + e / KX)


def UV(p):
    e = (p[1] - O[1]) * KX; n = (p[0] - O[0]) * KZ
    return (e * math.cos(TH) + n * math.sin(TH), -e * math.sin(TH) + n * math.cos(TH))


R = lambda u0, u1, v0, v1: [G(u0, v0), G(u1, v0), G(u1, v1), G(u0, v1)]
rect = lambda s, w, n, e: [(s, w), (n, w), (n, e), (s, e)]


def L(pts):
    return [[round(a, 5), round(b, 5)] for a, b in pts]


# ------------------------------------------------------------------ published coordinates (research.md)
FORTYORK = (43.63889, -79.40361); ROUILLE = (43.63062, -79.42356); YORK = (43.65028, -79.37194)
STJAMES = (43.65028, -79.37389); UNION = (43.64444, -79.38028); OLDCH = (43.65250, -79.38167)
CITYHALL = (43.65333, -79.38389); LEGIS = (43.662447, -79.391708); VIADUCT = (43.67528, -79.36389)
CNT = (43.642556, -79.387083); DOME = (43.64139, -79.38917); FCP = (43.648778, -79.381694)
PORTL = (43.64806, -79.33833); ISLANDS = (43.620833, -79.378611)
# ≈ positions from the street grid (no published coordinates opened; see research.md)
PARL1 = G(1380, -140)            # SW corner of Front & Parliament (OLA): 1st and 2nd parliament buildings
PARL3 = G(-700, -390)            # Front & Simcoe (OLA): 3rd parliament building
MARKET = G(560, -230)            # St. Lawrence Market / 1845 city hall, south of Front at Jarvis
STLHALL = G(600, 30)             # St. Lawrence Hall, King & Jarvis
ROYALYORK = (43.6458, -79.3815)  # 100 Front St W, opposite Union Station
TDT = (43.6474, -79.3812)        # 66 Wellington St W
CCOURT = (43.6484, -79.3790)     # 25 King St W / 199 Bay St

# ------------------------------------------------------------------ the 1793 shoreline (≈): "low sandy bluffs, just south of today's Front Street"
SHORE_UV = [(-5200, -1250), (-4500, -1060), (-4100, -1010), (-3200, -770), (-2300, -575), (-1500, -505), (-800, -465), (-320, -435),
            (100, -365), (470, -245), (900, -195), (1400, -165), (1800, -150), (2000, -120)]
SHORE = [G(u, v) for u, v in SHORE_UV]
# land north of the 1793 shore (west of the Don) and the north rim of Ashbridge's Bay marsh east of it (≈)
MARSH_N = [G(2000, -120), G(2600, -160), G(3300, -60), G(4200, 120), G(4900, 300), G(5600, 520)]
ORIG_LAND = SHORE + MARSH_N + [G(9000, 900), G(9000, 9000), G(-9000, 9000), G(-9000, -1500), G(-5200, -1500)]
# the old sand bar along the south of Ashbridge's Bay, which joined the peninsula to the mainland (≈)
BAR = [(43.6362, -79.3545), (43.6390, -79.3545), (43.6412, -79.3310), (43.6520, -79.3160), (43.6610, -79.3060), (43.6585, -79.3030),
       (43.6495, -79.3140), (43.6385, -79.3290), (43.6362, -79.3420)]
EASTERN_GAP = rect(43.6295, -79.3560, 43.6372, -79.3490)

# fill zones (name, year it is land, rough zone) — clipped to modern land minus ORIG_LAND and BAR; earlier entries win
ESPL = [G(u, v) for u, v in SHORE_UV if -1000 <= u <= 2000][::-1] + [G(u, v - 170) for u, v in SHORE_UV if -1000 <= u <= 2000]
ZONES = [
 ("The Esplanade (≈)", 1865, ESPL),
 ("North-shore fill, Yonge to the Don (≈)", 1955, [G(-150, -700), G(2050, -560), G(2050, -1000), G(-150, -1100)]),
 ("Harbour Commission fill, central (≈)", 1925, rect(43.6345, -79.4150, 43.6560, -79.3560)),
 ("Harbour Commission fill, west (≈)", 1925, rect(43.6200, -79.4800, 43.6420, -79.4150)),
 ("Ashbridge's Bay fill, west (≈)", 1922, rect(43.6380, -79.3560, 43.6600, -79.3380)),
 ("Ashbridge's Bay fill, east (≈)", 1929, rect(43.6390, -79.3380, 43.6650, -79.3050)),
 ("Leslie Street Spit (≈)", 1972, [(43.6400, -79.3500), (43.6420, -79.3150), (43.6100, -79.3150), (43.6000, -79.3400), (43.6200, -79.3500)]),
]


def build_fill():
    gp = os.path.join(HERE, 'geo.json')
    if not os.path.exists(gp):
        return [], False
    import base64
    import numpy as np
    from shapely.geometry import Polygon, box
    from shapely.ops import unary_union
    g = json.load(open(gp)); c = g['core'] if g.get('core') else g; lat0, lon0 = g['origin']
    k = 111.32 * math.cos(math.radians(lat0)); kz = 110.574
    from scipy import ndimage
    el = np.frombuffer(base64.b64decode(c['elev_b64']), dtype='<i2').reshape(c['nz'], c['nx'])
    land = el >= 0
    land = ndimage.binary_erosion(land, iterations=1)
    cell = c['cell_km']
    def cell_poly(j, i0, i1):
        x0 = c['x0'] + (i0 - 0.5) * cell; x1 = c['x0'] + (i1 + 0.5) * cell
        z0 = c['z0'] + (j - 0.5) * cell; z1 = c['z0'] + (j + 0.5) * cell
        return box(lon0 + x0 / k, lat0 - z1 / kz, lon0 + x1 / k, lat0 - z0 / kz)
    def to_xy(poly):
        return Polygon([(b, a) for a, b in poly]).buffer(0)
    orig = unary_union([to_xy(ORIG_LAND), to_xy(BAR)])
    def land_in(geom):
        mnx, mny, mxx, mxy = geom.bounds
        i0 = max(0, int(((mnx - lon0) * k - c['x0']) / cell) - 1); i1 = min(c['nx'] - 1, int(((mxx - lon0) * k - c['x0']) / cell) + 1)
        j0 = max(0, int((-(mxy - lat0) * kz - c['z0']) / cell) - 1); j1 = min(c['nz'] - 1, int((-(mny - lat0) * kz - c['z0']) / cell) + 1)
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
    smooth = lambda q: q.buffer(0.00012).buffer(-0.00024).buffer(0.00012) if q is not None and not q.is_empty else None
    out, taken, cores = [], unary_union([]), []
    for name, year, zp in ZONES:
        z = to_xy(zp).difference(orig).difference(taken)
        taken = taken.union(to_xy(zp))
        cores.append((name, year, smooth(land_in(z))))
    cores = [(n, y, q) for n, y, q in cores if q is not None and not q.is_empty]
    for idx, (name, year, q) in enumerate(cores):
        others = unary_union([q2 for j, (_, _, q2) in enumerate(cores) if j != idx])
        geom = q.buffer(0.0005).difference(orig).difference(others).union(q).simplify(0.00005)
        parts = [geom] if geom.geom_type == 'Polygon' else list(getattr(geom, 'geoms', []))
        for i, p in enumerate(parts):
            if p.geom_type != 'Polygon' or p.area < 2e-7: continue
            ring = [(round(y, 5), round(x, 5)) for x, y in p.exterior.coords][:-1]
            out.append({"name": name + (f" #{i + 1}" if len(parts) > 1 else ""), "fill": True, "from": 1600, "to": year, "poly": L(ring)})
    return out, True


FILL, HAVE_GEO = build_fill()

# ------------------------------------------------------------------ population (research.md)
OLD = [(1796, 600), (1812, 1460), (1813.3, 1460), (1813.4, 720), (1825, 1600), (1830, 2860), (1832, 5500), (1834, 9252),
       (1851, 30000), (1871, 56092), (1881, 86415), (1891, 181022), (1901, 208040), (1911, 381383), (1921, 521893),
       (1931, 631207), (1941, 667567), (1951, 675754), (1953.99, 675754)]
NOW = [(1951, 1176622), (1961, 1824481), (1971, 2089729), (1976, 2124291), (1981, 2137395), (1986, 2192721), (1991, 2275771),
       (1996, 2385421), (2001, 2481494), (2006, 2503281), (2011, 2615060), (2016, 2731571), (2021, 2794356), (2026, 2794356)]


def P(y):
    A = OLD if y < 1954 else NOW
    for y0, p0 in A:
        if y == y0: return p0
    for (y0, p0), (y1, p1) in zip(A, A[1:]):
        if y0 <= y <= y1:
            v = p0 + (p1 - p0) * (y - y0) / (y1 - y0)
            return int(round(v, -1 if v < 10000 else (-2 if v < 100000 else -3)))
    raise ValueError(y)
PI = lambda a, b: [P(a), P(b)]


def seg(frm, to, sec, era, city, title=None, sub=None, pop=None, cam=None, chapter=None):
    d = {"from": frm, "to": to, "seconds": sec, "era": era, "city_name": city}
    if title: d["title"] = title; d["sub"] = sub
    if pop is not None: d["population"] = pop
    if cam: d["camera"] = {"center": [round(cam[0], 5), round(cam[1], 5)], "dist_km": cam[2]}
    if chapter: d["chapter"] = chapter
    return d


IND = T("Indigenous Lands", "Yerli Toprakları")
FR = T("New France", "Yeni Fransa"); BR = T("British North America", "İngiliz Kuzey Amerikası")
UC = T("Upper Canada", "Yukarı Kanada"); PC = T("Province of Canada", "Kanada Eyaleti"); CA = T("Canada", "Kanada")
TODAY = T("Today", "Bugün")
SHOREN = T("Lake Ontario shore", "Ontario Gölü kıyısı"); TOR = T("Toronto", "Toronto"); YORKN = T("York", "York")
cam = lambda p, d, dn=0.0: (p[0] + dn, p[1], d)
HUMBER = (43.6550, -79.4750)

S = [
 seg(1650, 1686.9, 20, IND, SHOREN, T("The Carrying-Place", "Taşıma Yolu"),
     T("17th century: the Seneca village of Teiaiagon, some 2,000 people, guards the Humber trail",
       "17. yüzyıl: yaklaşık 2.000 kişilik Seneca köyü Teiaiagon, Humber patikasını korur"),
     cam=cam(HUMBER, 12.0), chapter=T("Before Toronto", "Toronto'dan Önce")),
 seg(1687, 1719.9, 14, IND, SHOREN, T("Mississauga Country", "Mississauga Toprakları"),
     T("By 1687 the Seneca villages are abandoned; Mississaugas move onto the shore",
       "1687'ye gelindiğinde Seneca köyleri terk edilmiştir; kıyıya Mississaugalar yerleşir"),
     cam=(43.6450, -79.4300, 14.0)),
 seg(1720, 1749.9, 15, FR, SHOREN, T("A French Post on the Humber", "Humber'da Bir Fransız Karakolu"),
     T("1720: the French build a small trading post on the Humber, the Magasin Royal",
       "1720: Fransızlar Humber kıyısına küçük bir ticaret karakolu, Magasin Royal'i kurar"),
     cam=cam(HUMBER, 7.0)),
 seg(1750, 1758.9, 17, FR, T("Fort Rouillé", "Rouillé Kalesi"), T("Fort Rouillé", "Rouillé Kalesi"),
     T("1750–51: the French build Fort Rouillé, a 55 m square palisade on the lake",
       "1750–51: Fransızlar göl kıyısına 55 metrelik kare bir şarampol, Rouillé Kalesi'ni kurar"),
     cam=cam(ROUILLE, 2.6, 0.004), chapter=T("A French Fort", "Bir Fransız Kalesi")),
 seg(1759, 1759.9, 15, FR, T("Fort Rouillé", "Rouillé Kalesi"), T("The French Burn Their Fort", "Fransızlar Kalelerini Yakıyor"),
     T("July 1759: after Fort Niagara falls, the garrison burns Fort Rouillé and leaves",
       "Temmuz 1759: Niagara Kalesi düşünce garnizon Rouillé Kalesi'ni yakıp çekilir"),
     cam=cam(ROUILLE, 3.0, 0.004)),
 seg(1760, 1786.9, 8, BR, SHOREN, cam=(43.6450, -79.3900, 9.0)),
 seg(1787, 1792.9, 16, BR, SHOREN, T("The Toronto Purchase", "Toronto Satın Alımı"),
     T("23 September 1787: the Crown buys land from the Mississaugas; the deal is disputed",
       "23 Eylül 1787: Taç, Mississaugalardan toprak satın alır; anlaşma tartışmalıdır"),
     cam=(43.6550, -79.3900, 14.0), chapter=T("The Town of York", "York Kasabası")),
 seg(1793, 1793.6, 16, UC, SHOREN, T("The Queen's Rangers Land", "Korucular Karaya Çıkıyor"),
     T("20 July 1793: 100 soldiers land by Garrison Creek and begin Fort York",
       "20 Temmuz 1793: 100 asker Garrison Deresi'nin yanında karaya çıkar ve York Kalesi'ni kurar"),
     cam=cam(FORTYORK, 3.0, 0.004)),
 seg(1793.65, 1795.9, 18, UC, YORKN, T("The Town of York", "York Kasabası"),
     T("27 August 1793: Simcoe founds York — ten blocks between Front and Adelaide",
       "27 Ağustos 1793: Simcoe, Front ile Adelaide arasında on bloktan oluşan York'u kurar"),
     cam=cam(YORK, 2.6, 0.003)),
 seg(1796, 1796.99, 15, UC, YORKN, T("Capital of Upper Canada", "Yukarı Kanada'nın Başkenti"),
     T("1 February 1796: York becomes the permanent capital of Upper Canada",
       "1 Şubat 1796: York, Yukarı Kanada'nın kalıcı başkenti olur"),
     pop=600, cam=cam(YORK, 3.0, 0.003)),
 seg(1797, 1806.9, 16, UC, YORKN, T("Parliament on Front Street", "Front Caddesi'nde Meclis"),
     T("1797: parliament meets in brick buildings at Front and Parliament; the town grows west",
       "1797: meclis Front ve Parliament köşesindeki tuğla binalarda toplanır; kasaba batıya büyür"),
     pop=PI(1797, 1806.9), cam=cam(G(700, -100), 3.2, 0.003)),
 seg(1807, 1812.9, 14, UC, YORKN, T("The First Church", "İlk Kilise"),
     T("1807: a wooden church rises on King Street — the first St. James'",
       "1807: King Caddesi'nde ahşap bir kilise yükselir — ilk St. James"),
     pop=PI(1807, 1812.9), cam=cam(STJAMES, 2.4, 0.002)),
 seg(1813, 1813.33, 22, UC, YORKN, T("The Battle of York", "York Muharebesi"),
     T("27 April 1813: US troops land; retreating British blow up the fort's magazine",
       "27 Nisan 1813: ABD askerleri karaya çıkar; çekilen İngilizler kalenin cephaneliğini patlatır"),
     pop=[1460, 1460], cam=cam(FORTYORK, 3.4, 0.004), chapter=T("The War of 1812", "1812 Savaşı")),
 seg(1813.33, 1813.6, 17, UC, YORKN, T("York Occupied", "York İşgal Altında"),
     T("Until 8 May 1813: the invaders hold the town and burn the parliament buildings",
       "8 Mayıs 1813'e dek: işgalciler kasabayı tutar ve meclis binalarını yakar"),
     pop=[1460, 720], cam=cam(G(700, -100), 3.4, 0.003)),
 seg(1813.6, 1819.9, 15, UC, YORKN, T("Fort York Rebuilt", "York Kalesi Yeniden Kuruluyor"),
     T("By 1816 the rebuilt fort has eighteen buildings for 650 soldiers",
       "1816'ya gelindiğinde yeniden kurulan kalede 650 asker için on sekiz bina vardır"),
     pop=PI(1813.6, 1819.9), cam=cam(FORTYORK, 3.0, 0.004)),
 seg(1820, 1831.9, 15, UC, YORKN, T("Parliament Burns Again", "Meclis Yine Yanıyor"),
     T("1824: an overheated chimney flue burns the second parliament building",
       "1824: aşırı ısınan bir baca, ikinci meclis binasını yakar"),
     pop=PI(1820, 1831.9), cam=cam(G(800, -100), 3.6, 0.003)),
 seg(1832, 1833.99, 15, UC, YORKN, T("Cholera", "Kolera"),
     T("1832 and 1834: cholera outbreaks kill about 1,000 people in York",
       "1832 ve 1834: kolera salgınları York'ta yaklaşık 1.000 kişinin canını alır"),
     pop=PI(1832, 1833.99), cam=cam(YORK, 4.0, 0.004)),
 seg(1834, 1836.9, 18, UC, TOR, T("The City of Toronto", "Toronto Şehri"),
     T("6 March 1834: York is incorporated as the City of Toronto — 9,252 people",
       "6 Mart 1834: York, Toronto Şehri olur — 9.252 kişi"),
     pop=PI(1834, 1836.9), cam=cam(G(200, 0), 4.5, 0.006), chapter=T("City of Toronto", "Toronto Şehri")),
 seg(1837, 1840.9, 15, UC, TOR, T("Rebellion on Yonge Street", "Yonge Caddesi'nde İsyan"),
     T("1837: the Upper Canada Rebellion is crushed at Montgomery's Tavern on Yonge Street",
       "1837: Yukarı Kanada İsyanı, Yonge Caddesi'ndeki Montgomery Meyhanesi'nde bastırılır"),
     pop=PI(1837, 1840.9), cam=(43.6650, -79.3900, 7.0)),
 seg(1841, 1846.9, 8, PC, TOR, pop=PI(1841, 1846.9), cam=cam(G(0, 300), 5.0, 0.006)),
 seg(1847, 1848.99, 14, PC, TOR, T("Typhus", "Tifüs"),
     T("1847: a typhus epidemic kills 863 Irish immigrants", "1847: bir tifüs salgını 863 İrlandalı göçmenin canını alır"),
     pop=PI(1847, 1848.99), cam=cam(G(0, 0), 4.5, 0.006)),
 seg(1849, 1849.5, 20, PC, TOR, T("The Cathedral Fire", "Katedral Yangını"),
     T("7 April 1849: fire destroys the Market Block and St. James' Church",
       "7 Nisan 1849: yangın Pazar Bloğu'nu ve St. James Kilisesi'ni yok eder"),
     pop=PI(1849, 1849.5), cam=cam(STJAMES, 2.2, 0.002)),
 seg(1849.5, 1852.9, 15, PC, TOR, T("St. Lawrence Hall", "St. Lawrence Salonu"),
     T("1851: St. Lawrence Hall and a new market rise from the ashes",
       "1851: St. Lawrence Salonu ve yeni bir pazar küllerden yükselir"),
     pop=PI(1849.5, 1852.9), cam=cam(STLHALL, 2.4, 0.002)),
 seg(1853, 1857.9, 16, PC, TOR, T("The Railway Arrives", "Demiryolu Geliyor"),
     T("1853: the Ontario, Simcoe and Huron Railroad reaches the harbour",
       "1853: Ontario, Simcoe ve Huron Demiryolu limana ulaşır"),
     pop=PI(1853, 1857.9), cam=(43.6440, -79.3800, 5.5), chapter=T("Railways and the Waterfront", "Demiryolları ve Kıyı")),
 seg(1858, 1858.6, 18, PC, TOR, T("An Island Is Born", "Bir Ada Doğuyor"),
     T("13 April 1858: a storm cuts through the peninsula — it becomes Toronto Island",
       "13 Nisan 1858: bir fırtına yarımadayı ikiye böler — Toronto Adası doğar"),
     pop=PI(1858, 1858.6), cam=(43.6340, -79.3550, 5.0)),
 seg(1858.6, 1866.99, 16, PC, TOR, T("Making Land", "Toprak Yapmak"),
     T("By 1865 the Esplanade is built on new land along the shore, with railways on it",
       "1865'e gelindiğinde kıyı boyunca yeni toprak üzerine Esplanade ve demiryolları kurulur"),
     pop=PI(1858.6, 1866.99), cam=(43.6450, -79.3720, 4.0)),
 seg(1867, 1872.9, 8, CA, TOR, pop=PI(1867, 1872.9), cam=(43.6480, -79.3800, 5.0)),
 seg(1873, 1882.9, 16, CA, TOR, T("St. James' Spire", "St. James'in Kulesi"),
     T("1873–74: the cathedral's spire rises to 92.9 metres over King Street",
       "1873–74: katedralin kulesi King Caddesi üzerinde 92,9 metreye yükselir"),
     pop=PI(1873, 1882.9), cam=cam(STJAMES, 3.0, 0.003)),
 seg(1883, 1892.9, 16, CA, TOR, T("The City Spreads", "Şehir Yayılıyor"),
     T("1883–1893: Yorkville, Parkdale and other villages join the city",
       "1883–1893: Yorkville, Parkdale ve başka köyler şehre katılır"),
     pop=PI(1883, 1892.9), cam=(43.6620, -79.3950, 11.0), chapter=T("Victorian Toronto", "Viktorya Dönemi Toronto")),
 seg(1893, 1898.9, 15, CA, TOR, T("Queen's Park", "Queen's Park"),
     T("1893: Ontario's new Legislative Building opens in Queen's Park",
       "1893: Ontario'nun yeni Yasama Binası Queen's Park'ta açılır"),
     pop=PI(1893, 1898.9), cam=cam(LEGIS, 3.0, 0.003)),
 seg(1899, 1903.9, 16, CA, TOR, T("Old City Hall", "Eski Belediye Binası"),
     T("18 September 1899: Lennox's City Hall opens; its clock tower stands 103.6 m",
       "18 Eylül 1899: Lennox'un Belediye Binası açılır; saat kulesi 103,6 m"),
     pop=PI(1899, 1903.9), cam=cam(OLDCH, 2.6, 0.003)),
 seg(1904, 1904.6, 22, CA, TOR, T("The Great Fire of 1904", "1904 Büyük Yangını"),
     T("19 April 1904: fire spreads from Wellington Street and destroys over 100 buildings",
       "19 Nisan 1904: Wellington Caddesi'nden yayılan yangın 100'den fazla binayı yok eder"),
     pop=PI(1904, 1904.6), cam=cam(G(-250, -250), 2.6, 0.003), chapter=T("The Great Fire", "Büyük Yangın")),
 seg(1904.6, 1911.9, 15, CA, TOR, T("More Annexations", "Yeni İlhaklar"),
     T("1905–1912: Rosedale, East Toronto, West Toronto and North Toronto join the city",
       "1905–1912: Rosedale, Doğu Toronto, Batı Toronto ve Kuzey Toronto şehre katılır"),
     pop=PI(1904.6, 1911.9), cam=(43.6700, -79.3900, 15.0)),
 seg(1912, 1917.9, 17, CA, TOR, T("Filling Ashbridge's Bay", "Ashbridge Koyu Dolduruluyor"),
     T("1912: the Harbour Commission begins filling the marsh at the mouth of the Don",
       "1912: Liman Komisyonu, Don Nehri'nin ağzındaki bataklığı doldurmaya başlar"),
     pop=PI(1912, 1917.9), cam=(PORTL[0] + 0.006, PORTL[1] - 0.004, 6.0), chapter=T("Made Land", "Yapay Toprak")),
 seg(1918, 1918.99, 16, CA, TOR, T("The Bloor Viaduct", "Bloor Viyadüğü"),
     T("18 October 1918: the 494 m Prince Edward Viaduct spans the Don Valley",
       "18 Ekim 1918: 494 metrelik Prince Edward Viyadüğü Don Vadisi'ni aşar"),
     pop=PI(1918, 1918.99), cam=cam(VIADUCT, 2.8, 0.003)),
 seg(1919, 1926.9, 15, CA, TOR, T("New Land on the Lake", "Gölde Yeni Toprak"),
     T("By 1922, 200 hectares of marsh at the mouth of the Don have been filled in",
       "1922'ye gelindiğinde Don Nehri'nin ağzındaki 200 hektar bataklık doldurulmuştur"),
     pop=PI(1919, 1926.9), cam=(43.6480, -79.3600, 7.0)),
 seg(1927, 1928.9, 16, CA, TOR, T("Union Station", "Union İstasyonu"),
     T("6 August 1927: the Prince of Wales opens Union Station on Front Street",
       "6 Ağustos 1927: Galler Prensi, Front Caddesi'ndeki Union İstasyonu'nu açar"),
     pop=PI(1927, 1928.9), cam=cam(UNION, 2.4, 0.002)),
 seg(1929, 1938.9, 15, CA, TOR, T("The Royal York", "Royal York"),
     T("1929: the 124 m Royal York Hotel becomes the city's tallest building",
       "1929: 124 metrelik Royal York Oteli şehrin en yüksek binası olur"),
     pop=PI(1929, 1938.9), cam=cam(ROYALYORK, 2.6, 0.002)),
 seg(1939, 1953.9, 15, CA, TOR, T("An Airport on the Island", "Adada Bir Havalimanı"),
     T("1939: Port George VI Island Airport opens on Toronto Island",
       "1939: Toronto Adası'nda Port George VI Ada Havalimanı açılır"),
     pop=PI(1939, 1953.9), cam=(43.6300, -79.3900, 6.0)),
 seg(1954, 1954.24, 16, CA, TOR, T("Metropolitan Toronto", "Metropoliten Toronto"),
     T("1954: the city and its suburbs form Metro Toronto; counter now shows today's city area",
       "1954: şehir ve banliyöleri Metro Toronto'yu kurar; sayaç artık bugünkü şehir alanını gösterir"),
     pop=PI(1954, 1954.24), cam=(43.7000, -79.3900, 30.0), chapter=T("Metro Toronto", "Metro Toronto")),
 seg(1954.24, 1954.7, 16, CA, TOR, T("Canada's First Subway", "Kanada'nın İlk Metrosu"),
     T("30 March 1954: the Yonge subway opens, 7.4 km from Union to Eglinton",
       "30 Mart 1954: Yonge metrosu Union'dan Eglinton'a 7,4 km olarak açılır"),
     pop=PI(1954.24, 1954.7), cam=(43.6750, -79.3880, 12.0)),
 seg(1954.7, 1960.9, 16, CA, TOR, T("Hurricane Hazel", "Hazel Kasırgası"),
     T("1954: Hurricane Hazel floods the river valleys and kills 81 people",
       "1954: Hazel Kasırgası nehir vadilerini sular altında bırakır, 81 kişi ölür"),
     pop=PI(1954.7, 1960.9), cam=(43.7100, -79.4200, 26.0)),
 seg(1961, 1964.9, 14, CA, TOR, T("The Expressways", "Otoyollar"),
     T("Late 1950s–early 1960s: the Gardiner and Don Valley expressways are built",
       "1950'lerin sonu–1960'ların başı: Gardiner ve Don Vadisi otoyolları yapılır"),
     pop=PI(1961, 1964.9), cam=(43.6600, -79.3700, 12.0)),
 seg(1965, 1966.1, 17, CA, TOR, T("A New City Hall", "Yeni Belediye Binası"),
     T("13 September 1965: Viljo Revell's new City Hall opens on Queen Street",
       "13 Eylül 1965: Viljo Revell'in yeni Belediye Binası Queen Caddesi'nde açılır"),
     pop=PI(1965, 1966.1), cam=cam(CITYHALL, 2.4, 0.002), chapter=T("The Skyline Rises", "Silüet Yükseliyor")),
 seg(1966.1, 1966.99, 14, CA, TOR, T("Across the Viaduct", "Viyadüğün Altından"),
     T("26 February 1966: the Bloor–Danforth subway runs on the viaduct's lower deck",
       "26 Şubat 1966: Bloor–Danforth metrosu viyadüğün alt katından geçer"),
     pop=PI(1966.1, 1966.99), cam=cam(VIADUCT, 4.0, 0.004)),
 seg(1967, 1972.9, 15, CA, TOR, T("Towers of the Banks", "Bankaların Kuleleri"),
     T("1967: the 223 m TD Bank Tower; 1972: Commerce Court West, 239 m",
       "1967: 223 metrelik TD Bank Kulesi; 1972: 239 metrelik Commerce Court West"),
     pop=PI(1967, 1972.9), cam=cam(TDT, 3.0, 0.003)),
 seg(1973, 1975.3, 18, CA, TOR, T("The CN Tower Rises", "CN Kulesi Yükseliyor"),
     T("6 February 1973: work begins; 2 April 1975: the tower is topped off",
       "6 Şubat 1973: inşaat başlar; 2 Nisan 1975: kulenin tepesi tamamlanır"),
     pop=PI(1973, 1975.3), cam=cam(CNT, 3.4, 0.003)),
 seg(1975.3, 1976.45, 15, CA, TOR, T("First Canadian Place", "First Canadian Place"),
     T("5 June 1975: the 298 m First Canadian Place — Canada's tallest building for 50 years",
       "5 Haziran 1975: 298 m'lik First Canadian Place — 50 yıl Kanada'nın en yüksek binası"),
     pop=PI(1975.3, 1976.45), cam=cam(FCP, 3.0, 0.003)),
 seg(1976.45, 1988.9, 18, CA, TOR, T("553 Metres", "553 Metre"),
     T("26 June 1976: the 553.3 m CN Tower opens — the world's tallest free-standing structure",
       "26 Haziran 1976: 553,3 m'lik CN Kulesi açılır — dünyanın en yüksek serbest yapısı"),
     pop=PI(1976.45, 1988.9), cam=cam(CNT, 5.0, 0.006)),
 seg(1989, 1997.9, 16, CA, TOR, T("SkyDome", "SkyDome"),
     T("3 June 1989: SkyDome opens — the first stadium with a fully retractable motorized roof",
       "3 Haziran 1989: SkyDome açılır — tamamen açılıp kapanan motorlu çatılı ilk stadyum"),
     pop=PI(1989, 1997.9), cam=cam(DOME, 3.0, 0.003)),
 seg(1998, 2009.9, 16, CA, TOR, T("One City", "Tek Şehir"),
     T("1 January 1998: Metro and its six municipalities merge into one City of Toronto",
       "1 Ocak 1998: Metro ve altı belediyesi tek bir Toronto Şehri'nde birleşir"),
     pop=PI(1998, 2009.9), cam=(43.7200, -79.3900, 34.0), chapter=T("Toronto Today", "Bugünün Toronto'su")),
 seg(2010, 2024.9, 16, CA, TOR, T("A City of Towers", "Kuleler Şehri"),
     T("2011–2021: the city grows from 2,615,060 to 2,794,356 people",
       "2011–2021: şehrin nüfusu 2.615.060'tan 2.794.356'ya çıkar"),
     pop=PI(2010, 2024.9), cam=(43.6500, -79.3850, 7.0)),
 seg(2025, 2026, 26, TODAY, TOR, T("Toronto Today", "Bugünün Toronto'su"),
     T("From ten blocks by the lake in 1793 to 2,794,356 people at the 2021 census",
       "1793'te göl kıyısındaki on bloktan 2021 sayımında 2.794.356 kişiye"),
     pop=PI(2025, 2026), cam=(43.6900, -79.3900, 32.0)),
]

# ------------------------------------------------------------------ districts (all ≈, see research.md)
OLDTOWN = R(800, 1300, -150, 140)
NEWTOWN = R(-1400, 800, -380, 260)
CITY1834 = R(-2300, 1750, -450, 1100)
VICT = R(-3200, 1950, -560, 2700)
EAST = [G(2000, -100), G(4800, 300), G(5200, 2700), G(2050, 2700)]
WEST = [G(-6800, -1400), G(-3200, -560), G(-3200, 2700), G(-6800, 2700)]
NORTH = R(-5000, 2400, 2700, 6800)
EASTDON = [G(5200, 300), G(9000, 900), G(9000, 4000), G(2400, 4000), G(2400, 2700), G(5200, 2700)]
CITYLIMIT = [(43.5810, -79.5420), (43.6200, -79.5480), (43.7480, -79.6400), (43.8560, -79.1700), (43.8000, -79.1150),
             (43.7600, -79.1300), (43.6650, -79.3000), (43.6200, -79.3400), (43.6050, -79.4300), (43.5900, -79.5000)]
INNER = [G(-6800, -1400), G(9000, 900), G(9000, 6800), G(-6800, 6800)]
FIN = R(-700, 250, -380, 260)
CONDO = R(-2100, -350, -900, -430)
PORTIND = rect(43.6380, -79.3560, 43.6560, -79.3200)

# open spaces (≈)
ISLAND_PARK = [(43.6060, -79.4000), (43.6330, -79.4000), (43.6345, -79.3460), (43.6180, -79.3460)]
SPIT_PARK = [(43.6020, -79.3480), (43.6370, -79.3480), (43.6400, -79.3200), (43.6060, -79.3200)]
HIGH_PARK = [(43.6380, -79.4740), (43.6560, -79.4740), (43.6560, -79.4560), (43.6380, -79.4560)]
QUEENS_PARK = [G(-1150, 1950), G(-850, 1950), G(-850, 2350), G(-1150, 2350)]
DON_VALLEY = [(43.6600, -79.3590), (43.6800, -79.3640), (43.7050, -79.3560), (43.7250, -79.3400), (43.7230, -79.3330),
              (43.7020, -79.3490), (43.6800, -79.3580), (43.6600, -79.3530)]
HUMBER_V = [(43.6350, -79.4770), (43.6700, -79.4980), (43.7100, -79.5150), (43.7080, -79.5050), (43.6700, -79.4900), (43.6360, -79.4700)]
EXHIB = [(43.6300, -79.4280), (43.6350, -79.4280), (43.6370, -79.4100), (43.6320, -79.4100)]
ROUILLE_SITE = rect(ROUILLE[0] - 0.0012, ROUILLE[1] - 0.0016, ROUILLE[0] + 0.0012, ROUILLE[1] + 0.0016)

districts = [
 {"name": "Town of York, ten blocks (≈)", "style": "georgian", "poly": L(OLDTOWN), "from": 1793.7, "to": 1812, "density": 0.55, "grain_m": 48,
  "grid_deg": 16, "grow_from": list(G(1050, -50))},
 {"name": "York extended west to Peter Street (≈)", "style": "georgian", "poly": L(NEWTOWN), "holes": [L(OLDTOWN)], "from": 1797, "to": 1834,
  "density": 0.6, "grain_m": 50, "grid_deg": 16, "grow_from": list(G(700, 0))},
 {"name": "City of 1834–1850 (≈)", "style": "georgian", "poly": L(CITY1834), "holes": [L(NEWTOWN), L(OLDTOWN)], "from": 1830, "to": 1855,
  "density": 0.65, "grain_m": 55, "grid_deg": 16, "grow_from": list(G(0, 0))},
 {"name": "Victorian city to Bloor (≈)", "style": "victorian", "poly": L(VICT), "holes": [L(CITY1834), L(QUEENS_PARK)], "from": 1850, "to": 1895,
  "density": 0.75, "grain_m": 65, "grid_deg": 16, "grow_from": list(G(0, 300))},
 {"name": "Parkdale and the west (≈)", "style": "victorian", "poly": L(WEST), "holes": [L(HIGH_PARK), L(EXHIB), L(ROUILLE_SITE)], "from": 1880,
  "to": 1925, "density": 0.65, "grain_m": 75, "grid_deg": 16, "grow_from": list(G(-3200, 0))},
 {"name": "Riverdale, east of the Don (≈)", "style": "victorian", "poly": L(EAST), "from": 1880, "to": 1920, "density": 0.65, "grain_m": 75,
  "grid_deg": 16, "grow_from": list(G(2100, 300))},
 {"name": "The Annex to North Toronto (≈)", "style": "victorian", "poly": L(NORTH), "from": 1885, "to": 1935, "density": 0.6, "grain_m": 85,
  "grid_deg": 16, "grow_from": list(G(-500, 2700))},
 {"name": "East York, Danforth, the Beaches (≈)", "style": "suburb", "poly": L(EASTDON), "holes": [L(DON_VALLEY)], "from": 1905, "to": 1945,
  "density": 0.55, "grain_m": 110, "grid_deg": 16, "grow_from": list(G(2500, 1500))},
 {"name": "Waterfront rail and industry (≈)", "style": "industrial", "poly": L(R(-2400, 1950, -900, -300)), "from": 1866, "to": 1930,
  "density": 0.45, "grain_m": 110, "grid_deg": 16, "grow_from": list(G(0, -500))},
 {"name": "Port Lands industry (≈)", "style": "industrial", "poly": L(PORTIND), "from": 1925, "to": 1960, "density": 0.4, "grain_m": 140,
  "grid_deg": 0, "grow_from": [43.6480, -79.3500]},
 {"name": "Postwar suburbs of Metro (≈)", "style": "suburb", "poly": L(CITYLIMIT),
  "holes": [L(INNER), L(DON_VALLEY), L(HUMBER_V), L(ISLAND_PARK), L(SPIT_PARK)], "from": 1946, "to": 1990,
  "density": 0.5, "grain_m": 170, "grid_deg": 16, "grow_from": list(G(0, 5000))},
 {"name": "Financial district towers (≈)", "style": "highrise", "poly": L(FIN), "from": 1962, "to": 2020, "density": 0.6, "grain_m": 70,
  "grid_deg": 16, "grow_from": list(G(-200, 0))},
 {"name": "Railway lands condos (≈)", "style": "highrise", "poly": L(CONDO), "from": 1995, "to": 2022, "density": 0.55, "grain_m": 80,
  "grid_deg": 16, "grow_from": list(G(-1200, -650))},
]

walls = []
bridges = [
 {"name": "Prince Edward Viaduct (≈ ends)", "path": L([G(*(lambda uv: (uv[0] - 247, uv[1]))(UV(VIADUCT))),
                                                     G(*(lambda uv: (uv[0] + 247, uv[1]))(UV(VIADUCT)))]),
  "built": 1918.8, "style": "iron", "width_m": 26},
]

roads = [
 {"name": "Yonge Street (≈)", "path": L([G(0, -350), G(0, 3000), G(0, 7500), (43.7800, -79.4150)]), "from": 1796, "kind": "road", "width_m": 18,
  "draw_s": 4},
 {"name": "Kingston Road east (≈)", "path": L([G(1300, 0), G(2400, 200), G(4500, 650), (43.6800, -79.2900)]), "from": 1800, "kind": "road",
  "width_m": 16},
 {"name": "Lakeshore railway (≈)", "path": L([G(-5200, -1180), G(-3200, -720), G(-1500, -460), G(-320, -390), G(1400, -120), G(2000, -60)]),
  "from": 1855, "kind": "rail", "width_m": 22},
 {"name": "Northern railway (≈)", "path": L([G(-1500, -460), G(-2600, 1200), G(-3400, 4200)]), "from": 1853, "kind": "rail", "width_m": 18},
 {"name": "Yonge subway (≈)", "path": L([UNION, G(0, -200), G(0, 2700), G(0, 6750)]), "from": 1954.24, "kind": "rail", "width_m": 14},
 {"name": "Bloor–Danforth subway (≈)", "path": L([(43.6560, -79.4600), G(*(lambda uv: (uv[0] - 247, uv[1]))(UV(VIADUCT))),
                                                    G(*(lambda uv: (uv[0] + 247, uv[1]))(UV(VIADUCT))), (43.6870, -79.3130)]),
  "from": 1966.15, "kind": "rail", "width_m": 14},
 {"name": "Gardiner Expressway (≈)", "path": L([(43.6320, -79.4750), G(-4500, -1000), G(-2300, -700), G(-320, -560), G(1600, -300), (43.6520, -79.3560)]),
  "from": 1958, "kind": "motorway", "width_m": 30, "draw_s": 4},
 {"name": "Don Valley Parkway (≈)", "path": L([(43.6520, -79.3560), (43.6800, -79.3610), (43.7050, -79.3530), (43.7300, -79.3350), (43.7700, -79.3350)]),
  "from": 1961, "kind": "motorway", "width_m": 28, "draw_s": 4},
]

C_ = lambda w, r: {"wall": w, "roof": r}
BRICK = "#a8573e"
p = lambda pt: [round(pt[0], 5), round(pt[1], 5)]
landmarks = [
 {"type": "fort", "name": T("Fort Rouillé", "Rouillé Kalesi"), "at": p(ROUILLE), "built": 1750.6, "removed": 1759.6, "rise_s": 6,
  "size_m": [55, 55, 6], "scale": 1.5, "colors": {"wall": "#8a6a48"}},
 {"type": "fort", "name": T("Fort York (1793)", "York Kalesi (1793)"), "at": p(FORTYORK), "built": 1793.56, "removed": 1813.32, "rise_s": 6,
  "size_m": [160, 110, 7], "scale": 1.4, "rot_deg": -16, "colors": {"wall": "#8a6a48"}},
 {"type": "fort", "name": T("Fort York", "York Kalesi"), "at": p(FORTYORK), "built": 1813.65, "rise_s": 8,
  "size_m": [200, 130, 8], "scale": 1.4, "rot_deg": -16, "colors": {"wall": "#b9ad94"}},
 {"type": "parliament", "name": T("First parliament buildings (≈)", "İlk meclis binaları (≈)"), "at": p(PARL1), "built": 1797, "removed": 1813.4,
  "rise_s": 6, "size_m": [40, 16, 9], "scale": 1.4, "rot_deg": -16, "colors": C_(BRICK, "#4f5a60")},
 {"type": "parliament", "name": T("Second parliament building (≈)", "İkinci meclis binası (≈)"), "at": p(PARL1), "built": 1819, "removed": 1824.4,
  "rise_s": 6, "size_m": [40, 16, 10], "scale": 1.4, "rot_deg": -16, "colors": C_(BRICK, "#4f5a60")},
 {"type": "parliament", "name": T("Third parliament building (≈)", "Üçüncü meclis binası (≈)"), "at": p(PARL3), "built": 1830.5, "removed": 1893.3,
  "rise_s": 8, "size_m": [90, 30, 14], "scale": 1.3, "rot_deg": -16, "colors": C_(BRICK, "#4f5a60")},
 {"type": "church", "name": T("St. James' Church", "St. James Kilisesi"), "at": p(STJAMES), "built": 1807, "removed": 1849.28, "rise_s": 6,
  "size_m": [30, 14, 12], "scale": 1.4, "rot_deg": -16, "colors": C_("#d9cdb5", "#5a4a44")},
 {"type": "cathedral", "name": T("St. James' Cathedral", "St. James Katedrali"), "at": p(STJAMES), "built": 1850.5, "rise_s": 10,
  "size_m": [60, 28, 22], "scale": 1.3, "rot_deg": -16, "colors": C_("#d6c9a8", "#5f666f")},
 {"type": "spire_tower", "name": T("St. James' spire", "St. James kulesi"), "at": p(G(*(lambda uv: (uv[0], uv[1] - 30))(UV(STJAMES)))),
  "built": 1873, "rise_s": 8, "size_m": [10, 10, 93], "colors": C_("#d6c9a8", "#5f666f")},
 {"type": "box", "name": T("St. Lawrence Market (≈)", "St. Lawrence Pazarı (≈)"), "at": p(MARKET), "built": 1844, "rise_s": 6,
  "size_m": [90, 45, 12], "scale": 1.3, "rot_deg": -16, "colors": C_(BRICK, "#5f666f")},
 {"type": "box", "name": T("St. Lawrence Hall (≈)", "St. Lawrence Salonu (≈)"), "at": p(STLHALL), "built": 1850.3, "rise_s": 6,
  "size_m": [40, 30, 16], "scale": 1.3, "rot_deg": -16, "colors": C_("#e3dccb", "#5f666f")},
 {"type": "palace", "name": T("Ontario Legislative Building", "Ontario Yasama Binası"), "at": p(LEGIS), "built": 1886, "rise_s": 20,
  "size_m": [150, 70, 22], "scale": 1.3, "rot_deg": -16, "colors": C_("#b8826e", "#5f666f")},
 {"type": "box", "name": T("Old City Hall", "Eski Belediye Binası"), "at": p(OLDCH), "built": 1889, "rise_s": 30,
  "size_m": [90, 85, 24], "scale": 1.2, "rot_deg": -16, "colors": C_("#c9a98a", "#4f5a60")},
 {"type": "clocktower", "name": T("Old City Hall tower", "Eski Belediye Binası kulesi"), "at": p(G(*(lambda uv: (uv[0], uv[1] - 45))(UV(OLDCH)))),
  "built": 1895, "rise_s": 10, "size_m": [14, 14, 104], "colors": C_("#c9a98a", "#4f5a60")},
 {"type": "station", "name": T("Union Station", "Union İstasyonu"), "at": p(UNION), "built": 1914, "rise_s": 40,
  "size_m": [229, 60, 30], "rot_deg": -16, "colors": C_("#e3dccb", "#5f666f")},
 {"type": "skyscraper", "name": T("Royal York Hotel (≈ position)", "Royal York Oteli (≈ konum)"), "at": p(ROYALYORK), "built": 1928.2, "rise_s": 8,
  "size_m": [70, 40, 124], "rot_deg": -16, "colors": {"wall": "#c9b896"}},
 {"type": "skyscraper", "name": T("Commerce Court North (≈ position)", "Commerce Court North (≈ konum)"), "at": p(CCOURT), "built": 1930.2,
  "rise_s": 8, "size_m": [35, 35, 145], "rot_deg": -16, "colors": {"wall": "#cdbf9f"}},
 {"type": "skyscraper", "name": T("Toronto City Hall, east tower", "Toronto Belediye Binası, doğu kulesi"),
  "at": p(G(*(lambda uv: (uv[0] + 60, uv[1] + 20))(UV(CITYHALL)))), "built": 1962, "rise_s": 10, "size_m": [70, 20, 100],
  "rot_deg": -16, "colors": {"wall": "#d8d8d2"}},
 {"type": "skyscraper", "name": T("Toronto City Hall, west tower", "Toronto Belediye Binası, batı kulesi"),
  "at": p(G(*(lambda uv: (uv[0] - 60, uv[1] + 20))(UV(CITYHALL)))), "built": 1962, "rise_s": 10, "size_m": [70, 20, 80],
  "rot_deg": -16, "colors": {"wall": "#d8d8d2"}},
 {"type": "skyscraper", "name": T("TD Bank Tower (≈ position)", "TD Bank Kulesi (≈ konum)"), "at": p(TDT), "built": 1965.5, "rise_s": 10,
  "size_m": [55, 35, 223], "rot_deg": -16, "colors": {"wall": "#2e2f33"}},
 {"type": "skyscraper", "name": T("Commerce Court West (≈ position)", "Commerce Court West (≈ konum)"),
  "at": p(G(*(lambda uv: (uv[0] - 10, uv[1] - 70))(UV(CCOURT)))), "built": 1970.5, "rise_s": 10, "size_m": [50, 50, 239],
  "rot_deg": -16, "colors": {"wall": "#8f9599"}},
 {"type": "spire_tower", "name": T("CN Tower", "CN Kulesi"), "at": p(CNT), "built": 1973.1, "rise_s": 18, "size_m": [40, 40, 553],
  "colors": C_("#cfcfc8", "#9a9a94")},
 {"type": "skyscraper", "name": T("First Canadian Place", "First Canadian Place"), "at": p(FCP), "built": 1973.5, "rise_s": 12,
  "size_m": [55, 55, 298], "rot_deg": -16, "colors": {"wall": "#e6e6e0"}},
 {"type": "dome_arena", "name": T("SkyDome / Rogers Centre", "SkyDome / Rogers Centre"), "at": p(DOME), "built": 1986.75, "rise_s": 14,
  "size_m": [210, 210, 60], "colors": C_("#d8d8d2", "#c9cdd0")},
]

fires = [
 {"year": 1849.27, "poly": L(R(340, 640, 10, 140)), "duration_s": 6, "plumes": 4},
 {"year": 1904.3, "poly": L(R(-420, -60, -330, -110)), "duration_s": 8, "plumes": 6},
]
smoke = [
 {"at": p(ROUILLE), "from": 1759.5, "to": 1759.7, "scale": 0.8},
 {"at": p(FORTYORK), "from": 1813.31, "to": 1813.36, "scale": 1.4},
 {"at": p(PARL1), "from": 1813.4, "to": 1813.45, "scale": 1.0},
]
camps = [
 {"poly": L(rect(43.6330, -79.4300, 43.6380, -79.4180)), "from": 1813.31, "to": 1813.35, "count": 120},
]
open_spaces = [
 {"name": "Toronto Island (≈)", "poly": L(ISLAND_PARK)},
 {"name": "Leslie Street Spit (≈)", "poly": L(SPIT_PARK)},
 {"name": "High Park (≈)", "poly": L(HIGH_PARK)},
 {"name": "Queen's Park (≈)", "poly": L(QUEENS_PARK)},
 {"name": "Don Valley (≈)", "poly": L(DON_VALLEY)},
 {"name": "Humber Valley (≈)", "poly": L(HUMBER_V)},
 {"name": "Exhibition grounds / Fort Rouillé site (≈)", "poly": L(EXHIB)},
]
timed_water = [
 {"name": "Eastern Gap (cut by the 1858 storm)", "poly": L(EASTERN_GAP), "from": 1858.28, "to": None},
] + FILL

labels = [
 {"text": T("LAKE ONTARIO", "ONTARIO GÖLÜ"), "at": [43.5900, -79.3900], "kind": "water", "from": 1650},
 {"text": T("Humber River", "Humber Nehri"), "at": [43.6450, -79.4800], "kind": "water", "from": 1650, "to": 1760},
 {"text": T("TORONTO CARRYING-PLACE", "TORONTO TAŞIMA YOLU"), "at": [43.6900, -79.5000], "kind": "region", "from": 1650, "to": 1719.9},
 {"text": T("MISSISSAUGA COUNTRY", "MISSISSAUGA TOPRAKLARI"), "at": [43.6800, -79.4200], "kind": "region", "from": 1687, "to": 1719.9},
 {"text": T("Fort Rouillé", "Rouillé Kalesi"), "at": p(ROUILLE), "kind": "place", "from": 1750, "to": 1759.9},
 {"text": T("THE PENINSULA", "YARIMADA"), "at": [43.6230, -79.3700], "kind": "region", "from": 1760, "to": 1857.9},
 {"text": T("TORONTO HARBOUR", "TORONTO LİMANI"), "at": [43.6365, -79.3780], "kind": "water", "from": 1787, "to": 1925},
 {"text": T("Fort York", "York Kalesi"), "at": p(FORTYORK), "kind": "place", "from": 1793, "to": 1793.6},
 {"text": T("YORK", "YORK"), "at": p(G(1050, 250)), "kind": "region", "from": 1793.65, "to": 1796.99},
 {"text": T("Parliament", "Meclis"), "at": p(PARL1), "kind": "place", "from": 1797, "to": 1806.9},
 {"text": T("St. James'", "St. James"), "at": p(STJAMES), "kind": "place", "from": 1807, "to": 1812.9},
 {"text": T("Fort York", "York Kalesi"), "at": p(FORTYORK), "kind": "place", "from": 1813, "to": 1819.9},
 {"text": T("Parliament", "Meclis"), "at": p(PARL1), "kind": "place", "from": 1820, "to": 1831.9},
 {"text": T("YONGE STREET", "YONGE CADDESİ"), "at": p(G(-180, 4500)), "kind": "region", "from": 1837, "to": 1846.9},
 {"text": T("Market Block", "Pazar Bloğu"), "at": p(G(500, 80)), "kind": "place", "from": 1849, "to": 1849.5},
 {"text": T("St. Lawrence Hall", "St. Lawrence Salonu"), "at": p(STLHALL), "kind": "place", "from": 1849.5, "to": 1852.9},
 {"text": T("Eastern Gap", "Doğu Boğazı"), "at": [43.6300, -79.3520], "kind": "place", "from": 1858, "to": 1858.6},
 {"text": T("TORONTO ISLAND", "TORONTO ADASI"), "at": [43.6200, -79.3800], "kind": "region", "from": 1858.3},
 {"text": T("ASHBRIDGE'S BAY", "ASHBRIDGE KOYU"), "at": [43.6480, -79.3330], "kind": "water", "from": 1793, "to": 1921},
 {"text": T("St. James' Cathedral", "St. James Katedrali"), "at": p(STJAMES), "from": 1873, "to": 1882.9, "lift_m": 110},
 {"text": T("YORKVILLE", "YORKVILLE"), "at": p(G(-500, 2900)), "kind": "region", "from": 1883, "to": 1888},
 {"text": T("PARKDALE", "PARKDALE"), "at": p(G(-4500, 0)), "kind": "region", "from": 1888, "to": 1892.9},
 {"text": T("Legislative Building", "Yasama Binası"), "at": p(LEGIS), "kind": "place", "from": 1893, "to": 1898.9},
 {"text": T("Old City Hall", "Eski Belediye Binası"), "at": p(OLDCH), "from": 1899, "to": 1903.9, "lift_m": 125},
 {"text": T("NORTH TORONTO", "KUZEY TORONTO"), "at": p(G(0, 6000)), "kind": "region", "from": 1905, "to": 1911.9},
 {"text": T("Don River", "Don Nehri"), "at": [43.6640, -79.3580], "kind": "place", "from": 1912, "to": 1917.9},
 {"text": T("Prince Edward Viaduct", "Prince Edward Viyadüğü"), "at": p(VIADUCT), "kind": "place", "from": 1918, "to": 1918.99},
 {"text": T("PORT LANDS", "PORT LANDS"), "at": p(PORTL), "kind": "region", "from": 1922, "to": 1926.9},
 {"text": T("Union Station", "Union İstasyonu"), "at": p(UNION), "kind": "place", "from": 1927, "to": 1928.9},
 {"text": T("Royal York", "Royal York"), "at": p(ROYALYORK), "from": 1929, "to": 1938.9, "lift_m": 150},
 {"text": T("METROPOLITAN TORONTO", "METROPOLİTEN TORONTO"), "at": [43.7500, -79.3900], "kind": "region", "from": 1954, "to": 1954.24},
 {"text": T("Eglinton", "Eglinton"), "at": p(G(0, 6750)), "kind": "place", "from": 1954.24, "to": 1954.7},
 {"text": T("Union", "Union"), "at": p(UNION), "kind": "place", "from": 1954.24, "to": 1954.7},
 {"text": T("New City Hall", "Yeni Belediye Binası"), "at": p(CITYHALL), "from": 1965, "to": 1966.1, "lift_m": 125},
 {"text": T("CN Tower", "CN Kulesi"), "at": p(CNT), "from": 1975.3, "to": 1988.9, "lift_m": 580},
 {"text": T("First Canadian Place", "First Canadian Place"), "at": p(FCP), "from": 1975.3, "to": 1976.45, "lift_m": 320},
 {"text": T("SkyDome", "SkyDome"), "at": p(DOME), "kind": "place", "from": 1989, "to": 1997.9},
 {"text": T("SCARBOROUGH", "SCARBOROUGH"), "at": [43.7750, -79.2300], "kind": "region", "from": 1998, "to": 2009.9},
 {"text": T("ETOBICOKE", "ETOBICOKE"), "at": [43.6600, -79.5500], "kind": "region", "from": 1998, "to": 2009.9},
 {"text": T("NORTH YORK", "NORTH YORK"), "at": [43.7600, -79.4200], "kind": "region", "from": 1998, "to": 2009.9},
]

city = {
 "slug": "toronto", "seed": 1793, "long_ok": True,
 "name": T("Toronto", "Toronto"), "intro": T("From 1793 to Today", "1793'ten Bugüne"), "intro_seconds": 4.5,
 "geo": {"bbox": [43.50, -79.72, 43.92, -79.02], "cell_m": 110, "core_bbox": [43.600, -79.440, 43.690, -79.300], "core_cell_m": 30,
         "rivers_keep": ["Don River", "Humber River"]},
 "view": {"azimuth_deg": 0, "pitch_deg": 46, "fov": 34},
 "render": {"vertical_exaggeration": 1.6},
 "segments": S,
 "districts": districts, "walls": walls, "bridges": bridges, "roads": roads, "landmarks": landmarks,
 "fires": fires, "camps": camps, "smoke": smoke, "open_spaces": open_spaces, "timed_water": timed_water, "labels": labels,
 "youtube": {
  "title": T("Toronto (3D Timelapse)", "Toronto (3D Timelapse)"),
  "description": T(
   "The Toronto Carrying-Place on the Humber, a French fort burned in 1759, and in 1793 the Town of York: ten blocks by the "
   "lake. Watch Toronto grow from a frontier capital burned in the War of 1812 into a Victorian railway city, rebuild after "
   "the fires of 1849 and 1904, push its shoreline into Lake Ontario on made land, and rise into Canada's largest city: Fort "
   "York, St. James' Cathedral, St. Lawrence Hall, Toronto Island, Old City Hall, Queen's Park, the Bloor Viaduct, Union "
   "Station, the CN Tower and SkyDome, with the year and the population on screen.",
   "Humber kıyısındaki Toronto Taşıma Yolu, 1759'da yakılan bir Fransız kalesi ve 1793'te York Kasabası: göl kıyısında on "
   "blok. Toronto'nun 1812 Savaşı'nda yakılan bir sınır başkentinden Viktorya dönemi demiryolu şehrine büyümesini, 1849 ve "
   "1904 yangınlarından sonra yeniden kurulmasını, kıyısını yapay toprakla Ontario Gölü'ne doğru ilerletmesini ve Kanada'nın "
   "en büyük şehrine dönüşmesini izleyin: York Kalesi, St. James Katedrali, St. Lawrence Salonu, Toronto Adası, Eski "
   "Belediye Binası, Queen's Park, Bloor Viyadüğü, Union İstasyonu, CN Kulesi ve SkyDome; yıl ve nüfus ekranda."),
  "tags": ["toronto history", "history of toronto", "toronto", "cn tower", "fort york", "town of york", "3d timelapse", "city evolution",
           "how toronto grew", "toronto timelapse", "canadian history", "urban history", "war of 1812", "lake ontario"],
  "hashtags": ["#Toronto", "#History", "#Timelapse"],
  "playlist": T("Cities of North America", "Kuzey Amerika Şehirleri"),
  "playlist_desc": T("North American cities rebuilt in 3D, from the first house to the skyline.",
                     "Kuzey Amerika şehirleri 3D olarak, ilk evden siluete."),
  "thumb": {"line1": T("Toronto", "Toronto"), "line2": T("1793 → TODAY", "1793 → BUGÜN"),
            "line3": T("From ten blocks to megacity", "On bloktan dev şehre"),
            "extra": "&mood=golden&pitch=30&az=0&cam=43.6450,-79.3850,6.0"},
 },
 "sources": json.load(open(os.path.join(HERE, "_sources.json"))),
}
total = sum(s_["seconds"] for s_ in S)
mins = round(total / 60)
years = 2026 - 1793
city["intro"] = T(f"{years} Years in {mins} Minutes", f"{mins} Dakikada {years} Yıl")
city["youtube"]["title"] = T(f"Toronto: {years} Years in {mins} Minutes (3D Timelapse)",
                             f"Toronto: {mins} Dakikada {years} Yıl (3D Timelapse)")
json.dump(city, open(os.path.join(HERE, "city.json"), "w"), ensure_ascii=False, indent=1)
print("segments", len(S), "duration", total, "s =", f"{total // 60}:{total % 60:02d}",
      "| fill polys", len(FILL), "(geo.json present)" if HAVE_GEO else "(no geo.json yet: fills left out)")
