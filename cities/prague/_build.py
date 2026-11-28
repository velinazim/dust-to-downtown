"""Builds cities/prague/city.json. Every date/figure is from research.md (sources listed there).
Run: python3 cities/prague/_build.py
Footprints of growth are simplified reconstructions (marked ≈); landmark points are Wikipedia infobox coordinates where
research.md says so, otherwise ≈ placements next to a sourced point."""
import json, math, os

T = lambda en, tr: {"en": en, "tr": tr}
HERE = os.path.dirname(os.path.abspath(__file__))
LAT0 = 50.08
KX, KY = 111.32 * math.cos(math.radians(LAT0)), 110.574


def L(pts):
    return [[round(a, 5), round(b, 5)] for a, b in pts]


def oval(c, a_m, b_m, rot_deg=0, n=16):
    out = []
    for i in range(n):
        t = 2 * math.pi * i / n; x, y = a_m * math.cos(t), b_m * math.sin(t)
        r = math.radians(rot_deg); x, y = x * math.cos(r) - y * math.sin(r), x * math.sin(r) + y * math.cos(r)
        out.append((c[0] + y / 1000 / KY, c[1] + x / 1000 / KX))
    return out


def strip(a, b, w_m):
    """rectangle w_m wide along the line a→b"""
    dx, dy = (b[1] - a[1]) * KX, (b[0] - a[0]) * KY; n = math.hypot(dx, dy); ox, oy = -dy / n * w_m / 2000, dx / n * w_m / 2000
    return [(a[0] + oy / KY, a[1] + ox / KX), (b[0] + oy / KY, b[1] + ox / KX), (b[0] - oy / KY, b[1] - ox / KX), (a[0] - oy / KY, a[1] - ox / KX)]


# ------------------------------------------------------------------ sourced points (research.md "Coordinates")
CASTLE = (50.0905, 14.4000)        # WP Prague Castle 50.09, 14.40 (≈ refined to the castle courtyards)
VITUS = (50.0909, 14.4006)         # ≈ inside the castle (cathedral stands in the third courtyard)
MALA = (50.08806, 14.40389)        # WP Malá Strana
STARE = (50.08750, 14.42056)       # WP Old Town (≈ Old Town Square)
TOWNHALL = (50.0870, 14.4207)      # ≈ south-west corner of Old Town Square
POWDER = (50.0872, 14.4278)        # WP Powder Tower
JOSEFOV = (50.08972, 14.41861)     # WP Josefov
SYNAG = (50.0900, 14.4186)         # Old New Synagogue 50°05′24″N 14°25′07″E
BRIDGE = (50.08639, 14.41194)      # WP Charles Bridge (centre)
NOVE = (50.07667, 14.42639)        # WP New Town
WENC = (50.08139, 14.42750)        # WP Wenceslas Square
MUSEUM = (50.078831, 14.430797)    # WP National Museum
CHARLESQ = (50.0757, 14.4195)      # ≈ Charles Square (no infobox point; New Town page)
NEWHALL = (50.0773, 14.4197)       # ≈ New Town Hall, north end of Charles Square
HAYMKT = (50.0855, 14.4305)        # ≈ Senovážné náměstí
VYSEHRAD = (50.06417, 14.41944)    # WP Vyšehrad
PETRIN = (50.08361, 14.39528)      # WP Petřín
PTOWER = (50.08354, 14.39505)      # WP Petřín Lookout Tower
THEATRE = (50.08111, 14.41361)     # WP National Theatre
STATION = (50.08806, 14.43306)     # WP Masaryk station
TVTOWER = (50.08083, 14.45139)     # WP Žižkov Television Tower
VITKOV = (50.0888, 14.4514)        # WP Battle of Vítkov Hill
ZIZKOV = (50.08528, 14.47139)      # WP Žižkov
VINO = (50.07556, 14.44583)        # WP Vinohrady
NUSLE_BR = (50.065844, 14.430483)  # WP Nusle Bridge
DANCING = (50.07556, 14.41417)     # WP Dancing House
KARLIN = (50.0925, 14.4500)        # ≈ Karlín, east of Florenc along the river
SMICHOV = (50.0705, 14.4040)       # ≈ Smíchov, west bank south of Malá Strana
HOLES_ = (50.1030, 14.4380)        # ≈ Holešovice, inside the river bend
LIBEN = (50.1060, 14.4750)         # ≈ Libeň
DEJVICE = (50.1010, 14.3930)       # ≈ Dejvice
HRADCANY = (50.0890, 14.3930)      # ≈ Hradčany town, west of the castle
JIZNI = (50.0300, 14.5100)         # ≈ Jižní Město (Chodov/Háje)
SEVERNI = (50.1270, 14.4800)       # ≈ Severní Město (Prosek/Ďáblice)
JZM = (50.0470, 14.3300)           # ≈ Jihozápadní Město (Stodůlky)
PETRINY = (50.0880, 14.3520)       # ≈ Petřiny estate
PANKRAC = (50.0510, 14.4390)       # ≈ Pankrác estate


# ------------------------------------------------------------------ timeline
def seg(frm, to, sec, era, city, title=None, sub=None, pop=None, cam=None, chapter=None):
    d = {"from": frm, "to": to, "seconds": sec, "era": era, "city_name": city}
    if title: d["title"] = title; d["sub"] = sub
    if pop is not None: d["population"] = pop
    if cam: d["camera"] = {"center": [cam[0], cam[1]], "dist_km": cam[2]}
    if chapter: d["chapter"] = chapter
    return d


PRE = T("Přemyslid Bohemia", "Přemysl Bohemyası"); MED = T("Medieval Prague", "Orta Çağ Prag'ı")
GOLD = T("Age of Charles IV", "IV. Karl Çağı"); HUS = T("Hussite Wars", "Husçu Savaşları")
HAB = T("Habsburg Prague", "Habsburg Prag'ı"); BAR = T("Baroque Prague", "Barok Prag")
IND = T("Industrial Age", "Sanayi Çağı"); CZ = T("Czechoslovakia", "Çekoslovakya")
WAR = T("Occupation & War", "İşgal ve Savaş"); COM = T("Communist Era", "Komünist Dönem")
TODAY = T("Today", "Bugün")
PR = T("Prague", "Prag")

# sourced anchors (year, people) — research.md; log-interpolated between them. 1346 and 1483: McEvedy band 15–22k
# (midpoint). From 1880 the series includes the suburbs (Timeline of Prague "metro"), so the 1922 merger is no jump.
ANCH = [(1346, 18500), (1483, 18500), (1618, 60000), (1650, 20000), (1705, 40000), (1771, 80000), (1837, 100000),
        (1880, 293822), (1896, 368490), (1906, 460849), (1922, 676000), (1930, 848823), (1938, 1000000),
        (1974, 1095615), (1985, 1190576), (2001, 1169106), (2011, 1268796), (2021, 1301432), (2024, 1397880),
        (2026, 1409528)]


def P(y):
    for (y0, p0), (y1, p1) in zip(ANCH, ANCH[1:]):
        if y0 <= y <= y1:
            u = (y - y0) / (y1 - y0); v = math.exp(math.log(p0) + (math.log(p1) - math.log(p0)) * u)
            return int(round(v, -2 if v < 100000 else -3))
    raise ValueError(y)


PI = lambda a, b: [P(a), P(b)]
S = [
 seg(870, 899, 12, PRE, PR, T("Prague Castle", "Prag Kalesi"),
     T("Around 880: Prince Bořivoj founds a castle on the hill above the Vltava",
       "880 civarı: Prens Bořivoj, Vltava'nın üstündeki tepede bir kale kurar"),
     cam=(50.0890, 14.4030, 2.6), chapter=T("Přemyslid Prague", "Přemysl Prag'ı")),
 seg(900, 934, 11, PRE, PR, T("The Rotunda of St Vitus", "Aziz Vitus Rotondası"),
     T("Around 925: Prince Wenceslas founds a round church of St Vitus inside the castle",
       "925 civarı: Prens Wenceslas, kalenin içinde yuvarlak bir Aziz Vitus kilisesi kurar"),
     cam=(50.0900, 14.4010, 2.2)),
 seg(935, 972, 6, PRE, PR, cam=(50.0860, 14.4080, 3.4)),
 seg(973, 1059, 11, PRE, PR, T("A Bishop for Prague", "Prag'a Bir Piskopos"),
     T("973: Prague becomes the seat of a bishop; a market town grows across the river",
       "973: Prag bir piskoposluk merkezi olur; nehrin karşısında bir pazar kasabası büyür"),
     cam=(50.0850, 14.4120, 4.0)),
 seg(1060, 1139, 11, PRE, PR, T("Vyšehrad", "Vyšehrad"),
     T("Late 11th century: Duke Vratislav II moves his seat from Prague Castle to Vyšehrad",
       "11. yüzyıl sonu: Dük II. Vratislav makamını Prag Kalesi'nden Vyšehrad'a taşır"),
     cam=(50.0700, 14.4180, 4.4)),
 seg(1140, 1157, 6, PRE, PR, cam=(50.0830, 14.4120, 4.0)),
 seg(1158, 1229, 11, MED, PR, T("The Judith Bridge", "Judith Köprüsü"),
     T("1158–1172: the stone Judith Bridge joins the castle side to the market town",
       "1158–1172: taş Judith Köprüsü kale tarafını pazar kasabasına bağlar"),
     cam=(50.0865, 14.4120, 2.6), chapter=T("Medieval Towns", "Orta Çağ Kasabaları")),
 seg(1230, 1256, 11, MED, PR, T("The Old Town Walls", "Eski Şehir Surları"),
     T("1230s: the Old Town gets town rights and a wall with a moat around it",
       "1230'lar: Eski Şehir kent haklarını ve çevresinde hendekli bir sur alır"),
     cam=(50.0860, 14.4190, 3.0)),
 seg(1257, 1269, 11, MED, PR, T("The Lesser Town", "Küçük Şehir"),
     T("1257: King Ottokar II founds a new town below the castle, today's Malá Strana",
       "1257: Kral II. Ottokar kalenin altında yeni bir kasaba kurar; bugünkü Malá Strana"),
     cam=(50.0880, 14.4050, 2.6)),
 seg(1270, 1319, 11, MED, PR, T("The Old-New Synagogue", "Eski-Yeni Sinagog"),
     T("Around 1270: the Old-New Synagogue is completed in the Jewish Town",
       "1270 civarı: Yahudi Mahallesi'ndeki Eski-Yeni Sinagog tamamlanır"),
     cam=(50.0890, 14.4180, 2.4)),
 seg(1320, 1337, 6, MED, PR, cam=(50.0890, 14.3990, 2.8)),
 seg(1338, 1343, 11, MED, PR, T("The Old Town Hall", "Eski Belediye Binası"),
     T("1338: King John lets the Old Town buy a house on its square for a town hall",
       "1338: Kral John, Eski Şehir'in meydanda belediye için bir ev almasına izin verir"),
     cam=(50.0870, 14.4200, 2.2)),
 seg(1344, 1347, 11, GOLD, PR, T("St Vitus Cathedral", "Aziz Vitus Katedrali"),
     T("1344: Charles IV begins a Gothic cathedral at the castle; it is finished only in 1929",
       "1344: IV. Karl kalede Gotik bir katedrale başlar; ancak 1929'da tamamlanır"),
     pop=PI(1346, 1347), cam=(50.0905, 14.4010, 2.2), chapter=T("Charles IV's Capital", "IV. Karl'ın Başkenti")),
 seg(1348, 1356, 12, GOLD, PR, T("The New Town", "Yeni Şehir"),
     T("1348: Charles IV founds a university and a planned New Town, nearly doubling Prague",
       "1348: IV. Karl bir üniversite ve planlı bir Yeni Şehir kurar; Prag neredeyse iki katına çıkar"),
     pop=PI(1348, 1356), cam=(50.0790, 14.4240, 5.0)),
 seg(1357, 1359, 11, GOLD, PR, T("Charles Bridge", "Karl Köprüsü"),
     T("1357: work begins on a new stone bridge; the Judith Bridge had fallen in a flood in 1342",
       "1357: yeni bir taş köprüye başlanır; Judith Köprüsü 1342'de bir selde yıkılmıştı"),
     pop=PI(1357, 1359), cam=(50.0864, 14.4120, 2.2)),
 seg(1360, 1409, 11, GOLD, PR, T("The Hunger Wall", "Açlık Duvarı"),
     T("1360–1362: Charles IV has a wall built across Petřín hill to guard the castle side",
       "1360–1362: IV. Karl kale tarafını korumak için Petřín tepesi boyunca bir duvar ördürür"),
     pop=PI(1360, 1409), cam=(50.0840, 14.3990, 2.8)),
 seg(1410, 1418, 11, GOLD, PR, T("The Astronomical Clock", "Astronomik Saat"),
     T("1410: the astronomical clock is installed on the Old Town Hall; it still runs today",
       "1410: astronomik saat Eski Belediye Binası'na takılır; bugün hâlâ çalışıyor"),
     pop=PI(1410, 1418), cam=(50.0870, 14.4205, 1.8)),
 seg(1419, 1419.9, 11, HUS, PR, T("The First Defenestration", "Birinci Defenestrasyon"),
     T("30 July 1419: Hussites throw Catholic councillors from the windows of the New Town Hall",
       "30 Temmuz 1419: Husçular Katolik meclis üyelerini Yeni Belediye'nin pencerelerinden atar"),
     pop=P(1419), cam=(50.0775, 14.4200, 2.0), chapter=T("Hussite Prague", "Husçu Prag")),
 seg(1420, 1474, 11, HUS, PR, T("Battle of Vítkov Hill", "Vítkov Tepesi Muharebesi"),
     T("14 July 1420: Jan Žižka's Hussites drive off the crusader army besieging Prague",
       "14 Temmuz 1420: Jan Žižka'nın Husçuları Prag'ı kuşatan haçlı ordusunu püskürtür"),
     pop=PI(1420, 1474), cam=(50.0860, 14.4400, 4.4)),
 seg(1475, 1540, 11, HUS, PR, T("The Powder Tower", "Barut Kulesi"),
     T("1475: King Vladislav II lays the first stone of a new gate tower, today's Powder Tower",
       "1475: Kral II. Vladislav yeni bir kapı kulesinin temelini atar; bugünkü Barut Kulesi"),
     pop=PI(1475, 1540), cam=(50.0870, 14.4260, 2.2)),
 seg(1541, 1597, 11, HAB, PR, T("The Fire of 1541", "1541 Yangını"),
     T("1541: fire sweeps the Lesser Town and the castle; fifty people die",
       "1541: yangın Küçük Şehir'i ve kaleyi kasıp kavurur; elli kişi ölür"),
     pop=PI(1541, 1597), cam=(50.0890, 14.4030, 2.6), chapter=T("Habsburg Prague", "Habsburg Prag'ı")),
 seg(1598, 1617, 11, HAB, PR, T("Rudolf II's Capital", "II. Rudolf'un Başkenti"),
     T("1598: Emperor Rudolf II makes Hradčany a royal town; Prague is the empire's centre",
       "1598: İmparator II. Rudolf Hradčany'yi kraliyet kenti yapar; Prag imparatorluğun merkezidir"),
     pop=PI(1598, 1617), cam=(50.0895, 14.3980, 2.6)),
 seg(1618, 1620.9, 11, HAB, PR, T("Defenestration of 1618", "1618 Defenestrasyonu"),
     T("23 May 1618: royal officials are thrown from a castle window; war follows",
       "23 Mayıs 1618: kraliyet görevlileri kale penceresinden atılır; ardından savaş gelir"),
     pop=PI(1618, 1620.9), cam=(50.0905, 14.4000, 2.0)),
 seg(1621, 1647, 6, HAB, PR, pop=PI(1621, 1647), cam=(50.0860, 14.4120, 3.4)),
 seg(1648, 1653, 11, HAB, PR, T("The Swedes at the Bridge", "Köprüdeki İsveçliler"),
     T("1648: Swedish troops take the castle side but are stopped on Charles Bridge",
       "1648: İsveç askerleri kale tarafını alır ama Karl Köprüsü'nde durdurulur"),
     pop=PI(1648, 1653), cam=(50.0865, 14.4110, 2.4)),
 seg(1654, 1688, 11, BAR, PR, T("A Baroque Fortress", "Barok Kale"),
     T("1654: Vyšehrad is rebuilt as a Baroque fortress guarding the south of the city",
       "1654: Vyšehrad, şehrin güneyini koruyan Barok bir kale olarak yeniden yapılır"),
     pop=PI(1654, 1688), cam=(50.0680, 14.4190, 3.2), chapter=T("Baroque Prague", "Barok Prag")),
 seg(1689, 1699, 11, BAR, PR, T("The Great Fire of 1689", "1689 Büyük Yangını"),
     T("1689: a great fire damages the Old Town and the Jewish Town",
       "1689: büyük bir yangın Eski Şehir'e ve Yahudi Mahallesi'ne zarar verir"),
     pop=PI(1689, 1699), cam=(50.0875, 14.4190, 2.8)),
 seg(1700, 1783, 11, BAR, PR, T("Saints on the Bridge", "Köprüdeki Azizler"),
     T("1683–1714: most of the 30 statues go up on the bridge; 80,000 people live here by 1771",
       "1683–1714: 30 heykelin çoğu köprüye dikilir; 1771'de burada 80.000 kişi yaşar"),
     pop=PI(1700, 1783), cam=(50.0864, 14.4120, 2.6)),
 seg(1784, 1816, 11, BAR, PR, T("Four Towns Become One", "Dört Kasaba Tek Şehir"),
     T("12 February 1784: Joseph II unites Old Town, New Town, Lesser Town and Hradčany",
       "12 Şubat 1784: II. Joseph Eski, Yeni ve Küçük Şehir'i ve Hradčany'yi birleştirir"),
     pop=PI(1784, 1816), cam=(50.0830, 14.4150, 5.0)),
 seg(1817, 1844, 11, IND, PR, T("Karlín", "Karlín"),
     T("1817: building begins on Karlín, Prague's first suburb, outside the walls",
       "1817: Prag'ın ilk banliyösü Karlín'in inşasına surların dışında başlanır"),
     pop=PI(1817, 1844), cam=(50.0880, 14.4380, 4.0), chapter=T("Industrial Prague", "Sanayi Çağı Prag'ı")),
 seg(1845, 1873, 11, IND, PR, T("The Railway Arrives", "Demiryolu Geliyor"),
     T("20 August 1845: Prague's first station opens; today it is Masaryk station",
       "20 Ağustos 1845: Prag'ın ilk istasyonu açılır; bugün Masaryk istasyonu"),
     pop=PI(1845, 1873), cam=(50.0870, 14.4350, 4.2)),
 seg(1874, 1880, 11, IND, PR, T("The Walls Come Down", "Surlar Yıkılıyor"),
     T("20 July 1874: demolition of the city walls begins; the suburbs grow together",
       "20 Temmuz 1874: şehir surlarının yıkımı başlar; banliyöler birbirine kavuşur"),
     pop=PI(1874, 1880), cam=(50.0800, 14.4350, 6.0)),
 seg(1881, 1890, 11, IND, PR, T("The National Theatre", "Ulusal Tiyatro"),
     T("June 1881: the National Theatre opens; it burns in August and reopens in 1883",
       "Haziran 1881: Ulusal Tiyatro açılır; ağustosta yanar ve 1883'te yeniden açılır"),
     pop=PI(1881, 1890), cam=(50.0815, 14.4150, 2.2)),
 seg(1891, 1892, 11, IND, PR, T("1891: Tower and Museum", "1891: Kule ve Müze"),
     T("1891: the Petřín tower rises for a great exhibition; the National Museum is finished",
       "1891: büyük bir sergi için Petřín kulesi yükselir; Ulusal Müze tamamlanır"),
     pop=PI(1891, 1892), cam=(50.0820, 14.4140, 4.0)),
 seg(1893, 1917, 11, IND, PR, T("The Old Ghetto Is Cleared", "Eski Getto Yıkılıyor"),
     T("1893–1913: most of the old Jewish Town is torn down; six synagogues are kept",
       "1893–1913: eski Yahudi Mahallesi'nin çoğu yıkılır; altı sinagog korunur"),
     pop=PI(1893, 1917), cam=(50.0895, 14.4180, 2.2)),
 seg(1918, 1921, 11, CZ, PR, T("Capital of Czechoslovakia", "Çekoslovakya'nın Başkenti"),
     T("28 October 1918: independence is declared on Wenceslas Square; Prague becomes a capital",
       "28 Ekim 1918: Venceslas Meydanı'nda bağımsızlık ilan edilir; Prag başkent olur"),
     pop=PI(1918, 1921), cam=(50.0815, 14.4270, 3.0), chapter=T("Capital of a Republic", "Bir Cumhuriyetin Başkenti")),
 seg(1922, 1938, 11, CZ, PR, T("Greater Prague", "Büyük Prag"),
     T("1 January 1922: 37 towns and villages join the city; 676,000 people now live in Prague",
       "1 Ocak 1922: 37 kasaba ve köy şehre katılır; Prag'da artık 676.000 kişi yaşar"),
     pop=PI(1922, 1938), cam=(50.0800, 14.4300, 14.0)),
 seg(1939, 1944, 11, WAR, PR, T("Occupation", "İşgal"),
     T("March 1939: German troops occupy Prague, seat of the Nazi 'Protectorate' until 1945",
       "Mart 1939: Alman askerleri Prag'ı işgal eder; 1945'e dek Nazi 'Protektorası'nın merkezi"),
     pop=PI(1939, 1944), cam=(50.0850, 14.4200, 8.0), chapter=T("War and Occupation", "Savaş ve İşgal")),
 seg(1945, 1947, 11, WAR, PR, T("Bombs and the Uprising", "Bombalar ve Ayaklanma"),
     T("14 February 1945: a US raid in error kills 701 people; on 5 May Prague rises up",
       "14 Şubat 1945: ABD'nin hatalı bir baskını 701 kişiyi öldürür; 5 Mayıs'ta Prag ayaklanır"),
     pop=PI(1945, 1947), cam=(50.0740, 14.4250, 4.0)),
 seg(1948, 1967, 11, COM, PR, T("Panel Housing", "Panel Bloklar"),
     T("February 1948: the Communists take power; big panel estates rise from 1959",
       "Şubat 1948: Komünistler iktidarı alır; 1959'dan itibaren büyük panel siteler yükselir"),
     pop=PI(1948, 1967), cam=(50.0700, 14.4000, 16.0), chapter=T("Communist Prague", "Komünist Prag")),
 seg(1968, 1972, 11, COM, PR, T("August 1968", "Ağustos 1968"),
     T("August 1968: Warsaw Pact armies occupy Prague and end the Prague Spring",
       "Ağustos 1968: Varşova Paktı orduları Prag'ı işgal eder ve Prag Baharı'nı bitirir"),
     pop=PI(1968, 1972), cam=(50.0810, 14.4280, 4.0)),
 seg(1973, 1973.9, 11, COM, PR, T("The Nusle Bridge", "Nusle Köprüsü"),
     T("22 February 1973: the 485 m Nusle Bridge opens across the valley below Vyšehrad",
       "22 Şubat 1973: 485 m'lik Nusle Köprüsü, Vyšehrad'ın altındaki vadinin üstünde açılır"),
     pop=PI(1973, 1973.9), cam=(50.0660, 14.4280, 2.6)),
 seg(1974, 1984, 11, COM, PR, T("The Metro and the Estates", "Metro ve Siteler"),
     T("9 May 1974: the metro opens; the city grows to 496 km² and Jižní Město rises",
       "9 Mayıs 1974: metro açılır; şehir 496 km²'ye büyür ve Jižní Město yükselir"),
     pop=PI(1974, 1984), cam=(50.0600, 14.4500, 18.0)),
 seg(1985, 1991, 11, COM, PR, T("The Velvet Revolution", "Kadife Devrim"),
     T("November 1989: huge crowds on Wenceslas Square bring Communist rule to an end",
       "Kasım 1989: Venceslas Meydanı'ndaki dev kalabalıklar Komünist yönetimi sona erdirir"),
     pop=PI(1985, 1991), cam=(50.0800, 14.4350, 5.0), chapter=T("Prague Today", "Bugünün Prag'ı")),
 seg(1992, 2001, 11, TODAY, PR, T("The Dancing House", "Dans Eden Ev"),
     T("1996: the Dancing House by Milunić and Gehry fills a gap left by the 1945 bombs",
       "1996: Milunić ve Gehry'nin Dans Eden Ev'i 1945 bombalarının bıraktığı boşluğu doldurur"),
     pop=PI(1992, 2001), cam=(50.0760, 14.4150, 2.0)),
 seg(2002, 2025, 11, TODAY, PR, T("The Flood of 2002", "2002 Seli"),
     T("August 2002: the Vltava floods the city; archives suffer, but the landmarks survive",
       "Ağustos 2002: Vltava şehri basar; arşivler zarar görür ama anıt yapılar ayakta kalır"),
     pop=PI(2002, 2025), cam=(50.0860, 14.4250, 6.0)),
 seg(2026, 2026, 16, TODAY, PR, T("Prague Today", "Bugünün Prag'ı"),
     T("From a castle on a hill around 880 to about 1.41 million people today",
       "880 civarında bir tepedeki kaleden bugün yaklaşık 1,41 milyon kişiye"),
     pop=[1397880, 1409528], cam=(50.0700, 14.4400, 20.0)),
]
for s_ in S:   # pacing: titled segments 11.4 s (target ≈ 525 s with the cold open)
    if s_.get("title"): s_["seconds"] = 16 if s_["to"] == 2026 else 11.4
# the 1419 segment's sub is long in TR: check lengths later with the validator

# ------------------------------------------------------------------ geography of growth (≈ reconstructions, research.md)
# Old Town wall/moat: under today's Národní – Na Příkopě – Revoluční (Old Town WP), from the river to the river
OLD_WALL = [(50.0816, 14.4142), (50.0820, 14.4170), (50.0826, 14.4200), (50.0836, 14.4228), (50.0852, 14.4250),
            (50.0866, 14.4270), (50.0872, 14.4278), (50.0893, 14.4281), (50.0915, 14.4283), (50.0930, 14.4278)]
OLD_RIVER = [(50.0930, 14.4278), (50.0928, 14.4200), (50.0915, 14.4150), (50.0890, 14.4140), (50.0864, 14.4138),
             (50.0840, 14.4140), (50.0816, 14.4142)]
OLD_TOWN = OLD_WALL + OLD_RIVER[1:-1]
JEWISH = [(50.0912, 14.4155), (50.0915, 14.4185), (50.0905, 14.4212), (50.0890, 14.4210), (50.0885, 14.4180),
          (50.0890, 14.4155)]
# New Town wall (1348, ≈3.5 km, WP New Town): from Vyšehrad up the ridge and north to the river at Těšnov (≈)
NEW_WALL = [(50.0660, 14.4200), (50.0675, 14.4265), (50.0705, 14.4300), (50.0745, 14.4320), (50.0790, 14.4335),
            (50.0835, 14.4345), (50.0870, 14.4365), (50.0900, 14.4385), (50.0930, 14.4392)]
NEW_TOWN = (OLD_WALL + [(50.0930, 14.4392)] + list(reversed(NEW_WALL))[1:]
            + [(50.0700, 14.4160), (50.0760, 14.4135), (50.0800, 14.4135)])
# Lesser Town wall (1257) and the castle (≈)
LESSER_WALL = [(50.0920, 14.4100), (50.0912, 14.4060), (50.0898, 14.4040), (50.0880, 14.4010), (50.0860, 14.4000),
               (50.0835, 14.4010), (50.0815, 14.4030), (50.0803, 14.4055)]
LESSER = LESSER_WALL + [(50.0815, 14.4075), (50.0850, 14.4085), (50.0880, 14.4090), (50.0905, 14.4100)]
HUNGER = [(50.0862, 14.3895), (50.0850, 14.3920), (50.0838, 14.3948), (50.0825, 14.3975), (50.0813, 14.4005),
          (50.0805, 14.4035), (50.0800, 14.4058)]
CASTLE_RING = oval(CASTLE, 300, 75, rot_deg=0, n=14)
HRAD_TOWN = [(50.0905, 14.3970), (50.0912, 14.3900), (50.0880, 14.3880), (50.0868, 14.3905), (50.0878, 14.3965)]
VYS_RING = oval(VYSEHRAD, 330, 220, rot_deg=-20, n=14)
CASTLE_SET = oval((50.0878, 14.4050), 260, 180, rot_deg=10, n=12)
MARKET = oval((50.0870, 14.4185), 420, 300, rot_deg=0, n=14)

KARLIN_P = [(50.0935, 14.4400), (50.0950, 14.4660), (50.0905, 14.4660), (50.0895, 14.4400)]
SMICHOV_P = [(50.0800, 14.4050), (50.0790, 14.3980), (50.0700, 14.3980), (50.0620, 14.4020), (50.0610, 14.4110),
             (50.0700, 14.4110), (50.0780, 14.4075)]
VINO_P = [(50.0835, 14.4350), (50.0815, 14.4650), (50.0700, 14.4650), (50.0670, 14.4330), (50.0745, 14.4325)]
ZIZ_P = [(50.0895, 14.4400), (50.0880, 14.4850), (50.0820, 14.4850), (50.0815, 14.4360)]
VITKOV_P = oval(VITKOV, 650, 150, rot_deg=0, n=12)
HOLE_P = [(50.0960, 14.4150), (50.1080, 14.4200), (50.1090, 14.4550), (50.1000, 14.4600), (50.0955, 14.4400)]
LIBEN_P = oval(LIBEN, 1300, 800, n=14)
NUSLE_P = [(50.0670, 14.4250), (50.0690, 14.4700), (50.0560, 14.4700), (50.0560, 14.4250)]
DEJV_P = [(50.0940, 14.3750), (50.1100, 14.3750), (50.1130, 14.4100), (50.0990, 14.4130), (50.0935, 14.4050)]
BREVNOV_P = [(50.0880, 14.3400), (50.0935, 14.3800), (50.0880, 14.3880), (50.0800, 14.3870), (50.0790, 14.3450)]
INNER = [L(OLD_TOWN), L(LESSER), L(HRAD_TOWN), L(KARLIN_P), L(SMICHOV_P), L(VINO_P), L(ZIZ_P), L(HOLE_P), L(NUSLE_P),
         L(DEJV_P), L(BREVNOV_P)]
PETRIN_P = [(50.0880, 14.3870), (50.0870, 14.3990), (50.0830, 14.4020), (50.0800, 14.4010), (50.0790, 14.3960),
            (50.0820, 14.3900)]
LETNA_P = [(50.0960, 14.4120), (50.0985, 14.4160), (50.0975, 14.4300), (50.0950, 14.4290), (50.0945, 14.4150)]
STROMOVKA_P = [(50.1040, 14.4050), (50.1080, 14.4100), (50.1070, 14.4300), (50.1035, 14.4280)]
GREATER = [(50.1350, 14.3300), (50.1400, 14.4500), (50.1300, 14.5300), (50.0900, 14.5600), (50.0350, 14.5300),
           (50.0150, 14.4500), (50.0200, 14.3500), (50.0600, 14.3000), (50.1000, 14.3000)]
OUTER = [(50.1700, 14.2600), (50.1750, 14.5000), (50.1500, 14.6500), (50.0800, 14.6700), (49.9800, 14.6200),
         (49.9500, 14.4500), (49.9800, 14.3000), (50.0400, 14.2400), (50.1100, 14.2300)]
GREEN = [L(PETRIN_P), L(LETNA_P), L(STROMOVKA_P), L(VITKOV_P)]
WENC_SQ = strip((50.0835, 14.4235), (50.0796, 14.4300), 60)
CHARLES_SQ = strip((50.0772, 14.4198), (50.0738, 14.4190), 150)
OLD_SQ = oval(STARE, 70, 55, n=10)


def D(name, style, poly, frm, to, dens, grain, grow, **kw):
    d = {"name": name, "style": style, "poly": L(poly), "from": frm, "to": to, "density": dens, "grain_m": grain,
         "grow_from": list(grow)}
    d.update(kw); return d


SQ_HOLES = [L(WENC_SQ), L(CHARLES_SQ), L(OLD_SQ)]
districts = [
 D("Settlement below the castle (≈)", "celtic", CASTLE_SET, 880, 960, 0.4, 45, (50.0885, 14.4045)),
 D("Vyšehrad settlement (≈)", "celtic", oval(VYSEHRAD, 260, 170, rot_deg=-20, n=12), 940, 1080, 0.35, 45, VYSEHRAD),
 D("Market town on the right bank (≈)", "medieval", MARKET, 973, 1225, 0.5, 50, STARE, holes=[L(OLD_SQ)]),
 D("Old Town (≈)", "medieval", OLD_TOWN, 1230, 1300, 0.75, 50, STARE, holes=[L(OLD_SQ), L(JEWISH)]),
 D("Jewish Town (≈)", "medieval", JEWISH, 1240, 1300, 0.85, 40, JOSEFOV),
 D("Lesser Town (≈)", "medieval", LESSER, 1257, 1300, 0.7, 50, MALA),
 D("Hradčany (≈)", "medieval", HRAD_TOWN, 1320, 1360, 0.55, 55, HRADCANY),
 D("New Town (≈)", "medieval", NEW_TOWN, 1348, 1420, 0.55, 60, (50.0800, 14.4250), holes=SQ_HOLES),
 D("Lesser Town rebuilt after 1541 (≈)", "stone", LESSER, 1545, 1720, 0.75, 55, MALA),
 D("Jewish Town rebuilt after 1689 (≈)", "medieval", JEWISH, 1690, 1715, 0.85, 40, JOSEFOV, fade=[1893, 1913, 0.15]),
 D("Old Town rebuilt after 1689 (≈)", "stone", OLD_TOWN, 1690, 1750, 0.78, 52, STARE, holes=[L(OLD_SQ), L(JEWISH)]),
 D("Josefov rebuilt (≈)", "victorian", JEWISH, 1897, 1915, 0.7, 55, JOSEFOV),
 D("New Town 19th century (≈)", "victorian", NEW_TOWN, 1830, 1890, 0.7, 60, (50.0810, 14.4300), holes=SQ_HOLES),
 D("Karlín (≈)", "industrial", KARLIN_P, 1817, 1870, 0.65, 70, (50.0920, 14.4420), grid_deg=0),
 D("Smíchov (≈)", "industrial", SMICHOV_P, 1830, 1905, 0.6, 75, (50.0760, 14.4050)),
 D("Vinohrady (≈)", "victorian", VINO_P, 1867, 1910, 0.7, 70, (50.0770, 14.4380), grid_deg=0),
 D("Žižkov (≈)", "victorian", ZIZ_P, 1875, 1905, 0.7, 70, (50.0860, 14.4420), holes=[L(VITKOV_P)]),
 D("Holešovice-Bubny (≈)", "industrial", HOLE_P, 1880, 1920, 0.55, 85, (50.0990, 14.4300), holes=[L(LETNA_P), L(STROMOVKA_P)]),
 D("Libeň (≈)", "suburb", LIBEN_P, 1890, 1925, 0.5, 100, LIBEN),
 D("Nusle and Vršovice (≈)", "victorian", NUSLE_P, 1890, 1925, 0.6, 85, (50.0650, 14.4350)),
 D("Dejvice and Bubeneč (≈)", "suburb", DEJV_P, 1900, 1935, 0.6, 90, (50.0990, 14.4000), holes=[L(STROMOVKA_P)]),
 D("Břevnov and Střešovice (≈)", "suburb", BREVNOV_P, 1900, 1935, 0.5, 100, (50.0850, 14.3800)),
 D("Greater Prague (≈)", "suburb", GREATER, 1922, 1950, 0.5, 110, (50.0800, 14.4300),
   holes=INNER + GREEN + [L(oval(PETRINY, 700, 500)), L(oval(PANKRAC, 700, 500))]),
 D("Petřiny estate (≈)", "modern", oval(PETRINY, 700, 500), 1959, 1965, 0.5, 110, PETRINY),
 D("Pankrác estate (≈)", "modern", oval(PANKRAC, 700, 500), 1962, 1967, 0.5, 110, PANKRAC),
 D("Severní Město (≈)", "modern", oval(SEVERNI, 1600, 1000), 1968, 1985, 0.45, 130, SEVERNI),
 D("Jižní Město (≈)", "modern", oval(JIZNI, 1800, 1200, rot_deg=20), 1971, 1990, 0.5, 130, JIZNI),
 D("Jihozápadní Město (≈)", "modern", oval(JZM, 1500, 900), 1978, 1995, 0.45, 130, JZM),
 D("Outer suburbs (≈)", "suburb", OUTER, 1955, 2024, 0.35, 170, (50.0800, 14.4300),
   holes=[L(GREATER), L(oval(SEVERNI, 1600, 1000)), L(oval(JIZNI, 1800, 1200, rot_deg=20)), L(oval(JZM, 1500, 900))]),
]

landmarks = [
 {"type": "castle", "name": T("Prague Castle", "Prag Kalesi"), "at": list(CASTLE), "built": 880, "rise_s": 5,
  "size_m": [420, 110, 18], "rot_deg": 0, "colors": {"wall": "#d8cfbf", "roof": "#8a4b37"}},
 {"type": "church", "name": T("Rotunda of St Vitus", "Aziz Vitus Rotondası"), "at": list(VITUS), "built": 925, "removed": 1060,
  "rise_s": 4, "size_m": [20, 20, 14], "scale": 1.5, "colors": {"wall": "#e9e1d2", "roof": "#6b5a4a"}},
 {"type": "church", "name": T("Basilica of St Vitus", "Aziz Vitus Bazilikası"), "at": list(VITUS), "built": 1060, "removed": 1344,
  "rise_s": 4, "size_m": [60, 22, 20], "scale": 1.4, "colors": {"wall": "#e9e1d2", "roof": "#6b5a4a"}},
 {"type": "cathedral", "name": T("St Vitus Cathedral (unfinished)", "Aziz Vitus Katedrali (yarım)"), "at": list(VITUS),
  "built": 1344, "removed": 1929, "rise_s": 20, "size_m": [70, 40, 45], "scale": 1.4, "colors": {"wall": "#b9b3a8", "roof": "#4e6a63"}},
 {"type": "cathedral", "name": T("St Vitus Cathedral", "Aziz Vitus Katedrali"), "at": list(VITUS), "built": 1929, "rise_s": 6,
  "size_m": [124, 60, 60], "scale": 1.4, "colors": {"wall": "#b9b3a8", "roof": "#4e6a63"}},
 {"type": "castle", "name": T("Vyšehrad castle", "Vyšehrad kalesi"), "at": list(VYSEHRAD), "built": 950, "removed": 1654, "rise_s": 4,
  "size_m": [160, 90, 14], "rot_deg": -20, "colors": {"wall": "#cfc6b4", "roof": "#7c4a36"}},
 {"type": "fort", "name": T("Vyšehrad fortress", "Vyšehrad kalesi"), "at": list(VYSEHRAD), "built": 1654, "rise_s": 5,
  "size_m": [420, 260, 10], "rot_deg": -20, "colors": {"wall": "#9a8f7c"}},
 {"type": "box", "name": T("Old-New Synagogue", "Eski-Yeni Sinagog"), "at": list(SYNAG), "built": 1270, "rise_s": 4,
  "size_m": [26, 16, 16], "scale": 1.5, "colors": {"wall": "#d7cbb3", "roof": "#6a5544"}},
 {"type": "clocktower", "name": T("Old Town Hall", "Eski Belediye Binası"), "at": list(TOWNHALL), "built": 1338.5, "rise_s": 5,
  "size_m": [30, 16, 60], "scale": 1.3, "colors": {"wall": "#d9d0bf", "roof": "#4f4a46"}},
 {"type": "clocktower", "name": T("New Town Hall", "Yeni Belediye Binası"), "at": list(NEWHALL), "built": 1377, "rise_s": 5,
  "size_m": [50, 18, 40], "scale": 1.3, "colors": {"wall": "#ddd5c4", "roof": "#4f4a46"}},
 {"type": "tower", "name": T("Powder Tower", "Barut Kulesi"), "at": list(POWDER), "built": 1475, "rise_s": 6,
  "size_m": [14, 14, 65], "scale": 1.3, "colors": {"wall": "#6d6559", "roof": "#3f3d3a"}},
 {"type": "station", "name": T("Prague station", "Prag istasyonu"), "at": list(STATION), "built": 1845.6, "rise_s": 5,
  "size_m": [150, 40, 15], "rot_deg": 80, "colors": {"wall": "#e2d6be", "roof": "#7d5a44"}},
 {"type": "palace", "name": T("National Theatre", "Ulusal Tiyatro"), "at": list(THEATRE), "built": 1881.44, "removed": 1881.62,
  "rise_s": 3, "size_m": [90, 60, 30], "colors": {"wall": "#e6dcc6", "roof": "#3a5d58"}},
 {"type": "palace", "name": T("National Theatre (rebuilt)", "Ulusal Tiyatro (yeniden)"), "at": list(THEATRE), "built": 1883.88,
  "rise_s": 3, "size_m": [90, 60, 30], "colors": {"wall": "#e6dcc6", "roof": "#3a5d58"}},
 {"type": "palace", "name": T("National Museum", "Ulusal Müze"), "at": list(MUSEUM), "built": 1891, "rise_s": 5,
  "size_m": [104, 70, 36], "rot_deg": 35, "colors": {"wall": "#d9cdb3", "roof": "#3a5d58"}},
 {"type": "tower", "name": T("Petřín Lookout Tower", "Petřín Seyir Kulesi"), "at": list(PTOWER), "built": 1891.3, "rise_s": 5,
  "size_m": [12, 12, 63.5], "scale": 1.6, "colors": {"wall": "#5b4a42"}},
 {"type": "spire_tower", "name": T("Žižkov Television Tower", "Žižkov Televizyon Kulesi"), "at": list(TVTOWER), "built": 1992,
  "rise_s": 8, "size_m": [24, 24, 216], "scale": 1.2, "colors": {"wall": "#c9ccd0"}},
 {"type": "box", "name": T("Dancing House", "Dans Eden Ev"), "at": list(DANCING), "built": 1996, "rise_s": 5,
  "size_m": [30, 24, 26], "scale": 1.4, "colors": {"wall": "#d9dcdf", "roof": "#9aa3aa"}},
]


def wall(name, path, built, removed, height="mid", towers=80, **kw):
    d = {"name": name, "path": L(path), "built": built, "height": height, "towers_m": towers}
    if removed is not None: d["removed"] = removed
    d.update(kw); return d


walls = [
 wall("Castle rampart (≈)", CASTLE_RING + [CASTLE_RING[0]], 880, None, height="mid", towers=70),
 wall("Old Town wall and moat (≈)", OLD_WALL, 1232, 1784, height="mid", towers=70, moat=True, double_side=-1),
 wall("Lesser Town wall (≈)", LESSER_WALL, 1257, 1874.6, height="mid", towers=70),
 wall("New Town wall (≈)", NEW_WALL, 1348.3, 1874.6, height="high", towers=110),
 wall("Hunger Wall (≈)", HUNGER, 1360, None, height="low", towers=120),
 wall("Hradčany wall (≈)", [(50.0905, 14.3970), (50.0912, 14.3900), (50.0880, 14.3880), (50.0862, 14.3895)], 1360, 1874.6,
      height="mid", towers=90),
 wall("Vyšehrad Baroque ramparts (≈)", VYS_RING + [VYS_RING[0]], 1654, None, height="high", towers=0),
]

CB_E, CB_W = (50.08620, 14.41530), (50.08655, 14.40850)   # ≈ ends of the 516 m bridge around the WP centre point
bridges = [
 {"name": "Judith Bridge", "path": L([(50.08665, 14.41520), (50.08700, 14.40860)]), "built": 1172, "removed": 1342.1,
  "style": "stone", "width_m": 8},
 {"name": "Charles Bridge", "path": L([CB_E, CB_W]), "built": 1357.5, "style": "stone", "width_m": 10},
 {"name": "Nusle Bridge", "path": L([(50.06800, 14.43000), (50.06370, 14.43100)]), "built": 1973.15, "style": "modern",
  "width_m": 26},
]

roads = [
 {"name": "Railway to Olomouc (≈)", "path": L([STATION, (50.0905, 14.4400), (50.0965, 14.4600), (50.1030, 14.4850),
  (50.1100, 14.5200), (50.1150, 14.5600)]), "from": 1845.6, "kind": "rail", "width_m": 12},
]

fires = [
 {"year": 1541.5, "poly": L(LESSER[:8] + [(50.0905, 14.3975), (50.0912, 14.4030)]), "duration_s": 6, "plumes": 7},
 {"year": 1689.5, "poly": L(OLD_TOWN), "duration_s": 6, "plumes": 7},
 {"year": 1881.6, "poly": L(oval(THEATRE, 60, 45, n=8)), "duration_s": 3, "plumes": 2},
 {"year": 1945.12, "poly": L(oval(DANCING, 45, 35, n=8)), "duration_s": 3, "plumes": 2},
]
smoke = [
 {"at": list(VITKOV), "from": 1420.3, "to": 1420.9, "scale": 1.1},
 {"at": list(MALA), "from": 1648.5, "to": 1648.9, "scale": 0.9},
 {"at": [50.0860, 14.4135], "from": 1648.55, "to": 1648.85, "scale": 0.7},
 {"at": list(VINO), "from": 1945.12, "to": 1945.4, "scale": 1.0},
 {"at": list(CHARLESQ), "from": 1945.12, "to": 1945.4, "scale": 0.8},
 {"at": list(TOWNHALL), "from": 1945.35, "to": 1945.5, "scale": 0.8},
]
camps = [
 {"poly": L(oval((50.0950, 14.4250), 700, 250, n=10)), "from": 1420.45, "to": 1420.55, "count": 160},
]


def lab(en, tr, at, frm=None, to=None, kind="place", now=None, lift=None):
    d = {"text": T(en, tr), "at": list(at), "kind": kind}
    if frm is not None: d["from"] = frm
    if to is not None: d["to"] = to
    if now: d["now"] = T(*now)
    if lift: d["lift_m"] = lift
    return d


labels = [
 lab("VLTAVA", "VLTAVA", (50.0800, 14.4110), kind="water", to=1347),
 lab("VLTAVA", "VLTAVA", (50.0700, 14.4130), kind="water", frm=1874, to=1938),
 lab("Prague Castle", "Prag Kalesi", CASTLE, 870, 899, lift=30),
 lab("St Vitus", "Aziz Vitus", VITUS, 900, 934, lift=25),
 lab("Market town", "Pazar kasabası", STARE, 973, 1059, now=("Old Town Square", "Eski Şehir Meydanı")),
 lab("Vyšehrad", "Vyšehrad", VYSEHRAD, 1060, 1139, lift=20),
 lab("Judith Bridge", "Judith Köprüsü", BRIDGE, 1158, 1229, lift=10),
 lab("Old Town moat", "Eski Şehir hendeği", (50.0836, 14.4228), 1230, 1256,
     now=("Národní, Na Příkopě, Revoluční", "Národní, Na Příkopě, Revoluční")),
 lab("Lesser Town", "Küçük Şehir", MALA, 1257, 1269, now=("Malá Strana", "Malá Strana")),
 lab("Jewish Town", "Yahudi Mahallesi", JOSEFOV, 1270, 1319, now=("Josefov", "Josefov")),
 lab("Hradčany", "Hradčany", HRADCANY, 1320, 1337),
 lab("Old Town Hall", "Eski Belediye", TOWNHALL, 1338, 1343, lift=70),
 lab("St Vitus Cathedral", "Aziz Vitus Katedrali", VITUS, 1344, 1347, lift=60),
 lab("Horse Market", "At Pazarı", WENC, 1348, 1356, now=("Wenceslas Square", "Venceslas Meydanı")),
 lab("Cattle Market", "Sığır Pazarı", CHARLESQ, 1348, 1356, now=("Charles Square", "Karl Meydanı")),
 lab("Hay Market", "Saman Pazarı", HAYMKT, 1348, 1356, now=("Senovážné náměstí", "Senovážné náměstí")),
 lab("Stone Bridge", "Taş Köprü", BRIDGE, 1357, 1359, now=("Charles Bridge", "Karl Köprüsü"), lift=10),
 lab("Royal vineyards", "Kraliyet bağları", VINO, 1360, 1409, now=("Vinohrady", "Vinohrady")),
 lab("Hunger Wall", "Açlık Duvarı", (50.0825, 14.3975), 1360, 1409),
 lab("Old Town Hall", "Eski Belediye", TOWNHALL, 1410, 1418, lift=70),
 lab("New Town Hall", "Yeni Belediye", NEWHALL, 1419, 1419.9, lift=50),
 lab("Vítkov Hill", "Vítkov Tepesi", VITKOV, 1420, 1474, now=("Žižkov, named after Jan Žižka", "Žižkov, adını Jan Žižka'dan alır")),
 lab("New Tower", "Yeni Kule", POWDER, 1475, 1540, now=("Powder Tower", "Barut Kulesi"), lift=70),
 lab("Lesser Town", "Küçük Şehir", MALA, 1541, 1597),
 lab("Hradčany", "Hradčany", HRADCANY, 1598, 1617),
 lab("Prague Castle", "Prag Kalesi", CASTLE, 1618, 1620.9, lift=30),
 lab("Charles Bridge", "Karl Köprüsü", BRIDGE, 1648, 1653, lift=10),
 lab("Vyšehrad", "Vyšehrad", VYSEHRAD, 1654, 1688, lift=20),
 lab("Jewish Town", "Yahudi Mahallesi", JOSEFOV, 1689, 1699),
 lab("Stone Bridge", "Taş Köprü", BRIDGE, 1700, 1783, now=("Charles Bridge", "Karl Köprüsü"), lift=10),
 lab("Old Town", "Eski Şehir", STARE, 1784, 1816, now=("Staré Město", "Staré Město")),
 lab("New Town", "Yeni Şehir", NOVE, 1784, 1816, now=("Nové Město", "Nové Město")),
 lab("Karlín", "Karlín", KARLIN, 1817),
 lab("Prague station", "Prag istasyonu", STATION, 1845.6, 1873, now=("Masaryk station", "Masaryk istasyonu"), lift=20),
 lab("Smíchov", "Smíchov", SMICHOV, 1845),
 lab("Vinohrady", "Vinohrady", VINO, 1874),
 lab("Žižkov", "Žižkov", ZIZKOV, 1881),
 lab("National Theatre", "Ulusal Tiyatro", THEATRE, 1881.4, 1890, lift=40),
 lab("Petřín Tower", "Petřín Kulesi", PTOWER, 1891, 1892, lift=90),
 lab("National Museum", "Ulusal Müze", MUSEUM, 1891, 1892, lift=40),
 lab("Holešovice", "Holešovice", HOLES_, 1884),
 lab("Josefov", "Josefov", JOSEFOV, 1893),
 lab("Wenceslas Square", "Venceslas Meydanı", WENC, 1918, 1921),
 lab("Vyšehrad", "Vyšehrad", VYSEHRAD, 1922),
 lab("Malá Strana", "Malá Strana", MALA, 1922),
 lab("Hradčany", "Hradčany", HRADCANY, 1922),
 lab("Bombed house", "Bombalanan ev", DANCING, 1945, 1947, now=("Dancing House", "Dans Eden Ev")),
 lab("Wenceslas Square", "Venceslas Meydanı", WENC, 1968, 1972),
 lab("Gottwald Bridge", "Gottwald Köprüsü", NUSLE_BR, 1973, 1973.9, now=("Nusle Bridge", "Nusle Köprüsü")),
 lab("Jižní Město", "Jižní Město", JIZNI, 1974),
 lab("Wenceslas Square", "Venceslas Meydanı", WENC, 1985, 1991),
 lab("Dancing House", "Dans Eden Ev", DANCING, 1992, 2001, lift=40),
 lab("Žižkov Tower", "Žižkov Kulesi", TVTOWER, 2002, lift=260),
]

city = {
 "slug": "prague", "seed": 880, "long_ok": True,
 "name": T("Prague", "Prag"),
 "intro": T("1,150 Years in 9 Minutes", "9 Dakikada 1.150 Yıl"), "intro_seconds": 3,
 "cold_open": {"seconds": 7, "hold": 4.5, "kicker": T("1,150 years · from a hilltop castle to a capital", "1.150 yıl · tepedeki bir kaleden başkente"),
               "camera": {"center": [50.0860, 14.4150], "dist_km": 6.0}},
 "people_notes": True,
 "closing_question": T("When did your family's story in Prague begin?", "Ailenizin Prag hikâyesi hangi yıl başladı?"),
 "music": {"style": "eras"},
 "geo": {"bbox": [49.90, 14.15, 50.24, 14.78], "cell_m": 100, "core_bbox": [50.045, 14.370, 50.115, 14.480], "core_cell_m": 30},   # rivers_keep ["Vltava"] kept 0 (OSM river areas unnamed) → all area rivers
 "view": {"azimuth_deg": 90, "pitch_deg": 46, "fov": 34},
 "render": {"vertical_exaggeration": 2.0},
 "segments": S,
 "districts": districts,
 "walls": walls, "bridges": bridges, "roads": roads, "landmarks": landmarks,
 "fires": fires, "smoke": smoke, "camps": camps,
 "open_spaces": [
  {"name": "Petřín (≈)", "poly": L(PETRIN_P)},
  {"name": "Letná plain (≈)", "poly": L(LETNA_P)},
  {"name": "Stromovka (≈)", "poly": L(STROMOVKA_P)},
  {"name": "Vítkov hill (≈)", "poly": L(VITKOV_P)},
  {"name": "Old Town Square (≈)", "poly": L(OLD_SQ)},
  {"name": "Wenceslas Square (≈)", "poly": L(WENC_SQ)},
  {"name": "Charles Square (≈)", "poly": L(CHARLES_SQ)},
 ],
 "labels": labels,
 "youtube": {
  "title": T("Prague: 1,150 Years in 9 Minutes (3D Timelapse, No AI)", "Prag: 9 Dakikada 1.150 Yıl (3D Timelapse, Yapay Zekâ Yok)"),
  "description": T(
   "Around 880 Prince Bořivoj founded a castle on a hill above the Vltava. Watch Prague grow from that castle and a market town "
   "across the river into the Old Town, the Lesser Town and Hradčany, then Charles IV's capital with its New Town, university, "
   "cathedral and stone bridge. See the Hussite defenestration of 1419 and the battle of Vítkov Hill, the fires of 1541 and 1689, "
   "the Swedes stopped on Charles Bridge in 1648, the four towns united in 1784, the railway, the walls coming down in 1874, "
   "Greater Prague in 1922, the war, the panel estates, 1968, 1989 — up to about 1.41 million people today, with the year and the "
   "population on screen.",
   "880 civarında Prens Bořivoj, Vltava'nın üstündeki bir tepede bir kale kurdu. Prag'ın bu kaleden ve nehrin karşısındaki "
   "pazar kasabasından Eski Şehir'e, Küçük Şehir'e ve Hradčany'ye, sonra Yeni Şehir'i, üniversitesi, katedrali ve taş köprüsüyle "
   "IV. Karl'ın başkentine dönüşmesini izleyin. 1419 Husçu defenestrasyonunu ve Vítkov Tepesi muharebesini, 1541 ve 1689 yangınlarını, "
   "1648'de Karl Köprüsü'nde durdurulan İsveçlileri, 1784'te birleşen dört kasabayı, demiryolunu, 1874'te yıkılan surları, 1922'de "
   "Büyük Prag'ı, savaşı, panel siteleri, 1968'i, 1989'u görün — bugünkü yaklaşık 1,41 milyon kişiye kadar; yıl ve nüfus ekranda."),
  "tags": ["prague history", "history of prague", "praha", "3d timelapse", "city evolution", "how prague grew",
           "prague timelapse", "charles bridge", "prague castle", "czech history", "old town prague", "charles iv",
           "urban history", "no ai"],
  "hashtags": ["#Prague", "#History", "#Timelapse"],
  "playlist": T("Cities of Europe", "Avrupa Şehirleri"),
  "thumb": {"line1": T("Prague", "Prag"), "line2": T("880 → TODAY", "880 → BUGÜN"),
            "line3": T("From hilltop castle to capital", "Tepedeki kaleden başkente"),
            "extra": "&pitch=30&az=90&cam=50.0880,14.4060,3.2", "style": "v2"},
 },
 "sources": [],
}
total = sum(s_["seconds"] for s_ in S) + city["cold_open"]["seconds"]
mins = round(total / 60)
city["intro"] = T(f"1,150 Years in {mins} Minutes", f"{mins} Dakikada 1.150 Yıl")
city["youtube"]["title"] = T(f"Prague: 1,150 Years in {mins} Minutes (3D Timelapse, No AI)",
                             f"Prag: {mins} Dakikada 1.150 Yıl (3D Timelapse, Yapay Zekâ Yok)")
city["sources"] = json.load(open(os.path.join(HERE, "_sources.json")))
json.dump(city, open(os.path.join(HERE, "city.json"), "w"), ensure_ascii=False, indent=1)
print("segments", len(S), "duration", total, "s =", f"{int(total) // 60}:{int(total) % 60:02d}")
