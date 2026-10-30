"""Join rendered chunks into the final episode files and write YouTube metadata.

  python3 tools/assemble.py <slug> <chunks_dir> <out_dir>

out_dir/<lang>/video.mp4, thumb.jpg (if present in chunks_dir as thumb_<lang>.jpg), meta.json
"""
import glob, json, os, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def ts(sec):
    sec = int(round(sec)); h, m, s = sec // 3600, sec % 3600 // 60, sec % 60
    return f'{h}:{m:02d}:{s:02d}' if h else f'{m}:{s:02d}'


def T(o, lang):
    return o if isinstance(o, str) else (o or {}).get(lang) or (o or {}).get('en', '')


def describe(city, lang, dur):
    yt = city.get('youtube', {})
    t, chapters = 0.0, []
    for s in city['segments']:
        if s.get('chapter'):
            chapters.append((t, T(s['chapter'], lang)))
        t += s['seconds']
    if not chapters or chapters[0][0] > 0:
        chapters.insert(0, (0, 'Intro' if lang == 'en' else 'Giriş'))
    chapters = [c for i, c in enumerate(chapters) if i == 0 or c[0] - chapters[i - 1][0] >= 10]   # YouTube needs ≥10 s chapters
    lines = [T(yt.get('description', ''), lang).strip(), '']
    lines += [f'{ts(a)} {b}' for a, b in chapters]
    src = city.get('sources', [])
    if src:
        lines += ['', 'Sources:' if lang == 'en' else 'Kaynaklar:'] + [f'• {s["title"]}' + (f' — {s["url"]}' if s.get('url') else '') for s in src[:15]]
    note = {'en': 'Reconstruction note: buildings are simplified symbols placed from historical maps and research; '
                  'population figures before modern censuses are scholarly estimates.\nTerrain: AWS Terrain Tiles; water: © OpenStreetMap contributors. Music: original.',
            'tr': 'Not: Binalar tarihî harita ve araştırmalara göre yerleştirilmiş sade sembollerdir; modern nüfus sayımlarından önceki rakamlar '
                  'akademik tahminlerdir.\nArazi: AWS Terrain Tiles; su: © OpenStreetMap katkıcıları. Müzik: özgün.'}[lang]
    lines += ['', note, '', ' '.join(yt.get('hashtags', ['#history', '#timelapse', '#cities']))]
    return '\n'.join(lines)[:4900]


def main(slug, chunks, out):
    city = json.load(open(os.path.join(ROOT, 'cities', slug, 'city.json')))
    dur = sum(s['seconds'] for s in city['segments'])
    yt = city.get('youtube', {})
    music = os.path.join(out, 'music.wav')
    os.makedirs(out, exist_ok=True)
    subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'music.py'), str(dur + 1), music, str(city.get('seed', 7))], check=True)
    langs = sorted({os.path.basename(p).split('_')[1] for p in glob.glob(os.path.join(chunks, '**', 'chunk_*_*.mp4'), recursive=True)})
    for lang in langs:
        parts = sorted(glob.glob(os.path.join(chunks, '**', f'chunk_{lang}_*.mp4'), recursive=True), key=lambda p: int(p.rsplit('_', 1)[1].split('.')[0]))
        d = os.path.join(out, lang); os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, 'list.txt'), 'w') as f:
            for p in parts:
                f.write(f"file '{os.path.abspath(p)}'\n")
        # The uploaded (English) version is scaled to 1440p: YouTube then streams it with its higher-bitrate codec,
        # which looks much sharper than a 1080p upload even when watched at 1080p.
        vcodec = (['-vf', 'scale=2560:1440:flags=lanczos', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '16', '-pix_fmt', 'yuv420p']
                  if lang == 'en' else ['-c:v', 'copy'])
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', os.path.join(d, 'list.txt'), '-i', music,
                        '-map', '0:v', '-map', '1:a', *vcodec, '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart',
                        os.path.join(d, 'video.mp4')], check=True)
        os.remove(os.path.join(d, 'list.txt'))
        th = glob.glob(os.path.join(chunks, '**', f'thumb_{lang}.jpg'), recursive=True)
        if th:
            shutil.copy(th[0], os.path.join(d, 'thumb.jpg'))
        other = 'tr' if lang == 'en' else 'en'
        meta = {'slug': slug, 'kind': 'long', 'lang': lang, 'file': 'video.mp4', 'thumb': 'thumb.jpg' if th else None,
                'title': T(yt.get('title', city['name']), lang), 'description': describe(city, lang, dur),
                'tags': yt.get('tags', []), 'playlist': T(yt.get('playlist'), lang) or None,
                'playlist_desc': T(yt.get('playlist_desc', ''), lang),
                'localizations': {other: {'title': T(yt.get('title', city['name']), other)[:100], 'description': describe(city, other, dur)}},
                'duration_s': dur}
        json.dump(meta, open(os.path.join(d, 'meta.json'), 'w'), indent=1, ensure_ascii=False)
        print('assembled', lang, len(parts), 'chunks', os.path.getsize(os.path.join(d, 'video.mp4')) // 1e6, 'MB')
    os.remove(music)


if __name__ == '__main__':
    main(*sys.argv[1:4])
