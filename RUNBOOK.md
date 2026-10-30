# Episode runbook (for Claude sessions)

Channel: **Dust to Downtown** (@DustToDowntown) — silent 3D timelapses of how great cities grew, ~15 min each,
English on screen (Turkish version rendered too, kept for a future Turkish channel). Owner speaks Turkish;
all messages to the owner are in Turkish. Two long episodes per week (published Tue + Fri 15:00 UTC).
Episodes are made ahead of time (one per day, up to 8 in stock) and wait on YouTube as private + scheduled.

The owner cares most about **accuracy and quality**. A slower, correct episode beats a fast, wrong one.

## A. Make the next episode (scheduled run, or owner says "yeni bölüm", "sıradaki şehri yap")

1. `git pull`. **Stock check:** count long videos in `uploads.json` whose `publish_at` is in the future, plus cities
   whose `render.json` exists but are not yet in `uploads.json`. If that is 8 or more (4 weeks of stock), make nothing:
   just report to the owner "stok dolu (N bölüm hazır, son yayın <tarih>)" and stop.
   Otherwise pick the first unchecked city in `cities/queue.md` (or the city the owner named).
   Skip a city whose folder already has `status.json` with `rendered`.
2. **Research (most of the time goes here).** Use WebSearch/WebFetch; open the pages you cite. At least 10 sources:
   Wikipedia for orientation (city article, history article, list of walls/bridges/landmarks), plus Britannica,
   museum / archaeology / city-government / university pages. Collect into `cities/<slug>/research.md`:
   - timeline of 35–50 events with dates (founding, walls, fires, plagues, sieges, key buildings, bridges, railways,
     big expansions, wars, modern landmarks), each with its source;
   - population estimates per period with sources (ranges where scholars disagree);
   - coordinates [lat, lon] for every landmark (Wikipedia/OSM coordinates), wall gates/corners, bridge ends;
   - the extent of the built-up area per era (from historical maps descriptions) → district polygons.
3. Write `cities/<slug>/city.json` following `CITY_SPEC.md` (target 13–16 min). Write the subtitles yourself in
   plain English and natural Turkish (not word-for-word). Fill `youtube` and `sources`.
4. `python3 tools/validate.py <slug>` until it prints OK. Fix every WARN you can.
5. Commit + push (`episode: <slug> draft`). The **Preview** action builds the real map and commits 10 stills per
   language to `cities/<slug>/preview/` (~10–20 min). Poll: every 60 s `git pull -q`, until
   `cities/<slug>/preview/log.txt` is newer than your push (max 30 min; if the action failed, read its log with
   `gh api repos/velinazim/dust-to-downtown/actions/runs?per_page=3` and fix).
6. **Check the map first**: `cities/<slug>/preview/map_core.png` and `map_full.png` show the real land/water with every
   wall, bridge, district, landmark and dock drawn on top. For a sharper look at one area run
   `python3 tools/debug_map.py <slug> /tmp/x` locally after `git pull` (geo.json is committed), or sample the shoreline
   in Python as cities/london shows. Bridge ends must be on land (sd > 20 m), walls must end at the shore.
   **Then look at every preview still** (Read the jpgs). Check: buildings/walls in the water? walls ending on land
   short of the shore? districts spilling outside the real coastline/river? camera too close/far, city off-frame?
   labels overlapping each other or the title? text cut off? Fix city.json and push again. Up to 3 rounds.
7. When the stills are right: write `cities/<slug>/render.json` = `{"upload": true}`, commit + push
   (`episode: <slug> render`). The **Render episode** action renders in ~20 parallel machines, joins, adds music
   and uploads the English video to YouTube as private, scheduled for the next free slot. ~45–90 min. Do not wait.
8. Tick the city in `cities/queue.md`, commit + push. Tell the owner (Turkish, short): city, length, what the
   episode covers, that rendering started, and when it is scheduled to go live.

## B. Report ("rapor", "durum")

`git pull`; read `uploads.json` (link, publish time), `cities/*/status.json` (render runs and upload logs), and the
last action runs (`gh api repos/velinazim/dust-to-downtown/actions/runs?per_page=10`). Report in Turkish: what is
scheduled/published, anything failed and why, what is next in the queue.

## C. Publish now / change time ("yayınla")

Write `requests/publish/<YYYYMMDD-HHMM>.json` = `{"video_ids": ["..."], "at": "<UTC ISO, optional>"}`; commit + push.
Result appears in `requests/done/` within ~5 minutes.

## Notes

- Preview/geo failures: the log is committed to `cities/<slug>/geo_log.txt` (GitHub's own log host is not reachable
  from Claude sessions). Overpass (OSM) can be busy: the script retries for a few minutes; if it still fails, re-run
  the Preview action later (`gh api -X POST repos/velinazim/dust-to-downtown/actions/workflows/preview.yml/dispatches -f ref=main -f 'inputs[slug]=<slug>'`).
- The channel is not phone-verified yet (`config/whoami.txt`: longUploadsStatus=eligible): keep episodes under 15:00
  until it says `allowed`; validate.py warns above 899 s.
- A city can be written with a small generator (cities/london/_build.py) — keep it next to city.json.

- Never put secrets in files or chat. YouTube credentials live only in GitHub Secrets.
- The upload refuses to run if the token belongs to another channel (config/channel.json).
- Rendering is CPU-only in the cloud; ~70k buildings is the practical ceiling — raise `grain_m` for modern sprawl.
- Engine/look changes go in `engine/index.html`; test locally with
  `python3 engine/render.py stills istanbul-test /tmp/st auto --w 1280 --h 720` (hand-made test map, no network needed).
