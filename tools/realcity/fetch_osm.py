"""Fetch real OSM data (buildings, roads, green, water, coastline) for a real-buildings Blender timelapse.

  python3 tools/realcity/fetch_osm.py <config.json> <out.json>

config: {"center": [lat, lon], "build_half_km": 2.5, "ground_half_km": 3.5}
"""
import json, math, sys, time
import requests

UA = {'User-Agent': 'dust-to-downtown/1.0 (real-buildings pilot)'}
SERVERS = ['https://overpass-api.de/api/interpreter', 'https://overpass.kumi.systems/api/interpreter',
           'https://overpass.private.coffee/api/interpreter']


def bbox(lat, lon, half_km):
    dlat = half_km / 111.32
    dlon = half_km / (111.32 * math.cos(math.radians(lat)))
    return lat - dlat, lon - dlon, lat + dlat, lon + dlon


def run(q):
    last = None
    for attempt in range(3):
        for url in SERVERS:
            try:
                r = requests.post(url, data={'data': q}, headers=UA, timeout=400)
                if r.status_code == 200:
                    els = r.json().get('elements', [])
                    print('  ', url.split('/')[2], len(els), 'elements', flush=True)
                    return els
                last = f'{url} {r.status_code}'
            except Exception as ex:  # noqa: BLE001
                last = f'{url} {ex}'
            print('   retry:', last, flush=True)
            time.sleep(10)
    raise SystemExit('overpass failed: ' + str(last))


def main():
    cfg = json.load(open(sys.argv[1]))
    lat, lon = cfg['center']
    b = '%.6f,%.6f,%.6f,%.6f' % bbox(lat, lon, cfg['build_half_km'])
    g = '%.6f,%.6f,%.6f,%.6f' % bbox(lat, lon, cfg['ground_half_km'])
    c = '%.6f,%.6f,%.6f,%.6f' % bbox(lat, lon, cfg['ground_half_km'] + 3)
    H = '[out:json][timeout:360];'
    out = {}
    print('buildings', flush=True)
    out['buildings'] = run(H + f'(way["building"]({b});relation["building"]["type"="multipolygon"]({b}););out tags geom;')
    print('roads', flush=True)
    out['roads'] = run(H + f'way["highway"~"^(motorway|trunk|primary|secondary|tertiary|residential|unclassified|living_street|pedestrian|service)$"]({g});out tags geom;')
    print('green', flush=True)
    out['green'] = run(H + f'(way["leisure"~"^(park|garden|pitch|golf_course)$"]({g});way["landuse"~"^(grass|forest|park|recreation_ground|meadow|orchard|village_green|cemetery)$"]({g});way["natural"~"^(wood|scrub|grassland|beach|sand)$"]({g});relation["landuse"~"^(forest|grass)$"]({g});relation["leisure"="park"]({g}););out tags geom;')
    print('water', flush=True)
    out['water'] = run(H + f'(way["natural"="water"]({g});relation["natural"="water"]({g});way["waterway"~"^(river|stream|canal)$"]({g}););out tags geom;')
    print('coastline', flush=True)
    out['coastline'] = run(H + f'way["natural"="coastline"]({c});out geom;')
    out['config'] = cfg
    json.dump(out, open(sys.argv[2], 'w'))
    print('saved', sys.argv[2])


if __name__ == '__main__':
    main()
