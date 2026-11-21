"""
process_mesh.py — Takht-i-Bahi Digital Twin asset pipeline (KPITB AI Challenge 2026)

1. Loads the 3Dflow photogrammetry scan (UTM 42N coordinates, ~1.1 M faces).
2. Auto-detects the Main Stupa plinth inside the Stupa Court and re-centres the
   whole scan on it (float64 maths -> no 32-bit jitter once on the GPU).
3. Decimates the scan to ~140 k faces, bakes a weathered-stone vertex colour
   (slope + cavity + noise) because the scan ships without its texture atlas.
4. Procedurally builds a 2nd-century CE Gandharan reconstruction of the Stupa
   Court (stupa, chapels with caitya arches, seated Buddhas) on the SAME origin.
5. Writes assets/ruins.glb, assets/reconstructed.glb and assets/scene_meta.json.

Axes: the scan is Z-up (x = East, y = North).  glTF is Y-up, so every mesh is
mapped (x, y, z) -> (x, z, -y): East = +X, Up = +Y, North = -Z.

Usage:
    pip install trimesh numpy scipy pillow fast_simplification
    python process_mesh.py [--input path.obj] [--faces 140000] [--literal-dims]
"""

import argparse
import json
import math
import os
import time

import numpy as np
import trimesh
from PIL import Image
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_INPUT = r"C:\Users\DELL\Desktop\Hack_Data\Scans\takht_e_bai_VR.obj"
DEFAULT_OUT = os.path.join(HERE, "assets")
_TEX_DIR = r"C:\Users\DELL\Desktop\Hack_Data\Scans\texture"
SRC_WALL_PHOTO = os.path.join(_TEX_DIR, "WhatsApp Image 2026-11-21 at 11.53.58 AM.jpeg")  # diaper masonry
SRC_ROCK_PHOTO = os.path.join(_TEX_DIR, "WhatsApp Image 2026-11-21 at 11.53.57 AM.jpeg")  # weathered bedrock

# Seed point (UTM 42N) roughly on the Main Stupa plinth; refined automatically.
SEED_UTM = (771275.1, 3797808.9)
UTM_ZONE = 42

# Fallback measurements (metres, relative to plinth centre) if detection fails.
FALLBACK = dict(hx=3.2, hy=3.3, top=1.35, court_w=-7.1, court_e=7.0,
                court_s=-6.3, court_n=10.7)

# Z-up (scan) -> Y-up (glTF)
ZUP_TO_YUP = np.array([[1, 0, 0, 0],
                       [0, 0, 1, 0],
                       [0, -1, 0, 0],
                       [0, 0, 0, 1]], dtype=np.float64)


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def to_yup(p):
    """Convert (N,3) Z-up local points to glTF Y-up."""
    p = np.asarray(p, dtype=np.float64)
    return np.stack([p[..., 0], p[..., 2], -p[..., 1]], axis=-1)


def utm_to_latlon(e, n, zone, north=True):
    """Inverse UTM (WGS84) — enough precision for display / AR anchoring."""
    a, f = 6378137.0, 1 / 298.257223563
    k0 = 0.9996
    e2 = f * (2 - f)
    ep2 = e2 / (1 - e2)
    x = e - 500000.0
    y = n if north else n - 10000000.0
    m = y / k0
    mu = m / (a * (1 - e2 / 4 - 3 * e2 ** 2 / 64 - 5 * e2 ** 3 / 256))
    e1 = (1 - math.sqrt(1 - e2)) / (1 + math.sqrt(1 - e2))
    phi1 = (mu + (3 * e1 / 2 - 27 * e1 ** 3 / 32) * math.sin(2 * mu)
            + (21 * e1 ** 2 / 16 - 55 * e1 ** 4 / 32) * math.sin(4 * mu)
            + (151 * e1 ** 3 / 96) * math.sin(6 * mu))
    n1 = a / math.sqrt(1 - e2 * math.sin(phi1) ** 2)
    t1 = math.tan(phi1) ** 2
    c1 = ep2 * math.cos(phi1) ** 2
    r1 = a * (1 - e2) / (1 - e2 * math.sin(phi1) ** 2) ** 1.5
    d = x / (n1 * k0)
    lat = phi1 - (n1 * math.tan(phi1) / r1) * (
        d ** 2 / 2 - (5 + 3 * t1 + 10 * c1 - 4 * c1 ** 2 - 9 * ep2) * d ** 4 / 24
        + (61 + 90 * t1 + 298 * c1 + 45 * t1 ** 2 - 252 * ep2 - 3 * c1 ** 2) * d ** 6 / 720)
    lon = (d - (1 + 2 * t1 + c1) * d ** 3 / 6
           + (5 - 2 * c1 + 28 * t1 - 3 * c1 ** 2 + 8 * ep2 + 24 * t1 ** 2) * d ** 5 / 120) / math.cos(phi1)
    return math.degrees(lat), (zone - 1) * 6 - 180 + 3 + math.degrees(lon)


# ----------------------------------------------------------------------------
# Phase A — scan loading & plinth detection
# ----------------------------------------------------------------------------

def load_scan(path):
    log(f"Loading {path} (this takes ~1 min for 142 MB) ...")
    t = time.time()
    m = trimesh.load(path, force="mesh", process=False, skip_materials=True)
    v = np.asarray(m.vertices, dtype=np.float64)
    f = np.asarray(m.faces, dtype=np.int64)
    log(f"  loaded {len(f):,} faces / {len(v):,} verts in {time.time() - t:.0f}s")
    return v, f


def height_grid(pts, x0, y0, nx, ny, res):
    """Max-Z height grid (NaN where empty)."""
    ij = np.floor((pts[:, :2] - (x0, y0)) / res).astype(np.int64)
    ok = (ij[:, 0] >= 0) & (ij[:, 0] < nx) & (ij[:, 1] >= 0) & (ij[:, 1] < ny)
    ij, z = ij[ok], pts[ok, 2]
    order = np.argsort(z)
    hm = np.full((ny, nx), np.nan)
    hm[ij[order, 1], ij[order, 0]] = z[order]
    return hm


def detect_plinth(v, seed, res=0.25, win=16.0):
    """Find the Main Stupa plinth + Stupa Court inner bounds near `seed` (UTM)."""
    sx, sy = seed
    sel = (np.abs(v[:, 0] - sx) < win) & (np.abs(v[:, 1] - sy) < win)
    p = v[sel]
    n = int(2 * win / res)
    x0, y0 = sx - win, sy - win
    hm = height_grid(p, x0, y0, n, n, res)

    # floor = dominant height level in the central area
    c = hm[n // 4: 3 * n // 4, n // 4: 3 * n // 4]
    vals = c[np.isfinite(c)]
    hist, edges = np.histogram(vals, bins=np.arange(vals.min(), vals.max() + 0.1, 0.1))
    floor = float(edges[np.argmax(hist)] + 0.05)
    hmf = np.nan_to_num(hm, nan=floor)

    mask = (hmf > floor + 0.6) & (hmf < floor + 2.5)
    lab, _ = ndimage.label(mask)
    sid = lab[n // 2, n // 2]
    if sid == 0:  # seed missed: take the component nearest to the centre
        idx = np.argwhere(lab > 0)
        d = np.hypot(idx[:, 0] - n / 2, idx[:, 1] - n / 2)
        sid = lab[tuple(idx[np.argmin(d)])]
    comp = lab == sid
    cols, rows = comp.sum(0), comp.sum(1)
    cx_idx = np.where(cols >= 0.6 * cols.max())[0]
    ry_idx = np.where(rows >= 0.6 * rows.max())[0]
    xmin, xmax = x0 + cx_idx.min() * res, x0 + (cx_idx.max() + 1) * res
    ymin, ymax = y0 + ry_idx.min() * res, y0 + (ry_idx.max() + 1) * res
    cx, cy = (xmin + xmax) / 2, (ymin + ymax) / 2
    hx, hy = (xmax - xmin) / 2, (ymax - ymin) / 2
    top = float(np.median(hmf[comp])) - floor

    # Court bounds: march outward from the plinth edge along parallel lines,
    # skip anything attached to the plinth (stairs), stop at the first wall.
    def march(direction):
        dx, dy = direction
        dists = []
        span = hy if dx else hx
        for off in np.linspace(-span * 0.8, span * 0.8, 9):
            px = cx + (off if dy else 0.0)
            py = cy + (off if dx else 0.0)
            start = hx if dx else hy
            on_floor = False
            for s in np.arange(start + 0.2, win - 0.5, res):
                gx = int((px + dx * s - x0) / res)
                gy = int((py + dy * s - y0) / res)
                h = hmf[gy, gx] - floor
                if h < 0.4:
                    on_floor = True
                elif on_floor and h > 0.9:
                    dists.append(s)
                    break
        return float(np.median(dists)) if dists else None

    court = dict(court_e=march((1, 0)), court_w=march((-1, 0)),
                 court_n=march((0, 1)), court_s=march((0, -1)))
    for k in court:
        if court[k] is not None and k in ("court_w", "court_s"):
            court[k] = -court[k]
    return dict(cx=cx, cy=cy, floor=floor, hx=hx, hy=hy, top=top, **court)


# ----------------------------------------------------------------------------
# Phase B — ruins mesh
# ----------------------------------------------------------------------------

def decimate(v, f, target):
    import fast_simplification
    if len(f) <= target:
        return v, f
    red = 1.0 - target / len(f)
    log(f"Decimating {len(f):,} -> ~{target:,} faces (reduction {red:.3f}) ...")
    v2, f2 = fast_simplification.simplify(v.astype(np.float32), f.astype(np.int32),
                                          target_reduction=red, agg=7)
    return np.asarray(v2, np.float64), np.asarray(f2, np.int64)


def drop_floaters(mesh, min_faces=200):
    comps = trimesh.graph.connected_components(mesh.face_adjacency, min_len=1,
                                               nodes=np.arange(len(mesh.faces)))
    keep = np.zeros(len(mesh.faces), bool)
    for c in comps:
        if len(c) >= min_faces:
            keep[c] = True
    mesh.update_faces(keep)
    mesh.remove_unreferenced_vertices()
    return mesh


def value_noise(xy, cell, seed):
    """Smooth 2-D value noise sampled at xy (metres)."""
    rng = np.random.default_rng(seed)
    lo = xy.min(0)
    g = ((xy - lo) / cell)
    shape = (int(g[:, 1].max()) + 3, int(g[:, 0].max()) + 3)
    grid = rng.random(shape)
    return ndimage.map_coordinates(grid, [g[:, 1], g[:, 0]], order=3, mode="nearest")


def cavity(mesh, hm_full, hm_origin, res):
    """-1 (deep recess) .. +1 (exposed top): vertex height vs blurred local surface."""
    v = mesh.vertices
    blur = ndimage.uniform_filter(np.nan_to_num(hm_full, nan=np.nanmin(hm_full)), 9)
    gi = ((v[:, :2] - hm_origin) / res)
    local = ndimage.map_coordinates(blur, [gi[:, 1], gi[:, 0]], order=1, mode="nearest")
    return np.clip((v[:, 2] - local) / 1.2, -1, 1)


# --- photographic stone textures ------------------------------------------------

def _as_jpeg(img, quality=88):
    """Round-trip through JPEG so trimesh embeds it as JPEG (not a 2 MB PNG)."""
    import io
    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="JPEG", quality=quality)
    buf.seek(0)
    out = Image.open(buf)
    out.load()
    return out


def seamless_tile(img, size=1024, blend=0.22):
    """Make a photo tileable: cross-fade it with a half-offset copy near the edges."""
    a = np.asarray(img.convert("RGB").resize((size, size), Image.LANCZOS), dtype=np.float32)
    b = np.roll(a, (size // 2, size // 2), axis=(0, 1))
    t = np.linspace(0, 1, size)
    edge = np.minimum(t, 1 - t)                      # 0 at the border, 0.5 in the middle
    w1 = np.clip(edge / blend, 0, 1)
    w = np.minimum.outer(w1, w1)[..., None]          # 1 inside, fades to 0 at every edge
    w = w * w * (3 - 2 * w)                          # smoothstep
    return Image.fromarray(np.clip(a * w + b * (1 - w), 0, 255).astype(np.uint8))


def load_stone_textures(wall_path, rock_path):
    wall = Image.open(wall_path)
    wW, wH = wall.size
    s = min(wW, wH)                                  # centred square crop keeps stone proportions
    wall = wall.crop(((wW - s) // 2, (wH - s) // 2, (wW + s) // 2, (wH + s) // 2))
    rock = None
    if rock_path and os.path.exists(rock_path):
        r = Image.open(rock_path)
        rW, rH = r.size
        # the bedrock photo has sky in its upper corners: keep the cracked slab only
        rock = r.crop((int(rW * 0.16), int(rH * 0.26), int(rW * 0.66), int(rH * 0.93)))
    return (_as_jpeg(seamless_tile(wall)),
            _as_jpeg(seamless_tile(rock)) if rock is not None else None)


def bake_ruins_textured(mesh, cav, wall_tex, rock_tex, repeat=2.5):
    """Split the scan into wall / ground primitives with baked triplanar UVs.

    Walls  (normal mostly horizontal) -> masonry photo, v axis = height so the
           horizontal courses of the diaper masonry stay horizontal.
    Ground (normal mostly up/down)   -> weathered bedrock photo (or masonry).
    COLOR_0 carries cavity / ambient-occlusion shading that multiplies the photo.
    Returns a list of (name, Trimesh) in glTF Y-up coordinates.
    """
    v, f = mesh.vertices, mesh.faces
    fn = mesh.face_normals
    a = np.abs(fn)
    cls = np.where(a[:, 2] > 0.75, 2, np.where(a[:, 0] >= a[:, 1], 0, 1))  # 0: X-wall 1: Y-wall 2: ground

    # per-vertex AO: deep recesses darker, exposed tops slightly bleached,
    # plus low-frequency tint drift so the repeat doesn't read as wallpaper
    n2 = value_noise(v[:, :2], 4.0, 2)
    n3 = value_noise(v[:, :2], 11.0, 3)
    ao = np.clip(0.72 + 0.55 * cav, 0.28, 1.12)
    ao = np.where(cav < -0.35, ao * 0.85, ao)
    tint = np.stack([1.02 + 0.06 * n3, 1.0 + 0.0 * n3, 0.95 - 0.06 * n3], 1) * (0.9 + 0.2 * n2)[:, None]
    shade = np.clip(ao[:, None] * tint, 0, 1)
    vn = mesh.vertex_normals

    PBR = trimesh.visual.material.PBRMaterial
    mats = {
        "wall": PBR(name="Gandhara_Diaper_Masonry", baseColorTexture=wall_tex,
                    metallicFactor=0.0, roughnessFactor=0.93),
        "ground": PBR(name="Weathered_Bedrock", baseColorTexture=rock_tex or wall_tex,
                      metallicFactor=0.0, roughnessFactor=0.96),
    }
    out = []
    for name, sel in (("wall", cls < 2), ("ground", cls == 2)):
        faces = f[sel]
        fc = cls[sel]
        # one vertex per (original vertex, projection class) so UVs stay continuous
        key = faces * 3 + fc[:, None]
        uniq, inv = np.unique(key.ravel(), return_inverse=True)
        vid, vcls = uniq // 3, uniq % 3
        p = v[vid]
        u = np.where(vcls == 0, p[:, 1], p[:, 0])          # X-wall: along Y, Y-wall/ground: along X
        w = np.where(vcls == 2, p[:, 1], p[:, 2])          # walls: height, ground: northing
        uv = np.column_stack([u, w]) / repeat
        rgba = np.concatenate([shade[vid] ** 2.2, np.ones((len(vid), 1))], 1)  # linear
        vis = trimesh.visual.TextureVisuals(uv=uv, material=mats[name])
        vis.vertex_attributes["color"] = (np.clip(rgba, 0, 1) * 255).astype(np.uint8)
        m = trimesh.Trimesh(to_yup(p), inv.reshape(-1, 3), vertex_normals=to_yup(vn[vid]),
                            visual=vis, process=False)
        out.append((f"Ruins_{name.capitalize()}", m))
    return out


def bake_stone_colors(mesh, hm_full, hm_origin, res):
    """Fallback procedural colouring, used only when no stone photo is available."""
    v = mesh.vertices
    nz = np.clip(mesh.vertex_normals[:, 2], -1, 1)
    cav = cavity(mesh, hm_full, hm_origin, res)

    n1 = value_noise(v[:, :2], 0.6, 1)
    n2 = value_noise(v[:, :2], 3.0, 2)
    base_dark = np.array([0.26, 0.24, 0.21])
    base_mid = np.array([0.47, 0.43, 0.37])     # grey-brown schist masonry
    base_dust = np.array([0.70, 0.62, 0.50])    # sun-bleached dusty tops
    green = np.array([0.36, 0.40, 0.28])

    flat = np.clip((nz - 0.55) / 0.4, 0, 1)[:, None]
    col = base_mid * (1 - flat) + base_dust * flat
    col = col * (0.78 + 0.44 * n1[:, None])
    col = col * (1 - 0.18 * n2[:, None]) + green * 0.18 * n2[:, None]
    shade = np.clip(0.80 + 0.5 * cav, 0.35, 1.15)[:, None]
    col = col * shade
    col = np.where(cav[:, None] < -0.35, col * 0.8 + base_dark * 0.2, col)
    lin = np.clip(col, 0, 1) ** 2.2          # glTF COLOR_0 is linear, the palette above is sRGB
    rgba = np.concatenate([lin, np.ones((len(v), 1))], 1)
    return (rgba * 255).astype(np.uint8)


# ----------------------------------------------------------------------------
# Phase C — procedural reconstruction helpers
# ----------------------------------------------------------------------------

def plaster_texture(size=512, seed=7):
    """Tileable lime-plaster (chunam) texture: ivory with warm ochre mottling."""
    rng = np.random.default_rng(seed)

    def field(beta):
        w = rng.normal(size=(size, size))
        fy = np.fft.fftfreq(size)[:, None]
        fx = np.fft.fftfreq(size)[None, :]
        fr = np.sqrt(fx ** 2 + fy ** 2)
        fr[0, 0] = 1
        out = np.real(np.fft.ifft2(np.fft.fft2(w) / fr ** beta))
        return (out - out.min()) / (out.max() - out.min())

    broad, mid, grain = field(1.8), field(1.2), field(0.3)
    ivory = np.array([238, 227, 203]) / 255
    ochre = np.array([214, 168, 104]) / 255
    sand = np.array([222, 199, 160]) / 255
    t = np.clip((broad - 0.45) * 2.2, 0, 1)[..., None]
    col = ivory * (1 - t) + sand * t
    col = col * (1 - 0.25 * np.clip(mid - 0.55, 0, 1)[..., None] * 3) \
        + ochre * 0.25 * np.clip(mid - 0.55, 0, 1)[..., None] * 3
    col *= (0.93 + 0.1 * grain)[..., None]
    return Image.fromarray((np.clip(col, 0, 1) * 255).astype(np.uint8))


def box(x0, x1, y0, y1, z0, z1):
    ext = [x1 - x0, y1 - y0, z1 - z0]
    tf = trimesh.transformations.translation_matrix([(x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2])
    return trimesh.creation.box(extents=ext, transform=tf)


def revolve(profile, sections=64):
    m = trimesh.creation.revolve(np.asarray(profile, float), sections=sections)
    m.merge_vertices()
    if m.volume < 0:  # make sure faces point outward
        m.invert()
    return m


def cylinder(r, z0, z1, sections=48):
    return revolve([[0, z0], [r, z0], [r, z1], [0, z1]], sections)


def ellipsoid(c, r, subdiv=2):
    m = trimesh.creation.icosphere(subdivisions=subdiv, radius=1.0)
    m.apply_scale(r)
    m.apply_translation(c)
    return m


def strip_solid(inner, outer, d0, d1):
    """Closed solid between two (s,z) polylines, extruded along local y (d0..d1)."""
    inner, outer = np.asarray(inner, float), np.asarray(outer, float)
    n = len(inner)
    rings = []
    for pts, d in ((inner, d0), (outer, d0), (inner, d1), (outer, d1)):
        rings.append(np.column_stack([pts[:, 0], np.full(n, d), pts[:, 1]]))
    V = np.vstack(rings)
    I0, O0, I1, O1 = (np.arange(n) + k * n for k in range(4))
    F = []
    for i in range(n - 1):
        j = i + 1
        F += [[I0[i], O0[i], O0[j]], [I0[i], O0[j], I0[j]]]      # front
        F += [[I1[i], O1[j], O1[i]], [I1[i], I1[j], O1[j]]]      # back
        F += [[I0[i], I0[j], I1[j]], [I0[i], I1[j], I1[i]]]      # inner
        F += [[O0[i], O1[j], O0[j]], [O0[i], O1[i], O1[j]]]      # outer
    k = 0                                                         # end caps
    F += [[I0[k], I1[k], O1[k]], [I0[k], O1[k], O0[k]]]
    k = n - 1
    F += [[I0[k], O1[k], I1[k]], [I0[k], O0[k], O1[k]]]
    return trimesh.Trimesh(V, np.array(F), process=False)


def rect_hit(theta, hw, h):
    """Point where a ray from (0,0) at angle theta hits the rectangle [-hw,hw]x[0,h]."""
    c, s = math.cos(theta), math.sin(theta)
    tx = hw / abs(c) if abs(c) > 1e-9 else 1e9
    tz = h / s if s > 1e-9 else 1e9
    t = min(tx, tz)
    return [c * t, s * t]


class MatBuilder:
    """Accumulates meshes for one material with triplanar UVs + crease-aware normals."""

    def __init__(self, name, material, uv_scale=2.0):
        self.name, self.material, self.uv_scale = name, material, uv_scale
        self.V, self.F, self.UV, self.N = [], [], [], []
        self.count = 0

    def add(self, mesh, tf=None):
        m = mesh.copy()
        if tf is not None:
            m.apply_transform(tf)
        fn = m.face_normals
        vn = m.vertex_normals[m.faces]                  # (F,3,3) smooth normals
        corners = m.vertices[m.faces]                   # (F,3,3)
        dot = np.einsum("fcj,fj->fc", vn, fn)
        normals = np.where(dot[..., None] > math.cos(math.radians(35)), vn, fn[:, None, :])
        axis = np.argmax(np.abs(fn), 1)
        uv = np.empty(corners.shape[:2] + (2,))
        for a, (u, w) in enumerate(((1, 2), (0, 2), (0, 1))):
            sel = axis == a
            uv[sel, :, 0] = corners[sel][..., u] / self.uv_scale
            uv[sel, :, 1] = corners[sel][..., w] / self.uv_scale
        nf = len(m.faces)
        self.V.append(corners.reshape(-1, 3))
        self.N.append(normals.reshape(-1, 3))
        self.UV.append(uv.reshape(-1, 2))
        self.F.append(np.arange(nf * 3).reshape(-1, 3) + self.count)
        self.count += nf * 3

    def build(self):
        V = to_yup(np.vstack(self.V))
        N = to_yup(np.vstack(self.N))
        N /= np.linalg.norm(N, axis=1, keepdims=True) + 1e-12
        UV = np.vstack(self.UV)
        # weld corners that share position + normal + uv (keeps the GLB small)
        key = np.round(np.hstack([V * 1e4, N * 1e3, UV * 1e4])).astype(np.int64)
        _, first, inv = np.unique(key, axis=0, return_index=True, return_inverse=True)
        F = inv.reshape(-1)[np.vstack(self.F)]
        vis = trimesh.visual.TextureVisuals(uv=UV[first], material=self.material)
        m = trimesh.Trimesh(V[first], F, vertex_normals=N[first], visual=vis, process=False)
        return m


def frame(origin, outward):
    """4x4 from chapel-local (s along wall, d outward, z up) into stupa-local."""
    o = np.array([outward[0], outward[1], 0.0])
    z = np.array([0, 0, 1.0])
    t = np.cross(o, z)
    M = np.eye(4)
    M[:3, 0], M[:3, 1], M[:3, 2], M[:3, 3] = t, o, z, [origin[0], origin[1], 0]
    return M


# ----------------------------------------------------------------------------
# Phase C — the reconstruction
# ----------------------------------------------------------------------------

def seated_buddha(B, z0, scale=1.0):
    """Stylised seated Buddha in dhyana mudra, facing local -y (toward court)."""
    s = scale
    gold, halo, trim = B["gilded"], B["halo"], B["trim"]
    # lotus pedestal
    trim.add(revolve([[0, z0], [0.42 * s, z0], [0.46 * s, z0 + 0.08 * s],
                      [0.38 * s, z0 + 0.14 * s], [0.48 * s, z0 + 0.26 * s],
                      [0.0, z0 + 0.26 * s]], 32))
    b = z0 + 0.26 * s
    gold.add(ellipsoid([0, 0, b + 0.13 * s], [0.46 * s, 0.30 * s, 0.15 * s]))   # crossed legs
    gold.add(ellipsoid([0, 0.03 * s, b + 0.47 * s], [0.25 * s, 0.17 * s, 0.34 * s]))  # torso/robe
    gold.add(ellipsoid([0, 0.02 * s, b + 0.70 * s], [0.30 * s, 0.17 * s, 0.10 * s]))  # shoulders
    gold.add(ellipsoid([0, -0.20 * s, b + 0.25 * s], [0.17 * s, 0.09 * s, 0.06 * s]))  # hands in lap
    gold.add(ellipsoid([0, 0.0, b + 0.92 * s], [0.12 * s, 0.13 * s, 0.15 * s]))      # head
    gold.add(ellipsoid([0, 0.01 * s, b + 1.07 * s], [0.075 * s, 0.075 * s, 0.07 * s], 2))  # ushnisha
    for sx in (-1, 1):  # elongated ears
        gold.add(ellipsoid([sx * 0.12 * s, 0.01 * s, b + 0.89 * s], [0.025 * s, 0.03 * s, 0.07 * s], 1))
    # halo (prabhamandala) behind the head
    h = revolve([[0, 0], [0.32 * s, 0], [0.32 * s, 0.035 * s], [0, 0.035 * s]], 40)
    rot = trimesh.transformations.rotation_matrix(math.pi / 2, [1, 0, 0])
    h.apply_transform(rot)
    h.apply_translation([0, 0.16 * s, b + 0.92 * s])
    halo.add(h)


def build_stupa(B, P, s):
    """Main Stupa: square plinth (measured) + drum, anda, harmika, chattravali."""
    plaster, trim, gilded = B["plaster"], B["trim"], B["gilded"]
    hx, hy, Hp = P["hx"], P["hy"], P["top"]

    # --- square plinth with mouldings and Corinthian-style pilasters
    plaster.add(box(-hx, hx, -hy, hy, 0, Hp))
    trim.add(box(-hx - 0.14, hx + 0.14, -hy - 0.14, hy + 0.14, 0, 0.22))
    trim.add(box(-hx - 0.12, hx + 0.12, -hy - 0.12, hy + 0.12, Hp - 0.16, Hp))
    for side in range(4):
        L = 2 * (hx if side % 2 == 0 else hy)
        npil = max(3, int(L / 1.1))
        for k in range(npil):
            u = -L / 2 + 0.35 + k * (L - 0.7) / (npil - 1)
            if side == 0:
                bx = box(u - 0.11, u + 0.11, -hy - 0.07, -hy, 0.22, Hp - 0.16)
            elif side == 2:
                if abs(u) < P["stair_w"] / 2 + 0.2:
                    continue
                bx = box(u - 0.11, u + 0.11, hy, hy + 0.07, 0.22, Hp - 0.16)
            elif side == 1:
                bx = box(hx, hx + 0.07, u - 0.11, u + 0.11, 0.22, Hp - 0.16)
            else:
                bx = box(-hx - 0.07, -hx, u - 0.11, u + 0.11, 0.22, Hp - 0.16)
            plaster.add(bx)

    # --- north stairway (measured on the scan)
    sw, sl = P["stair_w"], P["stair_len"]
    nsteps = 7
    for k in range(nsteps):
        plaster.add(box(-sw / 2, sw / 2, hy - 0.01, hy + sl * (k + 1) / nsteps,
                        0, Hp * (nsteps - k) / nsteps))
    for sx in (-1, 1):  # balustrades
        x = sx * (sw / 2 + 0.12)
        trim.add(box(x - 0.12, x + 0.12, hy, hy + sl, 0, 0.35))
        plaster.add(box(x - 0.1, x + 0.1, hy, hy + sl * 0.55, 0.35, Hp + 0.25))

    # --- drum + anda (one revolved profile, scaled by s)
    R = 3.8 * s
    z = Hp
    drum_h = 1.8 * s
    prof = [[0, z], [R + 0.18, z], [R + 0.18, z + 0.12], [R + 0.06, z + 0.2],
            [R, z + 0.22], [R, z + drum_h * 0.48], [R + 0.07, z + drum_h * 0.5],
            [R + 0.07, z + drum_h * 0.56], [R, z + drum_h * 0.58], [R, z + drum_h - 0.12],
            [R + 0.16, z + drum_h - 0.06], [R + 0.16, z + drum_h], [R, z + drum_h]]
    zc = z + drum_h
    for a in np.linspace(0, math.pi / 2, 28)[1:]:
        prof.append([R * math.cos(a), zc + R * math.sin(a)])
    prof[-1][0] = 0.0
    plaster.add(revolve(prof, 96))
    # ochre bands on drum
    trim.add(revolve([[R - 0.02, z + drum_h * 0.5], [R + 0.075, z + drum_h * 0.5],
                      [R + 0.075, z + drum_h * 0.56], [R - 0.02, z + drum_h * 0.56]], 96))
    # drum pilasters
    for k in range(20):
        a = 2 * math.pi * k / 20
        pil = box(-0.09, 0.09, -0.05, 0.05, z + 0.22, z + drum_h * 0.48)
        pil.apply_translation([0, R, 0])
        pil.apply_transform(trimesh.transformations.rotation_matrix(a, [0, 0, 1]))
        plaster.add(pil)
        pil2 = box(-0.08, 0.08, -0.05, 0.05, z + drum_h * 0.58, z + drum_h - 0.12)
        pil2.apply_translation([0, R, 0])
        pil2.apply_transform(trimesh.transformations.rotation_matrix(a + math.pi / 20, [0, 0, 1]))
        plaster.add(pil2)

    # --- harmika
    ztop = zc + R
    hw = 0.6 * s
    zh0 = ztop - 0.12 * s
    zh1 = zh0 + 0.8 * s
    trim.add(box(-hw, hw, -hw, hw, zh0, zh1))
    for k, grow in enumerate((0.08, 0.16, 0.25)):
        g = (hw + grow * s)
        plaster.add(box(-g, g, -g, g, zh1 + k * 0.1 * s, zh1 + (k + 1) * 0.1 * s))
    for sx in (-1, 1):  # vedika railing posts on harmika
        for t in np.linspace(-hw + 0.08, hw - 0.08, 4):
            plaster.add(box(sx * hw - 0.03, sx * hw + 0.03, t - 0.03, t + 0.03, zh0 + 0.1, zh1 - 0.05))
            plaster.add(box(t - 0.03, t + 0.03, sx * hw - 0.03, sx * hw + 0.03, zh0 + 0.1, zh1 - 0.05))
    zm0 = zh1 + 0.3 * s

    # --- mast (yasti) + 5 chattras
    mast_h = 3.5 * s
    trim.add(cylinder(0.07 * s, zm0 - 0.05, zm0 + mast_h, 16))
    radii = [1.8, 1.5, 1.2, 0.9, 0.6]
    for k, r in enumerate(radii):
        zc_ = zm0 + 0.35 * s + k * (mast_h - 0.6 * s) / (len(radii) - 1)
        r *= s
        t = 0.07 * s
        trim.add(revolve([[0, zc_ - t], [r * 0.92, zc_ - t - 0.05 * s], [r, zc_ - t - 0.09 * s],
                          [r, zc_ - t - 0.04 * s], [r * 0.5, zc_ + t * 0.6], [0, zc_ + t]], 64))
        gilded.add(revolve([[0, zc_ - t - 0.02], [0.1 * s, zc_ - t - 0.02],
                            [0.1 * s, zc_ + t + 0.02], [0, zc_ + t + 0.02]], 16))
    zf = zm0 + mast_h
    gilded.add(revolve([[0, zf], [0.12 * s, zf], [0.16 * s, zf + 0.12 * s], [0.08 * s, zf + 0.3 * s],
                        [0, zf + 0.45 * s]], 24))

    # --- relic casket (sealed inside the drum, revealed by the app's x-ray)
    B["halo"].add(revolve([[0, Hp + 0.2], [0.42, Hp + 0.2], [0.42, Hp + 0.75], [0.3, Hp + 0.88],
                           [0.08, Hp + 1.05], [0.06, Hp + 1.2], [0, Hp + 1.25]], 32))

    return dict(dome_top=ztop, drum_mid=Hp + drum_h * 0.5, R=R, finial=zf + 0.45 * s,
                relic=Hp + 0.5)


def build_chapel(B, M, w, D, wall_t, statue):
    """One chapel module (local: s across, d outward, z up). Front at d=0."""
    plaster, trim, paving = B["plaster"], B["trim"], B["paving"]
    hw = w / 2
    plat = 0.45          # raised chapel floor
    wall_h = 3.3         # springing of the vault
    # side walls (shared dividers — each module owns its left one + half)
    plaster.add(box(-hw, -hw + wall_t, 0, D, 0, wall_h), M)
    plaster.add(box(hw - wall_t, hw, 0, D, 0, wall_h), M)
    plaster.add(box(-hw, hw, D - wall_t, D, 0, wall_h), M)         # back wall
    paving.add(box(-hw + wall_t, hw - wall_t, 0.15, D - wall_t, 0, plat), M)
    trim.add(box(-hw, hw, -0.08, 0.15, 0, plat), M)                  # threshold step

    # front wall with arched doorway (spandrel solid between arch and rectangle)
    door_hw = hw - wall_t - 0.18
    spring = 2.15
    fw_t0, fw_t1 = 0.0, 0.32
    plaster.add(box(-hw + wall_t, -door_hw, fw_t0, fw_t1, plat, wall_h), M)
    plaster.add(box(door_hw, hw - wall_t, fw_t0, fw_t1, plat, wall_h), M)
    th = np.linspace(0, math.pi, 25)
    inner = np.column_stack([door_hw * np.cos(th), spring + door_hw * np.sin(th)])
    outer = np.array([rect_hit(t, door_hw, wall_h - spring) for t in th]) + [0, spring]
    plaster.add(strip_solid(inner, outer, fw_t0, fw_t1), M)
    # ochre arch moulding around the doorway
    ring_o = np.column_stack([(door_hw + 0.12) * np.cos(th), spring + (door_hw + 0.12) * np.sin(th)])
    trim.add(strip_solid(inner, ring_o, fw_t0 - 0.05, fw_t0 + 0.02), M)

    # barrel vault roof (axis along d) + cornice
    trim.add(box(-hw - 0.05, hw + 0.05, -0.12, D + 0.05, wall_h, wall_h + 0.14), M)
    vt = np.linspace(0, math.pi, 25)
    vin = np.column_stack([(hw - 0.05) * np.cos(vt), wall_h + 0.14 + (hw - 0.05) * 0.85 * np.sin(vt)])
    vout = vin.copy()
    vin_core = np.column_stack([(hw - 0.05) * 0.02 * np.cos(vt), wall_h + 0.14 + 0.0 * vt])
    plaster.add(strip_solid(vin_core, vout, 0.0, D), M)

    # caitya (ogee) gable arch on the façade
    ga = np.linspace(0, math.pi, 41)
    R0 = hw - 0.05
    tip = 0.55 * np.exp(-((ga - math.pi / 2) / 0.22) ** 2)
    g_out = np.column_stack([R0 * np.cos(ga), wall_h + 0.14 + R0 * 0.85 * np.sin(ga) + tip])
    g_in = np.column_stack([(R0 - 0.22) * np.cos(ga),
                            wall_h + 0.14 + (R0 - 0.22) * 0.85 * np.sin(ga) + tip * 0.75])
    trim.add(strip_solid(g_in, g_out, -0.14, 0.04), M)
    # tympanum (recessed plaster face inside the gable)
    core = np.column_stack([0.01 * np.cos(ga), np.full_like(ga, wall_h + 0.14)])
    plaster.add(strip_solid(core, g_in, -0.05, 0.02), M)
    # little stupa-finial on the gable apex
    fin = cylinder(0.08, 0, 0.25, 12)
    fin.apply_translation([0, -0.05, wall_h + 0.14 + R0 * 0.85 + 0.5])
    B["gilded"].add(fin, M)

    if statue:
        T =trimesh.transformations.translation_matrix([0, D - wall_t - 0.55, 0])
        seated_buddha(MatBuilderProxy(B, M @ T), plat, 1.0)
        return (M @ T) @ np.array([0, 0, plat + 1.3, 1.0])
    return None


class MatBuilderProxy(dict):
    """dict of builders that pre-applies a transform to every add()."""

    def __init__(self, B, M):
        super().__init__()
        for k, b in B.items():
            self[k] = _TfAdder(b, M)


class _TfAdder:
    def __init__(self, b, M):
        self.b, self.M = b, M

    def add(self, mesh, tf=None):
        self.b.add(mesh, self.M if tf is None else self.M @ tf)


def build_court(B, P):
    """Chapels on the W, S and E sides of the Stupa Court (N is the open stair side)."""
    D, wall_t = 2.6, 0.4
    W, E, S, N = P["court_w"], P["court_e"], P["court_s"], P["court_n"]
    statues = []
    sides = [  # (outward normal, start point on court edge, length)
        ((-1, 0), (W, S), N - S),
        ((1, 0), (E, N), N - S),
        ((0, -1), (E, S), E - W),
    ]
    for (ox, oy), (px, py), L in sides:
        n = max(3, int(round(L / 2.9)))
        w = L / n
        o = np.array([ox, oy, 0.0])
        t = np.cross(o, [0, 0, 1])
        for k in range(n):
            c = np.array([px, py, 0.0]) + t * (w * (k + 0.5))
            M = frame(c, (ox, oy))
            p = build_chapel(B, M, w, D, wall_t, statue=True)
            statues.append(p[:3])
    # corner blocks
    for cx, cy in ((W, S), (E, S)):
        sx = -1 if cx == W else 1
        B["plaster"].add(box(min(cx, cx + sx * D), max(cx, cx + sx * D), S - D, S, 0, 3.3))
        B["trim"].add(box(min(cx, cx + sx * D) - 0.05, max(cx, cx + sx * D) + 0.05,
                          S - D - 0.05, S + 0.05, 3.3, 3.44))
    # paved court floor (stone flags)
    B["paving"].add(box(W, E, S, N, 0.0, 0.05))
    # low parapet + central steps on the open north side
    for x0, x1 in ((W, -2.0), (2.0, E)):
        B["plaster"].add(box(x0, x1, N, N + 0.45, 0, 0.9))
        B["trim"].add(box(x0 - 0.03, x1 + 0.03, N - 0.03, N + 0.48, 0.9, 1.0))
    for k in range(5):
        B["paving"].add(box(-2.0, 2.0, N + k * 0.32, N + 1.6, 0, 0.24 * (k + 1)))
    return statues


def make_reconstruction(P, literal):
    tex = plaster_texture()
    PBR = trimesh.visual.material.PBRMaterial
    mats = dict(
        plaster=PBR(name="LimePlaster_Chunam", baseColorTexture=tex,
                    baseColorFactor=[1.0, 0.97, 0.92, 1.0], metallicFactor=0.0, roughnessFactor=0.88),
        trim=PBR(name="Ochre_Trim", baseColorTexture=tex,
                 baseColorFactor=[0.86, 0.62, 0.36, 1.0], metallicFactor=0.0, roughnessFactor=0.8),
        paving=PBR(name="Sandstone_Paving", baseColorTexture=tex,
                   baseColorFactor=[0.80, 0.70, 0.55, 1.0], metallicFactor=0.0, roughnessFactor=0.92),
        gilded=PBR(name="Gilded_Buddha", baseColorTexture=tex,
                   baseColorFactor=[1.0, 0.80, 0.42, 1.0], metallicFactor=0.45, roughnessFactor=0.34),
        halo=PBR(name="Gold_Halo", baseColorFactor=[1.0, 0.84, 0.45, 1.0], baseColorTexture=tex,
                 metallicFactor=0.85, roughnessFactor=0.25, emissiveFactor=[0.18, 0.12, 0.03]),
    )
    B = {k: MatBuilder(k, m, uv_scale=1.6) for k, m in mats.items()}

    # stupa scale: fit the drum on the measured plinth unless --literal-dims
    fit = (min(P["hx"], P["hy"]) - 0.3) / 3.8
    s = 1.0 if literal else min(1.0, fit)
    log(f"Stupa superstructure scale = {s:.3f} (drum radius {3.8 * s:.2f} m"
        f"{', literal spec' if literal else ', fitted to measured plinth'})")

    info = build_stupa(B, P, s)
    statues = build_court(B, P)

    scene = trimesh.Scene()
    names = dict(plaster="Recon_Plaster", trim="Recon_OchreTrim", paving="Recon_Paving",
                 gilded="Recon_Gilded", halo="Recon_Halo")
    total = 0
    for k, b in B.items():
        if b.count:
            m = b.build()
            total += len(m.faces)
            scene.add_geometry(m, node_name=names[k], geom_name=names[k])
    log(f"Reconstruction: {total:,} faces, {len(statues)} niche Buddhas")
    return scene, info, statues, s


# ----------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", default=DEFAULT_INPUT)
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--faces", type=int, default=140_000, help="target face count for ruins")
    ap.add_argument("--literal-dims", action="store_true",
                    help="use the literal 3.8 m drum radius even if it overhangs the plinth")
    ap.add_argument("--wall-texture", default=os.path.join(DEFAULT_OUT, "gandhara_stone_wall.jpg"),
                    help="photo of the diaper masonry baked onto walls of ruins.glb")
    ap.add_argument("--rock-texture", default=os.path.join(DEFAULT_OUT, "weathered_rock.jpg"),
                    help="photo of weathered bedrock baked onto floors / wall tops")
    ap.add_argument("--texture-repeat", type=float, default=2.5, help="metres per texture repeat")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    # copy the field photographs into assets/ if they aren't there yet
    import shutil
    for dst, src in ((args.wall_texture, SRC_WALL_PHOTO), (args.rock_texture, SRC_ROCK_PHOTO)):
        if not os.path.exists(dst) and os.path.exists(src):
            shutil.copyfile(src, dst)
            log(f"Copied {os.path.basename(src)} -> {dst}")
    t0 = time.time()

    v, f = load_scan(args.input)

    # --- plinth & court detection (in float64 UTM)
    log("Detecting Main Stupa plinth and Stupa Court bounds ...")
    P = detect_plinth(v, SEED_UTM)
    ok = (2.0 < P["hx"] < 8 and 2.0 < P["hy"] < 8 and 0.5 < P["top"] < 3
          and all(P[k] is not None and 3 < abs(P[k]) < 25
                  for k in ("court_w", "court_e", "court_s", "court_n")))
    if not ok:
        log(f"  detection looked unreliable ({P}); using fallback measurements")
        P.update(FALLBACK)
        P["cx"], P["cy"] = SEED_UTM
    P["stair_w"], P["stair_len"] = 2.5, 3.1
    log(f"  plinth centre UTM E{P['cx']:.3f} N{P['cy']:.3f}, floor z={P['floor']:.3f} m")
    log(f"  plinth {2 * P['hx']:.2f} x {2 * P['hy']:.2f} m, height {P['top']:.2f} m")
    log(f"  court inner bounds W{P['court_w']:.2f} E{P['court_e']:.2f} "
        f"S{P['court_s']:.2f} N{P['court_n']:.2f} m")
    origin = np.array([P["cx"], P["cy"], P["floor"]])

    # --- recentre in float64, then it is safe to drop to float32
    v = v - origin
    full_hm_res = 0.5
    hm_origin = v[:, :2].min(0)
    span = v[:, :2].max(0) - hm_origin
    hm_full = height_grid(v, hm_origin[0], hm_origin[1],
                          int(span[0] / full_hm_res) + 1, int(span[1] / full_hm_res) + 1, full_hm_res)

    mesh = trimesh.Trimesh(v, f, process=False)
    mesh.merge_vertices()
    log(f"  merged UV seams -> {len(mesh.vertices):,} verts")
    v2, f2 = decimate(np.asarray(mesh.vertices), np.asarray(mesh.faces), args.faces)
    ruins = trimesh.Trimesh(v2, f2, process=True)
    ruins = drop_floaters(ruins)
    log(f"  ruins mesh: {len(ruins.faces):,} faces, {len(ruins.vertices):,} verts")

    rs = trimesh.Scene()
    if os.path.exists(args.wall_texture):
        log(f"Baking photographic stone texture ({os.path.basename(args.wall_texture)}, "
            f"{args.texture_repeat} m repeat, triplanar) ...")
        wall_tex, rock_tex = load_stone_textures(args.wall_texture, args.rock_texture)
        cav = cavity(ruins, hm_full, hm_origin, full_hm_res)
        for name, m in bake_ruins_textured(ruins, cav, wall_tex, rock_tex, args.texture_repeat):
            rs.add_geometry(m, node_name=name, geom_name=name)
            log(f"  {name}: {len(m.faces):,} faces, {len(m.vertices):,} verts")
    else:
        log(f"  {args.wall_texture} not found: falling back to procedural vertex colours")
        colors = bake_stone_colors(ruins, hm_full, hm_origin, full_hm_res)
        ruins_y = trimesh.Trimesh(to_yup(ruins.vertices), ruins.faces,
                                  vertex_normals=to_yup(ruins.vertex_normals),
                                  vertex_colors=colors, process=False)
        rs.add_geometry(ruins_y, node_name="Ruins_Scan_2026", geom_name="Ruins_Scan_2026")
    ruins_path = os.path.join(args.out, "ruins.glb")
    rs.export(ruins_path)
    log(f"  wrote {ruins_path} ({os.path.getsize(ruins_path) / 1e6:.1f} MB)")

    # --- reconstruction
    log("Building 2nd-century CE reconstruction ...")
    recon, info, statues, s = make_reconstruction(P, args.literal_dims)
    recon_path = os.path.join(args.out, "reconstructed.glb")
    recon.export(recon_path)
    log(f"  wrote {recon_path} ({os.path.getsize(recon_path) / 1e6:.1f} MB)")

    # --- metadata for the web app (hotspots in glTF Y-up coordinates)
    lat, lon = utm_to_latlon(P["cx"], P["cy"], UTM_ZONE)
    west = [p for p in statues if p[0] < P["court_w"] - 0.5]
    niche = west[len(west) // 2] if west else statues[0]
    hot = {
        "stupa": to_yup([0, 0, info["dome_top"] + 0.3]).tolist(),
        "relic": to_yup([(info["R"] + 0.25) * 0.71, -(info["R"] + 0.25) * 0.71, info["relic"] + 0.4]).tolist(),
        "niche": to_yup(niche).tolist(),
    }
    bmin, bmax = rs.bounds
    meta = {
        "site": "Takht-i-Bahi Buddhist Monastery — Stupa Court",
        "crs": f"EPSG:326{UTM_ZONE}",
        "origin_utm": [round(float(x), 3) for x in origin],
        "origin_latlon": [round(lat, 7), round(lon, 7)],
        "axes": "glTF Y-up: +X East, +Y Up, -Z North; metres; origin = plinth centre at court floor",
        "plinth": {"width_ew": round(2 * P["hx"], 2), "depth_ns": round(2 * P["hy"], 2),
                   "height": round(P["top"], 2)},
        "court": {k: round(P[k], 2) for k in ("court_w", "court_e", "court_s", "court_n")},
        "stupa_scale": round(s, 3),
        "drum_radius": round(info["R"], 2),
        "stupa_height": round(info["finial"], 2),
        "ruins_bounds": [bmin.round(2).tolist(), bmax.round(2).tolist()],
        "ruins_faces": int(len(ruins.faces)),
        "hotspots": hot,
    }
    with open(os.path.join(args.out, "scene_meta.json"), "w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2, ensure_ascii=False)
    log(f"  lat/lon {lat:.6f}, {lon:.6f}; wrote scene_meta.json")
    log(f"Done in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
