"""Ask Overpass what water data exists around a point (used once per new city to choose the water method)."""
import json, sys, time, requests
UA = {'User-Agent': 'dust-to-downtown/1.0'}
S, W, N, E = map(float, sys.argv[1:5])
Q = {
 'coastline_ways': f'[out:json][timeout:120];way["natural"="coastline"]({S},{W},{N},{E});out ids;',
 'river_areas': f'[out:json][timeout:120];(way["natural"="water"]["water"~"river|tidal|canal"]({S},{W},{N},{E});relation["natural"="water"]["water"~"river|tidal|canal"]({S},{W},{N},{E});way["waterway"="riverbank"]({S},{W},{N},{E});relation["waterway"="riverbank"]({S},{W},{N},{E}););out tags;',
 'all_water_count': f'[out:json][timeout:120];(way["natural"="water"]({S},{W},{N},{E});relation["natural"="water"]({S},{W},{N},{E}););out count;',
}
for name, q in Q.items():
    for url in ['https://overpass-api.de/api/interpreter', 'https://overpass.kumi.systems/api/interpreter', 'https://overpass.private.coffee/api/interpreter']:
        try:
            r = requests.post(url, data={'data': q}, headers=UA, timeout=200)
            if r.status_code == 200:
                els = r.json().get('elements', [])
                print(name, url.split('/')[2], len(els), json.dumps([{k: e.get(k) for k in ('type', 'id', 'tags')} for e in els[:12]], ensure_ascii=False)[:1500])
                break
            print(name, url, r.status_code)
        except Exception as ex:
            print(name, url, 'ERR', ex)
        time.sleep(5)
