"""Builds cities/vienna/city.json. Every date/figure is from research.md (sources listed there).
Run: python3 cities/vienna/_build.py
Wall courses, district outlines, camps and the Danube Island strip are simplified traces (marked ≈ in research.md).
The Danube is drawn in its modern, straightened bed for the whole film (simplification: before 1870–1875 it ran in
many shifting arms); the New Danube channel is flooded only from 1988 (timed_water), the year Danube Island was finished."""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

T = lambda en, tr: {"en": en, "tr": tr}
HERE = os.path.dirname(os.path.abspath(__file__))
rect = lambda s, w, n, e: [(s, w), (n, w), (n, e), (s, e)]


def L(pts):
    return [[round(a, 5), round(b, 5)] for a, b in pts]


def scale(pts, c, f):
    return [(c[0] + (a - c[0]) * f, c[1] + (b - c[1]) * f) for a, b in pts]


# ------------------------------------------------------------------ geography (lat, lon); ≈ traces, see research.md
STEPHANSDOM = (48.2085, 16.3730)
# Roman legionary fortress, ≈20 ha: Tiefer Graben (W), Graben (S), Rotenturmstraße (E), Salzgries terrace (N)
CAMP = [(48.2095, 16.3684), (48.2089, 16.3730), (48.2122, 16.3742), (48.2130, 16.3688)]
CANABAE = [(48.2089, 16.3684), (48.2060, 16.3660), (48.2048, 16.3700), (48.2060, 16.3740), (48.2085, 16.3745)]
CIVIL_TOWN = [(48.2005, 16.3800), (48.1990, 16.3870), (48.1960, 16.3880), (48.1965, 16.3800)]   # 3rd district (Rennweg)
# Medieval wall (c. 1200) and the later bastioned fortress: just inside today's Ring, closed along the Danube Canal
WALL = [(48.2155, 16.3690), (48.2140, 16.3640), (48.2128, 16.3618), (48.2100, 16.3618), (48.2075, 16.3628), (48.2050, 16.3645),
        (48.2038, 16.3672), (48.2036, 16.3705), (48.2042, 16.3745), (48.2058, 16.3780), (48.2085, 16.3800), (48.2108, 16.3800),
        (48.2110, 16.3776), (48.2128, 16.3745), (48.2143, 16.3715)]
WALL_RING = WALL + [WALL[0]]
CORE_C = (48.2092, 16.3712)
FORT = scale(WALL, CORE_C, 1.06)
FORT_RING = FORT + [FORT[0]]
# Ringstraße zone (former glacis) — outer edge, closed along the canal
RING_OUT = [(48.2178, 16.3700), (48.2160, 16.3598), (48.2125, 16.3553), (48.2080, 16.3560), (48.2045, 16.3582), (48.2012, 16.3640),
            (48.2002, 16.3690), (48.1999, 16.3755), (48.2030, 16.3810), (48.2075, 16.3835), (48.2108, 16.3850), (48.2120, 16.3800),
            (48.2132, 16.3760), (48.2150, 16.3730), (48.2168, 16.3708)]
# Ring boulevard centre line (≈ 5.3 km), from the canal at Schottenring round to the canal at Urania
RING_ROAD = [(48.2172, 16.3700), (48.2150, 16.3615), (48.2120, 16.3590), (48.2085, 16.3592), (48.2052, 16.3612), (48.2030, 16.3655),
             (48.2022, 16.3700), (48.2020, 16.3750), (48.2040, 16.3790), (48.2075, 16.3815), (48.2110, 16.3838)]
# Danube Canal, south/west bank (≈), Spittelau → Rossau → Urania → St Marx
CANAL_N = [(48.2335, 16.3595), (48.2300, 16.3620), (48.2240, 16.3650), (48.2185, 16.3690)]
CANAL_S = [(48.2112, 16.3850), (48.2095, 16.3920), (48.2060, 16.3975), (48.2005, 16.4030), (48.1945, 16.4122)]
# Linienwall (1704), 13.5 km from the canal at St Marx to Lichtental, just inside today's Gürtel
LINIEN = [(48.1945, 16.4122), (48.1880, 16.4000), (48.1858, 16.3900), (48.1865, 16.3790), (48.1840, 16.3680), (48.1815, 16.3570),
          (48.1850, 16.3460), (48.1905, 16.3400), (48.1965, 16.3378), (48.2040, 16.3385), (48.2110, 16.3418), (48.2180, 16.3442),
          (48.2245, 16.3492), (48.2295, 16.3545), (48.2340, 16.3601)]
LINIEN_POLY = LINIEN + CANAL_N[1:] + CANAL_S       # suburbs between the glacis and the Linienwall (holes: RING_OUT)
GUERTEL = [(p[0] + (p[0] - CORE_C[0]) * 0.025, p[1] + (p[1] - CORE_C[1]) * 0.025) for p in LINIEN]
EARLY_SUB = scale(RING_OUT, CORE_C, 1.55)           # suburbs before 1683 (≈, a belt ~600 m beyond the glacis)
# island between the canal and the Danube
LEOPOLDSTADT = [(48.2125, 16.3790), (48.2185, 16.3720), (48.2260, 16.3700), (48.2290, 16.3800), (48.2230, 16.3900), (48.2180, 16.3930),
                (48.2120, 16.3880)]
ISLAND_19C = [(48.2120, 16.3880), (48.2185, 16.3720), (48.2300, 16.3660), (48.2400, 16.3660), (48.2470, 16.3700), (48.2440, 16.3820),
              (48.2330, 16.3960), (48.2240, 16.4020), (48.2170, 16.3990)]
AUGARTEN = [(48.2235, 16.3705), (48.2300, 16.3735), (48.2290, 16.3810), (48.2225, 16.3780)]
PRATER = [(48.2170, 16.3985), (48.2205, 16.4110), (48.2060, 16.4330), (48.1920, 16.4520), (48.1870, 16.4450), (48.2000, 16.4200),
          (48.2090, 16.4010)]
SCHOENBRUNN_P = [(48.1860, 16.3045), (48.1860, 16.3175), (48.1765, 16.3175), (48.1765, 16.3045)]
BELVEDERE_G = [(48.1935, 16.3765), (48.1920, 16.3820), (48.1905, 16.3815), (48.1918, 16.3758)]
VORORTE = [(48.2500, 16.3650), (48.2560, 16.3420), (48.2450, 16.3150), (48.2300, 16.3000), (48.2150, 16.2880), (48.2000, 16.2820),
           (48.1880, 16.2800), (48.1780, 16.2900), (48.1700, 16.3100), (48.1640, 16.3400), (48.1620, 16.3700), (48.1680, 16.3950),
           (48.1800, 16.4100), (48.1900, 16.4150), (48.1935, 16.4100)] + list(reversed(LINIEN))[1:] + [(48.2400, 16.3640)]
FLORIDSDORF = [(48.2440, 16.3900), (48.2580, 16.3760), (48.2800, 16.3800), (48.2900, 16.4100), (48.2750, 16.4400), (48.2550, 16.4300),
               (48.2380, 16.4100)]
# Danube centre line (≈) — used for the Danube Island strip on its north-east side
DANUBE = [(48.2830, 16.3530), (48.2650, 16.3680), (48.2470, 16.3830), (48.2350, 16.3950), (48.2270, 16.4080), (48.2160, 16.4220),
          (48.2040, 16.4380), (48.1900, 16.4560), (48.1750, 16.4780)]


def side_band(line, d0_m, d1_m):
    """Band on the north-east (left-hand, looking downstream) side of a polyline, between d0 and d1 metres."""
    kx = 111.32 * math.cos(math.radians(48.21)); kz = 110.574
    out0, out1 = [], []
    for i, (a, b) in enumerate(line):
        p, q = line[max(0, i - 1)], line[min(len(line) - 1, i + 1)]
        dx, dz = (q[1] - p[1]) * kx, (q[0] - p[0]) * kz; l = math.hypot(dx, dz)
        nx, nz = -dz / l, dx / l            # left normal (x = east, z = north)
        if nz < 0: nx, nz = -nx, -nz        # make it point north-east
        out0.append((a + nz * d0_m / 1000 / kz, b + nx * d0_m / 1000 / kx))
        out1.append((a + nz * d1_m / 1000 / kz, b + nx * d1_m / 1000 / kx))
    return out0 + list(reversed(out1))


from _danube import trace
NEW_DANUBE, ISLAND = trace(os.path.join(HERE, 'geo.json'))
DONAUINSEL = ISLAND or side_band(DANUBE[1:], 120, 700)   # floodplain (1875), later Danube Island + New Danube
OUTER = [(48.3000, 16.3450), (48.3000, 16.4300), (48.2750, 16.4900), (48.2450, 16.5400), (48.2100, 16.5400), (48.2000, 16.4950),
         (48.1750, 16.4750), (48.1450, 16.4300), (48.1330, 16.3600), (48.1300, 16.2800), (48.1480, 16.2500), (48.1750, 16.2600),
         (48.1950, 16.2650), (48.2200, 16.2850), (48.2500, 16.3050), (48.2700, 16.3300)]
LAINZ = [(48.1800, 16.2200), (48.1820, 16.2700), (48.1650, 16.2750), (48.1550, 16.2450), (48.1620, 16.2150)]
LOBAU = [(48.2000, 16.4700), (48.1950, 16.5300), (48.1700, 16.5500), (48.1600, 16.5050), (48.1750, 16.4700)]
DONAU_CITY = rect(48.2300, 16.4085, 48.2365, 16.4170)
SEESTADT = rect(48.2200, 16.4950, 48.2310, 16.5150)
HBF_Q = rect(48.1840, 16.3790, 48.1890, 16.3880)

# Danube upstream (Klosterneuburg → Tulln) and downstream (→ Fischamend): the OSM river relation does not close inside the
# bbox, so these stretches are drawn as river lines (≈ course, 350 m wide)
GEO_EDITS = [
 {"op": "river", "path": L([(48.3060, 16.3388), (48.3150, 16.3290), (48.3300, 16.3080), (48.3460, 16.2850), (48.3520, 16.2550),
                            (48.3450, 16.2200), (48.3380, 16.1700), (48.3350, 16.1100), (48.3330, 16.0400)]), "width_m": 350},
 {"op": "river", "path": L([(48.1570, 16.5220), (48.1450, 16.5600), (48.1320, 16.6000), (48.1290, 16.6400), (48.1350, 16.6800),
                            (48.1400, 16.7300)]), "width_m": 350},
]

# ------------------------------------------------------------------ population (research.md): sourced anchors, log-interpolated
ANCH = [(1500, 22500), (1637, 60000), (1683, 90000), (1710, 113800), (1754, 175460), (1783, 247753), (1793, 271800), (1830, 401200),
        (1840, 469400), (1850, 551300), (1857, 683000), (1869, 900998), (1880, 1162591), (1890, 1430213), (1900, 1769137),
        (1910, 2083630), (1923, 1918720), (1934, 1935881), (1939, 1770938), (1951, 1616125), (1961, 1627566), (1971, 1619885),
        (1981, 1531346), (1991, 1539848), (2001, 1550123), (2011, 1714227), (2021, 1926960), (2025, 2028399), (2026, 2042036)]


def P(y):
    for y0, p0 in ANCH:
        if y == y0: return p0
    for (y0, p0), (y1, p1) in zip(ANCH, ANCH[1:]):
        if y0 <= y <= y1:
            u = (y - y0) / (y1 - y0); return int(round(math.exp(math.log(p0) + (math.log(p1) - math.log(p0)) * u), -3))
    raise ValueError(y)
PI = lambda a, b: [P(a), P(b)]


# ------------------------------------------------------------------ timeline
def seg(frm, to, sec, era, city, title=None, sub=None, pop=None, cam=None, chapter=None):
    d = {"from": frm, "to": to, "seconds": sec, "era": era, "city_name": city}
    if title: d["title"] = title; d["sub"] = sub
    if pop is not None: d["population"] = pop
    if cam: d["camera"] = {"center": [cam[0], cam[1]], "dist_km": cam[2]}
    if chapter: d["chapter"] = chapter
    return d

ROM = T("Roman Empire", "Roma İmparatorluğu"); EARLY = T("Early Middle Ages", "Erken Orta Çağ"); BAB = T("Babenberg Austria", "Babenberg Avusturyası")
HAB = T("Habsburg Austria", "Habsburg Avusturyası"); BAR = T("Baroque Era", "Barok Dönem"); EMP = T("Austrian Empire", "Avusturya İmparatorluğu")
AH = T("Austria-Hungary", "Avusturya-Macaristan"); REP = T("First Republic", "Birinci Cumhuriyet"); NAZI = T("Nazi Germany", "Nazi Almanyası")
OCC = T("Allied Occupation", "Müttefik İşgali"); SEC = T("Second Republic", "İkinci Cumhuriyet"); TODAY = T("Today", "Bugün")
VIND = T("Vindobona", "Vindobona"); WIEN = T("Vienna", "Viyana"); WENIA = T("Wenia", "Wenia"); DANUBE_BANK = T("Banks of the Danube", "Tuna kıyısı")

C_CAMP = (48.2105, 16.3715)
S = [
 seg(97, 113, 18, ROM, VIND, T("A Fortress on the Danube", "Tuna'da Bir Kale"),
     T("c. AD 97–103: Roman legionaries build a 20-hectare fortress above the Danube",
       "MS ~97–103: Romalı lejyonerler Tuna'ya bakan 20 hektarlık bir kale kurar"),
     pop=6000, cam=(C_CAMP[0], C_CAMP[1], 2.2), chapter=T("Roman Vindobona", "Roma Vindobona'sı")),
 seg(114, 179, 16, ROM, VIND, T("The Tenth Legion", "Onuncu Lejyon"),
     T("AD 114: Legio X Gemina arrives and will stay for 300 years; a town grows outside the walls",
       "MS 114: X. Gemina lejyonu gelir ve 300 yıl kalır; surların dışında bir kasaba büyür"),
     pop=[6000, 15000], cam=(48.2095, 16.3720, 2.6)),
 seg(180, 211, 16, ROM, VIND, T("Death of an Emperor", "Bir İmparatorun Ölümü"),
     T("17 March 180: Marcus Aurelius is said to die at Vindobona during a war on the Danube",
       "17 Mart 180: Marcus Aurelius'un Tuna'daki bir savaş sırasında Vindobona'da öldüğü söylenir"),
     pop=15000, cam=(48.2090, 16.3730, 2.8)),
 seg(212, 399, 15, ROM, VIND, T("A Roman Town", "Bir Roma Kasabası"),
     T("By 212 the civilian town is a municipium; some 15,000 people live around the fortress",
       "212'ye gelindiğinde sivil kasaba bir municipium olur; kalenin çevresinde ~15.000 kişi yaşar"),
     pop=15000, cam=(48.2070, 16.3760, 3.4)),
 seg(400, 500, 15, ROM, VIND, T("Rome Withdraws", "Roma Çekiliyor"),
     T("After the Huns reach Pannonia in the 430s, the people leave and the fortress falls quiet",
       "430'larda Hunlar Pannonia'ya ulaşınca halk ayrılır ve kale sessizliğe gömülür"),
     pop=15000, cam=(48.2100, 16.3720, 2.6)),
 seg(501, 795, 6, EARLY, DANUBE_BANK, cam=(48.2105, 16.3725, 2.6), chapter=T("Early Middle Ages", "Erken Orta Çağ")),
 seg(796, 880, 15, EARLY, DANUBE_BANK, T("St Rupert's Church", "Aziz Rupert Kilisesi"),
     T("Vienna's oldest church, St Rupert's, was probably founded between 796 and 829",
       "Viyana'nın en eski kilisesi Aziz Rupert büyük olasılıkla 796–829 arasında kuruldu"),
     cam=(48.2112, 16.3735, 2.2)),
 seg(881, 975, 15, EARLY, WENIA, T("Wenia", "Wenia"),
     T("881: the Salzburg Annals record a battle 'at Wenia', the first mention of Vienna",
       "881: Salzburg Yıllıkları 'Wenia'da' bir savaştan söz eder; Viyana'nın ilk anılışı"),
     cam=(48.2100, 16.3725, 2.6)),
 seg(976, 1136, 15, BAB, WIEN, T("The Babenbergs", "Babenbergler"),
     T("976: the Babenberg family takes over the march; by the 11th century Vienna is a trading town",
       "976: Babenberg ailesi bölgeyi devralır; 11. yüzyılda Viyana bir ticaret kasabasıdır"),
     cam=(48.2095, 16.3720, 3.0), chapter=T("Babenberg Vienna", "Babenberg Viyanası")),
 seg(1137, 1154, 16, BAB, WIEN, T("The First St Stephen's", "İlk Aziz Stephan"),
     T("1137: Vienna is first called a city; in 1147 the first St Stephen's Church is consecrated",
       "1137: Viyana ilk kez şehir olarak anılır; 1147'de ilk Aziz Stephan Kilisesi kutsanır"),
     cam=(48.2090, 16.3725, 2.4)),
 seg(1155, 1191, 16, BAB, WIEN, T("Capital of a Duchy", "Bir Dükalığın Başkenti"),
     T("1155: Henry II makes Vienna his capital and founds the Scots Abbey; in 1156 Austria is a duchy",
       "1155: II. Heinrich Viyana'yı başkent yapar, İskoç Manastırı'nı kurar; 1156'da dükalık gelir"),
     cam=(48.2100, 16.3700, 2.8)),
 seg(1192, 1220, 18, BAB, WIEN, T("A King's Ransom", "Bir Kralın Fidyesi"),
     T("1192: Richard the Lionheart is seized in Erdberg; his ransom helps pay for new city walls",
       "1192: Aslan Yürekli Richard Erdberg'de yakalanır; fidyesi yeni surların yapımına yardım eder"),
     cam=(48.2085, 16.3730, 3.6)),
 seg(1221, 1277, 15, BAB, WIEN, T("City Rights", "Şehir Hakları"),
     T("1221: Vienna gets city rights and the staple right: passing merchants must sell goods here",
       "1221: Viyana şehir haklarını ve istif hakkını alır: geçen tüccarlar malını burada satmalıdır"),
     cam=(48.2090, 16.3720, 3.4)),
 seg(1278, 1338, 15, HAB, WIEN, T("The Habsburgs Arrive", "Habsburglar Geliyor"),
     T("1278: Rudolf I defeats Ottokar II; Habsburg rule begins and will last over 600 years",
       "1278: I. Rudolf, II. Ottokar'ı yener; Habsburg yönetimi başlar ve 600 yılı aşkın sürer"),
     cam=(48.2080, 16.3700, 3.4), chapter=T("Gothic Vienna", "Gotik Viyana")),
 seg(1339, 1364, 16, HAB, WIEN, T("A Gothic Cathedral", "Gotik Bir Katedral"),
     T("1340: St Stephen's Gothic choir is consecrated; on 7 April 1359 Rudolf IV lays a new stone",
       "1340: Aziz Stephan'ın Gotik koro bölümü kutsanır; 7 Nisan 1359'da IV. Rudolf yeni taşı koyar"),
     cam=(48.2085, 16.3730, 2.0)),
 seg(1365, 1432, 15, HAB, WIEN, T("The University", "Üniversite"),
     T("1365: Rudolf IV founds the University of Vienna", "1365: IV. Rudolf Viyana Üniversitesi'ni kurar"),
     cam=(48.2090, 16.3720, 3.0)),
 seg(1433, 1484, 16, HAB, WIEN, T("The South Tower", "Güney Kulesi"),
     T("1433: St Stephen's south tower is finished, about 136 m tall", "1433: Aziz Stephan'ın yaklaşık 136 m'lik güney kulesi tamamlanır"),
     cam=(48.2085, 16.3730, 1.9)),
 seg(1485, 1528, 15, HAB, WIEN, T("Hungarian Vienna", "Macar Viyanası"),
     T("1485: Matthias Corvinus of Hungary takes Vienna; it is his capital until 1490",
       "1485: Macar kralı Matthias Corvinus Viyana'yı alır; şehir 1490'a dek onun başkentidir"),
     pop=22500, cam=(48.2090, 16.3710, 3.6)),
 seg(1529, 1529.9, 19, HAB, WIEN, T("The First Siege", "Birinci Kuşatma"),
     T("27 Sept – 15 Oct 1529: Suleiman's army, over 100,000 strong, fails to take Vienna",
       "27 Eylül – 15 Ekim 1529: 100.000'i aşkın Kanuni ordusu Viyana'yı alamaz"),
     pop=P(1529), cam=(48.2060, 16.3600, 6.5), chapter=T("The Ottoman Sieges", "Osmanlı Kuşatmaları")),
 seg(1530, 1555, 16, HAB, WIEN, T("A Bastion Fortress", "Tabyalı Bir Kale"),
     T("1548: Vienna becomes a fortress with eleven bastions and a moat",
       "1548: Viyana on bir tabyası ve hendeğiyle bir kaleye dönüşür"),
     pop=PI(1530, 1555), cam=(48.2085, 16.3700, 3.8)),
 seg(1556, 1678, 15, HAB, WIEN, T("Seat of the Emperor", "İmparatorun Merkezi"),
     T("1556: Vienna becomes the seat of the Holy Roman Emperor; by 1637 it has about 60,000 people",
       "1556: Viyana Kutsal Roma İmparatoru'nun merkezi olur; 1637'de nüfusu ~60.000'dir"),
     pop=PI(1556, 1678), cam=(48.2085, 16.3690, 4.4)),
 seg(1679, 1682, 15, HAB, WIEN, T("The Great Plague", "Büyük Veba"),
     T("1679: plague kills nearly a third of Vienna's people", "1679: veba Viyana halkının neredeyse üçte birini öldürür"),
     pop=P(1679), cam=(48.2088, 16.3705, 3.4)),
 seg(1683.0, 1683.69, 21, HAB, WIEN, T("The Second Siege", "İkinci Kuşatma"),
     T("14 July 1683: Kara Mustafa's army surrounds Vienna; the defenders hold out for two months",
       "14 Temmuz 1683: Kara Mustafa'nın ordusu Viyana'yı kuşatır; savunucular iki ay direnir"),
     pop=90000, cam=(48.2070, 16.3580, 7.0)),
 seg(1683.7, 1695, 18, HAB, WIEN, T("Battle of the Kahlenberg", "Kahlenberg Muharebesi"),
     T("12 Sept 1683: a relief army under Jan Sobieski attacks from the Kahlenberg and ends the siege",
       "12 Eylül 1683: Jan Sobieski komutasındaki yardım ordusu Kahlenberg'den saldırır, kuşatma biter"),
     pop=PI(1683.7, 1695), cam=(48.2350, 16.3500, 14.0)),
 seg(1696, 1703, 16, BAR, WIEN, T("Schönbrunn", "Schönbrunn"),
     T("1696: work starts on a new palace at Schönbrunn; its central block is ready in 1700",
       "1696: Schönbrunn'da yeni bir sarayın yapımı başlar; orta bölümü 1700'de hazırdır"),
     pop=PI(1696, 1703), cam=(48.1880, 16.3250, 4.6), chapter=T("Baroque Vienna", "Barok Viyana")),
 seg(1704, 1711, 16, BAR, WIEN, T("The Linienwall", "Linienwall"),
     T("1704: a 13.5 km earthwork, the Linienwall, rings the suburbs against raids",
       "1704: 13,5 km'lik toprak bir set, Linienwall, banliyöleri akınlara karşı kuşatır"),
     pop=PI(1704, 1711), cam=(48.2060, 16.3700, 9.0)),
 seg(1712, 1715, 15, BAR, WIEN, T("The Belvedere", "Belvedere"),
     T("From 1712 Prince Eugene builds the Belvedere; the Upper Belvedere is finished in 1723",
       "1712'den itibaren Prens Eugen Belvedere'yi yaptırır; Yukarı Belvedere 1723'te tamamlanır"),
     pop=PI(1712, 1715), cam=(48.1960, 16.3780, 3.2)),
 seg(1716, 1739, 16, BAR, WIEN, T("The Karlskirche", "Karlskirche"),
     T("1716–1737: after the plague of 1713 the emperor builds the Karlskirche; its dome is 70 m high",
       "1716–1737: 1713 vebasından sonra imparator Karlskirche'yi yaptırır; kubbesi 70 m'dir"),
     pop=PI(1716, 1739), cam=(48.2010, 16.3715, 2.8)),
 seg(1740, 1765, 15, BAR, WIEN, T("Maria Theresa's Palace", "Maria Theresia'nın Sarayı"),
     T("1740s–1750s: Maria Theresa rebuilds Schönbrunn; by 1754 Vienna has 175,460 people",
       "1740'lar–1750'ler: Maria Theresia Schönbrunn'u yeniden yaptırır; 1754'te nüfus 175.460'tır"),
     pop=PI(1740, 1765), cam=(48.1880, 16.3250, 4.2)),
 seg(1766, 1804, 16, BAR, WIEN, T("The Prater Opens", "Prater Halka Açılıyor"),
     T("1766: Joseph II opens the Prater, the imperial hunting ground, to the public",
       "1766: II. Joseph imparatorluk av alanı Prater'i halka açar"),
     pop=PI(1766, 1804), cam=(48.2120, 16.3950, 6.0)),
 seg(1805, 1813, 15, EMP, WIEN, T("Napoleon in Vienna", "Viyana'da Napolyon"),
     T("1805 and 1809: French troops occupy Vienna twice", "1805 ve 1809: Fransız askerleri Viyana'yı iki kez işgal eder"),
     pop=PI(1805, 1813), cam=(48.2080, 16.3700, 7.0), chapter=T("Empire and Revolution", "İmparatorluk ve Devrim")),
 seg(1814, 1836, 16, EMP, WIEN, T("The Congress of Vienna", "Viyana Kongresi"),
     T("1814–1815: Europe's rulers meet in Vienna to redraw the map after Napoleon",
       "1814–1815: Avrupa'nın liderleri Napolyon sonrası haritayı yeniden çizmek için Viyana'da buluşur"),
     pop=PI(1814, 1836), cam=(48.2070, 16.3660, 4.0)),
 seg(1837, 1847, 15, EMP, WIEN, T("The Railway Arrives", "Demiryolu Geliyor"),
     T("1837: the Northern Railway opens beyond the Danube; in 1838 it reaches Vienna",
       "1837: Kuzey Demiryolu Tuna'nın ötesinde açılır; 1838'de Viyana'ya ulaşır"),
     pop=PI(1837, 1847), cam=(48.2280, 16.3950, 8.0)),
 seg(1848, 1849, 14, EMP, WIEN, T("Revolution", "Devrim"),
     T("13 March 1848: revolution forces Metternich to resign; an October rising is crushed",
       "13 Mart 1848: devrim Metternich'i istifaya zorlar; ekim ayaklanması bastırılır"),
     pop=PI(1848, 1849), cam=(48.2080, 16.3680, 4.0)),
 seg(1850, 1856, 14, EMP, WIEN, T("The Suburbs Join", "Banliyöler Katılıyor"),
     T("1850: the suburbs inside the Linienwall become part of Vienna; it has 551,300 people",
       "1850: Linienwall içindeki banliyöler Viyana'ya katılır; nüfus 551.300'dür"),
     pop=PI(1850, 1856), cam=(48.2050, 16.3700, 9.5)),
 seg(1857, 1868, 20, EMP, WIEN, T("Down Come the Walls", "Surlar Yıkılıyor"),
     T("1857: Franz Joseph orders the walls torn down; the 5.3 km Ringstrasse takes their place",
       "1857: Franz Joseph surların yıkılmasını emreder; yerini 5,3 km'lik Ringstraße alır"),
     pop=PI(1857, 1868), cam=(48.2080, 16.3700, 4.6), chapter=T("The Ringstrasse", "Ringstraße")),
 seg(1869, 1869.9, 15, AH, WIEN, T("The Opera", "Opera"),
     T("25 May 1869: the Court Opera opens on the Ring with Mozart's Don Giovanni",
       "25 Mayıs 1869: Saray Operası Ring üzerinde Mozart'ın Don Giovanni'siyle açılır"),
     pop=PI(1869, 1869.9), cam=(48.2040, 16.3690, 2.4)),
 seg(1870, 1872, 17, AH, WIEN, T("Taming the Danube", "Tuna'yı Evcilleştirmek"),
     T("1870–1875: the Danube gets a straight new bed, 280 m wide; the old bed becomes the Alte Donau",
       "1870–1875: Tuna'ya 280 m genişliğinde düz bir yatak açılır; eski yatak Alte Donau olur"),
     pop=PI(1870, 1872), cam=(48.2250, 16.4100, 11.0)),
 seg(1873, 1875, 15, AH, WIEN, T("The World's Fair", "Dünya Fuarı"),
     T("1 May 1873: a World's Fair opens in the Prater; that year the stock market crashes",
       "1 Mayıs 1873: Prater'de bir Dünya Fuarı açılır; aynı yıl borsa çöker"),
     pop=PI(1873, 1875), cam=(48.2150, 16.4000, 5.5)),
 seg(1876, 1882, 15, AH, WIEN, T("A Bridge Across", "Karşıya Bir Köprü"),
     T("21 August 1876: the first Reichsbrücke opens across the new Danube bed",
       "21 Ağustos 1876: ilk Reichsbrücke yeni Tuna yatağının üzerinde açılır"),
     pop=PI(1876, 1882), cam=(48.2260, 16.4050, 4.6)),
 seg(1883, 1889, 18, AH, WIEN, T("City Hall and Parliament", "Belediye Sarayı ve Parlamento"),
     T("1883: the City Hall, its tower 98 m high, and Hansen's Parliament are finished on the Ring",
       "1883: kulesi 98 m'lik Belediye Sarayı ve Hansen'in Parlamentosu Ring üzerinde tamamlanır"),
     pop=PI(1883, 1889), cam=(48.2100, 16.3600, 2.6)),
 seg(1890, 1896, 16, AH, WIEN, T("Greater Vienna", "Büyük Viyana"),
     T("1890–1892: the villages beyond the Gürtel join the city; it counts 1.43 million people",
       "1890–1892: Gürtel'in ötesindeki köyler şehre katılır; nüfus 1,43 milyondur"),
     pop=PI(1890, 1896), cam=(48.2050, 16.3600, 15.0)),
 seg(1897, 1909, 16, AH, WIEN, T("The Giant Wheel", "Dev Dönme Dolap"),
     T("1897: the Riesenrad, 64.75 m tall, rises in the Prater for the emperor's jubilee",
       "1897: 64,75 m'lik Riesenrad, imparatorun jübilesi için Prater'de yükselir"),
     pop=PI(1897, 1909), cam=(48.2160, 16.3920, 3.0)),
 seg(1910, 1917, 15, AH, WIEN, T("Two Million", "İki Milyon"),
     T("1910: the census counts 2,083,630 people; the city is now larger than ever",
       "1910: sayım 2.083.630 kişi sayar; şehir hiç olmadığı kadar büyüktür"),
     pop=PI(1910, 1917), cam=(48.2050, 16.3700, 19.0)),
 seg(1918, 1933, 17, REP, WIEN, T("Red Vienna", "Kızıl Viyana"),
     T("1918: the empire ends; the city builds homes like the 1,100 m Karl-Marx-Hof (1927–1930)",
       "1918: imparatorluk sona erer; şehir 1.100 m'lik Karl-Marx-Hof (1927–1930) gibi konutlar yapar"),
     pop=PI(1918, 1933), cam=(48.2450, 16.3620, 4.4), chapter=T("Red Vienna and War", "Kızıl Viyana ve Savaş")),
 seg(1934, 1937, 15, REP, WIEN, T("Civil War", "İç Savaş"),
     T("February 1934: in the Austrian Civil War the army shells the Karl-Marx-Hof",
       "Şubat 1934: Avusturya İç Savaşı'nda ordu Karl-Marx-Hof'u topa tutar"),
     pop=PI(1934, 1937), cam=(48.2500, 16.3640, 3.4)),
 seg(1938, 1944, 16, NAZI, WIEN, T("The Anschluss", "Anschluss"),
     T("March 1938: Nazi Germany annexes Austria; more than 100,000 Jews flee Vienna",
       "Mart 1938: Nazi Almanyası Avusturya'yı ilhak eder; 100.000'i aşkın Yahudi Viyana'dan kaçar"),
     pop=PI(1938, 1944), cam=(48.2080, 16.3700, 9.0)),
 seg(1944.01, 1945.3, 18, NAZI, WIEN, T("The War Comes Home", "Savaş Şehre Geliyor"),
     T("52 air raids kill 8,769 people; on 12 April 1945 the roof of St Stephen's burns",
       "52 hava saldırısı 8.769 kişiyi öldürür; 12 Nisan 1945'te Aziz Stephan'ın çatısı yanar"),
     pop=PI(1944.01, 1945.3), cam=(48.2080, 16.3710, 4.0)),
 seg(1945.31, 1955.3, 16, OCC, WIEN, T("Four Powers", "Dört Güç"),
     T("13 April 1945: the Soviet army takes Vienna; for ten years four Allied powers occupy it",
       "13 Nisan 1945: Sovyet ordusu Viyana'yı alır; şehir on yıl dört Müttefik gücün işgalinde kalır"),
     pop=PI(1945.31, 1955.3), cam=(48.2080, 16.3700, 8.0)),
 seg(1955.37, 1963, 16, SEC, WIEN, T("Free Again", "Yeniden Özgür"),
     T("15 May 1955: the Austrian State Treaty is signed at the Belvedere", "15 Mayıs 1955: Avusturya Devlet Antlaşması Belvedere'de imzalanır"),
     pop=PI(1955.37, 1963), cam=(48.1960, 16.3780, 3.0), chapter=T("Modern Vienna", "Modern Viyana")),
 seg(1964, 1972, 15, SEC, WIEN, T("The Danube Tower", "Tuna Kulesi"),
     T("16 April 1964: the 252 m Danube Tower opens with the international garden show",
       "16 Nisan 1964: 252 m'lik Tuna Kulesi uluslararası bahçe fuarıyla açılır"),
     pop=PI(1964, 1972), cam=(48.2360, 16.4050, 4.6)),
 seg(1973, 1976.5, 16, SEC, WIEN, T("UNO City", "BM Şehri"),
     T("1973–1979: the Vienna International Centre rises; Vienna becomes the third seat of the UN",
       "1973–1979: Viyana Uluslararası Merkezi yükselir; Viyana BM'nin üçüncü merkezi olur"),
     pop=PI(1973, 1976.5), cam=(48.2330, 16.4120, 4.0)),
 seg(1976.55, 1977.9, 14, SEC, WIEN, T("The Bridge Falls", "Köprü Çöküyor"),
     T("1 August 1976: shortly before 5 a.m. the Reichsbrücke collapses into the Danube",
       "1 Ağustos 1976: sabah 5'ten kısa süre önce Reichsbrücke Tuna'ya çöker"),
     pop=PI(1976.55, 1977.9), cam=(48.2280, 16.4090, 3.0)),
 seg(1978, 1983, 14, SEC, WIEN, T("The U-Bahn", "Metro"),
     T("25 February 1978: the first U-Bahn line, U1, opens from Reumannplatz to Karlsplatz",
       "25 Şubat 1978: ilk metro hattı U1, Reumannplatz ile Karlsplatz arasında açılır"),
     pop=PI(1978, 1983), cam=(48.2000, 16.3750, 8.0)),
 seg(1984, 1988, 16, SEC, WIEN, T("A New Island", "Yeni Bir Ada"),
     T("1972–1988: a flood channel, the New Danube, is dug and a 21.1 km island built beside it",
       "1972–1988: bir taşkın kanalı, Yeni Tuna, kazılır ve yanına 21,1 km'lik bir ada yapılır"),
     pop=PI(1984, 1988), cam=(48.2350, 16.4050, 12.0)),
 seg(1989, 2012, 8, SEC, WIEN, pop=PI(1989, 2012), cam=(48.2200, 16.3900, 16.0)),
 seg(2013, 2019, 15, TODAY, WIEN, T("A New Skyline", "Yeni Bir Silüet"),
     T("2013: DC Tower 1, 220 m to its roof, is finished beside the Danube",
       "2013: çatısına kadar 220 m olan DC Tower 1, Tuna'nın kıyısında tamamlanır"),
     pop=PI(2013, 2019), cam=(48.2320, 16.4100, 4.8), chapter=T("Vienna Today", "Bugünün Viyanası")),
 seg(2020, 2026, 22, TODAY, WIEN, T("Vienna Today", "Bugünün Viyanası"),
     T("From a Roman fortress to 2,042,036 people on 1 January 2026", "Bir Roma kalesinden 1 Ocak 2026'da 2.042.036 kişiye"),
     pop=[P(2020), 2042036], cam=(48.2150, 16.3800, 20.0)),
]
SCALE_T, SCALE_Q = 1.0, 1.0
for s_ in S:
    s_["seconds"] = round(s_["seconds"] * (SCALE_T if s_.get("title") else SCALE_Q))


def wall(name, path, built, removed=None, height="mid", towers=90, draw=3.0, **kw):
    d = {"name": name, "path": L(path), "built": built, "height": height, "towers_m": towers, "draw_s": draw}
    if removed is not None: d["removed"] = removed
    d.update(kw); return d


BAR_SUB = "Baroque suburbs (inside the Linienwall)"
districts = [
 {"name": "Vindobona fortress", "style": "roman", "poly": L(CAMP), "from": 98, "to": 125, "density": 0.75, "grain_m": 45, "grid_deg": 0,
  "grow_from": [48.2110, 16.3712], "fade": [430, 450, 0.08]},
 {"name": "Canabae (≈)", "style": "roman", "poly": L(CANABAE), "from": 115, "to": 200, "density": 0.45, "grain_m": 50,
  "grow_from": [48.2080, 16.3700], "fade": [430, 450, 0.0]},
 {"name": "Civil town, 3rd district (≈)", "style": "roman", "poly": L(CIVIL_TOWN), "from": 130, "to": 212, "density": 0.45, "grain_m": 55,
  "grow_from": [48.1985, 16.3840], "fade": [430, 450, 0.0]},
 {"name": "Early medieval settlement in the old camp (≈)", "style": "medieval", "poly": L(CAMP), "from": 800, "to": 1100, "density": 0.55, "grain_m": 50,
  "grow_from": [48.2112, 16.3735]},
 {"name": "Babenberg town (≈)", "style": "medieval", "poly": L(scale(WALL, CORE_C, 0.75)), "holes": [L(CAMP)], "from": 1100, "to": 1190, "density": 0.6,
  "grow_from": [48.2095, 16.3720]},
 {"name": "Medieval city inside the walls", "style": "medieval", "poly": L(WALL), "from": 1195, "to": 1350, "density": 0.85,
  "grow_from": [48.2090, 16.3715], "grain_m": 45},
 {"name": "Early suburbs (≈)", "style": "medieval", "poly": L(EARLY_SUB), "holes": [L(RING_OUT)], "from": 1300, "to": 1660, "density": 0.32, "grain_m": 70,
  "grow_from": [48.2090, 16.3715], "fade": [1683.55, 1683.66, 0.25]},
 {"name": "Baroque Innere Stadt", "style": "stone", "poly": L(WALL), "from": 1690, "to": 1760, "density": 0.9, "grain_m": 45,
  "grow_from": [48.2090, 16.3715]},
 {"name": BAR_SUB, "style": "stone", "poly": L(LINIEN_POLY), "holes": [L(RING_OUT), L(BELVEDERE_G)], "from": 1690, "to": 1830, "density": 0.55,
  "grain_m": 60, "grow_from": [48.2090, 16.3715]},
 {"name": "Leopoldstadt (≈)", "style": "stone", "poly": L(LEOPOLDSTADT), "holes": [L(AUGARTEN)], "from": 1690, "to": 1840, "density": 0.6, "grain_m": 60,
  "grow_from": [48.2140, 16.3800]},
 {"name": "Ringstrasse", "style": "victorian", "poly": L(RING_OUT), "holes": [L(FORT)], "from": 1860, "to": 1890, "density": 0.75, "grain_m": 55,
  "grow_from": [48.2100, 16.3600]},
 {"name": "Gründerzeit suburbs", "style": "victorian", "poly": L(LINIEN_POLY), "holes": [L(RING_OUT), L(BELVEDERE_G)], "from": 1860, "to": 1914, "density": 0.85,
  "grain_m": 55, "grow_from": [48.2090, 16.3715]},
 {"name": "Leopoldstadt and Brigittenau", "style": "victorian", "poly": L(ISLAND_19C), "holes": [L(AUGARTEN), L(PRATER)], "from": 1860, "to": 1914,
  "density": 0.82, "grain_m": 60, "grow_from": [48.2150, 16.3800], "grid_deg": 40},
 {"name": "Vororte (joined 1890–1892)", "style": "victorian", "poly": L(VORORTE), "holes": [L(LINIEN_POLY), L(SCHOENBRUNN_P)], "from": 1870, "to": 1930,
  "density": 0.62, "grain_m": 65, "grow_from": [48.2050, 16.3500]},
 {"name": "Floridsdorf", "style": "industrial", "poly": L(FLORIDSDORF), "holes": [L(DONAUINSEL)], "from": 1880, "to": 1960, "density": 0.6, "grain_m": 85,
  "grow_from": [48.2565, 16.4000]},
 {"name": "Postwar and modern suburbs", "style": "suburb", "poly": L(OUTER), "holes": [L(VORORTE), L(LINIEN_POLY), L(ISLAND_19C), L(FLORIDSDORF), L(PRATER),
  L(DONAUINSEL), L(LOBAU), L(LAINZ), L(SCHOENBRUNN_P)], "from": 1950, "to": 2020, "density": 0.5, "grain_m": 100, "grow_from": [48.2100, 16.3800]},
 {"name": "Donau City", "style": "highrise", "poly": L(DONAU_CITY), "from": 1995, "to": 2020, "density": 0.55, "grain_m": 75, "grid_deg": 30,
  "grow_from": [48.2330, 16.4130]},
 {"name": "Seestadt Aspern (≈)", "style": "modern", "poly": L(SEESTADT), "from": 2012, "to": 2025, "density": 0.6, "grain_m": 85,
  "grow_from": [48.2250, 16.5050]},
 {"name": "Hauptbahnhof quarter (≈)", "style": "modern", "poly": L(HBF_Q), "from": 2012, "to": 2020, "density": 0.7, "grain_m": 70,
  "grow_from": [48.1865, 16.3830]},
]

walls = [
 wall("Vindobona fortress wall", CAMP + [CAMP[0]], 100, 1200, height="low", towers=70, draw=2.5),
 wall("Medieval city wall (c. 1200)", WALL_RING, 1194, 1550, height="mid", towers=80, draw=4.0),
 wall("Bastion fortress (1548)", FORT_RING, 1548, 1860, height="high", towers=0, draw=4.0, moat=True, double_side=-1),
 wall("Linienwall", LINIEN, 1704, 1894.2, height="low", towers=0, draw=4.0),
]

bridges = [
 {"name": "Reichsbrücke I (Kronprinz-Rudolf-Brücke)", "path": [[48.2254, 16.40488], [48.2306, 16.41346]], "built": 1876.6, "removed": 1934.5,
  "style": "iron", "width_m": 22},
 {"name": "Reichsbrücke II", "path": [[48.2254, 16.40488], [48.2306, 16.41346]], "built": 1937.77, "removed": 1976.58, "style": "tower", "width_m": 26},
 {"name": "Reichsbrücke III", "path": [[48.2254, 16.40488], [48.2306, 16.41346]], "built": 1980.85, "style": "modern", "width_m": 30},
]

roads = [
 {"name": "Ringstraße", "path": L(RING_ROAD), "from": 1860, "kind": "avenue", "width_m": 40, "draw_s": 4},
 {"name": "Gürtel", "path": L(GUERTEL), "from": 1873, "kind": "avenue", "width_m": 34, "draw_s": 3},
 {"name": "Northern Railway (≈)", "path": L([(48.2190, 16.3930), (48.2300, 16.4000), (48.2450, 16.4020), (48.2570, 16.4010), (48.2750, 16.4300)]),
  "from": 1838, "kind": "rail", "width_m": 22},
 {"name": "Southern Railway (≈)", "path": L([(48.1865, 16.3780), (48.1800, 16.3550), (48.1700, 16.3330), (48.1450, 16.3050), (48.1350, 16.2950)]),
  "from": 1842, "kind": "rail", "width_m": 22},
]

landmarks = [
 {"type": "church", "name": T("St Rupert's", "Aziz Rupert"), "at": [48.211944, 16.374444], "built": 800, "rise_s": 3, "size_m": [22, 10, 12],
  "colors": {"wall": "#ddd3bd", "roof": "#6a5f55"}},
 {"type": "church", "name": T("First St Stephen's", "İlk Aziz Stephan"), "at": list(STEPHANSDOM), "built": 1137, "removed": 1339.5, "rise_s": 6,
  "size_m": [60, 24, 18], "rot_deg": -8, "colors": {"wall": "#ddd3bd", "roof": "#6a5f55"}},
 {"type": "cathedral", "name": T("St Stephen's Cathedral", "Aziz Stephan Katedrali"), "at": list(STEPHANSDOM), "built": 1340, "removed": 1945.28,
  "rise_s": 12, "size_m": [107, 40, 36], "rot_deg": -8, "scale": 1.4, "colors": {"wall": "#d9cfb8", "roof": "#3f6d5c", "spire": False}},
 {"type": "cathedral", "name": T("St Stephen's (roof burnt)", "Aziz Stephan (çatısı yanmış)"), "at": list(STEPHANSDOM), "built": 1945.29, "removed": 1952.3,
  "rise_s": 0.2, "size_m": [107, 40, 36], "rot_deg": -8, "scale": 1.4, "colors": {"wall": "#b9b2a3", "roof": "#3b3b3b", "spire": False}},
 {"type": "cathedral", "name": T("St Stephen's (restored)", "Aziz Stephan (onarılmış)"), "at": list(STEPHANSDOM), "built": 1952.31, "rise_s": 1.5,
  "size_m": [107, 40, 36], "rot_deg": -8, "scale": 1.4, "colors": {"wall": "#d9cfb8", "roof": "#3f6d5c", "spire": False}},
 {"type": "tower", "name": T("South tower", "Güney kulesi"), "at": [48.20835, 16.37325], "built": 1359.3, "rise_s": 25, "size_m": [26, 26, 97], "scale": 1.4,
  "colors": {"wall": "#8f8878", "roof": "#6f6a60"}},
 {"type": "church", "name": T("Scots Abbey", "İskoç Manastırı"), "at": [48.2125, 16.3652], "built": 1155, "rise_s": 4, "size_m": [55, 22, 20],
  "colors": {"wall": "#e4dccb", "roof": "#6a6f75"}},
 {"type": "castle", "name": T("Hofburg castle", "Hofburg kalesi"), "at": [48.20639, 16.36528], "built": 1275, "removed": 1660, "rise_s": 4,
  "size_m": [80, 70, 22], "colors": {"wall": "#d9cfb6"}},
 {"type": "palace", "name": T("Hofburg", "Hofburg"), "at": [48.20639, 16.36528], "built": 1660, "rise_s": 8, "size_m": [200, 150, 24],
  "colors": {"wall": "#e8e0cc", "roof": "#6f8f7c"}},
 {"type": "palace", "name": T("Neue Burg", "Neue Burg"), "at": [48.2050, 16.3640], "built": 1881, "rise_s": 20, "size_m": [180, 60, 26],
  "rot_deg": 35, "colors": {"wall": "#ece4d0", "roof": "#6f8f7c"}},
 {"type": "palace", "name": T("Schönbrunn Palace", "Schönbrunn Sarayı"), "at": [48.184516, 16.311865], "built": 1696, "rise_s": 8, "size_m": [180, 110, 24], "scale": 1.3,
  "colors": {"wall": "#e8c25a", "roof": "#8a6f55"}},
 {"type": "box", "name": T("Gloriette (≈)", "Gloriette (≈)"), "at": [48.1782, 16.3089], "built": 1775, "rise_s": 3, "size_m": [90, 18, 20],
  "colors": {"wall": "#ece6d6"}},
 {"type": "palace", "name": T("Upper Belvedere", "Yukarı Belvedere"), "at": [48.19417, 16.38028], "built": 1717, "rise_s": 8, "size_m": [150, 50, 22],
  "colors": {"wall": "#efe9dc", "roof": "#5f8c7a"}},
 {"type": "domechurch", "name": T("Karlskirche", "Karlskirche"), "at": [48.19828, 16.37190], "built": 1716, "rise_s": 12, "size_m": [55, 40, 34], "scale": 1.4,
  "colors": {"wall": "#ece4d0", "dome": "#6f9c8a", "lantern": True}},
 {"type": "column", "name": T("Karlskirche column", "Karlskirche sütunu"), "at": [48.19828, 16.37130], "built": 1716, "rise_s": 10, "size_m": [8, 8, 40],
  "colors": {"wall": "#e8e1cf", "top": "#c9a94a"}},
 {"type": "cathedral", "name": T("Votivkirche", "Votivkirche"), "at": [48.21528, 16.35861], "built": 1856, "rise_s": 15, "size_m": [90, 40, 32], "scale": 1.3,
  "rot_deg": -60, "colors": {"wall": "#e6e0d2", "roof": "#5f666f"}},
 {"type": "box", "name": T("Court Opera", "Saray Operası"), "at": [48.20306, 16.36889], "built": 1861, "rise_s": 8, "size_m": [140, 100, 30], "scale": 1.3,
  "rot_deg": 35, "colors": {"wall": "#e8dcc0", "roof": "#59656a"}},
 {"type": "parliament", "name": T("City Hall", "Belediye Sarayı"), "at": [48.21083, 16.35722], "built": 1872.4, "rise_s": 12, "size_m": [152, 110, 26], "scale": 1.3,
  "rot_deg": 90, "colors": {"wall": "#ddd3bb", "roof": "#59656a"}},
 {"type": "palace", "name": T("Parliament (≈)", "Parlamento (≈)"), "at": [48.2082, 16.3583], "built": 1874.5, "rise_s": 10, "size_m": [150, 120, 24],
  "rot_deg": 35, "colors": {"wall": "#ece6d6", "roof": "#5c6a70"}},
 {"type": "wheel", "name": T("Riesenrad", "Riesenrad"), "at": [48.2166505, 16.3959494], "built": 1897, "rise_s": 3, "size_m": [30], "scale": 1.5,
  "colors": {"wall": "#b23a2e"}},
 {"type": "station", "name": T("Northern Railway station (≈)", "Kuzey Demiryolu istasyonu (≈)"), "at": [48.2190, 16.3925], "built": 1838, "rise_s": 3,
  "size_m": [200, 70, 22], "rot_deg": 45},
 {"type": "box", "name": T("Karl-Marx-Hof (south)", "Karl-Marx-Hof (güney)"), "at": [48.2505, 16.3653], "built": 1927, "rise_s": 6, "size_m": [260, 30, 20],
  "rot_deg": 80, "colors": {"wall": "#d9b19a", "roof": "#a1524a"}},
 {"type": "box", "name": T("Karl-Marx-Hof (north)", "Karl-Marx-Hof (kuzey)"), "at": [48.2550, 16.3645], "built": 1928, "rise_s": 6, "size_m": [260, 30, 20],
  "rot_deg": 80, "colors": {"wall": "#d9b19a", "roof": "#a1524a"}},
 {"type": "tower", "name": T("Danube Tower", "Tuna Kulesi"), "at": [48.24000, 16.41083], "built": 1962.8, "rise_s": 8, "size_m": [16, 16, 180],
  "colors": {"wall": "#d8d8d4", "roof": "#c9c9c4"}},
 {"type": "skyscraper", "name": T("Vienna International Centre", "Viyana Uluslararası Merkezi"), "at": [48.23472, 16.41694], "built": 1973, "rise_s": 10,
  "size_m": [70, 30, 127], "rot_deg": 30, "colors": {"wall": "#7f8d95"}},
 {"type": "skyscraper", "name": T("Vienna International Centre 2", "Viyana Uluslararası Merkezi 2"), "at": [48.23400, 16.41800], "built": 1974, "rise_s": 10,
  "size_m": [70, 30, 110], "rot_deg": -40, "colors": {"wall": "#7f8d95"}},
 {"type": "skyscraper", "name": T("Millennium Tower", "Millennium Tower"), "at": [48.24000, 16.38694], "built": 1997, "rise_s": 5, "size_m": [36, 36, 202],
  "colors": {"wall": "#8fa6b5"}},
 {"type": "skyscraper", "name": T("DC Tower 1", "DC Tower 1"), "at": [48.23194, 16.41278], "built": 2011, "rise_s": 8, "size_m": [45, 30, 220],
  "colors": {"wall": "#3d4650"}},
 {"type": "station", "name": T("Hauptbahnhof", "Hauptbahnhof"), "at": [48.186667, 16.380000], "built": 2007.5, "rise_s": 6, "size_m": [260, 80, 22],
  "rot_deg": 5, "colors": {"wall": "#d9d9d9", "roof": "#8a949b"}},
]

timed_water = [{"name": "New Danube", "poly": L(NEW_DANUBE), "from": 1985}] if NEW_DANUBE else []

camps = [
 {"poly": L(rect(48.1880, 16.3350, 48.2000, 16.3550)), "from": 1529.74, "to": 1529.8, "count": 140},
 {"poly": L(rect(48.1830, 16.3650, 48.1900, 16.3950)), "from": 1529.74, "to": 1529.8, "count": 100},
 {"poly": L(rect(48.1900, 16.3200, 48.2050, 16.3450)), "from": 1683.53, "to": 1683.7, "count": 200},
 {"poly": L(rect(48.2050, 16.3250, 48.2250, 16.3450)), "from": 1683.53, "to": 1683.7, "count": 160},
 {"poly": L(rect(48.1820, 16.3500, 48.1920, 16.3800)), "from": 1683.53, "to": 1683.7, "count": 120},
]
smoke = [
 {"at": [48.2068, 16.3628], "from": 1529.76, "to": 1529.79, "scale": 1.0},
 {"at": [48.2068, 16.3628], "from": 1683.56, "to": 1683.69, "scale": 1.1},
 {"at": [48.2088, 16.3705], "from": 1945.0, "to": 1945.3, "scale": 1.0},
 {"at": [48.20306, 16.36889], "from": 1945.19, "to": 1945.25, "scale": 1.1},
 {"at": list(STEPHANSDOM), "from": 1945.27, "to": 1945.31, "scale": 1.3},
 {"at": [48.2500, 16.3650], "from": 1934.1, "to": 1934.14, "scale": 0.8},
]
open_spaces = [
 {"name": "Prater", "poly": L(PRATER)},
 {"name": "Augarten", "poly": L(AUGARTEN)},
 {"name": "Schönbrunn gardens", "poly": L(SCHOENBRUNN_P)},
 {"name": "Belvedere gardens", "poly": L(BELVEDERE_G)},
 {"name": "Danube floodplain / Danube Island (≈)", "poly": L(DONAUINSEL)},
 {"name": "Lobau", "poly": L(LOBAU)},
 {"name": "Lainzer Tiergarten", "poly": L(LAINZ)},
]
labels = [
 {"text": T("DANUBE", "TUNA"), "at": [48.2380, 16.3930], "kind": "water", "from": 97, "to": 1960},
 {"text": T("DANUBE", "TUNA"), "at": [48.2180, 16.4250], "kind": "water", "from": 1960},
 {"text": T("VINDOBONA", "VINDOBONA"), "at": [48.2060, 16.3720], "kind": "region", "from": 97, "to": 450},
 {"text": T("St Rupert's", "Aziz Rupert"), "at": [48.211944, 16.374444], "from": 800, "to": 880, "lift_m": 25},
 {"text": T("St Stephen's", "Aziz Stephan"), "at": list(STEPHANSDOM), "from": 1140, "to": 1154, "lift_m": 40},
 {"text": T("Scots Abbey", "İskoç Manastırı"), "at": [48.2125, 16.3652], "from": 1156, "to": 1191, "lift_m": 35},
 {"text": T("Erdberg", "Erdberg"), "at": [48.2010, 16.3980], "kind": "place", "from": 1192, "to": 1220},
 {"text": T("Hofburg", "Hofburg"), "at": [48.20639, 16.36528], "from": 1280, "to": 1338, "lift_m": 40},
 {"text": T("St Stephen's", "Aziz Stephan"), "at": list(STEPHANSDOM), "from": 1340, "to": 1364, "lift_m": 60},
 {"text": T("St Stephen's", "Aziz Stephan"), "at": list(STEPHANSDOM), "from": 1433, "to": 1484, "lift_m": 150},
 {"text": T("OTTOMAN CAMP", "OSMANLI ORDUGAHI"), "at": [48.1950, 16.3450], "kind": "region", "from": 1529.74, "to": 1529.8},
 {"text": T("OTTOMAN CAMP", "OSMANLI ORDUGAHI"), "at": [48.2050, 16.3330], "kind": "region", "from": 1683.53, "to": 1683.69},
 {"text": T("Kahlenberg", "Kahlenberg"), "at": [48.28333, 16.33333], "kind": "place", "from": 1683.7, "to": 1695, "lift_m": 60},
 {"text": T("Schönbrunn", "Schönbrunn"), "at": [48.184516, 16.311865], "from": 1697, "to": 1703, "lift_m": 40},
 {"text": T("LINIENWALL", "LINIENWALL"), "at": [48.1890, 16.3480], "kind": "region", "from": 1704, "to": 1711},
 {"text": T("Belvedere", "Belvedere"), "at": [48.19417, 16.38028], "from": 1714, "to": 1715, "lift_m": 40},
 {"text": T("Karlskirche", "Karlskirche"), "at": [48.19828, 16.37190], "from": 1720, "to": 1739, "lift_m": 80},
 {"text": T("Schönbrunn", "Schönbrunn"), "at": [48.184516, 16.311865], "from": 1740, "to": 1765, "lift_m": 40},
 {"text": T("Prater", "Prater"), "at": [48.2100, 16.4150], "kind": "place", "from": 1766, "to": 1804},
 {"text": T("Hofburg", "Hofburg"), "at": [48.20639, 16.36528], "from": 1814, "to": 1836, "lift_m": 40},
 {"text": T("Northern Railway", "Kuzey Demiryolu"), "at": [48.2190, 16.3925], "from": 1838.2, "to": 1847, "lift_m": 30},
 {"text": T("RINGSTRASSE", "RINGSTRASSE"), "at": [48.2028, 16.3700], "kind": "region", "from": 1860, "to": 1868},
 {"text": T("Opera", "Opera"), "at": [48.20306, 16.36889], "from": 1869, "to": 1869.9, "lift_m": 45},
 {"text": T("ALTE DONAU", "ALTE DONAU"), "at": [48.2400, 16.4300], "kind": "water", "from": 1871, "to": 1875},
 {"text": T("Prater", "Prater"), "at": [48.2100, 16.4150], "kind": "place", "from": 1873, "to": 1875},
 {"text": T("Reichsbrücke", "Reichsbrücke"), "at": [48.2282, 16.4095], "from": 1876.7, "to": 1882, "lift_m": 20},
 {"text": T("City Hall", "Belediye Sarayı"), "at": [48.21083, 16.35722], "from": 1883, "to": 1889, "lift_m": 110},
 {"text": T("Parliament", "Parlamento"), "at": [48.2082, 16.3583], "from": 1883, "to": 1889, "lift_m": 40},
 {"text": T("GÜRTEL", "GÜRTEL"), "at": [48.1950, 16.3360], "kind": "region", "from": 1890, "to": 1896},
 {"text": T("Riesenrad", "Riesenrad"), "at": [48.2166505, 16.3959494], "from": 1897.2, "to": 1909, "lift_m": 80},
 {"text": T("Karl-Marx-Hof", "Karl-Marx-Hof"), "at": [48.2527, 16.3650], "from": 1928, "to": 1937, "lift_m": 30},
 {"text": T("St Stephen's", "Aziz Stephan"), "at": list(STEPHANSDOM), "from": 1944.5, "to": 1945.3, "lift_m": 150},
 {"text": T("Belvedere", "Belvedere"), "at": [48.19417, 16.38028], "from": 1955.37, "to": 1963, "lift_m": 40},
 {"text": T("Danube Tower", "Tuna Kulesi"), "at": [48.24000, 16.41083], "from": 1964.3, "to": 1972, "lift_m": 270},
 {"text": T("UNO City", "BM Şehri"), "at": [48.23472, 16.41694], "from": 1975, "to": 1976.5, "lift_m": 140},
 {"text": T("Reichsbrücke", "Reichsbrücke"), "at": [48.2282, 16.4095], "from": 1976.55, "to": 1977.9, "lift_m": 20},
 {"text": T("Karlsplatz", "Karlsplatz"), "at": [48.2005, 16.3700], "kind": "place", "from": 1978, "to": 1983},
 {"text": T("DANUBE ISLAND", "TUNA ADASI"), "at": [48.2420, 16.3950], "kind": "region", "from": 1984, "to": 1988},
 {"text": T("DC Tower 1", "DC Tower 1"), "at": [48.23194, 16.41278], "from": 2013, "to": 2019, "lift_m": 240},
 {"text": T("Kahlenberg", "Kahlenberg"), "at": [48.28333, 16.33333], "kind": "place", "from": 2020, "lift_m": 60},
 {"text": T("Schönbrunn", "Schönbrunn"), "at": [48.184516, 16.311865], "kind": "place", "from": 2020, "lift_m": 40},
]

city = {
 "slug": "vienna", "seed": 97, "long_ok": True,
 "name": T("Vienna", "Viyana"), "intro": T("1,900 Years in 15 Minutes", "15 Dakikada 1.900 Yıl"), "intro_seconds": 4.5,
 "geo": {"bbox": [48.02, 16.05, 48.42, 16.72], "cell_m": 100, "core_bbox": [48.170, 16.290, 48.265, 16.445], "core_cell_m": 30,
         "rivers_keep": ["Donau"]},
 "geo_edits": GEO_EDITS,
 "view": {"azimuth_deg": 0, "pitch_deg": 46, "fov": 34},
 "render": {"vertical_exaggeration": 1.8},
 "segments": S,
 "timed_water": timed_water,
 "districts": districts, "walls": walls, "bridges": bridges, "roads": roads, "landmarks": landmarks,
 "camps": camps, "smoke": smoke, "open_spaces": open_spaces, "labels": labels,
 "youtube": {
  "title": T("Vienna: 1,900 Years in 15 Minutes (3D Timelapse)", "Viyana: 15 Dakikada 1.900 Yıl (3D Timelapse)"),
  "description": T(
   "Around AD 100 Roman legionaries built a fortress called Vindobona above the Danube. Watch Vienna grow from that camp to a walled "
   "medieval capital, survive two Ottoman sieges in 1529 and 1683, spread its Baroque suburbs to the Linienwall, trade its walls for "
   "the Ringstrasse, straighten the Danube and become a city of two million: St Stephen's Cathedral, the Hofburg, Schönbrunn, the "
   "Belvedere, the Karlskirche, the Opera, the Riesenrad, Red Vienna, the war of 1945, UNO City and the Danube Island, with the year "
   "and the population on screen.",
   "MS 100 civarında Romalı lejyonerler Tuna'ya bakan Vindobona adlı bir kale kurdu. Viyana'nın bu ordugâhtan surlarla çevrili bir "
   "Orta Çağ başkentine büyüyüşünü, 1529 ve 1683'teki iki Osmanlı kuşatmasını atlatmasını, Barok banliyölerini Linienwall'a kadar "
   "yaymasını, surlarını Ringstraße'ye bırakmasını, Tuna'yı düzleştirmesini ve iki milyonluk bir şehre dönüşmesini izleyin: Aziz "
   "Stephan Katedrali, Hofburg, Schönbrunn, Belvedere, Karlskirche, Opera, Riesenrad, Kızıl Viyana, 1945 savaşı, BM Şehri ve Tuna "
   "Adası; yıl ve nüfus ekranda."),
  "tags": ["vienna history", "history of vienna", "vindobona", "siege of vienna", "3d timelapse", "city evolution", "how vienna grew",
           "vienna timelapse", "ringstrasse", "habsburg", "st stephens cathedral", "austria history", "urban history", "wien geschichte"],
  "hashtags": ["#Vienna", "#History", "#Timelapse"],
  "playlist": T("Cities of Europe", "Avrupa Şehirleri"),
  "playlist_desc": T("European cities rebuilt in 3D, from the first stone to the skyline.", "Avrupa şehirleri 3D olarak, ilk taştan siluete."),
  "thumb": {"line1": T("Vienna", "Viyana"), "line2": T("1,900 YEARS", "1.900 YIL"), "line3": T("From Roman fort to imperial capital", "Roma kalesinden imparatorluk başkentine"),
            "extra": "&mood=golden&pitch=30&az=0&cam=48.2080,16.3700,6.0"},
 },
 "sources": json.load(open(os.path.join(HERE, "_sources.json"))),
}
total = sum(s_["seconds"] for s_ in S)
mins = round(total / 60)
city["intro"] = T(f"1,900 Years in {mins} Minutes", f"{mins} Dakikada 1.900 Yıl")
city["youtube"]["title"] = T(f"Vienna: 1,900 Years in {mins} Minutes (3D Timelapse)", f"Viyana: {mins} Dakikada 1.900 Yıl (3D Timelapse)")
json.dump(city, open(os.path.join(HERE, "city.json"), "w"), ensure_ascii=False, indent=1)
print("segments", len(S), "duration", total, "s =", f"{total // 60}:{total % 60:02d}")
