"""Builds cities/edinburgh/city.json. Every on-screen date/figure is from research.md (sources listed there).
Run: python3 cities/edinburgh/_build.py
Street lines, district outlines, open spaces, camps and the Leith fortification are simplified traces between sourced
points (marked ≈ in research.md)."""
import json, math, os

T = lambda en, tr: {"en": en, "tr": tr}
HERE = os.path.dirname(os.path.abspath(__file__))
KX = 111.32 * math.cos(math.radians(55.95)); KZ = 110.574


def L(pts):
    return [[round(a, 5), round(b, 5)] for a, b in pts]


def circle(c, r_m, n=12):
    return [(c[0] + r_m / 1000 / KZ * math.sin(2 * math.pi * i / n), c[1] + r_m / 1000 / KX * math.cos(2 * math.pi * i / n)) for i in range(n)]


def strip(path, hw_m):
    """Polygon of half-width hw_m around a polyline (simple offset, fine for gentle bends)."""
    left, right = [], []
    for i, (la, lo) in enumerate(path):
        a = path[max(i - 1, 0)]; b = path[min(i + 1, len(path) - 1)]
        dx = (b[1] - a[1]) * KX; dz = (b[0] - a[0]) * KZ; n = math.hypot(dx, dz)
        nx, nz = -dz / n, dx / n                     # left normal (km)
        left.append((la + nz * hw_m / 1000 / KZ, lo + nx * hw_m / 1000 / KX))
        right.append((la - nz * hw_m / 1000 / KZ, lo - nx * hw_m / 1000 / KX))
    return left + right[::-1]


# ------------------------------------------------------------------ published coordinates (research.md)
CASTLE = (55.94861, -3.20083); GILES = (55.94947, -3.19150); NETHERBOW = (55.95065, -3.18430); PALACE = (55.95250, -3.17250)
ABBEY = (55.95285, -3.17220); PARL = (55.95220, -3.17470); NBRIDGE = (55.95187, -3.18840); SBRIDGE = (55.94874, -3.18683)
WAVERLEY = (55.95210, -3.18930); SCOTT = (55.95238, -3.19326); NELSON = (55.95433, -3.18258); NATMON = (55.95510, -3.18170)
OLDCOL = (55.94740, -3.18730); ARTHUR = (55.94417, -3.16194)
SHORE = (55.97640, -3.17000)          # ≈ Water of Leith mouth (checked on the map)

# ------------------------------------------------------------------ Old Town geometry (≈ between sourced points)
ROYAL_MILE = [(55.94890, -3.19720), (55.94925, -3.19400), (GILES[0] + 0.00025, GILES[1]), (55.94998, -3.18800), NETHERBOW]
CANONGATE = [NETHERBOW, (55.95120, -3.18050), (55.95180, -3.17700), (55.95235, -3.17420)]
COWGATE = [(55.94730, -3.19850), (55.94755, -3.19350), (55.94820, -3.18950), (55.94880, -3.18550), (55.94930, -3.18300)]
BURGH = strip(ROYAL_MILE, 95)
CANON = strip(CANONGATE, 85)
COWG = strip(COWGATE, 60)
FLODDEN = [(55.94800, -3.19900), (55.94750, -3.19798), (55.94690, -3.19850), (55.94622, -3.19698), (55.94660, -3.19332),
           (55.94643, -3.19111), (55.94660, -3.18800), (55.94841, -3.18236), (55.94960, -3.18250), (NETHERBOW[0], NETHERBOW[1] + 0.00010),
           (55.95150, -3.18380), (55.95150, -3.18850)]
FLODDEN_AREA = FLODDEN + [(55.95090, -3.19300), (55.95020, -3.19750), (55.94960, -3.19950)]
KINGS_WALL = [(55.94840, -3.19720), (55.94860, -3.19300), (55.94880, -3.18900), (55.94960, -3.18600), (55.95021, -3.18455), (55.95110, -3.18470)]
TELFER = [(55.94622, -3.19698), (55.94571, -3.19602), (55.94520, -3.19450), (55.94531, -3.19191), (55.94530, -3.18900), (55.94640, -3.18850)]
CASTLE_ROCK = circle(CASTLE, 190, 14)
SOUTHSIDE = [(55.94640, -3.19700), (55.94640, -3.18200), (55.94840, -3.18100), (55.94600, -3.17800), (55.94330, -3.17950),
             (55.94300, -3.19750)]
NOR_LOCH = [(55.94990, -3.20550), (55.95120, -3.20620), (55.95200, -3.19900), (55.95260, -3.19000), (55.95180, -3.18850),
            (55.95090, -3.19050), (55.95030, -3.19900)]
GARDENS = NOR_LOCH

# ------------------------------------------------------------------ New Town (grid ~20° north of east)
NT1 = [(55.95040, -3.20750), (55.95330, -3.19050), (55.95720, -3.19230), (55.95440, -3.20900)]
NT2 = [(55.95480, -3.20500), (55.95720, -3.19230), (55.96150, -3.19350), (55.95980, -3.20650)]
MORAY = [(55.95440, -3.20900), (55.95600, -3.20700), (55.95700, -3.21250), (55.95520, -3.21350)]
WESTEND = [(55.94850, -3.21900), (55.95040, -3.20750), (55.95440, -3.20900), (55.95520, -3.21350), (55.95100, -3.22200)]
CALTON_T = [(55.95500, -3.18650), (55.95700, -3.18100), (55.95700, -3.17400), (55.95560, -3.17550), (55.95420, -3.18200)]
CALTON_HILL = [(55.95380, -3.18450), (55.95560, -3.18500), (55.95620, -3.18050), (55.95480, -3.17800), (55.95360, -3.18100)]
HOLYROOD_PARK = [(55.95180, -3.17150), (55.95080, -3.16200), (55.94500, -3.14900), (55.93800, -3.15300), (55.93600, -3.16500),
                 (55.94000, -3.17200), (55.94600, -3.17550), (55.95000, -3.17400)]
MEADOWS = [(55.94300, -3.20000), (55.94300, -3.18300), (55.93950, -3.18400), (55.93900, -3.19900)]

# ------------------------------------------------------------------ Leith (≈)
LEITH_OLD = circle((SHORE[0] - 0.0015, SHORE[1] + 0.0005), 380, 12)
LEITH_FORT = circle((SHORE[0] - 0.0030, SHORE[1] + 0.0010), 430, 9)
LEITH_GEO = [(55.97900, -3.19500), (55.97950, -3.15500), (55.97000, -3.15000), (55.96400, -3.16500), (55.96500, -3.18500)]
WATER_OF_LEITH = [(55.95300, -3.21800), (55.95850, -3.20800), (55.96200, -3.19600), (55.96700, -3.18800), (55.97000, -3.18300),
                  (55.97350, -3.17600), (55.97640, -3.17050), (55.97950, -3.16950)]
# modern dock/harbour reclamation north of the old shore (≈): kept as sea so Leith sits on the shore in every era
OUTER_FORTH = [(55.98100, -3.23500), (55.98150, -3.20000), (55.98000, -3.18000), (55.97900, -3.16800), (55.97600, -3.15800),
               (55.97350, -3.15000), (55.97250, -3.14000), (55.99900, -3.14000), (55.99900, -3.23500)]
LEITH_WALK = [(55.95580, -3.18600), (55.96100, -3.18050), (55.96700, -3.17600), (55.97150, -3.17300)]

# ------------------------------------------------------------------ the later city (≈)
VICTORIAN = [(55.93200, -3.23000), (55.93200, -3.17800), (55.94000, -3.17600), (55.95300, -3.16000), (55.96200, -3.15200),
             (55.97200, -3.14600), (55.97900, -3.20500), (55.96500, -3.23500), (55.94500, -3.24000)]
SUBURBS = [(55.89000, -3.33000), (55.88500, -3.12000), (55.92000, -3.08000), (55.95000, -3.09000), (55.97500, -3.13000),
           (55.98200, -3.23000), (55.97000, -3.30000), (55.94000, -3.34000)]
OLD_CORE = FLODDEN_AREA

# ------------------------------------------------------------------ population (research.md)
POPS = [(1560, 10000), (1755, 57195), (1791, 81865), (1801, 82560), (1811, 102987), (1821, 138235), (1831, 161909), (1841, 166450),
        (1851, 193929), (1901, 303638), (1911, 320318), (1921, 420264), (1931, 439010), (1951, 466761), (2001, 448624), (2011, 476626),
        (2022, 514543), (2024.5, 530680), (2026, 530680)]


def P(y):
    for y0, p0 in POPS:
        if y == y0: return p0
    for (y0, p0), (y1, p1) in zip(POPS, POPS[1:]):
        if y0 <= y <= y1:
            v = p0 + (p1 - p0) * (y - y0) / (y1 - y0)
            return int(round(v, -2 if v < 100000 else -3))
    raise ValueError(y)
PI = lambda a, b: [P(a), P(b)]


def seg(frm, to, sec, era, city, title=None, sub=None, pop=None, cam=None, chapter=None):
    d = {"from": frm, "to": to, "seconds": sec, "era": era, "city_name": city}
    if title: d["title"] = title; d["sub"] = sub
    if pop is not None: d["population"] = pop
    if cam: d["camera"] = {"center": [cam[0], cam[1]], "dist_km": cam[2]}
    if chapter: d["chapter"] = chapter
    return d


PRE = T("Prehistory", "Tarih Öncesi"); IRON = T("Iron Age", "Demir Çağı"); GOD = T("Gododdin", "Gododdin")
NOR = T("Northumbria", "Northumbria"); SCO = T("Kingdom of Scotland", "İskoçya Krallığı"); WOI = T("Wars of Independence", "Bağımsızlık Savaşları")
GB = T("Great Britain", "Büyük Britanya"); VIC = T("Victorian Era", "Viktorya Dönemi"); MOD = T("Modern Era", "Modern Çağ")
DEV = T("Devolved Scotland", "Özerk İskoçya")
ROCK = T("Castle Rock", "Kale Kayası"); DIN = T("Din Eidyn", "Din Eidyn"); EDW = T("Edwinesburh", "Edwinesburh"); EDI = T("Edinburgh", "Edinburgh")
OT = (55.94980, -3.19000)

S = [
 seg(-1000, -501, 22, PRE, ROCK, T("A Volcanic Rock", "Volkanik Bir Kaya"),
     T("c. 1000 BC: people are already living on the Castle Rock", "MÖ ~1000: Kale Kayası'nda insanlar yaşamaktadır"),
     cam=(CASTLE[0] + 0.0010, CASTLE[1] + 0.0040, 4.0), chapter=T("The Rock", "Kaya")),
 seg(-500, 499, 18, IRON, ROCK, T("Hill Forts", "Tepe Kaleleri"),
     T("Iron Age: hill forts crown Arthur's Seat and the hills around it", "Demir Çağı: Arthur's Seat ve çevresindeki tepelerde kaleler yükselir"),
     cam=(55.94700, -3.18200, 5.5)),
 seg(500, 649, 20, GOD, DIN, T("Din Eidyn", "Din Eidyn"),
     T("c. AD 600: a Welsh poem names Din Eidyn, the Gododdin's fort on the rock", "MS ~600: Galce bir şiir, Gododdin'lerin kayadaki kalesi Din Eidyn'i anar"),
     cam=(CASTLE[0] + 0.0010, CASTLE[1] + 0.0030, 3.0)),
 seg(650, 853, 16, NOR, DIN, T("Northumbria", "Northumbria"),
     T("7th–10th centuries: the rock is part of the Anglian kingdom of Northumbria",
       "7.–10. yüzyıllar: kaya, Anglo kökenli Northumbria krallığının parçasıdır"),
     cam=(CASTLE[0] + 0.0010, CASTLE[1] + 0.0050, 4.0)),
 seg(854, 1057, 14, NOR, EDW, T("A New Name", "Yeni Bir Ad"),
     T("By AD 854 the name Din Eidyn has become Edwinesburh", "MS 854'e gelindiğinde Din Eidyn adı Edwinesburh olmuştur"),
     cam=(CASTLE[0] + 0.0010, CASTLE[1] + 0.0050, 3.5)),
 seg(1058, 1093, 17, SCO, EDI, T("Malcolm's Castle", "Malcolm'un Kalesi"),
     T("1058–93: Malcolm III is the first king known to live on the Castle Rock",
       "1058–93: III. Malcolm, Kale Kayası'nda yaşadığı bilinen ilk kraldır"),
     cam=(CASTLE[0] + 0.0005, CASTLE[1] + 0.0020, 2.4), chapter=T("Royal Burgh", "Kraliyet Kasabası")),
 seg(1094, 1127, 17, SCO, EDI, T("A King's Burgh", "Bir Kral Kasabası"),
     T("1124: David I founds St Giles'; by 1127 Edinburgh is a royal burgh",
       "1124: I. David St Giles'ı kurar; 1127'ye dek Edinburgh bir kraliyet kasabası olur"),
     cam=(GILES[0], GILES[1] - 0.0010, 2.4)),
 seg(1128, 1129.9, 16, SCO, EDI, T("Holyrood Abbey", "Holyrood Manastırı"),
     T("1128: David I founds Holyrood Abbey; its charter is the first record of Leith",
       "1128: I. David Holyrood Manastırı'nı kurar; fermanı Leith'in ilk kaydıdır"),
     cam=(55.95200, -3.17700, 2.8)),
 seg(1130, 1140, 15, SCO, EDI, T("St Margaret's Chapel", "Aziz Margaret Şapeli"),
     T("c. 1130–40: St Margaret's Chapel, now the castle's oldest building, is built",
       "~1130–40: bugün kalenin en eski yapısı olan Aziz Margaret Şapeli inşa edilir"),
     cam=(CASTLE[0] + 0.0005, CASTLE[1] + 0.0010, 1.8)),
 seg(1141, 1295, 12, SCO, EDI, cam=(OT[0], OT[1] + 0.0020, 3.2)),
 seg(1296, 1313, 17, WOI, EDI, T("Edward I Takes the Castle", "I. Edward Kaleyi Alıyor"),
     T("March 1296: the castle surrenders to Edward I after a three-day bombardment",
       "Mart 1296: kale, üç günlük bombardımanın ardından I. Edward'a teslim olur"),
     cam=(CASTLE[0] + 0.0005, CASTLE[1] + 0.0030, 2.4), chapter=T("Wars and Walls", "Savaşlar ve Surlar")),
 seg(1314, 1328, 16, WOI, EDI, T("A Night Attack", "Gece Baskını"),
     T("14 March 1314: Thomas Randolph retakes the castle; Bruce has it slighted",
       "14 Mart 1314: Thomas Randolph kaleyi geri alır; Bruce surlarını yıktırır"),
     cam=(CASTLE[0] + 0.0005, CASTLE[1] + 0.0020, 2.2)),
 seg(1329, 1366, 15, SCO, EDI, T("A Harbour at Leith", "Leith'te Bir Liman"),
     T("1329: Robert the Bruce gives his harbour at Leith to Edinburgh",
       "1329: Robert the Bruce, Leith'teki limanını Edinburgh'a verir"),
     cam=(55.96300, -3.17800, 6.5)),
 seg(1367, 1384, 15, SCO, EDI, T("David's Tower", "David Kulesi"),
     T("c. 1367: David II begins a great tower; Edinburgh is now called the capital",
       "~1367: II. David büyük bir kule başlatır; Edinburgh artık başkent diye anılır"),
     cam=(CASTLE[0] + 0.0005, CASTLE[1] + 0.0025, 2.2)),
 seg(1385, 1449, 15, SCO, EDI, T("St Giles' Burns", "St Giles Yanıyor"),
     T("1385: an English army raids the town and St Giles' is damaged by fire",
       "1385: bir İngiliz ordusu kasabaya saldırır, St Giles yangından zarar görür"),
     cam=(GILES[0], GILES[1] + 0.0005, 2.2)),
 seg(1450, 1494, 16, SCO, EDI, T("The King's Wall", "Kral Suru"),
     T("1450: James II lets the burgesses defend the town — the King's Wall",
       "1450: II. James kasabalılara şehri savunma izni verir — Kral Suru"),
     cam=(OT[0], OT[1] + 0.0010, 2.6)),
 seg(1495, 1497.9, 15, SCO, EDI, T("The Crown Spire", "Taç Kule"),
     T("1495: St Giles' raises its stone crown spire over the High Street",
       "1495: St Giles, High Street'in üzerinde taştan taç kulesini yükseltir"),
     cam=(GILES[0], GILES[1], 1.8)),
 seg(1498, 1512, 16, SCO, EDI, T("A Palace at Holyrood", "Holyrood'da Bir Saray"),
     T("1498–1501: James IV builds a royal palace beside Holyrood Abbey",
       "1498–1501: IV. James, Holyrood Manastırı'nın yanına bir kraliyet sarayı yaptırır"),
     cam=(PALACE[0], PALACE[1] - 0.0010, 2.0)),
 seg(1513, 1543, 18, SCO, EDI, T("The Flodden Wall", "Flodden Suru"),
     T("After defeat at Flodden in 1513, the town begins a new wall in 1514",
       "1513'teki Flodden yenilgisinin ardından kasaba 1514'te yeni bir sura başlar"),
     cam=(55.94850, -3.19000, 2.8), chapter=T("Flodden to Union", "Flodden'dan Birliğe")),
 seg(1544, 1547.9, 17, SCO, EDI, T("The English Land at Leith", "İngilizler Leith'e Çıkıyor"),
     T("May 1544: English troops land guns at Leith; the castle holds out",
       "Mayıs 1544: İngiliz birlikleri Leith'e top çıkarır; kale direnir"),
     cam=(55.96200, -3.18000, 7.0)),
 seg(1548, 1559.9, 15, SCO, EDI, T("Fortified Leith", "Tahkimli Leith"),
     T("1548: Mary of Guise begins walling Leith with Italian-style bastions",
       "1548: Guise'li Mary, Leith'i İtalyan tarzı burçlarla surlamaya başlar"),
     cam=(SHORE[0] - 0.0020, SHORE[1], 3.0)),
 seg(1560, 1560.9, 17, SCO, EDI, T("The Siege of Leith", "Leith Kuşatması"),
     T("1560: English and Scots besiege the French in Leith; they sail home in June",
       "1560: İngilizler ve İskoçlar Leith'teki Fransızları kuşatır; Haziran'da geri dönerler"),
     pop=10000, cam=(SHORE[0] - 0.0040, SHORE[1] - 0.0020, 3.8)),
 seg(1561, 1570, 16, SCO, EDI, T("A Walled Town", "Surlu Bir Kasaba"),
     T("1560: the Flodden Wall is complete, enclosing about 10,000 people",
       "1560: Flodden Suru tamamlanır; içinde yaklaşık 10.000 kişi yaşar"),
     pop=PI(1561, 1570), cam=(55.94900, -3.19000, 3.0)),
 seg(1571, 1627, 17, SCO, EDI, T("The Lang Siege", "Uzun Kuşatma"),
     T("1571–73: the Lang Siege wrecks David's Tower; the Half Moon Battery follows",
       "1571–73: Uzun Kuşatma David Kulesi'ni yıkar; ardından Yarım Ay Tabyası yapılır"),
     pop=PI(1571, 1627), cam=(CASTLE[0] + 0.0005, CASTLE[1] + 0.0030, 2.4)),
 seg(1628, 1644, 15, SCO, EDI, T("The Telfer Wall", "Telfer Suru"),
     T("1628–36: the Telfer Wall encloses new ground west of Greyfriars",
       "1628–36: Telfer Suru, Greyfriars'ın batısındaki yeni araziyi çevreler"),
     pop=PI(1628, 1644), cam=(55.94650, -3.19300, 2.2)),
 seg(1645, 1649.9, 15, SCO, EDI, T("Plague", "Veba"),
     T("1645: plague kills over 2,700 people in the parish of South Leith alone",
       "1645: veba yalnızca Güney Leith cemaatinde 2.700'den fazla can alır"),
     pop=PI(1645, 1649.9), cam=(55.96500, -3.17800, 6.0)),
 seg(1650, 1670.9, 17, SCO, EDI, T("Cromwell", "Cromwell"),
     T("1650: Cromwell's army takes the castle; a fire guts Holyrood Palace",
       "1650: Cromwell'in ordusu kaleyi alır; bir yangın Holyrood Sarayı'nı harap eder"),
     pop=PI(1650, 1670.9), cam=(55.95000, -3.18600, 3.6)),
 seg(1671, 1706.9, 15, SCO, EDI, T("A New Holyroodhouse", "Yeni Holyroodhouse"),
     T("1671–79: Holyrood Palace is rebuilt, much as it stands today",
       "1671–79: Holyrood Sarayı yeniden yapılır; bugünkü hâline büyük ölçüde o zaman kavuşur"),
     pop=PI(1671, 1706.9), cam=(PALACE[0], PALACE[1] - 0.0010, 2.0)),
 seg(1707, 1744.9, 15, GB, EDI, T("The Last Parliament", "Son Parlamento"),
     T("1707: Scotland's Parliament, in Parliament House since the 1630s, comes to an end",
       "1707: 1630'lardan beri Parlamento Binası'nda toplanan İskoç Parlamentosu sona erer"),
     pop=PI(1707, 1744.9), cam=(GILES[0], GILES[1] + 0.0005, 2.2)),
 seg(1745, 1754.9, 15, GB, EDI, T("The Jacobites", "Jakobitler"),
     T("1745: a Jacobite army holds the town, but the castle never falls",
       "1745: Jakobit ordusu kasabayı tutar, ama kale hiç düşmez"),
     pop=PI(1745, 1754.9), cam=(55.94950, -3.19100, 3.4)),
 seg(1755, 1762.9, 15, GB, EDI, T("A Crowded Ridge", "Kalabalık Sırt"),
     T("1755: Edinburgh and Leith count 57,195 people", "1755: Edinburgh ve Leith'te 57.195 kişi yaşar"),
     pop=PI(1755, 1762.9), cam=(55.95600, -3.18500, 6.0), chapter=T("The New Town", "Yeni Şehir")),
 seg(1763, 1765.9, 17, GB, EDI, T("Draining the Nor Loch", "Nor Gölü Kurutuluyor"),
     T("21 October 1763: first stone of the North Bridge as the Nor Loch is drained",
       "21 Ekim 1763: Nor Gölü kurutulurken Kuzey Köprüsü'nün ilk taşı konur"),
     pop=PI(1763, 1765.9), cam=(55.95150, -3.19300, 2.6)),
 seg(1766, 1768.8, 18, GB, EDI, T("James Craig's Plan", "James Craig'in Planı"),
     T("1766: James Craig, aged 26, wins the contest to plan a New Town; building starts 1767",
       "1766: 26 yaşındaki James Craig Yeni Şehir yarışmasını kazanır; inşaat 1767'de başlar"),
     pop=PI(1766, 1768.8), cam=(55.95400, -3.19900, 2.8)),
 seg(1768.9, 1769.5, 14, GB, EDI, T("The Abbey Falls", "Manastır Çöküyor"),
     T("2 December 1768: Holyrood Abbey's roof collapses, leaving a ruin",
       "2 Aralık 1768: Holyrood Manastırı'nın çatısı çöker; geriye bir harabe kalır"),
     pop=PI(1768.9, 1769.5), cam=(ABBEY[0], ABBEY[1] - 0.0010, 1.6)),
 seg(1769.6, 1772.9, 16, GB, EDI, T("The North Bridge", "Kuzey Köprüsü"),
     T("1769: the unfinished bridge collapses, killing five; it finally opens in 1772",
       "1769: bitmemiş köprü çöker, beş kişi ölür; köprü sonunda 1772'de açılır"),
     pop=PI(1769.6, 1772.9), cam=(NBRIDGE[0], NBRIDGE[1], 1.8)),
 seg(1773, 1784.9, 10, GB, EDI, pop=PI(1773, 1784.9), cam=(55.95300, -3.19500, 3.6)),
 seg(1785, 1788.9, 16, GB, EDI, T("The South Bridge", "Güney Köprüsü"),
     T("1785–88: the South Bridge carries a street over the Cowgate on 19 arches",
       "1785–88: Güney Köprüsü, bir caddeyi 19 kemerle Cowgate'in üzerinden geçirir"),
     pop=PI(1785, 1788.9), cam=(SBRIDGE[0], SBRIDGE[1], 1.8)),
 seg(1789, 1805.9, 16, GB, EDI, T("Old College", "Eski Kolej"),
     T("6 November 1789: the first stone of Robert Adam's Old College is laid",
       "6 Kasım 1789: Robert Adam'ın Eski Kolej binasının ilk taşı konur"),
     pop=PI(1789, 1805.9), cam=(OLDCOL[0], OLDCOL[1], 2.0)),
 seg(1806, 1816.9, 16, GB, EDI, T("Leith's Wet Docks", "Leith'in Islak Havuzları"),
     T("20 May 1806: Leith opens the first wet dock in Scotland", "20 Mayıs 1806: Leith, İskoçya'nın ilk ıslak havuzunu açar"),
     pop=PI(1806, 1816.9), cam=(SHORE[0] - 0.0005, SHORE[1] + 0.0010, 3.0)),
 seg(1817, 1823.9, 17, GB, EDI, T("Monuments on Calton Hill", "Calton Tepesi'nde Anıtlar"),
     T("1822: the National Monument is begun beside Nelson's tower on Calton Hill",
       "1822: Calton Tepesi'nde Nelson kulesinin yanında Ulusal Anıt'a başlanır"),
     pop=PI(1817, 1823.9), cam=(NELSON[0], NELSON[1] - 0.0010, 2.2)),
 seg(1824, 1824.95, 17, GB, EDI, T("The Great Fire", "Büyük Yangın"),
     T("15 November 1824: fire sweeps the High Street for days; 13 people die",
       "15 Kasım 1824: yangın günlerce High Street'i kasıp kavurur; 13 kişi ölür"),
     pop=PI(1824, 1824.95), cam=(GILES[0], GILES[1] + 0.0010, 1.8)),
 seg(1825, 1839.9, 15, GB, EDI, T("The New Towns Grow", "Yeni Şehirler Büyüyor"),
     T("By 1820 Charlotte Square ends the first New Town; more follow to the 1830s",
       "1820'de Charlotte Meydanı ilk Yeni Şehri tamamlar; 1830'lara dek yenileri eklenir"),
     pop=PI(1825, 1839.9), cam=(55.95500, -3.20000, 4.0)),
 seg(1840, 1845.9, 17, VIC, EDI, T("The Scott Monument", "Scott Anıtı"),
     T("1840–46: the 61 m Scott Monument rises in the gardens of the drained loch",
       "1840–46: 61 m'lik Scott Anıtı, kurutulan gölün bahçelerinde yükselir"),
     pop=PI(1840, 1845.9), cam=(SCOTT[0], SCOTT[1], 1.8), chapter=T("Victorian City", "Viktorya Dönemi Şehri")),
 seg(1846, 1865.9, 16, VIC, EDI, T("The Railway Arrives", "Demiryolu Geliyor"),
     T("22 June 1846: North Bridge station opens in the valley below the Old Town",
       "22 Haziran 1846: Kuzey Köprüsü istasyonu Eski Şehir'in altındaki vadide açılır"),
     pop=PI(1846, 1865.9), cam=(WAVERLEY[0], WAVERLEY[1] - 0.0010, 2.4)),
 seg(1866, 1891.9, 15, VIC, EDI, T("Waverley", "Waverley"),
     T("1866–68: the North British Railway merges three stations into Waverley",
       "1866–68: North British Demiryolu üç istasyonu Waverley'de birleştirir"),
     pop=PI(1866, 1891.9), cam=(55.95300, -3.18800, 5.0)),
 seg(1892, 1900.9, 16, VIC, EDI, T("Britain's Largest Station", "Britanya'nın En Büyük İstasyonu"),
     T("From 1892: Waverley is rebuilt on 23 acres — the largest station in Britain",
       "1892'den itibaren: Waverley 23 akre üzerinde yeniden yapılır — Britanya'nın en büyüğü"),
     pop=PI(1892, 1900.9), cam=(WAVERLEY[0], WAVERLEY[1], 2.2)),
 seg(1901, 1919.9, 15, VIC, EDI, T("A City of 300,000", "300.000'lik Şehir"),
     T("1901: 303,638 people; tenements and villas spread south and west",
       "1901: 303.638 kişi; apartmanlar ve villalar güneye ve batıya yayılır"),
     pop=PI(1901, 1919.9), cam=(55.94800, -3.19500, 9.0)),
 seg(1920, 1921.9, 18, MOD, EDI, T("Leith Joins Edinburgh", "Leith Edinburgh'a Katılıyor"),
     T("1 November 1920: Leith is merged with Edinburgh, though it voted 26,810 to 4,340 against",
       "1 Kasım 1920: Leith, 26.810'a 4.340 oyla karşı çıksa da Edinburgh'a katılır"),
     pop=PI(1920, 1921.9), cam=(55.96200, -3.18000, 9.0), chapter=T("Modern Capital", "Modern Başkent")),
 seg(1922, 1950.9, 12, MOD, EDI, pop=PI(1922, 1950.9), cam=(55.94500, -3.20000, 14.0)),
 seg(1951, 1994.9, 15, MOD, EDI, T("Suburbs", "Banliyöler"),
     T("1951: 466,761 people; new estates fill the land toward the hills",
       "1951: 466.761 kişi; yeni yerleşimler tepelere doğru araziyi doldurur"),
     pop=PI(1951, 1994.9), cam=(55.93500, -3.20000, 17.0)),
 seg(1995, 1998.9, 16, MOD, EDI, T("World Heritage", "Dünya Mirası"),
     T("1995: the Old and New Towns become a UNESCO World Heritage Site",
       "1995: Eski ve Yeni Şehir UNESCO Dünya Mirası olur"),
     pop=PI(1995, 1998.9), cam=(55.95200, -3.19500, 4.0)),
 seg(1999, 2004.7, 18, DEV, EDI, T("A Parliament Returns", "Parlamento Geri Dönüyor"),
     T("1999: a Scottish Parliament sits again, at first in the Assembly Hall on the Mound",
       "1999: İskoç Parlamentosu yeniden toplanır; önce Mound'daki Kurul Salonu'nda"),
     pop=PI(1999, 2004.7), cam=(55.95100, -3.18500, 3.4), chapter=T("Holyrood", "Holyrood")),
 seg(2004.77, 2022.9, 18, DEV, EDI, T("Holyrood", "Holyrood"),
     T("9 October 2004: the Queen opens the new Parliament building at Holyrood",
       "9 Ekim 2004: Kraliçe, Holyrood'daki yeni Parlamento binasını açar"),
     pop=PI(2004.77, 2022.9), cam=(PARL[0], PARL[1] - 0.0005, 2.0)),
 seg(2023, 2026, 22, DEV, EDI, T("Edinburgh Today", "Bugünkü Edinburgh"),
     T("2023: trams reach Leith; mid-2024: about 530,680 people live in the city",
       "2023: tramvay Leith'e ulaşır; 2024 ortası: şehirde yaklaşık 530.680 kişi yaşar"),
     pop=PI(2023, 2026), cam=(55.94500, -3.19000, 16.0)),
]

# ------------------------------------------------------------------ districts
D = lambda name, style, poly, frm, to, dens, grow, **kw: dict({"name": name, "style": style, "poly": L(poly), "from": frm, "to": to,
                                                               "density": dens, "grow_from": list(grow)}, **kw)
districts = [
 D("Huts on the Castle Rock (≈)", "celtic", circle((CASTLE[0] + 0.0004, CASTLE[1] + 0.0040), 160, 10), -950, -500, 0.35,
   (CASTLE[0] + 0.0004, CASTLE[1] + 0.0040), fade=[1090, 1140, 0.0]),
 D("Hill fort settlement, Arthur's Seat (≈)", "celtic", circle((55.94600, -3.15700), 220, 10), -450, -100, 0.3, (55.94600, -3.15700),
   fade=[700, 900, 0.0]),
 D("Burgh on the ridge (≈)", "medieval", BURGH, 1094, 1440, 0.75, (GILES[0], GILES[1]), grain_m=50),
 D("Canongate (≈)", "medieval", CANON, 1128, 1500, 0.6, NETHERBOW, grain_m=55),
 D("Leith harbour town (≈)", "medieval", LEITH_OLD, 1200, 1550, 0.6, SHORE, grain_m=55),
 D("Cowgate and Grassmarket (≈)", "medieval", COWG, 1450, 1560, 0.75, (55.94800, -3.19000), grain_m=50),
 D("Old Town tenements (≈)", "stone", OLD_CORE, 1560, 1750, 0.8, (GILES[0], GILES[1]), grain_m=50, holes=[L(CASTLE_ROCK), L(NOR_LOCH)]),
 D("Southside (≈)", "georgian", SOUTHSIDE, 1760, 1830, 0.65, (55.94600, -3.18800), grain_m=55),
 D("Leith (≈)", "georgian", LEITH_GEO, 1700, 1840, 0.6, SHORE, grain_m=60, holes=[L(LEITH_OLD)]),
 D("First New Town (≈)", "georgian", NT1, 1767, 1820, 0.85, (55.95450, -3.19300), grain_m=50, grid_deg=20),
 D("Second New Town (≈)", "georgian", NT2, 1800, 1830, 0.8, (55.95700, -3.19700), grain_m=52, grid_deg=20),
 D("West End (≈)", "georgian", WESTEND, 1805, 1850, 0.7, (55.95040, -3.20750), grain_m=55, grid_deg=20),
 D("Calton terraces (≈)", "georgian", CALTON_T, 1819, 1835, 0.6, (55.95550, -3.18200), grain_m=55),
 D("Moray estate (≈)", "georgian", MORAY, 1822, 1835, 0.8, (55.95550, -3.20900), grain_m=50),
 D("Victorian tenements and villas (≈)", "victorian", VICTORIAN, 1840, 1914, 0.8, OT, grain_m=62,
   holes=[L(OLD_CORE), L(CANON), L(NT1), L(NT2), L(MORAY), L(WESTEND), L(CALTON_T), L(CALTON_HILL), L(HOLYROOD_PARK), L(MEADOWS),
          L(GARDENS), L(SOUTHSIDE), L(LEITH_GEO), L(CASTLE_ROCK)]),
 D("Leith docks quarter (≈)", "industrial", [(55.97700, -3.18000), (55.98000, -3.16500), (55.97700, -3.15500), (55.97300, -3.16200)],
   1850, 1910, 0.45, (55.97600, -3.16800), grain_m=100),
 D("20th-century suburbs (≈)", "suburb", SUBURBS, 1920, 1975, 0.55, OT, grain_m=130,
   holes=[L(VICTORIAN), L(HOLYROOD_PARK), L(LEITH_GEO)]),
]

walls = [
 {"name": "King's Wall (≈)", "path": L(KINGS_WALL), "built": 1450, "removed": 1560, "height": "low", "towers_m": 0, "draw_s": 3},
 {"name": "Flodden Wall (≈ between sourced points)", "path": L(FLODDEN), "built": 1514, "removed": 1785, "height": "mid", "towers_m": 120,
  "draw_s": 5},
 {"name": "Leith fortifications (≈ shape)", "path": L(LEITH_FORT + [LEITH_FORT[0]]), "built": 1548, "removed": 1561, "height": "mid",
  "towers_m": 140, "draw_s": 4},
 {"name": "Telfer Wall (≈)", "path": L(TELFER), "built": 1628, "removed": 1762, "height": "low", "towers_m": 0, "draw_s": 3},
]

bridges = [
 {"name": "North Bridge (first)", "path": [[55.95050, -3.18710], [55.95320, -3.18960]], "built": 1772, "removed": 1896, "style": "stone",
  "width_m": 16},
 {"name": "North Bridge (1897)", "path": [[55.95050, -3.18710], [55.95320, -3.18960]], "built": 1897, "style": "iron", "width_m": 23},
 {"name": "South Bridge", "path": [[55.94930, -3.18720], [55.94820, -3.18650]], "built": 1788, "style": "stone", "width_m": 16},
]

roads = [
 {"name": "Royal Mile (≈)", "path": L(ROYAL_MILE + CANONGATE[1:]), "from": 1094, "kind": "road", "width_m": 14, "draw_s": 3},
 {"name": "Leith Walk (≈)", "path": L(LEITH_WALK), "from": 1650, "kind": "road", "width_m": 16, "draw_s": 3},
 {"name": "Princes Street (≈)", "path": L([(55.94980, -3.20900), (55.95340, -3.18950)]), "from": 1767, "kind": "avenue", "width_m": 26, "draw_s": 3},
 {"name": "George Street (≈)", "path": L([(55.95190, -3.20850), (55.95500, -3.19250)]), "from": 1767, "kind": "avenue", "width_m": 26},
 {"name": "The Mound (≈)", "path": L([(55.95270, -3.19650), (55.95020, -3.19500)]), "from": 1790, "kind": "road", "width_m": 20},
 {"name": "Railway west (≈)", "path": L([(55.94580, -3.21850), (55.94950, -3.20900), (55.95100, -3.20000), (55.95200, -3.19100)]),
  "from": 1846.5, "kind": "rail", "width_m": 22},
 {"name": "Railway east (≈)", "path": L([(55.95220, -3.18700), (55.95420, -3.17900), (55.95600, -3.16500), (55.95400, -3.14000)]),
  "from": 1846.5, "kind": "rail", "width_m": 22},
]

C_ = lambda w, r: {"wall": w, "roof": r}
STONE = "#9c958a"; SAND = "#c9b896"
landmarks = [
 {"type": "fort", "name": T("Din Eidyn hill fort (≈)", "Din Eidyn tepe kalesi (≈)"), "at": list(CASTLE), "built": 500, "removed": 1058,
  "rise_s": 6, "size_m": [140, 80, 4], "rot_deg": 0, "scale": 1.5, "colors": {"wall": "#8a7a60"}},
 {"type": "castle", "name": T("Edinburgh Castle", "Edinburgh Kalesi"), "at": list(CASTLE), "built": 1058, "rise_s": 10,
  "size_m": [200, 100, 22], "rot_deg": 10, "scale": 1.5, "colors": C_(STONE, "#5f666f")},
 {"type": "church", "name": T("St Margaret's Chapel", "Aziz Margaret Şapeli"), "at": [CASTLE[0] + 0.0001, CASTLE[1] - 0.0003], "built": 1130,
  "rise_s": 6, "size_m": [16, 7, 8], "scale": 1.6, "colors": C_(STONE, "#5f666f")},
 {"type": "tower", "name": T("David's Tower (≈ position)", "David Kulesi (≈ konum)"), "at": [CASTLE[0] - 0.0001, CASTLE[1] + 0.0008], "built": 1367,
  "removed": 1572, "rise_s": 6, "size_m": [16, 16, 30], "colors": C_(STONE, "#5f666f")},
 {"type": "church", "name": T("St Giles'", "St Giles"), "at": list(GILES), "built": 1124, "rise_s": 10, "size_m": [60, 35, 20], "rot_deg": 0,
  "colors": C_("#8f8a80", "#4f5a60")},
 {"type": "clocktower", "name": T("St Giles' crown spire", "St Giles taç kulesi"), "at": [GILES[0], GILES[1] + 0.0001], "built": 1495, "rise_s": 6,
  "size_m": [10, 10, 49], "colors": C_("#8f8a80", "#8f8a80")},
 {"type": "cathedral", "name": T("Holyrood Abbey", "Holyrood Manastırı"), "at": list(ABBEY), "built": 1128, "removed": 1768.92, "rise_s": 12,
  "size_m": [80, 25, 20], "rot_deg": 0, "colors": C_("#a8998a", "#5f666f")},
 {"type": "palace", "name": T("Palace of Holyroodhouse", "Holyroodhouse Sarayı"), "at": list(PALACE), "built": 1498, "rise_s": 10,
  "size_m": [70, 70, 18], "rot_deg": 0, "colors": C_("#b3a998", "#5f666f")},
 {"type": "tower", "name": T("Netherbow Port", "Netherbow Kapısı"), "at": list(NETHERBOW), "built": 1514, "removed": 1764, "rise_s": 4,
  "size_m": [14, 10, 18], "colors": C_(STONE, "#5f666f")},
 {"type": "palace", "name": T("Old College", "Eski Kolej"), "at": list(OLDCOL), "built": 1789.85, "rise_s": 20, "size_m": [110, 80, 20],
  "rot_deg": 0, "colors": C_("#b8ad96", "#5f666f")},
 {"type": "tower", "name": T("Nelson Monument", "Nelson Anıtı"), "at": list(NELSON), "built": 1807, "rise_s": 8, "size_m": [12, 12, 32],
  "scale": 1.5, "colors": C_("#b8ad96", "#b8ad96")},
 {"type": "temple", "name": T("National Monument (≈ position)", "Ulusal Anıt (≈ konum)"), "at": list(NATMON), "built": 1826, "rise_s": 8,
  "size_m": [70, 20, 13], "rot_deg": 0, "colors": C_("#c8bfa8", "#c8bfa8")},
 {"type": "spire_tower", "name": T("Scott Monument", "Scott Anıtı"), "at": list(SCOTT), "built": 1840.62, "rise_s": 10, "size_m": [16, 16, 61],
  "colors": C_("#6e665c", "#6e665c")},
 {"type": "station", "name": T("North Bridge station", "Kuzey Köprüsü istasyonu"), "at": [WAVERLEY[0], WAVERLEY[1] + 0.0008], "built": 1846.47,
  "removed": 1866, "rise_s": 6, "size_m": [140, 50, 10], "rot_deg": -20, "colors": C_("#a49a88", "#5f666f")},
 {"type": "station", "name": T("Waverley station", "Waverley istasyonu"), "at": list(WAVERLEY), "built": 1866, "removed": 1892, "rise_s": 8,
  "size_m": [260, 90, 12], "rot_deg": -20, "colors": C_("#a49a88", "#5f666f")},
 {"type": "station", "name": T("Waverley station (1890s)", "Waverley istasyonu (1890'lar)"), "at": list(WAVERLEY), "built": 1892, "rise_s": 20,
  "size_m": [380, 150, 14], "rot_deg": -20, "colors": C_("#a49a88", "#7d8a8f")},
 {"type": "harbor", "name": T("Leith harbour (≈)", "Leith limanı (≈)"), "at": list(SHORE), "built": 1329, "rise_s": 6, "size_m": [120, 60, 6],
  "colors": {"wall": "#8a7a60"}},
 {"type": "parliament", "name": T("Scottish Parliament", "İskoç Parlamentosu"), "at": list(PARL), "built": 1999.45, "rise_s": 20,
  "size_m": [190, 110, 16], "rot_deg": 0, "colors": C_("#c9c2b2", "#6d7a70")},
]

fires = [
 {"year": 1824.875, "poly": L([(55.94920, -3.19100), (55.95000, -3.18870), (55.94950, -3.18830), (55.94875, -3.19060)]), "duration_s": 7, "plumes": 5},
]
smoke = [
 {"at": [CASTLE[0], CASTLE[1] + 0.0005], "from": 1296.1, "to": 1296.3, "scale": 1.0},
 {"at": [GILES[0], GILES[1]], "from": 1385.1, "to": 1385.8, "scale": 0.9},
 {"at": [SHORE[0] - 0.0020, SHORE[1]], "from": 1560.2, "to": 1560.5, "scale": 1.2},
 {"at": [CASTLE[0], CASTLE[1] + 0.0005], "from": 1571.3, "to": 1573.4, "scale": 1.1},
 {"at": list(PALACE), "from": 1650.85, "to": 1650.95, "scale": 1.0},
]
camps = [
 {"poly": L([(55.96650, -3.18700), (55.96900, -3.18800), (55.97000, -3.17300), (55.96750, -3.17200)]), "from": 1560.2, "to": 1560.5, "count": 160},
]
open_spaces = [
 {"name": "Castle Rock", "poly": L(CASTLE_ROCK)},
 {"name": "Holyrood Park (≈)", "poly": L(HOLYROOD_PARK)},
 {"name": "Calton Hill (≈)", "poly": L(CALTON_HILL)},
 {"name": "The Meadows (≈)", "poly": L(MEADOWS)},
 {"name": "Princes Street Gardens (≈, former Nor Loch)", "poly": L(GARDENS)},
]
timed_water = [
 {"name": "Nor Loch (≈)", "poly": L(NOR_LOCH), "from": 1420, "to": 1765},
]

labels = [
 {"text": T("FIRTH OF FORTH", "FORTH KÖRFEZİ"), "at": [55.99500, -3.21000], "kind": "water", "from": -1000},
 {"text": T("Castle Rock", "Kale Kayası"), "at": list(CASTLE), "kind": "place", "from": -1000, "to": -501},
 {"text": T("Arthur's Seat", "Arthur's Seat"), "at": list(ARTHUR), "kind": "place", "from": -500, "to": 499},
 {"text": T("Din Eidyn", "Din Eidyn"), "at": list(CASTLE), "kind": "place", "from": 500, "to": 853},
 {"text": T("NORTHUMBRIA", "NORTHUMBRIA"), "at": [55.93500, -3.17000], "kind": "region", "from": 650, "to": 853},
 {"text": T("St Giles'", "St Giles"), "at": list(GILES), "kind": "place", "from": 1094, "to": 1127},
 {"text": T("Holyrood", "Holyrood"), "at": list(ABBEY), "kind": "place", "from": 1128, "to": 1129.9},
 {"text": T("Leith", "Leith"), "at": list(SHORE), "kind": "place", "from": 1329, "to": 1366},
 {"text": T("St Giles'", "St Giles"), "at": list(GILES), "from": 1385, "to": 1497.9, "lift_m": 60},
 {"text": T("Holyroodhouse", "Holyroodhouse"), "at": list(PALACE), "kind": "place", "from": 1498, "to": 1512},
 {"text": T("Leith", "Leith"), "at": list(SHORE), "kind": "place", "from": 1544, "to": 1560.9},
 {"text": T("OLD TOWN", "ESKİ ŞEHİR"), "at": [55.94800, -3.19000], "kind": "region", "from": 1561, "to": 1570},
 {"text": T("Greyfriars", "Greyfriars"), "at": [55.94660, -3.19250], "kind": "place", "from": 1628, "to": 1644},
 {"text": T("South Leith", "Güney Leith"), "at": [SHORE[0] - 0.0030, SHORE[1] + 0.0010], "kind": "place", "from": 1645, "to": 1649.9},
 {"text": T("Holyroodhouse", "Holyroodhouse"), "at": list(PALACE), "kind": "place", "from": 1650, "to": 1706.9},
 {"text": T("Parliament House", "Parlamento Binası"), "at": [55.94900, -3.19130], "kind": "place", "from": 1707, "to": 1744.9},
 {"text": T("LEITH", "LEITH"), "at": [SHORE[0] - 0.0020, SHORE[1]], "kind": "region", "from": 1755, "to": 1762.9},
 {"text": T("Nor Loch", "Nor Gölü"), "at": [55.95200, -3.19850], "kind": "water", "from": 1755, "to": 1765.9},
 {"text": T("NEW TOWN", "YENİ ŞEHİR"), "at": [55.95500, -3.19900], "kind": "region", "from": 1766, "to": 1768.8},
 {"text": T("North Bridge", "Kuzey Köprüsü"), "at": list(NBRIDGE), "kind": "place", "from": 1769.6, "to": 1772.9},
 {"text": T("Cowgate", "Cowgate"), "at": [55.94850, -3.18800], "kind": "place", "from": 1785, "to": 1788.9},
 {"text": T("Old College", "Eski Kolej"), "at": list(OLDCOL), "from": 1789, "to": 1805.9, "lift_m": 30},
 {"text": T("Leith Docks", "Leith Havuzları"), "at": [SHORE[0] + 0.0020, SHORE[1] + 0.0030], "kind": "place", "from": 1806, "to": 1816.9},
 {"text": T("Calton Hill", "Calton Tepesi"), "at": list(NELSON), "kind": "place", "from": 1817, "to": 1823.9},
 {"text": T("High Street", "High Street"), "at": [55.94990, -3.18950], "kind": "place", "from": 1824, "to": 1824.95},
 {"text": T("NEW TOWN", "YENİ ŞEHİR"), "at": [55.95600, -3.19900], "kind": "region", "from": 1825, "to": 1839.9},
 {"text": T("Scott Monument", "Scott Anıtı"), "at": list(SCOTT), "from": 1844, "to": 1845.9, "lift_m": 70},
 {"text": T("Waverley", "Waverley"), "at": list(WAVERLEY), "kind": "place", "from": 1866, "to": 1900.9},
 {"text": T("LEITH", "LEITH"), "at": [SHORE[0] - 0.0030, SHORE[1]], "kind": "region", "from": 1920, "to": 1921.9},
 {"text": T("Arthur's Seat", "Arthur's Seat"), "at": list(ARTHUR), "kind": "place", "from": 1951, "to": 1994.9},
 {"text": T("OLD TOWN", "ESKİ ŞEHİR"), "at": [55.94850, -3.19000], "kind": "region", "from": 1995, "to": 1998.9},
 {"text": T("NEW TOWN", "YENİ ŞEHİR"), "at": [55.95550, -3.19900], "kind": "region", "from": 1995, "to": 1998.9},
 {"text": T("The Mound", "The Mound"), "at": [55.95150, -3.19570], "kind": "place", "from": 1999, "to": 2004.7},
 {"text": T("Scottish Parliament", "İskoç Parlamentosu"), "at": list(PARL), "from": 2004.77, "to": 2022.9, "lift_m": 30},
 {"text": T("LEITH", "LEITH"), "at": [SHORE[0] - 0.0020, SHORE[1]], "kind": "region", "from": 2023},
]

city = {
 "slug": "edinburgh", "seed": 1124, "long_ok": True,
 "name": T("Edinburgh", "Edinburgh"), "intro": T("3,000 Years", "3.000 Yıl"), "intro_seconds": 4.5,
 "geo": {"bbox": [55.78, -3.52, 56.12, -2.86], "cell_m": 90, "core_bbox": [55.925, -3.245, 55.990, -3.140], "core_cell_m": 30,
         "rivers_keep": ["Forth"], "sea_level_m": 6.0},
 "geo_edits": [{"op": "water", "poly": L(OUTER_FORTH)}],
 "view": {"azimuth_deg": 0, "pitch_deg": 46, "fov": 34},
 "render": {"vertical_exaggeration": 3.0},
 "segments": S,
 "districts": districts, "walls": walls, "bridges": bridges, "roads": roads, "landmarks": landmarks,
 "fires": fires, "camps": camps, "smoke": smoke, "open_spaces": open_spaces, "timed_water": timed_water, "labels": labels,
 "youtube": {
  "description": T(
   "A volcanic rock lived on since about 1000 BC, the Gododdin fort of Din Eidyn, and a royal burgh along one ridge. Watch "
   "Edinburgh grow from the Castle Rock to Holyrood: the King's, Flodden and Telfer walls, the sieges of 1296, 1314, 1560 and "
   "1571–73, the draining of the Nor Loch and James Craig's New Town, the North and South Bridges, the Great Fire of 1824, the "
   "Scott Monument and Waverley station, Leith's merger in 1920 and the new Scottish Parliament of 2004 — with the year and the "
   "population on screen.",
   "MÖ ~1000'den beri yaşanan volkanik bir kaya, Gododdin'lerin Din Eidyn kalesi ve tek bir sırt boyunca uzanan bir kraliyet "
   "kasabası. Edinburgh'un Kale Kayası'ndan Holyrood'a büyümesini izleyin: Kral, Flodden ve Telfer surları; 1296, 1314, 1560 ve "
   "1571–73 kuşatmaları; Nor Gölü'nün kurutulması ve James Craig'in Yeni Şehri; Kuzey ve Güney köprüleri; 1824 Büyük Yangını; "
   "Scott Anıtı ve Waverley istasyonu; 1920'de Leith'in katılması ve 2004'teki yeni İskoç Parlamentosu — yıl ve nüfus ekranda."),
  "tags": ["edinburgh history", "history of edinburgh", "edinburgh", "edinburgh castle", "royal mile", "new town edinburgh",
           "scotland history", "3d timelapse", "city evolution", "how edinburgh grew", "edinburgh timelapse", "old town edinburgh",
           "holyrood", "leith", "urban history"],
  "hashtags": ["#Edinburgh", "#Scotland", "#History", "#Timelapse"],
  "playlist": T("Cities of Europe", "Avrupa Şehirleri"),
  "thumb": {"line1": T("Edinburgh", "Edinburgh"), "line2": T("3,000 YEARS", "3.000 YIL"),
            "line3": T("From castle rock to capital", "Kale kayasından başkente"),
            "extra": "&mood=golden&pitch=30&az=0&cam=55.9500,-3.1900,5.0"},
 },
 "sources": json.load(open(os.path.join(HERE, "_sources.json"))),
}
total = sum(s_["seconds"] for s_ in S)
mins = round(total / 60)
city["intro"] = T(f"3,000 Years in {mins} Minutes", f"{mins} Dakikada 3.000 Yıl")
city["youtube"]["title"] = T(f"Edinburgh: 3,000 Years in {mins} Minutes (3D Timelapse)", f"Edinburgh: {mins} Dakikada 3.000 Yıl (3D Timelapse)")
json.dump(city, open(os.path.join(HERE, "city.json"), "w"), ensure_ascii=False, indent=1)
print("segments", len(S), "duration", total, "s =", f"{total // 60}:{total % 60:02d}")
