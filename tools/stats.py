#!/usr/bin/env python3
"""Daily channel numbers for Dust to Downtown -> analytics/<YYYY-MM-DD>.json (read by the owner's dashboard).
Runs only in GitHub Actions with YT_CLIENT_ID / YT_CLIENT_SECRET / YT_REFRESH_TOKEN. Read-only: never changes a video.

  python3 tools/stats.py .
Output: {"date", "channel": {"title","subscribers","views","videos"}, "videos": [{"id","views"}]}
If the token lacks permission to read statistics the run fails with a clear message (needs scope youtube.readonly).
"""
import datetime as dt, json, os, sys
import requests
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import yt_api

repo = sys.argv[1] if len(sys.argv) > 1 else '.'
tok = yt_api.token()
cid = yt_api.check_channel(tok, repo)
r = requests.get(f'{yt_api.API}/channels', params={'part': 'statistics,snippet', 'id': cid}, headers=yt_api.H(tok), timeout=30)
if r.status_code != 200:
    sys.exit(f'channel statistics failed ({r.status_code}): {r.text[:300]} — if "insufficientPermissions", '
             f'create the refresh token again with scope https://www.googleapis.com/auth/youtube.readonly added')
it = r.json()['items'][0]
st = it['statistics']
ups = json.load(open(os.path.join(repo, 'uploads.json')))
ids = [u['video_id'] for u in ups if u.get('video_id') and not u.get('deleted')]
videos = []
for i in range(0, len(ids), 50):
    rv = requests.get(f'{yt_api.API}/videos', params={'part': 'statistics', 'id': ','.join(ids[i:i + 50])}, headers=yt_api.H(tok), timeout=30)
    if rv.status_code != 200:
        sys.exit(f'video statistics failed ({rv.status_code}): {rv.text[:300]}')
    videos += [{'id': v['id'], 'views': int(v['statistics'].get('viewCount', 0))} for v in rv.json().get('items', [])]
out = {'date': dt.date.today().isoformat(),
       'channel': {'title': it['snippet']['title'], 'subscribers': int(st.get('subscriberCount', 0)),
                   'views': int(st.get('viewCount', 0)), 'videos': int(st.get('videoCount', 0))},
       'videos': videos}
os.makedirs(os.path.join(repo, 'analytics'), exist_ok=True)
path = os.path.join(repo, 'analytics', out['date'] + '.json')
json.dump(out, open(path, 'w'), indent=1)
print(f"{out['date']}: {out['channel']['subscribers']} subscribers, {out['channel']['views']} views, {len(videos)} videos -> {path}")
