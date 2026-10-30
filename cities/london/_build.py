"""Builds cities/london/city.json. Every date/figure is from research.md (sources listed there).
Run: python3 cities/london/_build.py"""
import json, os

T = lambda en, tr: {"en": en, "tr": tr}
HERE = os.path.dirname(os.path.abspath(__file__))

# ------------------------------------------------------------------ geography (lat, lon)
LAND_WALL = [(51.5080, -0.0768), (51.5098, -0.0762), (51.5112, -0.0758), (51.5137, -0.0770), (51.5150, -0.0780), (51.5157, -0.0800),
             (51.5161, -0.0817), (51.5166, -0.0845), (51.5172, -0.0885), (51.5181, -0.0925), (51.5185, -0.0955), (51.5168, -0.0965),
             (51.5164, -0.0978), (51.5157, -0.1002), (51.5140, -0.1028), (51.5120, -0.1022)]
RIVER_WALL = [(51.5120, -0.1022), (51.5111, -0.0975), (51.5104, -0.0925), (51.5102, -0.0880), (51.5098, -0.0840), (51.5092, -0.0800),
              (51.5085, -0.0778), (51.5080, -0.0768)]
WALLED_CITY = LAND_WALL + RIVER_WALL[1:-1]
EARLY = [(51.5100, -0.0935), (51.5130, -0.0935), (51.5140, -0.0880), (51.5136, -0.0820), (51.5106, -0.0812), (51.5100, -0.0850), (51.5101, -0.0900)]
SOUTHWARK_R = [(51.5040, -0.0945), (51.5068, -0.0945), (51.5068, -0.0840), (51.5040, -0.0850)]
LUNDENWIC = [(51.5085, -0.1275), (51.5125, -0.1285), (51.5150, -0.1230), (51.5150, -0.1165), (51.5122, -0.1150), (51.5100, -0.1180), (51.5090, -0.1230)]
WESTMINSTER = [(51.4972, -0.1305), (51.5015, -0.1305), (51.5032, -0.1255), (51.5003, -0.1238), (51.4975, -0.1250)]
SOUTHWARK_M = [(51.5030, -0.0960), (51.5072, -0.0975), (51.5072, -0.0820), (51.5040, -0.0830), (51.5020, -0.0900)]
FLEET_STRAND = [(51.5103, -0.1250), (51.5125, -0.1252), (51.5150, -0.1100), (51.5156, -0.1040), (51.5132, -0.1030), (51.5110, -0.1080), (51.5095, -0.1180)]
TUDOR = [(51.4985, -0.1320), (51.5060, -0.1350), (51.5130, -0.1300), (51.5190, -0.1150), (51.5240, -0.1050), (51.5265, -0.0850),
         (51.5250, -0.0720), (51.5180, -0.0620), (51.5100, -0.0560), (51.5075, -0.0600), (51.5050, -0.0700), (51.5010, -0.0750),
         (51.4990, -0.0900), (51.5010, -0.1050), (51.5000, -0.1180)]
FIRE_1666 = [(51.5097, -0.0790), (51.5089, -0.0830), (51.5092, -0.0880), (51.5096, -0.0940), (51.5104, -0.1000), (51.5111, -0.1040),
             (51.5115, -0.1080), (51.5118, -0.1105), (51.5150, -0.1095), (51.5175, -0.1050), (51.5176, -0.1020), (51.5168, -0.0985),
             (51.5175, -0.0950), (51.5170, -0.0900), (51.5160, -0.0870), (51.5140, -0.0850), (51.5130, -0.0830), (51.5115, -0.0810),
             (51.5105, -0.0795)]
WEST_END = [(51.5005, -0.1450), (51.5070, -0.1530), (51.5130, -0.1580), (51.5200, -0.1600), (51.5240, -0.1500), (51.5250, -0.1300),
            (51.5230, -0.1150), (51.5170, -0.1170), (51.5120, -0.1300), (51.5060, -0.1330)]
GEORGIAN_EAST_SOUTH = [(51.5280, -0.0950), (51.5290, -0.0600), (51.5200, -0.0400), (51.5100, -0.0420), (51.4980, -0.0500), (51.4930, -0.0750),
                       (51.4920, -0.1050), (51.4950, -0.1200), (51.5050, -0.1150), (51.5090, -0.0700), (51.5180, -0.0700), (51.5240, -0.0900)]
DOCKLANDS = [(51.5110, -0.0750), (51.5130, -0.0300), (51.5160, 0.0000), (51.5170, 0.0850), (51.5040, 0.0850), (51.4960, 0.0100),
             (51.4850, -0.0100), (51.4830, -0.0450), (51.4920, -0.0650), (51.5040, -0.0750)]
OLD_CORE = [(51.4960, -0.1650), (51.5260, -0.1650), (51.5290, -0.0560), (51.4930, -0.0560)]
O13 = [(51.5650, -0.1400), (51.5650, -0.0800), (51.5450, -0.0300), (51.5300, -0.0050), (51.4950, -0.0050), (51.4750, -0.0200),
       (51.4550, -0.0700), (51.4550, -0.1200), (51.4650, -0.2000), (51.4950, -0.2250), (51.5250, -0.2150), (51.5400, -0.1950)]
O15 = [(51.6000, -0.2500), (51.6100, -0.1700), (51.6000, -0.1000), (51.5900, -0.0100), (51.5600, 0.0600), (51.5300, 0.0900),
       (51.4800, 0.0800), (51.4400, 0.0200), (51.4300, -0.0500), (51.4000, -0.1000), (51.4100, -0.2000), (51.4400, -0.3000),
       (51.4800, -0.3400), (51.5150, -0.3300), (51.5600, -0.3000)]
O16 = [(51.6250, -0.4000), (51.6400, -0.3000), (51.6600, -0.1900), (51.6600, -0.0600), (51.6400, 0.0200), (51.6100, 0.1200),
       (51.5900, 0.2100), (51.5400, 0.2300), (51.4900, 0.1900), (51.4400, 0.1500), (51.3700, 0.1000), (51.3600, 0.0200),
       (51.3400, -0.0700), (51.3500, -0.2000), (51.3750, -0.3000), (51.4200, -0.3800), (51.4600, -0.4500), (51.5200, -0.4700),
       (51.5800, -0.4400)]
POSTWAR_CORE = [(51.5200, -0.1050), (51.5200, -0.0300), (51.5050, -0.0150), (51.5000, -0.0500), (51.5080, -0.0850), (51.5100, -0.1050)]
CANARY = [(51.5070, -0.0280), (51.5070, -0.0120), (51.5030, -0.0120), (51.5030, -0.0280)]
CITY_CLUSTER = [(51.5165, -0.0860), (51.5165, -0.0780), (51.5120, -0.0780), (51.5120, -0.0860)]
STRATFORD = [(51.5470, -0.0250), (51.5470, -0.0050), (51.5360, -0.0050), (51.5360, -0.0250)]
rect = lambda s, w, n, e: [(s, w), (n, w), (n, e), (s, e)]


def L(pts):
    return [[round(a, 5), round(b, 5)] for a, b in pts]


# ------------------------------------------------------------------ timeline
# Population for segments written without one (sources in research.md). Segments not listed here have no
# sourced estimate and show a dash: 47–59 founding years, 190–599 late Roman decline and abandonment, 842–1040.
POP_FILL = {
    (60, 61): 15000,              # "by 60AD ... between ten and twenty thousand" (The History of London)
    (62, 99): [15000, 30000],     # interpolated between the AD 60 estimate and c. 100 (30,000–60,000, Wikipedia)
    (131, 189): 30000,            # mid-2nd century: 20,000–30,000 (City of London) / 45,000–60,000 c. 140 (Wikipedia)
    (600, 841): [5000, 10000],    # ~5,000 by the mid-8th century (The History of London); up to 10,000 late 8th (Project Britain)
    (1666.6, 1666.7): 460000,     # the 1665 figure held through the fire (Britannica)
}


def seg(frm, to, sec, era, city, title=None, sub=None, pop=None, cam=None, chapter=None):
    d = {"from": frm, "to": to, "seconds": sec, "era": era, "city_name": city}
    if title: d["title"] = title; d["sub"] = sub
    if pop is None: pop = POP_FILL.get((frm, to))
    if pop is not None: d["population"] = pop
    if cam: d["camera"] = {"center": [cam[0], cam[1]], "dist_km": cam[2]}
    if chapter: d["chapter"] = chapter
    return d

ROMAN = T("Roman Britain", "Roma Britanyası"); LDN = T("Londinium", "Londinium")
SAX = T("Anglo-Saxon", "Anglo-Sakson"); LON = T("London", "Londra")
S = [
 seg(-50, 43, 12, T("Iron Age", "Demir Çağı"), T("The Thames", "Thames"), T("Before London", "Londra'dan Önce"),
     T("AD 43: Rome invades Britain. Here there is only a tidal river and gravel banks", "MS 43: Roma Britanya'yı işgal eder. Burada henüz yalnızca bir nehir ve çakıl kıyılar var"),
     cam=(51.5098, -0.0890, 3.2)),
 seg(47, 59, 20, ROMAN, LDN, T("Londinium Is Founded", "Londinium Kuruluyor"),
     T("c. AD 47: a Roman port grows where the Thames is bridged, around AD 50", "MS ~47: Thames'in köprülendiği yerde (MS ~50) bir Roma limanı büyür"),
     cam=(51.5105, -0.0880, 3.4), chapter=T("Roman Londinium", "Roma Londinium'u")),
 seg(60, 61, 12, ROMAN, LDN, T("Boudica Burns London", "Boudica Londra'yı Yakıyor"),
     T("AD 60 or 61: the Iceni revolt razes the young town", "MS 60 ya da 61: İceni isyanı genç kasabayı yerle bir eder"), cam=(51.5105, -0.0880, 3.2)),
 seg(62, 99, 18, ROMAN, LDN, T("Rebuilt and Bigger", "Daha Büyük Yeniden"),
     T("By about AD 100 Londinium replaces Colchester as the capital of Britannia", "MS ~100'de Londinium, Colchester'ın yerine Britannia'nın başkenti olur"),
     cam=(51.5115, -0.0890, 3.8)),
 seg(100, 130, 20, ROMAN, LDN, T("Forum and Fort", "Forum ve Kale"),
     T("c. AD 120: one of the largest basilicas north of the Alps, and a fort for the garrison", "MS ~120: Alpler'in kuzeyindeki en büyük bazilikalardan biri ve garnizon için bir kale"),
     pop=[30000, 30000], cam=(51.5120, -0.0900, 4.2)),
 seg(131, 189, 6, ROMAN, LDN, cam=(51.5120, -0.0900, 4.3)),
 seg(190, 225, 18, ROMAN, LDN, T("The London Wall", "Londra Suru"),
     T("c. AD 190–225: a 3 km stone wall, up to 6 m high, encloses 330 acres", "MS ~190–225: 3 km uzunluğunda, 6 m'ye varan taş sur 130 hektarı çevreler"),
     cam=(51.5120, -0.0905, 4.6), chapter=T("The Wall", "Sur")),
 seg(226, 399, 14, ROMAN, LDN, T("The River Wall", "Nehir Suru"),
     T("From the late 3rd century a riverside wall closes the city's open side", "3. yüzyılın sonundan itibaren nehir kıyısına da sur örülür"), cam=(51.5118, -0.0920, 4.6)),
 seg(400, 499, 16, T("Sub-Roman Britain", "Roma sonrası Britanya"), LDN, T("Rome Leaves", "Roma Çekiliyor"),
     T("c. AD 410: Roman rule ends and the walled city is all but abandoned", "MS ~410: Roma yönetimi sona erer, surlarla çevrili şehir neredeyse terk edilir"),
     cam=(51.5115, -0.0950, 5.0), chapter=T("The Empty City", "Boş Şehir")),
 seg(500, 599, 6, SAX, T("Ruins of Londinium", "Londinium harabeleri"), cam=(51.5115, -0.1000, 5.4)),
 seg(600, 841, 18, SAX, T("Lundenwic", "Lundenwic"), T("Lundenwic", "Lundenwic"),
     T("From c. AD 600 a Saxon trading town grows along the Strand, west of the ruins", "MS ~600'den itibaren harabelerin batısında, Strand boyunca bir Sakson ticaret kasabası büyür"),
     cam=(51.5110, -0.1050, 5.6), chapter=T("Saxon Lundenwic", "Sakson Lundenwic'i")),
 seg(842, 885, 16, SAX, T("Lundenwic", "Lundenwic"), T("Viking Raids", "Viking Akınları"),
     T("AD 842 and 851: Viking attacks; by the 880s Lundenwic is abandoned", "MS 842 ve 851: Viking saldırıları; 880'lerde Lundenwic terk edilir"), cam=(51.5110, -0.1050, 5.6)),
 seg(886, 1040, 18, SAX, T("Lundenburh", "Lundenburh"), T("Back Inside the Walls", "Yeniden Surların İçinde"),
     T("AD 886: King Alfred resettles the old Roman walls as Lundenburh", "MS 886: Kral Alfred eski Roma surlarının içini Lundenburh adıyla yeniden iskân eder"),
     cam=(51.5115, -0.0950, 5.0), chapter=T("Lundenburh", "Lundenburh")),
 seg(1041, 1065, 18, SAX, LON, T("Westminster Abbey", "Westminster Manastırı"),
     T("1065: Edward the Confessor's abbey is consecrated upriver at Westminster", "1065: Edward'ın manastırı nehrin yukarısında, Westminster'da kutsanır"),
     pop=[20000, 20000], cam=(51.5060, -0.1050, 6.6)),
 seg(1066, 1100, 18, T("Norman", "Norman"), LON, T("The Conqueror's Tower", "Fatih'in Kulesi"),
     T("1066: William is crowned at Westminster; from the 1070s the White Tower rises", "1066: William Westminster'da taç giyer; 1070'lerden itibaren Beyaz Kule yükselir"),
     pop=[20000, 25000], cam=(51.5085, -0.0950, 5.6), chapter=T("Norman London", "Norman Londrası")),
 seg(1101, 1209, 18, T("Medieval", "Orta Çağ"), LON, T("Old London Bridge", "Eski London Köprüsü"),
     T("1176–1209: a stone bridge of 19 arches, soon lined with houses and shops", "1176–1209: 19 kemerli taş köprü kısa sürede evler ve dükkânlarla dolar"),
     pop=[25000, 40000], cam=(51.5095, -0.0920, 5.2)),
 seg(1210, 1314, 16, T("Medieval", "Orta Çağ"), LON, T("Old St Paul's", "Eski St Paul"),
     T("Completed in 1314; its spire was then the tallest in Europe", "1314'te tamamlanır; kulesi o dönem Avrupa'nın en yükseğidir"),
     pop=[40000, 80000], cam=(51.5095, -0.1000, 6.0)),
 seg(1315, 1347, 6, T("Medieval", "Orta Çağ"), LON, pop=[80000, 80000], cam=(51.5095, -0.1000, 6.2)),
 seg(1348, 1400, 18, T("Medieval", "Orta Çağ"), LON, T("The Black Death", "Kara Ölüm"),
     T("1348: plague strikes; by 1377 London has shrunk to about 40,000 people", "1348: veba gelir; 1377'de Londra yaklaşık 40.000 kişiye düşer"),
     pop=[80000, 40000], cam=(51.5100, -0.1000, 6.4)),
 seg(1401, 1549, 12, T("Tudor", "Tudor"), LON, T("Beyond the Walls", "Surların Ötesine"),
     T("By 1550 about 75,000 people; houses spread out along every road", "1550'de yaklaşık 75.000 kişi; evler her yol boyunca dışarı taşar"),
     pop=[50000, 75000], cam=(51.5095, -0.1000, 7.2), chapter=T("Tudor & Stuart", "Tudor ve Stuart")),
 seg(1550, 1650, 18, T("Tudor & Stuart", "Tudor ve Stuart"), LON, T("A City of 400,000", "400.000'lik Şehir"),
     T("About 200,000 people by 1600, and about 400,000 by 1650", "1600'de yaklaşık 200.000, 1650'de yaklaşık 400.000 kişi"),
     pop=[75000, 400000], cam=(51.5100, -0.1000, 8.5)),
 seg(1651, 1666.5, 14, T("Stuart", "Stuart"), LON, T("The Great Plague", "Büyük Veba"),
     T("1665: 68,596 recorded deaths, probably over 100,000 in reality", "1665: kayıtlı 68.596 ölüm; gerçek sayı muhtemelen 100.000'i aşar"),
     pop=[400000, 460000], cam=(51.5110, -0.0980, 8.0)),
 seg(1666.6, 1666.7, 22, T("Stuart", "Stuart"), LON, T("The Great Fire", "Büyük Yangın"),
     T("2–5 Sept 1666: 13,200 houses, 87 churches and St Paul's burn", "2–5 Eylül 1666: 13.200 ev, 87 kilise ve St Paul yanar"),
     cam=(51.5125, -0.0960, 5.2), chapter=T("The Great Fire", "Büyük Yangın")),
 seg(1667, 1711, 20, T("Stuart", "Stuart"), LON, T("Wren Rebuilds", "Wren Yeniden İnşa Ediyor"),
     T("The City is rebuilt in brick and stone; Wren's St Paul's is declared complete in 1711", "Şehir tuğla ve taştan yeniden kurulur; Wren'in St Paul'ü 1711'de tamamlanır"),
     pop=[400000, 550000], cam=(51.5110, -0.1000, 6.5)),
 seg(1712, 1800, 20, T("Georgian", "Georgian"), LON, T("The West End", "West End"),
     T("Squares and terraces spread west; Westminster Bridge opens in 1750", "Meydanlar ve sıra evler batıya yayılır; Westminster Köprüsü 1750'de açılır"),
     pop=[550000, 1011157], cam=(51.5085, -0.1150, 11.0), chapter=T("Georgian London", "Georgian Londra")),
 seg(1801, 1830, 18, T("Regency", "Regency"), LON, T("The Docks", "Doklar"),
     T("1802: the West India Docks open, the first of London's great enclosed docks", "1802: Londra'nın büyük kapalı doklarının ilki West India Dokları açılır"),
     pop=[1011157, 1729949], cam=(51.5050, -0.0700, 13.0)),
 seg(1831, 1850, 18, T("Victorian", "Viktorya"), LON, T("Railways Arrive", "Demiryolu Geliyor"),
     T("1836: the capital's first steam railway runs from London Bridge on 878 brick arches", "1836: başkentin ilk buharlı treni London Bridge'den 878 tuğla kemer üzerinde ilerler"),
     pop=[1729949, 2286609], cam=(51.5060, -0.0900, 13.5), chapter=T("Victorian London", "Viktorya Londrası")),
 seg(1851, 1852, 14, T("Victorian", "Viktorya"), LON, T("The Crystal Palace", "Kristal Saray"),
     T("1851: a 564 m hall of glass in Hyde Park houses the Great Exhibition", "1851: Hyde Park'taki 564 m'lik cam salon Büyük Sergi'ye ev sahipliği yapar"),
     pop=[2286609, 2300000], cam=(51.5070, -0.1300, 11.0)),
 seg(1853, 1862, 16, T("Victorian", "Viktorya"), LON, T("A New Parliament", "Yeni Parlamento"),
     T("Rebuilt after the fire of 1834; Big Ben is installed in 1859", "1834 yangınından sonra yeniden yapılır; Big Ben 1859'da yerleştirilir"),
     pop=[2300000, 3094391], cam=(51.5040, -0.1150, 11.5)),
 seg(1863, 1880, 16, T("Victorian", "Viktorya"), LON, T("The First Underground", "İlk Metro"),
     T("10 Jan 1863: the Metropolitan Railway opens from Paddington to Farringdon", "10 Ocak 1863: Metropolitan Railway, Paddington–Farringdon arasında açılır"),
     pop=[3094391, 4709960], cam=(51.5070, -0.1100, 14.0)),
 seg(1881, 1894, 16, T("Victorian", "Viktorya"), LON, T("Tower Bridge", "Tower Köprüsü"),
     T("Opened 30 June 1894, its two towers stand 65 m above the Thames", "30 Haziran 1894'te açılır; iki kulesi Thames'in 65 m üzerinde yükselir"),
     pop=[4709960, 5900000], cam=(51.5060, -0.0850, 12.0)),
 seg(1895, 1939, 20, T("Edwardian & Interwar", "Edward ve Savaşlar Arası"), T("Greater London", "Büyük Londra"),
     T("Suburbs Without End", "Bitmeyen Banliyöler"),
     T("Railways and the Tube pull houses outward; about 8.7 million people by 1939", "Tren ve metro evleri dışarı taşır; 1939'da yaklaşık 8,7 milyon kişi"),
     pop=[5900000, 8700000], cam=(51.5000, -0.1200, 30.0), chapter=T("Greater London", "Büyük Londra")),
 seg(1940, 1941.4, 20, T("Second World War", "İkinci Dünya Savaşı"), T("Greater London", "Büyük Londra"), T("The Blitz", "Blitz"),
     T("Sept 1940 – May 1941: bombs burn the docks and much of the City", "Eylül 1940 – Mayıs 1941: bombalar dokları ve City'nin büyük kısmını yakar"),
     pop=8700000, cam=(51.5080, -0.0650, 18.0), chapter=T("The Blitz", "Blitz")),
 seg(1941.5, 1980, 18, T("Post-war", "Savaş Sonrası"), T("Greater London", "Büyük Londra"), T("Rebuilding and Moving Out", "Yeniden İnşa ve Göç"),
     T("Bomb sites become estates; Greater London falls to 6.6 million by 1981", "Bomba alanlarına siteler yükselir; nüfus 1981'de 6,6 milyona iner"),
     pop=[8164416, 6608513], cam=(51.5000, -0.1200, 30.0)),
 seg(1981, 1991, 16, T("Modern", "Modern"), T("Greater London", "Büyük Londra"), T("Docklands Reborn", "Doklar Yeniden Doğuyor"),
     T("The docks close; in 1991 One Canada Square rises 235 m above them", "Doklar kapanır; 1991'de One Canada Square 235 m yükselir"),
     pop=[6608513, 6887280], cam=(51.5050, -0.0400, 15.0), chapter=T("Modern London", "Modern Londra")),
 seg(1992, 2012, 20, T("Modern", "Modern"), T("Greater London", "Büyük Londra"), T("A New Skyline", "Yeni Silüet"),
     T("The London Eye (2000), the Gherkin (2003) and the 310 m Shard (2012)", "London Eye (2000), Gherkin (2003) ve 310 m'lik Shard (2012)"),
     pop=[6887280, 8173941], cam=(51.5070, -0.0950, 12.0)),
 seg(2013, 2021, 16, T("Today", "Bugün"), T("Greater London", "Büyük Londra"), T("A Megacity", "Bir Megakent"),
     T("The 2021 census counts 8.8 million people in Greater London", "2021 sayımı Büyük Londra'da 8,8 milyon kişi sayar"),
     pop=[8173941, 8799728], cam=(51.4980, -0.1200, 40.0)),
 seg(2022, 2026, 24, T("Today", "Bugün"), LON, T("London Today", "Bugünün Londrası"),
     T("Mid-2025: about 9.1 million people, grown from a Roman bridge nearly 2,000 years ago", "2025 ortası: yaklaşık 9,1 milyon kişi; neredeyse 2.000 yıl önceki bir Roma köprüsünden"),
     pop=[8799728, 9122909], cam=(51.5060, -0.0950, 9.5)),
]
# pacing: titled segments x1.34, quiet ones x1.2 → ~14 min, kept under 15:00 (unverified channels can't upload longer)
for s_ in S:
    s_["seconds"] = round(s_["seconds"] * (1.34 if s_.get("title") else 1.2))

# ------------------------------------------------------------------ features
city = {
 "slug": "london", "seed": 47,
 "name": T("London", "Londra"), "intro": T("2,000 Years in 14 Minutes", "14 Dakikada 2.000 Yıl"), "intro_seconds": 4.5,
 "geo": {"bbox": [51.24, -0.63, 51.77, 0.41], "cell_m": 120, "core_bbox": [51.478, -0.215, 51.540, 0.005], "core_cell_m": 30,
         "rivers_keep": ["Thames"], "lakes_from": 1800},
 "view": {"azimuth_deg": 0, "pitch_deg": 46, "fov": 34},
 "render": {"vertical_exaggeration": 3.0},
 "segments": S,
 "districts": [
  {"name": "Early Londinium", "style": "roman", "poly": L(EARLY), "from": 47, "to": 58, "density": 0.6, "grow_from": [51.5100, -0.0870], "grain_m": 50},
  {"name": "Roman Southwark", "style": "roman", "poly": L(SOUTHWARK_R), "from": 50, "to": 70, "density": 0.45, "grow_from": [51.5062, -0.0880], "fade": [300, 460, 0.0]},
  {"name": "Roman Southwark (rebuilt)", "style": "roman", "poly": L(SOUTHWARK_R), "from": 64, "to": 120, "density": 0.45, "grow_from": [51.5062, -0.0880], "fade": [300, 460, 0.0]},
  {"name": "Roman city", "style": "roman", "poly": L(WALLED_CITY), "from": 62, "to": 125, "density": 0.72, "grow_from": [51.5128, -0.0860], "fade": [280, 470, 0.03]},
  {"name": "Lundenwic", "style": "celtic", "poly": L(LUNDENWIC), "from": 600, "to": 780, "density": 0.55, "grow_from": [51.5115, -0.1230], "fade": [842, 880, 0.0]},
  {"name": "Lundenburh", "style": "celtic", "poly": L(WALLED_CITY), "from": 886, "to": 1050, "density": 0.45, "grow_from": [51.5125, -0.0900]},
  {"name": "Westminster", "style": "medieval", "poly": L(WESTMINSTER), "from": 1045, "to": 1300, "density": 0.55, "grow_from": [51.4995, -0.1270]},
  {"name": "Medieval City", "style": "medieval", "poly": L(WALLED_CITY), "from": 1066, "to": 1300, "density": 0.92, "grow_from": [51.5120, -0.0920], "fade": [1348, 1380, 0.55]},
  {"name": "Medieval Southwark", "style": "medieval", "poly": L(SOUTHWARK_M), "from": 1100, "to": 1300, "density": 0.7, "grow_from": [51.5062, -0.0885], "fade": [1348, 1380, 0.6]},
  {"name": "Fleet Street & Strand", "style": "medieval", "poly": L(FLEET_STRAND), "from": 1150, "to": 1400, "density": 0.6, "grow_from": [51.5140, -0.1040]},
  {"name": "Tudor & Stuart London", "style": "medieval", "poly": L(TUDOR), "from": 1480, "to": 1650, "density": 0.78, "grow_from": [51.5120, -0.0920]},
  {"name": "Rebuilt City", "style": "georgian", "poly": L(FIRE_1666), "from": 1667, "to": 1690, "density": 0.92, "grow_from": [51.5125, -0.0950]},
  {"name": "West End", "style": "georgian", "poly": L(WEST_END), "from": 1680, "to": 1800, "density": 0.85, "grow_from": [51.5120, -0.1250]},
  {"name": "Georgian East & South", "style": "georgian", "poly": L(GEORGIAN_EAST_SOUTH), "from": 1700, "to": 1800, "density": 0.7, "grow_from": [51.5100, -0.0800]},
  {"name": "Docklands", "style": "industrial", "poly": L(DOCKLANDS), "from": 1802, "to": 1885, "density": 0.6, "grow_from": [51.5080, -0.0600]},
  {"name": "Victorian London", "style": "victorian", "poly": L(O13), "holes": [L(OLD_CORE), L(DOCKLANDS)], "from": 1820, "to": 1895, "density": 0.78,
   "grain_m": 75, "grow_from": [51.5100, -0.1100]},
  {"name": "Interwar suburbs", "style": "suburb", "poly": L(O15), "holes": [L(O13), L(DOCKLANDS)], "from": 1895, "to": 1939, "density": 0.85,
   "grain_m": 190, "grow_from": [51.5050, -0.1100]},
  {"name": "Outer suburbs", "style": "suburb", "poly": L(O16), "holes": [L(O15)], "from": 1925, "to": 1975, "density": 0.75,
   "grain_m": 240, "grow_from": [51.5050, -0.1100]},
  {"name": "Post-war rebuilding", "style": "modern", "poly": L(POSTWAR_CORE), "from": 1948, "to": 1980, "density": 0.55, "grain_m": 100, "grow_from": [51.5150, -0.0700]},
  {"name": "Canary Wharf", "style": "highrise", "poly": L(CANARY), "from": 1988, "to": 2015, "density": 0.8, "grain_m": 110, "grow_from": [51.5050, -0.0196]},
  {"name": "City towers", "style": "highrise", "poly": L(CITY_CLUSTER), "from": 1995, "to": 2020, "density": 0.55, "grain_m": 100, "grow_from": [51.5140, -0.0820]},
  {"name": "Stratford", "style": "modern", "poly": L(STRATFORD), "from": 2005, "to": 2020, "density": 0.7, "grain_m": 110, "grow_from": [51.5420, -0.0100]},
 ],
 "walls": [
  {"name": "Roman land wall", "path": L(LAND_WALL), "built": 190, "removed": 1765, "height": "mid", "towers_m": 160, "draw_s": 3.0},
  {"name": "Roman riverside wall", "path": L(RIVER_WALL), "built": 255, "removed": 700, "height": "low", "towers_m": 0, "draw_s": 2.0},
 ],
 "bridges": [
  {"name": "Roman bridge", "path": [[51.5097, -0.0868], [51.5063, -0.0878]], "built": 50, "removed": 1176, "style": "wood", "width_m": 12},
  {"name": "Old London Bridge", "path": [[51.5097, -0.0868], [51.5063, -0.0878]], "built": 1180, "removed": 1831, "style": "stone", "width_m": 24},
  {"name": "London Bridge (1831)", "path": [[51.5096, -0.0879], [51.5062, -0.0889]], "built": 1831, "style": "stone", "width_m": 22},
  {"name": "Westminster Bridge", "path": [[51.50086, -0.12457], [51.5012, -0.1194]], "built": 1750, "style": "stone", "width_m": 18},
  {"name": "Blackfriars Bridge", "path": [[51.5115, -0.104], [51.5082, -0.1047]], "built": 1769, "style": "stone", "width_m": 20},
  {"name": "Vauxhall Bridge", "path": [[51.48927, -0.12848], [51.4869, -0.1252]], "built": 1816, "style": "iron", "width_m": 18},
  {"name": "Waterloo Bridge", "path": [[51.51059, -0.11704], [51.5064, -0.115]], "built": 1817, "style": "stone", "width_m": 20},
  {"name": "Southwark Bridge", "path": [[51.51039, -0.09412], [51.5068, -0.0946]], "built": 1819, "style": "iron", "width_m": 16},
  {"name": "Lambeth Bridge", "path": [[51.49458, -0.12548], [51.494, -0.1197]], "built": 1862, "style": "iron", "width_m": 16},
  {"name": "Hungerford Bridge", "path": [[51.50703, -0.12255], [51.50474, -0.1187]], "built": 1864, "style": "iron", "width_m": 14},
  {"name": "Cannon Street Railway Bridge", "path": [[51.51, -0.0912], [51.5069, -0.0917]], "built": 1866, "style": "iron", "width_m": 18},
  {"name": "Tower Bridge", "path": [[51.50718, -0.07472], [51.50408, -0.07588]], "built": 1894, "style": "tower", "width_m": 22},
  {"name": "Millennium Bridge", "path": [[51.51111, -0.09835], [51.5071, -0.0988]], "built": 2000, "style": "modern", "width_m": 6},
 ],
 "roads": [
  {"name": "Road north (Ermine Street)", "path": L([(51.5161, -0.0817), (51.5260, -0.0790), (51.5450, -0.0760), (51.5800, -0.0720), (51.6400, -0.0650)]), "from": 55, "kind": "roman", "width_m": 18},
  {"name": "Road west (Watling Street)", "path": L([(51.5157, -0.1002), (51.5172, -0.1100), (51.5160, -0.1400), (51.5135, -0.1590), (51.5300, -0.1800), (51.5700, -0.2200)]), "from": 55, "kind": "roman", "width_m": 18},
  {"name": "Road east", "path": L([(51.5137, -0.0770), (51.5170, -0.0600), (51.5250, -0.0300), (51.5420, 0.0100)]), "from": 55, "kind": "roman", "width_m": 18},
  {"name": "Road south (Stane Street)", "path": L([(51.5063, -0.0878), (51.4990, -0.0930), (51.4800, -0.1100), (51.4600, -0.1350)]), "from": 55, "kind": "roman", "width_m": 18},
  {"name": "Road south-east (Watling Street)", "path": L([(51.5063, -0.0878), (51.4950, -0.0700), (51.4800, -0.0450), (51.4700, -0.0200)]), "from": 55, "kind": "roman", "width_m": 18},
  {"name": "London & Greenwich Railway", "path": L([(51.5050, -0.0860), (51.4990, -0.0700), (51.4880, -0.0400), (51.4810, -0.0230), (51.4785, -0.0125)]), "from": 1836, "kind": "rail", "width_m": 22},
 ],
 "landmarks": [
  {"type": "amphitheatre", "name": T("Amphitheatre", "Amfitiyatro"), "at": [51.5156, -0.0918], "built": 70, "removed": 420, "size_m": [100, 85, 18]},
  {"type": "forum", "name": T("Forum", "Forum"), "at": [51.5128, -0.0838], "built": 75, "removed": 300, "size_m": [160, 160], "colors": {"column": False}},
  {"type": "box", "name": T("Basilica", "Bazilika"), "at": [51.5134, -0.0838], "built": 115, "removed": 300, "size_m": [150, 45, 26], "colors": {"wall": "#ece2cc", "roof": "#b4583b"}},
  {"type": "fort", "name": T("Cripplegate fort", "Cripplegate kalesi"), "at": [51.5175, -0.0937], "built": 120, "removed": 200, "size_m": [240, 220, 8]},
  {"type": "church", "name": T("First St Paul's", "İlk St Paul"), "at": [51.5138, -0.0990], "built": 604, "removed": 1087, "size_m": [40, 16, 12]},
  {"type": "church", "name": T("Edward's abbey", "Edward'ın manastırı"), "at": [51.4994, -0.1275], "built": 1050, "removed": 1245, "size_m": [90, 28, 20]},
  {"type": "castle", "name": T("Tower of London", "Londra Kulesi"), "at": [51.5081, -0.0759], "built": 1078, "rise_s": 3, "size_m": [180, 170, 18], "colors": {"keep": "#ece9e0"}},
  {"type": "palace", "name": T("Palace of Westminster (old)", "Eski Westminster Sarayı"), "at": [51.4997, -0.1253], "built": 1097, "removed": 1834.8, "size_m": [110, 80, 18]},
  {"type": "cathedral", "name": T("Old St Paul's", "Eski St Paul"), "at": [51.5138, -0.0990], "built": 1100, "removed": 1666.65, "rise_s": 4, "size_m": [178, 40, 30], "scale": 1.25},
  {"type": "cathedral", "name": T("Westminster Abbey", "Westminster Manastırı"), "at": [51.4994, -0.1275], "built": 1245, "rise_s": 3, "size_m": [150, 40, 32], "colors": {"spire": False}},
  {"type": "column", "name": T("The Monument", "Anıt"), "at": [51.5101, -0.0859], "built": 1677, "size_m": [8, 8, 61]},
  {"type": "domechurch", "name": T("St Paul's Cathedral", "St Paul Katedrali"), "at": [51.5138, -0.0984], "built": 1697, "rise_s": 4, "size_m": [150, 75, 28], "scale": 1.3,
   "colors": {"wall": "#ddd8ca", "dome": "#9aa4a8", "lantern": True, "towers": True}},
  {"type": "palace", "name": T("Buckingham Palace", "Buckingham Sarayı"), "at": [51.5014, -0.1419], "built": 1837, "size_m": [120, 100, 24], "colors": {"wall": "#e8e3d6", "roof": "#8f949a"}},
  {"type": "box", "name": T("Crystal Palace", "Kristal Saray"), "at": [51.5030, -0.1670], "built": 1850.9, "removed": 1852, "rise_s": 2, "size_m": [564, 124, 33], "colors": {"wall": "#cfe3ea"}},
  {"type": "parliament", "name": T("Houses of Parliament", "Parlamento Binası"), "at": [51.4995, -0.1248], "built": 1845, "rise_s": 6, "rot_deg": 270, "size_m": [265, 70, 26]},
  {"type": "tower", "name": T("BT Tower", "BT Kulesi"), "at": [51.5215, -0.1389], "built": 1964, "size_m": [20, 20, 177], "colors": {"wall": "#c9ced2", "roof": "#9aa1a6"}},
  {"type": "skyscraper", "name": T("One Canada Square", "One Canada Square"), "at": [51.5050, -0.0196], "built": 1988, "rise_s": 6, "size_m": [50, 50, 235], "colors": {"wall": "#b8c3cb"}},
  {"type": "dome_arena", "name": T("Millennium Dome", "Millennium Dome"), "at": [51.5030, 0.0032], "built": 1999, "size_m": [180]},
  {"type": "wheel", "name": T("London Eye", "London Eye"), "at": [51.5033, -0.1196], "built": 2000, "size_m": [65], "rot_deg": 30},
  {"type": "tower", "name": T("The Gherkin", "Gherkin"), "at": [51.5145, -0.0803], "built": 2003, "size_m": [50, 50, 170], "colors": {"wall": "#7f97a6", "roof": "#6a8292"}},
  {"type": "skyscraper", "name": T("Heron Tower", "Heron Kulesi"), "at": [51.5162, -0.0806], "built": 2010, "size_m": [45, 45, 230], "colors": {"wall": "#9fb0bc"}},
  {"type": "spire_tower", "name": T("The Shard", "Shard"), "at": [51.5045, -0.0865], "built": 2010, "rise_s": 5, "size_m": [60, 60, 310]},
  {"type": "stadium", "name": T("Olympic Stadium", "Olimpiyat Stadı"), "at": [51.5386, -0.0166], "built": 2011, "size_m": [300, 250, 45]},
  {"type": "skyscraper", "name": T("Leadenhall Building", "Leadenhall Binası"), "at": [51.5137, -0.0822], "built": 2014, "size_m": [45, 45, 225], "colors": {"wall": "#a9b8c2"}},
  {"type": "skyscraper", "name": T("20 Fenchurch Street", "20 Fenchurch Street"), "at": [51.5113, -0.0835], "built": 2014, "size_m": [55, 50, 160], "colors": {"wall": "#8ea3b1"}},
 ],
 "fires": [
  {"year": 60.5, "poly": L(EARLY + [(51.5090, -0.0920)]), "duration_s": 6, "plumes": 5},
  {"year": 60.6, "poly": L(SOUTHWARK_R), "duration_s": 5, "plumes": 2},
  {"year": 1666.62, "poly": L(FIRE_1666), "duration_s": 14, "plumes": 9, "plume_scale": 1.8},
  {"year": 1940.68, "poly": L([(51.5100, -0.0700), (51.5110, -0.0300), (51.4950, -0.0200), (51.4920, -0.0450), (51.5000, -0.0650)]), "duration_s": 8, "plumes": 8, "plume_scale": 4.0},
  {"year": 1940.99, "poly": L([(51.5175, -0.1000), (51.5175, -0.0880), (51.5135, -0.0880), (51.5130, -0.1000)]), "duration_s": 6, "plumes": 5, "plume_scale": 3.0},
 ],
 "smoke": [
  {"at": [51.5118, -0.1225], "from": 842, "to": 860, "scale": 1.3},
  {"at": [51.5130, -0.1180], "from": 851, "to": 870, "scale": 1.3},
 ],
 "timed_water": [
  {"name": "West India Dock North", "poly": L(rect(51.5058, -0.0275, 51.5070, -0.0100)), "from": 1802},
  {"name": "West India Dock Middle", "poly": L(rect(51.5030, -0.0260, 51.5040, -0.0110)), "from": 1802},
  {"name": "West India Dock South", "poly": L(rect(51.5005, -0.0260, 51.5016, -0.0080)), "from": 1866},
  {"name": "London Docks", "poly": L(rect(51.5060, -0.0670, 51.5085, -0.0560)), "from": 1805, "to": 1970},
  {"name": "Surrey Commercial Docks", "poly": L(rect(51.4950, -0.0480, 51.5010, -0.0340)), "from": 1807, "to": 1970},
  {"name": "St Katharine Docks", "poly": L(rect(51.5068, -0.0730, 51.5085, -0.0700)), "from": 1828},
  {"name": "Royal Victoria Dock", "poly": L(rect(51.5070, 0.0130, 51.5090, 0.0420)), "from": 1855},
  {"name": "Millwall Dock", "poly": L(rect(51.4950, -0.0260, 51.4995, -0.0150)), "from": 1868},
  {"name": "Royal Albert Dock", "poly": L(rect(51.5065, 0.0480, 51.5080, 0.0800)), "from": 1880},
  {"name": "King George V Dock", "poly": L(rect(51.5000, 0.0480, 51.5018, 0.0720)), "from": 1921},
 ],
 "open_spaces": [
  {"name": "Hyde Park & Kensington Gardens", "poly": L([(51.5130, -0.1590), (51.5105, -0.1880), (51.5020, -0.1880), (51.5030, -0.1730), (51.5020, -0.1520), (51.5065, -0.1525)])},
  {"name": "Green Park & St James's Park", "poly": L([(51.5065, -0.1500), (51.5045, -0.1390), (51.5040, -0.1290), (51.5015, -0.1290), (51.5010, -0.1360), (51.5005, -0.1440), (51.5025, -0.1500)])},
  {"name": "Regent's Park", "poly": L([(51.5375, -0.1600), (51.5370, -0.1460), (51.5250, -0.1450), (51.5225, -0.1530), (51.5250, -0.1640), (51.5330, -0.1660)])},
  {"name": "Hampstead Heath", "poly": L([(51.5720, -0.1800), (51.5710, -0.1500), (51.5560, -0.1480), (51.5580, -0.1720)])},
  {"name": "Victoria Park", "poly": L([(51.5410, -0.0500), (51.5390, -0.0300), (51.5320, -0.0360), (51.5355, -0.0510)])},
  {"name": "Greenwich Park", "poly": L([(51.4800, -0.0060), (51.4790, 0.0060), (51.4720, 0.0060), (51.4730, -0.0050)])},
  {"name": "Blackheath", "poly": L([(51.4740, -0.0120), (51.4720, 0.0150), (51.4630, 0.0130), (51.4650, -0.0100)])},
  {"name": "Battersea Park", "poly": L([(51.4825, -0.1700), (51.4825, -0.1520), (51.4770, -0.1500), (51.4770, -0.1680)])},
  {"name": "Clapham Common", "poly": L([(51.4630, -0.1560), (51.4600, -0.1380), (51.4540, -0.1430), (51.4560, -0.1600)])},
  {"name": "Richmond Park", "poly": L([(51.4560, -0.2950), (51.4530, -0.2550), (51.4300, -0.2400), (51.4160, -0.2700), (51.4250, -0.3050), (51.4450, -0.3100)])},
  {"name": "Wimbledon Common", "poly": L([(51.4400, -0.2400), (51.4380, -0.2150), (51.4200, -0.2200), (51.4220, -0.2450)])},
  {"name": "Lea Valley", "poly": L([(51.6200, -0.0450), (51.6200, -0.0250), (51.5450, -0.0150), (51.5450, -0.0380)])},
  {"name": "Wormwood Scrubs", "poly": L(rect(51.5140, -0.2450, 51.5200, -0.2300))},
  {"name": "Heathrow", "poly": L(rect(51.4620, -0.4900, 51.4800, -0.4200))},
 ],
 "labels": [
  {"text": T("RIVER THAMES", "THAMES NEHRİ"), "at": [51.5077, -0.0990], "kind": "water", "to": 1700},
  {"text": T("RIVER THAMES", "THAMES NEHRİ"), "at": [51.4870, -0.1650], "kind": "water", "from": 1700},
  {"text": T("Forum", "Forum"), "at": [51.5128, -0.0838], "from": 80, "to": 300, "lift_m": 40},
  {"text": T("Amphitheatre", "Amfitiyatro"), "at": [51.5156, -0.0918], "from": 75, "to": 300, "lift_m": 30},
  {"text": T("Southwark", "Southwark"), "at": [51.5050, -0.0900], "kind": "region", "from": 55, "to": 400},
  {"text": T("Lundenwic", "Lundenwic"), "at": [51.5120, -0.1225], "from": 620, "to": 880, "lift_m": 30},
  {"text": T("Westminster", "Westminster"), "at": [51.4994, -0.1275], "from": 1050, "to": 1750, "lift_m": 60},
  {"text": T("Tower of London", "Londra Kulesi"), "at": [51.5081, -0.0759], "from": 1080, "to": 1700, "lift_m": 50},
  {"text": T("London Bridge", "London Köprüsü"), "at": [51.5080, -0.0873], "from": 1209, "to": 1700, "lift_m": 20},
  {"text": T("St Paul's", "St Paul"), "at": [51.5138, -0.0990], "from": 1300, "to": 1666.6, "lift_m": 120},
  {"text": T("Pudding Lane", "Pudding Lane"), "at": [51.5103, -0.0857], "from": 1666.55, "to": 1666.7, "lift_m": 20},
  {"text": T("St Paul's Cathedral", "St Paul Katedrali"), "at": [51.5138, -0.0984], "from": 1705, "to": 1800, "lift_m": 140},
  {"text": T("WEST END", "WEST END"), "at": [51.5140, -0.1450], "kind": "region", "from": 1720, "to": 1830},
  {"text": T("EAST END", "EAST END"), "at": [51.5190, -0.0550], "kind": "region", "from": 1790, "to": 1900},
  {"text": T("Docklands", "Doklar"), "at": [51.5040, -0.0200], "from": 1803, "to": 1850, "lift_m": 30},
  {"text": T("Crystal Palace", "Kristal Saray"), "at": [51.5030, -0.1670], "from": 1851, "to": 1852, "lift_m": 60},
  {"text": T("Houses of Parliament", "Parlamento"), "at": [51.4995, -0.1248], "from": 1855, "to": 1880, "lift_m": 110},
  {"text": T("Tower Bridge", "Tower Köprüsü"), "at": [51.5056, -0.0753], "from": 1894, "to": 1900, "lift_m": 80},
  {"text": T("CITY OF LONDON", "LONDRA CITY"), "at": [51.5150, -0.0920], "kind": "region", "from": 1940, "to": 1942},
  {"text": T("Canary Wharf", "Canary Wharf"), "at": [51.5050, -0.0196], "from": 1990, "to": 2012, "lift_m": 260},
  {"text": T("The Shard", "Shard"), "at": [51.5045, -0.0865], "from": 2012, "lift_m": 330},
  {"text": T("St Paul's", "St Paul"), "at": [51.5138, -0.0984], "from": 2022, "lift_m": 140},
  {"text": T("Westminster", "Westminster"), "at": [51.4995, -0.1260], "from": 2022, "lift_m": 120},
 ],
 "youtube": {
  "title": T("London: 2,000 Years in 14 Minutes (3D Timelapse)", "Londra: 14 Dakikada 2.000 Yıl (3D Timelapse)"),
  "description": T(
   "Around AD 47 the Romans built a port where the Thames could be bridged. Watch London grow from a timber trading town into a city of 9 million: "
   "Boudica's fire, the Roman wall, Saxon Lundenwic, the Tower, Old London Bridge, the Black Death, the Great Fire of 1666, the docks, "
   "the railways, the Blitz and today's skyline, with the year and the population on screen the whole way.",
   "MS 47 civarında Romalılar, Thames'in köprülenebildiği yerde bir liman kurdu. Londra'nın ahşap bir ticaret kasabasından 9 milyonluk bir şehre "
   "büyüyüşünü izleyin: Boudica yangını, Roma suru, Sakson Lundenwic'i, Londra Kulesi, Eski London Köprüsü, Kara Ölüm, 1666 Büyük Yangını, doklar, "
   "demiryolları, Blitz ve bugünün silueti; yıl ve nüfus baştan sona ekranda."),
  "tags": ["london history", "history of london", "londinium", "roman london", "great fire of london", "3d timelapse", "city evolution",
           "how london grew", "london timelapse", "urban history", "british history", "the blitz", "old london bridge"],
  "hashtags": ["#London", "#History", "#Timelapse"],
  "playlist": T("Cities of Europe", "Avrupa Şehirleri"),
  "playlist_desc": T("European cities rebuilt in 3D, from the first stone to the skyline.", "Avrupa şehirleri 3D olarak, ilk taştan siluete."),
  "thumb": {"line1": T("London", "Londra"), "line2": T("2,000 YEARS", "2.000 YIL"), "line3": T("From a Roman bridge to a megacity", "Bir Roma köprüsünden megakente"),
            "extra": "&mood=golden&pitch=30&az=-6&cam=51.5065,-0.0960,7.5"},
 },
 "sources": [
  {"title": "Londinium (Wikipedia mirror)", "url": "https://cavac.at/cavacopedia/Londinium"},
  {"title": "The Rise and Fall of Roman London — History Hit", "url": "https://www.historyhit.com/the-rise-and-fall-of-roman-london/"},
  {"title": "London Wall — Wikipedia", "url": "https://en.wikipedia.org/wiki/London_Wall"},
  {"title": "Anglo-Saxon London — Wikipedia", "url": "https://en.wikipedia.org/wiki/Anglo-Saxon_London"},
  {"title": "Lundenwic: the other medieval London — London Museum", "url": "https://www.londonmuseum.org.uk/collections/london-stories/lundenwic-other-medieval-london/"},
  {"title": "Norman and medieval London — Wikipedia", "url": "https://en.wikipedia.org/wiki/Norman_and_medieval_London"},
  {"title": "London, growth of — Encyclopedia.com", "url": "https://www.encyclopedia.com/history/encyclopedias-almanacs-transcripts-and-maps/london-growth"},
  {"title": "Old London Bridge — Britannica", "url": "https://www.britannica.com/topic/Old-London-Bridge"},
  {"title": "A history of St Paul's Cathedral — London Museum", "url": "https://londonmuseum.org.uk/collections/london-stories/a-history-of-st-pauls-cathedral"},
  {"title": "Great Plague of London — Britannica", "url": "https://www.britannica.com/event/Great-Plague-of-London"},
  {"title": "Great Fire of London — New World Encyclopedia", "url": "https://www.newworldencyclopedia.org/entry/Great_Fire_of_London"},
  {"title": "List of bridges in London — Wikipedia", "url": "https://en.wikipedia.org/wiki/List_of_bridges_in_London"},
  {"title": "West India Docks — Wikipedia", "url": "https://en.wikipedia.org/wiki/West_India_Docks"},
  {"title": "History of London Docklands — Canal & River Trust", "url": "https://canalrivertrust.org.uk/canals-and-rivers/london-docklands/history-of-london-docklands"},
  {"title": "London and Greenwich Railway — Wikipedia", "url": "https://en.wikipedia.org/wiki/London_and_Greenwich_Railway"},
  {"title": "Palace of Westminster key dates — UK Parliament", "url": "https://webtest.parliament.uk/about/living-heritage/building/palace/architecture/key-dates-fire1834-to-present"},
  {"title": "The world's first Underground — London Transport Museum", "url": "https://ltmuseum.co.uk/visit/museum-guide/worlds-first-underground"},
  {"title": "Tower Bridge — Wikipedia", "url": "https://en.wikipedia.org/wiki/Tower_Bridge"},
  {"title": "Demography of London — Wikipedia", "url": "https://ipfs.ssi.eecc.de/ipns/en.wikipedia-on-ipfs.org/wiki/Demography_of_London"},
  {"title": "The rise and fall of the first Roman town of Londinium — The History of London", "url": "https://www.thehistoryoflondon.co.uk/the-rise-and-fall-of-the-first-roman-town-of-londinium/"},
  {"title": "Roman London information sheet — City of London", "url": "https://www.cityoflondon.gov.uk/assets/Things-to-do/roman-amphitheatre-roman-london.pdf"},
  {"title": "The early Saxon settlers and the town of Lundenwic — The History of London", "url": "https://thehistoryoflondon.co.uk/the-early-saxon-settlers-and-the-town-of-lundenwic/2"},
  {"title": "Saxons and Vikings in London — Project Britain", "url": "https://projectbritain.com/london/history/saxonsandvikings.html"},
  {"title": "The Blitz hits London — History", "url": "https://www.history.co.uk/history-of-london/ww2-blitz-hits-london"},
  {"title": "One Canada Square — Wikipedia", "url": "https://en.wikipedia.org/wiki/One_Canada_Square"},
  {"title": "Tallest buildings in the UK — Designing Buildings", "url": "https://www.designingbuildings.co.uk/wiki/Tallest_buildings_in_the_UK"},
  {"title": "London: population — City Population", "url": "https://citypopulation.de/en/uk/london/"},
 ],
}
total = sum(s_["seconds"] for s_ in S)
mins = round(total / 60)
city["intro"] = T(f"2,000 Years in {mins} Minutes", f"{mins} Dakikada 2.000 Yıl")
city["youtube"]["title"] = T(f"London: 2,000 Years in {mins} Minutes (3D Timelapse)", f"Londra: {mins} Dakikada 2.000 Yıl (3D Timelapse)")
json.dump(city, open(os.path.join(HERE, "city.json"), "w"), ensure_ascii=False, indent=1)
print("segments", len(S), "duration", total, "s =", f"{total // 60}:{total % 60:02d}")
