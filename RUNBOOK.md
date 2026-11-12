# Episode runbook (for Claude sessions)

Channel: **Dust to Downtown** (@DustToDowntown) — silent 3D timelapses of how great cities grew, 8–10 min each (new format since 12 Nov 2026, section G),
English on screen (Turkish version rendered too, kept for a future Turkish channel). Owner speaks Turkish;
all messages to the owner are in Turkish. Two long episodes per week (published Tue + Fri) + 2–3 vertical Shorts
per episode on the days between. The weekdays are fixed in `config/schedule.json`; the hour of day is chosen by
`tools/best_slot.py` from where the audience lives (weekly Action "Best publish time", reason in `config/best_slot.md`;
currently 23:30 UTC = 02:30 Istanbul). Videos already scheduled keep their time. Never edit the hour by hand unless the
owner asks for a fixed time; then set `"fixed": true` in the file and the script leaves it alone.
Episodes are made just ahead of time (at most 2 in stock, owner 12 Nov 2026: so a change reaches the channel within
a week instead of having to delete weeks of stock) and wait on YouTube as private + scheduled.

The owner cares most about **accuracy and quality**. A slower, correct episode beats a fast, wrong one.

## A. Make the next episode (scheduled run, or owner says "yeni bölüm", "sıradaki şehri yap")

0. **Final-video QA of the last finished episode (every run, before anything else).** After `git pull`, find cities whose
   `status.json` has `"qa_checked": false` (the Render action set it) and a `cities/<slug>/qa_sheet.jpg`: 16 evenly spaced
   frames of the FINISHED English video. Read the sheet and look at every tile: city/land/water right, walls and
   landmarks where they belong, labels readable and not overlapping or cut off, no black/blank/stuck frame, the era
   captions and dates sensible (the video is silent, so there is no speech to compare; `status.json` `qa` also lists any
   blank frames the script found). If something is really wrong, fix `city.json`, and re-run the **Render episode** action
   for that slug (it is private + scheduled, so there is time before it goes live); if you are unsure how to replace
   the uploaded video safely, tell the owner exactly what is wrong instead of guessing. When clean (or fixed),
   set `"qa_checked": true` in that status.json (commit + push). Add ONE line to the report in Turkish, e.g.
   "Video kontrolü: <şehir> — 16 kare incelendi, <bulunan/düzeltilen> " or "…sorun yok." Never say an episode is done
   before this check.
1. `git pull`. **Stock check:** count long videos in `uploads.json` whose `publish_at` is in the future, plus cities
   whose `render.json` exists but are not yet in `uploads.json`. If that is 2 or more (about one week of stock), make nothing:
   just report to the owner "stok dolu (N bölüm hazır, son yayın <tarih>)" and stop.
   Otherwise pick the first unchecked city in `cities/queue.md` (or the city the owner named).
   Skip a city whose folder already has `status.json` with `rendered`. If the city folder already has `city.json`,
   `research.md` and a preview but no `render.json`, an earlier run was cut off: **continue that work** (read
   research.md and the latest preview stills, fix what is left, go to step 6/7) instead of starting over.
2. **Research (most of the time goes here).** Use WebSearch/WebFetch; open the pages you cite. At least 10 sources:
   Wikipedia for orientation (city article, history article, list of walls/bridges/landmarks), plus Britannica,
   museum / archaeology / city-government / university pages. Collect into `cities/<slug>/research.md`:
   - timeline of 35–50 events with dates (founding, walls, fires, plagues, sieges, key buildings, bridges, railways,
     big expansions, wars, modern landmarks), each with its source;
   - population estimates per period with sources (ranges where scholars disagree);
   - coordinates [lat, lon] for every landmark (Wikipedia/OSM coordinates), wall gates/corners, bridge ends;
   - the extent of the built-up area per era (from historical maps descriptions) → district polygons.
3. Write `cities/<slug>/city.json` following `CITY_SPEC.md` (**new format since 12 Nov 2026**, see section G: 8–10 min,
   cold open, thumb v2, people notes, era music). Write the subtitles yourself in
   plain English and natural Turkish (not word-for-word). Fill `youtube` and `sources`.
3b. **Shorts.** Write `cities/<slug>/shorts.json` (format and example: `cities/london/shorts.json`, docs at the top of
   `tools/shorts.py`): **3 Shorts**, strongest first — (1) `whole`: the whole timeline in 50 s, (2) and (3) the two
   most dramatic stretches of this city's history (a fire, a siege, a boom), 45–50 s each, every one ≤ 59 s with hold.
   Hook line 1 ≤ 22 characters, facts in titles/descriptions only from research.md. Only as many as fit before the
   next long episode are rendered (Fri episode → Sat/Sun/Mon = 3, Tue episode → Wed/Thu = 2), in this order.
   Check with `python3 tools/shorts.py info <slug>`.
   Channel review (3 Nov 2026): the Shorts bring the views (1,000+ each), the long episode far less, and almost nobody
   subscribes. So: build every Short around **one turning point** (a fire, a siege, a boom) with a clear time promise in
   the title ("… in 50 Seconds", "From X to Y"); the `description` must stay factual (it follows the link line, which
   `tools/shorts.py` now puts first, plus a "which city next?" question). Do not renumber old titles; do not rework the
   long episode's opening until a couple of weeks of data exist.
   **Tell the owner after every upload** (Turkish; PushNotification in unattended runs): one line per Short —
   `<Short başlığı> (<link>) → ilgili video: <uzun video başlığı> (<link>). Studio'da "İlgili video" olarak bunu seç;
   uzun videoda sabit yorum yap.` The API cannot set either.
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
   Then render 3 vertical stills per Short locally (`python3 engine/render.py stills <slug> /tmp/s 2,25,49 --short <id>
   --w 540 --h 960 --langs en`, needs geo.json from the preview) and check the city fills the frame and the text reads.
7. When the stills are right: write `cities/<slug>/render.json` = `{"upload": true}`, commit + push
   (`episode: <slug> render`). The **Render episode** action renders in ~20 parallel machines, joins, adds music
   and uploads the English video to YouTube as private, scheduled for the next free slot. ~45–90 min. Do not wait.
8. Tick the city in `cities/queue.md`, commit + push. Tell the owner (Turkish, short): city, length, what the
   episode covers, that rendering started, and when it is scheduled to go live (read `publish_at` from `uploads.json` and convert to Istanbul time; do not assume a fixed hour).

## B. Report ("rapor", "durum")

`git pull`; read `uploads.json` (link, publish time), `cities/*/status.json` (render runs and upload logs), and the
last action runs (`gh api repos/velinazim/dust-to-downtown/actions/runs?per_page=10`). Report in Turkish: what is
scheduled/published, anything failed and why, what is next in the queue.

Report also: Shorts in `uploads.json` (`kind: short`) and `status.json` `shorts_upload_log`. If a long episode is
uploaded but its Shorts are missing, start them: `gh api -X POST repos/velinazim/dust-to-downtown/actions/workflows/shorts.yml/dispatches -f ref=main -f "inputs[slug]=<slug>" -f "inputs[upload]=true"`.

## C. Publish now / change time ("yayınla")

Write `requests/publish/<YYYYMMDD-HHMM>.json` = `{"video_ids": ["..."], "at": "<UTC ISO, optional>"}`; commit + push.
Result appears in `requests/done/` within ~5 minutes.

## Notes

- Upload failed but the render succeeded (no entry in `uploads.json`, error in `cities/<slug>/status.json`): first check
  the channel with the YouTube action `list` (writes `config/videos.txt`) so nothing is uploaded twice, then run
  **Upload rendered episode** (`upload.yml`, inputs slug + the render run id). Re-running it for an uploaded episode only
  retries a missing custom thumbnail (needs the phone-verified channel).

- Preview/geo failures: the log is committed to `cities/<slug>/geo_log.txt` (GitHub's own log host is not reachable
  from Claude sessions). Overpass (OSM) can be busy: the script retries for a few minutes; if it still fails, re-run
  the Preview action later (`gh api -X POST repos/velinazim/dust-to-downtown/actions/workflows/preview.yml/dispatches -f ref=main -f 'inputs[slug]=<slug>'`).
- The channel is phone-verified since 30 Oct 2026 (`config/whoami.txt`: longUploadsStatus=allowed): episodes may run
  past 15:00 and custom thumbnails work. Set `"long_ok": true` in city.json to silence the validator warning.
- A city can be written with a small generator (cities/london/_build.py) — keep it next to city.json.

- Never put secrets in files or chat. YouTube credentials live only in GitHub Secrets.
- The upload refuses to run if the token belongs to another channel (config/channel.json).
- Rendering is CPU-only in the cloud; ~70k buildings is the practical ceiling — raise `grain_m` for modern sprawl.
- Engine/look changes go in `engine/index.html`; test locally with
  `python3 engine/render.py stills istanbul-test /tmp/st auto --w 1280 --h 720` (hand-made test map, no network needed).

## D. Music swap of scheduled videos (9 Nov 2026)

The owner replaced the soundtrack style (soft major-key piano, `tools/music.py`). Videos uploaded before that with the
old music are swapped by the **Re-music scheduled videos** action (`remusic.yml`, daily 08:20 UTC, soonest first,
a few per day because of YouTube's upload quota). Each swap = new private video with the same publish time; the old one
is taken off the schedule and stays private (owner deletes it in Studio). Progress: `remusic_log.md`. In every report,
tell the owner the new lines from `remusic_log.md` — for each new Short the line already says which long video to pick
as "İlgili video" (the owner sets it by hand), and new long videos need their pinned comment again.

## E. Pacing test (12 Nov 2026, owner approved "bi deneyelim")

Competitor check: the 3D city-timelapse videos with millions of views run 3–10 min, open on the finished city, then
go back in time, and use daylight thumbnails with a huge city name and "No AI". Test episode: **Istanbul** cut to ~9 min
with `cold_open`, thumb style v2 and "(3D Timelapse, No AI)" in the title (CITY_SPEC "cold_open"). Its city.json was
edited directly (retime + fields): **do not re-run cities/istanbul/_build.py** (it would undo the test). Already-scheduled cities keep
the 13–16 min format; compare Istanbul's numbers (CTR, average view duration) with Vienna/Athens and tell the owner.
A replaced long episode now also re-points its Shorts' "Full episode" link (yt_api.repoint_shorts); the owner still
has to pick the new video as "İlgili video" for those Shorts and re-pin the comment in Studio.

## F. Era soundtrack (12 Nov 2026, owner liked the sample)

`tools/eras.py`: the instruments change with the era on screen (ancient lyre/frame drum → medieval choir → Ottoman ney/
darbuka in Hijaz or European baroque pluck → industrial piano + clock → modern synth). Enable per city with
`"music": {"style": "eras"}` (+ `"flavor": "ottoman"` for Istanbul-like cities). NOT enabled anywhere yet: it waits until
the Istanbul pacing test (section E) has a week of data, so the two changes can be judged separately. Then it is tested
on the next new episode; ask the owner before turning it on for all cities.

## G. Format for every NEW episode (owner approved 12 Nov 2026)

Queue reordered by measured demand (cities/queue.md). Every new episode, starting with New York:
- `"cold_open"` (7 s, kicker "<N> years · from <first> to <today>"), `"intro_seconds": 3`, length 480–600 s.
- `youtube.title`: "<City>: <N> Years in <M> Minutes (3D Timelapse, No AI)"; `youtube.thumb.style: "v2"`,
  `line2` "<first year> → TODAY", daylight `extra` (no mood=golden), camera on the most recognisable core.
- `"people_notes": true` + 8–12 `labels[].now` "today: …" lines + today's districts as labels (CITY_SPEC "people notes").
  Research step 2 also collects these then→now pairs with sources.
- `"music": {"style": "eras"}` (+ `"flavor": "ottoman"` only for Ottoman-era cities).
- Tell the owner after upload: pin the closing question as a comment (the API cannot pin).
Episodes already scheduled keep their old format (except Istanbul, section E).
