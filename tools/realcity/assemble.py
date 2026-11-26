"""Frames -> mp4 with title + OSM attribution, plus a QA contact sheet of evenly spaced frames.

  python3 tools/realcity/assemble.py <framesdir> <outdir> --title ANTALYA --frames 900
"""
import argparse, glob, os, subprocess
from PIL import Image, ImageDraw, ImageFont


def font(sz, bold=True):
    for p in ['/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf' % ('-Bold' if bold else ''),
              '/usr/share/fonts/truetype/liberation/LiberationSans-%s.ttf' % ('Bold' if bold else 'Regular')]:
        if os.path.exists(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('fr'); ap.add_argument('out')
    ap.add_argument('--title', default='ANTALYA'); ap.add_argument('--frames', type=int, default=900)
    ap.add_argument('--fps', type=int, default=30)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True); tmp = os.path.join(a.out, '_ov'); os.makedirs(tmp, exist_ok=True)
    files = sorted(glob.glob(os.path.join(a.fr, '**', 'f_*.png'), recursive=True))
    have = {int(os.path.basename(f)[2:6]): f for f in files}
    missing = [i for i in range(a.frames) if i not in have]
    print('frames', len(have), 'missing', len(missing), missing[:20])
    F1, F2 = font(86), font(22, False)
    last = None
    for i in range(a.frames):
        src = have.get(i, last)
        last = src
        im = Image.open(src).convert('RGB').resize((1920, 1080), Image.LANCZOS)
        ov = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
        t = i / a.fps
        al = max(0.0, min(1.0, (t - 0.8) / 0.8, (5.5 - t) / 0.8))
        if al > 0:
            d.text((96 + 2, 860 + 3), a.title, font=F1, fill=(0, 0, 0, int(120 * al)))
            d.text((96, 860), a.title, font=F1, fill=(255, 255, 255, int(255 * al)))
        d.text((1920 - 330, 1080 - 44), '© OpenStreetMap contributors', font=F2, fill=(255, 255, 255, 190))
        Image.alpha_composite(im.convert('RGBA'), ov).convert('RGB').save(os.path.join(tmp, 'o_%04d.png' % i))
    mp4 = os.path.join(a.out, 'antalya_real_buildings.mp4')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(a.fps), '-i', os.path.join(tmp, 'o_%04d.png'),
                    '-c:v', 'libx264', '-preset', 'slow', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', mp4], check=True)
    # QA contact sheet: 16 evenly spaced frames
    idx = [round(k * (a.frames - 1) / 15) for k in range(16)]
    sheet = Image.new('RGB', (4 * 480, 4 * 290), (20, 20, 20)); d = ImageDraw.Draw(sheet)
    for n, i in enumerate(idx):
        th = Image.open(os.path.join(tmp, 'o_%04d.png' % i)).resize((480, 270))
        x, y = (n % 4) * 480, (n // 4) * 290
        sheet.paste(th, (x, y)); d.text((x + 6, y + 271), 'frame %d  (%.1fs)' % (i, i / a.fps), font=font(15, False), fill=(230, 230, 230))
    sheet.save(os.path.join(a.out, 'qa_sheet.jpg'), quality=88)
    for p in glob.glob(os.path.join(tmp, '*')):
        os.remove(p)
    os.rmdir(tmp)
    with open(os.path.join(a.out, 'missing.txt'), 'w') as f:
        f.write(' '.join(map(str, missing)))
    print('wrote', mp4)


if __name__ == '__main__':
    main()
