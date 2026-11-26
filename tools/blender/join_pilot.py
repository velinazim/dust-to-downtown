"""Join the Blender pilot: frames + engine overlay -> videos, side-by-side comparisons, QA sheets, timing.

  python3 tools/blender/join_pilot.py <exdir> <framesdir> <outdir>
"""
import glob, json, os, re, shutil, statistics, subprocess, sys
from PIL import Image

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def run(*a):
    print(" ".join(a), flush=True)
    subprocess.run(a, check=True)


def main():
    ex, fr, out = sys.argv[1:4]
    os.makedirs(out, exist_ok=True)
    lines = []
    for clip in ("A", "B"):
        d = json.load(open(os.path.join(ex, clip, "data.json")))
        f0, f1, fps, slug = d["f0"], d["f1"], d["fps"], d["slug"]
        src = os.path.join(fr, clip)
        missing = [f for f in range(f0, f1) if not os.path.exists(os.path.join(src, f"f_{f:06d}.png"))]
        if len(missing) == f1 - f0:
            lines.append(f"{clip}: no frames rendered"); continue
        prev = None
        for f in range(f0, f1):   # fill gaps (a failed job) with the previous frame so the video still plays
            p = os.path.join(src, f"f_{f:06d}.png")
            if os.path.exists(p): prev = p
            elif prev: shutil.copy(prev, p)
            else:
                nxt = next(os.path.join(src, f"f_{g:06d}.png") for g in range(f, f1) if os.path.exists(os.path.join(src, f"f_{g:06d}.png")))
                shutil.copy(nxt, p); prev = p
        n = f1 - f0
        bl = os.path.join(out, f"{slug}_{clip}_blender.mp4")
        run("ffmpeg", "-loglevel", "error", "-y", "-framerate", str(fps), "-start_number", str(f0), "-i", f"{src}/f_%06d.png",
            "-framerate", str(fps), "-start_number", str(f0), "-i", f"{ex}/ov{clip}/o_%06d.png",
            "-filter_complex", "[0][1]overlay,format=yuv420p", "-frames:v", str(n), "-c:v", "libx264", "-preset", "medium", "-crf", "20", bl)
        parts = sorted(glob.glob(f"{ex}/eng{clip}/chunk_en_*.mp4"))
        eng = []
        if parts:
            lst = os.path.join(out, f"_eng{clip}.txt")
            open(lst, "w").write("".join(f"file '{os.path.abspath(q)}'\n" for q in parts))
            eng = [os.path.join(out, f"_eng{clip}.mp4")]
            run("ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", eng[0])
        if eng:
            cmp_ = os.path.join(out, f"{slug}_{clip}_karsilastirma.mp4")
            lab = lambda t: f"drawtext=fontfile={FONT}:text='{t}':x=24:y=h-58:fontsize=34:fontcolor=white:box=1:boxcolor=black@0.55:boxborderw=10"
            run("ffmpeg", "-loglevel", "error", "-y", "-i", eng[0], "-i", bl, "-filter_complex",
                f"[0]scale=1280:720,{lab('Mevcut motor (Three.js)')}[a];[1]scale=1280:720,{lab('Blender (Cycles)')}[b];[a][b]hstack,format=yuv420p",
                "-c:v", "libx264", "-preset", "medium", "-crf", "22", cmp_)
            os.remove(eng[0]); os.remove(lst)
        # QA sheet: 16 evenly spaced frames of the finished Blender clip
        tiles = []
        for k in range(16):
            idx = min(n - 1, int((k + 0.5) * n / 16))
            p = os.path.join(out, f"_qa_{k}.png")
            run("ffmpeg", "-loglevel", "error", "-y", "-i", bl, "-vf", f"select=eq(n\\,{idx}),scale=480:270", "-frames:v", "1", p)
            tiles.append(p)
        sheet = Image.new("RGB", (480 * 4, 270 * 4))
        for k, p in enumerate(tiles):
            sheet.paste(Image.open(p), ((k % 4) * 480, (k // 4) * 270)); os.remove(p)
        sheet.save(os.path.join(out, f"{slug}_{clip}_qa_sheet.jpg"), quality=85)
        lines.append(f"{clip}: frames {f0}-{f1} ({n}), missing {len(missing)}")
    # timing
    walls = []
    for p in glob.glob(os.path.join(fr, "timing_*.txt")):
        m = re.search(r"wall (\d+) s, cores (\d+)", open(p).read())
        if m: walls.append((int(m.group(1)), int(m.group(2))))
    # clip B frames also lie inside A's range: split by the order the logs were written (A first, then B)
    per = {"A": [], "B": []}
    for p in glob.glob(os.path.join(fr, "timing_*.txt")):
        part = "A"; seen_built = 0
        for ln in open(p).read().splitlines():
            if ln.startswith("scene built"):
                seen_built += 1; part = "A" if seen_built == 1 else "B"
            mm = re.match(r"frame (\d+) \((\d+)\) ([\d.]+)s", ln)
            if mm: per[part].append(float(mm.group(3)))
    for c in ("A", "B"):
        if per[c]:
            s = statistics.mean(per[c])
            lines.append(f"{c}: {len(per[c])} frames, {s:.1f} s/frame avg (min {min(per[c]):.1f}, max {max(per[c]):.1f}) at 1920x1080, 24 samples")
    if walls:
        lines.append(f"render jobs: {len(walls)}, wall max {max(w for w, _ in walls) / 60:.1f} min, cores {walls[0][1]}")
    allf = per["A"] + per["B"]
    if allf:
        s = statistics.mean(allf); ep = 9 * 60 * 30
        lines.append(f"estimate for a 9-min episode ({ep} frames): {s * ep / 3600:.0f} machine-hours = "
                     f"{s * ep / 3600 / 20:.1f} h on 20 parallel machines (GitHub job limit 6 h)")
    open(os.path.join(out, "timing.txt"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
