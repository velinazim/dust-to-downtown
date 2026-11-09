# Music library

Put tracks downloaded from **YouTube Studio → Audio Library** here, in `music/library/`
(mp3/wav/m4a). Only pick tracks marked **"No attribution required"**.

Every episode and Short shuffles these tracks by its seed, joins them with 4 s crossfades,
and levels the result to a soft ~-23 LUFS background. If the folder is empty, the built-in
generator (`tools/music.py`) is used instead.
