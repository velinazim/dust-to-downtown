"""Cycles render of the real-buildings timelapse (buildings rise in their appear order, camera orbits).

  python3 tools/realcity/render.py <scenedir> <outdir> [--start 0 --step 1 --frames 900 --samples 20 --res 100]
"""
import argparse, json, math, os, time
import numpy as np
import bpy
from mathutils import Vector


def lin(c):
    c = np.asarray(c, np.float64)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def smooth(t):
    t = np.clip(t, 0, 1)
    return t * t * (3 - 2 * t)


def build(sd, args):
    z = np.load(os.path.join(sd, 'scene.npz'))
    meta = json.load(open(os.path.join(sd, 'meta.json')))
    ring, off, h = z['ring'].astype(np.float64), z['off'], z['h'].astype(np.float64)
    nb = len(h)
    k = np.diff(off)
    nv = int(2 * k.sum())
    verts = np.zeros((nv, 3)); bidx = np.zeros(nv, np.int64); top = np.zeros(nv, bool)
    faces, fcol_is_roof, fb = [], [], []
    v = 0
    for i in range(nb):
        r = ring[off[i]:off[i + 1]]; n = len(r)
        verts[v:v + n, :2] = r; verts[v + n:v + 2 * n, :2] = r; verts[v + n:v + 2 * n, 2] = h[i]
        bidx[v:v + 2 * n] = i; top[v + n:v + 2 * n] = True
        for j in range(n):
            a, b = v + j, v + (j + 1) % n
            faces.append((a, b, b + n, a + n)); fcol_is_roof.append(False); fb.append(i)
        faces.append(tuple(range(v + n, v + 2 * n))); fcol_is_roof.append(True); fb.append(i)
        v += 2 * n
    me = bpy.data.meshes.new('city')
    me.from_pydata(verts.tolist(), [], faces)
    me.update()
    fb = np.array(fb); roofm = np.array(fcol_is_roof)
    cols = np.where(roofm[:, None], z['roof'][fb], z['wall'][fb])
    cols = np.concatenate([lin(cols), np.ones((len(cols), 1))], 1).astype(np.float32)
    at = me.color_attributes.new('col', 'FLOAT_COLOR', 'FACE')
    at.data.foreach_set('color', cols.ravel())
    ob = bpy.data.objects.new('city', me); bpy.context.scene.collection.objects.link(ob)
    m = bpy.data.materials.new('bld'); m.use_nodes = True
    nt = m.node_tree; bs = nt.nodes['Principled BSDF']
    an = nt.nodes.new('ShaderNodeAttribute'); an.attribute_name = 'col'; an.attribute_type = 'GEOMETRY'
    nt.links.new(an.outputs['Color'], bs.inputs['Base Color'])
    bs.inputs['Roughness'].default_value = 0.82
    me.materials.append(m)
    print('scene built:', nb, 'buildings', nv, 'verts', len(faces), 'faces', flush=True)
    return me, verts[:, 2].copy(), bidx, z['appear'].astype(np.float64), meta


def ground(sd, meta):
    G = meta['ground_half_m']
    bpy.ops.mesh.primitive_plane_add(size=2 * G, location=(0, 0, -0.15))
    gp = bpy.context.active_object
    m = bpy.data.materials.new('ground'); m.use_nodes = True
    nt = m.node_tree; bs = nt.nodes['Principled BSDF']
    tx = nt.nodes.new('ShaderNodeTexImage'); tx.image = bpy.data.images.load(os.path.abspath(os.path.join(sd, 'ground.png')))
    tx.interpolation = 'Cubic'
    wm = nt.nodes.new('ShaderNodeTexImage'); wm.image = bpy.data.images.load(os.path.abspath(os.path.join(sd, 'water.png')))
    wm.image.colorspace_settings.name = 'Non-Color'
    nt.links.new(tx.outputs['Color'], bs.inputs['Base Color'])
    mr = nt.nodes.new('ShaderNodeMapRange')
    mr.inputs['To Min'].default_value = 0.95; mr.inputs['To Max'].default_value = 0.12
    nt.links.new(wm.outputs['Color'], mr.inputs['Value'])
    nt.links.new(mr.outputs['Result'], bs.inputs['Roughness'])
    gp.data.materials.append(m)
    # far surround so the frame edge never shows empty space
    bpy.ops.mesh.primitive_plane_add(size=80000, location=(0, 0, -0.6))
    far = bpy.context.active_object
    fm = bpy.data.materials.new('far'); fm.use_nodes = True
    fm.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (*lin([214 / 255, 204 / 255, 182 / 255]), 1)
    fm.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.95
    far.data.materials.append(fm)


def setup(args):
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.cycles.samples = args.samples
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 4
    sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
    sc.render.resolution_percentage = args.res
    sc.render.image_settings.file_format = 'PNG'
    sc.render.film_transparent = False
    try:
        sc.view_settings.view_transform = 'AgX'; sc.view_settings.look = 'AgX - Medium High Contrast'
    except Exception:  # noqa: BLE001
        pass
    w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
    bg = w.node_tree.nodes['Background']
    bg.inputs['Color'].default_value = (0.42, 0.58, 0.82, 1); bg.inputs['Strength'].default_value = 0.85
    sun = bpy.data.lights.new('sun', 'SUN'); sun.energy = 4.2; sun.angle = math.radians(1.2); sun.color = (1.0, 0.94, 0.86)
    so = bpy.data.objects.new('sun', sun); sc.collection.objects.link(so)
    so.rotation_euler = (math.radians(52), 0, math.radians(-38))
    cam = bpy.data.cameras.new('cam'); cam.lens = 32; cam.clip_start = 5; cam.clip_end = 60000
    co = bpy.data.objects.new('cam', cam); sc.collection.objects.link(co); sc.camera = co
    return co


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('sd'); ap.add_argument('out')
    ap.add_argument('--start', type=int, default=0); ap.add_argument('--step', type=int, default=1)
    ap.add_argument('--frames', type=int, default=900); ap.add_argument('--only', type=str, default='')
    ap.add_argument('--samples', type=int, default=20); ap.add_argument('--res', type=int, default=100)
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    co = setup(args)
    me, z0, bidx, appear, meta = build(args.sd, args)
    ground(args.sd, meta)
    camc = meta.get('camera', {})
    tx, ty = camc.get('target', [0, 0])
    N = args.frames
    g0, g1 = int(N * 0.05), int(N * 0.86)
    rise = 0.035
    frames = [int(f) for f in args.only.split(',')] if args.only else list(range(args.start, N, args.step))
    for f in frames:
        t0 = time.time()
        tg = (f - g0) / max(g1 - g0, 1)
        fac = smooth((tg - appear * (1 - rise)) / rise)[bidx]
        z = np.where(fac > 0.002, z0 * fac, -3.0)
        me.vertices.foreach_set('co', _co(me, z))
        me.update()
        u = smooth(f / max(N - 1, 1))
        az = math.radians(camc.get('az0', 200) + (camc.get('az1', 250) - camc.get('az0', 200)) * u)
        el = math.radians(camc.get('el0', 42) + (camc.get('el1', 34) - camc.get('el0', 42)) * u)
        R = camc.get('r0', 3400) + (camc.get('r1', 2600) - camc.get('r0', 3400)) * u
        tgt = Vector((tx, ty, 0))
        co.location = tgt + Vector((R * math.cos(el) * math.cos(az), R * math.cos(el) * math.sin(az), R * math.sin(el)))
        co.rotation_euler = (tgt - co.location).to_track_quat('-Z', 'Y').to_euler()
        bpy.context.scene.render.filepath = os.path.join(os.path.abspath(args.out), 'f_%04d.png' % f)
        bpy.ops.render.render(write_still=True)
        print('frame', f, '%.1fs' % (time.time() - t0), flush=True)


_XY = None


def _co(me, z):
    global _XY
    if _XY is None:
        a = np.zeros(len(me.vertices) * 3); me.vertices.foreach_get('co', a); _XY = a.reshape(-1, 3)[:, :2].copy()
    return np.column_stack([_XY, z]).ravel()


if __name__ == '__main__':
    main()
