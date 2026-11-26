"""Render the engine's text overlay (titles, year, population, labels) as transparent PNGs for a frame range.

  python3 tools/blender/overlay.py <slug> <outdir> --f0 7560 --f1 8610 [--lang en] [--extra "&cam=..."]

Writes <outdir>/o_<frame>.png (episode frame numbers), to be laid over the Blender frames.
"""
import argparse, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "engine"))
import render as R
from playwright.sync_api import sync_playwright


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug"); ap.add_argument("out")
    ap.add_argument("--f0", type=int, required=True); ap.add_argument("--f1", type=int, required=True)
    ap.add_argument("--fps", type=int, default=30); ap.add_argument("--lang", default="en"); ap.add_argument("--extra", default="")
    ap.add_argument("--w", type=int, default=1920); ap.add_argument("--h", type=int, default=1080)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    port = R.serve()
    with sync_playwright() as p:
        b, pg = R.open_page(p, port, a.slug, "overlay", a.lang, a.w, a.h, a.extra)
        for f in range(a.f0, a.f1):
            pg.evaluate(f"window.renderAt({f / a.fps})")
            pg.screenshot(path=os.path.join(a.out, f"o_{f:06d}.png"), omit_background=True)
        b.close()
    print(f"overlay {a.slug} {a.lang}: {a.f1 - a.f0} frames")


if __name__ == "__main__":
    main()
