"""Export one episode's 3D scene from the web engine for the Blender renderer (pilot).

  python3 tools/blender/export_scene.py <slug> <outdir> --t0 252 --t1 287 [--fps 30] [--w 1920 --h 1080]

Writes <outdir>/scene.glb (terrain, water, landmarks, bridges: exact engine geometry),
<outdir>/data.json (buildings, trees, wall/road pieces, smoke, timings) and <outdir>/cams.json
(camera + sun per frame of the window). Same coordinates as the engine (km, Y up); the Blender side
converts to Z up. Nothing in the engine changes: a patched copy of engine/index.html is served for the run.
"""
import argparse, base64, json, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "engine"))
import render as R  # engine/render.py: serve(), ROOT, ARGS
from playwright.sync_api import sync_playwright

HOOK = r"""
  window.__BX = { scene, camera, B, TR, pieces, animated, twMeshes, puffs, TENTS, sun, update, placeCamera };
  window.__bxCam = (T) => { const m = coMap(T); CAM_FORCE = m.cam; const r = placeCamera(m.ep);
    const d = r.d, tg = r.target; let sp;
    if (Q.get('mood') === 'golden') sp = [tg.x - d * 1.1, d * 0.38 + 0.6, tg.z - d * 0.15];
    else if (LOOK3) sp = [tg.x - d * 0.8, d * 0.62 + 1.5, tg.z + d * 0.2];
    else sp = [tg.x - d * 0.55, d * 0.8 + 2, tg.z + d * 0.45];
    return { ep: m.ep, p: camera.position.toArray(), t: [tg.x, tg.y, tg.z], fov: camera.fov, near: camera.near, far: camera.far, d, sun: [sp[0] - tg.x, sp[1] - tg.y, sp[2] - tg.z] }; };
"""

EXPORT_JS = r"""
async () => {
  const { GLTFExporter } = await import('three/addons/exporters/GLTFExporter.js');
  const X = window.__BX, THREE = X.scene.constructor;  // not used
  const col = c => (typeof c === 'string') ? c : '#ffffff';
  const objs = []; let ti = 0;
  for (const o of X.scene.children) {
    if (o.isInstancedMesh || o.isSprite || o.isLight) continue;
    if (o.isMesh && o.geometry.attributes.color) { o.name = 'terrain_' + (ti++); objs.push(o); }
    else if (o.isMesh && o.geometry.type === 'PlaneGeometry') { o.name = 'water'; objs.push(o); }
  }
  X.twMeshes.forEach((w, i) => { w.m.name = 'tw_' + i; w.m.visible = true; w.m.material.opacity = 0.95; objs.push(w.m); });
  const anim = X.animated.map((an, i) => { an.obj.name = 'anim_' + i; an.obj.visible = true; an.obj.scale.set(1, 1, 1);
    an.obj.traverse(c => { c.visible = true; c.scale.x = c.scale.x || 1; });
    objs.push(an.obj); return { name: an.obj.name, a: an.a, b: an.b, va: an.va, vb: an.vb, mode: an.mode, base: an.base,
      pos: an.obj.position.toArray(), roty: an.obj.rotation.y }; });
  // nested additions (minarets) are animated children: keep them at full size in the export
  const glb = await new GLTFExporter().parseAsync(objs, { binary: true, onlyVisible: false });
  const u8 = new Uint8Array(glb); let s = ''; for (let i = 0; i < u8.length; i += 0x8000) s += String.fromCharCode.apply(null, u8.subarray(i, i + 0x8000));
  const B = X.B.map(b => [b.x, b.y, b.z, b.w, b.d, b.h, b.rh, b.yaw, b.a, Math.min(b.v, 1e7), ({ hip: 0, gable: 1, flat: 2 })[b.st.roof] ?? 0, b.wc, b.rc, b.chim ? 1 : 0]);
  const TR = X.TR.map(t => [t.x, t.y, t.z, t.s, Math.min(t.v, 1e7)]);
  const PC = X.pieces.map(p => [p.x, p.y, p.z, p.yaw, p.sx, p.sy, p.sz, p.a, Math.min(p.f, 1e7), col(p.col), p.flat ? 1 : 0]);
  const PF = X.puffs.map(p => [p.x, p.z, p.py, p.a, p.b, p.scale, p.ph, p.j, p.gun ? 1 : 0, p.fire ? 1 : 0, p.s.material.color.getHexString()]);
  const TN = X.TENTS.map(t => [t.x, t.y, t.z, t.s, t.a, Math.min(t.f, 1e7), t.red ? 1 : 0]);
  return { glb: btoa(s), data: { buildings: B, trees: TR, pieces: PC, puffs: PF, tents: TN, anim,
    tw: X.twMeshes.map(w => ({ a: w.a, b: w.b })), sky: '#' + X.scene.background.getHexString(),
    fog: [X.scene.fog.near, X.scene.fog.far] } };
}
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug"); ap.add_argument("out")
    ap.add_argument("--t0", type=float, required=True); ap.add_argument("--t1", type=float, required=True)
    ap.add_argument("--extra", default="", help="extra engine query, e.g. &cam=lat,lon,km&pitch=30")
    ap.add_argument("--fps", type=int, default=30); ap.add_argument("--w", type=int, default=1920); ap.add_argument("--h", type=int, default=1080)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    src = open(os.path.join(R.ROOT, "engine", "index.html"), encoding="utf-8").read()
    marker = "  window.renderAt = T =>"
    assert src.count(marker) == 1, "engine changed: hook point not found"
    patched = src.replace(marker, HOOK + marker)
    tmp = os.path.join(R.ROOT, "engine", "_bx_export.html")
    open(tmp, "w", encoding="utf-8").write(patched)
    try:
        port = R.serve()
        with sync_playwright() as p:
            b = p.chromium.launch(args=R.ARGS)
            pg = b.new_page(viewport={"width": 640, "height": 360})
            pg.on("pageerror", lambda e: print("[pageerror]", e, file=sys.stderr))
            pg.goto(f"http://127.0.0.1:{port}/engine/_bx_export.html?city={a.slug}&mode=scene&lang=en&w={a.w}&h={a.h}&sh=0{a.extra}")
            pg.wait_for_function("window.ready === true", timeout=600000)
            f0, f1 = int(round(a.t0 * a.fps)), int(round(a.t1 * a.fps))
            cams = pg.evaluate(f"(() => {{ const r = []; for (let f = {f0}; f < {f1}; f++) r.push(window.__bxCam(f / {a.fps})); return r; }})()")
            res = pg.evaluate(EXPORT_JS)
            b.close()
    finally:
        os.remove(tmp)
    open(os.path.join(a.out, "scene.glb"), "wb").write(base64.b64decode(res["glb"]))
    d = res["data"]
    city = json.load(open(os.path.join(R.ROOT, "cities", a.slug, "city.json")))
    kinds = [{"kind": "bridge"} for _ in city.get("bridges", [])]   # engine order: bridges, then landmarks (+ their additions)
    for lm in city.get("landmarks", []):
        kinds.append({"kind": "landmark", "type": lm["type"], "size_m": lm.get("size_m"), "colors": lm.get("colors", {})})
        kinds += [{"kind": "addition"} for _ in lm.get("additions", [])]
    if len(kinds) == len(d["anim"]):
        for an, k in zip(d["anim"], kinds):
            an.update(k)
    d.update({"slug": a.slug, "fps": a.fps, "f0": f0, "f1": f1, "w": a.w, "h": a.h})
    json.dump(d, open(os.path.join(a.out, "data.json"), "w"))
    json.dump(cams, open(os.path.join(a.out, "cams.json"), "w"))
    print(f"exported {a.slug}: {len(d['buildings'])} buildings, {len(d['trees'])} trees, {len(d['pieces'])} pieces, "
          f"{len(d['anim'])} animated groups, {len(d['puffs'])} smoke puffs, frames {f0}-{f1}")


if __name__ == "__main__":
    main()
