"""Detailed "hero" models for the Blender renderer, built in code (no downloaded assets).

Each builder returns a mesh object in the landmark's local frame: km units, Z up, centred, base at z = 0,
long side along X (same frame as the engine's landmark group after the glTF import).
"""
import math
import bmesh, bpy
from mathutils import Matrix, Vector

K = 0.001  # metres -> km


def _mat(name, hexc, rough=0.85, noise=0.0):
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    h = hexc.lstrip('#'); c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    b.inputs['Roughness'].default_value = rough
    if noise:
        nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 2500.0; nz.inputs['Detail'].default_value = 4
        ramp = nt.nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].color = (c[0] * (1 - noise), c[1] * (1 - noise), c[2] * (1 - noise), 1)
        ramp.color_ramp.elements[1].color = (min(1, c[0] * (1 + noise * 0.5)), min(1, c[1] * (1 + noise * 0.5)), min(1, c[2] * (1 + noise * 0.5)), 1)
        nt.links.new(nz.outputs['Fac'], ramp.inputs['Fac']); nt.links.new(ramp.outputs['Color'], b.inputs['Base Color'])
    else:
        b.inputs['Base Color'].default_value = (*c, 1)
    bv = nt.nodes.new('ShaderNodeBevel'); bv.inputs['Radius'].default_value = 0.00025; bv.samples = 4
    nt.links.new(bv.outputs['Normal'], b.inputs['Normal'])
    return m


def _box(bm, cx, cy, z0, sx, sy, sz, yaw, mi):
    m = Matrix.Translation((cx, cy, z0 + sz / 2)) @ Matrix.Rotation(yaw, 4, 'Z') @ Matrix.Diagonal((sx, sy, sz, 1))
    r = bmesh.ops.create_cube(bm, size=1.0, matrix=m)
    for v in r['verts']:
        for f in v.link_faces:
            f.material_index = mi


def _ring(bm, a0, b0, a1, b1, z0, z1, n, mi, z0in=None):
    """Elliptic band between outer (a0,b0) at height z0..z1 and inner (a1,b1); z0in = inner top height (slopes)."""
    zi = z1 if z0in is None else z0in
    vs = []
    for i in range(n):
        t = 2 * math.pi * i / n; c, s = math.cos(t), math.sin(t)
        vs.append((bm.verts.new((a0 * c, b0 * s, z0)), bm.verts.new((a0 * c, b0 * s, z1)),
                   bm.verts.new((a1 * c, b1 * s, zi)), bm.verts.new((a1 * c, b1 * s, z0))))
    for i in range(n):
        p, q = vs[i], vs[(i + 1) % n]
        for (u, w) in ((0, 1), (1, 2), (2, 3)):
            f = bm.faces.new((p[u], q[u], q[w], p[w])); f.material_index = mi


def amphitheatre(size_m=None, colors=None):
    """Colosseum-type: 80 bays, three arcaded tiers with engaged columns, attic, stepped cavea, arena."""
    w, d, h = size_m or [190, 156, 48]
    A, Bm = w / 2, d / 2
    me = bpy.data.meshes.new('hero_amph'); bm = bmesh.new()
    mats = [_mat('travertine', (colors or {}).get('wall', '#e2d6b8'), 0.8, 0.18), _mat('amph_dark', '#7c6d58', 0.95),
            _mat('amph_seats', '#d6c8a6', 0.9, 0.12), _mat('amph_sand', '#d8bd85', 1.0, 0.1)]
    for m in mats:
        me.materials.append(m)
    tiers = [h * 0.22, h * 0.245, h * 0.24]            # three arcades, then the attic
    attic = h - sum(tiers)
    n = 80; depth = 4.0
    bay = math.pi * (3 * (A + Bm) - math.sqrt((3 * A + Bm) * (A + 3 * Bm))) / n
    _ring(bm, (A + 0.5) * K, (Bm + 0.5) * K, (A - depth) * K, (Bm - depth) * K, -8 * K, 0, 160, 0)   # footing below grade
    z = 0.0
    for ti, th in enumerate(tiers):
        band = th * 0.16
        for j in range(n):
            t = 2 * math.pi * (j + 0.5) / n
            px, py = A * math.cos(t), Bm * math.sin(t)
            tx, ty = -A * math.sin(t), Bm * math.cos(t); yaw = math.atan2(ty, tx)
            nx, ny = math.cos(t) / A, math.sin(t) / Bm; nl = math.hypot(nx, ny); nx, ny = nx / nl, ny / nl
            # pier + engaged half column (proud of the wall)
            _box(bm, (px - nx * depth / 2) * K, (py - ny * depth / 2) * K, z * K, bay * 0.42 * K, depth * K, (th - band) * K, yaw, 0)
            _box(bm, (px + nx * 0.5) * K, (py + ny * 0.5) * K, z * K, 1.1 * K, 1.2 * K, (th - band) * K, yaw, 0)
            # arch top: a lintel block that leaves a round-ish opening
            _box(bm, (px - nx * depth / 2) * K, (py - ny * depth / 2) * K, (z + th - band - th * 0.12) * K, bay * K * 0.98, depth * 0.9 * K, th * 0.12 * K, yaw + 0.0, 0)
        _ring(bm, (A + 0.6) * K, (Bm + 0.6) * K, (A - depth) * K, (Bm - depth) * K, (z + th - band) * K, (z + th) * K, 160, 0)
        z += th
    # attic: solid wall with pilasters and small windows (dark slots)
    _ring(bm, A * K, Bm * K, (A - depth) * K, (Bm - depth) * K, z * K, (z + attic) * K, 160, 0)
    for j in range(0, n, 2):
        t = 2 * math.pi * (j + 0.5) / n
        px, py = A * math.cos(t), Bm * math.sin(t); yaw = math.atan2(Bm * math.cos(t), -A * math.sin(t))
        _box(bm, px * K * 1.002, py * K * 1.002, (z + attic * 0.45) * K, 1.6 * K, 0.3 * K, attic * 0.22 * K, yaw, 1)
    _ring(bm, (A + 0.8) * K, (Bm + 0.8) * K, (A - depth) * K, (Bm - depth) * K, (z + attic - 1.2) * K, (z + attic) * K, 160, 0)
    # dark inner ambulatory wall seen through the arches
    _ring(bm, (A - 9) * K, (Bm - 9) * K, (A - 11) * K, (Bm - 11) * K, -6 * K, (h - attic) * K, 160, 1)
    # cavea: 14 stepped terraces from the inner wall down to the podium
    ar_a, ar_b = 41.5, 24.0
    pod = 4.5; top = h - attic - 2
    rows = 14
    for r in range(rows):
        u0, u1 = r / rows, (r + 1) / rows
        a0 = (A - 11) - (A - 11 - ar_a - 4) * u0; b0 = (Bm - 11) - (Bm - 11 - ar_b - 4) * u0
        a1 = (A - 11) - (A - 11 - ar_a - 4) * u1; b1 = (Bm - 11) - (Bm - 11 - ar_b - 4) * u1
        zz = top - (top - pod) * u1
        _ring(bm, a0 * K, b0 * K, a1 * K, b1 * K, 0, zz * K, 120, 2 if r % 4 else 1)
    # podium wall and arena
    _ring(bm, (ar_a + 4) * K, (ar_b + 4) * K, ar_a * K, ar_b * K, 0, pod * K, 120, 0)
    c = bm.verts.new((0, 0, 0.6 * K)); ring = [bm.verts.new((ar_a * math.cos(2 * math.pi * i / 96) * K, ar_b * math.sin(2 * math.pi * i / 96) * K, 0.6 * K)) for i in range(96)]
    for i in range(96):
        f = bm.faces.new((c, ring[i], ring[(i + 1) % 96])); f.material_index = 3
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new('hero_amph', me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


BUILDERS = {'amphitheatre': amphitheatre}
