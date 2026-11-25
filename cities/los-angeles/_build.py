"""Builds cities/los-angeles/city.json. Every date/figure is from research.md (sources listed there).
Run: python3 cities/los-angeles/_build.py
Footprints of growth are simplified reconstructions (marked ≈); landmark points are Wikipedia infobox coordinates where
research.md says so, otherwise ≈ placements next to a sourced point."""
import json, math, os

T = lambda en, tr: {"en": en, "tr": tr}
HERE = os.path.dirname(os.path.abspath(__file__))
LAT0 = 34.05
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


def box(s, w, n, e):
    return [(s, w), (s, e), (n, e), (n, w)]


# ------------------------------------------------------------------ sourced points (research.md "Coordinates")
AVILA = (34.05722, -118.23778)          # Ávila Adobe (WP infobox)
PLAZA = (34.0571, -118.2382)            # ≈ beside the Ávila Adobe
CHURCH = (34.0567, -118.2393)           # ≈ Plaza church, west side of the plaza
PICO = (34.0564, -118.2377)             # ≈ Pico House, south side of the plaza
YAANGA = (34.0553, -118.2385)           # ≈ "just west of the river, beneath US 101", south of the plaza
FORT_MOORE = (34.05818, -118.24174)     # WP
CITY_HALL = (34.0536, -118.2430)        # WP
UNION = (34.05528, -118.23525)          # WP
COLISEUM = (34.01417, -118.28778)       # WP
DODGER = (34.07361, -118.24000)         # WP
DISNEY = (34.05528, -118.25000)         # WP
WILSHIRE = (34.05011, -118.25999)       # WP list
USBANK = (34.05101, -118.25444)         # WP list
AON = (34.04920, -118.25697)            # WP list
TWOCAL = (34.05137, -118.25163)         # WP list
GASCO = (34.05011, -118.25327)          # WP list
WELLS = (34.05290, -118.25184)          # WP list
SIGN = (34.13406, -118.32159)           # WP
LABREA = (34.0628, -118.3560)           # WP
MISSION = (34.09667, -118.10667)        # WP (present site)
HOLLYWOOD = (34.10167, -118.32667)      # WP
NOHO = (34.1739, -118.3790)             # WP
VANNUYS = (34.18667, -118.44874)        # WP
CANOGA = (34.20111, -118.59722)         # WP
VENICE = (33.99083, -118.45917)         # WP
WILMINGTON = (33.7800, -118.26167)      # WP
SANPEDRO = (33.7400, -118.2900)         # WP
PORT = (33.7300, -118.2625)             # WP
WATTS = (33.94167, -118.24167)          # WP
HIGHLAND = (34.11194, -118.19806)       # WP
DOWNTOWN = (34.0500, -118.2500)         # WP
ANGELS = (34.0516, -118.2502)           # ≈ original site at Third St between Hill and Olive (LA Conservancy)
LASHP = (34.0663, -118.2292)            # ≈ Los Angeles State Historic Park, beside the surviving Zanja segment
BOYLE = (34.0330, -118.2060)            # ≈ east across the river from downtown


# ------------------------------------------------------------------ timeline
def seg(frm, to, sec, era, city, title=None, sub=None, pop=None, cam=None, chapter=None):
    d = {"from": frm, "to": to, "seconds": sec, "era": era, "city_name": city}
    if title: d["title"] = title; d["sub"] = sub
    if pop is not None: d["population"] = pop
    if cam: d["camera"] = {"center": [cam[0], cam[1]], "dist_km": cam[2]}
    if chapter: d["chapter"] = chapter
    return d


TON = T("Tongva Land", "Tongva Toprakları"); SPA = T("Spanish California", "İspanyol Kaliforniyası")
MEX = T("Mexican California", "Meksika Kaliforniyası"); USA = T("American Frontier", "Amerikan Sınır Kenti")
RAIL = T("Railroad Boom", "Demiryolu Patlaması"); GROW = T("Greater Los Angeles", "Büyük Los Angeles")
MOD = T("20th Century", "20. Yüzyıl"); TODAY = T("Today", "Bugün")
YA = T("Yaanga", "Yaanga"); PUE = T("El Pueblo de los Ángeles", "El Pueblo de los Ángeles"); LA = T("Los Angeles", "Los Angeles")

# sourced anchors (year, people) — research.md; log-interpolated between them. 1850 census (1,610) is a known
# undercount and is not used as an anchor; 1844 → 1860 is interpolated.
ANCH = [(1781, 44), (1800, 315), (1810, 365), (1820, 650), (1830, 1300), (1836, 2228), (1840, 2240), (1844, 2497),
        (1860, 4385), (1870, 5728), (1880, 11183), (1890, 50395), (1900, 102479), (1910, 319198), (1920, 576673),
        (1930, 1238048), (1940, 1504277), (1950, 1970358), (1960, 2479015), (1970, 2816061), (1980, 2966850),
        (1990, 3485567), (2000, 3694820), (2010, 3792621), (2020, 3898747), (2025, 3839536), (2026, 3806201)]


def P(y):
    for (y0, p0), (y1, p1) in zip(ANCH, ANCH[1:]):
        if y0 <= y <= y1:
            u = (y - y0) / (y1 - y0); v = math.exp(math.log(p0) + (math.log(p1) - math.log(p0)) * u)
            return int(round(v, -1 if v < 10000 else (-2 if v < 100000 else -3))) if v >= 100 else int(round(v))
    raise ValueError(y)


PI = lambda a, b: [P(a), P(b)]
C0 = (34.0565, -118.2385)
S = [
 seg(1769, 1770.9, 12, TON, YA, T("Yaanga", "Yaanga"),
     T("2 August 1769: Portolà's Spanish expedition arrives at Yaanga, a large Tongva village",
       "2 Ağustos 1769: Portolà'nın İspanyol seferi büyük bir Tongva köyü olan Yaanga'ya ulaşır"),
     cam=(34.0560, -118.2380, 4.5), chapter=T("Tongva Yaanga", "Tongva Köyü Yaanga")),
 seg(1771, 1780.9, 12, TON, YA, T("Mission San Gabriel", "San Gabriel Misyonu"),
     T("8 September 1771: friars found Mission San Gabriel; floods soon move it to today's San Gabriel",
       "8 Eylül 1771: rahipler San Gabriel Misyonu'nu kurar; bir sel onu bugünkü San Gabriel'e taşıtır"),
     cam=(34.0700, -118.1700, 16.0)),
 seg(1781, 1781.9, 13, SPA, PUE, T("El Pueblo Is Founded", "El Pueblo Kuruluyor"),
     T("4 September 1781: 44 settlers in 11 families found a farming town beside Yaanga",
       "4 Eylül 1781: 11 aileden 44 yerleşimci, Yaanga'nın yanında bir tarım kasabası kurar"),
     pop=44, cam=(34.0570, -118.2385, 3.2), chapter=T("Spanish Pueblo", "İspanyol Kasabası")),
 seg(1782, 1799, 12, SPA, PUE, T("The Mother Ditch", "Ana Hendek"),
     T("Within a month of the founding, the Zanja Madre brings river water to the town and its fields",
       "Kuruluştan bir ay içinde Zanja Madre hendeği nehir suyunu kasabaya ve tarlalara taşır"),
     pop=PI(1782, 1799), cam=(34.0600, -118.2350, 3.6)),
 seg(1800, 1813, 7, SPA, PUE, pop=PI(1800, 1813), cam=(34.0570, -118.2385, 3.4)),
 seg(1814, 1817.9, 12, SPA, PUE, T("The Great Flood of 1815", "1815'in Büyük Seli"),
     T("1815: a great flood shifts the river, and the new church is moved to higher ground",
       "1815: büyük bir sel nehrin yatağını kaydırır; yeni kilise daha yüksek bir yere taşınır"),
     pop=PI(1814, 1817.9), cam=(34.0565, -118.2370, 3.0)),
 seg(1818, 1821.6, 12, SPA, PUE, T("The Ávila Adobe", "Ávila Kerpiç Evi"),
     T("1818: Francisco Ávila builds his adobe, today the oldest house in Los Angeles",
       "1818: Francisco Ávila kerpiç evini yapar; bugün Los Angeles'ın en eski evi"),
     pop=PI(1818, 1821.6), cam=(34.0572, -118.2380, 2.4)),
 seg(1821.7, 1834, 12, MEX, PUE, T("Mexican Los Angeles", "Meksikalı Los Angeles"),
     T("September 1821: Mexico wins independence; the Plaza church is dedicated in December 1822",
       "Eylül 1821: Meksika bağımsızlığını kazanır; Plaza kilisesi Aralık 1822'de açılır"),
     pop=PI(1821.7, 1834), cam=(34.0568, -118.2388, 2.8), chapter=T("Mexican Los Angeles", "Meksikalı Los Angeles")),
 seg(1835, 1844.9, 12, MEX, PUE, T("A Mexican City", "Bir Meksika Şehri"),
     T("1835: the Mexican Congress makes Los Angeles a city; about 2,230 people live here by 1836",
       "1835: Meksika Kongresi Los Angeles'ı şehir yapar; 1836'da burada yaklaşık 2.230 kişi yaşar"),
     pop=PI(1835, 1844.9), cam=(34.0565, -118.2390, 3.4)),
 seg(1845, 1846.9, 12, MEX, PUE, T("Yaanga Is Uprooted", "Yaanga Yerinden Ediliyor"),
     T("December 1845: Yaanga's people are moved across the river; the old village is razed in 1847",
       "Aralık 1845: Yaanga halkı nehrin doğusuna taşınır; eski köy 1847'de yerle bir edilir"),
     pop=PI(1845, 1846.9), cam=(34.0500, -118.2250, 4.2)),
 seg(1847, 1849.9, 12, USA, LA, T("Fort Moore", "Fort Moore"),
     T("13 January 1847: the Treaty of Cahuenga ends the fighting; on 4 July US troops open Fort Moore",
       "13 Ocak 1847: Cahuenga Antlaşması savaşı bitirir; 4 Temmuz'da ABD askerleri Fort Moore'u açar"),
     pop=PI(1847, 1849.9), cam=(34.0575, -118.2400, 2.6), chapter=T("American Los Angeles", "Amerikan Los Angeles'ı")),
 seg(1850, 1867.9, 12, USA, LA, T("An American City", "Bir Amerikan Şehri"),
     T("4 April 1850: Los Angeles is incorporated as a US city; 4,385 people live here in 1860",
       "4 Nisan 1850: Los Angeles bir ABD şehri olarak kurulur; 1860'ta burada 4.385 kişi yaşar"),
     pop=PI(1850, 1867.9), cam=(34.0540, -118.2420, 4.0)),
 seg(1868, 1875.9, 12, USA, LA, T("Rails to the Harbor", "Limana Raylar"),
     T("1869: the Los Angeles & San Pedro Railroad links the town to Banning's port at Wilmington",
       "1869: Los Angeles & San Pedro Demiryolu kasabayı Banning'in Wilmington limanına bağlar"),
     pop=PI(1868, 1875.9), cam=(33.9500, -118.2500, 20.0)),
 seg(1876, 1883.9, 12, RAIL, LA, T("The Golden Spike", "Altın Çivi"),
     T("5 September 1876: a golden spike at Lang's Station joins Los Angeles to the Southern Pacific",
       "5 Eylül 1876: Lang İstasyonu'nda çakılan altın çivi Los Angeles'ı Southern Pacific'e bağlar"),
     pop=PI(1876, 1883.9), cam=(34.0700, -118.2600, 14.0), chapter=T("The Railroad Boom", "Demiryolu Patlaması")),
 seg(1884, 1889.9, 12, RAIL, LA, T("The Boom of the 1880s", "1880'lerin Patlaması"),
     T("1885–1887: a railroad fare war brings newcomers; towns like Hollywood are laid out",
       "1885–1887: demiryolu bilet savaşı yeni gelenler getirir; Hollywood gibi kasabalar kurulur"),
     pop=PI(1884, 1889.9), cam=(34.0700, -118.2800, 16.0)),
 seg(1890, 1898.9, 12, RAIL, LA, T("Fifty Thousand", "Elli Bin"),
     T("1880–1890: the city grows from 11,183 to 50,395 people in ten years",
       "1880–1890: şehir on yılda 11.183'ten 50.395 kişiye çıkar"),
     pop=PI(1890, 1898.9), cam=(34.0500, -118.2600, 12.0)),
 seg(1899, 1900.9, 12, RAIL, LA, T("The Breakwater", "Dalgakıran"),
     T("1899: work begins on a breakwater at San Pedro; Los Angeles passes 100,000 people in 1900",
       "1899: San Pedro'da dalgakıran yapımı başlar; Los Angeles 1900'de 100.000 kişiyi geçer"),
     pop=PI(1899, 1900.9), cam=(33.9000, -118.2700, 30.0)),
 seg(1901, 1905.9, 12, MOD, LA, T("Angels Flight", "Angels Flight"),
     T("1901: the Angels Flight railway opens, carrying riders up Bunker Hill",
       "1901: Angels Flight füniküleri açılır ve yolcuları Bunker Hill'e taşır"),
     pop=PI(1901, 1905.9), cam=(34.0520, -118.2480, 5.0), chapter=T("Greater Los Angeles", "Büyük Los Angeles")),
 seg(1906, 1908.9, 12, MOD, LA, T("The Shoestring", "Ayakkabı Bağı"),
     T("End of 1906: the city annexes a long, narrow strip of land reaching south toward the harbor",
       "1906 sonu: şehir, limana doğru uzanan uzun ve dar bir şeridi topraklarına katar"),
     pop=PI(1906, 1908.9), cam=(33.9000, -118.2700, 34.0)),
 seg(1909, 1909.9, 12, MOD, LA, T("The Port Joins", "Liman Katılıyor"),
     T("28 August 1909: Wilmington and San Pedro consolidate with Los Angeles",
       "28 Ağustos 1909: Wilmington ve San Pedro Los Angeles ile birleşir"),
     pop=PI(1909, 1909.9), cam=(33.7700, -118.2700, 12.0)),
 seg(1910, 1912.9, 12, MOD, LA, T("Hollywood Joins", "Hollywood Katılıyor"),
     T("7 February 1910: Hollywood merges with Los Angeles to secure its water supply",
       "7 Şubat 1910: Hollywood, su ihtiyacını güvenceye almak için Los Angeles ile birleşir"),
     pop=PI(1910, 1912.9), cam=(34.0900, -118.3100, 8.0)),
 seg(1913, 1914.9, 12, MOD, LA, T("The Aqueduct", "Su Kemeri"),
     T("5 November 1913: 30,000 people watch Owens Valley water pour down the Cascades",
       "5 Kasım 1913: 30.000 kişi Owens Vadisi suyunun Cascades'ten akışını izler"),
     pop=PI(1913, 1914.9), cam=(34.1800, -118.4000, 30.0)),
 seg(1915, 1922.9, 12, MOD, LA, T("The Valley Joins", "Vadi Katılıyor"),
     T("May 1915: the San Fernando Valley joins the city, and Los Angeles doubles in size",
       "Mayıs 1915: San Fernando Vadisi şehre katılır ve Los Angeles'ın yüzölçümü iki katına çıkar"),
     pop=PI(1915, 1922.9), cam=(34.1500, -118.4200, 34.0)),
 seg(1923, 1924.9, 12, MOD, LA, T("Hollywoodland", "Hollywoodland"),
     T("1923: a $21,000 sign reading HOLLYWOODLAND goes up to sell a new housing tract",
       "1923: yeni bir konut projesini satmak için 21.000 dolarlık HOLLYWOODLAND tabelası dikilir"),
     pop=PI(1923, 1924.9), cam=(34.1050, -118.3200, 6.0)),
 seg(1925, 1927.9, 12, MOD, LA, T("Venice and Watts Join", "Venice ve Watts Katılıyor"),
     T("1926: the seaside city of Venice and the town of Watts both become part of Los Angeles",
       "1926: sahil kenti Venice ve Watts kasabası Los Angeles'a katılır"),
     pop=PI(1925, 1927.9), cam=(33.9900, -118.3500, 26.0)),
 seg(1928, 1931.9, 12, MOD, LA, T("City Hall", "Belediye Sarayı"),
     T("26 April 1928: the 138 m City Hall is dedicated, tallest in the city until 1966",
       "26 Nisan 1928: 138 m'lik Belediye Sarayı açılır; 1966'ya kadar şehrin en yüksek binası"),
     pop=PI(1928, 1931.9), cam=(34.0530, -118.2440, 3.6), chapter=T("Boomtown", "Patlama Kenti")),
 seg(1932, 1937.9, 12, MOD, LA, T("The 1932 Olympics", "1932 Olimpiyatları"),
     T("1932: the Olympic Games come to the Coliseum, completed in 1923 and enlarged for them",
       "1932: Olimpiyat Oyunları, 1923'te bitirilip onlar için büyütülen Coliseum'a gelir"),
     pop=PI(1932, 1937.9), cam=(34.0150, -118.2880, 3.6)),
 seg(1938, 1938.9, 12, MOD, LA, T("The Flood of 1938", "1938 Seli"),
     T("1938: a great flood; the river is later lined in concrete, a job finished in the 1960s",
       "1938: büyük bir sel; nehir sonradan betonla kaplanır, iş 1960'larda biter"),
     pop=PI(1938, 1938.9), cam=(34.0700, -118.2400, 12.0)),
 seg(1939, 1940.9, 12, MOD, LA, T("Union Station", "Union Station"),
     T("3 May 1939: Union Station opens, built on fill over the site of the original Chinatown",
       "3 Mayıs 1939: Union Station açılır; ilk Çin Mahallesi'nin yerine dökülen dolgu üstünde"),
     pop=PI(1939, 1940.9), cam=(34.0560, -118.2370, 2.6)),
 seg(1940.95, 1948.9, 12, MOD, LA, T("The First Freeway", "İlk Otoyol"),
     T("30 December 1940: the Arroyo Seco Parkway, the first freeway in the West, is dedicated",
       "30 Aralık 1940: Batı'nın ilk otoyolu Arroyo Seco Parkway açılır"),
     pop=PI(1940.95, 1948.9), cam=(34.0900, -118.2000, 12.0), chapter=T("Freeway City", "Otoyol Şehri")),
 seg(1949, 1956.9, 12, MOD, LA, T("HOLLYWOOD", "HOLLYWOOD"),
     T("1949: the sign loses its last four letters; in 1950 the Hollywood Freeway opens",
       "1949: tabela son dört harfini kaybeder; 1950'de Hollywood Otoyolu açılır"),
     pop=PI(1949, 1956.9), cam=(34.0950, -118.3000, 10.0)),
 seg(1957, 1961.9, 12, MOD, LA, T("The Height Limit Falls", "Yükseklik Sınırı Kalkıyor"),
     T("1957: the city drops its 150-foot height limit, and towers can finally rise downtown",
       "1957: şehir 46 metrelik yükseklik sınırını kaldırır; kuleler sonunda yükselebilir"),
     pop=PI(1957, 1961.9), cam=(34.0510, -118.2530, 4.0)),
 seg(1962, 1968.9, 12, MOD, LA, T("Dodger Stadium", "Dodger Stadyumu"),
     T("10 April 1962: Dodger Stadium opens in Chavez Ravine, whose last residents were evicted in 1959",
       "10 Nisan 1962: Dodger Stadyumu, son sakinleri 1959'da çıkarılan Chavez Ravine'de açılır"),
     pop=PI(1962, 1968.9), cam=(34.0700, -118.2420, 4.5)),
 seg(1969, 1983.9, 12, MOD, LA, T("Bunker Hill Rebuilt", "Bunker Hill Yeniden"),
     T("1969: Angels Flight is taken down as Bunker Hill is cleared; office towers rise in its place",
       "1969: Bunker Hill temizlenirken Angels Flight sökülür; yerine ofis kuleleri yükselir"),
     pop=PI(1969, 1983.9), cam=(34.0510, -118.2540, 3.4)),
 seg(1984, 1988.9, 12, MOD, LA, T("The 1984 Olympics", "1984 Olimpiyatları"),
     T("28 July 1984: the Games open at the Coliseum, the first stadium to host the Olympics twice",
       "28 Temmuz 1984: Oyunlar, Olimpiyatları iki kez ağırlayan ilk stadyum Coliseum'da başlar"),
     pop=PI(1984, 1988.9), cam=(34.0150, -118.2870, 4.0), chapter=T("Los Angeles Today", "Bugünün Los Angeles'ı")),
 seg(1989, 2002.9, 12, TODAY, LA, T("Tallest in the West", "Batı'nın En Yükseği"),
     T("1989: the 310 m U.S. Bank Tower becomes the tallest building in Los Angeles",
       "1989: 310 m'lik U.S. Bank Tower, Los Angeles'ın en yüksek binası olur"),
     pop=PI(1989, 2002.9), cam=(34.0510, -118.2560, 4.2)),
 seg(2003, 2016.9, 12, TODAY, LA, T("Walt Disney Concert Hall", "Walt Disney Konser Salonu"),
     T("23 October 2003: Frank Gehry's steel-clad Walt Disney Concert Hall opens on Bunker Hill",
       "23 Ekim 2003: Frank Gehry'nin çelik kaplı Walt Disney Konser Salonu Bunker Hill'de açılır"),
     pop=PI(2003, 2016.9), cam=(34.0540, -118.2520, 3.0)),
 seg(2017, 2019.9, 12, TODAY, LA, T("Wilshire Grand Center", "Wilshire Grand Center"),
     T("23 June 2017: the 335 m Wilshire Grand Center opens, the tallest tower in the city",
       "23 Haziran 2017: 335 m'lik Wilshire Grand Center açılır; şehrin en yüksek kulesi"),
     pop=PI(2017, 2019.9), cam=(34.0505, -118.2570, 4.0)),
 seg(2020, 2026, 16, TODAY, LA, T("Los Angeles Today", "Bugünün Los Angeles'ı"),
     T("From 44 settlers in 1781 to about 3.8 million Angelenos on some 500 square miles today",
       "1781'deki 44 yerleşimciden bugün 1.300 km²'ye yayılan yaklaşık 3,8 milyon Angelenoya"),
     pop=[3898747, 3806201], cam=(34.0400, -118.3200, 34.0)),
]
for s_ in S:   # pacing: titled segments 13.5 s (target ≈ 530 s with the cold open)
    if s_.get("title"): s_["seconds"] = 18 if s_["to"] == 2026 else 13.5

# ------------------------------------------------------------------ geography of growth (≈ reconstructions, research.md)
SMM = [(34.1100, -118.2750), (34.1300, -118.2800), (34.1400, -118.3200), (34.1350, -118.3800), (34.1300, -118.4400),
       (34.1350, -118.5200), (34.1450, -118.6000), (34.1500, -118.7000), (34.0350, -118.7000), (34.0400, -118.5600),
       (34.0500, -118.5200), (34.0750, -118.4700), (34.0900, -118.4200), (34.0980, -118.3800), (34.1070, -118.3400),
       (34.1080, -118.3000)]   # Santa Monica Mts + Griffith Park (≈)
SGM = [(34.2700, -118.7000), (34.3000, -118.5300), (34.3300, -118.4200), (34.2800, -118.3300), (34.2300, -118.2300),
       (34.2100, -118.1300), (34.2000, -118.0200), (34.3600, -118.0200), (34.3600, -118.7000)]                      # San Gabriel / Santa Susana foothills (≈)
VERDUGO = [(34.1600, -118.2700), (34.2100, -118.2300), (34.2300, -118.2200), (34.2000, -118.2600), (34.1700, -118.2900)]
ELYSIAN = oval((34.0780, -118.2430), 900, 600, rot_deg=40)
PUEBLO1 = oval(PLAZA, 230, 170, rot_deg=45, n=12)
PUEBLO2 = oval((34.0560, -118.2390), 520, 380, rot_deg=45, n=14)
TOWN1850 = [(34.0600, -118.2440), (34.0610, -118.2360), (34.0480, -118.2320), (34.0440, -118.2440), (34.0520, -118.2500)]
CITY1890 = [(34.0750, -118.2550), (34.0750, -118.2200), (34.0450, -118.2050), (34.0150, -118.2400), (34.0150, -118.2900),
            (34.0450, -118.2950), (34.0650, -118.2800)]
BASIN = [(34.0950, -118.4100), (34.0950, -118.2700), (34.1150, -118.2000), (34.0800, -118.1500), (34.0000, -118.1500),
         (33.9200, -118.1700), (33.9000, -118.3200), (33.9500, -118.4000), (34.0200, -118.4300)]
WESTSIDE = [(34.0750, -118.5000), (34.0850, -118.4100), (34.0200, -118.4300), (33.9500, -118.4000), (33.9300, -118.4300),
            (33.9800, -118.4800), (34.0300, -118.5200)]
SOUTHBAY = [(33.9300, -118.4300), (33.9000, -118.3200), (33.9200, -118.1700), (33.8500, -118.1000), (33.7700, -118.1500),
            (33.7700, -118.2400), (33.8000, -118.3300), (33.8200, -118.3900)]
HARBOR = [(33.7950, -118.2400), (33.7950, -118.3050), (33.7350, -118.3200), (33.7150, -118.2950), (33.7300, -118.2500)]
SGV = [(34.1700, -118.2000), (34.1800, -118.0200), (34.0200, -118.0200), (34.0000, -118.1500), (34.0800, -118.1500),
       (34.1150, -118.2000)]
VALLEY = [(34.1450, -118.6400), (34.2700, -118.6400), (34.3000, -118.5300), (34.3200, -118.4300), (34.2800, -118.3300),
          (34.2100, -118.2700), (34.1500, -118.2800), (34.1350, -118.3700), (34.1500, -118.5300)]
DT_TOWERS = [(34.0560, -118.2560), (34.0530, -118.2470), (34.0470, -118.2520), (34.0480, -118.2640), (34.0520, -118.2640)]
WILSHIRE_COR = [(34.0640, -118.3700), (34.0640, -118.2700), (34.0560, -118.2700), (34.0560, -118.3700)]
HOLES = [L(SMM), L(ELYSIAN)]
# Pacific stripes in the elevation tiles → water (computed once by _coast_fix.py from the first geo.json)
_cf = os.path.join(HERE, "_coast_fix.json")
COAST_FIX = [{"op": "water", "poly": p} for p in json.load(open(_cf))] if os.path.exists(_cf) else []


def D(name, style, poly, frm, to, dens, grain, grow, **kw):
    d = {"name": name, "style": style, "poly": L(poly), "from": frm, "to": to, "density": dens, "grain_m": grain,
         "grow_from": list(grow)}
    d.update(kw); return d


districts = [
 D("Yaanga village (≈)", "celtic", oval(YAANGA, 220, 160, n=12), 1769, 1770, 0.3, 45, YAANGA, fade=[1836, 1848, 0.0]),
 D("Pueblo (≈)", "ancient", PUEBLO1, 1781, 1800, 0.45, 45, PLAZA),
 D("Pueblo after the flood (≈)", "ancient", PUEBLO2, 1815, 1848, 0.5, 45, CHURCH, holes=[L(oval(PLAZA, 60, 45, n=8))]),
 D("Mission San Gabriel (≈)", "ancient", oval(MISSION, 260, 200, n=10), 1776, 1800, 0.35, 50, MISSION),
 D("American town (≈)", "victorian", TOWN1850, 1850, 1880, 0.6, 55, (34.0540, -118.2420), grid_deg=40,
   holes=[L(oval(PLAZA, 60, 45, n=8))]),
 D("Wilmington (≈)", "victorian", oval(WILMINGTON, 900, 600), 1858, 1900, 0.35, 90, WILMINGTON),
 D("San Pedro (≈)", "victorian", oval(SANPEDRO, 1200, 900), 1882, 1910, 0.35, 90, SANPEDRO),
 D("Boom-era city (≈)", "victorian", CITY1890, 1884, 1905, 0.7, 80, (34.0500, -118.2450), grid_deg=40,
   holes=[L(TOWN1850), L(ELYSIAN)]),
 D("Hollywood (≈)", "suburb", oval(HOLLYWOOD, 2200, 1300), 1887, 1920, 0.55, 110, HOLLYWOOD, holes=[L(SMM)]),
 D("Lankershim / North Hollywood (≈)", "suburb", oval(NOHO, 1500, 1200), 1887, 1925, 0.35, 140, NOHO),
 D("Highland Park (≈)", "suburb", oval(HIGHLAND, 1400, 1000), 1890, 1915, 0.45, 120, HIGHLAND),
 D("Venice (≈)", "suburb", oval(VENICE, 1300, 900, rot_deg=40), 1905, 1925, 0.5, 110, VENICE),
 D("Watts (≈)", "suburb", oval(WATTS, 1500, 1200), 1902, 1930, 0.45, 130, WATTS),
 D("Van Nuys (≈)", "suburb", oval(VANNUYS, 1500, 1200), 1911, 1930, 0.4, 140, VANNUYS),
 D("Owensmouth / Canoga Park (≈)", "suburb", oval(CANOGA, 1200, 900), 1912, 1935, 0.35, 150, CANOGA),
 D("Pasadena and the San Gabriel Valley (≈, outside the city)", "suburb", SGV, 1885, 1960, 0.55, 130, (34.1450, -118.1400),
   holes=HOLES + [L(SGM), L(oval(HIGHLAND, 1400, 1000))]),
 D("The basin: South and Central LA (≈)", "suburb", BASIN, 1900, 1940, 0.65, 95, (34.0450, -118.2500),
   holes=HOLES + [L(CITY1890), L(oval(HOLLYWOOD, 2200, 1300)), L(oval(WATTS, 1500, 1200)), L(oval(COLISEUM, 500, 400, n=10)),
                  L(oval(LABREA, 250, 200, n=8))]),
 D("Westside (≈, incl. Santa Monica and Beverly Hills)", "suburb", WESTSIDE, 1910, 1955, 0.6, 110, (34.0300, -118.4400),
   holes=HOLES + [L(oval(VENICE, 1300, 900, rot_deg=40))]),
 D("South Bay and Long Beach (≈, mostly outside the city)", "suburb", SOUTHBAY, 1910, 1960, 0.55, 130, (33.8500, -118.2500)),
 D("Harbor communities (≈)", "suburb", HARBOR, 1910, 1955, 0.45, 160, (33.7600, -118.2800),
   holes=[L(oval(SANPEDRO, 1200, 900)), L(oval(WILMINGTON, 900, 600))]),
 D("San Fernando Valley (≈)", "suburb", VALLEY, 1940, 1975, 0.6, 135, (34.1800, -118.4400),
   holes=[L(SGM), L(VERDUGO), L(oval(NOHO, 1500, 1200)), L(oval(VANNUYS, 1500, 1200)), L(oval(CANOGA, 1200, 900))]),
 D("Downtown office core (≈)", "modern", CITY1890, 1905, 1930, 0.5, 90, (34.0480, -118.2500), grid_deg=40,
   holes=[L(ELYSIAN), L(oval(DODGER, 450, 350, n=10))]),
 D("Wilshire corridor (≈)", "modern", WILSHIRE_COR, 1925, 1990, 0.45, 130, (34.0600, -118.2900),
   holes=[L(oval(LABREA, 250, 200, n=8))]),
 D("Downtown towers", "highrise", DT_TOWERS, 1960, 2017, 0.35, 110, (34.0510, -118.2550)),
]

landmarks = [
 {"type": "church", "name": T("Mission San Gabriel", "San Gabriel Misyonu"), "at": list(MISSION), "built": 1776, "rise_s": 5,
  "size_m": [50, 14, 14], "scale": 2.5, "colors": {"wall": "#e6dccb", "roof": "#a5543a"}},
 {"type": "church", "name": T("Plaza Church", "Plaza Kilisesi"), "at": list(CHURCH), "built": 1822.9, "rise_s": 5,
  "size_m": [36, 12, 13], "rot_deg": 45, "scale": 1.4, "colors": {"wall": "#efe7d8", "roof": "#a5543a"}},
 {"type": "box", "name": T("Ávila Adobe", "Ávila Kerpiç Evi"), "at": list(AVILA), "built": 1818, "rise_s": 4,
  "size_m": [30, 14, 5], "rot_deg": 45, "scale": 1.3, "colors": {"wall": "#cfa77d", "roof": "#7a5a3c"}},
 {"type": "fort", "name": T("Fort Moore", "Fort Moore"), "at": list(FORT_MOORE), "built": 1847.5, "removed": 1853, "rise_s": 4,
  "size_m": [70, 40, 5], "colors": {"wall": "#a98f6d"}},
 {"type": "palace", "name": T("Pico House", "Pico House"), "at": list(PICO), "built": 1870, "rise_s": 4,
  "size_m": [38, 36, 16], "rot_deg": 45, "colors": {"wall": "#e3d7bd", "roof": "#6e767c"}},
 {"type": "harbor", "name": T("Port of Los Angeles", "Los Angeles Limanı"), "at": list(PORT), "built": 1907.9, "rise_s": 5,
  "size_m": [600, 300, 12]},
 {"type": "spire_tower", "name": T("City Hall", "Belediye Sarayı"), "at": list(CITY_HALL), "built": 1928.3, "rise_s": 8,
  "size_m": [45, 45, 138], "scale": 1.3, "colors": {"wall": "#ece6d8"}},
 {"type": "stadium", "name": T("Memorial Coliseum", "Memorial Coliseum"), "at": list(COLISEUM), "built": 1923.3, "rise_s": 5,
  "size_m": [300, 220, 30], "colors": {"wall": "#c9b28f"}},
 {"type": "box", "name": T("Hollywood Sign", "Hollywood Tabelası"), "at": list(SIGN), "built": 1923.5, "rise_s": 4,
  "size_m": [110, 3, 14], "scale": 2.2, "colors": {"wall": "#ffffff", "roof": "#ffffff"}},
 {"type": "station", "name": T("Union Station", "Union Station"), "at": list(UNION), "built": 1939.3, "rise_s": 6,
  "size_m": [200, 70, 25], "rot_deg": 0, "colors": {"wall": "#e8dcc4", "roof": "#a5543a"}},
 {"type": "stadium", "name": T("Dodger Stadium", "Dodger Stadyumu"), "at": list(DODGER), "built": 1962.27, "rise_s": 6,
  "size_m": [280, 250, 30], "colors": {"wall": "#d8dde2"}},
 {"type": "skyscraper", "name": T("Aon Center", "Aon Center"), "at": list(AON), "built": 1973, "rise_s": 6,
  "size_m": [55, 40, 262], "rot_deg": 40, "colors": {"wall": "#3d4650"}},
 {"type": "skyscraper", "name": T("Wells Fargo Tower", "Wells Fargo Tower"), "at": list(WELLS), "built": 1982, "rise_s": 6,
  "size_m": [50, 50, 226], "rot_deg": 40, "colors": {"wall": "#9a6f55"}},
 {"type": "skyscraper", "name": T("U.S. Bank Tower", "U.S. Bank Tower"), "at": list(USBANK), "built": 1988.5, "rise_s": 8,
  "size_m": [55, 55, 310], "colors": {"wall": "#b8b2a6"}},
 {"type": "skyscraper", "name": T("Gas Company Tower", "Gas Company Tower"), "at": list(GASCO), "built": 1990, "rise_s": 6,
  "size_m": [50, 45, 228], "rot_deg": 40, "colors": {"wall": "#5f7d93"}},
 {"type": "skyscraper", "name": T("Two California Plaza", "Two California Plaza"), "at": list(TWOCAL), "built": 1991, "rise_s": 6,
  "size_m": [50, 45, 229], "rot_deg": 40, "colors": {"wall": "#8a9aa6"}},
 {"type": "dome_arena", "name": T("Walt Disney Concert Hall", "Walt Disney Konser Salonu"), "at": list(DISNEY), "built": 2003.8,
  "rise_s": 6, "size_m": [110, 90, 30], "colors": {"wall": "#d9dde0", "roof": "#e6e9eb"}},
 {"type": "spire_tower", "name": T("Wilshire Grand Center", "Wilshire Grand Center"), "at": list(WILSHIRE), "built": 2016.5,
  "rise_s": 8, "size_m": [60, 45, 335], "colors": {"wall": "#8fb2c8"}},
]

roads = [
 {"name": "Zanja Madre (≈ course)", "path": L([(34.0720, -118.2290), (34.0660, -118.2310), (34.0610, -118.2350), (34.0575, -118.2378)]),
  "from": 1781.5, "to": 1904, "kind": "road", "width_m": 5},
 {"name": "Los Angeles & San Pedro Railroad (≈)", "path": L([(34.0480, -118.2350), (34.0000, -118.2400), (33.9300, -118.2400),
  (33.8600, -118.2350), (33.7900, -118.2450), (33.7800, -118.2600)]), "from": 1869, "kind": "rail", "width_m": 10},
 {"name": "Southern Pacific north (≈)", "path": L([(34.0550, -118.2340), (34.0800, -118.2250), (34.1200, -118.2600),
  (34.1800, -118.3100), (34.2300, -118.3900), (34.2900, -118.4400), (34.3500, -118.4800)]), "from": 1876.7, "kind": "rail", "width_m": 10},
 {"name": "Arroyo Seco Parkway (≈)", "path": L([(34.0655, -118.2330), (34.0800, -118.2200), (34.0960, -118.2050), (34.1100, -118.1900),
  (34.1150, -118.1700), (34.1300, -118.1500)]), "from": 1940.99, "kind": "motorway", "width_m": 30},
 {"name": "Hollywood Freeway (≈)", "path": L([(34.0560, -118.2380), (34.0640, -118.2550), (34.0750, -118.2850), (34.0900, -118.3150),
  (34.1100, -118.3350), (34.1350, -118.3550)]), "from": 1950.95, "kind": "motorway", "width_m": 30},
]


def lab(en, tr, at, frm=None, to=None, kind="place", now=None, lift=None):
    d = {"text": T(en, tr), "at": list(at), "kind": kind}
    if frm is not None: d["from"] = frm
    if to is not None: d["to"] = to
    if now: d["now"] = T(*now)
    if lift: d["lift_m"] = lift
    return d


labels = [
 lab("LOS ANGELES RIVER", "LOS ANGELES NEHRİ", (34.0450, -118.2240), kind="water", to=1849.9),
 lab("PACIFIC OCEAN", "BÜYÜK OKYANUS", (33.9300, -118.5600), kind="water", frm=1906),
 lab("SANTA MONICA MOUNTAINS", "SANTA MONICA DAĞLARI", (34.1100, -118.4800), kind="region", frm=1910, to=1922.9),
 lab("Yaanga", "Yaanga", YAANGA, 1769, 1780.9, now=("beside Union Station, under the 101", "Union Station yanı, 101 otoyolu altı")),
 lab("Mission San Gabriel", "San Gabriel Misyonu", MISSION, 1771, 1780.9),
 lab("Pueblo plaza", "Kasaba meydanı", PLAZA, 1781, 1799, lift=10),
 lab("Zanja Madre", "Zanja Madre", (34.0660, -118.2310), 1782, 1799, now=("LA State Historic Park", "LA State Historic Park")),
 lab("Plaza Church", "Plaza Kilisesi", CHURCH, 1821.7, 1834, lift=20),
 lab("Ávila Adobe", "Ávila Kerpiç Evi", AVILA, 1818, 1821.6, lift=15),
 lab("Pueblito", "Pueblito", BOYLE, 1845, 1846.9, now=("Boyle Heights", "Boyle Heights")),
 lab("Fort Moore", "Fort Moore", FORT_MOORE, 1847, 1849.9, now=("Fort Moore Pioneer Memorial", "Fort Moore Öncüler Anıtı"), lift=15),
 lab("Rancho La Brea", "Rancho La Brea", LABREA, 1850, 1875.9, now=("La Brea Tar Pits", "La Brea Katran Çukurları")),
 lab("Wine Street", "Wine Street", (34.0577, -118.2376), 1850, 1867.9, now=("Olvera Street", "Olvera Sokağı"), lift=10),
 lab("Wilmington", "Wilmington", WILMINGTON, 1868, 1875.9),
 lab("Agricultural Park", "Agricultural Park", COLISEUM, 1876, 1883.9, now=("Exposition Park", "Exposition Park")),
 lab("Old Chinatown", "Eski Çin Mahallesi", UNION, 1938, 1938.9, now=("Union Station", "Union Station"), lift=10),
 lab("Hollywood", "Hollywood", HOLLYWOOD, 1887, 1898.9),
 lab("Toluca", "Toluca", NOHO, 1887, 1895.9, now=("North Hollywood", "North Hollywood")),
 lab("San Pedro", "San Pedro", SANPEDRO, 1899, 1900.9),
 lab("Bunker Hill", "Bunker Hill", ANGELS, 1901, 1905.9, lift=20),
 lab("Wilmington", "Wilmington", WILMINGTON, 1909, 1909.9),
 lab("San Pedro", "San Pedro", SANPEDRO, 1909, 1909.9),
 lab("Hollywood", "Hollywood", HOLLYWOOD, 1910, 1912.9),
 lab("SAN FERNANDO VALLEY", "SAN FERNANDO VADİSİ", (34.2100, -118.4600), kind="region", frm=1913, to=1922.9),
 lab("Lankershim", "Lankershim", NOHO, 1915, 1922.9),
 lab("Van Nuys", "Van Nuys", VANNUYS, 1915, 1922.9),
 lab("Owensmouth", "Owensmouth", CANOGA, 1915, 1922.9, now=("Canoga Park", "Canoga Park")),
 lab("HOLLYWOODLAND", "HOLLYWOODLAND", SIGN, 1923, 1924.9, now=("the Hollywood Sign", "Hollywood Tabelası"), lift=40),
 lab("Venice", "Venice", VENICE, 1925, 1927.9),
 lab("Watts", "Watts", WATTS, 1925, 1927.9),
 lab("City Hall", "Belediye Sarayı", CITY_HALL, 1928, 1931.9, lift=200),
 lab("Coliseum", "Coliseum", COLISEUM, 1932, 1937.9, lift=40),
 lab("Union Station", "Union Station", UNION, 1939, 1940.9, lift=40),
 lab("Arroyo Seco Parkway", "Arroyo Seco Parkway", (34.0960, -118.2050), 1941, 1948.9,),
 lab("HOLLYWOOD", "HOLLYWOOD", SIGN, 1949, 1956.9, lift=40),
 lab("Chavez Ravine", "Chavez Ravine", DODGER, 1950, 1961.9, now=("Dodger Stadium", "Dodger Stadyumu")),
 lab("Dodger Stadium", "Dodger Stadyumu", DODGER, 1962, 1968.9, lift=40),
 lab("Bunker Hill", "Bunker Hill", ANGELS, 1969, 1983.9, lift=300),
 lab("Coliseum", "Coliseum", COLISEUM, 1984, 1988.9, lift=40),
 lab("U.S. Bank Tower", "U.S. Bank Tower", USBANK, 1989, 2002.9, lift=420),
 lab("Disney Hall", "Disney Salonu", DISNEY, 2003, 2016.9, lift=60),
 lab("Wilshire Grand", "Wilshire Grand", WILSHIRE, 2017, 2019.9, lift=440),
 lab("Downtown", "Downtown", DOWNTOWN, 2020, lift=60),
 lab("Hollywood", "Hollywood", HOLLYWOOD, 2020),
 lab("Venice", "Venice", VENICE, 2020),
 lab("Watts", "Watts", WATTS, 2020),
 lab("Highland Park", "Highland Park", HIGHLAND, 2020),
 lab("North Hollywood", "North Hollywood", NOHO, 2020),
 lab("Van Nuys", "Van Nuys", VANNUYS, 2020),
 lab("Canoga Park", "Canoga Park", CANOGA, 2020),
 lab("San Pedro", "San Pedro", SANPEDRO, 2020),
 lab("Wilmington", "Wilmington", WILMINGTON, 2020),
]

city = {
 "slug": "los-angeles", "seed": 1781, "long_ok": True,
 "name": T("Los Angeles", "Los Angeles"),
 "intro": T("245 Years in 8 Minutes", "8 Dakikada 245 Yıl"), "intro_seconds": 3,
 "cold_open": {"seconds": 7, "hold": 4.5, "kicker": T("245 years · from El Pueblo to megacity", "245 yıl · El Pueblo'dan megakente"),
               "camera": {"center": [34.0500, -118.2700], "dist_km": 16.0}},
 "people_notes": True,
 "closing_question": T("When did your family's story in Los Angeles begin?", "Ailenizin Los Angeles hikâyesi hangi yıl başladı?"),
 "music": {"style": "eras"},
 "geo": {"bbox": [33.66, -118.74, 34.36, -118.0], "cell_m": 120, "core_bbox": [33.99, -118.33, 34.12, -118.18], "core_cell_m": 30,
         "rivers_keep": ["Los Angeles River"], "lakes_from": 1900},
 "geo_edits": COAST_FIX,
 "view": {"azimuth_deg": 0, "pitch_deg": 46, "fov": 34},
 "render": {"vertical_exaggeration": 2.0},
 "segments": S,
 "districts": districts,
 "roads": roads, "landmarks": landmarks,
 "open_spaces": [
  {"name": "Santa Monica Mountains and Griffith Park (≈)", "poly": L(SMM)},
  {"name": "Elysian Park hills (≈)", "poly": L(ELYSIAN)},
  {"name": "Exposition Park (≈)", "poly": L(oval(COLISEUM, 500, 400, n=10))},
  {"name": "Hancock Park / La Brea Tar Pits (≈)", "poly": L(oval(LABREA, 250, 200, n=8))},
  {"name": "Plaza (≈)", "poly": L(oval(PLAZA, 60, 45, n=8))},
 ],
 "labels": labels,
 "youtube": {
  "title": T("Los Angeles: 245 Years in 8 Minutes (3D Timelapse, No AI)", "Los Angeles: 8 Dakikada 245 Yıl (3D Timelapse, Yapay Zekâ Yok)"),
  "description": T(
   "In 1781, 44 settlers in 11 families founded a small farming town beside Yaanga, a Tongva village on the Los Angeles River. "
   "Watch the pueblo dig its Zanja Madre, survive the flood of 1815, become Mexican in 1821 and American in 1847–1850. Then the "
   "railroads arrive, the 1880s boom lays out towns like Hollywood, the city swallows the harbor in 1909, Hollywood in 1910 and the "
   "San Fernando Valley in 1915 after the aqueduct brings Owens Valley water. City Hall, the Coliseum, Union Station, the first "
   "freeway, Dodger Stadium and the downtown towers follow — up to the Wilshire Grand Center and about 3.8 million Angelenos today, "
   "with the year and the population on screen.",
   "1781'de 11 aileden 44 yerleşimci, Los Angeles Nehri kıyısındaki Tongva köyü Yaanga'nın yanında küçük bir tarım kasabası kurdu. "
   "Kasabanın Zanja Madre'yi kazmasını, 1815 selini atlatmasını, 1821'de Meksikalı, 1847–1850'de Amerikalı olmasını izleyin. Sonra "
   "demiryolları gelir, 1880'lerin patlaması Hollywood gibi kasabalar kurar, şehir 1909'da limanı, 1910'da Hollywood'u ve su kemeri "
   "Owens Vadisi suyunu getirdikten sonra 1915'te San Fernando Vadisi'ni topraklarına katar. Belediye Sarayı, Coliseum, Union Station, "
   "ilk otoyol, Dodger Stadyumu ve şehir merkezinin kuleleri gelir — Wilshire Grand Center'a ve bugünkü yaklaşık 3,8 milyon Angelenoya "
   "kadar; yıl ve nüfus ekranda."),
  "tags": ["los angeles history", "history of los angeles", "el pueblo de los angeles", "3d timelapse", "city evolution",
           "how los angeles grew", "los angeles timelapse", "hollywood history", "san fernando valley", "la history",
           "olvera street", "downtown los angeles", "urban history", "no ai"],
  "hashtags": ["#LosAngeles", "#History", "#Timelapse"],
  "playlist": T("Cities of North America", "Kuzey Amerika Şehirleri"),
  "playlist_desc": T("North American cities rebuilt in 3D, from the first house to the skyline.", "Kuzey Amerika şehirleri 3D olarak, ilk evden siluete."),
  "thumb": {"line1": T("Los Angeles", "Los Angeles"), "line2": T("1781 → TODAY", "1781 → BUGÜN"),
            "line3": T("From El Pueblo to megacity", "El Pueblo'dan megakente"),
            "extra": "&pitch=34&az=0&cam=34.0520,-118.2520,6.0", "style": "v2"},
 },
 "sources": [],
}
total = sum(s_["seconds"] for s_ in S) + city["cold_open"]["seconds"]
mins = round(total / 60)
city["intro"] = T(f"245 Years in {mins} Minutes", f"{mins} Dakikada 245 Yıl")
city["youtube"]["title"] = T(f"Los Angeles: 245 Years in {mins} Minutes (3D Timelapse, No AI)",
                             f"Los Angeles: {mins} Dakikada 245 Yıl (3D Timelapse, Yapay Zekâ Yok)")
city["sources"] = json.load(open(os.path.join(HERE, "_sources.json")))
json.dump(city, open(os.path.join(HERE, "city.json"), "w"), ensure_ascii=False, indent=1)
print("segments", len(S), "duration", total, "s =", f"{int(total) // 60}:{int(total) % 60:02d}")
