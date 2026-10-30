"""Builds cities/rome/city.json. Every date/figure is from research.md (sources listed there).
Run: python3 cities/rome/_build.py"""
import json, math, os

T = lambda en, tr: {"en": en, "tr": tr}
HERE = os.path.dirname(os.path.abspath(__file__))
rect = lambda s, w, n, e: [(s, w), (n, w), (n, e), (s, e)]


def L(pts):
    return [[round(a, 5), round(b, 5)] for a, b in pts]


# ------------------------------------------------------------------ geography (lat, lon); ≈ traces, see research.md
PALATINE = [(41.8903, 12.4858), (41.8906, 12.4880), (41.8896, 12.4894), (41.8882, 12.4889), (41.8877, 12.4866), (41.8888, 12.4852)]
ARCHAIC = [(41.8925, 12.4800), (41.8945, 12.4840), (41.8950, 12.4885), (41.8935, 12.4930), (41.8905, 12.4935), (41.8880, 12.4905),
           (41.8870, 12.4860), (41.8885, 12.4815), (41.8905, 12.4795)]
GALLIC_FIRE = [(41.8932, 12.4838), (41.8948, 12.4885), (41.8935, 12.4930), (41.8905, 12.4935), (41.8880, 12.4905), (41.8870, 12.4860),
               (41.8885, 12.4830), (41.8912, 12.4838)]
SERVIAN = [(41.8928, 12.4785), (41.8945, 12.4808), (41.8955, 12.4830), (41.8975, 12.4855), (41.8995, 12.4880), (41.9010, 12.4915),
           (41.9050, 12.4975), (41.9030, 12.5000), (41.9010, 12.5015), (41.8975, 12.5025), (41.8958, 12.5012), (41.8925, 12.5005),
           (41.8890, 12.5000), (41.8865, 12.4965), (41.8840, 12.4900), (41.8815, 12.4885), (41.8790, 12.4865), (41.8780, 12.4825),
           (41.8795, 12.4790), (41.8830, 12.4778), (41.8868, 12.4797)]
REPUBLIC = SERVIAN + [(41.8900, 12.4790)]
CAMPUS = [(41.8930, 12.4740), (41.8960, 12.4690), (41.9000, 12.4660), (41.9030, 12.4690), (41.9065, 12.4730), (41.9110, 12.4740),
          (41.9115, 12.4765), (41.9060, 12.4800), (41.9000, 12.4815), (41.8955, 12.4815), (41.8932, 12.4790)]
TRASTEVERE = [(41.8945, 12.4680), (41.8925, 12.4660), (41.8885, 12.4620), (41.8850, 12.4680), (41.8835, 12.4745), (41.8870, 12.4772),
              (41.8905, 12.4762), (41.8928, 12.4722)]
# Aurelian Walls, left bank (river N end → gates clockwise → river S end); Trastevere loop; river wall along the Campus Martius
AUR_LEFT = [(41.9117, 12.4728), (41.91153, 12.47597), (41.9128, 12.4790), (41.9108, 12.4850), (41.90944, 12.48833), (41.9096, 12.4960),
            (41.9092, 12.5011), (41.9082, 12.5070), (41.9032, 12.5088), (41.8975, 12.51028), (41.8940, 12.5130), (41.89146, 12.51524),
            (41.8880, 12.5160), (41.8868, 12.5120), (41.88583, 12.50917), (41.8830, 12.5050), (41.8805, 12.4990), (41.8770, 12.5015),
            (41.8745, 12.5040), (41.8736, 12.5019), (41.8732, 12.4950), (41.8745, 12.4880), (41.8764, 12.4808), (41.8778, 12.4762),
            (41.8790, 12.4738)]
AUR_TRAS = [(41.8830, 12.4752), (41.8839, 12.47402), (41.8855, 12.4690), (41.8875, 12.4640), (41.88844, 12.4615), (41.8900, 12.4635),
            (41.8915, 12.4660), (41.89221, 12.46761), (41.8935, 12.4690)]
AUR_RIVER = [(41.8935, 12.4712), (41.8965, 12.4680), (41.8995, 12.4665), (41.9015, 12.4675), (41.9035, 12.4705), (41.9060, 12.4728),
             (41.9090, 12.4732), (41.9117, 12.4728)]
IMPERIAL = AUR_LEFT + [(41.8840, 12.4775), (41.8900, 12.4795), (41.8930, 12.4740)] + AUR_RIVER[1:-1]
LEONINE = [(41.9031, 12.4655), (41.9040, 12.4600), (41.9050, 12.4560), (41.9045, 12.4525), (41.9020, 12.4510), (41.8995, 12.4530),
           (41.8995, 12.4580), (41.9000, 12.4630), (41.9005, 12.4655)]
FIRE64 = [(41.8915, 12.4830), (41.8935, 12.4880), (41.8960, 12.4960), (41.8945, 12.5010), (41.8900, 12.5010), (41.8860, 12.4960),
          (41.8830, 12.4900), (41.8845, 12.4820), (41.8880, 12.4810)]
ABITATO = [(41.8930, 12.4735), (41.8965, 12.4685), (41.9005, 12.4665), (41.9035, 12.4700), (41.9070, 12.4735), (41.9080, 12.4760),
           (41.9030, 12.4795), (41.8985, 12.4810), (41.8945, 12.4815), (41.8920, 12.4800), (41.8905, 12.4790)]
BORGO = [(41.9040, 12.4655), (41.9040, 12.4570), (41.9030, 12.4555), (41.9005, 12.4560), (41.9000, 12.4640), (41.9015, 12.4665)]
LATERAN_M = rect(41.8840, 12.5020, 41.8875, 12.5085)
SMM_M = rect(41.8960, 12.4955, 41.8990, 12.5010)
RENAISSANCE = [(41.8930, 12.4735), (41.8965, 12.4685), (41.9005, 12.4665), (41.9035, 12.4700), (41.9075, 12.4735), (41.9112, 12.4745),
               (41.9112, 12.4775), (41.9060, 12.4835), (41.9020, 12.4870), (41.8985, 12.4905), (41.8950, 12.4920), (41.8935, 12.4880),
               (41.8945, 12.4840), (41.8920, 12.4800), (41.8905, 12.4790)]
BAROQUE = [(41.9060, 12.4835), (41.9045, 12.4920), (41.9010, 12.4985), (41.8960, 12.5000), (41.8930, 12.4960), (41.8950, 12.4920),
           (41.8985, 12.4905), (41.9020, 12.4870)]
UMB_IN = [(41.9080, 12.4880), (41.9085, 12.5050), (41.9000, 12.5100), (41.8920, 12.5130), (41.8890, 12.5080), (41.8930, 12.4990),
          (41.8990, 12.4960), (41.9040, 12.4900)]
TESTACCIO = [(41.8800, 12.4740), (41.8800, 12.4800), (41.8770, 12.4800), (41.8765, 12.4745)]
PRATI = [(41.9135, 12.4520), (41.9145, 12.4680), (41.9085, 12.4725), (41.9045, 12.4680), (41.9050, 12.4590)]
NE_QUARTERS = [(41.9200, 12.4900), (41.9180, 12.5100), (41.9050, 12.5250), (41.8960, 12.5230), (41.8980, 12.5120), (41.9085, 12.5060), (41.9100, 12.4900)]
INTERWAR = [(41.9400, 12.4500), (41.9350, 12.4950), (41.9250, 12.5300), (41.9050, 12.5450), (41.8800, 12.5400), (41.8650, 12.5150),
            (41.8600, 12.4850), (41.8650, 12.4550), (41.8750, 12.4400), (41.8950, 12.4380), (41.9150, 12.4400), (41.9300, 12.4430)]
POSTWAR = [(41.9850, 12.4300), (41.9800, 12.5100), (41.9600, 12.5700), (41.9200, 12.6100), (41.8700, 12.6000), (41.8350, 12.5600),
           (41.8150, 12.5000), (41.8200, 12.4300), (41.8450, 12.3900), (41.8800, 12.3800), (41.9200, 12.3800), (41.9600, 12.3950)]
OUTER = [(42.0300, 12.4000), (42.0300, 12.5300), (41.9900, 12.6400), (41.9200, 12.6900), (41.8400, 12.6500), (41.7800, 12.5800),
         (41.7600, 12.4800), (41.7900, 12.3700), (41.8500, 12.3200), (41.9300, 12.3200), (41.9900, 12.3400)]
OSTIA = [(41.7450, 12.2700), (41.7450, 12.3150), (41.7250, 12.3300), (41.7200, 12.2850)]
EUR = rect(41.8260, 12.4600, 41.8420, 12.4820)
OLD_CORE = IMPERIAL
BORGHESE = [(41.9175, 12.4790), (41.9180, 12.4930), (41.9110, 12.4945), (41.9100, 12.4820)]
PAMPHILI = [(41.8920, 12.4400), (41.8890, 12.4560), (41.8820, 12.4560), (41.8830, 12.4400)]
VILLA_ADA = [(41.9340, 12.4960), (41.9330, 12.5060), (41.9260, 12.5050), (41.9270, 12.4960)]
APPIA_PARK = [(41.8700, 12.5000), (41.8600, 12.5250), (41.8200, 12.5500), (41.8100, 12.5300), (41.8500, 12.5050)]
VATICAN_G = [(41.9060, 12.4470), (41.9050, 12.4520), (41.9020, 12.4520), (41.9010, 12.4470)]
CAPITOL = (41.8933, 12.4828)
GRA = [(CAPITOL[0] + 0.1027 * math.cos(math.radians(a)), CAPITOL[1] + 0.1375 * math.sin(math.radians(a))) for a in range(0, 361, 10)]


# ------------------------------------------------------------------ timeline
def seg(frm, to, sec, era, city, title=None, sub=None, pop=None, cam=None, chapter=None):
    d = {"from": frm, "to": to, "seconds": sec, "era": era, "city_name": city}
    if title: d["title"] = title; d["sub"] = sub
    if pop is not None: d["population"] = pop
    if cam: d["camera"] = {"center": [cam[0], cam[1]], "dist_km": cam[2]}
    if chapter: d["chapter"] = chapter
    return d

IRON = T("Iron Age", "Demir Çağı"); KINGS = T("Kings of Rome", "Krallar Dönemi"); REP = T("Roman Republic", "Roma Cumhuriyeti")
LREP = T("Late Republic", "Geç Cumhuriyet"); EMP = T("Roman Empire", "Roma İmparatorluğu"); LEMP = T("Late Empire", "Geç İmparatorluk")
ROMA = T("Rome", "Roma"); MED = T("Middle Ages", "Orta Çağ"); REN = T("Renaissance", "Rönesans"); BAR = T("Baroque", "Barok")
PAPAL = T("Papal States", "Papalık Devleti"); KING = T("Kingdom of Italy", "İtalya Krallığı"); RIT = T("Italian Republic", "İtalya Cumhuriyeti")
M = 1000000
S = [
 seg(-1000, -801, 13, IRON, T("Tiber valley", "Tiber vadisi"), T("Before Rome", "Roma'dan Önce"),
     T("c. 1000 BC: villagers bury their dead in the marshy valley of the future Forum", "MÖ ~1000: köylüler, ileride Forum olacak bataklık vadiye ölülerini gömer"),
     cam=(41.8905, 12.4860, 2.6), chapter=T("Origins", "Başlangıç")),
 seg(-800, -700, 20, IRON, ROMA, T("Huts on the Palatine", "Palatin'de Kulübeler"),
     T("Legend says Rome was founded on 21 April 753 BC; huts already stood on the Palatine", "Efsaneye göre Roma 21 Nisan MÖ 753'te kuruldu; Palatin'de kulübeler zaten vardı"),
     cam=(41.8898, 12.4868, 2.8)),
 seg(-699, -560, 18, KINGS, ROMA, T("The Forum Is Drained", "Forum Kurutuluyor"),
     T("7th century BC: the first Cloaca Maxima drains the valley; c. 600 BC it is paved", "MÖ 7. yüzyıl: ilk Cloaca Maxima vadiyi kurutur; MÖ ~600'de zemin döşenir"),
     cam=(41.8908, 12.4858, 3.0)),
 seg(-559, -509, 18, KINGS, ROMA, T("Temple of Jupiter", "Jüpiter Tapınağı"),
     T("509 BC: the great temple on the Capitol is dedicated as the Republic begins", "MÖ 509: Cumhuriyet başlarken Capitolium'daki büyük tapınak açılır"),
     cam=(41.8915, 12.4845, 3.2)),
 seg(-508, -391, 7, REP, ROMA, cam=(41.8915, 12.4855, 3.4), chapter=T("The Republic", "Cumhuriyet")),
 seg(-390, -387, 15, REP, ROMA, T("The Gauls Sack Rome", "Galyalılar Roma'yı Yağmalıyor"),
     T("390 BC (or 387): Gauls burn the city; only the Capitol holds out", "MÖ 390 (ya da 387): Galyalılar şehri yakar; yalnızca Capitolium direnir"),
     cam=(41.8915, 12.4865, 3.2)),
 seg(-386, -320, 18, REP, ROMA, T("The Servian Wall", "Servius Suru"),
     T("Early 4th century BC: an 11 km stone wall, up to 10 m high, rings the hills", "MÖ 4. yüzyıl başı: 11 km uzunluğunda, 10 m'ye varan taş bir sur tepeleri çevreler"),
     cam=(41.8920, 12.4890, 4.8)),
 seg(-319, -221, 18, REP, ROMA, T("Roads and Water", "Yollar ve Su"),
     T("312 BC: Appius Claudius begins the Via Appia and Rome's first aqueduct", "MÖ 312: Appius Claudius, Via Appia'yı ve Roma'nın ilk su kemerini başlatır"),
     cam=(41.8870, 12.4930, 5.4)),
 seg(-220, -180, 7, REP, ROMA, cam=(41.8950, 12.4840, 5.4)),
 seg(-179, -142, 16, REP, ROMA, T("The First Stone Bridge", "İlk Taş Köprü"),
     T("179–142 BC: the Pons Aemilius crosses the Tiber on stone piers and arches", "MÖ 179–142: Pons Aemilius, taş ayaklar ve kemerlerle Tiber'i geçer"),
     cam=(41.8905, 12.4805, 3.2)),
 seg(-141, -63, 7, REP, ROMA, cam=(41.8935, 12.4790, 4.0)),
 seg(-62, -44, 18, LREP, ROMA, T("Pompey's Theatre", "Pompeius Tiyatrosu"),
     T("55 BC: Pompey opens a vast theatre; in 44 BC Caesar is killed in its curia", "MÖ 55: Pompeius dev bir tiyatro açar; MÖ 44'te Sezar onun meclis salonunda öldürülür"),
     cam=(41.8955, 12.4765, 3.2)),
 seg(-43, 14, 20, EMP, ROMA, T("The Rome of Augustus", "Augustus'un Roması"),
     T("His mausoleum (28 BC) and Agrippa's Pantheon rise; Rome nears a million people", "Mozolesi (MÖ 28) ve Agrippa'nın Pantheon'u yükselir; Roma bir milyona yaklaşır"),
     pop=M, cam=(41.9000, 12.4795, 4.4), chapter=T("Imperial Rome", "İmparatorluk Roması")),
 seg(15, 63, 7, EMP, ROMA, pop=M, cam=(41.8950, 12.4850, 4.8)),
 seg(64, 64.5, 18, EMP, ROMA, T("The Great Fire", "Büyük Yangın"),
     T("July AD 64: fire starts by the Circus Maximus; 10 of 14 districts are destroyed", "Temmuz MS 64: yangın Circus Maximus'ta başlar; 14 bölgenin 10'u yok olur"),
     pop=M, cam=(41.8885, 12.4895, 3.8)),
 seg(64.6, 80, 18, EMP, ROMA, T("The Colosseum", "Kolezyum"),
     T("AD 70–80: Vespasian and Titus build a 48 m arena for about 50,000 spectators", "MS 70–80: Vespasianus ve Titus, yaklaşık 50.000 kişilik 48 m'lik bir arena yapar"),
     pop=M, cam=(41.8905, 12.4912, 2.9)),
 seg(81, 125, 18, EMP, ROMA, T("Trajan's Forum", "Traianus Forumu"),
     T("AD 112: Trajan's Forum opens; Hadrian's domed Pantheon follows c. AD 125", "MS 112: Traianus Forumu açılır; Hadrianus'un kubbeli Pantheon'u MS ~125'te gelir"),
     pop=M, cam=(41.8965, 12.4825, 3.2)),
 seg(126, 200, 16, EMP, ROMA, T("Hadrian's Tomb", "Hadrianus'un Mezarı"),
     T("AD 134–139: Hadrian's mausoleum and its bridge rise across the Tiber", "MS 134–139: Hadrianus'un mozolesi ve köprüsü Tiber'in karşı yakasında yükselir"),
     pop=M, cam=(41.9010, 12.4700, 3.4)),
 seg(201, 270, 16, EMP, ROMA, T("Baths of Caracalla", "Caracalla Hamamları"),
     T("AD 216: the baths open in a walled precinct about 400 m on each side", "MS 216: hamamlar, her kenarı yaklaşık 400 m olan duvarlı bir alanda açılır"),
     pop=M, cam=(41.8830, 12.4925, 3.6)),
 seg(271, 311, 18, LEMP, ROMA, T("The Aurelian Walls", "Aurelianus Surları"),
     T("AD 271–275: a 19 km wall now encloses about 14 km² of the city", "MS 271–275: 19 km'lik yeni sur şehrin yaklaşık 14 km²'sini çevreler"),
     cam=(41.8945, 12.4885, 8.5), chapter=T("Late Empire", "Geç İmparatorluk")),
 seg(312, 400, 18, LEMP, ROMA, T("A Christian City", "Hristiyan Şehir"),
     T("After the Milvian Bridge (312) Constantine founds the Lateran (324) and St Peter's", "Milvius Köprüsü'nden (312) sonra Konstantin, Lateran'ı (324) ve St. Peter'i kurar"),
     cam=(41.8955, 12.4805, 7.2)),
 seg(401, 455.6, 18, T("Fall of the West", "Batı'nın Çöküşü"), ROMA, T("Rome Is Sacked", "Roma Yağmalanıyor"),
     T("AD 410: the Visigoths sack Rome for three days; in 455 the Vandals for two weeks", "MS 410: Vizigotlar Roma'yı üç gün yağmalar; 455'te Vandallar iki hafta"),
     cam=(41.8955, 12.4850, 6.2), chapter=T("The Fall", "Çöküş")),
 seg(456, 600, 18, T("Goths and Byzantines", "Gotlar ve Bizans"), ROMA, T("The Water Stops", "Su Kesiliyor"),
     T("c. AD 537: besieging Goths cut the aqueducts; soon fewer than 50,000 people remain", "MS ~537: kuşatan Gotlar su kemerlerini keser; kısa sürede 50.000'den az kişi kalır"),
     cam=(41.8925, 12.4855, 5.6)),
 seg(601, 845, 16, MED, ROMA, T("Down to the River", "Nehir Kıyısına"),
     T("609: the Pantheon becomes a church; the people move down to the Tiber bend", "609: Pantheon kiliseye dönüşür; halk Tiber'in kıvrımına iner"),
     cam=(41.8985, 12.4760, 4.6), chapter=T("Medieval Rome", "Orta Çağ Roması")),
 seg(846, 1083, 18, MED, ROMA, T("The Leonine Wall", "Leo Suru"),
     T("846: raiders sack Old St Peter's; Pope Leo IV then walls in the Vatican hill", "846: akıncılar Eski St. Peter'i yağmalar; Papa IV. Leo ardından Vatikan tepesini surla çevirir"),
     cam=(41.9015, 12.4610, 3.6)),
 seg(1084, 1347, 16, MED, ROMA, T("The Norman Sack", "Norman Yağması"),
     T("1084: Norman troops sack the city; Rome now has fewer than 30,000 people", "1084: Norman askerleri şehri yağmalar; Roma'da artık 30.000'den az kişi yaşar"),
     cam=(41.8930, 12.4870, 5.0)),
 seg(1348, 1419, 16, T("Late Middle Ages", "Geç Orta Çağ"), ROMA, T("Plague and Earthquake", "Veba ve Deprem"),
     T("After the Black Death fewer than 20,000 remain; in 1349 a quake hits the Colosseum", "Kara Ölüm'den sonra 20.000'den az kişi kalır; 1349'da bir deprem Kolezyum'u yıkar"),
     cam=(41.8935, 12.4850, 4.4)),
 seg(1420, 1472, 14, REN, ROMA, T("The Popes Return", "Papalar Dönüyor"),
     T("1420: Pope Martin V returns to a city of huts and ruins and begins to rebuild", "1420: Papa V. Martinus kulübe ve harabe dolu şehre döner, yeniden inşaya başlar"),
     cam=(41.8985, 12.4725, 4.4), chapter=T("Renaissance", "Rönesans")),
 seg(1473, 1505, 14, REN, ROMA, T("Ponte Sisto", "Ponte Sisto"),
     T("1473–1479: Sixtus IV builds the first new bridge over the Tiber since antiquity", "1473–1479: IV. Sixtus, antik çağdan beri Tiber'e yapılan ilk yeni köprüyü kurar"),
     cam=(41.8945, 12.4705, 3.0)),
 seg(1506, 1526, 15, REN, ROMA, T("A New St Peter's", "Yeni St. Peter"),
     T("18 April 1506: work begins on a new St Peter's in place of Constantine's basilica", "18 Nisan 1506: Konstantin'in bazilikasının yerine yeni St. Peter'in inşası başlar"),
     cam=(41.9020, 12.4565, 3.2)),
 seg(1527, 1530, 16, REN, ROMA, T("The Sack of 1527", "1527 Yağması"),
     T("6 May 1527: imperial troops sack Rome; its people fall from 55,000 to about 10,000", "6 Mayıs 1527: imparatorluk askerleri Roma'yı yağmalar; nüfus 55.000'den ~10.000'e düşer"),
     pop=[55000, 10000], cam=(41.9000, 12.4680, 4.4)),
 seg(1531, 1589, 16, REN, ROMA, T("Sixtus V Replans Rome", "V. Sixtus'un Yeni Roması"),
     T("1585–1590: Sixtus V cuts straight streets; in 1586 the Vatican obelisk is moved", "1585–1590: V. Sixtus düz caddeler açar; 1586'da Vatikan dikilitaşı yerinden taşınır"),
     cam=(41.9000, 12.4800, 6.0)),
 seg(1590, 1655, 16, BAR, ROMA, T("The Great Dome", "Büyük Kubbe"),
     T("1590: St Peter's 137 m dome is finished; by 1600 Rome has over 100,000 people", "1590: St. Peter'in 137 m'lik kubbesi biter; 1600'de Roma 100.000'i aşar"),
     pop=100000, cam=(41.9020, 12.4590, 3.8), chapter=T("Baroque Rome", "Barok Roma")),
 seg(1656, 1667, 15, BAR, ROMA, T("St Peter's Square", "St. Peter Meydanı"),
     T("1656–1667: Bernini's colonnades wrap the vast square in front of the basilica", "1656–1667: Bernini'nin sütunlu galerileri bazilikanın önündeki meydanı kuşatır"),
     cam=(41.9022, 12.4600, 2.8)),
 seg(1668, 1790, 15, BAR, ROMA, T("Grand Tour Rome", "Büyük Tur Roması"),
     T("By 1790 the city of the popes has grown to about 165,000 people", "1790'a gelindiğinde papaların şehri yaklaşık 165.000 kişiye ulaşır"),
     pop=[100000, 165000], cam=(41.8990, 12.4800, 6.5)),
 seg(1791, 1862, 7, PAPAL, ROMA, cam=(41.8990, 12.4880, 5.8)),
 seg(1863, 1869, 14, PAPAL, ROMA, T("The Railway Arrives", "Demiryolu Geliyor"),
     T("25 Feb 1863: Pius IX opens a station at Termini for three railway lines", "25 Şubat 1863: IX. Pius, üç demiryolu hattı için Termini'de bir istasyon açar"),
     cam=(41.8990, 12.4960, 5.0)),
 seg(1870, 1871.1, 16, KING, ROMA, T("The Breach of Porta Pia", "Porta Pia Gediği"),
     T("20 Sept 1870: Italian troops breach the wall near Porta Pia and take Rome", "20 Eylül 1870: İtalyan birlikleri Porta Pia yakınında suru yarar ve Roma'yı alır"),
     cam=(41.9060, 12.5000, 3.6), chapter=T("Capital of Italy", "İtalya'nın Başkenti")),
 seg(1871.2, 1910, 18, KING, ROMA, T("Capital of Italy", "İtalya'nın Başkenti"),
     T("Capital from 1871: new quarters and river walls; 209,222 people become 511,076 by 1911", "1871'den itibaren başkent: yeni mahalleler, rıhtımlar; 209.222 kişi 1911'de 511.076 olur"),
     pop=[209222, 511076], cam=(41.9000, 12.4850, 7.8)),
 seg(1911, 1936.8, 16, KING, ROMA, T("The Vittoriano", "Vittoriano"),
     T("Opened in 1911 and finished in 1935, the 81 m monument rises beside the Capitol", "1911'de açılıp 1935'te tamamlanan 81 m'lik anıt Capitolium'un yanında yükselir"),
     pop=[511076, 1133202], cam=(41.8955, 12.4835, 5.0)),
 seg(1936.9, 1950, 16, KING, ROMA, T("Road to St Peter's", "St. Peter'e Giden Yol"),
     T("1936–1950: the heart of the old Borgo is cleared for the Via della Conciliazione", "1936–1950: Via della Conciliazione için eski Borgo'nun ortası yıkılır"),
     pop=[1133202, 1626793], cam=(41.9020, 12.4620, 3.6)),
 seg(1951, 1960.9, 16, RIT, ROMA, T("The 1960 Olympics", "1960 Olimpiyatları"),
     T("Rome hosts the 1960 Games at the Stadio Olimpico; EUR is all but finished", "Roma 1960 Oyunları'nı Stadio Olimpico'da düzenler; EUR neredeyse tamamdır"),
     pop=[1626793, 2155093], cam=(41.8860, 12.4720, 14.0), chapter=T("Modern Rome", "Modern Roma")),
 seg(1961, 1981, 18, RIT, ROMA, T("The Great Expansion", "Büyük Genişleme"),
     T("By 1981 Rome counts 2.8 million people; its 68 km ring road is finished in 1970", "1981'de Roma 2,8 milyon kişiyi sayar; 68 km'lik çevre yolu 1970'te tamamlanır"),
     pop=[2155093, 2797337], cam=(41.8900, 12.4880, 26.0)),
 seg(1982, 2021, 18, T("Today", "Bugün"), ROMA, T("Rome Today", "Bugünün Roması"),
     T("The 2021 census counts 2,749,031 people in the city of Rome", "2021 sayımı Roma şehrinde 2.749.031 kişi sayar"),
     pop=[2797337, 2749031], cam=(41.8900, 12.4800, 30.0)),
 seg(2022, 2025, 22, T("Today", "Bugün"), ROMA, T("The Eternal City", "Ebedi Şehir"),
     T("From huts on the Palatine to 2.7 million people, nearly 2,800 years on", "Palatin'deki kulübelerden 2,7 milyon kişiye, yaklaşık 2.800 yıl sonra"),
     pop=2749031, cam=(41.8960, 12.4760, 8.5)),
]
SCALE_T, SCALE_Q = 1.21, 1.1   # pacing; total kept under 15:00 (channel not verified for longer uploads)
for s_ in S:
    s_["seconds"] = round(s_["seconds"] * (SCALE_T if s_.get("title") else SCALE_Q))

W = lambda c: {"wall": c}
city = {
 "slug": "rome", "seed": 753,
 "name": T("Rome", "Roma"), "intro": T("3,000 Years in 15 Minutes", "15 Dakikada 3.000 Yıl"), "intro_seconds": 4.5,
 "geo": {"bbox": [41.60, 12.10, 42.18, 12.78], "cell_m": 100, "core_bbox": [41.840, 12.400, 41.950, 12.560], "core_cell_m": 30,
         "rivers_keep": ["Tevere", "Tiber"]},
 "view": {"azimuth_deg": 70, "pitch_deg": 46, "fov": 34},
 "render": {"vertical_exaggeration": 3.0},
 "segments": S,
 "districts": [
  {"name": "Palatine huts", "style": "celtic", "poly": L(PALATINE), "from": -850, "to": -760, "density": 0.55, "grain_m": 45,
   "grow_from": [41.8893, 12.4872], "fade": [-640, -600, 0.0]},
  {"name": "Archaic Rome", "style": "ancient", "poly": L(ARCHAIC), "from": -700, "to": -540, "density": 0.6, "grow_from": [41.8905, 12.4860]},
  {"name": "Republican Rome", "style": "ancient", "poly": L(REPUBLIC), "from": -386, "to": -230, "density": 0.72, "grow_from": [41.8910, 12.4860],
   "fade": [450, 650, 0.08]},
  {"name": "Campus Martius & Trastevere (late Republic)", "style": "roman", "poly": L(CAMPUS), "from": -150, "to": -20, "density": 0.6,
   "grow_from": [41.8950, 12.4790], "fade": [450, 650, 0.1]},
  {"name": "Trastevere", "style": "roman", "poly": L(TRASTEVERE), "from": -120, "to": 0, "density": 0.65, "grow_from": [41.8895, 12.4760],
   "fade": [450, 650, 0.1]},
  {"name": "Imperial Rome", "style": "roman", "poly": L(IMPERIAL), "from": -30, "to": 60, "density": 0.82, "grow_from": [41.8930, 12.4860],
   "fade": [450, 650, 0.07]},
  {"name": "Rebuilt after the fire", "style": "roman", "poly": L(FIRE64), "from": 65, "to": 95, "density": 0.82, "grow_from": [41.8900, 12.4900],
   "fade": [450, 650, 0.07]},
  {"name": "Medieval Rome (Tiber bend)", "style": "ottoman", "poly": L(ABITATO), "from": 650, "to": 1100, "density": 0.75, "grow_from": [41.8975, 12.4720],
   "fade": [1348, 1360, 0.7]},
  {"name": "Medieval Trastevere", "style": "ottoman", "poly": L(TRASTEVERE), "from": 700, "to": 1150, "density": 0.6, "grow_from": [41.8900, 12.4740]},
  {"name": "Borgo (Leonine City)", "style": "ottoman", "poly": L(BORGO), "from": 850, "to": 1000, "density": 0.65, "grow_from": [41.9020, 12.4620]},
  {"name": "Lateran", "style": "ottoman", "poly": L(LATERAN_M), "from": 800, "to": 1000, "density": 0.45, "grow_from": [41.8858, 12.5056]},
  {"name": "Santa Maria Maggiore", "style": "ottoman", "poly": L(SMM_M), "from": 800, "to": 1000, "density": 0.45, "grow_from": [41.8975, 12.4986]},
  {"name": "Renaissance Rome", "style": "ottoman", "poly": L(RENAISSANCE), "from": 1420, "to": 1600, "density": 0.88, "grow_from": [41.8985, 12.4730]},
  {"name": "Borgo (Renaissance)", "style": "ottoman", "poly": L(BORGO), "from": 1480, "to": 1600, "density": 0.82, "grow_from": [41.9020, 12.4630]},
  {"name": "Trastevere (Renaissance)", "style": "ottoman", "poly": L(TRASTEVERE), "from": 1500, "to": 1650, "density": 0.82, "grow_from": [41.8905, 12.4730]},
  {"name": "Baroque Monti & Quirinal", "style": "ottoman", "poly": L(BAROQUE), "from": 1590, "to": 1790, "density": 0.78, "grow_from": [41.9000, 12.4870]},
  {"name": "Umbertine Esquilino", "style": "roman", "poly": L(UMB_IN), "from": 1872, "to": 1910, "density": 0.85, "grain_m": 65, "grid_deg": 30,
   "grow_from": [41.9000, 12.4990]},
  {"name": "Testaccio", "style": "roman", "poly": L(TESTACCIO), "from": 1885, "to": 1915, "density": 0.85, "grid_deg": 35, "grow_from": [41.8785, 12.4770]},
  {"name": "Prati", "style": "roman", "poly": L(PRATI), "from": 1885, "to": 1925, "density": 0.85, "grain_m": 65, "grid_deg": 15,
   "grow_from": [41.9060, 12.4680]},
  {"name": "Salario & San Lorenzo", "style": "roman", "poly": L(NE_QUARTERS), "from": 1885, "to": 1930, "density": 0.8, "grain_m": 70,
   "grow_from": [41.9080, 12.5060]},
  {"name": "Interwar Rome", "style": "modern", "poly": L(INTERWAR), "holes": [L(OLD_CORE), L(PRATI), L(NE_QUARTERS), L(BORGHESE), L(VATICAN_G)],
   "from": 1915, "to": 1950, "density": 0.7, "grain_m": 120, "grow_from": [41.8960, 12.4880]},
  {"name": "EUR", "style": "modern", "poly": L(EUR), "from": 1938, "to": 1960, "density": 0.6, "grain_m": 120, "grid_deg": 0, "grow_from": [41.8336, 12.4708]},
  {"name": "Post-war Rome", "style": "modern", "poly": L(POSTWAR), "holes": [L(INTERWAR), L(EUR)], "from": 1950, "to": 1981, "density": 0.68,
   "grain_m": 190, "grow_from": [41.8950, 12.4880]},
  {"name": "Outer suburbs", "style": "suburb", "poly": L(OUTER), "holes": [L(POSTWAR)], "from": 1965, "to": 2020, "density": 0.45,
   "grain_m": 240, "grow_from": [41.8950, 12.4880]},
  {"name": "Ostia", "style": "modern", "poly": L(OSTIA), "from": 1950, "to": 1990, "density": 0.6, "grain_m": 160, "grow_from": [41.7330, 12.2900]},
 ],
 "walls": [
  {"name": "Palatine wall", "path": L([(41.8903, 12.4856), (41.8907, 12.4881), (41.8896, 12.4896), (41.8880, 12.4890), (41.8875, 12.4865),
                                       (41.8888, 12.4850), (41.8903, 12.4856)]), "built": -725, "removed": -500, "height": "low", "towers_m": 0, "draw_s": 2.0},
  {"name": "Servian Wall", "path": L(SERVIAN), "built": -378, "removed": 300, "height": "mid", "towers_m": 0, "draw_s": 3.5},
  {"name": "Aurelian Walls", "path": L(AUR_LEFT), "built": 271, "height": "mid", "towers_m": 60, "draw_s": 4.0},
  {"name": "Aurelian Walls (Trastevere)", "path": L(AUR_TRAS), "built": 272, "height": "mid", "towers_m": 60, "draw_s": 2.0},
  {"name": "Aurelian Walls (river)", "path": L(AUR_RIVER), "built": 273, "height": "low", "towers_m": 60, "draw_s": 2.0},
  {"name": "Leonine Wall", "path": L(LEONINE), "built": 848, "height": "mid", "towers_m": 70, "draw_s": 3.0},
 ],
 "bridges": [
  {"name": "Pons Sublicius", "path": [[41.8878, 12.4788], [41.8872, 12.4775]], "built": -642, "removed": 800, "style": "wood", "width_m": 10},
  {"name": "Milvian Bridge (wood)", "path": [[41.9362, 12.4669], [41.9349, 12.4670]], "built": -206, "removed": -109, "style": "wood", "width_m": 10},
  {"name": "Milvian Bridge", "path": [[41.9362, 12.4669], [41.9349, 12.4670]], "built": -109, "style": "stone", "width_m": 12},
  {"name": "Pons Aemilius", "path": [[41.8892, 12.4802], [41.8897, 12.4787]], "built": -179, "removed": 1598, "style": "stone", "width_m": 14},
  {"name": "Pons Fabricius", "path": [[41.8915, 12.4789], [41.8908, 12.4780]], "built": -62, "style": "stone", "width_m": 10},
  {"name": "Pons Cestius", "path": [[41.8902, 12.4768], [41.8897, 12.4760]], "built": -46, "style": "stone", "width_m": 10},
  {"name": "Pons Aelius (Ponte Sant'Angelo)", "path": [[41.9025, 12.4663], [41.9013, 12.4667]], "built": 134, "style": "stone", "width_m": 14},
  {"name": "Ponte Sisto", "path": [[41.8928, 12.4713], [41.8919, 12.4702]], "built": 1475, "style": "stone", "width_m": 12},
 ],
 "roads": [
  {"name": "Via Appia", "path": L([(41.8840, 12.4895), (41.8800, 12.4945), (41.8736, 12.5019), (41.8400, 12.5300), (41.7900, 12.5750), (41.7300, 12.6250)]),
   "from": -312, "kind": "roman", "width_m": 16},
  {"name": "Via Flaminia", "path": L([(41.8955, 12.4825), (41.9050, 12.4795), (41.91153, 12.47597), (41.9250, 12.4700), (41.9349, 12.4670), (41.9450, 12.4720),
                                       (41.9900, 12.4900), (42.0500, 12.4950)]), "from": -220, "kind": "roman", "width_m": 16},
  {"name": "Railways from Termini", "path": L([(41.90083, 12.50194), (41.8960, 12.5180), (41.8870, 12.5380), (41.8700, 12.5650), (41.8400, 12.6100)]),
   "from": 1863, "kind": "rail", "width_m": 22},
  {"name": "Via dei Fori Imperiali", "path": L([(41.8958, 12.4826), (41.8930, 12.4870), (41.8910, 12.4905)]), "from": 1933, "kind": "avenue", "width_m": 30},
  {"name": "Via della Conciliazione", "path": L([(41.9022, 12.4590), (41.9023, 12.4620), (41.9025, 12.4650)]), "from": 1950, "kind": "avenue", "width_m": 40},
  {"name": "Grande Raccordo Anulare", "path": L(GRA), "from": 1970, "kind": "motorway", "width_m": 40},
 ],
 "landmarks": [
  {"type": "forum", "name": T("Roman Forum", "Roma Forumu"), "at": [41.8922, 12.4852], "built": -600, "size_m": [130, 50], "rot_deg": 35, "colors": {"column": False}},
  {"type": "circus", "name": T("Circus Maximus", "Circus Maximus"), "at": [41.8858, 12.4858], "built": -550, "removed": 1100, "size_m": [621, 118], "rot_deg": 28},
  {"type": "temple", "name": T("Temple of Jupiter", "Jüpiter Tapınağı"), "at": [41.8922, 12.4817], "built": -509, "removed": 800, "rise_s": 3,
   "size_m": [55, 60, 22], "rot_deg": 90},
  {"type": "box", "name": T("Theatre of Pompey", "Pompeius Tiyatrosu"), "at": [41.8953, 12.4736], "built": -55, "removed": 700, "size_m": [150, 95, 22],
   "colors": {"wall": "#e6dcc4"}},
  {"type": "tower", "name": T("Mausoleum of Augustus", "Augustus Mozolesi"), "at": [41.9061, 12.4764], "built": -28, "rise_s": 3, "size_m": [90, 90, 42],
   "colors": {"wall": "#e8dfcc", "roof": "#6f8a5a"}},
  {"type": "temple", "name": T("Agrippa's Pantheon", "Agrippa'nın Pantheon'u"), "at": [41.8986, 12.4768], "built": -25, "removed": 113, "size_m": [45, 25, 18], "rot_deg": 90},
  {"type": "box", "name": T("Pyramid of Cestius", "Cestius Piramidi"), "at": [41.8764, 12.4808], "built": -15, "size_m": [30, 30, 30], "colors": {"wall": "#ece6d8", "roof": "#ece6d8"}},
  {"type": "amphitheatre", "name": T("Colosseum", "Kolezyum"), "at": [41.8903, 12.4922], "built": 72, "rise_s": 6, "size_m": [189, 156, 48], "rot_deg": 20},
  {"type": "forum", "name": T("Trajan's Forum", "Traianus Forumu"), "at": [41.89542, 12.48587], "built": 108, "size_m": [300, 185], "rot_deg": 35, "colors": {"column": False}},
  {"type": "column", "name": T("Trajan's Column", "Traianus Sütunu"), "at": [41.8958, 12.4843], "built": 113, "size_m": [8, 8, 38]},
  {"type": "domechurch", "name": T("Pantheon", "Pantheon"), "at": [41.8986, 12.4768], "built": 118, "rise_s": 4, "size_m": [70, 56, 22], "rot_deg": 90,
   "colors": {"wall": "#d9cfbd", "dome": "#a39e94"}},
  {"type": "tower", "name": T("Mausoleum of Hadrian", "Hadrianus Mozolesi"), "at": [41.9031, 12.4663], "built": 135, "rise_s": 3, "size_m": [80, 80, 32],
   "colors": {"wall": "#e3d9c4", "roof": "#8f8a80"}},
  {"type": "palace", "name": T("Baths of Caracalla", "Caracalla Hamamları"), "at": [41.87944, 12.49306], "built": 212, "size_m": [400, 390, 10],
   "colors": {"wall": "#e2d2b4", "roof": "#c0694a"}},
  {"type": "box", "name": T("Caracalla bath block", "Caracalla hamam binası"), "at": [41.87944, 12.49306], "built": 214, "rise_s": 3, "size_m": [214, 110, 38],
   "colors": {"wall": "#e8dcc2", "roof": "#b4583b"}},
  {"type": "cathedral", "name": T("Lateran Basilica", "Lateran Bazilikası"), "at": [41.8858, 12.5056], "built": 318, "rise_s": 3, "size_m": [140, 50, 30],
   "colors": {"wall": "#e6dcc8", "roof": "#a9533a", "spire": False}},
  {"type": "cathedral", "name": T("Old St Peter's", "Eski St. Peter"), "at": [41.90222, 12.45333], "built": 326, "removed": 1506, "rise_s": 3,
   "size_m": [120, 60, 30], "colors": {"wall": "#e6dcc8", "roof": "#a9533a", "spire": False}},
  {"type": "church", "name": T("Santa Maria Maggiore", "Santa Maria Maggiore"), "at": [41.8975, 12.4986], "built": 432, "size_m": [85, 35, 24],
   "colors": {"wall": "#ece2cc", "roof": "#a9533a"}},
  {"type": "castle", "name": T("Castel Sant'Angelo", "Sant'Angelo Kalesi"), "at": [41.9031, 12.4663], "built": 1350, "size_m": [140, 140, 14],
   "colors": {"wall": "#cfc0a2"}},
  {"type": "domechurch", "name": T("St Peter's Basilica", "St. Peter Bazilikası"), "at": [41.90222, 12.45333], "built": 1506.1, "rise_s": 52,
   "size_m": [200, 140, 45], "colors": {"wall": "#e6dfcf", "dome": "#9aa4a8", "lantern": True}},
  {"type": "obelisk", "name": T("Vatican obelisk", "Vatikan dikilitaşı"), "at": [41.9022, 12.4573], "built": 1586, "size_m": [6, 6, 26]},
  {"type": "forum", "name": T("St Peter's Square", "St. Peter Meydanı"), "at": [41.9022, 12.4573], "built": 1657, "rise_s": 4, "size_m": [320, 240],
   "colors": {"wall": "#e3dccb", "column": False}},
  {"type": "station", "name": T("Termini", "Termini"), "at": [41.90083, 12.50194], "built": 1868, "size_m": [240, 90, 22], "rot_deg": 60},
  {"type": "palace", "name": T("Vittoriano", "Vittoriano"), "at": [41.8947, 12.4831], "built": 1885, "rise_s": 14, "size_m": [135, 130, 45],
   "colors": {"wall": "#f4f2ec", "roof": "#e9e6dd"}},
  {"type": "stadium", "name": T("Stadio Olimpico", "Stadio Olimpico"), "at": [41.93389, 12.45472], "built": 1953, "size_m": [300, 230, 40]},
 ],
 "fires": [
  {"year": -389.5, "poly": L(GALLIC_FIRE), "duration_s": 6, "plumes": 4},
  {"year": 64.2, "poly": L(FIRE64), "duration_s": 12, "plumes": 8, "plume_scale": 1.6},
 ],
 "smoke": [
  {"at": [41.9000, 12.4900], "from": 410, "to": 413, "scale": 1.4},
  {"at": [41.8930, 12.4830], "from": 455.4, "to": 455.6, "scale": 1.4},
  {"at": [41.90222, 12.45333], "from": 846, "to": 860, "scale": 1.2},
  {"at": [41.8870, 12.5000], "from": 1084, "to": 1100, "scale": 1.4},
  {"at": [41.9010, 12.4600], "from": 1527.3, "to": 1528.5, "scale": 1.3},
  {"at": [41.8980, 12.4720], "from": 1527.4, "to": 1529, "scale": 1.3},
  {"at": [41.9092, 12.5011], "from": 1870.7, "to": 1870.9, "scale": 1.0},
 ],
 "camps": [
  {"poly": L(rect(41.9110, 12.5020, 41.9160, 12.5110)), "from": 1870.6, "to": 1870.75, "count": 90},
 ],
 "open_spaces": [
  {"name": "Villa Borghese", "poly": L(BORGHESE)},
  {"name": "Villa Doria Pamphili", "poly": L(PAMPHILI)},
  {"name": "Villa Ada", "poly": L(VILLA_ADA)},
  {"name": "Appia Antica park", "poly": L(APPIA_PARK)},
  {"name": "Vatican Gardens", "poly": L(VATICAN_G)},
 ],
 "labels": [
  {"text": T("TIBER", "TİBER"), "at": [41.8975, 12.4700], "kind": "water", "to": 1870},
  {"text": T("TIBER", "TİBER"), "at": [41.9200, 12.4680], "kind": "water", "from": 1870},
  {"text": T("Palatine", "Palatin"), "at": [41.8892, 12.4872], "kind": "place", "from": -850, "to": -560, "lift_m": 30},
  {"text": T("Forum", "Forum"), "at": [41.8922, 12.4852], "from": -690, "to": -560, "lift_m": 20},
  {"text": T("Capitol", "Capitolium"), "at": [41.8922, 12.4817], "from": -540, "to": -380, "lift_m": 50},
  {"text": T("Via Appia", "Via Appia"), "at": [41.8790, 12.4960], "kind": "region", "from": -312, "to": -230},
  {"text": T("Tiber Island", "Tiber Adası"), "at": [41.8906, 12.4776], "from": -179, "to": -140, "lift_m": 20},
  {"text": T("CAMPUS MARTIUS", "CAMPUS MARTIUS"), "at": [41.8990, 12.4745], "kind": "region", "from": -60, "to": 0},
  {"text": T("Theatre of Pompey", "Pompeius Tiyatrosu"), "at": [41.8953, 12.4736], "from": -55, "to": -44, "lift_m": 40},
  {"text": T("Mausoleum of Augustus", "Augustus Mozolesi"), "at": [41.9061, 12.4764], "from": -25, "to": 14, "lift_m": 60},
  {"text": T("Circus Maximus", "Circus Maximus"), "at": [41.8858, 12.4858], "from": 64, "to": 64.5, "lift_m": 30},
  {"text": T("Colosseum", "Kolezyum"), "at": [41.8903, 12.4922], "from": 72, "to": 120, "lift_m": 70},
  {"text": T("Pantheon", "Pantheon"), "at": [41.8986, 12.4768], "from": 120, "to": 200, "lift_m": 60},
  {"text": T("Trajan's Forum", "Traianus Forumu"), "at": [41.89542, 12.48587], "from": 110, "to": 125, "lift_m": 30},
  {"text": T("Mausoleum of Hadrian", "Hadrianus Mozolesi"), "at": [41.9031, 12.4663], "from": 136, "to": 200, "lift_m": 60},
  {"text": T("Baths of Caracalla", "Caracalla Hamamları"), "at": [41.87944, 12.49306], "from": 214, "to": 270, "lift_m": 60},
  {"text": T("TRASTEVERE", "TRASTEVERE"), "at": [41.8885, 12.4690], "kind": "region", "from": 272, "to": 311},
  {"text": T("St Peter's", "St. Peter"), "at": [41.90222, 12.45333], "from": 330, "to": 400, "lift_m": 60},
  {"text": T("Lateran", "Lateran"), "at": [41.8858, 12.5056], "from": 325, "to": 400, "lift_m": 50},
  {"text": T("Pantheon", "Pantheon"), "at": [41.8986, 12.4768], "from": 609, "to": 845, "lift_m": 60},
  {"text": T("Old St Peter's", "Eski St. Peter"), "at": [41.90222, 12.45333], "from": 846, "to": 1080, "lift_m": 60},
  {"text": T("BORGO", "BORGO"), "at": [41.9020, 12.4610], "kind": "region", "from": 860, "to": 1080},
  {"text": T("Colosseum", "Kolezyum"), "at": [41.8903, 12.4922], "from": 1348, "to": 1419, "lift_m": 70},
  {"text": T("Ponte Sisto", "Ponte Sisto"), "at": [41.89233, 12.47075], "from": 1476, "to": 1505, "lift_m": 20},
  {"text": T("St Peter's", "St. Peter"), "at": [41.90222, 12.45333], "from": 1507, "to": 1530, "lift_m": 100},
  {"text": T("Castel Sant'Angelo", "Sant'Angelo Kalesi"), "at": [41.9031, 12.4663], "from": 1527, "to": 1530, "lift_m": 60},
  {"text": T("St Peter's", "St. Peter"), "at": [41.90222, 12.45333], "from": 1590, "to": 1790, "lift_m": 170},
  {"text": T("Termini", "Termini"), "at": [41.90083, 12.50194], "from": 1863, "to": 1869, "lift_m": 30},
  {"text": T("Porta Pia", "Porta Pia"), "at": [41.9092, 12.5011], "kind": "place", "from": 1870, "to": 1871.1, "lift_m": 20},
  {"text": T("PRATI", "PRATI"), "at": [41.9100, 12.4620], "kind": "region", "from": 1890, "to": 1910},
  {"text": T("Vittoriano", "Vittoriano"), "at": [41.8947, 12.4831], "from": 1911, "to": 1936.8, "lift_m": 90},
  {"text": T("Via della Conciliazione", "Via della Conciliazione"), "at": [41.9024, 12.4625], "from": 1945, "to": 1950, "lift_m": 20},
  {"text": T("Stadio Olimpico", "Stadio Olimpico"), "at": [41.93389, 12.45472], "from": 1953, "to": 1961, "lift_m": 50},
  {"text": T("EUR", "EUR"), "at": [41.8336, 12.4708], "kind": "place", "from": 1952, "to": 1981, "lift_m": 40},
  {"text": T("Ring road (GRA)", "Çevre yolu (GRA)"), "at": [41.9933, 12.5450], "kind": "region", "from": 1970, "to": 1981},
  {"text": T("Fiumicino", "Fiumicino"), "at": [41.7720, 12.2400], "kind": "place", "from": 1982, "to": 2021},
  {"text": T("St Peter's", "St. Peter"), "at": [41.90222, 12.45333], "from": 2022, "lift_m": 170},
  {"text": T("Colosseum", "Kolezyum"), "at": [41.8903, 12.4922], "from": 2022, "lift_m": 70},
 ],
 "youtube": {
  "title": T("Rome: 3,000 Years in 15 Minutes (3D Timelapse)", "Roma: 15 Dakikada 3.000 Yıl (3D Timelapse)"),
  "description": T(
   "Around 1000 BC there was only a marshy valley between seven hills by the Tiber. Watch Rome grow from huts on the Palatine "
   "into the capital of an empire of a million people, shrink to a small town in the Middle Ages, rise again as the city of the popes "
   "and become the capital of modern Italy: the Forum, the Servian and Aurelian walls, the Colosseum, the Pantheon, the sacks of 410 and 1527, "
   "St Peter's, the breach of Porta Pia and today's city of 2.7 million, with the year and the population on screen.",
   "MÖ 1000 civarında Tiber kıyısındaki yedi tepenin arasında yalnızca bataklık bir vadi vardı. Roma'nın Palatin'deki kulübelerden "
   "bir milyon kişilik bir imparatorluğun başkentine büyüyüşünü, Orta Çağ'da küçük bir kasabaya dönüşmesini, papaların şehri olarak yeniden "
   "yükselişini ve modern İtalya'nın başkenti oluşunu izleyin: Forum, Servius ve Aurelianus surları, Kolezyum, Pantheon, 410 ve 1527 yağmaları, "
   "St. Peter, Porta Pia gediği ve bugünün 2,7 milyonluk şehri; yıl ve nüfus ekranda."),
  "tags": ["rome history", "history of rome", "ancient rome", "roman empire", "3d timelapse", "city evolution", "how rome grew",
           "rome timelapse", "colosseum", "aurelian walls", "medieval rome", "urban history", "italian history", "eternal city"],
  "hashtags": ["#Rome", "#History", "#Timelapse"],
  "playlist": T("Cities of Europe", "Avrupa Şehirleri"),
  "playlist_desc": T("European cities rebuilt in 3D, from the first stone to the skyline.", "Avrupa şehirleri 3D olarak, ilk taştan siluete."),
  "thumb": {"line1": T("Rome", "Roma"), "line2": T("3,000 YEARS", "3.000 YIL"), "line3": T("From Palatine huts to the Eternal City", "Palatin kulübelerinden Ebedi Şehre"),
            "extra": "&mood=golden&pitch=30&az=64&cam=41.8960,12.4800,6.5"},
 },
 "sources": [
  {"title": "Founding of Rome — Wikipedia", "url": "https://en.wikipedia.org/wiki/Founding_of_Rome"},
  {"title": "Roman Forum — Wikipedia", "url": "https://en.wikipedia.org/wiki/Roman_Forum"},
  {"title": "Servian Wall — Wikipedia", "url": "https://en.wikipedia.org/wiki/Servian_Wall"},
  {"title": "Aurelian Walls — Wikipedia", "url": "https://en.wikipedia.org/wiki/Aurelian_Walls"},
  {"title": "Temple of Jupiter Optimus Maximus — Wikipedia", "url": "https://en.wikipedia.org/wiki/Temple_of_Jupiter_Optimus_Maximus"},
  {"title": "Sack of Rome (390 BC) — Wikipedia", "url": "https://en.wikipedia.org/wiki/Sack_of_Rome_(390_BC)"},
  {"title": "Aqua Appia — Wikipedia", "url": "https://en.wikipedia.org/wiki/Aqua_Appia"},
  {"title": "A Brief History of Via Appia Antica — Culture Trip", "url": "https://www.theculturetrip.com/europe/italy/articles/a-brief-history-of-via-appia-antica-romes-oldest-road"},
  {"title": "Via Flaminia — Wikipedia", "url": "https://en.wikipedia.org/wiki/Via_Flaminia"},
  {"title": "Circus Maximus — World History Encyclopedia", "url": "https://worldhistory.org/Circus_Maximus/"},
  {"title": "Pons Aemilius — Wikipedia", "url": "https://en.wikipedia.org/wiki/Pons_Aemilius"},
  {"title": "Pons Fabricius — Wikipedia", "url": "https://en.wikipedia.org/wiki/Pons_Fabricius"},
  {"title": "Ponte Milvio — Wikipedia", "url": "https://en.wikipedia.org/wiki/Ponte_Milvio"},
  {"title": "The Bridges of Rome — Rome Guide", "url": "https://rolfgross.dreamhosters.com/Rome-Guide/Bridges/Bridges.html"},
  {"title": "Theatre of Pompey — Wikipedia", "url": "https://en.wikipedia.org/wiki/Theatre_of_Pompey"},
  {"title": "Mausoleum of Augustus — Wikipedia", "url": "https://en.wikipedia.org/wiki/Mausoleum_of_Augustus"},
  {"title": "The Population of Rome (Oates, Classical Philology 1934)", "url": "https://penelope.uchicago.edu/Thayer/E/Journals/CP/29/2/Population_of_Rome*.html"},
  {"title": "Great Fire of Rome — Wikipedia", "url": "https://en.wikipedia.org/wiki/Great_Fire_of_Rome"},
  {"title": "Colosseum — Wikipedia", "url": "https://en.wikipedia.org/wiki/Colosseum"},
  {"title": "Trajan's Forum — Wikipedia", "url": "https://en.wikipedia.org/wiki/Trajan%27s_Forum"},
  {"title": "Pantheon, Rome — Wikipedia", "url": "https://ipfs.ssi.eecc.de/ipns/en.wikipedia-on-ipfs.org/wiki/Pantheon%2C_Rome"},
  {"title": "Castel Sant'Angelo — Wikipedia", "url": "https://en.wikipedia.org/wiki/Castel_Sant%27Angelo"},
  {"title": "Baths of Caracalla — Wikipedia", "url": "https://en.wikipedia.org/wiki/Baths_of_Caracalla"},
  {"title": "Bishops of Rome under Constantine the Great — Wikipedia", "url": "https://en.wikipedia.org/wiki/Bishops_of_Rome_under_Constantine_the_Great"},
  {"title": "Archbasilica of Saint John Lateran — Wikipedia", "url": "https://ipfs.ssi.eecc.de/ipns/en.wikipedia-on-ipfs.org/wiki/Archbasilica_of_Saint_John_Lateran"},
  {"title": "Sack of Rome (455) — Wikipedia", "url": "https://en.wikipedia.org/wiki/Sack_of_Rome_(455)"},
  {"title": "Arab raid against Rome — Wikipedia", "url": "https://cavac.at/cavacopedia/Arab%20raid%20against%20Rome"},
  {"title": "Pope Leo IV — Wikipedia", "url": "https://en.wikipedia.org/wiki/Pope_Leo_IV"},
  {"title": "Rome: City of the popes — Britannica", "url": "https://www.britannica.com/place/Rome/City-of-the-popes"},
  {"title": "Rome: Evolution of the modern city — Britannica", "url": "https://www.britannica.com/place/Rome/Evolution-of-the-modern-city"},
  {"title": "Rome: Capital of a united Italy — Britannica", "url": "https://www.britannica.com/place/Rome/Capital-of-a-united-Italy"},
  {"title": "Development of the Disabitato — Carleton CGMR", "url": "https://cgmr.carleton.edu/exhibits/show/uninhabited_rome/disabitato_development"},
  {"title": "Renaissance city planning in Rome — University of Washington", "url": "https://courses.washington.edu/rome250/week8notes%20ren%20city%20planning.htm"},
  {"title": "Ponte Sisto — Wikipedia", "url": "https://en.wikipedia.org/wiki/Ponte_Sisto"},
  {"title": "St. Peter's Basilica — Wikipedia", "url": "https://en.wikipedia.org/wiki/St._Peter%27s_Basilica"},
  {"title": "Sack of Rome (1527) — Wikipedia", "url": "https://en.wikipedia.org/wiki/Sack_of_Rome_(1527)"},
  {"title": "Roma Termini railway station — Wikipedia", "url": "https://en.wikipedia.org/wiki/Roma_Termini_railway_station"},
  {"title": "Capture of Rome — Wikipedia", "url": "https://en.wikipedia.org/wiki/Capture_of_Rome"},
  {"title": "Lungotevere — Wikipedia", "url": "https://en.wikipedia.org/wiki/Lungotevere"},
  {"title": "Victor Emmanuel II Monument — Wikipedia", "url": "https://en.wikipedia.org/wiki/Victor_Emmanuel_II_Monument"},
  {"title": "Via della Conciliazione — Wikipedia", "url": "https://en.wikipedia.org/wiki/Via_della_Conciliazione"},
  {"title": "EUR, Rome — Wikipedia", "url": "https://en.wikipedia.org/wiki/EUR,_Rome"},
  {"title": "Stadio Olimpico — Wikipedia", "url": "https://en.wikipedia.org/wiki/Stadio_Olimpico"},
  {"title": "Grande Raccordo Anulare (A90) — Wikipedia", "url": "https://en.wikipedia.org/wiki/Autostrada_A90"},
  {"title": "Roma: censimenti della popolazione — Tuttitalia (ISTAT)", "url": "https://www.tuttitalia.it/lazio/33-roma/statistiche/censimenti-popolazione/"},
 ],
}
total = sum(s_["seconds"] for s_ in S)
mins = round(total / 60)
city["intro"] = T(f"3,000 Years in {mins} Minutes", f"{mins} Dakikada 3.000 Yıl")
city["youtube"]["title"] = T(f"Rome: 3,000 Years in {mins} Minutes (3D Timelapse)", f"Roma: {mins} Dakikada 3.000 Yıl (3D Timelapse)")
json.dump(city, open(os.path.join(HERE, "city.json"), "w"), ensure_ascii=False, indent=1)
print("segments", len(S), "duration", total, "s =", f"{total // 60}:{total % 60:02d}")
