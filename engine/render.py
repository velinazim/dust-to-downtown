"""Frame capture for the Dust to Downtown engine.

  python3 engine/render.py info   <slug>
  python3 engine/render.py stills <slug> <outdir> <t1,t2,...|auto> [--langs en,tr] [--w 1920 --h 1080]
  python3 engine/render.py chunk  <slug> <outdir> --start F0 --end F1 [--fps 30] [--langs en,tr]

A local static server is started on the repo root automatically.
Chunks are H.264 files with identical settings so they can be joined with the ffmpeg concat demuxer.
"""
import argparse, functools, http.server, json, os, shutil, socketserver, subprocess, sys, threading, time
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARGS = ["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist", "--disable-gpu-sandbox"]


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


def serve():
    handler = functools.partial(Quiet, directory=ROOT)
    httpd = socketserver.ThreadingTCPServer(("127.0.0.1", 0), handler)
    httpd.daemon_threads = True
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd.server_address[1]


def open_page(p, port, slug, mode, lang, w, h, extra=""):
    b = p.chromium.launch(args=ARGS)
    pg = b.new_page(viewport={"width": w, "height": h}, device_scale_factor=1)
    pg.on("pageerror", lambda e: print("[pageerror]", e, file=sys.stderr))
    pg.on("console", lambda m: print("[console]", m.text, file=sys.stderr) if m.type == "error" else None)
    pg.goto(f"http://127.0.0.1:{port}/engine/index.html?city={slug}&mode={mode}&lang={lang}&w={w}&h={h}{extra}")
    pg.wait_for_function("window.ready === true", timeout=600000)
    return b, pg


def duration(slug):
    c = json.load(open(os.path.join(ROOT, "cities", slug, "city.json")))
    return sum(s["seconds"] for s in c["segments"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd"); ap.add_argument("slug"); ap.add_argument("out", nargs="?"); ap.add_argument("times", nargs="?")
    ap.add_argument("--langs", default="en,tr"); ap.add_argument("--w", type=int, default=1920); ap.add_argument("--h", type=int, default=1080)
    ap.add_argument("--fps", type=int, default=30); ap.add_argument("--start", type=int, default=0); ap.add_argument("--end", type=int, default=-1)
    ap.add_argument("--crf", default="19"); ap.add_argument("--extra", default="")
    a = ap.parse_args()
    langs = [l for l in a.langs.split(",") if l]
    dur = duration(a.slug)
    if a.cmd == "info":
        print(json.dumps({"duration_s": dur, "frames": int(round(dur * a.fps))}))
        return
    port = serve()
    os.makedirs(a.out, exist_ok=True)
    with sync_playwright() as p:
        if a.cmd == "stills":
            ts = [round(dur * k / 17, 2) for k in range(1, 17)] if a.times in (None, "auto") else [float(x) for x in a.times.split(",")]
            b, pg = open_page(p, port, a.slug, "scene", "en", a.w, a.h, a.extra)
            print("stats", pg.evaluate("window.stats"), flush=True)
            for t in ts:
                t0 = time.time(); pg.evaluate(f"window.renderAt({t})")
                pg.screenshot(path=f"{a.out}/s_{t:07.2f}.png")
                print(f"  scene t={t} {time.time() - t0:.1f}s", flush=True)
            b.close()
            for lang in langs:
                b, pg = open_page(p, port, a.slug, "overlay", lang, a.w, a.h)
                for t in ts:
                    pg.evaluate(f"window.renderAt({t})")
                    pg.screenshot(path=f"{a.out}/o_{lang}_{t:07.2f}.png", omit_background=True)
                b.close()
                for t in ts:
                    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", f"{a.out}/s_{t:07.2f}.png", "-i", f"{a.out}/o_{lang}_{t:07.2f}.png",
                                    "-filter_complex", "overlay", f"{a.out}/{lang}_{t:07.2f}.jpg"], check=True)
                    os.remove(f"{a.out}/o_{lang}_{t:07.2f}.png")
            for t in ts:
                os.remove(f"{a.out}/s_{t:07.2f}.png")
        elif a.cmd == "thumb":
            cj = json.load(open(os.path.join(ROOT, "cities", a.slug, "city.json"))).get("youtube", {}).get("thumb", {})
            t = float(a.times) if a.times not in (None, "auto") else float(cj.get("t", round(dur * 0.93, 2)))
            b, pg = open_page(p, port, a.slug, "scene", "en", 1280, 720, a.extra or cj.get("extra", ""))
            pg.evaluate(f"window.renderAt({t})"); pg.screenshot(path=f"{a.out}/thumb_scene.png"); b.close()
            for lang in langs:
                b, pg = open_page(p, port, a.slug, "overlay", lang, 1280, 720, "&thumb=1")
                pg.screenshot(path=f"{a.out}/thumb_ov_{lang}.png", omit_background=True); b.close()
                subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", f"{a.out}/thumb_scene.png", "-i", f"{a.out}/thumb_ov_{lang}.png",
                                "-filter_complex", "overlay", "-q:v", "3", f"{a.out}/thumb_{lang}.jpg"], check=True)
                os.remove(f"{a.out}/thumb_ov_{lang}.png")
            os.remove(f"{a.out}/thumb_scene.png")
        elif a.cmd == "chunk":
            n = int(round(dur * a.fps)); f0 = a.start; f1 = n if a.end < 0 else min(a.end, n)
            tmp = os.path.join(a.out, f"tmp_{f0}")
            os.makedirs(f"{tmp}/scene", exist_ok=True)
            b, pg = open_page(p, port, a.slug, "scene", "en", a.w, a.h, a.extra)
            t0 = time.time()
            for f in range(f0, f1):
                pg.evaluate(f"window.renderAt({f / a.fps})")
                pg.screenshot(path=f"{tmp}/scene/{f - f0:05d}.jpg", type="jpeg", quality=92)
                if (f - f0) % 60 == 0:
                    print(f"scene {f - f0}/{f1 - f0} {time.time() - t0:.0f}s", flush=True)
            b.close()
            for lang in langs:
                os.makedirs(f"{tmp}/ov_{lang}", exist_ok=True)
                b, pg = open_page(p, port, a.slug, "overlay", lang, a.w, a.h)
                for f in range(f0, f1):
                    pg.evaluate(f"window.renderAt({f / a.fps})")
                    pg.screenshot(path=f"{tmp}/ov_{lang}/{f - f0:05d}.png", omit_background=True)
                b.close()
                out = os.path.join(a.out, f"chunk_{lang}_{f0:06d}.mp4")
                subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-framerate", str(a.fps), "-i", f"{tmp}/scene/%05d.jpg",
                                "-framerate", str(a.fps), "-i", f"{tmp}/ov_{lang}/%05d.png", "-filter_complex", "[0][1]overlay,format=yuv420p",
                                "-c:v", "libx264", "-preset", "veryfast", "-crf", a.crf, "-g", str(a.fps * 2), "-r", str(a.fps), out], check=True)
                print("wrote", out, flush=True)
                shutil.rmtree(f"{tmp}/ov_{lang}")
            shutil.rmtree(tmp)


if __name__ == "__main__":
    main()
