"""Builds cities/berlin/city.json. Every date/figure is from research.md (sources listed there).
Run: python3 cities/berlin/_build.py
Wall courses, district outlines, open spaces and the 1961 Wall ring are simplified traces (marked ≈ in research.md)."""
import json, math, os

T = lambda en, tr: {"en": en, "tr": tr}
HERE = os.path.dirname(os.path.abspath(__file__))
rect = lambda s, w, n, e: [(s, w), (n, w), (n, e), (s, e)]


def L(pts):
    return [[round(a, 5), round(b, 5)] for a, b in pts]


def circle(c, r_m, n=10):
    kx = 111.32 * math.cos(math.radians(c[0])); kz = 110.574
    return [(c[0] + r_m / 1000 / kz * math.sin(2 * math.pi * i / n), c[1] + r_m / 1000 / kx * math.cos(2 * math.pi * i / n)) for i in range(n)]


# ------------------------------------------------------------------ landmarks' published coordinates (research.md)
NIKOLAI = (52.51680, 13.40755); MARIEN = (52.52056, 13.40667); PALACE = (52.51750, 13.40278); DOM = (52.5191, 13.4011)
BTOR = (52.51639, 13.37778); REICHSTAG = (52.51861, 13.37611); RATHAUS = (52.51861, 13.40833); CHARL = (52.52083, 13.29583)
KWMC = (52.50500, 13.33500); THF = (52.47361, 13.40167); OLY = (52.51472, 13.23944); TV = (52.52083, 13.40944)
POTSPL = (52.50889, 13.37639); HBF = (52.52500, 13.36944); BER = (52.36667, 13.50333); SIEG2 = (52.51444, 13.35000)
SIEG1 = (52.5186, 13.3725)   # Königsplatz ≈

# ------------------------------------------------------------------ geography (lat, lon); ≈ traces, see research.md
CORE_C = (52.5165, 13.4060)
# Cölln: island between the Spree and the Spreekanal (south part of today's Museum/Fischer island)
COELLN = [(52.5100, 13.4085), (52.5112, 13.4045), (52.5130, 13.4008), (52.5160, 13.3995), (52.5166, 13.4030), (52.5155, 13.4043),
          (52.5146, 13.4074), (52.5136, 13.4094), (52.5120, 13.4098)]
# Alt-Berlin on the north-east bank
ALTBERLIN = [(52.5150, 13.4095), (52.5160, 13.4072), (52.5170, 13.4052), (52.5182, 13.4040), (52.5196, 13.4026), (52.5210, 13.4012),
             (52.5219, 13.4006), (52.5226, 13.4060), (52.5224, 13.4112),
             (52.5195, 13.4135), (52.5160, 13.4140), (52.5134, 13.4118)]
WALL_B = [(52.5218, 13.4003), (52.5226, 13.4060), (52.5224, 13.4112), (52.5195, 13.4135), (52.5160, 13.4140), (52.5133, 13.4118)]
WALL_C = [(52.5100, 13.4088), (52.5112, 13.4045), (52.5130, 13.4006), (52.5161, 13.3990), (52.5164, 13.4024), (52.5168, 13.4033)]
# Fortress (13 bastions, 1650–1683), a ring outside the old wall incl. Friedrichswerder
FORT_N = [(52.5228, 13.3990), (52.5240, 13.4060), (52.5236, 13.4130), (52.5205, 13.4165), (52.5160, 13.4170), (52.5126, 13.4148)]
FORT_S = [(52.5092, 13.4112), (52.5094, 13.4040), (52.5112, 13.3990), (52.5132, 13.3950), (52.5170, 13.3940), (52.5198, 13.3962),
          (52.5212, 13.3985)]
WERDER = [(52.5112, 13.3990), (52.5132, 13.3952), (52.5168, 13.3944), (52.5185, 13.3955), (52.5163, 13.3992), (52.5130, 13.4005)]
DOROTHEEN = [(52.5150, 13.3790), (52.5208, 13.3790), (52.5210, 13.3930), (52.5170, 13.3942), (52.5150, 13.3945)]
FRIEDRICH = [(52.4985, 13.3830), (52.5150, 13.3795), (52.5150, 13.3945), (52.5130, 13.3955), (52.5100, 13.3995), (52.5000, 13.4000)]
# Customs wall 1737–1868, north of the Spree (Unterbaum → Oberbaum) and south (Silesian Gate → Spree near the Reichstag)
CUST_N = [(52.5236, 13.3755), (52.5270, 13.3792), (52.5276, 13.3875), (52.5297, 13.4015), (52.5290, 13.4135), (52.5262, 13.4245),
          (52.5222, 13.4290), (52.5168, 13.4385), (52.5120, 13.4440), (52.5040, 13.4448)]
CUST_S = [(52.5012, 13.4452), (52.5003, 13.4425), (52.4990, 13.4180), (52.4975, 13.3915), (52.5032, 13.3815), (52.5093, 13.3770), (52.5164, 13.3772),
          (52.5191, 13.3765)]
INNER = CUST_N + CUST_S           # area inside the customs wall (Spree runs through it)
INNER_SUB = INNER                 # 18th-century suburbs (holes: old town, new towns)
OLD_TOWN = [(52.5228, 13.3990), (52.5240, 13.4060), (52.5236, 13.4130), (52.5205, 13.4165), (52.5160, 13.4170), (52.5100, 13.4140),
            (52.5092, 13.4040), (52.5112, 13.3990), (52.5132, 13.3950), (52.5170, 13.3940), (52.5198, 13.3962)]
TIERGARTEN = [(52.5085, 13.3765), (52.5195, 13.3762), (52.5205, 13.3600), (52.5180, 13.3420), (52.5115, 13.3370), (52.5075, 13.3450),
              (52.5070, 13.3650)]
THF_FIELD = [(52.4680, 13.3920), (52.4815, 13.3900), (52.4825, 13.4150), (52.4690, 13.4185)]
# Wilhelmine ring inside the Ringbahn (Hobrecht Plan area)
RING = [(52.5010, 13.2830), (52.5180, 13.2850), (52.5300, 13.3000), (52.5340, 13.3290), (52.5370, 13.3440), (52.5430, 13.3660),
        (52.5487, 13.3885), (52.5490, 13.4140), (52.5450, 13.4270), (52.5400, 13.4390), (52.5290, 13.4560), (52.5240, 13.4650),
        (52.5140, 13.4750), (52.5030, 13.4690), (52.4935, 13.4620), (52.4730, 13.4550), (52.4690, 13.4420), (52.4675, 13.4310),
        (52.4700, 13.3850), (52.4750, 13.3650), (52.4795, 13.3520), (52.4785, 13.3420), (52.4775, 13.3290), (52.4800, 13.3120),
        (52.4890, 13.3000), (52.4960, 13.2900)]
CHARL_TOWN = [(52.5130, 13.2920), (52.5195, 13.2920), (52.5195, 13.3150), (52.5130, 13.3150)]
SPANDAU = circle((52.5375, 13.2030), 320)
KOEPENICK = circle((52.4450, 13.5750), 280)
# Greater Berlin limits (1920), ±1–2 km
LIMITS = [(52.6600, 13.3100), (52.6400, 13.4000), (52.6300, 13.4900), (52.5900, 13.5600), (52.5600, 13.6400), (52.5000, 13.6700),
          (52.4500, 13.7500), (52.4000, 13.7300), (52.3800, 13.6400), (52.3900, 13.5200), (52.3700, 13.4300), (52.3900, 13.3400),
          (52.4000, 13.2400), (52.4000, 13.1200), (52.4300, 13.1100), (52.4900, 13.1200), (52.5500, 13.1300), (52.5900, 13.1800),
          (52.6300, 13.2300)]
GRUNEWALD = [(52.4300, 13.1900), (52.5000, 13.2100), (52.4950, 13.2650), (52.4600, 13.2700), (52.4300, 13.2350)]
TEGEL_F = [(52.5800, 13.2200), (52.6300, 13.2300), (52.6250, 13.2800), (52.5850, 13.2850)]
KOEP_F = [(52.3800, 13.6000), (52.4400, 13.6000), (52.4500, 13.7300), (52.3900, 13.7200)]
POTS_Q = [(52.5060, 13.3700), (52.5110, 13.3700), (52.5112, 13.3785), (52.5062, 13.3785)]
# Berlin Wall (1961–1990): inner-city section, then the outer ring around West Berlin (≈)
BWALL = [(52.5545, 13.3980), (52.5355, 13.3895), (52.5262, 13.3722), (52.5222, 13.3732), (52.5182, 13.3790), (52.5163, 13.3792),
         (52.5093, 13.3792), (52.5068, 13.3832), (52.5075, 13.3904), (52.5080, 13.4040), (52.5066, 13.4160), (52.5105, 13.4270),
         (52.5022, 13.4460), (52.4960, 13.4610), (52.4730, 13.4720), (52.4130, 13.4900), (52.3850, 13.4100), (52.3950, 13.2850),
         (52.4100, 13.2300), (52.3950, 13.1250), (52.4135, 13.0905), (52.4300, 13.1000), (52.4700, 13.1080), (52.5350, 13.1250),
         (52.6200, 13.2050), (52.6500, 13.2950), (52.6250, 13.3600), (52.5900, 13.3800), (52.5545, 13.3980)]

# ------------------------------------------------------------------ population (research.md): sourced anchors, log-interpolated
ANCH = [(1250, 1200), (1307, 7000), (1400, 8500), (1576, 12000), (1600, 9000), (1618, 12000), (1631, 8100), (1642, 7500), (1648, 6000),
        (1654, 6197), (1680, 10000), (1685, 17500), (1690, 21500), (1700, 29000), (1709, 55000), (1710, 60000), (1712, 61000),
        (1750, 113289), (1755, 126661), (1760, 95245), (1775, 136137), (1786, 147338), (1800, 172132), (1806, 155000), (1810, 162971),
        (1825, 219968), (1840, 322626), (1849, 418733), (1861, 524900), (1871, 826341), (1880, 1122330), (1890, 1578794),
        (1900, 1888848), (1910, 2071257), (1916, 1712679), (1919.8, 1902509),
        (1920.75, 3800000), (1921, 3879409), (1925, 4024286), (1933, 4242501), (1939, 4338756), (1945.0, 2900000), (1945.6, 2807405),
        (1946.8, 3170832), (1950, 3336026), (1960, 3274016), (1970, 3208719), (1980, 3048759), (1990, 3433695), (2000, 3382169),
        (2010, 3460725), (2016, 3670622), (2020, 3664088), (2025, 3700577), (2026, 3700577)]


def P(y):
    for y0, p0 in ANCH:
        if y == y0: return p0
    for (y0, p0), (y1, p1) in zip(ANCH, ANCH[1:]):
        if y0 <= y <= y1:
            u = (y - y0) / (y1 - y0); v = math.exp(math.log(p0) + (math.log(p1) - math.log(p0)) * u)
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


SLAV = T("Slavic Lands", "Slav Toprakları"); MARK = T("Margraviate of Brandenburg", "Brandenburg Uç Beyliği")
ELEC = T("Electorate of Brandenburg", "Brandenburg Prensliği"); PRUS = T("Kingdom of Prussia", "Prusya Krallığı")
EMP = T("German Empire", "Alman İmparatorluğu"); WEIM = T("Weimar Republic", "Weimar Cumhuriyeti"); NAZI = T("Nazi Germany", "Nazi Almanyası")
OCC = T("Allied Occupation", "Müttefik İşgali"); DIV = T("Divided City", "Bölünmüş Şehir"); UNI = T("Reunified Germany", "Birleşik Almanya")
TODAY = T("Today", "Bugün")
SPREE = T("Banks of the Spree", "Spree kıyısı"); CB = T("Berlin-Cölln", "Berlin-Cölln"); BER_N = T("Berlin", "Berlin")
WB = T("Berlin", "Berlin")

C0 = (52.5150, 13.4060)
S = [
 seg(650, 1156, 18, SLAV, SPREE, T("Slavs on the Spree", "Spree'de Slavlar"),
     T("7th century: Slavic Hevelli and Sprevane settle here; their main forts are Spandau and Köpenick",
       "7. yüzyıl: Slav Heveller ve Sprevanlar buraya yerleşir; ana kaleleri Spandau ve Köpenick'tir"),
     cam=(52.4950, 13.3900, 26.0), chapter=T("Before Berlin", "Berlin'den Önce")),
 seg(1157, 1182, 15, MARK, SPREE, T("The Margraves Arrive", "Uç Beyleri Geliyor"),
     T("1157: Albert the Bear founds the Margraviate of Brandenburg", "1157: Ayı Albrecht, Brandenburg Uç Beyliği'ni kurar"),
     cam=(52.5100, 13.4000, 12.0)),
 seg(1183, 1219, 16, MARK, SPREE, T("A Beam from 1183", "1183'ten Bir Kiriş"),
     T("An oak beam dug up at Petriplatz in 2008 probably dates from 1183",
       "2008'de Petriplatz'ta çıkarılan meşe kirişi büyük olasılıkla 1183 yılına ait"),
     cam=(C0[0], C0[1], 3.2)),
 seg(1220, 1236, 15, MARK, SPREE, T("St Nicholas' Church", "Aziz Nikolaus Kilisesi"),
     T("c. 1220–1230: St Nicholas' Church is built on the north-east bank of the Spree",
       "~1220–1230: Spree'nin kuzeydoğu kıyısında Aziz Nikolaus Kilisesi yapılır"),
     cam=(52.5160, 13.4070, 2.4)),
 seg(1237, 1243, 16, MARK, T("Cölln", "Cölln"), T("Cölln Is Named", "Cölln'ün Adı Geçiyor"),
     T("28 October 1237: a deed names a priest of Cölln, Berlin's official founding date",
       "28 Ekim 1237: bir belge Cölln'lü bir rahibi anar; Berlin'in resmî kuruluş tarihi"),
     cam=(52.5135, 13.4040, 2.0), chapter=T("Twin Towns on the Spree", "Spree'de İkiz Kasabalar")),
 seg(1244, 1249, 15, MARK, CB, T("Berlin Appears", "Berlin Ortaya Çıkıyor"),
     T("29 April 1244: Berlin, across the river from Cölln, is first named in a document",
       "29 Nisan 1244: Cölln'ün karşı kıyısındaki Berlin ilk kez bir belgede anılır"),
     pop=1200, cam=(52.5175, 13.4085, 2.2)),
 seg(1250, 1291, 16, MARK, CB, T("A Wall of Stone", "Taştan Bir Sur"),
     T("From about 1250 a stone wall rises around the two towns; by 1280 their seal shows two bears",
       "~1250'den itibaren iki kasabanın çevresinde taş sur yükselir; 1280'de mühürde iki ayı vardır"),
     pop=PI(1250, 1291), cam=(52.5160, 13.4065, 2.6)),
 seg(1292, 1306, 14, MARK, CB, T("St Mary's Church", "Aziz Meryem Kilisesi"),
     T("By 1292 a second parish church, St Mary's, is on record in Berlin",
       "1292'de Berlin'de ikinci bir bölge kilisesi, Aziz Meryem, kayıtlardadır"),
     pop=PI(1292, 1306), cam=(52.5200, 13.4070, 2.0)),
 seg(1307, 1359, 16, MARK, CB, T("Twin Towns Unite", "İkiz Kasabalar Birleşiyor"),
     T("20 March 1307: Berlin and Cölln form a union and share a new town hall",
       "20 Mart 1307: Berlin ve Cölln bir birlik kurar ve yeni bir belediye binasını paylaşır"),
     pop=PI(1307, 1359), cam=(52.5160, 13.4070, 2.4)),
 seg(1360, 1379, 15, MARK, CB, T("A Hanseatic Town", "Bir Hansa Kasabası"),
     T("1360: Berlin-Cölln joins the Hanseatic League of trading towns",
       "1360: Berlin-Cölln, ticaret kentlerinin Hansa Birliği'ne katılır"),
     pop=PI(1360, 1379), cam=(52.5155, 13.4060, 2.8)),
 seg(1380, 1410, 16, MARK, CB, T("The Great Fire", "Büyük Yangın"),
     T("1380: fire sweeps the town centre and destroys most of the early records",
       "1380: yangın kent merkezini sarar ve ilk kayıtların çoğunu yok eder"),
     pop=PI(1380, 1410), cam=(52.5165, 13.4080, 2.2)),
 seg(1411, 1442, 15, ELEC, CB, T("The Hohenzollerns", "Hohenzollernler"),
     T("1411: Frederick of Hohenzollern takes over Brandenburg; in 1415 he becomes elector",
       "1411: Hohenzollern'li Friedrich Brandenburg'u devralır; 1415'te prens-seçici olur"),
     pop=PI(1411, 1442), cam=(52.5160, 13.4060, 2.8), chapter=T("Hohenzollern Residence", "Hohenzollern Sarayı")),
 seg(1443, 1447, 16, ELEC, CB, T("A Castle on the Spree", "Spree'de Bir Kale"),
     T("1443: the elector begins a castle in Cölln, the future Berlin Palace",
       "1443: prens-seçici Cölln'de bir kale yapmaya başlar; geleceğin Berlin Sarayı"),
     pop=PI(1443, 1447), cam=(52.5170, 13.4035, 1.8)),
 seg(1448, 1485, 15, ELEC, CB, T("The Berlin Indignation", "Berlin Öfkesi"),
     T("1448: townspeople rise against the castle and lose their old freedoms",
       "1448: kentliler kaleye karşı ayaklanır ve eski özgürlüklerini kaybeder"),
     pop=PI(1448, 1485), cam=(52.5165, 13.4050, 2.4)),
 seg(1486, 1538, 14, ELEC, CB, T("Seat of the Electors", "Prens-Seçicilerin Merkezi"),
     T("11 March 1486: the palace becomes the electors' seat; in 1530 the Tiergarten is a royal hunt",
       "11 Mart 1486: saray prens-seçicilerin kalıcı merkezi olur; 1530'da Tiergarten av alanı olur"),
     pop=PI(1486, 1538), cam=(52.5160, 13.3960, 4.2)),
 seg(1539, 1575, 13, ELEC, CB, T("The Reformation", "Reform"),
     T("1 November 1539: Brandenburg and Berlin turn Lutheran", "1 Kasım 1539: Brandenburg ve Berlin Lutherci olur"),
     pop=PI(1539, 1575), cam=(52.5165, 13.4060, 2.6)),
 seg(1576, 1617, 15, ELEC, CB, T("Plague", "Veba"),
     T("1576: bubonic plague kills about 6,000 people", "1576: hıyarcıklı veba yaklaşık 6.000 kişiyi öldürür"),
     pop=PI(1576, 1617), cam=(52.5160, 13.4070, 2.4)),
 seg(1618, 1646, 18, ELEC, CB, T("The Thirty Years' War", "Otuz Yıl Savaşları"),
     T("1618–1648: war damages a third of the houses; Berlin loses half its people",
       "1618–1648: savaş evlerin üçte birine zarar verir; Berlin halkının yarısını kaybeder"),
     pop=PI(1618, 1646), cam=(52.5160, 13.4060, 2.8), chapter=T("Fortress and Kingdom", "Kale ve Krallık")),
 seg(1647, 1649, 14, ELEC, CB, T("Under the Lime Trees", "Ihlamurların Altında"),
     T("1647: the Great Elector lays out the avenue Unter den Linden", "1647: Büyük Prens-Seçici Unter den Linden caddesini açar"),
     pop=PI(1647, 1649), cam=(52.5170, 13.3920, 3.2)),
 seg(1650, 1673, 18, ELEC, CB, T("Fortress Berlin", "Kale Berlin"),
     T("From 1650 a fortress with 13 bastions rings Berlin, Cölln and Friedrichswerder",
       "1650'den itibaren 13 tabyalı bir kale Berlin, Cölln ve Friedrichswerder'i çevreler"),
     pop=PI(1650, 1673), cam=(52.5160, 13.4040, 3.2)),
 seg(1674, 1684, 15, ELEC, CB, T("Dorotheenstadt", "Dorotheenstadt"),
     T("1674: Dorotheenstadt, a new town west of the fortress, gets town rights",
       "1674: kalenin batısındaki yeni kasaba Dorotheenstadt kasaba hakları alır"),
     pop=PI(1674, 1684), cam=(52.5170, 13.3920, 3.0)),
 seg(1685, 1687, 16, ELEC, CB, T("The Huguenots", "Huguenotlar"),
     T("1685: the Edict of Potsdam; 6,000 French Huguenot refugees settle in Berlin",
       "1685: Potsdam Fermanı; 6.000 Fransız Huguenot mülteci Berlin'e yerleşir"),
     pop=PI(1685, 1687), cam=(52.5150, 13.3980, 3.4)),
 seg(1688, 1700, 16, ELEC, CB, T("Friedrichstadt", "Friedrichstadt"),
     T("From 1688 a new grid town, Friedrichstadt, is laid out; in 1699 Charlottenburg Palace opens",
       "1688'den itibaren ızgara planlı Friedrichstadt kurulur; 1699'da Charlottenburg Sarayı açılır"),
     pop=PI(1688, 1700), cam=(52.5120, 13.3700, 7.0)),
 seg(1701, 1709, 16, PRUS, CB, T("A Royal Capital", "Bir Kraliyet Başkenti"),
     T("18 January 1701: the elector becomes King in Prussia and Berlin his capital",
       "18 Ocak 1701: prens-seçici Prusya kralı olur ve Berlin onun başkenti olur"),
     pop=PI(1701, 1709), cam=(52.5160, 13.4000, 3.0)),
 seg(1710, 1733, 15, PRUS, BER_N, T("One City", "Tek Şehir"),
     T("1 January 1710: five towns unite as the royal capital Berlin, with 60,000 people",
       "1 Ocak 1710: beş kasaba 60.000 kişilik kraliyet başkenti Berlin olarak birleşir"),
     pop=PI(1710, 1733), cam=(52.5130, 13.3950, 4.5)),
 seg(1734, 1739, 16, PRUS, BER_N, T("The Customs Wall", "Gümrük Duvarı"),
     T("1734–1737: the fortress is given up; a customs wall with 14 gates rings the growing city",
       "1734–1737: kale terk edilir; 14 kapılı bir gümrük duvarı büyüyen şehri çevreler"),
     pop=PI(1734, 1739), cam=(52.5130, 13.4050, 6.5)),
 seg(1740, 1756, 14, PRUS, BER_N, T("Frederick the Great", "Büyük Friedrich"),
     T("1740: Frederick the Great begins his 46-year reign", "1740: Büyük Friedrich 46 yıllık saltanatına başlar"),
     pop=PI(1740, 1756), cam=(52.5150, 13.3950, 4.5)),
 seg(1757, 1787, 14, PRUS, BER_N, T("Occupied for Four Days", "Dört Günlük İşgal"),
     T("9–12 October 1760: Russian and Austrian troops briefly take the city",
       "9–12 Ekim 1760: Rus ve Avusturya birlikleri şehri kısa süreliğine ele geçirir"),
     pop=PI(1757, 1787), cam=(52.5130, 13.4050, 6.0)),
 seg(1788, 1805, 16, PRUS, BER_N, T("The Brandenburg Gate", "Brandenburg Kapısı"),
     T("1788–1791: the Brandenburg Gate is built in the customs wall at the end of Unter den Linden",
       "1788–1791: Brandenburg Kapısı, Unter den Linden'in ucunda gümrük duvarına yapılır"),
     pop=PI(1788, 1805), cam=(52.5160, 13.3800, 2.0)),
 seg(1806, 1809, 14, PRUS, BER_N, T("Napoleon in Berlin", "Napolyon Berlin'de"),
     T("24 October 1806: the French army marches in and occupies Berlin",
       "24 Ekim 1806: Fransız ordusu Berlin'e girer ve şehri işgal eder"),
     pop=PI(1806, 1809), cam=(52.5150, 13.3850, 4.0), chapter=T("The Industrial City", "Sanayi Şehri")),
 seg(1810, 1837, 14, PRUS, BER_N, T("A New University", "Yeni Bir Üniversite"),
     T("15 October 1810: the University of Berlin opens, today Humboldt University",
       "15 Ekim 1810: Berlin Üniversitesi açılır; bugünkü Humboldt Üniversitesi"),
     pop=PI(1810, 1837), cam=(52.5150, 13.3950, 5.0)),
 seg(1838, 1847, 15, PRUS, BER_N, T("The Railway Age", "Demiryolu Çağı"),
     T("29 October 1838: Prussia's first railway opens, from Berlin to Potsdam",
       "29 Ekim 1838: Prusya'nın ilk demiryolu Berlin ile Potsdam arasında açılır"),
     pop=PI(1838, 1847), cam=(52.4800, 13.3300, 14.0)),
 seg(1848, 1859, 14, PRUS, BER_N, T("Barricades", "Barikatlar"),
     T("18 March 1848: street fighting at the barricades; the king promises reforms",
       "18 Mart 1848: barikatlarda sokak çatışmaları; kral reform sözü verir"),
     pop=PI(1848, 1859), cam=(52.5160, 13.4000, 4.0)),
 seg(1860, 1861.9, 14, PRUS, BER_N, T("The Wall Comes Down", "Duvar Yıkılıyor"),
     T("1860: the customs wall loses its purpose; Moabit and Wedding join Berlin in 1861",
       "1860: gümrük duvarı işlevini yitirir; Moabit ve Wedding 1861'de Berlin'e katılır"),
     pop=PI(1860, 1861.9), cam=(52.5200, 13.3900, 8.0)),
 seg(1862, 1870, 17, PRUS, BER_N, T("The Hobrecht Plan", "Hobrecht Planı"),
     T("18 July 1862: the Hobrecht Plan maps ring roads and blocks for 50 years of growth",
       "18 Temmuz 1862: Hobrecht Planı 50 yıllık büyüme için çevre yolları ve adaları çizer"),
     pop=PI(1862, 1870), cam=(52.5100, 13.3900, 11.0)),
 seg(1871, 1883, 18, EMP, BER_N, T("Imperial Capital", "İmparatorluk Başkenti"),
     T("18 January 1871: Berlin becomes capital of the new German Empire",
       "18 Ocak 1871: Berlin yeni Alman İmparatorluğu'nun başkenti olur"),
     pop=PI(1871, 1883), cam=(52.5150, 13.3700, 6.0), chapter=T("Imperial Berlin", "İmparatorluk Berlini")),
 seg(1884, 1901, 16, EMP, BER_N, T("The Reichstag", "Reichstag"),
     T("1884–1894: the Reichstag is built; by 1890 Berlin has 1.5 million people",
       "1884–1894: Reichstag inşa edilir; 1890'da Berlin'in nüfusu 1,5 milyonu bulur"),
     pop=PI(1884, 1901), cam=(52.5180, 13.3780, 3.0)),
 seg(1902, 1918.8, 15, EMP, BER_N, T("The U-Bahn", "Metro"),
     T("1902: after six years of work, Berlin's first U-Bahn line starts running",
       "1902: altı yıllık çalışmanın ardından Berlin'in ilk metro hattı çalışmaya başlar"),
     pop=PI(1902, 1918.8), cam=(52.5050, 13.4000, 10.0)),
 seg(1918.85, 1919.8, 15, WEIM, BER_N, T("A Republic", "Bir Cumhuriyet"),
     T("9 November 1918: a German republic is proclaimed from the Reichstag",
       "9 Kasım 1918: Reichstag'dan bir Alman cumhuriyeti ilan edilir"),
     pop=PI(1918.85, 1919.8), cam=(52.5180, 13.3800, 3.0)),
 seg(1920.75, 1932, 20, WEIM, BER_N, T("Greater Berlin", "Büyük Berlin"),
     T("1 October 1920: 8 towns, 59 villages and 27 estates merge into a city of 3.8 million",
       "1 Ekim 1920: 8 kasaba, 59 köy ve 27 malikâne 3,8 milyonluk tek bir şehirde birleşir"),
     pop=PI(1920.75, 1932), cam=(52.5000, 13.4000, 34.0), chapter=T("Greater Berlin", "Büyük Berlin")),
 seg(1933, 1935, 15, NAZI, BER_N, T("The Reichstag Fire", "Reichstag Yangını"),
     T("27 February 1933: the Reichstag burns, weeks after Hitler becomes chancellor",
       "27 Şubat 1933: Hitler'in şansölye olmasından haftalar sonra Reichstag yanar"),
     pop=PI(1933, 1935), cam=(52.5180, 13.3780, 3.0)),
 seg(1936, 1938.8, 15, NAZI, BER_N, T("The 1936 Olympics", "1936 Olimpiyatları"),
     T("1 August 1936: the Olympic Games open in the new Olympic Stadium",
       "1 Ağustos 1936: Olimpiyat Oyunları yeni Olimpiyat Stadı'nda açılır"),
     pop=PI(1936, 1938.8), cam=(52.5150, 13.2400, 4.0)),
 seg(1938.85, 1943.8, 15, NAZI, BER_N, T("Kristallnacht", "Kristal Gecesi"),
     T("November 1938: Nazis attack synagogues and Jewish property in Berlin",
       "Kasım 1938: Naziler Berlin'deki sinagoglara ve Yahudi mülklerine saldırır"),
     pop=PI(1938.85, 1943.8), cam=(52.5150, 13.3900, 7.0)),
 seg(1943.85, 1945.25, 18, NAZI, BER_N, T("Bombs on Berlin", "Berlin'e Bombalar"),
     T("363 air raids hit Berlin; about a third of the city is badly damaged",
       "Berlin 363 hava saldırısına uğrar; şehrin yaklaşık üçte biri ağır hasar görür"),
     pop=PI(1943.85, 1945.25), cam=(52.5100, 13.3800, 14.0), chapter=T("War and Division", "Savaş ve Bölünme")),
 seg(1945.29, 1945.4, 18, NAZI, BER_N, T("The Battle of Berlin", "Berlin Muharebesi"),
     T("16 April – 2 May 1945: the Soviet army takes Berlin; about 100,000 civilians die",
       "16 Nisan – 2 Mayıs 1945: Sovyet ordusu Berlin'i alır; yaklaşık 100.000 sivil ölür"),
     pop=PI(1945.29, 1945.4), cam=(52.5150, 13.3850, 6.0)),
 seg(1945.5, 1948.4, 15, OCC, BER_N, T("Four Sectors", "Dört Bölge"),
     T("July 1945: the city is split into American, British, French and Soviet sectors",
       "Temmuz 1945: şehir Amerikan, İngiliz, Fransız ve Sovyet bölgelerine ayrılır"),
     pop=PI(1945.6, 1948.4), cam=(52.5000, 13.3900, 22.0)),
 seg(1948.48, 1949.4, 17, OCC, BER_N, T("The Airlift", "Hava Köprüsü"),
     T("24 June 1948 – 12 May 1949: a Soviet blockade; 278,228 flights supply West Berlin",
       "24 Haziran 1948 – 12 Mayıs 1949: Sovyet ablukası; 278.228 uçuş Batı Berlin'i besler"),
     pop=PI(1948.48, 1949.4), cam=(52.4800, 13.4000, 6.0)),
 seg(1949.5, 1953.4, 15, DIV, BER_N, T("The Palace Is Destroyed", "Saray Yıkılıyor"),
     T("1950: East Germany demolishes the war-damaged Berlin Palace", "1950: Doğu Almanya savaşta hasar gören Berlin Sarayı'nı yıktırır"),
     pop=PI(1949.5, 1953.4), cam=(52.5170, 13.4030, 2.0)),
 seg(1953.45, 1961.6, 14, DIV, BER_N, T("Uprising in the East", "Doğu'da Ayaklanma"),
     T("17 June 1953: an uprising in East Berlin is put down",
       "17 Haziran 1953: Doğu Berlin'de bir ayaklanma bastırılır"),
     pop=PI(1953.45, 1961.6), cam=(52.5150, 13.4100, 6.0)),
 seg(1961.62, 1968, 20, DIV, BER_N, T("The Wall", "Duvar"),
     T("13 August 1961: the GDR begins a wall around West Berlin, 155 km long",
       "13 Ağustos 1961: Doğu Almanya Batı Berlin'in çevresine 155 km'lik bir duvar örmeye başlar"),
     pop=PI(1961.62, 1968), cam=(52.4950, 13.3700, 34.0)),
 seg(1969, 1972, 15, DIV, BER_N, T("The TV Tower", "Televizyon Kulesi"),
     T("3 October 1969: East Berlin's 365 m TV tower is inaugurated",
       "3 Ekim 1969: Doğu Berlin'in 365 m'lik televizyon kulesi açılır"),
     pop=PI(1969, 1972), cam=(52.5180, 13.4050, 5.0)),
 seg(1973, 1989.8, 10, DIV, BER_N, pop=PI(1973, 1989.8), cam=(52.5100, 13.3900, 12.0)),
 seg(1989.85, 1990.7, 20, UNI, BER_N, T("The Wall Falls", "Duvar Yıkılıyor"),
     T("9 November 1989: the border opens; from June 1990 the Wall is torn down",
       "9 Kasım 1989: sınır açılır; Haziran 1990'dan itibaren Duvar yıkılır"),
     pop=PI(1989.85, 1990.7), cam=(52.5160, 13.3800, 4.0), chapter=T("One City Again", "Yeniden Tek Şehir")),
 seg(1990.75, 1997.9, 15, UNI, BER_N, T("Capital Again", "Yeniden Başkent"),
     T("3 October 1990: Germany is reunited; in 1991 parliament votes to return to Berlin",
       "3 Ekim 1990: Almanya yeniden birleşir; 1991'de meclis Berlin'e dönmeye karar verir"),
     pop=PI(1990.75, 1997.9), cam=(52.5150, 13.3900, 12.0)),
 seg(1998, 2005, 16, UNI, BER_N, T("A Glass Dome", "Cam Bir Kubbe"),
     T("19 April 1999: the Bundestag meets in the rebuilt Reichstag under its glass dome",
       "19 Nisan 1999: Federal Meclis cam kubbesiyle yenilenen Reichstag'da toplanır"),
     pop=PI(1998, 2005), cam=(52.5150, 13.3770, 2.6)),
 seg(2006, 2019, 15, UNI, BER_N, T("A New Main Station", "Yeni Bir Ana İstasyon"),
     T("26 May 2006: the Hauptbahnhof opens; Tempelhof Airport closes in 2008",
       "26 Mayıs 2006: Hauptbahnhof açılır; Tempelhof Havalimanı 2008'de kapanır"),
     pop=PI(2006, 2019), cam=(52.5100, 13.3800, 9.0)),
 seg(2020, 2022, 14, TODAY, BER_N, T("A New Airport", "Yeni Bir Havalimanı"),
     T("31 October 2020: BER airport opens; the palace rises again as the Humboldt Forum",
       "31 Ekim 2020: BER havalimanı açılır; saray Humboldt Forum olarak yeniden yükselir"),
     pop=PI(2020, 2022), cam=(52.4300, 13.4500, 22.0), chapter=T("Berlin Today", "Bugünün Berlini")),
 seg(2023, 2026, 22, TODAY, BER_N, T("Berlin Today", "Bugünün Berlini"),
     T("From two riverside towns to 3,700,577 people at the end of 2025",
       "İki nehir kıyısı kasabasından 2025 sonunda 3.700.577 kişiye"),
     pop=[P(2023), 3700577], cam=(52.5050, 13.3950, 34.0)),
]


def wall(name, path, built, removed=None, height="mid", towers=90, draw=3.0, **kw):
    d = {"name": name, "path": L(path), "built": built, "height": height, "towers_m": towers, "draw_s": draw}
    if removed is not None: d["removed"] = removed
    d.update(kw); return d


districts = [
 {"name": "Spandau (Slavic fort, ≈)", "style": "celtic", "poly": L(SPANDAU), "from": 680, "to": 900, "density": 0.45, "grain_m": 60,
  "grow_from": [52.5375, 13.2030]},
 {"name": "Köpenick (Slavic fort, ≈)", "style": "celtic", "poly": L(KOEPENICK), "from": 700, "to": 900, "density": 0.45, "grain_m": 60,
  "grow_from": [52.4450, 13.5750]},
 {"name": "Cölln", "style": "medieval", "poly": L(COELLN), "from": 1183, "to": 1300, "density": 0.85, "grain_m": 40,
  "grow_from": [52.5120, 13.4040], "fade": [1625, 1640, 0.6]},
 {"name": "Alt-Berlin", "style": "medieval", "poly": L(ALTBERLIN), "from": 1200, "to": 1320, "density": 0.85, "grain_m": 40,
  "grow_from": [52.5168, 13.4078], "fade": [1625, 1640, 0.6]},
 {"name": "Old town rebuilt (17th c.)", "style": "stone", "poly": L(OLD_TOWN), "from": 1650, "to": 1700, "density": 0.85, "grain_m": 45,
  "grow_from": [52.5165, 13.4060], "fade": [1944.0, 1945.4, 0.62]},
 {"name": "Friedrichswerder (≈)", "style": "stone", "poly": L(WERDER), "from": 1658, "to": 1690, "density": 0.75, "grain_m": 45,
  "grow_from": [52.5150, 13.3975], "fade": [1944.0, 1945.4, 0.62]},
 {"name": "Dorotheenstadt (≈)", "style": "stone", "poly": L(DOROTHEEN), "from": 1674, "to": 1710, "density": 0.75, "grain_m": 50, "grid_deg": 0,
  "grow_from": [52.5175, 13.3920], "fade": [1944.0, 1945.4, 0.62]},
 {"name": "Friedrichstadt (≈)", "style": "stone", "poly": L(FRIEDRICH), "from": 1688, "to": 1740, "density": 0.8, "grain_m": 50, "grid_deg": 0,
  "grow_from": [52.5130, 13.3920], "fade": [1944.0, 1945.4, 0.62]},
 {"name": "Charlottenburg (town, ≈)", "style": "stone", "poly": L(CHARL_TOWN), "from": 1705, "to": 1800, "density": 0.45, "grain_m": 60,
  "grow_from": [52.5180, 13.2990]},
 {"name": "Suburbs inside the customs wall", "style": "georgian", "poly": L(INNER_SUB),
  "holes": [L(OLD_TOWN), L(DOROTHEEN), L(FRIEDRICH)], "from": 1700, "to": 1840, "density": 0.6, "grain_m": 60,
  "grow_from": [52.5165, 13.4060], "fade": [1944.0, 1945.4, 0.65]},
 {"name": "Wilhelmine ring (Hobrecht Plan)", "style": "victorian", "poly": L(RING), "holes": [L(INNER), L(TIERGARTEN), L(THF_FIELD), L(CHARL_TOWN)],
  "from": 1862, "to": 1914, "density": 0.85, "grain_m": 70, "grow_from": [52.5165, 13.4060], "fade": [1944.0, 1945.4, 0.72]},
 {"name": "Greater Berlin suburbs", "style": "suburb", "poly": L(LIMITS),
  "holes": [L(RING), L(GRUNEWALD), L(TEGEL_F), L(KOEP_F), L(THF_FIELD)], "from": 1895, "to": 1939, "density": 0.3, "grain_m": 115,
  "grow_from": [52.5165, 13.4060]},
 {"name": "Postwar rebuilding (centre)", "style": "modern", "poly": L(INNER), "holes": [L(TIERGARTEN)], "from": 1950, "to": 1975, "density": 0.7,
  "grain_m": 75, "grow_from": [52.5165, 13.4060]},
 {"name": "Postwar rebuilding (ring)", "style": "modern", "poly": L(RING), "holes": [L(INNER), L(TIERGARTEN), L(THF_FIELD)], "from": 1950,
  "to": 1980, "density": 0.75, "grain_m": 95, "grow_from": [52.5165, 13.4060]},
 {"name": "Postwar housing estates (≈)", "style": "modern", "poly": L(LIMITS),
  "holes": [L(RING), L(GRUNEWALD), L(TEGEL_F), L(KOEP_F), L(THF_FIELD)], "from": 1955, "to": 1990, "density": 0.25, "grain_m": 170,
  "grow_from": [52.5165, 13.4060]},
 {"name": "Potsdamer Platz", "style": "highrise", "poly": L(POTS_Q), "from": 1996, "to": 2000, "density": 0.75, "grain_m": 70,
  "grow_from": list(POTSPL)},
]

walls = [
 wall("Medieval wall (Berlin)", WALL_B, 1250, 1660, height="mid", towers=70, draw=3.0),
 wall("Medieval wall (Cölln)", WALL_C, 1250, 1660, height="mid", towers=70, draw=3.0),
 wall("Fortress (north)", FORT_N, 1658, 1745, height="high", towers=0, draw=4.0, moat=True),
 wall("Fortress (south and Friedrichswerder)", FORT_S, 1658, 1745, height="high", towers=0, draw=4.0, moat=True),
 wall("Customs wall (north)", CUST_N, 1735, 1868, height="low", towers=0, draw=4.0),
 wall("Customs wall (south)", CUST_S, 1735, 1868, height="low", towers=0, draw=4.0),
 wall("Berlin Wall", BWALL, 1961.62, 1990.6, height="low", towers=900, draw=5.0),
]

bridges = [
 {"name": "Lange Brücke (≈)", "path": [[52.5163, 13.4033], [52.5172, 13.4056]], "built": 1695, "style": "stone", "width_m": 18},
 {"name": "Oberbaum Bridge (≈)", "path": [[52.5032, 13.4462], [52.5007, 13.4440]], "built": 1896, "style": "stone", "width_m": 26},
]

roads = [
 {"name": "Unter den Linden", "path": L([(52.5172, 13.3995), (52.5170, 13.3900), (52.5166, 13.3795)]), "from": 1647, "kind": "avenue",
  "width_m": 40, "draw_s": 3},
 {"name": "Berlin–Potsdam railway (≈)", "path": L([(52.5060, 13.3760), (52.4900, 13.3600), (52.4600, 13.3200), (52.4300, 13.2600),
  (52.4100, 13.1800), (52.3950, 13.0950)]), "from": 1838.8, "kind": "rail", "width_m": 22},
]

C_ = lambda w, r: {"wall": w, "roof": r}
landmarks = [
 {"type": "church", "name": T("St Nicholas' Church", "Aziz Nikolaus Kilisesi"), "at": list(NIKOLAI), "built": 1225, "rise_s": 6,
  "size_m": [55, 24, 22], "rot_deg": 0, "colors": C_("#d9c7a8", "#6a5f55")},
 {"type": "church", "name": T("St Mary's Church", "Aziz Meryem Kilisesi"), "at": list(MARIEN), "built": 1292, "rise_s": 5,
  "size_m": [60, 25, 22], "rot_deg": 0, "colors": C_("#c98f6a", "#5f666f")},
 {"type": "castle", "name": T("Elector's castle", "Prens-seçicinin kalesi"), "at": list(PALACE), "built": 1443, "removed": 1689, "rise_s": 6,
  "size_m": [90, 60, 22], "colors": {"wall": "#d9cfb6"}},
 {"type": "palace", "name": T("Berlin Palace", "Berlin Sarayı"), "at": list(PALACE), "built": 1689, "removed": 1950.75, "rise_s": 12,
  "size_m": [190, 115, 30], "rot_deg": -30, "colors": C_("#e6dcc4", "#6f7a7f")},
 {"type": "box", "name": T("Palace of the Republic (≈)", "Cumhuriyet Sarayı (≈)"), "at": [52.5176, 13.4036], "built": 1973, "removed": 2006.2,
  "rise_s": 6, "size_m": [180, 85, 32], "rot_deg": -30, "colors": C_("#9a7a4a", "#3f4448")},
 {"type": "palace", "name": T("Humboldt Forum", "Humboldt Forum"), "at": list(PALACE), "built": 2013.45, "rise_s": 30, "size_m": [190, 115, 30],
  "rot_deg": -30, "colors": C_("#e6dcc4", "#6f7a7f")},
 {"type": "domechurch", "name": T("Berlin Cathedral (≈)", "Berlin Katedrali (≈)"), "at": list(DOM), "built": 1894, "rise_s": 14,
  "size_m": [114, 73, 60], "scale": 1.2, "colors": {"wall": "#cfc6b3", "dome": "#5f8c7a", "lantern": True}},
 {"type": "box", "name": T("Brandenburg Gate", "Brandenburg Kapısı"), "at": list(BTOR), "built": 1788, "rise_s": 10, "size_m": [63, 11, 26],
  "scale": 1.4, "rot_deg": 90, "colors": C_("#e6dfcf", "#6f8f6c")},
 {"type": "palace", "name": T("Charlottenburg Palace", "Charlottenburg Sarayı"), "at": list(CHARL), "built": 1695, "rise_s": 10,
  "size_m": [200, 60, 24], "scale": 1.3, "colors": C_("#e8d9a8", "#5f8c7a")},
 {"type": "parliament", "name": T("Red Town Hall", "Kızıl Belediye Binası"), "at": list(RATHAUS), "built": 1861, "rise_s": 12,
  "size_m": [100, 90, 30], "scale": 1.3, "colors": C_("#b35a3c", "#5a4a44")},
 {"type": "column", "name": T("Victory Column (Königsplatz)", "Zafer Sütunu (Königsplatz)"), "at": list(SIEG1), "built": 1873.67,
  "removed": 1938.5, "rise_s": 6, "size_m": [8, 8, 60], "colors": {"wall": "#d8cfbd", "top": "#c9a94a"}},
 {"type": "column", "name": T("Victory Column", "Zafer Sütunu"), "at": list(SIEG2), "built": 1939.3, "rise_s": 3, "size_m": [8, 8, 67],
  "colors": {"wall": "#d8cfbd", "top": "#c9a94a"}},
 {"type": "parliament", "name": T("Reichstag", "Reichstag"), "at": list(REICHSTAG), "built": 1884.45, "rise_s": 20, "size_m": [137, 97, 40],
  "scale": 1.0, "colors": C_("#cbc2ad", "#5c6a70")},
 {"type": "cathedral", "name": T("Kaiser Wilhelm Memorial Church", "Kaiser Wilhelm Anıt Kilisesi"), "at": list(KWMC), "built": 1891.2,
  "removed": 1943.89, "rise_s": 10, "size_m": [70, 30, 40], "scale": 1.3, "colors": {"wall": "#b8a88e", "roof": "#4f5a60"}},
 {"type": "tower", "name": T("Memorial church ruin", "Anıt kilise kalıntısı"), "at": list(KWMC), "built": 1943.9, "rise_s": 0.3, "size_m": [16, 16, 50],
  "colors": {"wall": "#6e675c", "roof": "#4a4540"}},
 {"type": "box", "name": T("Tempelhof terminal", "Tempelhof terminali"), "at": [52.4825, 13.3920], "built": 1936.3, "rise_s": 10,
  "size_m": [900, 50, 22], "rot_deg": -20, "colors": C_("#cfc5b0", "#7a7f80")},
 {"type": "stadium", "name": T("Olympic Stadium", "Olimpiyat Stadı"), "at": list(OLY), "built": 1934.3, "rise_s": 10, "size_m": [300, 230, 18],
  "scale": 1.2, "colors": {"wall": "#cfc6b3"}},
 {"type": "tower", "name": T("TV tower", "Televizyon kulesi"), "at": list(TV), "built": 1965.6, "rise_s": 12, "size_m": [20, 20, 260],
  "colors": {"wall": "#d8d8d4", "roof": "#c9c9c4"}},
 {"type": "skyscraper", "name": T("Potsdamer Platz tower", "Potsdamer Platz kulesi"), "at": [52.5098, 13.3762], "built": 1997, "rise_s": 5,
  "size_m": [40, 30, 103], "colors": {"wall": "#9a5a48"}},
 {"type": "skyscraper", "name": T("Sony Center tower (≈)", "Sony Center kulesi (≈)"), "at": [52.5100, 13.3735], "built": 1998.5, "rise_s": 5,
  "size_m": [40, 30, 103], "colors": {"wall": "#7f8d95"}},
 {"type": "station", "name": T("Hauptbahnhof", "Hauptbahnhof"), "at": list(HBF), "built": 2005.5, "rise_s": 8, "size_m": [320, 90, 30],
  "rot_deg": 0, "colors": C_("#d9d9d9", "#8a949b")},
 {"type": "box", "name": T("BER terminal", "BER terminali"), "at": list(BER), "built": 2019.5, "rise_s": 6, "size_m": [400, 220, 26],
  "colors": C_("#d6d3cb", "#8a949b")},
]

fires = [{"year": 1380.3, "poly": L(ALTBERLIN[:6] + [(52.5160, 13.4140)]), "duration_s": 6, "plumes": 5}]
smoke = [
 {"at": list(REICHSTAG), "from": 1933.15, "to": 1933.3, "scale": 1.0},
 {"at": [52.5150, 13.3950], "from": 1943.88, "to": 1945.25, "scale": 1.4},
 {"at": [52.5000, 13.4200], "from": 1943.95, "to": 1945.25, "scale": 1.1},
 {"at": [52.5300, 13.3600], "from": 1944.1, "to": 1945.25, "scale": 1.0},
 {"at": [52.5170, 13.3900], "from": 1945.29, "to": 1945.4, "scale": 1.5},
]
camps = [
 {"poly": L(rect(52.5240, 13.4200, 52.5320, 13.4400)), "from": 1945.29, "to": 1945.38, "count": 160},
 {"poly": L(rect(52.4950, 13.4300, 52.5050, 13.4550)), "from": 1945.29, "to": 1945.38, "count": 120},
]
open_spaces = [
 {"name": "Tiergarten (≈)", "poly": L(TIERGARTEN)},
 {"name": "Tempelhofer Feld (≈)", "poly": L(THF_FIELD)},
 {"name": "Grunewald (≈)", "poly": L(GRUNEWALD)},
 {"name": "Tegel forest (≈)", "poly": L(TEGEL_F)},
 {"name": "Köpenick forest (≈)", "poly": L(KOEP_F)},
]
labels = [
 {"text": T("SPREE", "SPREE"), "at": [52.5050, 13.4400], "kind": "water", "from": 650},
 {"text": T("HAVEL", "HAVEL"), "at": [52.4700, 13.1650], "kind": "water", "from": 650, "to": 1500},
 {"text": T("Spandau", "Spandau"), "at": [52.5375, 13.2030], "kind": "place", "from": 650, "to": 1156},
 {"text": T("Köpenick", "Köpenick"), "at": [52.4450, 13.5750], "kind": "place", "from": 650, "to": 1156},
 {"text": T("BRANDENBURG", "BRANDENBURG"), "at": [52.4700, 13.3500], "kind": "region", "from": 1157, "to": 1182},
 {"text": T("Petriplatz", "Petriplatz"), "at": [52.5120, 13.4035], "kind": "place", "from": 1183, "to": 1219},
 {"text": T("St Nicholas'", "Aziz Nikolaus"), "at": list(NIKOLAI), "from": 1225, "to": 1236, "lift_m": 30},
 {"text": T("CÖLLN", "CÖLLN"), "at": [52.5125, 13.4030], "kind": "region", "from": 1237, "to": 1306},
 {"text": T("BERLIN", "BERLIN"), "at": [52.5195, 13.4100], "kind": "region", "from": 1244, "to": 1306},
 {"text": T("St Mary's", "Aziz Meryem"), "at": list(MARIEN), "from": 1292, "to": 1306, "lift_m": 30},
 {"text": T("Castle", "Kale"), "at": list(PALACE), "from": 1444, "to": 1485, "lift_m": 30},
 {"text": T("Tiergarten", "Tiergarten"), "at": [52.5140, 13.3550], "kind": "place", "from": 1530, "to": 1538},
 {"text": T("UNTER DEN LINDEN", "UNTER DEN LINDEN"), "at": [52.5160, 13.3880], "kind": "region", "from": 1647, "to": 1649},
 {"text": T("FRIEDRICHSWERDER", "FRIEDRICHSWERDER"), "at": [52.5150, 13.3965], "kind": "region", "from": 1660, "to": 1673},
 {"text": T("DOROTHEENSTADT", "DOROTHEENSTADT"), "at": [52.5185, 13.3860], "kind": "region", "from": 1674, "to": 1684},
 {"text": T("FRIEDRICHSTADT", "FRIEDRICHSTADT"), "at": [52.5070, 13.3900], "kind": "region", "from": 1688, "to": 1700},
 {"text": T("Charlottenburg", "Charlottenburg"), "at": list(CHARL), "from": 1696, "to": 1700, "lift_m": 30},
 {"text": T("CUSTOMS WALL", "GÜMRÜK DUVARI"), "at": [52.4990, 13.4050], "kind": "region", "from": 1734, "to": 1739},
 {"text": T("Brandenburg Gate", "Brandenburg Kapısı"), "at": list(BTOR), "from": 1789, "to": 1809, "lift_m": 30},
 {"text": T("Potsdam", "Potsdam"), "at": [52.3950, 13.0950], "kind": "place", "from": 1838.8, "to": 1847},
 {"text": T("Moabit", "Moabit"), "at": [52.5280, 13.3400], "kind": "place", "from": 1860, "to": 1861.9},
 {"text": T("Wedding", "Wedding"), "at": [52.5460, 13.3620], "kind": "place", "from": 1860, "to": 1861.9},
 {"text": T("Red Town Hall", "Kızıl Belediye"), "at": list(RATHAUS), "from": 1866, "to": 1870, "lift_m": 60},
 {"text": T("Victory Column", "Zafer Sütunu"), "at": list(SIEG1), "from": 1874, "to": 1883, "lift_m": 80},
 {"text": T("Reichstag", "Reichstag"), "at": list(REICHSTAG), "from": 1888, "to": 1901, "lift_m": 70},
 {"text": T("Reichstag", "Reichstag"), "at": list(REICHSTAG), "from": 1918.85, "to": 1919.8, "lift_m": 70},
 {"text": T("Tempelhof", "Tempelhof"), "at": list(THF), "kind": "place", "from": 1923.8, "to": 1932},
 {"text": T("Spandau", "Spandau"), "at": [52.5375, 13.2030], "kind": "place", "from": 1920.75, "to": 1932},
 {"text": T("Köpenick", "Köpenick"), "at": [52.4450, 13.5750], "kind": "place", "from": 1920.75, "to": 1932},
 {"text": T("Reichstag", "Reichstag"), "at": list(REICHSTAG), "from": 1933, "to": 1935, "lift_m": 70},
 {"text": T("Olympic Stadium", "Olimpiyat Stadı"), "at": list(OLY), "from": 1936.4, "to": 1938.8, "lift_m": 40},
 {"text": T("WEST BERLIN", "BATI BERLİN"), "at": [52.4950, 13.3100], "kind": "region", "from": 1948.48, "to": 1990.6},
 {"text": T("EAST BERLIN", "DOĞU BERLİN"), "at": [52.5300, 13.4500], "kind": "region", "from": 1949.8, "to": 1990.6},
 {"text": T("Tempelhof", "Tempelhof"), "at": list(THF), "kind": "place", "from": 1948.48, "to": 1949.4},
 {"text": T("Palace", "Saray"), "at": list(PALACE), "from": 1949.5, "to": 1950.7, "lift_m": 40},
 {"text": T("TV tower", "Televizyon kulesi"), "at": list(TV), "from": 1969.8, "to": 1972, "lift_m": 280},
 {"text": T("Brandenburg Gate", "Brandenburg Kapısı"), "at": list(BTOR), "from": 1989.85, "to": 1990.7, "lift_m": 30},
 {"text": T("Reichstag", "Reichstag"), "at": list(REICHSTAG), "from": 1999.3, "to": 2005, "lift_m": 70},
 {"text": T("Potsdamer Platz", "Potsdamer Platz"), "at": list(POTSPL), "kind": "place", "from": 1998, "to": 2005},
 {"text": T("Hauptbahnhof", "Hauptbahnhof"), "at": list(HBF), "from": 2006.4, "to": 2019, "lift_m": 40},
 {"text": T("BER", "BER"), "at": list(BER), "kind": "place", "from": 2020.83, "to": 2022},
 {"text": T("TV tower", "Televizyon kulesi"), "at": list(TV), "from": 2023, "lift_m": 280},
 {"text": T("Tempelhofer Feld", "Tempelhofer Feld"), "at": list(THF), "kind": "place", "from": 2023},
]

city = {
 "slug": "berlin", "seed": 1237, "long_ok": True,
 "name": T("Berlin", "Berlin"), "intro": T("800 Years in 15 Minutes", "15 Dakikada 800 Yıl"), "intro_seconds": 4.5,
 "geo": {"bbox": [52.20, 12.90, 52.82, 13.95], "cell_m": 110, "core_bbox": [52.480, 13.320, 52.550, 13.480], "core_cell_m": 30},
 "view": {"azimuth_deg": 0, "pitch_deg": 46, "fov": 34},
 "render": {"vertical_exaggeration": 3.0},
 "segments": S,
 "districts": districts, "walls": walls, "bridges": bridges, "roads": roads, "landmarks": landmarks,
 "fires": fires, "camps": camps, "smoke": smoke, "open_spaces": open_spaces, "labels": labels,
 "youtube": {
  "title": T("Berlin: 800 Years in 15 Minutes (3D Timelapse)", "Berlin: 15 Dakikada 800 Yıl (3D Timelapse)"),
  "description": T(
   "In 1237 a deed names a priest of Cölln, a small trading town on an island in the Spree; in 1244 its twin, Berlin, appears "
   "on the opposite bank. Watch the two towns unite, burn in 1380, become the seat of the Hohenzollerns, lose half their people "
   "in the Thirty Years' War, grow into a star fortress, a royal capital and an industrial giant, merge into Greater Berlin in "
   "1920, fall in ruins in 1945, split by the Wall in 1961 and come together again in 1989–1990: the Berlin Palace, St Nicholas', "
   "the Brandenburg Gate, the Reichstag, the TV tower and Potsdamer Platz, with the year and the population on screen.",
   "1237'de bir belge, Spree'deki bir adada küçük bir ticaret kasabası olan Cölln'den bir rahibi anar; 1244'te ikizi Berlin karşı "
   "kıyıda ortaya çıkar. İki kasabanın birleşmesini, 1380'de yanmasını, Hohenzollernlerin merkezi olmasını, Otuz Yıl Savaşları'nda "
   "halkının yarısını kaybetmesini, yıldız biçimli bir kaleye, kraliyet başkentine ve sanayi devine dönüşmesini, 1920'de Büyük "
   "Berlin'de birleşmesini, 1945'te harabeye dönmesini, 1961'de Duvar'la bölünmesini ve 1989–1990'da yeniden birleşmesini izleyin: "
   "Berlin Sarayı, Aziz Nikolaus, Brandenburg Kapısı, Reichstag, televizyon kulesi ve Potsdamer Platz; yıl ve nüfus ekranda."),
  "tags": ["berlin history", "history of berlin", "berlin wall", "brandenburg gate", "3d timelapse", "city evolution", "how berlin grew",
           "berlin timelapse", "prussia", "cölln", "germany history", "urban history", "berlin geschichte", "cold war berlin"],
  "hashtags": ["#Berlin", "#History", "#Timelapse"],
  "playlist": T("Cities of Europe", "Avrupa Şehirleri"),
  "playlist_desc": T("European cities rebuilt in 3D, from the first stone to the skyline.", "Avrupa şehirleri 3D olarak, ilk taştan siluete."),
  "thumb": {"line1": T("Berlin", "Berlin"), "line2": T("800 YEARS", "800 YIL"), "line3": T("From twin towns to world city", "İkiz kasabalardan dünya şehrine"),
            "extra": "&mood=golden&pitch=30&az=0&cam=52.5160,13.3950,6.0"},
 },
 "sources": json.load(open(os.path.join(HERE, "_sources.json"))),
}
total = sum(s_["seconds"] for s_ in S)
mins = round(total / 60)
city["intro"] = T(f"800 Years in {mins} Minutes", f"{mins} Dakikada 800 Yıl")
city["youtube"]["title"] = T(f"Berlin: 800 Years in {mins} Minutes (3D Timelapse)", f"Berlin: {mins} Dakikada 800 Yıl (3D Timelapse)")
json.dump(city, open(os.path.join(HERE, "city.json"), "w"), ensure_ascii=False, indent=1)
print("segments", len(S), "duration", total, "s =", f"{total // 60}:{total % 60:02d}")
