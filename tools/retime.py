"""Shorten (or lengthen) an episode to a target length by scaling every segment's seconds.

  python3 tools/retime.py <slug> <target_seconds> [--min-title 9] [--min-plain 3] [--dry]

Titled segments never go below --min-title seconds (the card must stay readable), untitled ones below --min-plain.
Fire durations are scaled too. "N Minutes" / "N Dakikada" in the intro and YouTube title are updated to the new
length (cold open included). Years, places and text are not touched.
Channel test, 12 Nov 2026: the competitors that get millions of views run 3–10 min; our episodes ran 13–15.
"""
import argparse, json, math, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('slug'); ap.add_argument('target', type=float)
    ap.add_argument('--min-title', type=float, default=9); ap.add_argument('--min-plain', type=float, default=3)
    ap.add_argument('--dry', action='store_true')
    a = ap.parse_args()
    path = os.path.join(ROOT, 'cities', a.slug, 'city.json')
    c = json.load(open(path, encoding='utf-8'))
    segs = c['segments']
    co = c.get('cold_open'); cos = float(co.get('seconds', 7)) if co else 0.0
    old = sum(s['seconds'] for s in segs)
    goal = a.target - cos
    floor = lambda s: a.min_title if s.get('title') else a.min_plain
    # find the scale k so that sum(max(floor, k * seconds)) == goal (bisection; floors make it non-linear)
    lo, hi = 0.01, 5.0
    for _ in range(60):
        k = (lo + hi) / 2
        tot = sum(max(floor(s), k * s['seconds']) for s in segs)
        lo, hi = (k, hi) if tot < goal else (lo, k)
    for s in segs:
        s['seconds'] = round(max(floor(s), k * s['seconds']) * 2) / 2   # half seconds
    for f in c.get('fires', []):
        if 'duration_s' in f:
            f['duration_s'] = max(2.5, round(f['duration_s'] * k, 1))
    new = sum(s['seconds'] for s in segs) + cos
    mins = max(1, round(new / 60))
    def fix(o):
        if isinstance(o, dict):
            if 'en' in o: o['en'] = re.sub(r'in \d+ Minutes', f'in {mins} Minutes', o['en'])
            if 'tr' in o: o['tr'] = re.sub(r'\d+ Dakikada', f'{mins} Dakikada', o['tr'])
    fix(c.get('intro')); fix(c.get('youtube', {}).get('title'))
    print(f'{a.slug}: {old + cos:.0f}s → {new:.0f}s ({new / 60:.1f} min), scale {k:.3f}, '
          f'titled cards {min(s["seconds"] for s in segs if s.get("title"))}–{max(s["seconds"] for s in segs if s.get("title"))}s')
    if not a.dry:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(c, f, indent=1, ensure_ascii=False)


if __name__ == '__main__':
    main()
