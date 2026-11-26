"""Blender (Cycles) renderer for an exported engine scene — pilot.

  python3 tools/blender/render_blender.py <exportdir> <outdir> [--start 0 --end -1 --step 1]
        [--samples 32] [--scale 100] [--dof 1] [--save-blend file.blend]

<exportdir> comes from tools/blender/export_scene.py. Frames are written as <outdir>/f_<frame>.png, frame numbers
are episode frames (f0..f1 of the export), so several machines can render disjoint ranges.
The scene is the engine's own scene (same buildings, timings, camera); Blender only changes how it is lit and
shaded: physical sun + sky, soft shadows, bounce light, bevelled edges, glossy water, depth of field.
Needs the pip package bpy (Blender as a Python module, same version as requirements below).
"""
import argparse, json, math, os, sys, time
import numpy as np
import bpy, bmesh
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import heroes
from mathutils import Vector

# ------------------------------------------------------------------ helpers
def sstep(a, b, v):
    t = np.clip((v - a) / np.where(b == a, 1e-9, b - a), 0, 1)
    return t * t * (3 - 2 * t)


def s1(a, b, v):
    if b == a:
        return 1.0 if v >= b else 0.0
    t = min(1.0, max(0.0, (v - a) / (b - a)))
    return t * t * (3 - 2 * t)


def srgb2lin(c):
    c = np.asarray(c, dtype=np.float64)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def hexcol(h):
    h = h.lstrip('#')
    return [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]


def lin_rgba(hexes):
    rgb = srgb2lin(np.array([hexcol(h) for h in hexes]))
    return np.concatenate([rgb, np.ones((len(hexes), 1))], axis=1)


def conv(p):  # engine (x, y up, z) -> Blender (x, y, z up)
    return Vector((p[0], -p[2], p[1]))


def node(nt, kind, **kw):
    n = nt.nodes.new(kind)
    for k, v in kw.items():
        if k in n.inputs:
            n.inputs[k].default_value = v
        else:
            setattr(n, k, v)
    return n


def principled(name, color_attr=None, color=(0.8, 0.8, 0.8, 1), rough=0.85, bevel=0.0, bump=None, spec=0.3):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes['Principled BSDF']
    bsdf.inputs['Roughness'].default_value = rough
    bsdf.inputs['Specular IOR Level'].default_value = spec
    if color_attr:
        a = node(nt, 'ShaderNodeAttribute', attribute_name=color_attr)
        nt.links.new(a.outputs['Color'], bsdf.inputs['Base Color'])
    else:
        bsdf.inputs['Base Color'].default_value = color
    nrm = None
    if bevel > 0:
        bv = node(nt, 'ShaderNodeBevel', samples=4)
        bv.inputs['Radius'].default_value = bevel
        nrm = bv
    if bump:
        nz = node(nt, 'ShaderNodeTexNoise')
        nz.inputs['Scale'].default_value = bump[0]
        nz.inputs['Detail'].default_value = 6
        bp = node(nt, 'ShaderNodeBump')
        bp.inputs['Strength'].default_value = bump[1]
        bp.inputs['Distance'].default_value = bump[2]
        nt.links.new(nz.outputs['Fac'], bp.inputs['Height'])
        if nrm:
            nt.links.new(nrm.outputs['Normal'], bp.inputs['Normal'])
        nrm = bp
    if nrm:
        nt.links.new(nrm.outputs['Normal'], bsdf.inputs['Normal'])
    return m


# ------------------------------------------------------------------ instanced "batches" with per-frame vertex update
class Batch:
    """N copies of a small template mesh in one Blender mesh; each frame every copy gets a scale/yaw/position."""

    def __init__(self, name, tv, tf, colors, mat, smooth=False):
        n = len(colors)
        self.tv = np.asarray(tv, dtype=np.float64)  # template verts in engine axes (x, y up, z)
        nv = len(self.tv)
        verts = np.zeros((n * nv, 3))
        faces = [[i * nv + j for j in f] for i in range(n) for f in tf]
        me = bpy.data.meshes.new(name)
        me.from_pydata(verts.tolist(), [], faces)
        me.update()
        ca = me.color_attributes.new('col', 'FLOAT_COLOR', 'POINT')
        ca.data.foreach_set('color', np.repeat(colors, nv, axis=0).ravel().astype(np.float32))
        me.materials.append(mat)
        if smooth:
            me.polygons.foreach_set('use_smooth', np.ones(len(me.polygons), dtype=bool))
        self.ob = bpy.data.objects.new(name, me)
        bpy.context.scene.collection.objects.link(self.ob)
        self.me, self.n, self.nv = me, n, nv

    def set(self, pos, scale, yaw):
        """pos (n,3), scale (n,3), yaw (n,) all in engine axes; scale 0 hides a copy."""
        v = self.tv[None, :, :] * scale[:, None, :]
        c, s = np.cos(yaw)[:, None], np.sin(yaw)[:, None]
        x = v[..., 0] * c + v[..., 2] * s
        z = -v[..., 0] * s + v[..., 2] * c
        y = v[..., 1]
        X = x + pos[:, 0:1]; Y = y + pos[:, 1:2]; Z = z + pos[:, 2:3]
        out = np.stack([X, -Z, Y], axis=-1).reshape(-1, 3).astype(np.float32)
        self.me.vertices.foreach_set('co', out.ravel())
        self.me.update()


BOX_V = [[-.5, 0, -.5], [.5, 0, -.5], [.5, 0, .5], [-.5, 0, .5], [-.5, 1, -.5], [.5, 1, -.5], [.5, 1, .5], [-.5, 1, .5]]
BOX_F = [[0, 3, 2, 1], [4, 5, 6, 7], [0, 1, 5, 4], [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]
HIP_V = [[-.53, 0, -.53], [.53, 0, -.53], [.53, 0, .53], [-.53, 0, .53], [0, 1, 0]]
HIP_F = [[0, 3, 2, 1], [0, 1, 4], [1, 2, 4], [2, 3, 4], [3, 0, 4]]
GAB_V = [[-.5, 0, -.5], [.5, 0, -.5], [0, 1, -.5], [-.5, 0, .5], [.5, 0, .5], [0, 1, .5]]
GAB_F = [[0, 2, 1], [3, 4, 5], [0, 3, 5, 2], [1, 2, 5, 4], [0, 1, 4, 3]]


def ico():
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=1, radius=1.0)
    v = [[p.co.x, p.co.z, -p.co.y] for p in bm.verts]  # to engine axes
    f = [[x.index for x in fa.verts] for fa in bm.faces]
    bm.free()
    return v, f


def cone(seg=7, r=1.0, h=1.3):
    v = [[r * math.sin(2 * math.pi * i / seg), 0, r * math.cos(2 * math.pi * i / seg)] for i in range(seg)] + [[0, h, 0]]
    f = [list(range(seg))[::-1]] + [[i, (i + 1) % seg, seg] for i in range(seg)]
    return v, f


# ------------------------------------------------------------------ scene
def build(ex, a):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    D = json.load(open(os.path.join(ex, 'data.json')))
    bpy.ops.import_scene.gltf(filepath=os.path.join(ex, 'scene.glb'))

    # terrain + water from the engine (exact geometry), new materials
    m_ter = None
    for ob in list(bpy.data.objects):
        if ob.type != 'MESH':
            continue
        nm = ob.name.split('.')[0]
        par = ob.parent.name if ob.parent else ''
        if nm.startswith('terrain_') or par.startswith('terrain_'):
            me = ob.data
            if me.color_attributes:
                me.color_attributes[0].name = 'tcol'
            if m_ter is None:
                m_ter = principled('terrain', color_attr='tcol', rough=0.95, bump=(900.0, 0.25, 0.0006), spec=0.15)
            me.materials.clear(); me.materials.append(m_ter)
            me.polygons.foreach_set('use_smooth', np.ones(len(me.polygons), dtype=bool))
        elif nm == 'water' or par == 'water':
            m = principled('water', color=(0.035, 0.16, 0.21, 1), rough=0.06, spec=0.5)
            b = m.node_tree.nodes['Principled BSDF']
            b.inputs['Alpha'].default_value = 0.82
            wv = node(m.node_tree, 'ShaderNodeTexNoise')
            wv.inputs['Scale'].default_value = 1500.0
            bp = node(m.node_tree, 'ShaderNodeBump')
            bp.inputs['Strength'].default_value = 0.08
            bp.inputs['Distance'].default_value = 0.0002
            m.node_tree.links.new(wv.outputs['Fac'], bp.inputs['Height'])
            m.node_tree.links.new(bp.outputs['Normal'], b.inputs['Normal'])
            ob.data.materials.clear(); ob.data.materials.append(m)
        else:  # landmark / bridge parts: keep engine colours, nicer surface
            for slot in ob.material_slots:
                mt = slot.material
                if mt and mt.use_nodes and not mt.get('_bx'):
                    bs = mt.node_tree.nodes.get('Principled BSDF')
                    if bs:
                        bs.inputs['Roughness'].default_value = 0.8
                        bv = node(mt.node_tree, 'ShaderNodeBevel', samples=4)
                        bv.inputs['Radius'].default_value = 0.0006
                        mt.node_tree.links.new(bv.outputs['Normal'], bs.inputs['Normal'])
                    mt['_bx'] = 1

    # animated groups (landmarks, bridges)
    anims = []; flats = []
    for an in D['anim']:
        ob = bpy.data.objects.get(an['name'])
        if ob is None:
            continue
        anims.append((ob, an))
        if a.hero and an.get('type') in heroes.BUILDERS:
            for c in list(ob.children_recursive):
                bpy.data.objects.remove(c, do_unlink=True)
            hero = heroes.BUILDERS[an['type']](an.get('size_m'), an.get('colors'))
            hero.parent = ob
            flats.append((ob, an))

    # a hero needs a level site: press the terrain inside its footprint down to the landmark's base
    if flats:
        bpy.context.view_layer.update()
        for tob in [o for o in bpy.data.objects if o.type == 'MESH' and (o.name.startswith('terrain_') or (o.parent and o.parent.name.startswith('terrain_')))]:
            me = tob.data; co = np.zeros(len(me.vertices) * 3); me.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
            Mw = np.array(tob.matrix_world); wco = co @ Mw[:3, :3].T + Mw[:3, 3]
            changed = False
            for ob, an in flats:
                Mi = np.array(ob.matrix_world.inverted()); lc = wco @ Mi[:3, :3].T + Mi[:3, 3]
                sw, sd = (an.get('size_m') or [190, 156])[:2]
                r = (lc[:, 0] / (sw / 2 * 0.001 + 0.03)) ** 2 + (lc[:, 1] / (sd / 2 * 0.001 + 0.03)) ** 2
                m = r < 1.0
                if m.any():
                    wco[m, 2] = np.minimum(wco[m, 2], ob.matrix_world.translation.z - 0.0015); changed = True
            if changed:
                Mi = np.array(tob.matrix_world.inverted()); co = wco @ Mi[:3, :3].T + Mi[:3, 3]
                me.vertices.foreach_set('co', co.ravel().astype(np.float32)); me.update()

    # buildings
    Bd = D['buildings']
    B = np.array([b[:11] for b in Bd], dtype=np.float64)
    wc = lin_rgba([b[11] for b in Bd]); rc = lin_rgba([b[12] for b in Bd]); chim = np.array([b[13] for b in Bd], bool)
    m_b = principled('buildings', color_attr='col', rough=0.82, bevel=0.0007, spec=0.25)
    roof = B[:, 10].astype(int)
    S = {'B': B, 'chim': chim, 'roof': roof}
    S['body'] = Batch('bodies', BOX_V, BOX_F, wc, m_b)
    S['hip'] = (np.where(roof == 0)[0], None); S['gab'] = (np.where(roof == 1)[0], None); S['flat'] = (np.where(roof == 2)[0], None)
    for key, tv, tf in (('hip', HIP_V, HIP_F), ('gab', GAB_V, GAB_F), ('flat', BOX_V, BOX_F)):
        idx = S[key][0]
        S[key] = (idx, Batch('roof_' + key, tv, tf, rc[idx], m_b) if len(idx) else None)
        S[key + '_ix'] = idx
    ci = np.where(chim)[0]
    S['chimb'] = (ci, Batch('chimneys', BOX_V, BOX_F, lin_rgba(['#5a3a30'] * len(ci)), m_b) if len(ci) else None)

    # trees
    T = np.array(D['trees'], dtype=np.float64).reshape(-1, 5)
    iv, iff = ico()
    tcols = lin_rgba(['#3f5a2c', '#4b6633', '#56703a', '#3a5230'])
    m_t = principled('trees', color_attr='col', rough=0.9, spec=0.1)
    S['T'] = T
    S['trees'] = Batch('trees', iv, iff, tcols[np.arange(len(T)) % 4], m_t, smooth=True) if len(T) else None

    # wall / road / chain pieces
    P = np.array([p[:9] + [p[10]] for p in D['pieces']], dtype=np.float64).reshape(-1, 10)
    S['P'] = P
    m_p = principled('pieces', color_attr='col', rough=0.88, bevel=0.0005, spec=0.2)
    S['pieces'] = Batch('pieces', BOX_V, BOX_F, lin_rgba([p[9] for p in D['pieces']]), m_p) if len(P) else None

    # tents
    TN = np.array(D['tents'], dtype=np.float64).reshape(-1, 7)
    S['TN'] = TN
    if len(TN):
        cv, cf = cone()
        S['tents'] = Batch('tents', cv, cf, lin_rgba(['#b23a2e' if t[6] else '#f1ece0' for t in TN]), principled('tents', color_attr='col', rough=0.9))
    else:
        S['tents'] = None

    # smoke: camera-facing quads with a soft round alpha
    PF = D['puffs']
    S['PF'] = np.array([p[:10] for p in PF], dtype=np.float64).reshape(-1, 10)
    if len(PF):
        n = len(PF)
        me = bpy.data.meshes.new('smoke')
        me.from_pydata(np.zeros((n * 4, 3)).tolist(), [], [[i * 4, i * 4 + 1, i * 4 + 2, i * 4 + 3] for i in range(n)])
        uv = me.uv_layers.new(name='UVMap')
        uv.data.foreach_set('uv', np.tile([0, 0, 1, 0, 1, 1, 0, 1], n).astype(np.float32))
        ca = me.color_attributes.new('col', 'FLOAT_COLOR', 'POINT')
        ca.data.foreach_set('color', np.repeat(lin_rgba(['#' + p[10] for p in PF]), 4, axis=0).ravel().astype(np.float32))
        al = me.attributes.new('op', 'FLOAT', 'POINT')
        m = bpy.data.materials.new('smoke'); m.use_nodes = True; nt = m.node_tree
        nt.nodes.remove(nt.nodes['Principled BSDF'])
        out = nt.nodes['Material Output']
        ac = node(nt, 'ShaderNodeAttribute', attribute_name='col')
        ao = node(nt, 'ShaderNodeAttribute', attribute_name='op')
        tc = node(nt, 'ShaderNodeTexCoord')
        vs = node(nt, 'ShaderNodeVectorMath', operation='DISTANCE'); vs.inputs[1].default_value = (0.5, 0.5, 0.0)
        nt.links.new(tc.outputs['UV'], vs.inputs[0])
        rad = node(nt, 'ShaderNodeMapRange'); rad.inputs['From Min'].default_value = 0.5; rad.inputs['From Max'].default_value = 0.0
        nt.links.new(vs.outputs['Value'], rad.inputs['Value'])
        pw = node(nt, 'ShaderNodeMath', operation='POWER'); pw.inputs[1].default_value = 1.6
        nt.links.new(rad.outputs['Result'], pw.inputs[0])
        mul = node(nt, 'ShaderNodeMath', operation='MULTIPLY')
        nt.links.new(pw.outputs[0], mul.inputs[0]); nt.links.new(ao.outputs['Fac'], mul.inputs[1])
        tr = node(nt, 'ShaderNodeBsdfTransparent')
        df = node(nt, 'ShaderNodeBsdfTranslucent')
        dd = node(nt, 'ShaderNodeBsdfDiffuse')
        mx0 = node(nt, 'ShaderNodeMixShader'); mx0.inputs['Fac'].default_value = 0.45
        nt.links.new(ac.outputs['Color'], df.inputs['Color']); nt.links.new(ac.outputs['Color'], dd.inputs['Color'])
        nt.links.new(dd.outputs[0], mx0.inputs[1]); nt.links.new(df.outputs[0], mx0.inputs[2])
        mx = node(nt, 'ShaderNodeMixShader')
        nt.links.new(mul.outputs[0], mx.inputs['Fac']); nt.links.new(tr.outputs[0], mx.inputs[1]); nt.links.new(mx0.outputs[0], mx.inputs[2])
        nt.links.new(mx.outputs[0], out.inputs['Surface'])
        me.materials.append(m)
        ob = bpy.data.objects.new('smoke', me); sc.collection.objects.link(ob)
        ob.visible_shadow = False
        S['smoke'] = me
    else:
        S['smoke'] = None

    # camera, sun, sky
    cam = bpy.data.cameras.new('cam'); cam.sensor_fit = 'VERTICAL'
    S['cam'] = bpy.data.objects.new('cam', cam); sc.collection.objects.link(S['cam']); sc.camera = S['cam']
    sl = bpy.data.lights.new('sun', 'SUN'); sl.energy = a.sunE; sl.angle = math.radians(1.8); sl.color = (1.0, 0.95, 0.86)
    S['sun'] = bpy.data.objects.new('sun', sl); sc.collection.objects.link(S['sun'])
    w = bpy.data.worlds.new('world'); w.use_nodes = True; sc.world = w
    nt = w.node_tree; bg = nt.nodes['Background']
    sky = node(nt, 'ShaderNodeTexSky', sky_type='MULTIPLE_SCATTERING')
    try:
        sky.sun_disc = False
    except Exception:
        pass
    nt.links.new(sky.outputs['Color'], bg.inputs['Color']); bg.inputs['Strength'].default_value = a.sky
    S['sky'] = sky

    # render settings
    sc.render.engine = 'CYCLES'
    cy = sc.cycles
    cy.device = 'CPU'; cy.samples = a.samples; cy.use_adaptive_sampling = True; cy.adaptive_threshold = 0.04
    cy.use_denoising = True
    try:
        cy.denoiser = 'OPENIMAGEDENOISE'
    except Exception:
        pass
    cy.max_bounces = 4; cy.diffuse_bounces = 2; cy.glossy_bounces = 2; cy.transmission_bounces = 2; cy.transparent_max_bounces = 128
    cy.caustics_reflective = False; cy.caustics_refractive = False
    cy.blur_glossy = 1.0
    sc.render.resolution_x = D['w']; sc.render.resolution_y = D['h']; sc.render.resolution_percentage = a.scale
    sc.render.image_settings.file_format = 'PNG'
    sc.render.use_persistent_data = False
    sc.view_settings.view_transform = a.view
    if a.look:
        sc.view_settings.look = a.look
    sc.view_settings.exposure = a.exposure
    S['anims'] = anims
    S['D'] = D
    return S


def frame(S, f, a):
    D = S['D']; fps = D['fps']; t = f / fps
    C = json.load(open(os.path.join(a.export, 'cams.json')))[f - D['f0']] if 'C' not in S else S['C'][f - D['f0']]
    t = C['ep']
    B = S['B']
    k = sstep(B[:, 8], B[:, 8] + 0.55, t) * (1 - sstep(B[:, 9], B[:, 9] + 0.5, t))
    k = np.where(k <= 0.001, 0.0, k)
    sc_ = np.where(k > 0, 0.55 + 0.45 * k, 0.0)
    pos = B[:, 0:3]; yaw = B[:, 7]
    S['body'].set(pos, np.stack([B[:, 3] * sc_, B[:, 5] * k, B[:, 4] * sc_], 1), yaw)
    top = pos.copy(); top[:, 1] = B[:, 1] + B[:, 5] * k
    for key, mx in (('hip', 1.02), ('gab', 1.04), ('flat', 0.9)):
        idx, bt = S[key]
        if bt is None:
            continue
        hh = B[idx, 6] * k[idx] if key != 'flat' else 0.0025 * k[idx]
        bt.set(top[idx], np.stack([B[idx, 3] * sc_[idx] * mx, hh, B[idx, 4] * sc_[idx] * mx], 1), yaw[idx])
    ci, bt = S['chimb']
    if bt is not None:
        p = pos[ci].copy(); p[:, 0] += B[ci, 3] * 0.3
        kk = k[ci]; on = (kk > 0).astype(float)
        bt.set(p, np.stack([0.006 * on, (B[ci, 5] + 0.03) * kk, 0.006 * on], 1), np.zeros(len(ci)))
    if S['trees'] is not None:
        T = S['T']; kt = 1 - sstep(T[:, 4], T[:, 4] + 0.5, t)
        S['trees'].set(T[:, 0:3], np.stack([T[:, 3] * kt, T[:, 3] * 1.25 * kt, T[:, 3] * kt], 1), np.zeros(len(T)))
    if S['pieces'] is not None:
        P = S['P']; kp = sstep(P[:, 7], P[:, 7] + 0.3, t) * (1 - sstep(P[:, 8], P[:, 8] + 0.7, t))
        on = (kp > 0).astype(float); fl = P[:, 9] > 0
        sy = np.where(fl, P[:, 5], P[:, 5] * kp) * on; sz = np.where(fl, P[:, 6] * kp, P[:, 6]) * on
        S['pieces'].set(P[:, 0:3], np.stack([P[:, 4] * on, sy, sz], 1), P[:, 3])
    if S['tents'] is not None:
        TN = S['TN']; kn = sstep(TN[:, 4], TN[:, 4] + 0.4, t) * (1 - sstep(TN[:, 5], TN[:, 5] + 0.6, t))
        S['tents'].set(TN[:, 0:3], np.stack([TN[:, 3] * kn] * 3, 1), np.zeros(len(TN)))
    for ob, an in S['anims']:
        kk = s1(an['a'], an['b'], t) * (1 - s1(an['va'], an['vb'], t))
        hid = kk <= 0.002
        for o in [ob] + list(ob.children_recursive):
            o.hide_render = hid
        Bs = an['base']
        ob.scale = (Bs, Bs, Bs * max(kk, 0.001)) if an['mode'] == 'rise' else (Bs * max(kk, 0.001),) * 3

    # camera
    cp, ct = conv(C['p']), conv(C['t'])
    cam = S['cam']; cam.location = cp
    cam.rotation_mode = 'QUATERNION'; cam.rotation_quaternion = (ct - cp).to_track_quat('-Z', 'Y')
    cam.data.sensor_height = 24.0; cam.data.lens = 12.0 / math.tan(math.radians(C['fov']) / 2); cam.data.clip_start = C['near']; cam.data.clip_end = C['far']
    cam.data.dof.use_dof = bool(a.dof)
    cam.data.dof.focus_distance = (ct - cp).length
    cam.data.dof.aperture_fstop = a.fstop
    # sun from the engine's sun position
    sv = conv(C['sun']).normalized()
    S['sun'].rotation_mode = 'QUATERNION'; S['sun'].rotation_quaternion = (-sv).to_track_quat('-Z', 'Y')
    sky = S['sky']
    try:
        sky.sun_elevation = math.asin(max(0.05, sv.z)); sky.sun_rotation = math.atan2(sv.y, sv.x) - math.pi / 2
    except Exception:
        pass

    # smoke billboards
    if S['smoke'] is not None:
        PF = S['PF']
        on = sstep(PF[:, 3], PF[:, 3] + 1.0, t) * (1 - sstep(PF[:, 4] - 1.0, PF[:, 4], t))
        gun = PF[:, 8] > 0
        ph = np.mod(t * np.where(gun, 0.75, 0.32) + PF[:, 6], 1.0)
        scl = PF[:, 5]
        x = PF[:, 0] + np.where(gun, ph * 0.12 * scl + (PF[:, 7] - 0.5) * 0.02, ph * 0.3 * scl + (PF[:, 7] - 0.5) * 0.04)
        y = PF[:, 2] + np.where(gun, ph * 0.18 * scl, ph * 0.6 * scl)
        z = PF[:, 1] - np.where(gun, ph * 0.05, ph * 0.08)
        size = (0.08 + ph * 0.42) * scl
        op = on * 0.8 * np.sin(np.pi * np.minimum(1, ph * 1.15))
        size = np.where(on > 0.001, size, 0.0)
        ctr = np.stack([x, -z, y], 1)
        q = cam.rotation_quaternion
        r = np.array(q @ Vector((1, 0, 0))); u = np.array(q @ Vector((0, 1, 0)))
        hs = (size / 2)[:, None]
        corners = np.stack([ctr - r * hs - u * hs, ctr + r * hs - u * hs, ctr + r * hs + u * hs, ctr - r * hs + u * hs], 1)
        me = S['smoke']
        me.vertices.foreach_set('co', corners.reshape(-1).astype(np.float32))
        me.attributes['op'].data.foreach_set('value', np.repeat(op, 4).astype(np.float32))
        me.update()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('export'); ap.add_argument('out')
    ap.add_argument('--start', type=int, default=0); ap.add_argument('--end', type=int, default=-1); ap.add_argument('--step', type=int, default=1)
    ap.add_argument('--frames', default='', help='comma list of window frame indices (overrides start/end)')
    ap.add_argument('--samples', type=int, default=32); ap.add_argument('--scale', type=int, default=100)
    ap.add_argument('--dof', type=int, default=1); ap.add_argument('--fstop', type=float, default=0.6)
    ap.add_argument('--view', default='Standard'); ap.add_argument('--look', default='')
    ap.add_argument('--sky', type=float, default=0.07); ap.add_argument('--sunE', type=float, default=4.0); ap.add_argument('--exposure', type=float, default=-0.25)
    ap.add_argument('--threads', type=int, default=0); ap.add_argument('--hero', type=int, default=1); ap.add_argument('--save-blend', default='')
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    t0 = time.time()
    S = build(a.export, a)
    S['C'] = json.load(open(os.path.join(a.export, 'cams.json')))
    sc = bpy.context.scene
    if a.threads:
        sc.render.threads_mode = 'FIXED'; sc.render.threads = a.threads
    n = len(S['C'])
    idx = [int(x) for x in a.frames.split(',')] if a.frames else list(range(a.start, n if a.end < 0 else min(n, a.end), a.step))
    print(f'scene built in {time.time() - t0:.1f}s; rendering {len(idx)} frames', flush=True)
    for i in idx:
        f = S['D']['f0'] + i
        t1 = time.time()
        frame(S, f, a)
        if a.save_blend and i == idx[0]:
            bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath(a.save_blend))
        sc.render.filepath = os.path.join(os.path.abspath(a.out), f'f_{f:06d}.png')
        bpy.ops.render.render(write_still=True)
        print(f'frame {f} ({i}) {time.time() - t1:.1f}s', flush=True)


if __name__ == '__main__':
    main()
