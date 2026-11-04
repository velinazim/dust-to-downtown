#!/usr/bin/env python3
"""Final-video QA: contact sheet of evenly spaced frames + speech-to-text vs. script, word by word.

    python3 tools/video_qa.py <video.mp4> [--script <lines.json | episode.json | text file>] [--out DIR] [--frames 12] [--silent]

What it does
  1. Frames: grabs N evenly spaced frames from the FINISHED video and tiles them into ONE image
     (<out>/qa_sheet.jpg, each tile stamped with its timestamp). The agent MUST open that image and look at every tile
     (captions readable and spelled right, nothing cut off, right picture for the words, no black/blank/stuck frames).
  2. Words (skipped with --silent, or when the file has no audio stream): transcribes the audio with Whisper
     (sherpa-onnx, model downloaded once from the k2-fsa GitHub release, cached in ~/.cache/video_qa) and compares the
     transcript with the narration in the script word by word. Differences are printed with timestamps.
Exit code: 0 = clean, 1 = needs a look (mismatches above tolerance, or a problem frame), 2 = tool error.
The last line printed is ONE line summary, ready to paste into the owner's report.

Script formats understood: lines.json ([{"say": ...}]), episode json with scenes[].narration, any text file.
"""
import argparse
import warnings
import bz2
import difflib
import json
import os
import re
import subprocess
import sys
import tarfile
import urllib.request
import wave
from pathlib import Path

warnings.filterwarnings("ignore")

MODEL = "sherpa-onnx-whisper-base.en"
MODEL_URL = f"https://github.com/k2-fsa/sherpa-onnx/releases/download/asr-models/{MODEL}.tar.bz2"
CACHE = Path(os.path.expanduser("~/.cache/video_qa"))

ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, **kw)


def num_words(n):
    if n < 20:
        return [ONES[n]]
    if n < 100:
        return [TENS[n // 10]] + ([ONES[n % 10]] if n % 10 else [])
    if n < 1000:
        return [ONES[n // 100], "hundred"] + (num_words(n % 100) if n % 100 else [])
    if n < 1000000:
        return num_words(n // 1000) + ["thousand"] + (num_words(n % 1000) if n % 1000 else [])
    return [str(n)]


def tokens(text):
    """Lower-case word list; digits are spelled out so '2,000' matches 'two thousand'."""
    text = text.lower().replace("’", "'").replace("—", " ").replace("–", " ")
    text = re.sub(r"(\d),(\d{3})", r"\1\2", text)
    text = re.sub(r"(\d+)\s*%", r"\1 percent", text)
    out = []
    for w in re.findall(r"[a-z0-9']+", text):
        if w.isdigit():
            n = int(w)
            if 1100 <= n <= 2099 and len(w) == 4:  # years may be said either way; keep as spoken pairs below
                out.append(("YEAR", w))
                continue
            out.extend(num_words(n))
        else:
            out.append(w.strip("'"))
    out = [t if isinstance(t, tuple) else re.sub(r"our(ed|s|ing)?$", r"or\1", t) for t in out]
    return [t for t in out if t]


def flat(ts):
    return [t if isinstance(t, str) else t[1] for t in ts]


def year_forms(y):
    n = int(y)
    a, b = n // 100, n % 100
    forms = {" ".join(num_words(n))}
    forms.add(" ".join(num_words(a) + (["oh"] + num_words(b) if 0 < b < 10 else num_words(b) if b else ["hundred"])))
    return forms


def load_script(path):
    p = Path(path)
    raw = p.read_text(encoding="utf-8")
    try:
        data = json.loads(raw)
    except ValueError:
        return raw
    parts = []
    if isinstance(data, list):
        for x in data:
            if isinstance(x, dict):
                parts.append(x.get("say") or x.get("narration") or x.get("text") or "")
            elif isinstance(x, str):
                parts.append(x)
    elif isinstance(data, dict):
        for s in data.get("scenes", []):
            parts.append(s.get("narration") or s.get("say") or "")
    return " ".join(parts)


def probe(video):
    r = run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type", "-of", "json", str(video)])
    j = json.loads(r.stdout or "{}")
    dur = float(j.get("format", {}).get("duration", 0))
    has_audio = any(s.get("codec_type") == "audio" for s in j.get("streams", []))
    return dur, has_audio


def contact_sheet(video, dur, out, n):
    from PIL import Image, ImageDraw, ImageFont
    out.mkdir(parents=True, exist_ok=True)
    tiles, stats = [], []
    for i in range(n):
        t = dur * (i + 0.5) / n
        f = out / f"qa_f{i:02d}.jpg"
        run(["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.2f}", "-i", str(video), "-frames:v", "1", "-vf", "scale=360:-2", "-q:v", "3", str(f)])
        if not f.exists():
            stats.append((t, "no frame decoded"))
            continue
        im = Image.open(f).convert("RGB")
        g = im.convert("L").resize((48, 48))
        px = list(g.getdata())
        mean = sum(px) / len(px)
        spread = max(px) - min(px)
        if mean < 12 or spread < 10:
            stats.append((t, "blank/near-black frame" if mean < 40 else "flat frame"))
        tiles.append((t, im))
        f.unlink()
    if not tiles:
        return None, ["no frames could be decoded"]
    w, h = tiles[0][1].size
    cols = 4 if w >= h else 6
    rows = (len(tiles) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * w, rows * h), (20, 20, 20))
    d = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 16)
    except OSError:
        font = ImageFont.load_default()
    for k, (t, im) in enumerate(tiles):
        x, y = (k % cols) * w, (k // cols) * h
        sheet.paste(im, (x, y))
        d.rectangle([x, y, x + 78, y + 22], fill=(0, 0, 0))
        d.text((x + 4, y + 2), f"{int(t // 60)}:{t % 60:04.1f}", fill=(255, 255, 255), font=font)
    path = out / "qa_sheet.jpg"
    sheet.save(path, quality=85)
    return path, [f"{int(t // 60)}:{t % 60:04.1f} {msg}" for t, msg in stats]


def ensure_model():
    d = CACHE / MODEL
    if (d / f"{MODEL.split('sherpa-onnx-whisper-')[1]}-encoder.int8.onnx").exists():
        return d
    CACHE.mkdir(parents=True, exist_ok=True)
    tgz = CACHE / (MODEL + ".tar.bz2")
    print(f"downloading speech model once ({MODEL}) ...", flush=True)
    urllib.request.urlretrieve(MODEL_URL, tgz)
    with tarfile.open(tgz, "r:bz2") as tf:
        tf.extractall(CACHE)
    tgz.unlink()
    return d


def transcribe(video, out):
    import numpy as np
    try:
        import sherpa_onnx
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--break-system-packages", "sherpa-onnx"], capture_output=True)
        import sherpa_onnx
    wav = out / "qa_audio.wav"
    run(["ffmpeg", "-y", "-v", "error", "-i", str(video), "-vn", "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(wav)])
    d = ensure_model()
    name = MODEL.split("sherpa-onnx-whisper-")[1]
    rec = sherpa_onnx.OfflineRecognizer.from_whisper(
        encoder=str(d / f"{name}-encoder.int8.onnx"), decoder=str(d / f"{name}-decoder.int8.onnx"),
        tokens=str(d / f"{name}-tokens.txt"), language="en", task="transcribe", num_threads=2)
    with wave.open(str(wav)) as wf:
        sr = wf.getframerate()
        audio = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16).astype(np.float32) / 32768
    # cut on the quietest point near each 25 s mark so words are not split
    seg, words, pos = 25 * sr, [], 0
    while pos < len(audio):
        end = min(pos + seg, len(audio))
        if end < len(audio):
            win = audio[end - 2 * sr:end + 2 * sr] if end - 2 * sr > pos else audio[pos:end]
            hop = sr // 50
            env = [float(np.mean(win[i:i + hop] ** 2)) for i in range(0, len(win) - hop, hop)]
            end = (end - 2 * sr if end - 2 * sr > pos else pos) + int(np.argmin(env)) * hop
        chunk = audio[pos:end]
        if len(chunk) > sr // 4:
            s = rec.create_stream()
            s.accept_waveform(sr, chunk)
            rec.decode_stream(s)
            ws = [flat([w])[0] for w in tokens(s.result.text)]
            for k, w in enumerate(ws):
                words.append((w, pos / sr + (end - pos) / sr * k / max(len(ws), 1)))
        pos = end if end > pos else pos + seg
    wav.unlink()
    return words


def compare(script_text, heard):
    ref = tokens(script_text)
    ref_flat = []
    for t in ref:
        ref_flat.append(t if isinstance(t, str) else t[1])
    heard_words = [w for w, _ in heard]
    times = [t for _, t in heard]
    # years: accept either "1453" read out as words
    exp = []
    for t in ref:
        if isinstance(t, tuple):
            exp.append(("Y", t[1]))
        else:
            exp.append(t)
    # build the reference list with year alternatives resolved against what was heard
    ref_list, i = [], 0
    hs = " ".join(heard_words)
    for t in exp:
        if isinstance(t, tuple):
            best = None
            for form in year_forms(t[1]):
                if form in hs:
                    best = form
                    break
            ref_list.extend((best or sorted(year_forms(t[1]))[0]).split())
        else:
            ref_list.append(t)
    sm = difflib.SequenceMatcher(a=ref_list, b=heard_words, autojunk=False)
    issues = []
    for op, a0, a1, b0, b1 in sm.get_opcodes():
        if op == "equal":
            continue
        if "".join(ref_list[a0:a1]) == "".join(heard_words[b0:b1]):
            continue  # "for ever" vs "forever"
        at = times[b0] if b0 < len(times) else (times[-1] if times else 0)
        issues.append({"at": round(at, 1), "script": " ".join(ref_list[a0:a1]), "heard": " ".join(heard_words[b0:b1]), "op": op})
    wrong = sum(max(a1 - a0, b1 - b0) for op, a0, a1, b0, b1 in sm.get_opcodes()
                if op != "equal" and "".join(ref_list[a0:a1]) != "".join(heard_words[b0:b1]))
    return issues, wrong, len(ref_list)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--script")
    ap.add_argument("--out")
    ap.add_argument("--frames", type=int, default=12)
    ap.add_argument("--silent", action="store_true", help="video has no narration (frames check only)")
    ap.add_argument("--tolerance", type=float, default=0.04, help="word mismatch share above which the check fails")
    a = ap.parse_args()
    video = Path(a.video)
    out = Path(a.out) if a.out else video.parent
    dur, has_audio = probe(video)
    if dur <= 0:
        print("QA ERROR: cannot read the video")
        return 2
    sheet, frame_issues = contact_sheet(video, dur, out, a.frames)
    print(f"CONTACT SHEET: {sheet}  ({a.frames} frames over {dur:.1f}s) — open it and look at every tile")
    for m in frame_issues:
        print("  FRAME PROBLEM:", m)
    ok = not frame_issues
    summary = f"{a.frames} kare"
    if a.silent or not has_audio:
        print("WORDS: skipped (--silent, or no audio)")
        summary += ", kelime kontrolü yok (sessiz/kısa kesit)"
    else:
        if not a.script:
            print("QA ERROR: --script is required for narrated videos")
            return 2
        try:
            heard = transcribe(video, out)
        except Exception as e:  # model missing/blocked: say it, never pretend
            print(f"QA ERROR: speech check could not run ({type(e).__name__}: {str(e)[:160]})")
            return 2
        issues, wrong, total = compare(load_script(a.script), heard)
        rate = wrong / max(total, 1)
        print(f"WORDS: {total} script words, {wrong} differ ({rate:.1%}); tolerance {a.tolerance:.0%}")
        for it in issues[:40]:
            print(f"  @{it['at']:>6}s  script: [{it['script']}]  heard: [{it['heard']}]")
        print("  (small speech-to-text slips on rare names are normal: listen/decide; real script/audio drift is not)")
        ok = ok and rate <= a.tolerance
        summary += f", {total} kelime, {wrong} fark"
    print(f"QA {'OK' if ok else 'CHECK'}: {summary}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
