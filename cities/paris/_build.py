"""Builds cities/paris/city.json. Every date/figure is from research.md (sources listed there).
Run: python3 cities/paris/_build.py"""
import json, math, os

T = lambda en, tr: {"en": en, "tr": tr}
HERE = os.path.dirname(os.path.abspath(__file__))
rect = lambda s, w, n, e: [(s, w), (n, w), (n, e), (s, e)]


def L(pts):
    return [[round(a, 5), round(b, 5)] for a, b in pts]


# ------------------------------------------------------------------ geography (lat, lon); ≈ traces, see research.md
CITE = [(48.8570, 2.3412), (48.8567, 2.3455), (48.8556, 2.3490), (48.8541, 2.3512), (48.8526, 2.3513), (48.8529, 2.3480),
        (48.8540, 2.3446), (48.8556, 2.3417)]
CITE_EAST_WALL = [(48.8563, 2.3458), (48.8553, 2.3492), (48.8539, 2.3512), (48.8527, 2.3511), (48.8530, 2.3482), (48.8536, 2.3458),
                  (48.8563, 2.3458)]
LUTETIA = [(48.8528, 2.3432), (48.8526, 2.3490), (48.8505, 2.3508), (48.8470, 2.3515), (48.8440, 2.3505), (48.8416, 2.3478),
           (48.8411, 2.3422), (48.8430, 2.3388), (48.8470, 2.3378), (48.8505, 2.3398)]
# Wall of Philip Augustus (1190–1213), river to river, through the gates in research.md
PA_R = [(48.8590, 2.3378), (48.8604, 2.3392), (48.8615, 2.3405), (48.8630, 2.3428), (48.8642, 2.3445), (48.8648, 2.3462),
        (48.8643, 2.3500), (48.8627, 2.3533), (48.8607, 2.3560), (48.8588, 2.3600), (48.8567, 2.3615), (48.8552, 2.3620),
        (48.8535, 2.3608), (48.8521, 2.3600)]
PA_L = [(48.8574, 2.3372), (48.8558, 2.3383), (48.8540, 2.3392), (48.8522, 2.3390), (48.8508, 2.3393), (48.8492, 2.3402),
        (48.8480, 2.3412), (48.8470, 2.3448), (48.8458, 2.3462), (48.8448, 2.3488), (48.8455, 2.3510), (48.8475, 2.3518),
        (48.8490, 2.3530), (48.8504, 2.3551)]
RB_SHORE_PA = [(48.8521, 2.3600), (48.8540, 2.3540), (48.8560, 2.3490), (48.8575, 2.3440), (48.8588, 2.3390)]
LB_SHORE_PA = [(48.8504, 2.3551), (48.8515, 2.3510), (48.8527, 2.3470), (48.8545, 2.3430), (48.8565, 2.3385)]
PA_RB = PA_R + RB_SHORE_PA[1:]
PA_LB = PA_L + LB_SHORE_PA[1:]
# Wall of Charles V (1356–1383), right bank
CV = [(48.8603, 2.3313), (48.8625, 2.3330), (48.8642, 2.3360), (48.8657, 2.3412), (48.8672, 2.3470), (48.8690, 2.3528),
      (48.8693, 2.3590), (48.8672, 2.3635), (48.8645, 2.3660), (48.8605, 2.3680), (48.8560, 2.3690), (48.8533, 2.3692),
      (48.8512, 2.3660), (48.8497, 2.3628)]
CV_RB = CV + [(48.8515, 2.3590), (48.8540, 2.3540), (48.8560, 2.3490), (48.8578, 2.3430), (48.8592, 2.3370)]
# Louis XIII extension (1633–1636), from the Seine at the Tuileries to the Porte Saint-Denis
L13 = [(48.8645, 2.3212), (48.8668, 2.3225), (48.8695, 2.3245), (48.8706, 2.3290), (48.8712, 2.3340), (48.8716, 2.3400),
       (48.8710, 2.3460), (48.8702, 2.3510), (48.8692, 2.3528)]
WEST_RB = L13 + [(48.8672, 2.3470), (48.8657, 2.3412), (48.8642, 2.3360), (48.8625, 2.3330), (48.8603, 2.3313), (48.8625, 2.3255)]
ILE_SL = [(48.8530, 2.3545), (48.8524, 2.3585), (48.8510, 2.3608), (48.8502, 2.3600), (48.8509, 2.3565), (48.8521, 2.3542)]
FBG_L = [(48.8574, 2.3372), (48.8580, 2.3300), (48.8585, 2.3220), (48.8560, 2.3180), (48.8510, 2.3200), (48.8470, 2.3260),
         (48.8440, 2.3330), (48.8425, 2.3420), (48.8420, 2.3520), (48.8440, 2.3580), (48.8475, 2.3600), (48.8504, 2.3551),
         (48.8490, 2.3530), (48.8455, 2.3510), (48.8448, 2.3488), (48.8470, 2.3448), (48.8492, 2.3402), (48.8540, 2.3392)]
# Wall of the Farmers-General (1784–1791) along the later boulevards
FG_R = [(48.8558, 2.2870), (48.8600, 2.2885), (48.8650, 2.2905), (48.8700, 2.2935), (48.8738, 2.2950), (48.8770, 2.2995),
        (48.8800, 2.3080), (48.8825, 2.3175), (48.8835, 2.3270), (48.8822, 2.3380), (48.8835, 2.3500), (48.8842, 2.3600),
        (48.8830, 2.3700), (48.8770, 2.3735), (48.8720, 2.3770), (48.8660, 2.3830), (48.8590, 2.3895), (48.8530, 2.3945),
        (48.8483, 2.3960), (48.8430, 2.3985), (48.8395, 2.3920), (48.8382, 2.3800)]
FG_L = [(48.8362, 2.3740), (48.8340, 2.3660), (48.8318, 2.3580), (48.8310, 2.3555), (48.8318, 2.3450), (48.8330, 2.3380),
        (48.8338, 2.3320), (48.8395, 2.3260), (48.8410, 2.3200), (48.8420, 2.3140), (48.8450, 2.3090), (48.8490, 2.2990),
        (48.8530, 2.2900), (48.8543, 2.2878)]
FG_POLY = FG_R + FG_L
# Thiers wall (1841–1846) along today's Boulevards des Maréchaux
TH_R = [(48.8305, 2.3885), (48.8355, 2.4040), (48.8410, 2.4110), (48.8470, 2.4105), (48.8560, 2.4100), (48.8645, 2.4085),
        (48.8740, 2.4045), (48.8830, 2.3990), (48.8885, 2.3925), (48.8960, 2.3880), (48.8985, 2.3700), (48.8985, 2.3590),
        (48.8975, 2.3450), (48.8960, 2.3300), (48.8945, 2.3135), (48.8900, 2.3000), (48.8860, 2.2930), (48.8810, 2.2860),
        (48.8780, 2.2830), (48.8715, 2.2765), (48.8610, 2.2690), (48.8530, 2.2620), (48.8475, 2.2585), (48.8400, 2.2570),
        (48.8375, 2.2625), (48.8392, 2.2680)]
TH_L = [(48.8275, 2.3830), (48.8230, 2.3720), (48.8215, 2.3640), (48.8190, 2.3595), (48.8195, 2.3480), (48.8225, 2.3370),
        (48.8235, 2.3255), (48.8255, 2.3140), (48.8275, 2.3055), (48.8305, 2.2950), (48.8325, 2.2875), (48.8350, 2.2790),
        (48.8376, 2.2722)]
TH_POLY = TH_R + list(reversed(TH_L))
C0 = (48.8566, 2.3440)
PERI = [(C0[0] + (a - C0[0]) * 1.045, C0[1] + (b - C0[1]) * 1.045) for a, b in TH_POLY]
PERI = PERI + [PERI[0]]
BOULOGNE = [(48.8780, 2.2540), (48.8740, 2.2700), (48.8600, 2.2660), (48.8480, 2.2560), (48.8460, 2.2420), (48.8560, 2.2360),
            (48.8700, 2.2420)]
VINCENNES = [(48.8470, 2.4200), (48.8450, 2.4500), (48.8380, 2.4700), (48.8250, 2.4600), (48.8240, 2.4350), (48.8320, 2.4180)]
LUXEMBOURG = rect(48.8440, 2.3330, 48.8490, 2.3400)
TUILERIES_G = [(48.8648, 2.3218), (48.8636, 2.3218), (48.8615, 2.3300), (48.8627, 2.3310)]
CHAMP_DE_MARS = [(48.8585, 2.2955), (48.8545, 2.3035), (48.8525, 2.3010), (48.8565, 2.2930)]
DEFENSE = rect(48.8875, 2.2300, 48.8950, 2.2500)
MARAIS = [(48.8605, 2.3560), (48.8640, 2.3640), (48.8600, 2.3675), (48.8555, 2.3680), (48.8545, 2.3625), (48.8567, 2.3615)]
INNER = [(48.9500, 2.2300), (48.9550, 2.3500), (48.9400, 2.4400), (48.8900, 2.4900), (48.8200, 2.4800), (48.7800, 2.4100),
         (48.7700, 2.3200), (48.7900, 2.2300), (48.8300, 2.1800), (48.8900, 2.1800)]
OUTER = [(49.0300, 2.1500), (49.0400, 2.3500), (49.0100, 2.5600), (48.9200, 2.6300), (48.8100, 2.6100), (48.7200, 2.5000),
         (48.6900, 2.3300), (48.7200, 2.1500), (48.7900, 2.0500), (48.8900, 2.0400), (48.9800, 2.0800)]
NOTRE_DAME = (48.85306, 2.35)


# ------------------------------------------------------------------ timeline
def seg(frm, to, sec, era, city, title=None, sub=None, pop=None, cam=None, chapter=None):
    d = {"from": frm, "to": to, "seconds": sec, "era": era, "city_name": city}
    if title: d["title"] = title; d["sub"] = sub
    if pop is not None: d["population"] = pop
    if cam: d["camera"] = {"center": [cam[0], cam[1]], "dist_km": cam[2]}
    if chapter: d["chapter"] = chapter
    return d

IRON = T("Iron Age", "Demir Çağı"); ROM = T("Roman Gaul", "Roma Galyası"); LATE = T("Late Antiquity", "Geç Antik Çağ")
FRANK = T("Frankish Kingdom", "Frank Krallığı"); MED = T("Middle Ages", "Orta Çağ"); HYW = T("Hundred Years' War", "Yüz Yıl Savaşları")
REN = T("Renaissance", "Rönesans"); BOUR = T("Bourbon France", "Bourbon Fransası"); REV = T("Revolution", "Devrim")
EMP = T("Napoleonic Era", "Napolyon Dönemi"); MON = T("July Monarchy", "Temmuz Monarşisi"); SEC = T("Second Empire", "İkinci İmparatorluk")
THIRD = T("Third Republic", "Üçüncü Cumhuriyet"); WAR = T("World War II", "II. Dünya Savaşı"); FIFTH = T("Fifth Republic", "Beşinci Cumhuriyet")
TODAY = T("Today", "Bugün")
LUT = T("Lutetia", "Lutetia"); PAR = T("Paris", "Paris"); SEINE = T("Banks of the Seine", "Seine kıyısı")

# sourced anchors (year, people) — see research.md; log-interpolated between them
ANCH = [(1328, 200000), (1348.4, 200000), (1350, 150000), (1383, 150000), (1436, 100000), (1500, 250000), (1643, 400000),
        (1789, 620000), (1797, 570000), (1801, 546856), (1811, 622636), (1831, 785862), (1836, 899313), (1841, 935261),
        (1846, 1053897), (1851, 1053262), (1856, 1174346), (1859.99, 1270000)]
CENS = [(1860, 1696141), (1866, 1825274), (1872, 1851792), (1876, 1988806), (1881, 2269023), (1886, 2344550), (1891, 2447957),
        (1896, 2536834), (1901, 2714068), (1906, 2763393), (1911, 2888110), (1921, 2906472), (1926, 2871429), (1931, 2891020),
        (1936, 2829753), (1946, 2725374), (1954, 2850189), (1962, 2790091), (1968, 2590771), (1975, 2299830), (1982, 2176243),
        (1990, 2152423), (1999, 2125246), (2007, 2193030), (2015, 2206488), (2019, 2165423), (2022, 2113705), (2023, 2103778)]
def interp(tab, y):
    for (y0, p0), (y1, p1) in zip(tab, tab[1:]):
        if y0 <= y <= y1:
            u = (y - y0) / (y1 - y0); return int(round(math.exp(math.log(p0) + (math.log(p1) - math.log(p0)) * u), -3))
    raise ValueError(y)
def P(y):
    if y >= 1860: return interp(CENS, y)
    return interp(ANCH, y)
PI = lambda a, b: [P(a), P(b)]

S = [
 seg(-250, -53, 18, IRON, SEINE, T("The Parisii", "Parisiiler"),
     T("c. 250 BC: a Gallic tribe, the Parisii, settles on the Seine; where their town stood is debated",
       "MÖ ~250: Galyalı Parisii kabilesi Seine kıyısına yerleşir; kasabalarının yeri hâlâ tartışmalı"),
     cam=(48.8545, 2.3470, 2.4), chapter=T("Origins", "Başlangıç")),
 seg(-52, -51, 16, IRON, SEINE, T("Rome Takes the Seine", "Roma Seine'i Alıyor"),
     T("52 BC: the Parisii burn their town and bridges; Labienus's legions win the battle",
       "MÖ 52: Parisiiler kasabalarını ve köprülerini yakar; Labienus'un lejyonları savaşı kazanır"),
     cam=(48.8545, 2.3470, 2.6)),
 seg(-50, 60, 18, ROM, LUT, T("Lutetia", "Lutetia"),
     T("The Romans build a new town on the left bank along one straight main street, the cardo",
       "Romalılar sol yakada, tek bir düz ana cadde (cardo) boyunca yeni bir kasaba kurar"),
     pop=[6000, 7000], cam=(48.8490, 2.3455, 3.0), chapter=T("Roman Lutetia", "Roma Lutetia'sı")),
 seg(61, 150, 18, ROM, LUT, T("Forum and Arena", "Forum ve Arena"),
     T("Late 1st century AD: a forum crowns the hill; the arena seats up to 15,000 people",
       "MS 1. yüzyıl sonu: tepeye bir forum kurulur; arenada 15.000 kişiye kadar yer vardır"),
     pop=[7000, 8000], cam=(48.8470, 2.3470, 2.8)),
 seg(151, 274, 18, ROM, LUT, T("The Baths of Cluny", "Cluny Hamamları"),
     T("c. AD 200: great public baths rise beside the cardo; their vaulted hall still stands",
       "MS ~200: cardo'nun yanında büyük hamamlar yükselir; tonozlu salonu bugün hâlâ ayakta"),
     pop=8000, cam=(48.8495, 2.3445, 2.6)),
 seg(275, 300, 17, LATE, LUT, T("Retreat to the Island", "Adaya Çekiliş"),
     T("From AD 275 raids empty the left bank; stones of its monuments wall the island",
       "MS 275'ten itibaren akınlar sol yakayı boşaltır; anıtlarının taşlarıyla ada surlanır"),
     cam=(48.8525, 2.3480, 2.6), chapter=T("Late Antiquity", "Geç Antik Çağ")),
 seg(301, 450, 17, LATE, PAR, T("Julian, Emperor in Paris", "Paris'te İmparator Julianus"),
     T("February 360: Julian's troops proclaim him emperor in the city, now known as Paris",
       "Şubat 360: Julianus'un askerleri onu, artık Paris adıyla bilinen şehirde imparator ilan eder"),
     cam=(48.8535, 2.3475, 2.6)),
 seg(451, 485, 15, LATE, PAR, T("Genevieve and Attila", "Genevieve ve Attila"),
     T("451: Attila's army threatens Paris but passes it by; Genevieve urged the people to stay",
       "451: Attila'nın ordusu Paris'i tehdit eder ama geçip gider; Genevieve halkı kalmaya çağırmıştı"),
     cam=(48.8540, 2.3470, 3.0)),
 seg(486, 844, 17, FRANK, PAR, T("Capital of Clovis", "Clovis'in Başkenti"),
     T("508: Clovis, king of the Franks, makes Paris his capital; in 751 the court moves to Aachen",
       "508: Frank kralı Clovis Paris'i başkenti yapar; 751'de saray Aachen'e taşınır"),
     cam=(48.8540, 2.3460, 3.2), chapter=T("Franks and Vikings", "Franklar ve Vikingler")),
 seg(845, 884, 16, FRANK, PAR, T("The Vikings Arrive", "Vikingler Geliyor"),
     T("Easter 845: 120 Viking ships reach Paris; the king pays 7,000 livres to make them leave",
       "Paskalya 845: 120 Viking gemisi Paris'e ulaşır; kral gitmeleri için 7.000 livre öder"),
     cam=(48.8550, 2.3460, 3.2)),
 seg(885, 986, 16, FRANK, PAR, T("The Great Siege", "Büyük Kuşatma"),
     T("885–886: a Viking army besieges Paris for a year; the island city holds out",
       "885–886: bir Viking ordusu Paris'i bir yıl boyunca kuşatır; ada şehri direnir"),
     cam=(48.8550, 2.3455, 3.4)),
 seg(987, 1162, 16, MED, PAR, T("A Royal Town", "Bir Kraliyet Kasabası"),
     T("987: Hugh Capet founds the Capetian dynasty; the town spreads over the right bank",
       "987: Hugues Capet, Capet hanedanını kurar; kasaba sağ yakaya yayılır"),
     cam=(48.8560, 2.3480, 3.4), chapter=T("Medieval Paris", "Orta Çağ Parisi")),
 seg(1163, 1189, 17, MED, PAR, T("Notre-Dame", "Notre-Dame"),
     T("1163: the first stone of Notre-Dame is laid; its high altar is consecrated in 1182",
       "1163: Notre-Dame'ın ilk taşı konur; ana sunağı 1182'de kutsanır"),
     cam=(48.8535, 2.3490, 2.4)),
 seg(1190, 1215, 19, MED, PAR, T("Philip Augustus's Wall", "Philippe Auguste Suru"),
     T("1190–1213: a wall with 77 towers rings 253 hectares; the Louvre fortress guards the river",
       "1190–1213: 77 kuleli bir sur 253 hektarı çevreler; Louvre kalesi nehri korur"),
     cam=(48.8550, 2.3470, 4.2)),
 seg(1216, 1327, 17, MED, PAR, T("The Sainte-Chapelle", "Sainte-Chapelle"),
     T("26 April 1248: Louis IX's Sainte-Chapelle is consecrated beside the royal palace",
       "26 Nisan 1248: IX. Louis'nin Sainte-Chapelle'i kraliyet sarayının yanında kutsanır"),
     cam=(48.8550, 2.3450, 2.6)),
 seg(1328, 1347, 15, MED, PAR, T("Largest City in Europe", "Avrupa'nın En Büyük Şehri"),
     T("1328: about 200,000 people make Paris the largest city in Europe",
       "1328: yaklaşık 200.000 kişiyle Paris Avrupa'nın en büyük şehridir"),
     pop=200000, cam=(48.8560, 2.3480, 4.8)),
 seg(1348, 1355, 15, HYW, PAR, T("The Black Death", "Kara Ölüm"),
     T("1348–1349: plague kills 40,000–50,000 Parisians, about a quarter of the city",
       "1348–1349: veba 40.000–50.000 Parisliyi, şehrin yaklaşık dörtte birini öldürür"),
     pop=[200000, 150000], cam=(48.8560, 2.3480, 4.6)),
 seg(1356, 1383, 18, HYW, PAR, T("The Wall of Charles V", "V. Charles Suru"),
     T("1356–1383: a new wall takes in the Marais; the Bastille rises at its eastern gate",
       "1356–1383: yeni sur Marais'yi içine alır; doğu kapısında Bastille yükselir"),
     pop=150000, cam=(48.8580, 2.3530, 4.8)),
 seg(1384, 1436, 16, HYW, PAR, T("English Paris", "İngiliz Parisi"),
     T("1420–1436: English troops hold Paris; by 1436 only about 100,000 people remain",
       "1420–1436: İngiliz askerleri Paris'i elinde tutar; 1436'da yalnızca ~100.000 kişi kalır"),
     pop=[150000, 100000], cam=(48.8575, 2.3500, 5.0)),
 seg(1437, 1532, 16, REN, PAR, T("The City Recovers", "Şehir Toparlanıyor"),
     T("By 1500 Paris has grown back to about 250,000 people", "1500'e gelindiğinde Paris yeniden yaklaşık 250.000 kişiye ulaşır"),
     pop=PI(1437, 1532), cam=(48.8570, 2.3480, 5.2), chapter=T("Renaissance Paris", "Rönesans Parisi")),
 seg(1533, 1563, 16, REN, PAR, T("A Royal Louvre", "Kraliyet Louvre'u"),
     T("1533: work begins on a new Hôtel de Ville; from 1534 the Louvre is the royal home",
       "1533: yeni Hôtel de Ville'in yapımı başlar; 1534'ten itibaren Louvre kraliyet konutudur"),
     pop=PI(1533, 1563), cam=(48.8585, 2.3430, 3.0)),
 seg(1564, 1571, 14, REN, PAR, T("The Tuileries Palace", "Tuileries Sarayı"),
     T("1564: Catherine de' Medici begins the Tuileries Palace west of the Louvre",
       "1564: Catherine de Médicis, Louvre'un batısında Tuileries Sarayı'nı başlatır"),
     pop=PI(1564, 1571), cam=(48.8605, 2.3390, 3.0)),
 seg(1572, 1577, 14, REN, PAR, T("St Bartholomew's Day", "Aziz Bartholomeos Günü"),
     T("24 August 1572: the massacre of Protestants begins in Paris, in years of religious war",
       "24 Ağustos 1572: din savaşları yıllarında Paris'te Protestanlara yönelik katliam başlar"),
     pop=PI(1572, 1577), cam=(48.8575, 2.3450, 3.6)),
 seg(1578, 1604, 17, REN, PAR, T("The Pont Neuf", "Pont Neuf"),
     T("1578–1607: the Pont Neuf, 232 m long, crosses the Seine at the tip of the island",
       "1578–1607: 232 m'lik Pont Neuf, adanın ucunda Seine'i geçer"),
     pop=PI(1578, 1604), cam=(48.8570, 2.3420, 2.4)),
 seg(1605, 1632, 16, BOUR, PAR, T("Place Royale", "Place Royale"),
     T("1605–1612: Henry IV builds a 140 m square of brick houses, today's Place des Vosges",
       "1605–1612: IV. Henri 140 m'lik bir meydan yaptırır: bugünkü Place des Vosges"),
     pop=PI(1605, 1632), cam=(48.8560, 2.3600, 3.0), chapter=T("The Age of Kings", "Krallar Çağı")),
 seg(1633, 1669, 16, BOUR, PAR, T("The City Pushes West", "Şehir Batıya Uzanıyor"),
     T("1633–1636: a new wall takes in the west; by 1643 Paris has about 400,000 people",
       "1633–1636: yeni bir sur batıyı içine alır; 1643'te Paris'te ~400.000 kişi yaşar"),
     pop=PI(1633, 1669), cam=(48.8615, 2.3420, 5.0)),
 seg(1670, 1675, 15, BOUR, PAR, T("The Grand Boulevards", "Büyük Bulvarlar"),
     T("1670: Louis XIV orders the walls torn down; tree-lined boulevards take their place",
       "1670: XIV. Louis surların yıkılmasını emreder; yerlerini ağaçlı bulvarlar alır"),
     pop=PI(1670, 1675), cam=(48.8640, 2.3480, 5.4)),
 seg(1676, 1706, 16, BOUR, PAR, T("Les Invalides", "Les Invalides"),
     T("1671–1706: Louis XIV builds Les Invalides for old soldiers; its dome rises 107 m",
       "1671–1706: XIV. Louis yaşlı askerler için Les Invalides'i yaptırır; kubbesi 107 m'ye yükselir"),
     pop=PI(1676, 1706), cam=(48.8555, 2.3200, 3.4)),
 seg(1707, 1783, 7, BOUR, PAR, pop=PI(1707, 1783), cam=(48.8590, 2.3400, 6.5)),
 seg(1784, 1788, 15, REV, PAR, T("The Farmers-General Wall", "Fermiers Généraux Suru"),
     T("1784–1791: a 24 km customs wall with 55 toll gates rings the whole city",
       "1784–1791: 55 gümrük kapılı, 24 km'lik bir vergi suru bütün şehri çevreler"),
     pop=PI(1784, 1788), cam=(48.8600, 2.3420, 8.5), chapter=T("Revolution", "Devrim")),
 seg(1789, 1799, 17, REV, PAR, T("The Fall of the Bastille", "Bastille'in Düşüşü"),
     T("14 July 1789: crowds storm the Bastille; by November it is mostly torn down",
       "14 Temmuz 1789: kalabalık Bastille'e saldırır; kasıma kadar büyük kısmı yıkılır"),
     pop=[620000, 570000], cam=(48.8545, 2.3640, 3.2)),
 seg(1800, 1836, 17, EMP, PAR, T("The Arc de Triomphe", "Zafer Takı"),
     T("1806–1836: the 50 m Arc de Triomphe rises; the 1801 census counts 546,856 Parisians",
       "1806–1836: 50 m'lik Zafer Takı yükselir; 1801 sayımında 546.856 Parisli vardır"),
     pop=[546856, 899313], cam=(48.8665, 2.3150, 5.4), chapter=T("19th-Century Paris", "19. Yüzyıl Parisi")),
 seg(1837, 1840, 14, MON, PAR, T("The First Railway", "İlk Demiryolu"),
     T("24 August 1837: Paris's first station opens, for the line to Saint-Germain-en-Laye",
       "24 Ağustos 1837: Saint-Germain-en-Laye hattı için Paris'in ilk istasyonu açılır"),
     pop=PI(1837, 1840), cam=(48.8700, 2.3200, 5.8)),
 seg(1841, 1852, 16, MON, PAR, T("The Thiers Wall", "Thiers Suru"),
     T("1841–1846: a 33 km rampart with 94 bastions encircles Paris and its villages",
       "1841–1846: 94 tabyalı, 33 km'lik bir sur Paris'i ve çevre köylerini kuşatır"),
     pop=PI(1841, 1852), cam=(48.8590, 2.3400, 13.0)),
 seg(1853, 1859, 18, SEC, PAR, T("Haussmann's Paris", "Haussmann'ın Parisi"),
     T("From 1853 Haussmann tears down 19,730 buildings and cuts wide new boulevards",
       "1853'ten itibaren Haussmann 19.730 binayı yıkar ve geniş yeni bulvarlar açar"),
     pop=PI(1853, 1859), cam=(48.8590, 2.3450, 6.4), chapter=T("Haussmann", "Haussmann")),
 seg(1860, 1869, 16, SEC, PAR, T("Twenty Arrondissements", "Yirmi Bölge"),
     T("1 January 1860: Paris annexes its suburbs up to the Thiers wall; 12 districts become 20",
       "1 Ocak 1860: Paris, Thiers suruna kadar banliyöleri katar; 12 bölge 20 olur"),
     pop=[P(1860), P(1869)], cam=(48.8590, 2.3420, 12.0)),
 seg(1870, 1871.1, 16, THIRD, PAR, T("The Siege of Paris", "Paris Kuşatması"),
     T("19 Sept 1870 – 28 Jan 1871: German armies besiege the city and shell it in January",
       "19 Eylül 1870 – 28 Ocak 1871: Alman orduları şehri kuşatır, ocakta bombalar"),
     pop=[P(1870), P(1871.1)], cam=(48.8560, 2.3400, 17.0), chapter=T("Siege and Commune", "Kuşatma ve Komün")),
 seg(1871.2, 1872, 16, THIRD, PAR, T("Paris Burns", "Paris Yanıyor"),
     T("May 1871: as the Commune is crushed, fires gut the Tuileries and the Hôtel de Ville",
       "Mayıs 1871: Komün bastırılırken yangınlar Tuileries'yi ve Hôtel de Ville'i harap eder"),
     pop=[P(1871.2), P(1872)], cam=(48.8590, 2.3420, 3.4)),
 seg(1873, 1886, 16, THIRD, PAR, T("Opera and Sacré-Cœur", "Opera ve Sacré-Cœur"),
     T("1875: the Palais Garnier opera opens and work begins on Sacré-Cœur on Montmartre",
       "1875: Palais Garnier operası açılır ve Montmartre'da Sacré-Cœur'ün yapımı başlar"),
     pop=PI(1873, 1886), cam=(48.8740, 2.3390, 4.6), chapter=T("Belle Époque", "Belle Époque")),
 seg(1887, 1899, 18, THIRD, PAR, T("The Eiffel Tower", "Eiffel Kulesi"),
     T("1887–1889: a 300 m iron tower is built for the World's Fair on the Champ de Mars",
       "1887–1889: Champ de Mars'taki Dünya Fuarı için 300 m'lik demir bir kule yapılır"),
     pop=PI(1887, 1899), cam=(48.8570, 2.3050, 4.4)),
 seg(1900, 1918, 16, THIRD, PAR, T("The Métro", "Metro"),
     T("19 July 1900: the first Métro line opens, from Porte Maillot to Porte de Vincennes",
       "19 Temmuz 1900: ilk metro hattı Porte Maillot ile Porte de Vincennes arasında açılır"),
     pop=PI(1900, 1918), cam=(48.8600, 2.3400, 11.0)),
 seg(1919, 1939, 16, THIRD, PAR, T("Peak Paris", "Zirvedeki Paris"),
     T("From 1919 the Thiers wall is torn down; in 1921 Paris peaks at 2,906,472 people",
       "1919'dan itibaren Thiers suru yıkılır; 1921'de Paris 2.906.472 kişiyle zirveye ulaşır"),
     pop=PI(1919, 1939), cam=(48.8590, 2.3400, 15.0), chapter=T("20th-Century Paris", "20. Yüzyıl Parisi")),
 seg(1940, 1944.7, 16, WAR, PAR, T("Occupation and Liberation", "İşgal ve Kurtuluş"),
     T("1940–1944: German troops occupy Paris; it is liberated on 25 August 1944",
       "1940–1944: Alman askerleri Paris'i işgal eder; şehir 25 Ağustos 1944'te kurtarılır"),
     pop=PI(1940, 1944.7), cam=(48.8570, 2.3450, 9.0)),
 seg(1944.8, 1968, 16, FIFTH, PAR, T("La Défense", "La Défense"),
     T("1958: work starts on a business district west of Paris; its first tower opens in 1966",
       "1958: Paris'in batısında bir iş merkezinin yapımı başlar; ilk kulesi 1966'da açılır"),
     pop=PI(1944.8, 1968), cam=(48.8700, 2.2900, 13.0)),
 seg(1969, 1976, 16, FIFTH, PAR, T("Ring Road and Tower", "Çevre Yolu ve Kule"),
     T("1973: the 35 km Boulevard Périphérique is finished and the 210 m Montparnasse tower opens",
       "1973: 35 km'lik Périphérique çevre yolu biter ve 210 m'lik Montparnasse kulesi açılır"),
     pop=PI(1969, 1976), cam=(48.8540, 2.3350, 15.0)),
 seg(1977, 1989, 16, FIFTH, PAR, T("Grand Projects", "Büyük Projeler"),
     T("1977: the Centre Pompidou opens; on 14 July 1989 the Grande Arche is inaugurated",
       "1977: Centre Pompidou açılır; 14 Temmuz 1989'da Grande Arche açılışını yapar"),
     pop=PI(1977, 1989), cam=(48.8690, 2.3000, 12.0)),
 seg(1990, 2018, 8, FIFTH, PAR, pop=PI(1990, 2018), cam=(48.8600, 2.3300, 22.0)),
 seg(2019, 2024.4, 17, TODAY, PAR, T("Notre-Dame Burns", "Notre-Dame Yanıyor"),
     T("15 April 2019: fire destroys Notre-Dame's spire and roof; it reopens in December 2024",
       "15 Nisan 2019: yangın Notre-Dame'ın kulesini ve çatısını yakar; Aralık 2024'te yeniden açılır"),
     pop=PI(2019, 2023), cam=(48.8535, 2.3490, 2.6), chapter=T("Paris Today", "Bugünün Parisi")),
 seg(2024.5, 2024.9, 15, TODAY, PAR, T("The Games on the Seine", "Seine'de Olimpiyatlar"),
     T("26 July 2024: 85 boats carry 6,800 athletes down the Seine to open the Olympic Games",
       "26 Temmuz 2024: 85 tekne 6.800 sporcuyu Seine boyunca taşıyarak Olimpiyatları açar"),
     pop=2103778, cam=(48.8580, 2.3250, 6.5)),
 seg(2025, 2026, 22, TODAY, PAR, T("Paris Today", "Bugünün Parisi"),
     T("From a Gallic tribe's town to 2.1 million Parisians, some 2,300 years on",
       "Galyalı bir kabilenin kasabasından 2,1 milyon Parisliye, yaklaşık 2.300 yıl sonra"),
     pop=2103778, cam=(48.8620, 2.3300, 11.0)),
]
SCALE_T, SCALE_Q = 1.12, 1.1
for s_ in S:
    s_["seconds"] = round(s_["seconds"] * (SCALE_T if s_.get("title") else SCALE_Q))


def ring_wall(name, path, built, removed=None, height="mid", towers=90, draw=3.0, **kw):
    d = {"name": name, "path": L(path), "built": built, "height": height, "towers_m": towers, "draw_s": draw}
    if removed is not None: d["removed"] = removed
    d.update(kw); return d

city = {
 "slug": "paris", "seed": 52, "long_ok": True,
 "name": T("Paris", "Paris"), "intro": T("2,300 Years in 15 Minutes", "15 Dakikada 2.300 Yıl"), "intro_seconds": 4.5,
 "geo": {"bbox": [48.62, 1.95, 49.10, 2.78], "cell_m": 100, "core_bbox": [48.800, 2.210, 48.915, 2.470], "core_cell_m": 30,
         "rivers_keep": ["Seine", "Marne"], "lakes_from": 1855},
 "view": {"azimuth_deg": 0, "pitch_deg": 46, "fov": 34},
 "render": {"vertical_exaggeration": 3.0},
 "segments": S,
 "districts": [
  {"name": "Parisii village (≈, site debated)", "style": "celtic", "poly": L(CITE), "from": -250, "to": -150, "density": 0.5, "grain_m": 45,
   "grow_from": [48.8550, 2.3470]},
  {"name": "Roman island", "style": "roman", "poly": L(CITE), "from": -45, "to": 40, "density": 0.7, "grain_m": 45, "grow_from": [48.8550, 2.3470]},
  {"name": "Lutetia (left bank)", "style": "roman", "poly": L(LUTETIA), "from": -48, "to": 120, "density": 0.62, "grid_deg": 82,
   "grow_from": [48.8510, 2.3460], "fade": [275, 300, 0.1]},
  {"name": "Late Roman Cité", "style": "medieval", "poly": L(CITE), "from": 276, "to": 300, "density": 0.85, "grain_m": 40, "grow_from": [48.8540, 2.3490]},
  {"name": "Right bank (10th–12th c.)", "style": "medieval", "poly": L([(48.8582, 2.3440), (48.8605, 2.3445), (48.8622, 2.3475), (48.8616, 2.3522),
   (48.8596, 2.3560), (48.8572, 2.3575), (48.8560, 2.3545), (48.8570, 2.3490)]), "from": 950, "to": 1150, "density": 0.75, "grow_from": [48.8575, 2.3480]},
  {"name": "Left bank bourgs (12th c.)", "style": "medieval", "poly": L([(48.8528, 2.3432), (48.8527, 2.3485), (48.8505, 2.3510), (48.8480, 2.3500),
   (48.8478, 2.3430), (48.8500, 2.3410)]), "from": 1100, "to": 1180, "density": 0.6, "grow_from": [48.8515, 2.3460]},
  {"name": "Inside Philip Augustus (right bank)", "style": "medieval", "poly": L(PA_RB), "from": 1190, "to": 1300, "density": 0.85, "grow_from": [48.8590, 2.3480]},
  {"name": "Inside Philip Augustus (left bank)", "style": "medieval", "poly": L(PA_LB), "from": 1200, "to": 1320, "density": 0.75, "grow_from": [48.8510, 2.3450]},
  {"name": "Marais (Charles V)", "style": "medieval", "poly": L(CV_RB), "holes": [L(PA_RB)], "from": 1360, "to": 1500, "density": 0.75,
   "grow_from": [48.8590, 2.3600]},
  {"name": "Left-bank faubourgs", "style": "stone", "poly": L(FBG_L), "holes": [L(LUXEMBOURG)], "from": 1540, "to": 1700, "density": 0.65,
   "grow_from": [48.8530, 2.3380]},
  {"name": "Western right bank (Louis XIII)", "style": "stone", "poly": L(WEST_RB), "holes": [L(TUILERIES_G)], "from": 1630, "to": 1690,
   "density": 0.8, "grow_from": [48.8640, 2.3350]},
  {"name": "Île Saint-Louis (≈ 17th c.)", "style": "stone", "poly": L(ILE_SL), "from": 1620, "to": 1660, "density": 0.85, "grain_m": 40,
   "grow_from": [48.8516, 2.3570]},
  {"name": "18th-century faubourgs", "style": "georgian", "poly": L(FG_POLY), "holes": [L(CV_RB), L(PA_LB), L(FBG_L), L(WEST_RB), L(CITE),
   L(ILE_SL), L(LUXEMBOURG), L(TUILERIES_G), L(CHAMP_DE_MARS)], "from": 1700, "to": 1800, "density": 0.55, "grain_m": 75,
   "grow_from": [48.8600, 2.3450]},
  {"name": "Haussmann's Paris", "style": "stone", "poly": L(FG_POLY), "holes": [L(MARAIS), L(ILE_SL), L(LUXEMBOURG), L(TUILERIES_G), L(CHAMP_DE_MARS)],
   "from": 1853, "to": 1872, "density": 0.85, "grain_m": 75, "grow_from": [48.8600, 2.3450]},
  {"name": "Annexed communes (1860)", "style": "stone", "poly": L(TH_POLY), "holes": [L(FG_POLY), L(BOULOGNE)], "from": 1860, "to": 1914,
   "density": 0.75, "grain_m": 95, "grow_from": [48.8600, 2.3450]},
  {"name": "Inner suburbs", "style": "suburb", "poly": L(INNER), "holes": [L(PERI), L(BOULOGNE), L(VINCENNES), L(DEFENSE)], "from": 1880, "to": 1960,
   "density": 0.55, "grain_m": 190, "grow_from": [48.8600, 2.3450]},
  {"name": "Outer suburbs", "style": "suburb", "poly": L(OUTER), "holes": [L(INNER)], "from": 1950, "to": 2015, "density": 0.4, "grain_m": 280,
   "grow_from": [48.8600, 2.3450]},
  {"name": "La Défense", "style": "highrise", "poly": L(DEFENSE), "from": 1964, "to": 2015, "density": 0.7, "grain_m": 110, "grid_deg": 35,
   "grow_from": [48.8920, 2.2400]},
 ],
 "walls": [
  ring_wall("Gallo-Roman wall (Cité)", CITE_EAST_WALL, 276, 1200, height="low", towers=0, draw=2.0),
  ring_wall("Wall of Philip Augustus (right bank)", PA_R, 1190, 1700, towers=60, draw=4.0),
  ring_wall("Wall of Philip Augustus (left bank)", PA_L, 1200, 1700, towers=60, draw=4.0),
  ring_wall("Wall of Charles V", CV, 1356, 1670, height="mid", towers=80, draw=4.0, moat=True),
  ring_wall("Louis XIII wall", L13, 1633, 1670, height="mid", towers=0, draw=2.0, moat=True),
  ring_wall("Wall of the Farmers-General (right bank)", FG_R, 1787, 1860, height="low", towers=0, draw=3.5),
  ring_wall("Wall of the Farmers-General (left bank)", FG_L, 1784, 1860, height="low", towers=0, draw=3.0),
  ring_wall("Thiers wall (right bank)", TH_R, 1841, 1925, height="mid", towers=0, draw=4.0, moat=True),
  ring_wall("Thiers wall (left bank)", TH_L, 1842, 1925, height="mid", towers=0, draw=3.0, moat=True),
 ],
 "bridges": [
  {"name": "Petit Pont (≈)", "path": [[48.8530, 2.3474], [48.8521, 2.3471]], "built": -40, "style": "wood", "width_m": 12, "removed": 1200},
  {"name": "Grand Pont (≈)", "path": [[48.8562, 2.3468], [48.8573, 2.3472]], "built": -40, "style": "wood", "width_m": 12, "removed": 1200},
  {"name": "Petit Pont (stone, ≈)", "path": [[48.8530, 2.3474], [48.8521, 2.3471]], "built": 1200, "style": "stone", "width_m": 14},
  {"name": "Pont au Change (≈)", "path": [[48.8562, 2.3468], [48.8573, 2.3472]], "built": 1200, "style": "stone", "width_m": 18},
  {"name": "Pont Neuf", "path": [[48.8590, 2.3428], [48.8558, 2.3405]], "built": 1578, "style": "stone", "width_m": 22, "draw_s": 6},
 ],
 "roads": [
  {"name": "Cardo (rue Saint-Jacques)", "path": L([(48.8521, 2.3471), (48.8490, 2.3460), (48.8460, 2.3448), (48.8420, 2.3432), (48.8340, 2.3395), (48.8200, 2.3350)]),
   "from": -48, "kind": "roman", "width_m": 14},
  {"name": "Right-bank road (rue Saint-Martin)", "path": L([(48.8573, 2.3472), (48.8610, 2.3505), (48.8660, 2.3530), (48.8720, 2.3555), (48.8850, 2.3600)]),
   "from": -40, "kind": "road", "width_m": 12},
  {"name": "Grands Boulevards", "path": L([(48.8698, 2.3245), (48.8706, 2.3290), (48.8712, 2.3340), (48.8716, 2.3400), (48.8710, 2.3460), (48.8702, 2.3510),
   (48.8693, 2.3590), (48.8672, 2.3635), (48.8645, 2.3660), (48.8605, 2.3680), (48.8560, 2.3690), (48.8533, 2.3692)]), "from": 1671, "kind": "avenue", "width_m": 30},
  {"name": "Champs-Élysées (≈, drawn from 1836)", "path": L([(48.8656, 2.3212), (48.8700, 2.3080), (48.8738, 2.2950)]), "from": 1836, "kind": "avenue", "width_m": 40},
  {"name": "Railway to Saint-Germain", "path": L([(48.8763, 2.3253), (48.8850, 2.3120), (48.8930, 2.2980)]), "from": 1837, "kind": "rail", "width_m": 22},
  {"name": "Rue de Rivoli", "path": L([(48.8655, 2.3225), (48.8620, 2.3340), (48.8590, 2.3440), (48.8570, 2.3540), (48.8555, 2.3600)]), "from": 1855, "kind": "avenue", "width_m": 26},
  {"name": "Boulevard de Sébastopol", "path": L([(48.8580, 2.3475), (48.8640, 2.3505), (48.8700, 2.3535), (48.8760, 2.3585)]), "from": 1855, "kind": "avenue", "width_m": 30},
  {"name": "Boulevard Saint-Michel", "path": L([(48.8532, 2.3440), (48.8490, 2.3420), (48.8440, 2.3395), (48.8400, 2.3365)]), "from": 1859, "kind": "avenue", "width_m": 28},
  {"name": "Boulevard Périphérique", "path": L(PERI), "from": 1973, "kind": "motorway", "width_m": 45},
 ],
 "landmarks": [
  {"type": "forum", "name": T("Forum of Lutetia", "Lutetia Forumu"), "at": [48.8466, 2.3423], "built": 80, "removed": 300, "size_m": [178, 89], "rot_deg": 82,
   "colors": {"column": False}},
  {"type": "amphitheatre", "name": T("Arena of Lutetia", "Lutetia Arenası"), "at": [48.84500, 2.35278], "built": 85, "removed": 600, "rise_s": 3,
   "size_m": [130, 100, 14], "rot_deg": 20},
  {"type": "box", "name": T("Baths of Cluny", "Cluny Hamamları"), "at": [48.8506, 2.3440], "built": 200, "rise_s": 3, "size_m": [100, 70, 18],
   "colors": {"wall": "#e2d6bd", "roof": "#b4583b"}},
  {"type": "cathedral", "name": T("Notre-Dame", "Notre-Dame"), "at": [48.85306, 2.35], "built": 1163, "removed": 2019.29, "rise_s": 40,
   "size_m": [128, 48, 34], "rot_deg": 18, "colors": {"wall": "#ddd6c4", "roof": "#5f666f"}},
  {"type": "cathedral", "name": T("Notre-Dame (after the fire)", "Notre-Dame (yangından sonra)"), "at": [48.85306, 2.35], "built": 2019.3, "removed": 2024.93,
   "rise_s": 0.2, "size_m": [128, 48, 34], "rot_deg": 18, "colors": {"wall": "#ddd6c4", "roof": "#3b3b3b", "spire": False}},
  {"type": "cathedral", "name": T("Notre-Dame (restored)", "Notre-Dame (restore)"), "at": [48.85306, 2.35], "built": 2024.94, "rise_s": 1.5,
   "size_m": [128, 48, 34], "rot_deg": 18, "colors": {"wall": "#e6dfcd", "roof": "#5f666f"}},
  {"type": "castle", "name": T("Louvre fortress", "Louvre kalesi"), "at": [48.86025, 2.33800], "built": 1190, "removed": 1546, "rise_s": 4,
   "size_m": [78, 72, 22], "colors": {"wall": "#d9cfb6"}},
  {"type": "tower", "name": T("Grosse Tour", "Büyük Kule"), "at": [48.86025, 2.33800], "built": 1200, "removed": 1528, "size_m": [16, 16, 30],
   "colors": {"wall": "#d9cfb6", "roof": "#5f666f"}},
  {"type": "palace", "name": T("Louvre Palace", "Louvre Sarayı"), "at": [48.86025, 2.33800], "built": 1546, "rise_s": 6, "size_m": [160, 160, 26],
   "colors": {"wall": "#e8e0cc", "roof": "#6f7680"}},
  {"type": "church", "name": T("Sainte-Chapelle", "Sainte-Chapelle"), "at": [48.85528, 2.34500], "built": 1242, "rise_s": 3, "size_m": [36, 17, 30],
   "rot_deg": 20, "colors": {"wall": "#e4dccb", "roof": "#4f565e"}},
  {"type": "castle", "name": T("Bastille", "Bastille"), "at": [48.85333, 2.36917], "built": 1370, "removed": 1789.8, "rise_s": 4, "size_m": [68, 37, 24],
   "colors": {"wall": "#bfb39b"}},
  {"type": "palace", "name": T("Hôtel de Ville", "Hôtel de Ville"), "at": [48.85639, 2.35222], "built": 1533, "removed": 1871.4, "rise_s": 8,
   "size_m": [110, 60, 22], "colors": {"wall": "#ece4d0", "roof": "#59656a"}},
  {"type": "palace", "name": T("Hôtel de Ville (rebuilt)", "Hôtel de Ville (yeniden)"), "at": [48.85639, 2.35222], "built": 1873, "rise_s": 6,
   "size_m": [140, 80, 24], "colors": {"wall": "#ece4d0", "roof": "#59656a"}},
  {"type": "box", "name": T("Tuileries Palace", "Tuileries Sarayı"), "at": [48.86222, 2.33250], "built": 1564, "removed": 1883.7, "rise_s": 6,
   "size_m": [266, 30, 24], "rot_deg": -62, "colors": {"wall": "#e8e0cc", "roof": "#59656a"}},
  {"type": "forum", "name": T("Place Royale", "Place Royale"), "at": [48.85556, 2.36556], "built": 1605, "rise_s": 4, "size_m": [140, 140],
   "colors": {"wall": "#9fb07f", "column": False}},
  {"type": "palace", "name": T("Hôtel des Invalides", "Invalides"), "at": [48.8565, 2.3125], "built": 1671, "rise_s": 6, "size_m": [200, 180, 20],
   "colors": {"wall": "#e2dccb", "roof": "#59656a"}},
  {"type": "domechurch", "name": T("Dôme des Invalides", "Invalides Kubbesi"), "at": [48.8549, 2.3125], "built": 1680, "rise_s": 14, "size_m": [60, 60, 40],
   "colors": {"wall": "#e6dfcf", "dome": "#c9a94a", "lantern": True}},
  {"type": "box", "name": T("Arc de Triomphe", "Zafer Takı"), "at": [48.87378, 2.29503], "built": 1806.6, "rise_s": 14, "size_m": [45, 22, 50],
   "colors": {"wall": "#ebe5d6"}},
  {"type": "palace", "name": T("Palais Garnier", "Palais Garnier"), "at": [48.87194, 2.33167], "built": 1861.6, "rise_s": 10, "size_m": [155, 70, 32],
   "rot_deg": 90, "colors": {"wall": "#e8dcc0", "roof": "#6e8f6a"}},
  {"type": "domechurch", "name": T("Sacré-Cœur", "Sacré-Cœur"), "at": [48.88667, 2.34306], "built": 1875.5, "rise_s": 24, "size_m": [85, 35, 40],
   "rot_deg": 90, "colors": {"wall": "#f4f1ea", "dome": "#efece4"}},
  {"type": "spire_tower", "name": T("Eiffel Tower", "Eiffel Kulesi"), "at": [48.85822, 2.29450], "built": 1887.1, "rise_s": 9, "size_m": [125, 125, 300],
   "colors": {"wall": "#7b6a55"}},
  {"type": "skyscraper", "name": T("Tour Montparnasse", "Montparnasse Kulesi"), "at": [48.8421, 2.3220], "built": 1969.5, "rise_s": 6, "size_m": [50, 32, 210],
   "colors": {"wall": "#3d4650"}},
  {"type": "box", "name": T("Centre Pompidou", "Centre Pompidou"), "at": [48.86064, 2.35225], "built": 1971.5, "rise_s": 4, "size_m": [166, 60, 45],
   "colors": {"wall": "#4f7fb0"}},
  {"type": "box", "name": T("Grande Arche", "Grande Arche"), "at": [48.89278, 2.23583], "built": 1985.5, "rise_s": 4, "size_m": [110, 110, 110],
   "colors": {"wall": "#f2f2f0"}},
 ],
 "fires": [
  {"year": -52, "poly": L(CITE), "duration_s": 6, "plumes": 4},
  {"year": 1871.39, "poly": L([(48.8648, 2.3290), (48.8630, 2.3355), (48.8612, 2.3340), (48.8628, 2.3275)]), "duration_s": 6, "plumes": 4},
  {"year": 1871.395, "poly": L(rect(48.8556, 2.3505, 48.8572, 2.3540)), "duration_s": 6, "plumes": 3},
 ],
 "smoke": [
  {"at": [48.8550, 2.3470], "from": 845.2, "to": 846, "scale": 1.1},
  {"at": [48.8550, 2.3470], "from": 856.9, "to": 858, "scale": 1.2},
  {"at": [48.8556, 2.3440], "from": 1871.39, "to": 1871.5, "scale": 1.2},
  {"at": [48.85333, 2.36917], "from": 1789.53, "to": 1789.9, "scale": 1.0},
  {"at": [48.8460, 2.3330], "from": 1871.01, "to": 1871.07, "scale": 1.0},
  {"at": [48.85306, 2.35], "from": 2019.29, "to": 2019.33, "scale": 1.3},
 ],
 "camps": [
  {"poly": L(rect(48.8500, 2.3280, 48.8545, 2.3360)), "from": 885.8, "to": 886.8, "count": 80},
  {"poly": L(rect(48.8590, 2.3520, 48.8620, 2.3600)), "from": 885.8, "to": 886.8, "count": 60},
  {"poly": L(rect(48.9380, 2.3000, 48.9500, 2.4200)), "from": 1870.72, "to": 1871.08, "count": 140},
  {"poly": L(rect(48.7700, 2.2600, 48.7820, 2.4000)), "from": 1870.72, "to": 1871.08, "count": 140},
  {"poly": L(rect(48.8100, 2.1500, 48.8900, 2.1650)), "from": 1870.72, "to": 1871.08, "count": 100},
 ],
 "open_spaces": [
  {"name": "Bois de Boulogne", "poly": L(BOULOGNE)},
  {"name": "Bois de Vincennes", "poly": L(VINCENNES)},
  {"name": "Jardin du Luxembourg", "poly": L(LUXEMBOURG)},
  {"name": "Jardin des Tuileries", "poly": L(TUILERIES_G)},
  {"name": "Champ de Mars", "poly": L(CHAMP_DE_MARS)},
 ],
 "labels": [
  {"text": T("SEINE", "SEINE"), "at": [48.8590, 2.3290], "kind": "water", "to": 1840},
  {"text": T("SEINE", "SEINE"), "at": [48.8620, 2.3030], "kind": "water", "from": 1840},
  {"text": T("Île de la Cité", "Cité Adası"), "at": [48.8548, 2.3475], "kind": "place", "from": -250, "to": -53, "lift_m": 20},
  {"text": T("LEFT BANK", "SOL YAKA"), "at": [48.8460, 2.3440], "kind": "region", "from": -50, "to": 60},
  {"text": T("Forum", "Forum"), "at": [48.8466, 2.3423], "from": 85, "to": 150, "lift_m": 20},
  {"text": T("Arena", "Arena"), "at": [48.8450, 2.35278], "from": 88, "to": 150, "lift_m": 25},
  {"text": T("Baths of Cluny", "Cluny Hamamları"), "at": [48.8506, 2.3440], "from": 202, "to": 274, "lift_m": 30},
  {"text": T("Île de la Cité", "Cité Adası"), "at": [48.8548, 2.3475], "kind": "place", "from": 276, "to": 362, "lift_m": 20},
  {"text": T("Notre-Dame", "Notre-Dame"), "at": [48.85306, 2.35], "from": 1165, "to": 1189, "lift_m": 80},
  {"text": T("Louvre", "Louvre"), "at": [48.86025, 2.33800], "from": 1192, "to": 1215, "lift_m": 40},
  {"text": T("Sainte-Chapelle", "Sainte-Chapelle"), "at": [48.85528, 2.34500], "from": 1244, "to": 1270, "lift_m": 50},
  {"text": T("MARAIS", "MARAIS"), "at": [48.8590, 2.3610], "kind": "region", "from": 1365, "to": 1383},
  {"text": T("Bastille", "Bastille"), "at": [48.85333, 2.36917], "from": 1372, "to": 1436, "lift_m": 40},
  {"text": T("Louvre", "Louvre"), "at": [48.86025, 2.33800], "from": 1534, "to": 1563, "lift_m": 40},
  {"text": T("Tuileries", "Tuileries"), "at": [48.86222, 2.33250], "from": 1565, "to": 1571, "lift_m": 40},
  {"text": T("Pont Neuf", "Pont Neuf"), "at": [48.8575, 2.3417], "from": 1580, "to": 1604, "lift_m": 20},
  {"text": T("Place Royale", "Place Royale"), "at": [48.85556, 2.36556], "from": 1607, "to": 1632, "lift_m": 20},
  {"text": T("Les Invalides", "Les Invalides"), "at": [48.8549, 2.3125], "from": 1680, "to": 1706, "lift_m": 120},
  {"text": T("Bastille", "Bastille"), "at": [48.85333, 2.36917], "from": 1789, "to": 1790, "lift_m": 40},
  {"text": T("Arc de Triomphe", "Zafer Takı"), "at": [48.87378, 2.29503], "from": 1810, "to": 1836, "lift_m": 70},
  {"text": T("Palais Garnier", "Palais Garnier"), "at": [48.87194, 2.33167], "from": 1873, "to": 1886, "lift_m": 50},
  {"text": T("Montmartre", "Montmartre"), "at": [48.88667, 2.34306], "kind": "place", "from": 1873, "to": 1886, "lift_m": 60},
  {"text": T("Eiffel Tower", "Eiffel Kulesi"), "at": [48.85822, 2.29450], "from": 1889.2, "to": 1918, "lift_m": 320},
  {"text": T("Tuileries", "Tuileries"), "at": [48.86222, 2.33250], "from": 1871.25, "to": 1872, "lift_m": 40},
  {"text": T("Hôtel de Ville", "Hôtel de Ville"), "at": [48.85639, 2.35222], "from": 1871.25, "to": 1872, "lift_m": 40},
  {"text": T("La Défense", "La Défense"), "at": [48.8920, 2.2400], "kind": "place", "from": 1958, "to": 1989, "lift_m": 100},
  {"text": T("Montparnasse", "Montparnasse"), "at": [48.8421, 2.3220], "from": 1973, "to": 1976, "lift_m": 230},
  {"text": T("Centre Pompidou", "Centre Pompidou"), "at": [48.86064, 2.35225], "from": 1977, "to": 1989, "lift_m": 60},
  {"text": T("Notre-Dame", "Notre-Dame"), "at": [48.85306, 2.35], "from": 2019, "to": 2024.4, "lift_m": 80},
  {"text": T("Eiffel Tower", "Eiffel Kulesi"), "at": [48.85822, 2.29450], "from": 2024.5, "lift_m": 320},
  {"text": T("Montmartre", "Montmartre"), "at": [48.88667, 2.34306], "kind": "place", "from": 2025, "lift_m": 60},
 ],
 "youtube": {
  "title": T("Paris: 2,300 Years in 15 Minutes (3D Timelapse)", "Paris: 15 Dakikada 2.300 Yıl (3D Timelapse)"),
  "description": T(
   "Around 250 BC a Gallic tribe, the Parisii, settled on the Seine. Watch Paris grow from Roman Lutetia on the left bank to a walled "
   "medieval capital, a city of kings and revolution, Haussmann's boulevards and today's city of 2.1 million: the island city, Notre-Dame, "
   "the walls of Philip Augustus and Charles V, the Louvre and the Bastille, the Pont Neuf, the Farmers-General and Thiers walls, the siege "
   "and fires of 1870–1871, the Eiffel Tower, the Périphérique and the 2019 Notre-Dame fire, with the year and the population on screen.",
   "MÖ 250 civarında Galyalı Parisii kabilesi Seine kıyısına yerleşti. Paris'in sol yakadaki Roma kasabası Lutetia'dan surlarla çevrili "
   "bir Orta Çağ başkentine, kralların ve devrimin şehrine, Haussmann'ın bulvarlarına ve bugünün 2,1 milyonluk şehrine büyüyüşünü izleyin: "
   "ada şehri, Notre-Dame, Philippe Auguste ve V. Charles surları, Louvre ve Bastille, Pont Neuf, Fermiers Généraux ve Thiers surları, "
   "1870–1871 kuşatması ve yangınları, Eiffel Kulesi, Périphérique ve 2019 Notre-Dame yangını; yıl ve nüfus ekranda."),
  "tags": ["paris history", "history of paris", "lutetia", "medieval paris", "3d timelapse", "city evolution", "how paris grew",
           "paris timelapse", "notre dame", "haussmann", "walls of paris", "french revolution", "eiffel tower", "urban history"],
  "hashtags": ["#Paris", "#History", "#Timelapse"],
  "playlist": T("Cities of Europe", "Avrupa Şehirleri"),
  "playlist_desc": T("European cities rebuilt in 3D, from the first stone to the skyline.", "Avrupa şehirleri 3D olarak, ilk taştan siluete."),
  "thumb": {"line1": T("Paris", "Paris"), "line2": T("2,300 YEARS", "2.300 YIL"), "line3": T("From a Gallic village to the City of Light", "Galya köyünden Işık Şehri'ne"),
            "extra": "&mood=golden&pitch=30&az=0&cam=48.8600,2.3300,7.0"},
 },
 "sources": [
  {"title": "History of Paris — Wikipedia", "url": "https://en.wikipedia.org/wiki/History_of_Paris"},
  {"title": "Timeline of Paris — Wikipedia (Wikiwand)", "url": "https://www.wikiwand.com/en/articles/Timeline_of_Paris"},
  {"title": "Lutetia — Wikipedia", "url": "https://en.wikipedia.org/wiki/Lutetia"},
  {"title": "Paris-Lutetia: from earliest times to c. 1000 — Indiana University", "url": "https://paris10.sitehost.iu.edu/ParisOSS/Day_1_Early_Paris/Ancient_Early_Medieval/Jones_Ancient_Background.html"},
  {"title": "The amphitheatre — Archéologie de Paris (Ministère de la Culture)", "url": "https://archeologie.culture.gouv.fr/paris/en/amphitheatre"},
  {"title": "Arènes de Lutèce — Wikipedia", "url": "https://en.wikipedia.org/wiki/Ar%C3%A8nes_de_Lut%C3%A8ce"},
  {"title": "Thermes de Cluny — Wikipedia", "url": "https://en.wikipedia.org/wiki/Thermes_de_Cluny"},
  {"title": "City walls of Paris — Wikipedia", "url": "https://en.wikipedia.org/wiki/City_walls_of_Paris"},
  {"title": "Wall of Philip II Augustus — Wikipedia", "url": "https://en.wikipedia.org/wiki/Wall_of_Philip_II_Augustus"},
  {"title": "Wall of Charles V — Wikipedia", "url": "https://en.wikipedia.org/wiki/Wall_of_Charles_V"},
  {"title": "Wall of the Fermiers généraux — Wikipedia", "url": "https://en.wikipedia.org/wiki/Wall_of_the_Fermiers_g%C3%A9n%C3%A9raux"},
  {"title": "Thiers wall — Wikipedia", "url": "https://en.wikipedia.org/wiki/Thiers_wall"},
  {"title": "Siege of Paris (845) — Wikipedia", "url": "https://en.wikipedia.org/wiki/Siege_of_Paris_(845)"},
  {"title": "Paris: Medieval development and discord — Britannica", "url": "https://www.britannica.com/place/Paris/Medieval-development-and-discord-12th-century-to-16th-century"},
  {"title": "Notre-Dame de Paris — Wikipedia", "url": "https://en.wikipedia.org/wiki/Notre-Dame_de_Paris"},
  {"title": "Medieval Louvre Castle — Wikipedia", "url": "https://en.wikipedia.org/wiki/Medieval_Louvre_Castle"},
  {"title": "Sainte-Chapelle — Wikipedia", "url": "https://kiwix.lema.org/wikipedia_en_all_mini_2024-02/A/Sainte-Chapelle"},
  {"title": "Bastille — Wikipedia", "url": "https://en.wikipedia.org/wiki/Bastille"},
  {"title": "Hôtel de Ville, Paris — Wikipedia", "url": "https://bafybeiemxf5abjwjbikoz4mc3a3dla6ual3jsgpdr4cjr3oz3evfyavhwq.ipfs.4everland.io/wiki/H%C3%B4tel_de_Ville%2C_Paris.html"},
  {"title": "Tuileries Palace — Wikipedia", "url": "https://en.wikipedia.org/wiki/Tuileries_Palace"},
  {"title": "Pont Neuf — Wikipedia", "url": "https://kiwix.lema.org/wikipedia_en_all_mini_2024-02/A/Pont_Neuf"},
  {"title": "Place des Vosges — Wikipedia", "url": "https://en.wikipedia.org/wiki/Place_des_Vosges"},
  {"title": "Les Invalides — Wikipedia", "url": "https://en.wikipedia.org/wiki/Les_Invalides"},
  {"title": "Arc de Triomphe — Wikipedia", "url": "https://kiwix.lema.org/wikipedia_en_all_mini_2024-02/A/Arc_De_Triomphe"},
  {"title": "Haussmann's renovation of Paris — Wikipedia", "url": "https://en.wikipedia.org/wiki/Haussmann%27s_renovation_of_Paris"},
  {"title": "Palais Garnier — Wikipedia", "url": "https://en.wikipedia.org/wiki/Palais_Garnier"},
  {"title": "Sacré-Cœur, Paris — Wikipedia", "url": "https://en.wikipedia.org/wiki/Sacr%C3%A9-C%C5%93ur,_Paris"},
  {"title": "Siege of Paris (1870–1871) — Wikipedia", "url": "https://en.wikipedia.org/wiki/Siege_of_Paris_(1870%E2%80%931871)"},
  {"title": "Fires in the Paris Commune — Wikipedia", "url": "https://en.wikipedia.org/wiki/Fires_in_the_Paris_Commune"},
  {"title": "Eiffel Tower — Wikipedia", "url": "https://kiwix.lema.org/wikipedia_en_all_mini_2024-02/A/Tour_Eiffel"},
  {"title": "Paris Métro Line 1 — Wikipedia", "url": "https://en.wikipedia.org/wiki/Paris_M%C3%A9tro_Line_1"},
  {"title": "Liberation of Paris — Wikipedia", "url": "https://en.wikipedia.org/wiki/Liberation_of_Paris"},
  {"title": "History of the place — Paris La Défense", "url": "https://www.ladefense.fr/en/history-place"},
  {"title": "Boulevard Périphérique — Wikipedia", "url": "https://en.wikipedia.org/wiki/Boulevard_P%C3%A9riph%C3%A9rique"},
  {"title": "Tour Montparnasse — Wikipedia", "url": "https://ipfs.ssi.eecc.de/ipns/en.wikipedia-on-ipfs.org/wiki/Tour_Montparnasse"},
  {"title": "Centre Pompidou — Wikipedia", "url": "https://kiwix.lema.org/wikipedia_en_all_mini_2024-02/A/Pompidou_Center"},
  {"title": "Grande Arche — Wikipedia", "url": "https://en.wikipedia.org/wiki/Grande_Arche"},
  {"title": "Paris 2024 Opening Ceremony on the Seine — Olympics.com", "url": "https://olympics.com/en/news/paris-2024-olympic-games-opening-ceremony-flame-cauldron"},
  {"title": "Demographics of Paris — Wikipedia (census table)", "url": "https://www.safekipedia.com/discoverer/wiki/Demographics_of_Paris"},
  {"title": "Paris — population by census — City Population", "url": "https://www.citypopulation.de/en/france/admin/75__paris"},
  {"title": "Populations des départements en 2023 — INSEE", "url": "https://www.insee.fr/fr/statistiques/8680659"},
 ],
}
total = sum(s_["seconds"] for s_ in S)
mins = round(total / 60)
city["intro"] = T(f"2,300 Years in {mins} Minutes", f"{mins} Dakikada 2.300 Yıl")
city["youtube"]["title"] = T(f"Paris: 2,300 Years in {mins} Minutes (3D Timelapse)", f"Paris: {mins} Dakikada 2.300 Yıl (3D Timelapse)")
json.dump(city, open(os.path.join(HERE, "city.json"), "w"), ensure_ascii=False, indent=1)
print("segments", len(S), "duration", total, "s =", f"{total // 60}:{total % 60:02d}")
