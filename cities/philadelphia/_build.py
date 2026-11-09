"""Builds cities/philadelphia/city.json. Every on-screen date/figure is from research.md (sources listed there).
Run: python3 cities/philadelphia/_build.py
Street lines, district outlines, open spaces and camps are simplified traces between sourced points (marked ≈ in
research.md). Penn's grid: Front St to Broad St = 13 blocks; Broad St runs through City Hall (sourced coordinates)."""
import json, math, os

T = lambda en, tr: {"en": en, "tr": tr}
HERE = os.path.dirname(os.path.abspath(__file__))
rect = lambda s, w, n, e: [(s, w), (n, w), (n, e), (s, e)]


def L(pts):
    return [[round(a, 5), round(b, 5)] for a, b in pts]


def circle(c, r_m, n=10):
    kx = 111.32 * math.cos(math.radians(c[0])); kz = 110.574
    return [(c[0] + r_m / 1000 / kz * math.sin(2 * math.pi * i / n), c[1] + r_m / 1000 / kx * math.cos(2 * math.pi * i / n)) for i in range(n)]


# ------------------------------------------------------------------ published coordinates (research.md)
CITYHALL = (39.95239, -75.16360); INDEP = (39.94889, -75.15000); CHRIST = (39.95083, -75.14389); GLORIA = (39.93450, -75.14350)
CARP = (39.94810, -75.14720); TREATY = (39.96711, -75.12849); WATERW = (39.96556, -75.18083); PMA = (39.96610, -75.18110)
ESP = (39.96830, -75.17250); BFB = (39.95300, -75.13400); WWB = (39.90530, -75.12970); NAVY = (39.89110, -75.17860)
MIFFLIN = (39.87530, -75.21300); STN30 = (39.95583, -75.18194); OLP = (39.95220, -75.16780); CTC = (39.95490, -75.17040)

# ------------------------------------------------------------------ Penn's grid (≈): street lines between the rivers
FRONT = -75.1425; BLK = (CITYHALL[1] - FRONT) / 13          # Front St .. Broad St (14th) = 13 blocks
st = lambda n: FRONT + (n - 1) * BLK                         # n-th street east of Broad
VINE, MARKET, SOUTH = 39.9575, 39.9520, 39.9415
DEL_E = -75.1385                                             # just over the Delaware shore (buildings stop at water)
SCH_W = -75.1800                                             # Schuylkill east bank ≈ (buildings stop at water)

EARLY = rect(39.9440, DEL_E, 39.9560, st(3))                 # first houses along the Delaware (≈)
COLONIAL = rect(SOUTH, DEL_E, VINE, st(7))                   # 18th-century city, "east of 6th Street"
NLIB = rect(VINE, DEL_E, 39.9660, st(6))                     # Northern Liberties (≈)
SWARK = rect(39.9300, -75.1420, SOUTH, st(6))                # Southwark (≈)
TO_BROAD = rect(SOUTH, st(7), VINE, CITYHALL[1] - 0.0004)    # early 19th c. to Centre Square
TO_SCH = rect(SOUTH, CITYHALL[1] - 0.0004, VINE, SCH_W)      # Centre Square to the Schuylkill
CENTER = rect(SOUTH, DEL_E, VINE, SCH_W)
LIBERTIES = [(VINE, -75.1720), (39.9750, -75.1780), (39.9850, -75.1650), (39.9850, -75.1150), (39.9700, -75.1200),
             (39.9620, -75.1330), (VINE, DEL_E)]
LIB_HOLES = [NLIB]
SOUTHERN = [(SOUTH, -75.1420), (SOUTH, -75.1800), (39.9250, -75.1850), (39.9200, -75.1650), (39.9250, -75.1430)]
WICACO = circle(GLORIA, 350, 9)
CAMDEN = [(39.9600, -75.1300), (39.9600, -75.0950), (39.9300, -75.0900), (39.9200, -75.1200), (39.9350, -75.1350)]
NAVY_Y = [(39.8850, -75.1550), (39.8980, -75.1550), (39.8980, -75.1950), (39.8870, -75.1950)]
# rowhouse city of the consolidation era (≈): North, South and West Philadelphia
ROW = [(39.9200, -75.1430), (39.9600, -75.1350), (39.9900, -75.1000), (40.0150, -75.0750), (40.0250, -75.1200),
       (40.0300, -75.1700), (40.0050, -75.1850), (39.9800, -75.2100), (39.9800, -75.2450), (39.9350, -75.2450),
       (39.9150, -75.2200), (39.9050, -75.1900), (39.9050, -75.1500)]
# the rest of the county (≈ outline of today's city limits)
COUNTY = [(39.8800, -75.1350), (39.9600, -75.1300), (39.9900, -75.0850), (40.0300, -75.0400), (40.0600, -74.9800),
          (40.0900, -74.9650), (40.1350, -75.0150), (40.0900, -75.0950), (40.0800, -75.2050), (40.0600, -75.2650),
          (39.9750, -75.2800), (39.9200, -75.2600), (39.8900, -75.2300), (39.8750, -75.1900)]
FAIRMOUNT_PARK = [(39.9680, -75.1820), (39.9800, -75.1870), (39.9950, -75.1950), (40.0100, -75.2050), (40.0150, -75.1980),
                  (40.0000, -75.1850), (39.9850, -75.1780), (39.9700, -75.1760)]
WISSAHICKON = [(40.0150, -75.2050), (40.0400, -75.2150), (40.0650, -75.2250), (40.0700, -75.2150), (40.0450, -75.2020),
               (40.0200, -75.1960)]
HIGH = rect(39.9500, -75.1720, 39.9565, CITYHALL[1] - 0.0010)   # Center City office core west of City Hall (≈)
PENNCTR = rect(39.9525, -75.1700, 39.9545, CITYHALL[1] - 0.0012)

# five squares (≈, from the grid): Centre Square = City Hall; four quadrant squares
SQ = lambda c: rect(c[0] - 0.0009, c[1] - 0.0013, c[0] + 0.0009, c[1] + 0.0013)
FRANKLIN_SQ = (39.9555, st(7)); WASHINGTON_SQ = (39.9468, st(7)); RITTENHOUSE_SQ = (39.9493, -75.1718); LOGAN_SQ = (39.9573, -75.1705)

# ------------------------------------------------------------------ population (research.md)
CITY = [(1683, 600), (1731, 12000), (1775, 30000), (1777.7, 30000), (1777.75, 15000), (1778.45, 15000), (1790, 28522),
        (1810, 53722), (1830, 80462), (1840, 93665), (1850, 121376), (1853.99, 121376)]
COUNTY_P = [(1850, 408761), (1860, 565529), (1870, 674022), (1890, 1046964), (1900, 1293697), (1910, 1549008), (1930, 1950961),
            (1940, 1931334), (1950, 2071605), (1970, 1948609), (1980, 1688210), (1990, 1585577), (2000, 1517550), (2010, 1526006),
            (2019, 1584064), (2020, 1603797), (2025, 1574281), (2026, 1574281)]


def P(y):
    A = CITY if y < 1854 else COUNTY_P
    for y0, p0 in A:
        if y == y0: return p0
    for (y0, p0), (y1, p1) in zip(A, A[1:]):
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


LEN = T("Lenapehoking", "Lenape Toprakları"); SWE = T("New Sweden", "Yeni İsveç"); PROV = T("Province of Pennsylvania", "Pennsylvania Eyaleti")
REV = T("American Revolution", "Amerikan Devrimi"); US = T("United States", "Amerika Birleşik Devletleri")
TODAY = T("Today", "Bugün")
SHORE = T("Banks of the Delaware", "Delaware kıyısı"); PHL = T("Philadelphia", "Philadelphia")
OLDC = (39.9505, -75.1460)

S = [
 seg(1600, 1645, 20, LEN, SHORE, T("Lenape Land", "Lenape Toprakları"),
     T("Before Europeans: Lenape country; Shackamaxon is a meeting place on the Delaware",
       "Avrupalılardan önce: Lenape ülkesi; Shackamaxon, Delaware kıyısında bir buluşma yeri"),
     cam=(39.9500, -75.1550, 16.0), chapter=T("Before Philadelphia", "Philadelphia'dan Önce")),
 seg(1646, 1676, 16, SWE, SHORE, T("Swedish Farmers", "İsveçli Çiftçiler"),
     T("1646: settlers of New Sweden are the first Europeans to settle the area",
       "1646: Yeni İsveç'in yerleşimcileri bölgeye yerleşen ilk Avrupalılar olur"),
     cam=(39.9420, -75.1480, 8.0)),
 seg(1677, 1680.9, 15, SWE, SHORE, T("A Blockhouse Church", "Kaleden Bozma Kilise"),
     T("1677: Swedes at Wicaco turn a blockhouse into their church",
       "1677: Wicaco'daki İsveçliler bir ahşap kaleyi kiliseye çevirir"),
     cam=(39.9380, -75.1440, 3.5)),
 seg(1681, 1682.5, 15, PROV, SHORE, T("Penn's Charter", "Penn'in Fermanı"),
     T("4 March 1681: King Charles II grants Pennsylvania to William Penn",
       "4 Mart 1681: Kral II. Charles, Pennsylvania'yı William Penn'e verir"),
     cam=(39.9500, -75.1600, 9.0), chapter=T("Penn's Grid", "Penn'in Izgarası")),
 seg(1682.5, 1682.8, 18, PROV, PHL, T("A Grid Between Two Rivers", "İki Nehir Arasında Izgara"),
     T("1682: Thomas Holme lays out a grid of 1,200 acres from the Delaware to the Schuylkill",
       "1682: Thomas Holme, Delaware'den Schuylkill'e 1.200 akrelik bir ızgara planı çizer"),
     cam=(39.9500, -75.1610, 6.0)),
 seg(1682.8, 1683.9, 16, PROV, PHL, T("The Treaty Elm", "Antlaşma Karaağacı"),
     T("1682: by tradition, Penn makes a treaty with Tamanend under an elm at Shackamaxon",
       "1682: rivayete göre Penn, Shackamaxon'da bir karaağacın altında Tamanend'le antlaşma yapar"),
     pop=600, cam=(39.9590, -75.1370, 3.5)),
 seg(1684, 1699.9, 15, PROV, PHL, T("A Town on the River", "Nehir Kıyısında Bir Kasaba"),
     T("1683: about 600 people; by 1699 several hundred houses crowd the riverfront",
       "1683: yaklaşık 600 kişi; 1699'da birkaç yüz ev nehir kıyısına sıkışır"),
     pop=PI(1684, 1699.9), cam=(OLDC[0], OLDC[1], 3.0)),
 seg(1700, 1726, 16, PROV, PHL, T("Old Swedes' Church", "Eski İsveçliler Kilisesi"),
     T("2 June 1700: Gloria Dei, the Old Swedes' Church, is consecrated at Wicaco",
       "2 Haziran 1700: Eski İsveçliler Kilisesi Gloria Dei, Wicaco'da kutsanır"),
     pop=PI(1700, 1726), cam=(39.9440, -75.1450, 3.6)),
 seg(1727, 1731.9, 15, PROV, PHL, T("Christ Church", "Christ Kilisesi"),
     T("1727: work begins on Christ Church; its main body is finished in 1744",
       "1727: Christ Kilisesi'nin inşaatı başlar; ana gövdesi 1744'te biter"),
     pop=PI(1727, 1731.9), cam=(CHRIST[0], CHRIST[1] - 0.002, 2.6)),
 seg(1732, 1752.9, 17, PROV, PHL, T("The State House", "Eyalet Binası"),
     T("1732–1753: the Pennsylvania State House rises on Chestnut Street",
       "1732–1753: Pennsylvania Eyalet Binası Chestnut Caddesi'nde yükselir"),
     pop=PI(1732, 1752.9), cam=(INDEP[0], INDEP[1] + 0.001, 2.8)),
 seg(1753, 1753.9, 14, PROV, PHL, T("A Bell for the Tower", "Kuleye Bir Çan"),
     T("1753: a bell is hung in the State House tower", "1753: Eyalet Binası'nın kulesine bir çan asılır"),
     pop=PI(1753, 1753.9), cam=(INDEP[0], INDEP[1] + 0.001, 2.4)),
 seg(1754, 1769.9, 16, PROV, PHL, T("America's Tallest Steeple", "Amerika'nın En Yüksek Kulesi"),
     T("1754: Christ Church's 196 ft (60 m) steeple — the tallest in America until 1810",
       "1754: Christ Kilisesi'nin 60 m'lik kulesi — 1810'a dek Amerika'nın en yükseği"),
     pop=PI(1754, 1769.9), cam=(39.9505, -75.1470, 3.4)),
 seg(1770, 1773.9, 15, PROV, PHL, T("Carpenters' Hall", "Marangozlar Salonu"),
     T("1770–1774: the city's carpenters build their guild hall off Chestnut Street",
       "1770–1774: şehrin marangozları Chestnut Caddesi yakınına lonca salonlarını yapar"),
     pop=PI(1770, 1773.9), cam=(CARP[0], CARP[1], 2.6)),
 seg(1774, 1775.9, 16, REV, PHL, T("The Continental Congress", "Kıta Kongresi"),
     T("5 September 1774: the First Continental Congress meets in Carpenters' Hall",
       "5 Eylül 1774: Birinci Kıta Kongresi Marangozlar Salonu'nda toplanır"),
     pop=PI(1774, 1775.9), cam=(CARP[0], CARP[1], 2.4), chapter=T("Revolution", "Devrim")),
 seg(1776, 1776.95, 22, REV, PHL, T("Independence", "Bağımsızlık"),
     T("4 July 1776: the Declaration of Independence is approved in the State House",
       "4 Temmuz 1776: Bağımsızlık Bildirgesi Eyalet Binası'nda kabul edilir"),
     pop=PI(1776, 1776.95), cam=(INDEP[0], INDEP[1], 2.2)),
 seg(1777, 1777.72, 15, REV, PHL, T("Congress Flees", "Kongre Kaçıyor"),
     T("11 September 1777: defeat at Brandywine; Congress flees the city",
       "11 Eylül 1777: Brandywine yenilgisi; Kongre şehirden kaçar"),
     pop=PI(1777, 1777.7), cam=(39.9480, -75.1600, 7.0)),
 seg(1777.73, 1777.82, 15, REV, PHL, T("The British March In", "İngilizler Şehre Giriyor"),
     T("26 September 1777: British troops occupy Philadelphia", "26 Eylül 1777: İngiliz birlikleri Philadelphia'yı işgal eder"),
     pop=15000, cam=(39.9530, -75.1550, 5.0)),
 seg(1777.82, 1778.3, 17, REV, PHL, T("Fort Mifflin Falls", "Mifflin Kalesi Düşüyor"),
     T("16 November 1777: after weeks of siege, the British take Fort Mifflin",
       "16 Kasım 1777: haftalarca süren kuşatmanın ardından İngilizler Mifflin Kalesi'ni alır"),
     pop=15000, cam=(39.9050, -75.1900, 9.0)),
 seg(1778.3, 1786.9, 16, REV, PHL, T("The British Leave", "İngilizler Gidiyor"),
     T("18 June 1778: the British leave; Congress is back on 2 July",
       "18 Haziran 1778: İngilizler ayrılır; Kongre 2 Temmuz'da geri döner"),
     pop=PI(1778.45, 1786.9), cam=(39.9500, -75.1500, 4.0)),
 seg(1787, 1789.9, 16, US, PHL, T("The Constitution", "Anayasa"),
     T("May–September 1787: the Constitutional Convention meets in the State House",
       "Mayıs–Eylül 1787: Anayasa Kurultayı Eyalet Binası'nda toplanır"),
     pop=PI(1787, 1789.9), cam=(INDEP[0], INDEP[1], 2.4)),
 seg(1790, 1792.9, 16, US, PHL, T("Capital of the Nation", "Ulusun Başkenti"),
     T("6 December 1790: Philadelphia becomes the US capital, until 1800",
       "6 Aralık 1790: Philadelphia ABD'nin başkenti olur; 1800'e kadar"),
     pop=PI(1790, 1792.9), cam=(39.9500, -75.1520, 4.0), chapter=T("Capital of a New Nation", "Yeni Bir Ulusun Başkenti")),
 seg(1793, 1793.95, 18, US, PHL, T("Yellow Fever", "Sarı Humma"),
     T("Aug–Nov 1793: yellow fever kills 5,000 or more; some 20,000 flee",
       "Ağustos–Kasım 1793: sarı humma 5.000'den fazla can alır; 20.000 kadar kişi kaçar"),
     pop=PI(1793, 1793.95), cam=(39.9500, -75.1490, 3.2)),
 seg(1794, 1811.9, 15, US, PHL, T("The Capital Moves On", "Başkent Taşınıyor"),
     T("1800: the federal government leaves for Washington, D.C.", "1800: federal hükümet Washington'a taşınır"),
     pop=PI(1794, 1811.9), cam=(39.9510, -75.1560, 5.0)),
 seg(1812, 1821.9, 16, US, PHL, T("Fairmount Water Works", "Fairmount Su İşletmesi"),
     T("1812–1815: steam pumps at Fairmount lift Schuylkill water for the city",
       "1812–1815: Fairmount'taki buhar pompaları şehre Schuylkill suyu basar"),
     pop=PI(1812, 1821.9), cam=(39.9600, -75.1750, 4.0), chapter=T("Workshop of the World", "Dünyanın Atölyesi")),
 seg(1822, 1828.9, 15, US, PHL, T("Water Wheels", "Su Çarkları"),
     T("1822: Fairmount Dam is complete; water wheels replace the steam engines",
       "1822: Fairmount Barajı tamamlanır; su çarkları buhar makinelerinin yerini alır"),
     pop=PI(1822, 1828.9), cam=(WATERW[0], WATERW[1] + 0.003, 2.6)),
 seg(1829, 1833.9, 15, US, PHL, T("Eastern State Penitentiary", "Eastern State Cezaevi"),
     T("25 October 1829: Eastern State Penitentiary opens on 11 acres",
       "25 Ekim 1829: Eastern State Cezaevi 11 akrelik alanda açılır"),
     pop=PI(1829, 1833.9), cam=(ESP[0], ESP[1], 3.0)),
 seg(1834, 1849.9, 16, US, PHL, T("To the Schuylkill", "Schuylkill'e Doğru"),
     T("1834: a railroad heads west; the built-up city spreads toward the Schuylkill",
       "1834: demiryolu batıya uzanır; yerleşim Schuylkill'e doğru yayılır"),
     pop=PI(1834, 1849.9), cam=(39.9530, -75.1600, 6.5)),
 seg(1850, 1853.9, 8, US, PHL, pop=121376, cam=(39.9600, -75.1550, 9.0)),
 seg(1854, 1859.9, 22, US, PHL, T("One City, One County", "Tek Şehir, Tek İlçe"),
     T("2 February 1854: the city absorbs all of Philadelphia County",
       "2 Şubat 1854: şehir, Philadelphia İlçesi'nin tamamını bünyesine katar"),
     pop=PI(1854, 1859.9), cam=(39.9900, -75.1500, 22.0), chapter=T("Consolidation", "Birleşme")),
 seg(1860, 1870.9, 15, US, PHL, T("Half a Million", "Yarım Milyon"),
     T("1860: the consolidated city counts 565,529 people", "1860: birleşik şehir 565.529 kişi sayar"),
     pop=PI(1860, 1870.9), cam=(39.9700, -75.1550, 14.0)),
 seg(1871, 1875.9, 16, US, PHL, T("A Tower at Centre Square", "Merkez Meydan'da Bir Kule"),
     T("1871: work begins on City Hall; the Navy Yard moves to League Island",
       "1871: Belediye Binası'nın yapımı başlar; Donanma Tersanesi League Adası'na taşınır"),
     pop=PI(1871, 1875.9), cam=(39.9300, -75.1650, 9.0)),
 seg(1876, 1880.9, 18, US, PHL, T("The Centennial", "Yüzüncü Yıl"),
     T("10 May 1876: the Centennial Exhibition opens in Fairmount Park",
       "10 Mayıs 1876: Yüzüncü Yıl Sergisi Fairmount Park'ta açılır"),
     pop=PI(1876, 1880.9), cam=(39.9800, -75.1900, 6.0)),
 seg(1881, 1893.9, 16, US, PHL, T("Broad Street Station", "Broad Street İstasyonu"),
     T("December 1881: the Pennsylvania Railroad opens Broad Street Station",
       "Aralık 1881: Pennsylvania Demiryolu Broad Street İstasyonu'nu açar"),
     pop=PI(1881, 1893.9), cam=(39.9530, -75.1700, 3.4)),
 seg(1894, 1900.9, 16, US, PHL, T("William Penn on Top", "Tepede William Penn"),
     T("1894: a 37 ft (11 m) statue of William Penn is raised onto City Hall's tower",
       "1894: 11 m'lik William Penn heykeli Belediye Binası'nın kulesine çıkarılır"),
     pop=PI(1894, 1900.9), cam=(CITYHALL[0], CITYHALL[1], 2.6)),
 seg(1901, 1906.9, 16, US, PHL, T("City Hall Is Finished", "Belediye Binası Bitti"),
     T("1901: City Hall is complete — 548 ft (167 m) to the top of Penn's hat",
       "1901: Belediye Binası tamam — Penn'in şapkasına kadar 167 m"),
     pop=PI(1901, 1906.9), cam=(CITYHALL[0], CITYHALL[1], 4.0)),
 seg(1907, 1917.9, 15, US, PHL, T("The El", "Havai Raylı"),
     T("March 1907: the Market Street El opens from 69th Street to City Hall",
       "Mart 1907: Market Street havai raylısı 69. Cadde'den Belediye Binası'na açılır"),
     pop=PI(1907, 1917.9), cam=(39.9580, -75.2000, 9.0), chapter=T("The Big City", "Büyük Şehir")),
 seg(1918, 1918.9, 14, US, PHL, T("The 1918 Flu", "1918 Gribi"),
     T("1918: the Spanish flu kills about 12,000 Philadelphians",
       "1918: İspanyol gribi yaklaşık 12.000 Philadelphialının ölümüne yol açar"),
     pop=PI(1918, 1918.9), cam=(39.9700, -75.1600, 13.0)),
 seg(1919, 1926.4, 16, US, PHL, T("A Temple on the Hill", "Tepedeki Tapınak"),
     T("1919: work starts on the Museum of Art on Fairmount; it opens in 1928",
       "1919: Fairmount tepesinde Sanat Müzesi'nin inşaatı başlar; 1928'de açılır"),
     pop=PI(1919, 1926.4), cam=(39.9600, -75.1720, 3.6)),
 seg(1926.5, 1932.9, 16, US, PHL, T("A Bridge to Camden", "Camden'a Bir Köprü"),
     T("1 July 1926: the Delaware bridge opens — the world's longest suspension span",
       "1 Temmuz 1926: Delaware köprüsü açılır — dünyanın en uzun asma köprü açıklığı"),
     pop=PI(1926.5, 1932.9), cam=(BFB[0], BFB[1] - 0.004, 4.0)),
 seg(1933, 1949.9, 15, US, PHL, T("30th Street Station", "30. Cadde İstasyonu"),
     T("1933: 30th Street Station opens on the west bank of the Schuylkill",
       "1933: 30. Cadde İstasyonu Schuylkill'in batı kıyısında açılır"),
     pop=PI(1933, 1949.9), cam=(STN30[0], STN30[1] + 0.004, 3.4)),
 seg(1950, 1952.2, 16, US, PHL, T("Two Million People", "İki Milyon İnsan"),
     T("1950: the census counts 2,071,605 people — the city's all-time peak",
       "1950: sayım 2.071.605 kişi sayar — şehrin tüm zamanların zirvesi"),
     pop=PI(1950, 1952.2), cam=(39.9900, -75.1400, 26.0)),
 seg(1952.3, 1956.9, 15, US, PHL, T("The Old Station Goes", "Eski İstasyon Yıkılıyor"),
     T("27 April 1952: Broad Street Station closes; it is torn down in 1953",
       "27 Nisan 1952: Broad Street İstasyonu kapanır; 1953'te yıkılır"),
     pop=PI(1952.3, 1956.9), cam=(39.9530, -75.1690, 3.0)),
 seg(1957, 1970.9, 16, US, PHL, T("Walt Whitman Bridge", "Walt Whitman Köprüsü"),
     T("16 May 1957: the Walt Whitman Bridge opens over the Delaware",
       "16 Mayıs 1957: Walt Whitman Köprüsü Delaware üzerinde açılır"),
     pop=PI(1957, 1970.9), cam=(39.9150, -75.1450, 7.0)),
 seg(1971, 1975.9, 14, US, PHL, T("The Prison Closes", "Cezaevi Kapanıyor"),
     T("1971: Eastern State Penitentiary closes after 142 years",
       "1971: Eastern State Cezaevi 142 yıl sonra kapanır"),
     pop=PI(1971, 1975.9), cam=(ESP[0], ESP[1], 4.0)),
 seg(1976, 1984.9, 16, US, PHL, T("The Bicentennial", "İki Yüzüncü Yıl"),
     T("4 July 1976: the nation marks 200 years where independence was declared",
       "4 Temmuz 1976: ulus, bağımsızlığın ilan edildiği yerde 200. yılını kutlar"),
     pop=PI(1976, 1984.9), cam=(INDEP[0], INDEP[1] - 0.004, 4.5)),
 seg(1985, 1989.9, 18, US, PHL, T("Above Penn's Hat", "Penn'in Şapkasının Üstünde"),
     T("1987: One Liberty Place, 945 ft, ends the custom of building no higher than Penn",
       "1987: 288 m'lik One Liberty Place, Penn'den yükseğe çıkmama geleneğine son verir"),
     pop=PI(1985, 1989.9), cam=(39.9530, -75.1680, 3.6), chapter=T("A New Skyline", "Yeni Bir Silüet")),
 seg(1990, 2006.9, 15, US, PHL, T("The Navy Yard Closes", "Tersane Kapanıyor"),
     T("1995: the Navy Yard closes after 124 years on League Island",
       "1995: Donanma Tersanesi League Adası'ndaki 124 yılın ardından kapanır"),
     pop=PI(1990, 2006.9), cam=(39.9150, -75.1750, 8.0)),
 seg(2007, 2017.9, 15, US, PHL, T("The Comcast Center", "Comcast Center"),
     T("2007: the Comcast Center tops out and takes Pennsylvania's height record",
       "2007: Comcast Center tamamlanır ve Pennsylvania'nın yükseklik rekorunu alır"),
     pop=PI(2007, 2017.9), cam=(39.9545, -75.1680, 3.4)),
 seg(2018, 2022.9, 16, US, PHL, T("1,121 Feet", "342 Metre"),
     T("2018: the 1,121 ft (342 m) Comcast Technology Center becomes the tallest in the state",
       "2018: 342 m'lik Comcast Technology Center eyaletin en yüksek binası olur"),
     pop=PI(2018, 2022.9), cam=(CTC[0], CTC[1] + 0.002, 4.0), chapter=T("Philadelphia Today", "Bugünün Philadelphia'sı")),
 seg(2023, 2026, 26, TODAY, PHL, T("Philadelphia Today", "Bugünün Philadelphia'sı"),
     T("From a riverside grid of 1682 to 1,574,281 people in July 2025",
       "1682'nin nehir kıyısı ızgarasından Temmuz 2025'te 1.574.281 kişiye"),
     pop=PI(2023, 2026), cam=(39.9900, -75.1350, 30.0)),
]

districts = [
 {"name": "Swedish farms at Wicaco (≈)", "style": "celtic", "poly": L(WICACO), "from": 1660, "to": 1700, "density": 0.35, "grain_m": 70,
  "grow_from": list(GLORIA)},
 {"name": "First houses on the Delaware (≈)", "style": "georgian", "poly": L(EARLY), "from": 1682.85, "to": 1700, "density": 0.7,
  "grain_m": 45, "grid_deg": 0, "grow_from": [MARKET, FRONT]},
 {"name": "Colonial city, east of 7th Street (≈)", "style": "georgian", "poly": L(COLONIAL), "holes": [L(EARLY)], "from": 1700, "to": 1776,
  "density": 0.8, "grain_m": 45, "grid_deg": 0, "grow_from": [MARKET, FRONT]},
 {"name": "Northern Liberties (≈)", "style": "georgian", "poly": L(NLIB), "from": 1730, "to": 1800, "density": 0.7, "grain_m": 50,
  "grid_deg": 0, "grow_from": [VINE, -75.1420]},
 {"name": "Southwark (≈)", "style": "georgian", "poly": L(SWARK), "from": 1730, "to": 1800, "density": 0.7, "grain_m": 50,
  "grid_deg": 0, "grow_from": [SOUTH, -75.1440]},
 {"name": "West to Centre Square (≈)", "style": "georgian", "poly": L(TO_BROAD), "from": 1790, "to": 1830, "density": 0.75, "grain_m": 50,
  "grid_deg": 0, "grow_from": [MARKET, st(7)]},
 {"name": "Centre Square to the Schuylkill (≈)", "style": "georgian", "poly": L(TO_SCH), "from": 1815, "to": 1855, "density": 0.7,
  "grain_m": 55, "grid_deg": 0, "grow_from": [MARKET, CITYHALL[1]]},
 {"name": "Northern districts (Spring Garden, Kensington ≈)", "style": "georgian", "poly": L(LIBERTIES), "holes": [L(h) for h in LIB_HOLES],
  "from": 1800, "to": 1853, "density": 0.65, "grain_m": 60, "grid_deg": 0, "grow_from": [VINE, -75.1450]},
 {"name": "Southern districts (Moyamensing ≈)", "style": "georgian", "poly": L(SOUTHERN), "holes": [L(SWARK)], "from": 1800, "to": 1853,
  "density": 0.6, "grain_m": 60, "grid_deg": 0, "grow_from": [SOUTH, -75.1500]},
 {"name": "Rowhouse city (≈)", "style": "victorian", "poly": L(ROW), "holes": [L(CENTER), L(LIBERTIES), L(SOUTHERN), L(SWARK), L(NLIB), L(FAIRMOUNT_PARK)],
  "from": 1854, "to": 1925, "density": 0.8, "grain_m": 68, "grid_deg": 0, "grow_from": list(CITYHALL)},
 {"name": "Navy Yard, League Island (≈)", "style": "industrial", "poly": L(NAVY_Y), "from": 1871, "to": 1900, "density": 0.5, "grain_m": 110,
  "grow_from": list(NAVY)},
 {"name": "Camden (≈, across the river)", "style": "victorian", "poly": L(CAMDEN), "from": 1850, "to": 1930, "density": 0.5, "grain_m": 95,
  "grow_from": [39.9450, -75.1220]},
 {"name": "Outer neighbourhoods (≈)", "style": "suburb", "poly": L(COUNTY), "holes": [L(ROW), L(NAVY_Y), L(FAIRMOUNT_PARK), L(WISSAHICKON), L(CAMDEN)],
  "from": 1900, "to": 1975, "density": 0.5, "grain_m": 125, "grow_from": list(CITYHALL)},
 {"name": "Penn Center (≈)", "style": "modern", "poly": L(PENNCTR), "from": 1953.5, "to": 1970, "density": 0.85, "grain_m": 60,
  "grid_deg": 0, "grow_from": [39.9535, -75.1660]},
 {"name": "Center City towers (≈)", "style": "highrise", "poly": L(HIGH), "holes": [L(PENNCTR)], "from": 1986, "to": 2020, "density": 0.6,
  "grain_m": 75, "grid_deg": 0, "grow_from": list(OLP)},
]


def wall(name, path, built, removed, **kw):
    d = {"name": name, "path": L(path), "built": built, "removed": removed, "height": kw.get("height", "low"), "towers_m": kw.get("towers", 0)}
    return d


walls = []

bridges = [
 {"name": "Benjamin Franklin Bridge (≈ ends)", "path": [[39.95480, -75.14080], [39.95080, -75.12750]], "built": 1926.5, "style": "modern", "width_m": 39},
 {"name": "Walt Whitman Bridge (≈ ends)", "path": [[39.90880, -75.13950], [39.90180, -75.12000]], "built": 1957.37, "style": "modern", "width_m": 34},
]

roads = [
 {"name": "High (Market) Street (≈)", "path": L([(MARKET, -75.1405), (MARKET, -75.1790)]), "from": 1682.8, "kind": "avenue", "width_m": 30, "draw_s": 4},
 {"name": "Broad Street (≈)", "path": L([(39.9150, CITYHALL[1] + 0.0040), (SOUTH, CITYHALL[1] + 0.0010), (CITYHALL[0], CITYHALL[1]),
                                         (VINE, CITYHALL[1] - 0.0003), (40.0300, -75.1500)]), "from": 1682.8, "kind": "avenue", "width_m": 30, "draw_s": 4},
 {"name": "Pennsylvania Railroad viaduct (≈)", "path": L([(39.9533, -75.1660), (39.9540, -75.1790)]), "from": 1881.9, "to": 1953.5,
  "kind": "rail", "width_m": 26},
 {"name": "Market Street El (≈)", "path": L([(39.9553, -75.1840), (39.9590, -75.2100), (39.9620, -75.2450), (39.9620, -75.2560)]),
  "from": 1907.18, "kind": "rail", "width_m": 20},
 {"name": "Benjamin Franklin Parkway (≈)", "path": L([(39.9545, -75.1650), (39.9600, -75.1720), (39.9645, -75.1790)]), "from": 1917,
  "kind": "avenue", "width_m": 40, "draw_s": 3},
]

C_ = lambda w, r: {"wall": w, "roof": r}
BRICK = "#a8573e"
landmarks = [
 {"type": "church", "name": T("Gloria Dei (Old Swedes')", "Gloria Dei (Eski İsveçliler)"), "at": list(GLORIA), "built": 1698, "rise_s": 6,
  "size_m": [30, 14, 14], "rot_deg": 0, "colors": C_(BRICK, "#5a4a44")},
 {"type": "church", "name": T("Christ Church", "Christ Kilisesi"), "at": list(CHRIST), "built": 1727, "rise_s": 8,
  "size_m": [36, 18, 18], "rot_deg": 0, "colors": C_(BRICK, "#4f5a60")},
 {"type": "spire_tower", "name": T("Christ Church steeple", "Christ Kilisesi kulesi"), "at": [CHRIST[0], CHRIST[1] - 0.00028], "built": 1754, "rise_s": 6,
  "size_m": [9, 9, 60], "colors": C_("#e8e2d4", "#e8e2d4")},
 {"type": "parliament", "name": T("Pennsylvania State House", "Pennsylvania Eyalet Binası"), "at": list(INDEP), "built": 1732, "rise_s": 14,
  "size_m": [33, 14, 14], "scale": 1.4, "rot_deg": 0, "colors": C_(BRICK, "#4f5a60")},
 {"type": "clocktower", "name": T("State House tower", "Eyalet Binası kulesi"), "at": [INDEP[0] - 0.00012, INDEP[1]], "built": 1752, "rise_s": 6,
  "size_m": [9, 9, 50], "colors": C_(BRICK, "#e8e2d4")},
 {"type": "box", "name": T("Carpenters' Hall", "Marangozlar Salonu"), "at": list(CARP), "built": 1770, "rise_s": 8, "size_m": [20, 20, 12],
  "scale": 1.4, "colors": C_(BRICK, "#4f5a60")},
 {"type": "fort", "name": T("Fort Mifflin", "Mifflin Kalesi"), "at": list(MIFFLIN), "built": 1771, "rise_s": 6, "size_m": [180, 140, 8],
  "colors": {"wall": "#b9ad94"}},
 {"type": "box", "name": T("Fairmount Water Works", "Fairmount Su İşletmesi"), "at": list(WATERW), "built": 1812, "rise_s": 8,
  "size_m": [60, 22, 10], "scale": 1.3, "rot_deg": 70, "colors": C_("#e8e2d4", "#5f666f")},
 {"type": "fort", "name": T("Eastern State Penitentiary", "Eastern State Cezaevi"), "at": list(ESP), "built": 1822, "rise_s": 12,
  "size_m": [210, 210, 10], "colors": {"wall": "#9a8f80"}},
 {"type": "parliament", "name": T("City Hall", "Belediye Binası"), "at": list(CITYHALL), "built": 1871, "rise_s": 30,
  "size_m": [145, 140, 34], "scale": 1.0, "colors": C_("#e3dccb", "#4f5a60")},
 {"type": "clocktower", "name": T("City Hall tower", "Belediye Binası kulesi"), "at": [CITYHALL[0] - 0.00055, CITYHALL[1]], "built": 1880,
  "rise_s": 20, "size_m": [27, 27, 167], "colors": C_("#e3dccb", "#c9a94a")},
 {"type": "station", "name": T("Broad Street Station (≈)", "Broad Street İstasyonu (≈)"), "at": [39.95330, -75.16560], "built": 1881.9,
  "removed": 1953.5, "rise_s": 8, "size_m": [180, 95, 28], "rot_deg": 0, "colors": C_(BRICK, "#5f666f")},
 {"type": "temple", "name": T("Philadelphia Museum of Art", "Philadelphia Sanat Müzesi"), "at": list(PMA), "built": 1919, "rise_s": 40,
  "size_m": [190, 150, 30], "rot_deg": 35, "colors": C_("#e6c99a", "#3f7f87")},
 {"type": "station", "name": T("30th Street Station", "30. Cadde İstasyonu"), "at": list(STN30), "built": 1927, "rise_s": 30,
  "size_m": [195, 100, 30], "rot_deg": 0, "colors": C_("#e3dccb", "#5f666f")},
 {"type": "skyscraper", "name": T("One Liberty Place", "One Liberty Place"), "at": list(OLP), "built": 1985.4, "rise_s": 10,
  "size_m": [55, 55, 288], "colors": {"wall": "#7f97a8"}},
 {"type": "skyscraper", "name": T("Comcast Center (≈ position)", "Comcast Center (≈ konum)"), "at": [39.95460, -75.16860], "built": 2005.5,
  "rise_s": 10, "size_m": [60, 45, 297], "colors": {"wall": "#8fa3ae"}},
 {"type": "skyscraper", "name": T("Comcast Technology Center", "Comcast Technology Center"), "at": list(CTC), "built": 2014.5, "rise_s": 12,
  "size_m": [55, 55, 342], "colors": {"wall": "#a7b6bf"}},
]

fires = []
smoke = [
 {"at": list(MIFFLIN), "from": 1777.82, "to": 1777.88, "scale": 1.2},
]
camps = [
 {"poly": L(rect(39.9600, -75.1700, 39.9700, -75.1500)), "from": 1777.74, "to": 1778.46, "count": 180},
]
open_spaces = [
 {"name": "Fairmount Park (≈)", "poly": L(FAIRMOUNT_PARK)},
 {"name": "Wissahickon (≈)", "poly": L(WISSAHICKON)},
 {"name": "Franklin Square (≈)", "poly": L(SQ(FRANKLIN_SQ))},
 {"name": "Washington Square (≈)", "poly": L(SQ(WASHINGTON_SQ))},
 {"name": "Rittenhouse Square (≈)", "poly": L(SQ(RITTENHOUSE_SQ))},
 {"name": "Logan Square (≈)", "poly": L(SQ(LOGAN_SQ))},
]

labels = [
 {"text": T("DELAWARE RIVER", "DELAWARE NEHRİ"), "at": [39.9380, -75.1330], "kind": "water", "from": 1600},
 {"text": T("SCHUYLKILL RIVER", "SCHUYLKILL NEHRİ"), "at": [39.9450, -75.1880], "kind": "water", "from": 1600},
 {"text": T("Shackamaxon", "Shackamaxon"), "at": list(TREATY), "kind": "place", "from": 1600, "to": 1645},
 {"text": T("LENAPE COUNTRY", "LENAPE ÜLKESİ"), "at": [39.9800, -75.1800], "kind": "region", "from": 1600, "to": 1645},
 {"text": T("Wicaco", "Wicaco"), "at": list(GLORIA), "kind": "place", "from": 1646, "to": 1680.9},
 {"text": T("PENNSYLVANIA", "PENNSYLVANIA"), "at": [39.9750, -75.1800], "kind": "region", "from": 1681, "to": 1682.5},
 {"text": T("PHILADELPHIA", "PHILADELPHIA"), "at": [39.9520, -75.1600], "kind": "region", "from": 1682.5, "to": 1682.8},
 {"text": T("Penn Treaty site", "Penn Antlaşması yeri"), "at": list(TREATY), "kind": "place", "from": 1682.8, "to": 1683.9},
 {"text": T("Old Swedes'", "Eski İsveçliler"), "at": list(GLORIA), "from": 1700, "to": 1726, "lift_m": 25},
 {"text": T("Christ Church", "Christ Kilisesi"), "at": list(CHRIST), "from": 1727, "to": 1731.9, "lift_m": 30},
 {"text": T("State House", "Eyalet Binası"), "at": list(INDEP), "from": 1732, "to": 1753.9, "lift_m": 45},
 {"text": T("Christ Church", "Christ Kilisesi"), "at": list(CHRIST), "from": 1754, "to": 1769.9, "lift_m": 70},
 {"text": T("Carpenters' Hall", "Marangozlar Salonu"), "at": list(CARP), "from": 1770, "to": 1775.9, "lift_m": 25},
 {"text": T("Independence Hall", "Bağımsızlık Salonu"), "at": list(INDEP), "from": 1776, "to": 1776.95, "lift_m": 45},
 {"text": T("Fort Mifflin", "Mifflin Kalesi"), "at": list(MIFFLIN), "kind": "place", "from": 1777.82, "to": 1778.3},
 {"text": T("Independence Hall", "Bağımsızlık Salonu"), "at": list(INDEP), "from": 1787, "to": 1789.9, "lift_m": 45},
 {"text": T("Fairmount", "Fairmount"), "at": list(WATERW), "kind": "place", "from": 1812, "to": 1828.9},
 {"text": T("Eastern State", "Eastern State"), "at": list(ESP), "kind": "place", "from": 1829, "to": 1833.9},
 {"text": T("CENTRE SQUARE", "MERKEZ MEYDAN"), "at": [CITYHALL[0] + 0.0010, CITYHALL[1]], "kind": "region", "from": 1834, "to": 1849.9},
 {"text": T("PHILADELPHIA COUNTY", "PHILADELPHIA İLÇESİ"), "at": [40.0300, -75.1300], "kind": "region", "from": 1854, "to": 1859.9},
 {"text": T("League Island", "League Adası"), "at": list(NAVY), "kind": "place", "from": 1871, "to": 1875.9},
 {"text": T("City Hall", "Belediye Binası"), "at": list(CITYHALL), "kind": "place", "from": 1871, "to": 1875.9},
 {"text": T("FAIRMOUNT PARK", "FAIRMOUNT PARK"), "at": [39.9880, -75.1930], "kind": "region", "from": 1876, "to": 1880.9},
 {"text": T("Broad Street Station", "Broad Street İstasyonu"), "at": [39.95330, -75.16560], "kind": "place", "from": 1881.9, "to": 1893.9},
 {"text": T("City Hall", "Belediye Binası"), "at": list(CITYHALL), "from": 1894, "to": 1906.9, "lift_m": 190},
 {"text": T("WEST PHILADELPHIA", "BATI PHILADELPHIA"), "at": [39.9580, -75.2200], "kind": "region", "from": 1907, "to": 1917.9},
 {"text": T("Museum of Art", "Sanat Müzesi"), "at": list(PMA), "kind": "place", "from": 1919, "to": 1926.4},
 {"text": T("CAMDEN", "CAMDEN"), "at": [39.9420, -75.1100], "kind": "region", "from": 1926.5, "to": 1932.9},
 {"text": T("30th Street Station", "30. Cadde İstasyonu"), "at": list(STN30), "kind": "place", "from": 1933, "to": 1949.9},
 {"text": T("Penn Center", "Penn Center"), "at": [39.95350, -75.16700], "kind": "place", "from": 1952.3, "to": 1956.9},
 {"text": T("Eastern State", "Eastern State"), "at": list(ESP), "kind": "place", "from": 1971, "to": 1975.9},
 {"text": T("Independence Hall", "Bağımsızlık Salonu"), "at": list(INDEP), "kind": "place", "from": 1976, "to": 1984.9},
 {"text": T("One Liberty Place", "One Liberty Place"), "at": list(OLP), "from": 1987, "to": 1989.9, "lift_m": 310},
 {"text": T("Navy Yard", "Donanma Tersanesi"), "at": list(NAVY), "kind": "place", "from": 1990, "to": 2006.9},
 {"text": T("Comcast Technology Center", "Comcast Technology Center"), "at": list(CTC), "from": 2018, "to": 2022.9, "lift_m": 360},
 {"text": T("CAMDEN", "CAMDEN"), "at": [39.9420, -75.1100], "kind": "region", "from": 2023},
]

city = {
 "slug": "philadelphia", "seed": 1682, "long_ok": True,
 "name": T("Philadelphia", "Philadelphia"), "intro": T("From 1682 to Today", "1682'den Bugüne"), "intro_seconds": 4.5,
 "geo": {"bbox": [39.70, -75.55, 40.25, -74.75], "cell_m": 110, "core_bbox": [39.900, -75.205, 39.990, -75.110], "core_cell_m": 30,
         "rivers_keep": ["Delaware", "Schuylkill"], "lakes_from": 1900},
 "view": {"azimuth_deg": 270, "pitch_deg": 46, "fov": 34},
 "render": {"vertical_exaggeration": 3.0},
 "segments": S,
 "districts": districts, "walls": walls, "bridges": bridges, "roads": roads, "landmarks": landmarks,
 "fires": fires, "camps": camps, "smoke": smoke, "open_spaces": open_spaces, "labels": labels,
 "youtube": {
  "title": T("Philadelphia: 400 Years in 15 Minutes (3D Timelapse)", "Philadelphia: 15 Dakikada 400 Yıl (3D Timelapse)"),
  "description": T(
   "Lenape country on the Delaware, Swedish farmers at Wicaco, and in 1682 William Penn's grid between two rivers. Watch "
   "Philadelphia grow from a riverside town into the city where independence was declared in 1776 and the Constitution written "
   "in 1787, the nation's capital of the 1790s, the 'Workshop of the World', a consolidated city of more than two million in "
   "1950 and today's skyline: Christ Church, Independence Hall, Carpenters' Hall, Fort Mifflin, the Fairmount Water Works, "
   "Eastern State Penitentiary, City Hall, the Museum of Art, the Benjamin Franklin Bridge and the Comcast towers, with the "
   "year and the population on screen.",
   "Delaware kıyısında Lenape ülkesi, Wicaco'da İsveçli çiftçiler ve 1682'de William Penn'in iki nehir arasındaki ızgarası. "
   "Philadelphia'nın nehir kıyısındaki bir kasabadan 1776'da bağımsızlığın ilan edildiği, 1787'de Anayasa'nın yazıldığı şehre, "
   "1790'ların başkentine, 'Dünyanın Atölyesi'ne, 1950'de iki milyonu aşan birleşik bir şehre ve bugünün siluetine büyümesini "
   "izleyin: Christ Kilisesi, Bağımsızlık Salonu, Marangozlar Salonu, Mifflin Kalesi, Fairmount Su İşletmesi, Eastern State "
   "Cezaevi, Belediye Binası, Sanat Müzesi, Benjamin Franklin Köprüsü ve Comcast kuleleri; yıl ve nüfus ekranda."),
  "tags": ["philadelphia history", "history of philadelphia", "philadelphia", "independence hall", "william penn", "3d timelapse",
           "city evolution", "how philadelphia grew", "philadelphia timelapse", "american history", "liberty bell", "urban history",
           "colonial america", "philly"],
  "hashtags": ["#Philadelphia", "#History", "#Timelapse"],
  "playlist": T("Cities of North America", "Kuzey Amerika Şehirleri"),
  "playlist_desc": T("North American cities rebuilt in 3D, from the first house to the skyline.",
                     "Kuzey Amerika şehirleri 3D olarak, ilk evden siluete."),
  "thumb": {"line1": T("Philadelphia", "Philadelphia"), "line2": T("1682 → TODAY", "1682 → BUGÜN"),
            "line3": T("From Penn's grid to skyline", "Penn'in ızgarasından silüete"),
            "extra": "&mood=golden&pitch=30&az=270&cam=39.9525,-75.1600,6.0"},
 },
 "sources": json.load(open(os.path.join(HERE, "_sources.json"))),
}
total = sum(s_["seconds"] for s_ in S)
mins = round(total / 60)
years = 2026 - 1682
city["intro"] = T(f"{years} Years in {mins} Minutes", f"{mins} Dakikada {years} Yıl")
city["youtube"]["title"] = T(f"Philadelphia: {years} Years in {mins} Minutes (3D Timelapse)",
                             f"Philadelphia: {mins} Dakikada {years} Yıl (3D Timelapse)")
json.dump(city, open(os.path.join(HERE, "city.json"), "w"), ensure_ascii=False, indent=1)
print("segments", len(S), "duration", total, "s =", f"{total // 60}:{total % 60:02d}")
