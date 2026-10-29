# city.json — how an episode is described

Every episode is one file, `cities/<slug>/city.json`. The engine draws everything from it; the map
(land, water, hills) comes from real data and is generated automatically (`geo.json`).
All coordinates are **[lat, lon]** (latitude first). All visible text is bilingual `{"en": "...", "tr": "..."}`.
Years: negative = BC, positive = AD.

## Accuracy rules (non-negotiable)

1. Every date, population figure and location must come from a source you actually opened. Record each in
   `research.md` with the source next to it. When sources disagree, give the range and pick the mainstream figure.
2. Population before modern censuses = scholarly estimate; never invent precision. Leave `population` out of a
   segment when there is no reasonable estimate.
3. Coordinates: landmarks from their Wikipedia/OSM coordinates; walls/roads/districts traced from historical-map
   descriptions and known gates/landmarks. Walls must run on land and end at the shore/river.
4. Things that existed but whose exact footprint is unknown: draw a plausible simplified area and say so in
   `research.md`. Never place a named building where it was not.
5. Sensitive history (wars, massacres, plagues): state it plainly and neutrally in the subtitle; no graphic wording.

## Top level

```json
{
  "slug": "london",
  "name": {"en": "London", "tr": "Londra"},
  "intro": {"en": "2,000 Years in 15 Minutes", "tr": "15 Dakikada 2.000 Yıl"},
  "intro_seconds": 4.5,
  "seed": 47,
  "geo": {"bbox": [51.28, -0.52, 51.70, 0.33], "cell_m": 80},
  "view": {"azimuth_deg": 0, "pitch_deg": 46, "fov": 34},
  "render": {"vertical_exaggeration": 3.0},
  "segments": [...], "districts": [...], "walls": [...], "landmarks": [...],
  "bridges": [...], "roads": [...], "open_spaces": [...], "fires": [...],
  "camps": [...], "smoke": [...], "labels": [...], "geo_edits": [...],
  "youtube": {...}, "sources": [{"title": "...", "url": "..."}]
}
```

- `geo.bbox` = [south, west, north, east]; must contain everything the camera ever shows. Keep it ≤ ~60 × 60 km.
  `cell_m` 60–120 (bigger bbox → bigger cells).
- `view.azimuth_deg`: 0 = camera south of the city looking north. Choose the direction that puts the main
  water (river/sea) across the frame and the old core in the middle.
- `geo_edits`: historical water/land the modern map lacks or has extra (filled harbours, reclaimed land):
  `{"op": "water"|"land", "poly": [[lat,lon],...]}`.

## segments — the timeline (this is the script)

Played in order. Each segment = a span of years shown over `seconds`. Years may jump between segments.

```json
{"from": 43, "to": 60, "seconds": 22,
 "era": {"en": "Roman", "tr": "Roma"}, "city_name": {"en": "Londinium", "tr": "Londinium"},
 "title": {"en": "Londinium Is Founded", "tr": "Londinium Kuruluyor"},
 "sub": {"en": "AD 47–50: Romans bridge the Thames and lay out a trading town", "tr": "MS 47–50: Romalılar Thames'e köprü kurar, bir ticaret kasabası kurulur"},
 "population": [1000, 10000],
 "camera": {"center": [51.511, -0.088], "dist_km": 4.0},
 "chapter": {"en": "Roman Londinium", "tr": "Roma Londinium'u"}}
```

- Target total **13–16 minutes (780–960 s)**, 35–50 segments, titled segments 14–30 s each.
  Quiet "time passes" segments without `title` (5–10 s) between big events are good pacing.
- `title` ≤ 34 characters, `sub` ≤ 95 characters, one concrete fact with a date.
- `population`: [start, end] of the segment, or one number. Omit when unknown.
- `camera`: where the camera is centred at the middle of the segment, and how far (km). Start close
  (2–5 km) on the first settlement and pull back as the city grows (up to ~40 km for a modern metropolis).
  Change gradually; big jumps look jerky. Segments without a camera keep the previous one.
- `chapter`: marks YouTube chapters (6–12 per episode, ≥10 s apart).

## districts — where buildings appear

```json
{"name": "Roman city", "style": "roman", "poly": [[lat,lon],...], "from": 50, "to": 120,
 "density": 0.8, "grow_from": [51.511, -0.088], "grain_m": 60, "grid_deg": 20, "fade": [410, 450, 0.1]}
```

- Buildings grow from `grow_from` outwards between `from` and `to`.
- A later district overlapping an earlier one **replaces** its buildings automatically when it grows.
- `fade`: [year_start, year_end, fraction_kept] = decline/abandonment (survivors form clusters).
- `style`: ancient, roman, celtic, medieval, stone, ottoman, georgian, industrial, victorian, suburb, modern, highrise.
- `grain_m` = spacing; default per style (60 m old towns … 150 m highrise). For huge modern suburbs use 150–250.
- Budget: the validator estimates buildings; keep the total under ~60,000.
- `grid_deg`: orientation of a planned street grid (omit for organic towns).

## walls, roads, bridges

```json
{"name": "London Wall", "path": [[lat,lon],...], "built": 200, "removed": 1760, "height": "mid",
 "towers_m": 90, "double": false, "double_side": 1, "moat": false}
{"name": "Watling Street", "path": [...], "from": 50, "to": null, "kind": "roman", "width_m": 20}
{"name": "Old London Bridge", "path": [[a],[b]], "built": 1209, "removed": 1831, "style": "stone", "width_m": 20}
```

- walls `height`: low | mid | high. `double_side`: 1 or -1 picks which side the outer wall/moat goes to (try both in preview).
- road `kind`: road, roman, avenue, rail, motorway. Roads also keep buildings off their line.
- bridge `style`: wood, stone, iron, modern, tower. Path = the two bank points.

## landmarks

```json
{"type": "cathedral", "name": {"en": "Old St Paul's", "tr": "Eski St Paul"}, "at": [lat, lon], "built": 1240,
 "removed": 1666, "rot_deg": 0, "scale": 1.3, "size_m": [180, 40, 35], "colors": {"wall": "#d7d0c0", "roof": "#5f666f"},
 "additions": [{"type": "minarets", "year": 1453, "count": 4}]}
```

Types: temple, church, cathedral, domechurch (big central dome; colors.lantern=true for a lantern; colors.towers=true
for two west towers), mosque (colors.minarets = n), castle, fort, tower, clocktower, palace, parliament, amphitheatre,
circus (hippodrome), stadium, forum, column, obelisk, skyscraper, spire_tower (pyramid tower like the Shard), wheel,
dome_arena, station, harbor, box (generic). `rot_deg` = clockwise from east along the long axis.
Landmarks are drawn ~1.3–1.6× real size (`scale`) so they read at a distance; keep it modest.

## fires, camps, smoke, open spaces, labels

```json
"fires": [{"year": 1666, "poly": [...], "duration_s": 6, "plumes": 6}]          // buildings inside burn away
"camps": [{"poly": [...], "from": 1452, "to": 1460, "count": 250}]              // army tents
"smoke": [{"at": [lat,lon], "from": 1453, "to": 1460, "scale": 1}]
"open_spaces": [{"name": "Hyde Park", "poly": [...]}]                            // never built on, trees stay
"labels": [{"text": {"en": "RIVER THAMES", "tr": "THAMES NEHRİ"}, "at": [lat,lon], "kind": "water", "from": -50, "to": null}]
```

Label kinds: water (italic, on the water), place (dot + name), region (spaced capitals, no dot).
Show only a few labels at a time; place labels for the landmark the current title is about.

## youtube

```json
"youtube": {
  "title": {"en": "London: 2,000 Years in 15 Minutes (3D Timelapse)", "tr": "Londra: 15 Dakikada 2.000 Yıl (3D Timelapse)"},
  "description": {"en": "From a Roman bridgehead to a global capital…", "tr": "…"},
  "tags": ["london history", "history of london", "londinium", "3d timelapse", "city evolution"],
  "hashtags": ["#London", "#History", "#Timelapse"],
  "playlist": {"en": "Cities of Europe", "tr": "Avrupa Şehirleri"},
  "thumb": {"line1": {"en": "London", "tr": "Londra"}, "line2": {"en": "2,000 YEARS", "tr": "2.000 YIL"}, "line3": {"en": "From Roman fort to megacity", "tr": "Roma kalesinden megakente"}}
}
```

Chapters, sources, the reconstruction note and the other-language title/description are added automatically.
