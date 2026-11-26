"""Builds cities/constantinople/city.json — TEST episode for the "v3" look (owner, 26 Nov 2026: "bi tane deneme videosu
yapalım"). Constantinople from Byzantion (667 BC) to the fall of the city (29 May 1453), ~8 min, low oblique close-ups.

Everything on screen comes from cities/istanbul/research.md (same sources) plus cities/constantinople/research.md
(the 1453 naval details, Great Palace, Holy Apostles, Blachernae). Walls, districts, landmarks and the map are taken
from cities/istanbul/city.json so both episodes stay consistent; geo.json is a copy of Istanbul's (same bbox/edits).
Run: python3 cities/constantinople/_build.py
"""
import base64, copy, json, math, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
IST = json.load(open(os.path.join(HERE, '..', 'istanbul', 'city.json')))
GEO = json.load(open(os.path.join(HERE, 'geo.json')))
END = 1453.5

# ---- shoreline sampler (core grid, 30 m) so ships sit in water and chain ends on the shore
_c = GEO['core']; LAT0, LON0 = GEO['origin']; KX = 111.32 * math.cos(math.radians(LAT0)); KZ = 110.574
_sd = np.frombuffer(base64.b64decode(_c['sd_b64']), dtype='<i2').reshape(_c['nz'], _c['nx'])
def sd(lat, lon):
    x, z = (lon - LON0) * KX, -(lat - LAT0) * KZ
    i, j = int(round((x - _c['x0']) / _c['cell_km'])), int(round((z - _c['z0']) / _c['cell_km']))
    return int(_sd[j, i])

def by_name(lst, name):
    return copy.deepcopy(next(x for x in lst if x['name'] == name or (isinstance(x['name'], dict) and x['name']['en'] == name)))

def ist_seg(i, seconds, camera, **kw):
    s = copy.deepcopy(IST['segments'][i]); s['seconds'] = seconds; s['camera'] = camera
    s.pop('chapter', None); s.update(kw); return s

def cam(lat, lon, d, pitch=34, az=0, at=None, drift=None):
    c = {'center': [lat, lon], 'dist_km': d, 'pitch_deg': pitch, 'azimuth_deg': az}
    if drift is not None: c['drift_deg'] = drift
    if at is not None: c['at'] = at
    return c

ch = lambda en, tr: {'chapter': {'en': en, 'tr': tr}}

# ------------------------------------------------------------------ timeline (~8 min)
S = [
    ist_seg(0, 14, cam(41.0118, 28.9835, 2.2, 30, -25), **ch('Greek Byzantion', 'Yunan Byzantion')),
    ist_seg(1, 9, cam(41.006, 29.002, 4.2, 36, -10)),
    ist_seg(2, 8, cam(41.011, 28.983, 2.6, 32, 5)),
    ist_seg(3, 9.5, cam(41.0115, 28.975, 2.6, 30, 20)),
    ist_seg(4, 6, cam(41.0105, 28.98, 2.4, 32, 30)),
    ist_seg(5, 9.5, cam(41.0105, 28.981, 2.0, 30, 15), **ch('Roman Byzantium', 'Roma Byzantion\'u')),
    ist_seg(6, 11, cam(41.0068, 28.9765, 1.5, 28, -20)),
    ist_seg(7, 11, cam(41.0115, 28.962, 4.6, 34, -35), **ch('Constantine\'s New Rome', 'Konstantin\'in Yeni Roma\'sı')),
    ist_seg(8, 10.5, cam(41.0085, 28.9715, 1.6, 28, -10)),
    ist_seg(9, 9.5, cam(41.0085, 28.9795, 1.3, 27, 15)),
    ist_seg(10, 10.5, cam(41.0158, 28.9555, 1.7, 26, 40)),
    ist_seg(11, 13, cam(41.012, 28.926, 2.8, 26, -75), **ch('The Theodosian Walls', 'Theodosius Surları')),
    ist_seg(12, 9, cam(41.0, 28.93, 2.2, 28, -60)),
    ist_seg(13, 10.5, cam(41.0068, 28.9775, 1.4, 27, -25), **ch('Justinian', 'Jüstinyen')),
    ist_seg(14, 15, cam(41.0083, 28.98, 0.85, 24, 25, drift=40)),
    ist_seg(15, 9, cam(41.012, 28.958, 3.6, 32, 40)),
    ist_seg(16, 9.5, cam(41.016, 28.925, 3.0, 28, -70), **ch('Centuries of Sieges', 'Kuşatma Yüzyılları')),
    ist_seg(17, 10, cam(41.0, 28.945, 3.4, 30, -20)),
    ist_seg(18, 10, cam(41.003, 28.955, 3.6, 30, -10)),
    ist_seg(19, 6, cam(41.015, 28.955, 4.2, 34, 10)),
    ist_seg(20, 13, cam(41.012, 28.962, 3.2, 30, 35, drift=30), **ch('Queen of Cities', 'Şehirlerin Kraliçesi')),
    ist_seg(21, 11.5, cam(41.022, 28.958, 2.6, 30, 160), **ch('The Fourth Crusade', 'Dördüncü Haçlı Seferi')),
    ist_seg(22, 8, cam(41.017, 28.955, 3.6, 32, 120)),
    ist_seg(23, 9, cam(41.0235, 28.9745, 1.8, 30, 150)),
    ist_seg(24, 8.5, cam(41.0256, 28.9742, 1.1, 26, 170)),
    ist_seg(25, 9.5, cam(41.0815, 29.0655, 1.6, 28, 120), **ch('The Conquest', 'Fetih')),
    ist_seg(26, 11, cam(41.081, 29.058, 1.7, 26, -20)),
    ist_seg(27, 13, cam(41.019, 28.921, 2.0, 24, -80)),
]
# 20 April 1453: the naval fight; 22 April: ships over the hill; 29 May: the assault and the fall
S[-1]['to'] = 1453.28
S += [
    {'from': 1453.281, 'to': 1453.302, 'seconds': 11, 'era': S[-1]['era'], 'city_name': S[-1]['city_name'],
     'title': {'en': 'The Chain Holds', 'tr': 'Zincir Dayanıyor'},
     'sub': {'en': '20 April 1453: four Christian ships fight past the Ottoman fleet into the Golden Horn',
             'tr': '20 Nisan 1453: dört Hristiyan gemisi Osmanlı donanmasını yarıp Haliç\'e girer'},
     'population': 50000, 'camera': cam(41.0135, 28.989, 1.7, 28, 160)},
    ist_seg(28, 14, cam(41.0395, 28.982, 1.8, 30, 170), **{'from': 1453.303, 'to': 1453.31}),
    {'from': 1453.311, 'to': 1453.405, 'seconds': 6, 'era': S[-1]['era'], 'city_name': S[-1]['city_name'],
     'population': 50000, 'camera': cam(41.02, 28.94, 3.0, 28, -60)},
    {'from': 1453.406, 'to': 1453.408, 'seconds': 12, 'era': S[-1]['era'], 'city_name': S[-1]['city_name'],
     'title': {'en': 'The Final Assault', 'tr': 'Son Saldırı'},
     'sub': {'en': '29 May 1453, after midnight: the last assault; the Ottomans break in near the St Romanus Gate',
             'tr': '29 Mayıs 1453, gece yarısından sonra: son saldırı; Osmanlılar Topkapı yakınında şehre girer'},
     'population': 50000, 'camera': cam(41.0195, 28.925, 2.3, 30, -100)},
    ist_seg(29, 14, cam(41.0083, 28.98, 1.15, 24, 40), **{'from': 1453.409, 'to': 1453.42}),
    {'from': 1453.421, 'to': END, 'seconds': 10, 'era': {'en': 'Ottoman', 'tr': 'Osmanlı'}, 'city_name': {'en': 'Istanbul', 'tr': 'İstanbul'},
     'title': {'en': 'Next: Ottoman Istanbul', 'tr': 'Sırada: Osmanlı İstanbul\'u'},
     'sub': {'en': '1,100 years after Constantine, a new empire begins to rebuild the city',
             'tr': 'Konstantin\'den 1.100 yıl sonra yeni bir imparatorluk şehri yeniden kurmaya başlar'},
     'population': 50000, 'camera': cam(41.014, 28.962, 5.5, 34, 60)},
]
# pacing: ~7.5 min in all (owner's competitor runs 8:35); the shots hold, so every segment gets a little longer
for s in S: s['seconds'] = round(s['seconds'] * 1.25, 1)
# the last Byzantine segments keep the Istanbul subtitles (6 Apr, 22 Apr, 29 May 1453); their population is 50,000
for s in S:
    s.pop('chapter', None) if s.get('chapter') == {} else None

# ------------------------------------------------------------------ map features (from Istanbul, up to 1453)
keep = lambda lst, key='from': [copy.deepcopy(x) for x in lst if (x.get(key, x.get('built', x.get('year', -1e9))) or -1e9) <= END]
districts = [by_name(IST['districts'], n) for n in ['Byzantion (≈)', 'Chalcedon (≈)', 'Byzantion rebuilt by Severus (≈)',
             "Constantine's city (≈)", 'Theodosian city (≈)', 'Late Byzantine decline (≈)', 'Genoese Galata (≈)']]
# denser: ~500,000 people by 540 and ~400,000 in the 12th century (research.md) — a packed city inside Constantine's wall
for d in districts:
    if d['name'] == "Constantine's city (≈)": d.update(density=0.9, grain_m=42)
    if d['name'] == 'Theodosian city (≈)': d.update(density=0.6, grain_m=50)
    if d['name'] == 'Byzantion rebuilt by Severus (≈)': d.update(density=0.85, grain_m=42)
    if d['name'] == 'Genoese Galata (≈)': d.update(density=0.9, grain_m=38)
    if d['name'] in ('Late Byzantine decline (≈)', 'Genoese Galata (≈)'): d['style'] = 'roman'
# the quarter burnt in the Nika riots (532) is rebuilt with Justinian's city (≈), and the 1204 fire zone is partly rebuilt (≈)
nika = next(f for f in IST['fires'] if f['year'] == 532.04)
districts.append({'name': 'Rebuilt after the Nika riots (≈)', 'style': 'roman', 'poly': nika['poly'], 'from': 533, 'to': 545,
                  'density': 0.8, 'grain_m': 44, 'grow_from': [41.0075, 28.978]})
# regrowth after the plague towards the 12th-century peak, then decline after 1204 (≈, research.md: 400,000 → 35,000)
cw = by_name(IST['districts'], "Constantine's city (≈)")
districts.append({'name': 'Middle Byzantine city (≈)', 'style': 'roman', 'poly': cw['poly'], 'from': 800, 'to': 1140,
                  'density': 0.85, 'grain_m': 44, 'grow_from': [41.011, 28.97], 'fade': [1204.3, 1262, 0.3]})
walls = [w for w in copy.deepcopy(IST['walls']) if w['built'] <= END]
for w in walls:
    if w['name'] == 'Theodosian land walls': w['height'] = 'high'
landmarks = [l for l in copy.deepcopy(IST['landmarks']) if l['built'] <= END]
for l in landmarks:
    if l['name']['en'] == 'Hagia Sophia': l.pop('additions', None); l.update(type='greatdome', scale=1.5, size_m=[82, 73, 30], colors={'wall': '#d9a47c', 'dome': '#9aa1a8'})
    if l['name']['en'] == 'Aqueduct of Valens': l.update(type='aqueduct', size_m=[921, 9, 29], colors={'wall': '#d6c3a0'})
    if l['name']['en'] == 'Great Church (first Hagia Sophia)': l['scale'] = 1.3
    if l['name']['en'] == 'Hippodrome': l['scale'] = 1.15
    if l['name']['en'] == 'Galata Tower': l['scale'] = 2.0
    if l['name']['en'] in ('Rumelihisarı', 'Anadoluhisarı'): l['type'] = 'castle'
landmarks += [
    {'type': 'palace2', 'name': {'en': 'Great Palace (≈)', 'tr': 'Büyük Saray (≈)'}, 'at': [41.0036, 28.9785], 'built': 330.2,
     'removed': 1454, 'rise_s': 6, 'size_m': [300, 190, 18], 'rot_deg': -58, 'colors': {'wall': '#efe4cc', 'roof': '#b6553a'}},
    {'type': 'cross5', 'name': {'en': 'Church of the Holy Apostles', 'tr': 'Havariyun Kilisesi'}, 'at': [41.01972, 28.94972],
     'built': 550.49, 'rise_s': 6, 'size_m': [70, 70, 20], 'scale': 1.2, 'colors': {'wall': '#d9a47c', 'dome': '#9aa1a8'}},
    {'type': 'palace2', 'name': {'en': 'Blachernae Palace (≈)', 'tr': 'Blakhernai Sarayı (≈)'}, 'at': [41.0352, 28.9405], 'built': 1090,
     'rise_s': 5, 'size_m': [170, 110, 20], 'rot_deg': 30, 'colors': {'wall': '#e6d8bc', 'roof': '#a9563a'}},
]
fires = [f for f in copy.deepcopy(IST['fires']) if f['year'] <= END]
camps = [c for c in copy.deepcopy(IST['camps']) if c['from'] <= END]
smoke = [s for s in copy.deepcopy(IST['smoke']) if s['from'] <= END]
roads = [r for r in copy.deepcopy(IST['roads']) if r['from'] <= END]
labels = [l for l in copy.deepcopy(IST['labels']) if (l.get('from') if l.get('from') is not None else -1e9) <= END]
for l in labels:
    if l.get('to') is None or l['to'] > END: l['to'] = None
labels += [
    {'text': {'en': 'Holy Apostles', 'tr': 'Havariyun'}, 'at': [41.01972, 28.94972], 'from': 551, 'to': 625, 'lift_m': 60},
    {'text': {'en': 'Great Palace', 'tr': 'Büyük Saray'}, 'at': [41.0036, 28.9785], 'from': 331, 'to': 359, 'lift_m': 30},
    {'text': {'en': 'Blachernae', 'tr': 'Blakhernai'}, 'at': [41.0352, 28.9405], 'from': 1143, 'to': 1203, 'lift_m': 30},
    {'text': {'en': 'The chain', 'tr': 'Zincir'}, 'at': [41.0198, 28.9788], 'from': 1453.282, 'to': 1453.302, 'lift_m': 10},
    {'text': {'en': 'St Romanus Gate', 'tr': 'Topkapı'}, 'at': [41.0205, 28.9215], 'from': 1453.406, 'to': 1453.408, 'lift_m': 30},
]

# ------------------------------------------------------------------ 1453 at sea and the guns (≈ positions, research.md)
CH_S, CH_N = [41.0166, 28.978], [41.0219, 28.978]     # Eugenius tower (≈ Sirkeci shore) → Galata shore (≈)
chains = [{'path': [CH_S, CH_N], 'from': 1453.255, 'to': 1453.42}]
fleets = [
    # Umayyad fleets in the Marmara, 674 and 717 (≈ positions; on screen only "fleet" in the subtitle)
    {'name': 'Umayyad fleet 674 (≈)', 'from': 674.2, 'to': 716, 'count': 26, 'rows': 3, 'kind': 'galley', 'sail': '#efe6d0', 'path': [[40.985, 28.95]]},
    {'name': 'Umayyad fleet 717 (≈)', 'from': 717.2, 'to': 739, 'count': 34, 'rows': 4, 'kind': 'galley', 'sail': '#efe6d0', 'path': [[40.99, 28.965]]},
    # Venetian fleet attacking the Golden Horn sea walls, April 1204 (≈)
    {'name': 'Crusader fleet 1204 (≈)', 'from': 1204.0, 'to': 1215, 'count': 30, 'rows': 2, 'kind': 'ship', 'sail': '#f2e9d6', 'spread_m': 80,
     'path': [[41.0345, 28.951], [41.031, 28.958]], 'move': [1204.05, 1204.3]},
    # 1453: Ottoman fleet anchored at the Double Columns (Diplokionion, today Beşiktaş), blocked by the chain
    {'name': 'Ottoman fleet at Diplokionion (≈)', 'from': 1453.26, 'to': 1453.31, 'count': 48, 'rows': 4, 'kind': 'galley', 'sail': '#b7322a',
     'path': [[41.038, 29.008]]},
    # 20 April: four Christian ships push up the Bosphorus mouth to the chain
    {'name': 'Four Christian ships, 20 April (≈)', 'from': 1453.281, 'to': 1453.42, 'count': 4, 'rows': 2, 'kind': 'ship', 'sail': '#f3eee2',
     'size_m': 55, 'spread_m': 60, 'path': [[41.004, 28.996], [41.012, 28.994], [41.0185, 28.984], [41.0195, 28.974]], 'move': [1453.283, 1453.301]},
    # 22 April: ships hauled from the Bosphorus over the hill into the Golden Horn (route ≈, Dolmabahçe valley → Kasımpaşa)
    {'name': 'Ships over the hill, 22 April (≈)', 'from': 1453.303, 'to': 1453.42, 'count': 30, 'rows': 2, 'kind': 'galley', 'sail': '#b7322a',
     'spread_m': 55, 'land': True, 'path': [[41.0385, 29.0], [41.042, 28.99], [41.041, 28.979], [41.036, 28.968], [41.031, 28.9625]],
     'move': [1453.3035, 1453.3095]},
]
# guns facing the land walls along the Lycus valley (Mesoteichion) and towards Blachernae (≈)
cannons = [
    {'at': [41.0205, 28.914], 'from': 1453.262, 'to': 1453.408, 'count': 7, 'spread_m': 600, 'bearing_deg': 95},
    {'at': [41.0295, 28.929], 'from': 1453.265, 'to': 1453.408, 'count': 4, 'spread_m': 350, 'bearing_deg': 120},
    {'at': [41.004, 28.912], 'from': 1453.27, 'to': 1453.408, 'count': 3, 'spread_m': 300, 'bearing_deg': 80},
]
# assault: smoke over the walls on 29 May, and the city's last night
smoke += [{'at': [41.0205, 28.9235], 'from': 1453.406, 'to': 1453.42, 'scale': 1.0}]

for f in fleets:
    for p in f['path'][:1] + f['path'][-1:]:
        if not f.get('land'):
            assert sd(*p) < -60, (f['name'], p, sd(*p))
        else: print(f['name'], [sd(*q) for q in f['path']])
for p in (CH_S, CH_N):
    print('chain end', p, 'sd', sd(*p))

MIN = int(sum(s['seconds'] for s in S) / 60 + 0.5)
THUMB_T = round(sum(s['seconds'] for s in S[:14]) + 3.5 + S[14]['seconds'] * 0.6, 1)   # Hagia Sophia in the packed city
city = {
    'slug': 'constantinople', 'seed': 1453, 'long_ok': True, 'test': 'look v3 (owner test, 26 Nov 2026)',
    'name': {'en': 'Constantinople', 'tr': 'Konstantinopolis'},
    'intro': {'en': f'2,100 Years in {MIN} Minutes', 'tr': f'{MIN} Dakikada 2.100 Yıl'}, 'intro_seconds': 3.5,
    'target_s': [420, 560],
    'geo': copy.deepcopy(IST['geo']), 'timed_water': copy.deepcopy(IST['timed_water']),
    'view': {'azimuth_deg': 0, 'pitch_deg': 32, 'fov': 32},
    'render': {'vertical_exaggeration': 2.2, 'look': 'v3', 'tilt_shift': 1.0},
    'segments': S, 'districts': districts, 'walls': walls, 'landmarks': landmarks, 'roads': roads, 'fires': fires,
    'camps': camps, 'smoke': smoke, 'open_spaces': [],
    'labels': labels, 'fleets': fleets, 'chains': chains, 'cannons': cannons,
    'music': {'style': 'eras', 'flavor': 'ottoman'},
    'youtube': {
        'title': {'en': f'Constantinople: 2,100 Years in {MIN} Minutes (3D Timelapse, No AI)', 'tr': f'Konstantinopolis: {MIN} Dakikada 2.100 Yıl (3D Timelapse, Yapay Zekâ Yok)'},
        'description': {'en': 'From the Greek colony of Byzantion to the morning of 29 May 1453. Watch Constantine build his New Rome, the Theodosian Walls rise, Justinian raise Hagia Sophia, the city survive siege after siege, the crusaders sack it in 1204, and Mehmed II take it in 1453: the chain across the Golden Horn, the ships dragged over the hill, the final assault. The year and the population are on screen.',
                        'tr': 'Yunan kolonisi Byzantion\'dan 29 Mayıs 1453 sabahına. Konstantin\'in Yeni Roma\'yı kurmasını, Theodosius Surları\'nın yükselmesini, Jüstinyen\'in Ayasofya\'yı inşa etmesini, şehrin kuşatma üstüne kuşatma atlatmasını, Haçlıların 1204\'te onu yağmalamasını ve II. Mehmed\'in 1453\'te fethini izleyin: Haliç\'i kapatan zincir, karadan yürütülen gemiler, son saldırı. Yıl ve nüfus ekranda.'},
        'tags': ['constantinople', 'fall of constantinople', 'byzantium', 'byzantine empire', 'history of constantinople', '1453',
                 'theodosian walls', 'hagia sophia', '3d timelapse', 'city evolution', 'istanbul history'],
        'hashtags': ['#Constantinople', '#History', '#Timelapse'],
        'playlist': {'en': 'Cities of Europe', 'tr': 'Avrupa Şehirleri'},
        'thumb': {'style': 'v2', 't': THUMB_T, 'line1': {'en': 'Constantinople', 'tr': 'Konstantinopolis'}, 'line2': {'en': '667 BC → 1453', 'tr': 'MÖ 667 → 1453'}},
    },
    'sources': copy.deepcopy(IST['sources']) + [
        {'title': 'Fall of Constantinople (Wikipedia)', 'url': 'https://en.wikipedia.org/wiki/Fall_of_Constantinople'},
        {'title': 'Van Millingen, Byzantine Constantinople: the route of the Turkish ships', 'url': 'https://textbase.scriptorium.ro/van_millingen/byzantine_constantinople/the_walls_along/the_route'},
        {'title': 'Great Palace of Constantinople (Wikipedia)', 'url': 'https://en.wikipedia.org/wiki/Great_Palace_of_Constantinople'},
        {'title': 'Church of the Holy Apostles (Wikipedia)', 'url': 'https://en.wikipedia.org/wiki/Church_of_the_Holy_Apostles'},
        {'title': 'Blachernae Palace (Wikipedia)', 'url': 'https://en.wikipedia.org/wiki/Blachernae_Palace'},
    ],
}
json.dump(city, open(os.path.join(HERE, 'city.json'), 'w'), ensure_ascii=False, indent=1)
print('segments', len(S), 'seconds', sum(s['seconds'] for s in S))
