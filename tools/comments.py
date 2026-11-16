#!/usr/bin/env python3
"""Fetch the channel's YouTube comments (read only) so the morning report can find viewer questions and requests.

Run by the daily analytics GitHub Action:

    python3 tools/comments.py <repo_dir>

Writes:
  analytics/comments/all.json  every top-level comment seen so far, keyed by comment id
  analytics/comments/new.json  only the ones first seen in this run (the morning report triages these)

Stored per comment: video id + title, text, like count, reply count, published time, and whether the channel already
replied. Commenter names and channel ids are NOT stored. Nothing is posted: replies are drafted for the owner.
Quota: 1 unit per page of 100 comments.
"""
import datetime as dt, html, json, os, re, sys
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from yt_api import API, H, token  # noqa: E402




def clean(t):
    return re.sub(r'<[^>]+>', ' ', html.unescape(t or '')).strip()


def main():
    repo = sys.argv[1] if len(sys.argv) > 1 else '.'
    out = os.path.join(repo, 'analytics', 'comments')
    os.makedirs(out, exist_ok=True)
    all_path = os.path.join(out, 'all.json')
    seen = json.load(open(all_path)) if os.path.exists(all_path) else {}
    tok = token()
    me = requests.get(f'{API}/channels', headers=H(tok), params={'part': 'id', 'mine': 'true'}, timeout=30).json()
    OWN_CHANNEL = me['items'][0]['id']
    titles, new, page = {}, {}, None
    for _ in range(5):  # newest 500 threads is plenty for a young channel
        params = {'part': 'snippet,replies', 'allThreadsRelatedToChannelId': OWN_CHANNEL, 'maxResults': 100,
                  'order': 'time', 'textFormat': 'plainText'}
        if page:
            params['pageToken'] = page
        r = requests.get(f'{API}/commentThreads', headers=H(tok), params=params, timeout=30)
        if r.status_code == 403 and 'commentsDisabled' in r.text:
            break
        if r.status_code != 200:
            # Keep the reason in the repo (the morning report reads it); never crash the analytics run.
            json.dump({'fetched': dt.datetime.utcnow().isoformat(timespec='seconds') + 'Z', 'comments': {},
                       'error': f'commentThreads HTTP {r.status_code}: {r.text[:400]}'},
                      open(os.path.join(out, 'new.json'), 'w'), indent=1, ensure_ascii=False)
            print('comments error', r.status_code, r.text[:400])
            return
        data = r.json()
        for th in data.get('items', []):
            top = th['snippet']['topLevelComment']['snippet']
            cid = th['id']
            replies = (th.get('replies') or {}).get('comments', [])
            row = {'video': th['snippet'].get('videoId'), 'text': clean(top.get('textDisplay')),
                   'likes': top.get('likeCount', 0), 'replies': th['snippet'].get('totalReplyCount', 0),
                   'published': top.get('publishedAt'),
                   'answered': any(c['snippet'].get('authorChannelId', {}).get('value') == OWN_CHANNEL
                                   for c in replies)}
            if top.get('authorChannelId', {}).get('value') == OWN_CHANNEL:
                continue  # the channel's own comments
            if cid not in seen:
                new[cid] = row
            seen[cid] = {**seen.get(cid, {}), **row}
        page = data.get('nextPageToken')
        if not page or all(th['id'] in seen and th['id'] not in new for th in data.get('items', [])):
            break
    vids = sorted({c['video'] for c in seen.values() if c.get('video')})
    for i in range(0, len(vids), 50):
        v = requests.get(f'{API}/videos', headers=H(tok), params={'part': 'snippet', 'id': ','.join(vids[i:i + 50])},
                         timeout=30).json()
        for it in v.get('items', []):
            titles[it['id']] = it['snippet']['title']
    for c in list(seen.values()) + list(new.values()):
        if c.get('video') in titles:
            c['video_title'] = titles[c['video']]
    json.dump(seen, open(all_path, 'w'), indent=1, ensure_ascii=False)
    json.dump({'fetched': dt.datetime.utcnow().isoformat(timespec='seconds') + 'Z', 'comments': new},
              open(os.path.join(out, 'new.json'), 'w'), indent=1, ensure_ascii=False)
    print(f'comments: {len(new)} new, {len(seen)} total')


if __name__ == '__main__':
    main()
