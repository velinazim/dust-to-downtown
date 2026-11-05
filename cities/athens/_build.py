"""Builds cities/athens/city.json. Every date/figure is from research.md (sources listed there).
Run: python3 cities/athens/_build.py
Wall courses, district outlines and the Long Walls are simplified traces (marked ≈ in research.md)."""
import json, math, os

T = lambda en, tr: {"en": en, "tr": tr}
HERE = os.path.dirname(os.path.abspath(__file__))
rect = lambda s, w, n, e: [(s, w), (n, w), (n, e), (s, e)]


def L(pts):
    return [[round(a, 5), round(b, 5)] for a, b in pts]


def scale(pts, c, f):
    return [(c[0] + (a - c[0]) * f, c[1] + (b - c[1]) * f) for a, b in pts]


def circle(c, r_m, n=14, sx=1.0):
    kx = 111.32 * math.cos(math.radians(c[0])); kz = 110.574
    return [(c[0] + r_m / 1000 / kz * math.sin(2 * math.pi * i / n), c[1] + sx * r_m / 1000 / kx * math.cos(2 * math.pi * i / n)) for i in range(n)]


# ------------------------------------------------------------------ geography (lat, lon); ≈ traces, see research.md
ACRO_C = (37.97167, 23.72611)
PARTHENON = (37.97156, 23.72663)
ACRO = [(37.97150, 23.72480), (37.97195, 23.72500), (37.97235, 23.72600), (37.97230, 23.72720), (37.97185, 23.72830),
        (37.97120, 23.72800), (37.97105, 23.72650), (37.97120, 23.72540)]
ACRO_SLOPE = scale(ACRO, ACRO_C, 1.55)
AGORA = [(37.97640, 23.72150), (37.97630, 23.72400), (37.97440, 23.72450), (37.97400, 23.72200)]
AREO = circle((37.9720, 23.7230), 70, 10)
HILLS = [(37.9748, 23.7168), (37.9742, 23.7198), (37.9718, 23.7212), (37.9692, 23.7232), (37.9664, 23.7232), (37.9654, 23.7203),
         (37.9672, 23.7172), (37.9712, 23.7158)]                       # Nymphs – Pnyx – Muses (Philopappos) ridge
LYCA = circle((37.9820, 23.7440), 420, 14)
NATGARDEN = [(37.9765, 23.7355), (37.9765, 23.7395), (37.9718, 23.7395), (37.9718, 23.7362)]
# Themistoclean wall (479 BC) through the gates located by ToposText (≈ between them)
GATES = {"dipylon": (37.9786, 23.7190), "sacred": (37.97806, 23.71856), "piraeus": (37.9758, 23.7160),
         "acharnian": (37.9810, 23.7287), "diochares": (37.97484, 23.73225), "itonian": (37.9676, 23.73143), "halade": (37.96663, 23.7288)}
THEM = [GATES["dipylon"], (37.9802, 23.7228), GATES["acharnian"], (37.9795, 23.7318), (37.9775, 23.7330), GATES["diochares"],
        (37.9718, 23.7330), GATES["itonian"], GATES["halade"], (37.9652, 23.7245), (37.9650, 23.7200), (37.9668, 23.7168),
        (37.9715, 23.7150), GATES["piraeus"], GATES["sacred"]]
THEM_RING = THEM + [THEM[0]]
CITY_C = (37.9745, 23.7245)
ARCHAIC = scale(THEM, CITY_C, 0.62)
EAST = [(37.9745, 23.7335), (37.9722, 23.7405), (37.9672, 23.7395), (37.9667, 23.7330), (37.9690, 23.7322)]   # Roman east quarter (≈)
VALERIAN = THEM[:6] + [(37.9752, 23.7340), (37.9740, 23.7405), (37.9700, 23.7415), (37.9668, 23.7395), (37.9668, 23.7335)] + THEM[7:]
# post-Herulian wall (EIE): Acropolis NW → Panathenaic Way → Stoa of Attalos → Library of Hadrian → ~350 m east → back south
POSTHER = [(37.97195, 23.72470), (37.97350, 23.72400), (37.97500, 23.72440), (37.97530, 23.72520), (37.97520, 23.72950),
           (37.97300, 23.72960), (37.97230, 23.72760)]
# Haseki wall (1778, WP course)
HASEKI = [(37.97076, 23.72444), (37.97030, 23.72780), (37.97018, 23.73203), (37.97300, 23.73480), (37.97584, 23.73447),
          (37.97800, 23.73150), (37.98000, 23.72800), (37.98330, 23.72250), (37.97980, 23.72000), (37.97640, 23.72000),
          (37.97200, 23.72300)]
HASEKI_RING = HASEKI + [HASEKI[0]]
TOWN_C = (37.9752, 23.7268)
PLAKA = [(37.97240, 23.72790), (37.97080, 23.73020), (37.97210, 23.73260), (37.97450, 23.73150), (37.97500, 23.72850)]
BYZ = scale(HASEKI, TOWN_C, 0.72)
# Long Walls (≈, ~180 m apart; the Middle wall through the excavated point at Tavros)
N_LONG = [(37.9742, 23.7163), (37.9645, 23.7015), (37.9572, 23.6760), (37.9505, 23.6505)]
M_LONG = [(37.9690, 23.7158), (37.96235, 23.7026), (37.9555, 23.6775), (37.9482, 23.6540)]
PHALERIC = [(37.9653, 23.7215), (37.9560, 23.7160), (37.9450, 23.7095), (37.9372, 23.7055), (37.9280, 23.7020), (37.9185, 23.7000)]
PIR_WALL = [(37.9418, 23.6340), (37.9455, 23.6335), (37.9478, 23.6335), (37.9510, 23.6420), (37.9505, 23.6505), (37.9482, 23.6540), (37.9452, 23.6600),
            (37.9405, 23.6620), (37.9378, 23.6633)]
PIRAEUS = [(37.9500, 23.6330), (37.9505, 23.6500), (37.9460, 23.6610), (37.9370, 23.6640), (37.9330, 23.6500),
           (37.9360, 23.6330), (37.9430, 23.6290)]
# new town of 1833 (Kleanthis–Schaubert triangle: Omonia apex, Ermou base)
OMONIA = (37.98417, 23.72778); SYNTAGMA = (37.975841, 23.734465)
TRI = [OMONIA, SYNTAGMA, (37.97600, 23.72600), (37.97700, 23.71950)]
CITY19 = [(37.9950, 23.7150), (37.9960, 23.7350), (37.9880, 23.7500), (37.9760, 23.7520), (37.9660, 23.7480), (37.9600, 23.7330),
          (37.9600, 23.7150), (37.9680, 23.7080), (37.9800, 23.7050), (37.9900, 23.7080)]
PIRAEUS19 = [(37.9560, 23.6300), (37.9570, 23.6550), (37.9500, 23.6700), (37.9370, 23.6680), (37.9310, 23.6500),
             (37.9350, 23.6300), (37.9450, 23.6230)]
REFUGEE = {  # 1922–1923 refugee towns (EKT names; positions approximate)
 "Nea Smyrni": circle((37.9480, 23.7140), 700), "Kallithea": circle((37.9570, 23.7010), 650),
 "Nea Ionia": circle((38.0370, 23.7550), 700), "Kaisariani": circle((37.9650, 23.7660), 450),
 "Vyronas": circle((37.9570, 23.7540), 500), "Nikaia": circle((37.9660, 23.6450), 700), "Aigaleo": circle((37.9920, 23.6800), 650),
}
MID = [(38.0200, 23.7000), (38.0250, 23.7400), (38.0100, 23.7700), (37.9850, 23.7750), (37.9550, 23.7650), (37.9400, 23.7400),
       (37.9380, 23.7100), (37.9450, 23.6700), (37.9600, 23.6500), (37.9800, 23.6650), (38.0050, 23.6800)]
BASIN = [(37.9600, 23.5750), (37.9750, 23.6250), (37.9950, 23.6600), (38.0300, 23.6750), (38.0700, 23.7050), (38.0850, 23.7550),
         (38.0750, 23.8100), (38.0450, 23.8250), (38.0050, 23.8000), (37.9750, 23.7850), (37.9400, 23.7720), (37.9000, 23.7680),
         (37.8650, 23.7680), (37.8500, 23.7450), (37.8800, 23.7150), (37.9100, 23.6950), (37.9300, 23.6750), (37.9400, 23.6100)]
HYM = [(38.0000, 23.7950), (37.9900, 23.8300), (37.9300, 23.8350), (37.8800, 23.8050), (37.9000, 23.7800), (37.9500, 23.7820),
       (37.9800, 23.7880)]
AIG = [(38.0700, 23.6400), (38.0300, 23.6600), (38.0000, 23.6550), (37.9850, 23.6350), (38.0200, 23.6150)]
TOURKO = circle((38.0200, 23.7600), 900, 12)
ELLINIKON = [(37.9050, 23.7200), (37.9000, 23.7450), (37.8820, 23.7400), (37.8800, 23.7180)]
ELL_NEW = [(37.8920, 23.7180), (37.8900, 23.7350), (37.8810, 23.7330), (37.8800, 23.7200)]
GEO_EDITS = []

# ------------------------------------------------------------------ population (research.md): sourced anchors, log-interpolated
ANCH = [(1760, 10000), (1824, 9040), (1833, 4000), (1839, 26473), (1870, 44500), (1879, 63374), (1896, 123000), (1907, 167479),
        (1928, 802000), (1940, 1124109), (1951, 1368142), (1971, 2101103), (2001, 3130841), (2021, 3041131)]


def P(y):
    if y >= 2021: return 3041131
    for y0, p0 in ANCH:
        if y == y0: return p0
    for (y0, p0), (y1, p1) in zip(ANCH, ANCH[1:]):
        if y0 <= y <= y1:
            u = (y - y0) / (y1 - y0); return int(round(math.exp(math.log(p0) + (math.log(p1) - math.log(p0)) * u), -3))
    raise ValueError(y)
PI = lambda a, b: [P(a), P(b)]


# ------------------------------------------------------------------ timeline
def seg(frm, to, sec, era, title=None, sub=None, pop=None, cam=None, chapter=None):
    d = {"from": frm, "to": to, "seconds": sec, "era": era, "city_name": ATH}
    if title: d["title"] = title; d["sub"] = sub
    if pop is not None: d["population"] = pop
    if cam: d["camera"] = {"center": [cam[0], cam[1]], "dist_km": cam[2]}
    if chapter: d["chapter"] = chapter
    return d

ATH = T("Athens", "Atina")
BRZ = T("Neolithic and Bronze Age", "Neolitik ve Tunç Çağı"); MYC = T("Mycenaean Age", "Miken Çağı")
IRON = T("Early Iron Age", "Erken Demir Çağı"); ARC = T("Archaic Athens", "Arkaik Atina"); CLA = T("Classical Athens", "Klasik Atina")
HEL = T("Hellenistic Age", "Helenistik Çağ"); ROM = T("Roman Empire", "Roma İmparatorluğu"); BYZE = T("Byzantine Empire", "Bizans İmparatorluğu")
DUC = T("Duchy of Athens", "Atina Dükalığı"); OTT = T("Ottoman Empire", "Osmanlı İmparatorluğu")
REV = T("Greek Revolution", "Yunan Bağımsızlık Savaşı"); KIN = T("Kingdom of Greece", "Yunanistan Krallığı")
OCC = T("Axis Occupation", "Mihver İşgali"); MOD = T("Modern Greece", "Modern Yunanistan"); TODAY = T("Today", "Bugün")

AC = (37.9718, 23.7258)
S = [
 seg(-3000, -1301, 17, BRZ, T("The First Settlers", "İlk Yerleşimciler"),
     T("By about 3000 BC people live on the slopes of the Acropolis, a steep rock above the plain",
       "MÖ 3000 civarında insanlar ovaya bakan dik bir kaya olan Akropolis'in yamaçlarında yaşar"),
     cam=(AC[0], AC[1], 2.0), chapter=T("The Bronze Age Rock", "Tunç Çağı Kayası")),
 seg(-1300, -1101, 18, MYC, T("A Mycenaean Citadel", "Bir Miken Kalesi"),
     T("c. 1200 BC: a massive 'Cyclopean' wall rings the palace on top of the Acropolis",
       "MÖ ~1200: devasa bir 'Kiklop' duvarı Akropolis'in tepesindeki sarayı çevreler"),
     cam=(AC[0], AC[1], 1.6)),
 seg(-1100, -701, 7, IRON, cam=(37.9728, 23.7250, 2.4)),
 seg(-700, -595, 7, ARC, cam=(37.9730, 23.7250, 2.6)),
 seg(-594, -567, 15, ARC, T("Solon's Laws", "Solon'un Yasaları"),
     T("594 BC: the statesman Solon reforms the laws of Athens", "MÖ 594: devlet adamı Solon Atina'nın yasalarını yeniden düzenler"),
     cam=(37.9738, 23.7240, 2.4), chapter=T("Archaic Athens", "Arkaik Atina")),
 seg(-566, -521, 15, ARC, T("A Festival for Athena", "Athena İçin Bir Bayram"),
     T("566 BC: the Panathenaic Games are reorganised; c. 530 a large temple of Athena rises",
       "MÖ 566: Panathenaia oyunları yeniden düzenlenir; ~530'da büyük bir Athena tapınağı yükselir"),
     cam=(AC[0], AC[1], 1.8)),
 seg(-520, -509, 15, ARC, T("A Temple for Zeus", "Zeus İçin Bir Tapınak"),
     T("c. 520 BC: the tyrant's family begins a giant temple of Zeus; it will take 650 years",
       "MÖ ~520: tiranın ailesi dev bir Zeus tapınağına başlar; bitmesi 650 yıl sürecek"),
     cam=(37.9705, 23.7300, 2.0)),
 seg(-508, -481, 16, ARC, T("Democracy", "Demokrasi"),
     T("508/507 BC: Cleisthenes' reforms give Athens its democracy", "MÖ 508/507: Kleisthenes'in reformları Atina'ya demokrasisini verir"),
     cam=(37.9728, 23.7225, 2.2)),
 seg(-480, -479.6, 18, CLA, T("The Persians Burn Athens", "Persler Atina'yı Yakıyor"),
     T("480 BC: the Persian army takes and burns Athens, then loses the sea battle of Salamis",
       "MÖ 480: Pers ordusu Atina'yı alıp yakar, ardından Salamis deniz savaşını kaybeder"),
     cam=(37.9600, 23.6700, 11.0), chapter=T("The Golden Age", "Altın Çağ")),
 seg(-479.5, -462, 18, CLA, T("The Themistoclean Wall", "Themistokles Suru"),
     T("479 BC: the Athenians rebuild their city wall in haste; it has at least 13 gates",
       "MÖ 479: Atinalılar şehir surunu aceleyle yeniden yapar; surun en az 13 kapısı vardır"),
     cam=(37.9735, 23.7245, 3.6)),
 seg(-461, -448, 18, CLA, T("The Long Walls", "Uzun Duvarlar"),
     T("460s–450s BC: Long Walls about 6 km long tie Athens to the sea at Piraeus and Phaleron",
       "MÖ 460'lar–450'ler: ~6 km'lik Uzun Duvarlar Atina'yı Pire ve Faliron'da denize bağlar"),
     cam=(37.9580, 23.6850, 10.0)),
 seg(-447, -438, 20, CLA, T("The Parthenon", "Parthenon"),
     T("447–438 BC: the Parthenon rises on the Acropolis; its sculptures are finished by 432",
       "MÖ 447–438: Parthenon Akropolis'te yükselir; heykelleri 432'ye dek tamamlanır"),
     cam=(PARTHENON[0], PARTHENON[1], 1.2)),
 seg(-437, -431, 16, CLA, T("The Propylaia", "Propylaia"),
     T("437–432 BC: the architect Mnesikles builds the great gateway to the Acropolis",
       "MÖ 437–432: mimar Mnesikles Akropolis'in görkemli giriş kapısını yapar"),
     cam=(37.97176, 23.72560, 1.3)),
 seg(-430, -422, 17, CLA, T("The Plague", "Veba"),
     T("430 BC: plague kills a quarter to a third of the people; Pericles dies in 429",
       "MÖ 430: veba halkın dörtte biri ile üçte birini öldürür; Perikles 429'da ölür"),
     cam=(37.9740, 23.7240, 3.2)),
 seg(-421, -405, 16, CLA, T("The Erechtheion", "Erektheion"),
     T("421–406 BC: in the middle of a long war, the Erechtheion is built on the Acropolis",
       "MÖ 421–406: uzun bir savaşın ortasında Akropolis'te Erektheion inşa edilir"),
     cam=(37.97209, 23.72641, 1.2)),
 seg(-404, -395, 16, CLA, T("Athens Surrenders", "Atina Teslim Oluyor"),
     T("404 BC: Athens loses the Peloponnesian War and must pull down its Long Walls",
       "MÖ 404: Atina Peloponez Savaşı'nı kaybeder ve Uzun Duvarlarını yıkmak zorunda kalır"),
     cam=(37.9590, 23.6850, 9.0)),
 seg(-394, -339, 14, CLA, T("The Walls Rise Again", "Duvarlar Yeniden Yükseliyor"),
     T("394 BC: the admiral Conon rebuilds the walls of Athens and Piraeus",
       "MÖ 394: amiral Konon Atina ve Pire'nin surlarını yeniden yaptırır"),
     cam=(37.9590, 23.6850, 9.5)),
 seg(-338, -331, 15, HEL, T("Chaeronea", "Khaironeia"),
     T("2 August 338 BC: Philip II of Macedon defeats Athens and Thebes at Chaeronea",
       "2 Ağustos MÖ 338: Makedonyalı II. Filip, Atina ve Thebai'yi Khaironeia'da yener"),
     cam=(37.9730, 23.7260, 4.0)),
 seg(-330, -160, 16, HEL, T("Built in Stone", "Taştan Yapılar"),
     T("c. 330 BC: under Lycurgus the Theatre of Dionysus and a stadium are built in stone",
       "MÖ ~330: Likurgos döneminde Dionysos Tiyatrosu ve bir stadyum taştan yapılır"),
     cam=(37.9698, 23.7340, 2.0)),
 seg(-159, -88, 15, HEL, T("The Stoa of Attalos", "Attalos Stoası"),
     T("159–138 BC: King Attalos II of Pergamon gives the Agora a 120 m, two-storey stoa",
       "MÖ 159–138: Bergama kralı II. Attalos, Agora'ya 120 m'lik iki katlı bir stoa armağan eder"),
     cam=(37.9752, 23.7238, 1.4)),
 seg(-87, -86, 18, ROM, T("Sulla's Siege", "Sulla'nın Kuşatması"),
     T("1 March 86 BC: Sulla's Romans break in at the Kerameikos and sack Athens",
       "1 Mart MÖ 86: Sulla'nın Romalıları Kerameikos'tan girer ve Atina'yı yağmalar"),
     cam=(37.9700, 23.7050, 5.5), chapter=T("Roman Athens", "Roma Atinası")),
 seg(-85, -56, 7, ROM, cam=(37.9735, 23.7245, 3.4)),
 seg(-55, 129, 16, ROM, T("Gifts from Rome", "Roma'dan Armağanlar"),
     T("c. 50 BC: the Tower of the Winds; c. 15 BC: Agrippa builds a concert hall in the Agora",
       "MÖ ~50: Rüzgârlar Kulesi; MÖ ~15: Agrippa Agora'ya bir konser salonu yaptırır"),
     cam=(37.9748, 23.7250, 1.6)),
 seg(130, 160, 18, ROM, T("Hadrian's Athens", "Hadrianus'un Atinası"),
     T("AD 131/132: Hadrian completes the Temple of Olympian Zeus and builds an arch and a library",
       "MS 131/132: Hadrianus Olimposlu Zeus Tapınağı'nı bitirir; bir kemer ve kütüphane yaptırır"),
     cam=(37.9715, 23.7310, 2.4)),
 seg(161, 266, 15, ROM, T("The Odeon of Herodes", "Herodes Odeonu"),
     T("AD 161: Herodes Atticus builds a 5,000-seat odeon in memory of his wife Regilla",
       "MS 161: Herodes Atticus, eşi Regilla'nın anısına 5.000 kişilik bir odeon yaptırır"),
     cam=(37.97076, 23.72444, 1.4)),
 seg(267, 395, 18, ROM, T("The Heruli", "Heruller"),
     T("AD 267: the Heruli sack Athens; the town shrinks behind a small new wall",
       "MS 267: Heruller Atina'yı yağmalar; şehir küçük yeni bir surun ardına çekilir"),
     cam=(37.9735, 23.7260, 3.0)),
 seg(396, 528, 7, ROM, cam=(37.9738, 23.7262, 2.4)),
 seg(529, 1017, 16, BYZE, T("The Schools Close", "Okullar Kapanıyor"),
     T("529: Emperor Justinian closes the schools of philosophy in Athens",
       "529: İmparator Justinianus Atina'daki felsefe okullarını kapatır"),
     cam=(37.9735, 23.7262, 2.4), chapter=T("Byzantines and Crusaders", "Bizanslılar ve Haçlılar")),
 seg(1018, 1203, 16, BYZE, T("An Emperor's Pilgrimage", "Bir İmparatorun Hac Yolculuğu"),
     T("1018: Emperor Basil II visits the Parthenon, now a church of the Virgin Mary",
       "1018: İmparator II. Basileios, artık bir Meryem Ana kilisesi olan Parthenon'u ziyaret eder"),
     cam=(PARTHENON[0], PARTHENON[1], 1.4)),
 seg(1204, 1310, 16, DUC, T("The Duchy of Athens", "Atina Dükalığı"),
     T("1204: crusaders take Athens; Otto de la Roche rules it as a Frankish duchy",
       "1204: Haçlılar Atina'yı alır; Otto de la Roche burayı bir Frank dükalığı olarak yönetir"),
     cam=(37.9740, 23.7262, 2.6)),
 seg(1311, 1387, 15, DUC, T("The Catalans", "Katalanlar"),
     T("15 March 1311: the Catalan Company defeats the duke and takes Athens",
       "15 Mart 1311: Katalan Kumpanyası dükü yener ve Atina'yı ele geçirir"),
     cam=(37.9740, 23.7262, 2.8)),
 seg(1388, 1455, 14, DUC, T("The Acciaioli", "Acciaioli Ailesi"),
     T("1388: the Florentine Nerio Acciaioli takes Athens; his family rules it until 1458",
       "1388: Floransalı Nerio Acciaioli Atina'yı alır; ailesi şehri 1458'e dek yönetir"),
     cam=(AC[0], AC[1], 2.0)),
 seg(1456, 1639, 17, OTT, T("Ottoman Athens", "Osmanlı Atinası"),
     T("1456: the Ottomans take the city; in 1458 the Acropolis surrenders and Mehmed II visits",
       "1456: Osmanlılar şehri alır; 1458'de Akropolis teslim olur ve II. Mehmed şehri ziyaret eder"),
     cam=(37.9745, 23.7262, 2.6), chapter=T("Ottoman Athens", "Osmanlı Atinası")),
 seg(1640, 1686, 7, OTT, cam=(37.9745, 23.7265, 2.6)),
 seg(1687, 1687.99, 20, OTT, T("The Parthenon Explodes", "Parthenon Havaya Uçuyor"),
     T("26 September 1687: Venetian guns ignite Ottoman gunpowder stored in the Parthenon",
       "26 Eylül 1687: Venedik topları Parthenon'da depolanan Osmanlı barutunu ateşler"),
     cam=(PARTHENON[0], PARTHENON[1], 1.6)),
 seg(1688, 1777, 16, OTT, T("The Venetians Leave", "Venedikliler Çekiliyor"),
     T("April 1688: the Venetians withdraw, and 4,000–5,000 Athenians leave with them",
       "Nisan 1688: Venedikliler çekilir ve 4.000–5.000 Atinalı onlarla birlikte ayrılır"),
     cam=(37.9748, 23.7265, 3.0)),
 seg(1778, 1800, 16, OTT, T("The Haseki Wall", "Haseki Suru"),
     T("1778: the governor Hadji Ali Haseki has a wall with seven gates built around the town",
       "1778: vali Hacı Ali Haseki kasabanın çevresine yedi kapılı bir sur yaptırır"),
     pop=10000, cam=(37.9758, 23.7270, 3.2)),
 seg(1801, 1820, 15, OTT, T("Elgin's Marbles", "Elgin Mermerleri"),
     T("1801–1812: agents of Lord Elgin remove sculptures from the Parthenon",
       "1801–1812: Lord Elgin'in adamları Parthenon'dan heykelleri söker"),
     pop=10000, cam=(PARTHENON[0], PARTHENON[1], 1.3)),
 seg(1821, 1825, 15, REV, T("Revolution", "Devrim"),
     T("1821: the Greek War of Independence begins; in June 1822 the Acropolis garrison surrenders",
       "1821: Yunan Bağımsızlık Savaşı başlar; Haziran 1822'de Akropolis garnizonu teslim olur"),
     pop=[10000, 9040], cam=(37.9745, 23.7265, 2.8), chapter=T("Independence", "Bağımsızlık")),
 seg(1826, 1832, 18, REV, T("Siege of the Acropolis", "Akropolis Kuşatması"),
     T("1826–1827: Kütahi Pasha besieges the Acropolis for 11 months; the town is left in ruins",
       "1826–1827: Kütahi Paşa Akropolis'i 11 ay kuşatır; kasaba harabeye döner"),
     pop=[9040, P(1832)], cam=(37.9740, 23.7262, 2.6)),
 seg(1833, 1835, 18, KIN, T("Capital of Greece", "Yunanistan'ın Başkenti"),
     T("1833: about 4,000 people live in Athens; in 1834 it becomes the capital of Greece",
       "1833: Atina'da yaklaşık 4.000 kişi yaşar; 1834'te şehir Yunanistan'ın başkenti olur"),
     pop=PI(1833, 1835), cam=(37.9775, 23.7280, 3.4), chapter=T("Capital of Greece", "Yunanistan'ın Başkenti")),
 seg(1836, 1842, 16, KIN, T("A New Town and a Palace", "Yeni Bir Şehir ve Bir Saray"),
     T("1836–1843: King Otto's palace, today the Parliament, rises above the new street plan",
       "1836–1843: bugün Parlamento olan Kral Otto'nun sarayı yeni sokak planının üzerinde yükselir"),
     pop=PI(1836, 1842), cam=(37.9775, 23.7320, 2.6)),
 seg(1843, 1868, 16, KIN, T("Syntagma", "Sintagma"),
     T("3 September 1843: a night uprising outside the palace wins Greece a constitution",
       "3 Eylül 1843: saray önündeki bir gece ayaklanması Yunanistan'a anayasa kazandırır"),
     pop=PI(1843, 1868), cam=(37.97584, 23.73447, 2.0)),
 seg(1869, 1895, 16, KIN, T("The Railway to Piraeus", "Pire Demiryolu"),
     T("27 February 1869: the 8.8 km railway from Thiseio to Piraeus opens",
       "27 Şubat 1869: Thiseio ile Pire arasındaki 8,8 km'lik demiryolu açılır"),
     pop=PI(1869, 1895), cam=(37.9610, 23.6820, 8.5)),
 seg(1896, 1921, 17, KIN, T("The First Olympics", "İlk Olimpiyatlar"),
     T("6–15 April 1896: the first modern Olympic Games are held in the Panathenaic Stadium",
       "6–15 Nisan 1896: ilk modern Olimpiyat Oyunları Panathinaiko Stadı'nda yapılır"),
     pop=PI(1896, 1921), cam=(37.9690, 23.7404, 1.8)),
 seg(1922, 1940, 18, KIN, T("The Refugees", "Mülteciler"),
     T("1922–1923: some 75,000 refugee families from Asia Minor settle in and around Athens",
       "1922–1923: Anadolu'dan gelen ~75.000 mülteci aile Atina ve çevresine yerleşir"),
     pop=PI(1922, 1940), cam=(37.9700, 23.7150, 11.0), chapter=T("Twentieth Century", "Yirminci Yüzyıl")),
 seg(1941, 1944.8, 16, OCC, T("Occupation and Famine", "İşgal ve Kıtlık"),
     T("27 April 1941: German troops enter Athens; tens of thousands die in the famine of 1941–42",
       "27 Nisan 1941: Alman askerleri Atina'ya girer; 1941–42 kıtlığında on binlerce kişi ölür"),
     pop=PI(1941, 1944.8), cam=(37.9760, 23.7250, 7.0)),
 seg(1944.81, 1967, 17, MOD, T("The Apartment Boom", "Apartman Patlaması"),
     T("After the war, the polykatoikia apartment block spreads across the whole plain",
       "Savaştan sonra polikatikia apartmanları bütün ovaya yayılır"),
     pop=PI(1944.81, 1967), cam=(37.9800, 23.7200, 14.0)),
 seg(1968, 1981, 16, MOD, T("Athens Tower", "Atina Kulesi"),
     T("1968–1971: the 28-floor, 103 m Athens Tower rises above the apartment blocks",
       "1968–1971: 28 katlı, 103 m'lik Atina Kulesi apartmanların üzerinde yükselir"),
     pop=PI(1968, 1981), cam=(37.9846, 23.7609, 3.0)),
 seg(1982, 1999, 15, MOD, T("A New Olympic Stadium", "Yeni Bir Olimpiyat Stadı"),
     T("8 September 1982: the Olympic Stadium in Marousi is inaugurated",
       "8 Eylül 1982: Marusi'deki Olimpiyat Stadı açılır"),
     pop=PI(1982, 1999), cam=(38.0361, 23.7876, 4.0)),
 seg(2000, 2003, 15, MOD, T("Metro and Airport", "Metro ve Havalimanı"),
     T("28 January 2000: the metro opens; in March 2001 a new airport replaces Ellinikon",
       "28 Ocak 2000: metro açılır; Mart 2001'de yeni havalimanı Ellinikon'un yerini alır"),
     pop=PI(2000, 2003), cam=(37.9500, 23.7600, 18.0), chapter=T("Modern Athens", "Modern Atina")),
 seg(2004, 2008, 16, MOD, T("The Olympics Return", "Olimpiyatlar Geri Dönüyor"),
     T("13–29 August 2004: Athens hosts the Summer Olympic Games for the second time",
       "13–29 Ağustos 2004: Atina Yaz Olimpiyat Oyunları'na ikinci kez ev sahipliği yapar"),
     pop=PI(2004, 2008), cam=(38.0300, 23.7800, 5.0)),
 seg(2009, 2015, 15, MOD, T("The Acropolis Museum", "Akropolis Müzesi"),
     T("20 June 2009: the new Acropolis Museum opens below the rock",
       "20 Haziran 2009: yeni Akropolis Müzesi kayanın eteğinde açılır"),
     pop=PI(2009, 2015), cam=(37.9700, 23.7275, 1.5)),
 seg(2016, 2020, 15, MOD, T("A Centre by the Sea", "Deniz Kıyısında Bir Merkez"),
     T("2016: Renzo Piano's Stavros Niarchos cultural centre opens at Faliro",
       "2016: Renzo Piano'nun Stavros Niarkos kültür merkezi Faliro'da açılır"),
     pop=PI(2016, 2020), cam=(37.9397, 23.6917, 3.0)),
 seg(2021, 2025, 16, TODAY, T("The Ellinikon", "Ellinikon"),
     T("From 2021 the old airport becomes a new district; its 200 m tower reaches full height in 2026",
       "2021'den itibaren eski havalimanı yeni bir semte dönüşür; 200 m'lik kulesi 2026'da tamamlanır"),
     pop=PI(2021, 2025), cam=(37.8850, 23.7280, 4.5)),
 seg(2026, 2026, 20, TODAY, T("Athens Today", "Bugünün Atinası"),
     T("From a hilltop settlement to 3,041,131 people in the urban area (2021 census)",
       "Bir tepe yerleşiminden kentsel alanda 3.041.131 kişiye (2021 sayımı)"),
     pop=[P(2021), 3041131], cam=(37.9750, 23.7250, 22.0)),
]


def wall(name, path, built, removed=None, height="mid", towers=90, draw=3.0, **kw):
    d = {"name": name, "path": L(path), "built": built, "height": height, "towers_m": towers, "draw_s": draw}
    if removed is not None: d["removed"] = removed
    d.update(kw); return d


ACRO_RING = scale(ACRO, ACRO_C, 1.06)
walls = [
 wall("Mycenaean (Cyclopean) wall", ACRO_RING + [ACRO_RING[0]], -1200, -467, height="mid", towers=0, draw=3.0),
 wall("Classical Acropolis wall", ACRO_RING + [ACRO_RING[0]], -467, None, height="mid", towers=0, draw=2.0),
 wall("Themistoclean wall", THEM_RING, -479.4, -86, height="mid", towers=70, draw=4.0),
 wall("Piraeus walls (≈)", PIR_WALL, -479, -404, height="mid", towers=80, draw=3.0),
 wall("North Long Wall (≈)", N_LONG, -460, -404, height="low", towers=120, draw=4.0),
 wall("Phaleric Wall (≈)", PHALERIC, -460, -404, height="low", towers=120, draw=4.0),
 wall("Middle Long Wall (≈)", M_LONG, -445, -404, height="low", towers=120, draw=3.0),
 wall("Piraeus walls (Conon, ≈)", PIR_WALL, -394, -86, height="mid", towers=80, draw=3.0),
 wall("North Long Wall (Conon, ≈)", N_LONG, -394, -86, height="low", towers=120, draw=3.0),
 wall("Middle Long Wall (Conon, ≈)", M_LONG, -394, -86, height="low", towers=120, draw=3.0),
 wall("Valerian wall (≈)", VALERIAN + [VALERIAN[0]], 256, 1100, height="mid", towers=70, draw=3.0),
 wall("Post-Herulian wall (≈)", POSTHER + [POSTHER[0]], 280, 1778, height="mid", towers=50, draw=2.5),
 wall("Haseki wall", HASEKI_RING, 1778.2, 1835, height="low", towers=0, draw=3.5),
]

roads = [
 {"name": "Sacred Way (≈)", "path": L([GATES["sacred"], (37.9830, 23.7050), (37.9900, 23.6900), (38.0050, 23.6600), (38.0150, 23.6350)]),
  "from": -600, "kind": "road", "width_m": 12},
 {"name": "Panathenaic Way (≈)", "path": L([GATES["dipylon"], (37.9768, 23.7215), (37.9745, 23.7240), (37.9725, 23.7245)]),
  "from": -560, "kind": "road", "width_m": 12},
 {"name": "Athens–Piraeus railway (≈)", "path": L([(37.9770, 23.7185), (37.9700, 23.7080), (37.9600, 23.6880), (37.9530, 23.6650),
  (37.9480, 23.6436)]), "from": 1869.15, "kind": "rail", "width_m": 20},
]

landmarks = [
 {"type": "palace", "name": T("Mycenaean palace (≈)", "Miken sarayı (≈)"), "at": [37.97200, 23.72630], "built": -1300, "removed": -1100,
  "rise_s": 4, "size_m": [45, 30, 10], "colors": {"wall": "#cdb99a", "roof": "#8a6f55"}},
 {"type": "temple", "name": T("Olympieion platform", "Olympieion temeli"), "at": [37.9694, 23.7337], "built": -520, "removed": 125, "rise_s": 3,
  "size_m": [108, 41, 3], "colors": {"wall": "#d9d0bd"}},
 {"type": "temple", "name": T("Temple of Olympian Zeus", "Olimposlu Zeus Tapınağı"), "at": [37.9694, 23.7337], "built": 125, "rise_s": 14,
  "size_m": [108, 41, 20], "colors": {"wall": "#ece4d2"}},
 {"type": "temple", "name": T("Temple of Hephaestus", "Hephaistos Tapınağı"), "at": [37.9756167, 23.7213917], "built": -449, "rise_s": 20,
  "size_m": [32, 14, 11], "colors": {"wall": "#e3d8c2"}},
 {"type": "temple", "name": T("Parthenon", "Parthenon"), "at": list(PARTHENON), "built": -447, "removed": 1687.74, "rise_s": 18,
  "size_m": [70, 31, 14], "scale": 1.6, "colors": {"wall": "#ece4d0"}, "additions": [{"type": "minarets", "year": 1458.6, "count": 1}]},
 {"type": "temple", "name": T("Parthenon (ruin)", "Parthenon (harabe)"), "at": list(PARTHENON), "built": 1687.74, "rise_s": 0.3,
  "size_m": [70, 31, 9], "scale": 1.6, "colors": {"wall": "#d6ccb6", "roof": "#d6ccb6"}},
 {"type": "box", "name": T("Propylaia", "Propylaia"), "at": [37.97176, 23.72522], "built": -437, "rise_s": 12, "size_m": [48, 24, 12],
  "colors": {"wall": "#e6dece", "roof": "#cfc6b4"}},
 {"type": "temple", "name": T("Temple of Athena Nike", "Athena Nike Tapınağı"), "at": [37.97154, 23.72487], "built": -427, "rise_s": 4,
  "size_m": [9, 6, 7], "colors": {"wall": "#ece4d0"}},
 {"type": "temple", "name": T("Erechtheion", "Erektheion"), "at": [37.97209, 23.72641], "built": -421, "rise_s": 14, "size_m": [24, 13, 11], "scale": 1.4,
  "colors": {"wall": "#ece4d0"}},
 {"type": "circus", "name": T("Panathenaic Stadium", "Panathinaiko Stadı"), "at": [37.9690, 23.7404], "built": -330, "rise_s": 5,
  "size_m": [204, 83], "rot_deg": 70, "colors": {"wall": "#e8e2d4"}},
 {"type": "box", "name": T("Stoa of Attalos", "Attalos Stoası"), "at": [37.975003, 23.7242], "built": -159, "rise_s": 10, "size_m": [116, 20, 11],
  "rot_deg": 90, "colors": {"wall": "#e6dcc8", "roof": "#a0583f"}},
 {"type": "tower", "name": T("Tower of the Winds", "Rüzgârlar Kulesi"), "at": [37.9742, 23.72705], "built": -50, "rise_s": 3, "size_m": [8, 8, 12],
  "colors": {"wall": "#e6dcc8", "roof": "#cfc6b4"}},
 {"type": "box", "name": T("Odeon of Agrippa", "Agrippa Odeonu"), "at": [37.97510, 23.72300], "built": -15, "removed": 267, "rise_s": 4,
  "size_m": [50, 45, 20], "colors": {"wall": "#e3d8c2", "roof": "#a0583f"}},
 {"type": "box", "name": T("Arch of Hadrian", "Hadrianus Kemeri"), "at": [37.97018, 23.73203], "built": 131, "rise_s": 3, "size_m": [14, 4, 18],
  "rot_deg": -40, "colors": {"wall": "#e6dece"}},
 {"type": "box", "name": T("Library of Hadrian", "Hadrianus Kütüphanesi"), "at": [37.9755, 23.7257], "built": 132, "rise_s": 6, "size_m": [122, 82, 12],
  "colors": {"wall": "#e3d8c2", "roof": "#a0583f"}},
 {"type": "box", "name": T("Odeon of Herodes Atticus", "Herodes Atticus Odeonu"), "at": [37.970756, 23.724444], "built": 161, "removed": 267.05,
  "rise_s": 5, "size_m": [80, 48, 22], "colors": {"wall": "#d9cdb4", "roof": "#8a6f55"}},
 {"type": "box", "name": T("Odeon of Herodes (ruin)", "Herodes Odeonu (harabe)"), "at": [37.970756, 23.724444], "built": 267.05, "rise_s": 0.3,
  "size_m": [80, 48, 12], "colors": {"wall": "#cfc3aa", "roof": "#cfc3aa"}},
 {"type": "church", "name": T("Kapnikarea", "Kapnikarea"), "at": [37.9763, 23.7285], "built": 1050, "rise_s": 3, "size_m": [20, 12, 10],
  "colors": {"wall": "#c99f78", "roof": "#8a5a3c"}},
 {"type": "church", "name": T("Little Metropolis", "Küçük Metropolis"), "at": [37.97504, 23.73001], "built": 1190, "rise_s": 3, "size_m": [16, 10, 10],
  "colors": {"wall": "#e3d8c2", "roof": "#8a5a3c"}},
 {"type": "mosque", "name": T("Fethiye Mosque", "Fethiye Camii"), "at": [37.97444, 23.72694], "built": 1668, "rise_s": 4, "size_m": [20, 20, 14],
  "colors": {"minarets": 1}},
 {"type": "palace", "name": T("Royal Palace (Parliament)", "Kraliyet Sarayı (Parlamento)"), "at": [37.97528, 23.73694], "built": 1836, "rise_s": 14,
  "size_m": [110, 85, 22], "scale": 1.2, "colors": {"wall": "#efe6cf", "roof": "#8f8a80"}},
 {"type": "circus", "name": T("Panathenaic Stadium (1896)", "Panathinaiko Stadı (1896)"), "at": [37.9690, 23.7404], "built": 1895.5, "rise_s": 3,
  "size_m": [204, 83], "rot_deg": 70, "colors": {"wall": "#f2efe6"}},
 {"type": "skyscraper", "name": T("Athens Tower", "Atina Kulesi"), "at": [37.984587, 23.760874], "built": 1968, "rise_s": 10, "size_m": [40, 30, 103],
  "colors": {"wall": "#3f4a52"}},
 {"type": "stadium", "name": T("Olympic Stadium", "Olimpiyat Stadı"), "at": [38.03607, 23.7876], "built": 1980, "rise_s": 8, "size_m": [300, 240, 40],
  "colors": {"wall": "#d9d9d4"}},
 {"type": "box", "name": T("Acropolis Museum", "Akropolis Müzesi"), "at": [37.969108, 23.728299], "built": 2007, "rise_s": 6, "size_m": [140, 110, 23],
  "colors": {"wall": "#b9c0c4", "roof": "#8f989d"}},
 {"type": "box", "name": T("Stavros Niarchos Centre", "Stavros Niarkos Merkezi"), "at": [37.93972, 23.69167], "built": 2013, "rise_s": 10,
  "size_m": [170, 70, 30], "rot_deg": -30, "colors": {"wall": "#dfe3e4", "roof": "#c8ccce"}},
 {"type": "skyscraper", "name": T("Riviera Tower", "Riviera Kulesi"), "at": [37.88284, 23.72685], "built": 2023, "rise_s": 30, "size_m": [40, 40, 200],
  "colors": {"wall": "#d9dee0"}},
]

districts = [
 {"name": "Early settlement on the slopes (≈)", "style": "ancient", "poly": L(scale(ACRO, ACRO_C, 2.4)), "holes": [L(ACRO)],
  "from": -3000, "to": -2200, "density": 0.22, "grain_m": 70, "grow_from": [37.9730, 23.7258]},
 {"name": "Mycenaean citadel (≈)", "style": "ancient", "poly": L(ACRO), "from": -1290, "to": -1220, "density": 0.55, "grain_m": 30,
  "grow_from": [37.9720, 23.7263], "fade": [-700, -620, 0.0]},
 {"name": "Archaic town (≈)", "style": "ancient", "poly": L(ARCHAIC), "holes": [L(ACRO_SLOPE), L(AGORA), L(AREO)], "from": -1050, "to": -650,
  "density": 0.55, "grain_m": 55, "grow_from": [37.9745, 23.7240]},
 {"name": "Classical city", "style": "ancient", "poly": L(THEM), "holes": [L(ACRO_SLOPE), L(AGORA), L(AREO), L(HILLS)], "from": -478, "to": -440,
  "density": 0.82, "grain_m": 45, "grow_from": [37.9745, 23.7235], "fade": [-86.6, -86.0, 0.6]},
 {"name": "Piraeus (≈)", "style": "ancient", "poly": L(PIRAEUS), "from": -478, "to": -445, "density": 0.6, "grain_m": 55,
  "grow_from": [37.9440, 23.6460], "fade": [-86.9, -86.4, 0.05]},
 {"name": "Roman Athens", "style": "roman", "poly": L(THEM), "holes": [L(ACRO_SLOPE), L(AGORA), L(AREO), L(HILLS)], "from": -40, "to": 150,
  "density": 0.7, "grain_m": 50, "grow_from": [37.9748, 23.7255], "fade": [267.0, 267.3, 0.12]},
 {"name": "Roman east quarter (≈)", "style": "roman", "poly": L(EAST), "from": 125, "to": 170, "density": 0.6, "grain_m": 55,
  "grow_from": [37.9705, 23.7340], "fade": [267.0, 267.3, 0.0]},
 {"name": "Late Roman town", "style": "roman", "poly": L(POSTHER), "holes": [L(ACRO_SLOPE)], "from": 280, "to": 420, "density": 0.75, "grain_m": 40,
  "grow_from": [37.9742, 23.7265]},
 {"name": "Byzantine town (≈)", "style": "medieval", "poly": L(BYZ), "holes": [L(ACRO_SLOPE), L(AGORA), L(AREO)], "from": 900, "to": 1180,
  "density": 0.6, "grain_m": 48, "grow_from": [37.9745, 23.7268]},
 {"name": "Ottoman town (≈)", "style": "ottoman", "poly": L(HASEKI), "holes": [L(ACRO_SLOPE), L(AGORA), L(AREO)], "from": 1460, "to": 1660,
  "density": 0.62, "grain_m": 48, "grow_from": [37.9748, 23.7268], "fade": [1688.15, 1688.4, 0.45]},
 {"name": "18th-century town (≈)", "style": "ottoman", "poly": L(HASEKI), "holes": [L(ACRO_SLOPE), L(AGORA), L(AREO)], "from": 1700, "to": 1790,
  "density": 0.62, "grain_m": 48, "grow_from": [37.9748, 23.7268], "fade": [1826.6, 1827.4, 0.15]},
 {"name": "New town of 1833 (Kleanthis–Schaubert)", "style": "stone", "poly": L(TRI), "holes": [L(AGORA)], "from": 1834, "to": 1865, "density": 0.72,
  "grain_m": 50, "grow_from": [37.9775, 23.7300]},
 {"name": "Plaka (rebuilt)", "style": "stone", "poly": L(PLAKA), "from": 1834, "to": 1855, "density": 0.8, "grain_m": 40, "grow_from": [37.9730, 23.7300]},
 {"name": "19th-century Athens (≈)", "style": "victorian", "poly": L(CITY19), "holes": [L(ACRO_SLOPE), L(AGORA), L(AREO), L(HILLS), L(LYCA), L(NATGARDEN), L(TRI), L(PLAKA)],
  "from": 1860, "to": 1921, "density": 0.75, "grain_m": 55, "grow_from": [37.9780, 23.7290]},
 {"name": "Piraeus (19th century, ≈)", "style": "victorian", "poly": L(PIRAEUS19), "from": 1840, "to": 1915, "density": 0.75, "grain_m": 60,
  "grow_from": [37.9450, 23.6450]},
]
for nm, poly in REFUGEE.items():
    districts.append({"name": f"{nm} (refugee settlement, ≈)", "style": "suburb", "poly": L(poly), "from": 1923, "to": 1935, "density": 0.7,
                      "grain_m": 60, "grow_from": list(poly[0])})
districts += [
 {"name": "Interwar Greater Athens (≈)", "style": "suburb", "poly": L(MID), "holes": [L(CITY19), L(PIRAEUS19), L(HILLS), L(LYCA), L(TOURKO)] + [L(p) for p in REFUGEE.values()],
  "from": 1925, "to": 1950, "density": 0.45, "grain_m": 80, "grow_from": [37.9780, 23.7250]},
 {"name": "Post-war apartment city (centre)", "style": "modern", "poly": L(CITY19), "holes": [L(ACRO_SLOPE), L(AGORA), L(AREO), L(HILLS), L(LYCA), L(NATGARDEN), L(PLAKA)],
  "from": 1952, "to": 1975, "density": 0.85, "grain_m": 55, "grow_from": [37.9800, 23.7300]},
 {"name": "Post-war basin (≈)", "style": "modern", "poly": L(BASIN), "holes": [L(CITY19), L(HYM), L(AIG), L(TOURKO), L(ELLINIKON), L(LYCA), L(HILLS)],
  "from": 1950, "to": 1995, "density": 0.7, "grain_m": 90, "grow_from": [37.9800, 23.7250]},
 {"name": "Ellinikon redevelopment (≈)", "style": "modern", "poly": L(ELL_NEW), "from": 2022, "to": 2026, "density": 0.5, "grain_m": 70,
  "grow_from": [37.8850, 23.7250]},
]

fires = [
 {"year": -480, "poly": L(scale(ARCHAIC, CITY_C, 1.05)), "duration_s": 7, "plumes": 6},
 {"year": 267.0, "poly": L(THEM), "duration_s": 6, "plumes": 5},
]
smoke = [
 {"at": list(ACRO_C), "from": -480, "to": -479.7, "scale": 1.2},
 {"at": [37.9786, 23.7190], "from": -86.5, "to": -86.0, "scale": 1.0},
 {"at": [37.9430, 23.6450], "from": -86.9, "to": -86.4, "scale": 1.0},
 {"at": list(PARTHENON), "from": 1687.73, "to": 1687.85, "scale": 1.4},
 {"at": list(ACRO_C), "from": 1826.5, "to": 1827.4, "scale": 1.0},
 {"at": list(ACRO_C), "from": 1822.3, "to": 1822.45, "scale": 0.8},
]
open_spaces = [
 {"name": "Acropolis rock and slopes", "poly": L(ACRO_SLOPE)},
 {"name": "Ancient Agora", "poly": L(AGORA)},
 {"name": "Areopagus", "poly": L(AREO)},
 {"name": "Hills of the Nymphs, Pnyx and Muses", "poly": L(HILLS)},
 {"name": "Lycabettus", "poly": L(LYCA)},
 {"name": "National Garden", "poly": L(NATGARDEN)},
 {"name": "Hymettus", "poly": L(HYM)},
 {"name": "Aigaleo", "poly": L(AIG)},
 {"name": "Tourkovounia (≈)", "poly": L(TOURKO)},
]
labels = [
 {"text": T("ACROPOLIS", "AKROPOLİS"), "at": [37.97167, 23.72611], "kind": "region", "from": -3000, "to": -1301},
 {"text": T("SARONIC GULF", "SARONİK KÖRFEZİ"), "at": [37.9050, 23.6500], "kind": "water", "from": -3000},
 {"text": T("Acropolis", "Akropolis"), "at": [37.97200, 23.72630], "from": -1300, "to": -1101, "lift_m": 30},
 {"text": T("Pnyx", "Pnyx"), "at": [37.971667, 23.719444], "kind": "place", "from": -508, "to": -481},
 {"text": T("Olympieion", "Olympieion"), "at": [37.9694, 23.7337], "from": -520, "to": -509, "lift_m": 15},
 {"text": T("Salamis", "Salamis"), "at": [37.95001, 23.5397], "kind": "place", "from": -480, "to": -479.6},
 {"text": T("Piraeus", "Pire"), "at": [37.9440, 23.6460], "kind": "place", "from": -461, "to": -395},
 {"text": T("Phaleron", "Faliron"), "at": [37.9373, 23.7062], "kind": "place", "from": -461, "to": -448},
 {"text": T("LONG WALLS", "UZUN DUVARLAR"), "at": [37.9610, 23.6880], "kind": "region", "from": -461, "to": -448},
 {"text": T("Parthenon", "Parthenon"), "at": list(PARTHENON), "from": -444, "to": -438, "lift_m": 40},
 {"text": T("Propylaia", "Propylaia"), "at": [37.97176, 23.72522], "from": -435, "to": -431, "lift_m": 30},
 {"text": T("Erechtheion", "Erektheion"), "at": [37.97209, 23.72641], "from": -418, "to": -405, "lift_m": 30},
 {"text": T("Kerameikos", "Kerameikos"), "at": [37.97833, 23.71889], "kind": "place", "from": -479.5, "to": -462},
 {"text": T("Theatre of Dionysus", "Dionysos Tiyatrosu"), "at": [37.9703, 23.7278], "kind": "place", "from": -330, "to": -160},
 {"text": T("Panathenaic Stadium", "Panathinaiko Stadı"), "at": [37.9690, 23.7404], "from": -325, "to": -160, "lift_m": 25},
 {"text": T("Stoa of Attalos", "Attalos Stoası"), "at": [37.975003, 23.7242], "from": -150, "to": -88, "lift_m": 25},
 {"text": T("Kerameikos", "Kerameikos"), "at": [37.97833, 23.71889], "kind": "place", "from": -87, "to": -86},
 {"text": T("Tower of the Winds", "Rüzgârlar Kulesi"), "at": [37.9742, 23.72705], "from": -45, "to": 50, "lift_m": 20},
 {"text": T("Odeon of Agrippa", "Agrippa Odeonu"), "at": [37.97510, 23.72300], "from": 51, "to": 129, "lift_m": 30},
 {"text": T("Temple of Olympian Zeus", "Olimposlu Zeus Tapınağı"), "at": [37.9694, 23.7337], "from": 131, "to": 160, "lift_m": 35},
 {"text": T("Odeon of Herodes Atticus", "Herodes Atticus Odeonu"), "at": [37.970756, 23.724444], "from": 162, "to": 266, "lift_m": 30},
 {"text": T("Parthenon", "Parthenon"), "at": list(PARTHENON), "from": 1018, "to": 1203, "lift_m": 40},
 {"text": T("Acropolis", "Akropolis"), "at": [37.97200, 23.72630], "from": 1388, "to": 1455, "lift_m": 40},
 {"text": T("Parthenon", "Parthenon"), "at": list(PARTHENON), "from": 1687, "to": 1687.99, "lift_m": 40},
 {"text": T("Parthenon", "Parthenon"), "at": list(PARTHENON), "from": 1801, "to": 1820, "lift_m": 30},
 {"text": T("Royal Palace", "Kraliyet Sarayı"), "at": [37.97528, 23.73694], "from": 1838, "to": 1842, "lift_m": 40},
 {"text": T("Syntagma", "Sintagma"), "at": [37.975841, 23.734465], "kind": "place", "from": 1843, "to": 1868},
 {"text": T("Omonia", "Omonia"), "at": list(OMONIA), "kind": "place", "from": 1836, "to": 1842},
 {"text": T("Piraeus", "Pire"), "at": [37.9440, 23.6460], "kind": "place", "from": 1869, "to": 1895},
 {"text": T("Panathenaic Stadium", "Panathinaiko Stadı"), "at": [37.9690, 23.7404], "from": 1896, "to": 1921, "lift_m": 25},
 {"text": T("Nea Smyrni", "Nea Smirni"), "at": [37.9480, 23.7140], "kind": "place", "from": 1923, "to": 1940},
 {"text": T("Nea Ionia", "Nea Ionia"), "at": [38.0370, 23.7550], "kind": "place", "from": 1923, "to": 1940},
 {"text": T("Piraeus", "Pire"), "at": [37.9440, 23.6460], "kind": "place", "from": 1923, "to": 1940},
 {"text": T("Lycabettus", "Likavitos"), "at": [37.9820, 23.7440], "kind": "place", "from": 1945, "to": 1967, "lift_m": 60},
 {"text": T("Athens Tower", "Atina Kulesi"), "at": [37.984587, 23.760874], "from": 1970, "to": 1981, "lift_m": 120},
 {"text": T("Olympic Stadium", "Olimpiyat Stadı"), "at": [38.03607, 23.7876], "from": 1982.7, "to": 1999, "lift_m": 30},
 {"text": T("Ellinikon", "Ellinikon"), "at": [37.89833, 23.72944], "kind": "place", "from": 2000, "to": 2003},
 {"text": T("Olympic Stadium", "Olimpiyat Stadı"), "at": [38.03607, 23.7876], "from": 2004, "to": 2008, "lift_m": 30},
 {"text": T("Acropolis Museum", "Akropolis Müzesi"), "at": [37.969108, 23.728299], "from": 2009, "to": 2015, "lift_m": 30},
 {"text": T("Parthenon", "Parthenon"), "at": list(PARTHENON), "from": 2009, "to": 2015, "lift_m": 30},
 {"text": T("Stavros Niarchos Centre", "Stavros Niarkos Merkezi"), "at": [37.93972, 23.69167], "from": 2016, "to": 2020, "lift_m": 40},
 {"text": T("Riviera Tower", "Riviera Kulesi"), "at": [37.88284, 23.72685], "from": 2023, "to": 2025, "lift_m": 210},
 {"text": T("Acropolis", "Akropolis"), "at": [37.97200, 23.72630], "kind": "place", "from": 2026},
 {"text": T("Piraeus", "Pire"), "at": [37.9440, 23.6460], "kind": "place", "from": 2026},
 {"text": T("HYMETTUS", "HİMETTOS"), "at": [37.9450, 23.8100], "kind": "region", "from": 2026},
]

city = {
 "slug": "athens", "seed": 480, "long_ok": True,
 "name": T("Athens", "Atina"), "intro": T("5,000 Years in 15 Minutes", "15 Dakikada 5.000 Yıl"), "intro_seconds": 4.5,
 "geo": {"bbox": [37.74, 23.42, 38.24, 24.02], "cell_m": 100, "core_bbox": [37.925, 23.620, 38.000, 23.770], "core_cell_m": 30, "rivers_keep": ["__none__"]},
 "geo_edits": GEO_EDITS,
 "view": {"azimuth_deg": 0, "pitch_deg": 46, "fov": 34},
 "render": {"vertical_exaggeration": 2.2},
 "segments": S,
 "districts": districts, "walls": walls, "roads": roads, "landmarks": landmarks,
 "fires": fires, "smoke": smoke, "open_spaces": open_spaces, "labels": labels,
 "youtube": {
  "title": T("Athens: 5,000 Years in 15 Minutes (3D Timelapse)", "Atina: 15 Dakikada 5.000 Yıl (3D Timelapse)"),
  "description": T(
   "By about 3000 BC people were living on the slopes of the Acropolis. Watch Athens grow from that rock to a Mycenaean citadel, "
   "burn in the Persian invasion of 480 BC, build its walls, the Long Walls to Piraeus and the Parthenon, survive Sulla, the Heruli, "
   "Byzantine, Frankish and Ottoman rule and the explosion of 1687, shrink to a town of about 4,000 people and then become the capital "
   "of modern Greece and a city of three million: the Acropolis, the Agora, the Temple of Olympian Zeus, the Panathenaic Stadium, the "
   "Royal Palace, the 1896 and 2004 Olympics, the refugee towns of 1922, the apartment boom, the metro and the Ellinikon, with the year "
   "and the population on screen.",
   "MÖ 3000 civarında insanlar Akropolis'in yamaçlarında yaşıyordu. Atina'nın bu kayadan bir Miken kalesine dönüşmesini, MÖ 480 Pers "
   "istilasında yanmasını, surlarını, Pire'ye uzanan Uzun Duvarları ve Parthenon'u yapmasını, Sulla'yı, Herulleri, Bizans, Frank ve "
   "Osmanlı yönetimini ve 1687 patlamasını atlatmasını, ~4.000 kişilik bir kasabaya küçülüp modern Yunanistan'ın başkenti ve üç "
   "milyonluk bir şehir olmasını izleyin: Akropolis, Agora, Olimposlu Zeus Tapınağı, Panathinaiko Stadı, Kraliyet Sarayı, 1896 ve 2004 "
   "Olimpiyatları, 1922 mülteci semtleri, apartman patlaması, metro ve Ellinikon; yıl ve nüfus ekranda."),
  "tags": ["athens history", "history of athens", "ancient athens", "acropolis", "parthenon", "3d timelapse", "city evolution",
           "how athens grew", "athens timelapse", "long walls", "classical athens", "greece history", "urban history", "ιστορία της αθήνας"],
  "hashtags": ["#Athens", "#History", "#Timelapse"],
  "playlist": T("Cities of Europe", "Avrupa Şehirleri"),
  "playlist_desc": T("European cities rebuilt in 3D, from the first stone to the skyline.", "Avrupa şehirleri 3D olarak, ilk taştan siluete."),
  "thumb": {"line1": T("Athens", "Atina"), "line2": T("5,000 YEARS", "5.000 YIL"), "line3": T("From the Acropolis to a city of millions", "Akropolis'ten milyonluk bir şehre"),
            "extra": "&mood=golden&pitch=30&az=0&cam=37.9730,23.7260,4.0"},
 },
 "sources": json.load(open(os.path.join(HERE, "_sources.json"))),
}
total = sum(s_["seconds"] for s_ in S)
mins = round(total / 60)
city["intro"] = T(f"5,000 Years in {mins} Minutes", f"{mins} Dakikada 5.000 Yıl")
city["youtube"]["title"] = T(f"Athens: 5,000 Years in {mins} Minutes (3D Timelapse)", f"Atina: {mins} Dakikada 5.000 Yıl (3D Timelapse)")
json.dump(city, open(os.path.join(HERE, "city.json"), "w"), ensure_ascii=False, indent=1)
print("segments", len(S), "duration", total, "s =", f"{total // 60}:{total % 60:02d}")
