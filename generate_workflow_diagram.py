"""
generate_workflow_diagram.py — pitch-deck graphic of the Takht-i-Bahi Digital Twin
system architecture & tech stack (KPITB AI Challenge 2026).

Output: 1920 x 1080 px (16:9) PNG at 300 DPI, saved to
    C:\\Users\\DELL\\Desktop\\tech_stack_workflow.png
    <this folder>\\assets\\tech_stack_workflow.png

    python generate_workflow_diagram.py
"""

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUTPUTS = [
    os.path.join(os.path.expanduser("~"), "Desktop", "tech_stack_workflow.png"),
    os.path.join(HERE, "assets", "tech_stack_workflow.png"),
]

W, H, DPI = 1920, 1080, 300          # pixels; figure = 6.4 x 3.6 in @ 300 dpi
PT = 72 / DPI                        # 1 px expressed in points

# palette
NAVY = "#0a1128"
CARD = "#101b3d"
CARD_HEAD = "#16244f"
CYAN = "#00d4ff"
GOLD = "#f6d58f"
WHITE = "#ffffff"
MUTED = "#aab8d6"
TEAL = "#18a08d"

SANS = "Segoe UI"
MONO = "Consolas"


def fp(px, weight="normal", family=SANS):
    """FontProperties sized in pixels."""
    return FontProperties(family=family, weight=weight, size=px * PT)


# ---------------------------------------------------------------------------
# Content (kept accurate to what the project actually does)
# ---------------------------------------------------------------------------
STAGES = [
    {
        "title": "DATA INGESTION",
        "sub": "Field data & references",
        "items": [
            ("Photogrammetry scan", "142 MB OBJ from 3DF Zephyr · UTM zone 42N · 1.14 M triangles"),
            ("On-site field photos", "Authentic Gandharan diaper masonry & weathered bedrock"),
            ("Archaeological records", "2nd-century CE Kushan stupa proportions & court plan"),
        ],
        "chips": ["OBJ", "JPEG", "UTM 42N", "EPSG:32642"],
    },
    {
        "title": "3D PREPROCESSING",
        "sub": "process_mesh.py",
        "mono_sub": True,
        "items": [
            ("Float64 re-centring", "Auto-detects the plinth; UTM → local (0,0,0), no 32-bit GPU jitter"),
            ("Quadric-error decimation", "1.14 M → 136 k faces (−88 %) · 142 MB → 6.4 MB GLB"),
            ("Procedural anastylosis", "6.5 m plinth · 2.95 m drum · anda · harmika · 5 chattras"),
            ("Photo texture bake", "Triplanar UVs + cavity AO baked into ruins.glb"),
        ],
        "chips": ["Python 3.13", "trimesh", "numpy", "scipy", "Pillow", "fast-simplification"],
    },
    {
        "title": "GRAPHICS & SHADERS",
        "sub": "Three.js real-time engine",
        "items": [
            ("WebGL 2 renderer", "PBR materials · warm outdoor sun · soft shadows · sky image-based light"),
            ("GLSL stone shader", "Field photo × baked AO with crack & mortar darkening"),
            ("Time-Warp shader", "uFade uniform cross-fades the 2026 ruins into the reconstruction inside the court"),
        ],
        "chips": ["Three.js r160", "GLTFLoader", "GLSL", "OrbitControls"],
    },
    {
        "title": "WEBAR & VOICE",
        "sub": "Multilingual AR engine",
        "items": [
            ("Camera pass-through", "MediaDevices getUserMedia · rear camera behind a transparent canvas"),
            ("Orientation + GPS anchor", "DeviceOrientation 3-DoF · compass heading · 1:1 geo-anchoring on site"),
            ("Trilingual narration", "Pre-rendered neural voices via HTML5 Audio · English · Urdu · Pashto"),
        ],
        "chips": ["MediaDevices", "Geolocation", "edge-tts", "Web Speech fallback"],
    },
    {
        "title": "END-USER DELIVERABLES",
        "sub": "Live on GitHub Pages",
        "items": [
            ("Zero-install WebAR", "Opens in mobile Chrome & Safari over HTTPS: no app store"),
            ("3D Orbit explorer", "Desktop & remote judges: orbit, zoom, hotspots, X-ray relic view"),
            ("Souvenir photo", "3000 px watermarked capture with native share"),
        ],
        "chips": ["HTTPS", "Mobile + Desktop", "EN / UR / PS"],
    },
]

METRICS = [
    ("135,706", "scan faces streamed"),
    ("10 MB", "total 3D payload"),
    ("3", "languages narrated"),
    ("0", "installs required"),
]


# ---------------------------------------------------------------------------
# Drawing helpers
# ---------------------------------------------------------------------------
class Canvas:
    def __init__(self):
        self.fig = plt.figure(figsize=(W / DPI, H / DPI), dpi=DPI, facecolor=NAVY)
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.set_xlim(0, W)
        self.ax.set_ylim(H, 0)                    # pixel coords, y down
        self.ax.axis("off")
        self.ax.set_facecolor(NAVY)
        self.r = self.fig.canvas.get_renderer()

    def width(self, s, prop):
        w, _, _ = self.r.get_text_width_height_descent(s, prop, ismath=False)
        return w

    def wrap(self, text, prop, max_w):
        lines, cur = [], ""
        for word in text.split():
            t = f"{cur} {word}".strip()
            if self.width(t, prop) <= max_w or not cur:
                cur = t
            else:
                lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines

    def text(self, x, y, s, prop, color=WHITE, ha="left", va="top", **kw):
        return self.ax.text(x, y, s, fontproperties=prop, color=color, ha=ha, va=va, **kw)

    def rbox(self, x, y, w, h, r, fc, ec="none", lw=0, alpha=1.0, z=1):
        p = FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                           fc=fc, ec=ec, lw=lw, alpha=alpha, zorder=z)
        self.ax.add_patch(p)
        return p

    def glow_box(self, x, y, w, h, r, color, z=2):
        for lw, a in ((7, 0.05), (4, 0.10), (2, 0.22)):
            self.rbox(x, y, w, h, r, "none", ec=color, lw=lw, alpha=a, z=z)
        self.rbox(x, y, w, h, r, "none", ec=color, lw=0.8, alpha=0.75, z=z + 0.1)


def background(c):
    # subtle radial vignette + faint grid for depth
    import numpy as np
    yy, xx = np.mgrid[0:H, 0:W]
    d = np.sqrt(((xx - W * 0.5) / W) ** 2 + ((yy - H * 0.45) / H) ** 2)
    glow = np.clip(1 - d * 1.6, 0, 1) ** 2
    base = np.array([10, 17, 40]) / 255
    lift = np.array([22, 38, 84]) / 255
    img = base + (lift - base) * glow[..., None]
    c.ax.imshow(img, extent=(0, W, H, 0), zorder=0, interpolation="bilinear")
    for gx in range(0, W, 48):
        c.ax.plot([gx, gx], [0, H], color=CYAN, lw=0.15, alpha=0.05, zorder=0.5)
    for gy in range(0, H, 48):
        c.ax.plot([0, W], [gy, gy], color=CYAN, lw=0.15, alpha=0.05, zorder=0.5)


def header(c):
    c.text(56, 40, "TAKHT-I-BAHI AI DIGITAL TWIN", fp(44, "bold"), WHITE)
    c.text(56 + c.width("TAKHT-I-BAHI AI DIGITAL TWIN", fp(44, "bold")) + 18, 52,
           "—  SYSTEM ARCHITECTURE & TECH STACK", fp(28, "bold"), CYAN)
    c.text(58, 102, "From a 142 MB field scan to zero-install WebAR time travel through the "
                    "2nd-century Gandharan Stupa Court · UNESCO World Heritage, Mardan, KP",
           fp(18), MUTED)
    # gold accent rule
    c.ax.plot([58, 300], [138, 138], color=GOLD, lw=1.0, solid_capstyle="round", zorder=3)
    c.ax.plot([300, 560], [138, 138], color=CYAN, lw=0.6, alpha=0.6, solid_capstyle="round", zorder=3)

    # KPITB challenge badge (top right)
    bw, bh, bx, by = 292, 82, W - 56 - 292, 34
    c.rbox(bx, by, bw, bh, 18, TEAL, z=3)
    c.rbox(bx, by, bw, bh, 18, "none", ec="#7df3e1", lw=0.8, alpha=0.8, z=3.1)
    c.rbox(bx + 12, by + 14, 98, bh - 28, 12, "#0c5e70", z=3.2)
    c.text(bx + 61, by + bh / 2, "KPITB", fp(25, "bold"), WHITE, ha="center", va="center", zorder=4)
    c.text(bx + 124, by + 20, "AI CHALLENGE", fp(19, "bold"), WHITE, zorder=4)
    c.text(bx + 124, by + 46, "2026  ·  Digital Heritage", fp(15), "#d9fff7", zorder=4)


def stage_card(c, i, x, y, w, h, st):
    c.rbox(x, y, w, h, 22, CARD, alpha=0.92, z=2)
    c.glow_box(x, y, w, h, 22, CYAN if i % 2 == 0 else GOLD)

    # header band
    hb = 96
    c.rbox(x + 1, y + 1, w - 2, hb, 21, CARD_HEAD, z=2.5)
    c.rbox(x + 1, y + hb - 22, w - 2, 22, 0, CARD_HEAD, z=2.5)       # square off lower corners
    c.ax.plot([x + 18, x + w - 18], [y + hb, y + hb], color=CYAN, lw=0.5, alpha=0.5, zorder=3)

    # numbered disc
    cx, cy = x + 44, y + 48
    c.ax.add_patch(Circle((cx, cy), 27, fc=GOLD, ec="none", zorder=3))
    c.ax.add_patch(Circle((cx, cy), 33, fc="none", ec=GOLD, lw=0.5, alpha=0.5, zorder=3))
    c.text(cx, cy + 1, str(i + 1), fp(28, "bold"), NAVY, ha="center", va="center", zorder=4)

    tx = x + 86
    title_lines = c.wrap(st["title"], fp(19, "bold"), w - 100)
    ty = y + (24 if len(title_lines) == 1 else 14)
    for ln in title_lines:
        c.text(tx, ty, ln, fp(19, "bold"), WHITE, zorder=4)
        ty += 24
    c.text(tx, ty + 4, st["sub"], fp(15, family=MONO if st.get("mono_sub") else SANS),
           CYAN, zorder=4)

    # items
    yy = y + hb + 26
    inner = w - 56
    for head, detail in st["items"]:
        c.ax.add_patch(Circle((x + 26, yy + 13), 5, fc=CYAN if i % 2 == 0 else GOLD,
                              ec="none", zorder=4))
        c.text(x + 40, yy, head, fp(21, "bold"), GOLD if i % 2 == 0 else CYAN, zorder=4)
        yy += 32
        for ln in c.wrap(detail, fp(18.5), inner):
            c.text(x + 40, yy, ln, fp(18.5), "#e6ecf8", zorder=4)
            yy += 26
        yy += 22

    # tech chips (bottom-aligned, wrapping)
    chip_font = fp(14, "bold", MONO)
    pad, ch, gap = 11, 30, 8
    rows, row, row_w = [], [], 0
    for t in st["chips"]:
        cw = c.width(t, chip_font) + 2 * pad
        if row and row_w + gap + cw > w - 36:
            rows.append(row)
            row, row_w = [], 0
        row.append((t, cw))
        row_w += cw + (gap if row_w else 0)
    rows.append(row)
    cy0 = y + h - 22 - len(rows) * (ch + gap) + gap
    c.ax.plot([x + 18, x + w - 18], [cy0 - 16, cy0 - 16], color=WHITE, lw=0.3, alpha=0.15, zorder=3)
    for r_i, row in enumerate(rows):
        cx0 = x + 18
        for t, cw in row:
            ry = cy0 + r_i * (ch + gap)
            c.rbox(cx0, ry, cw, ch, 15, "#0a2a46", ec=CYAN, lw=0.4, alpha=1, z=3)
            c.text(cx0 + cw / 2, ry + ch / 2 + 1, t, chip_font, "#bff3ff", ha="center", va="center", zorder=4)
            cx0 += cw + gap
    return yy


def arrow(c, x0, x1, y):
    for lw, a in ((5, 0.08), (2.5, 0.18)):
        c.ax.plot([x0, x1 - 6], [y, y], color=CYAN, lw=lw, alpha=a, solid_capstyle="round", zorder=3)
    c.ax.add_patch(FancyArrowPatch((x0, y), (x1, y), arrowstyle="-|>,head_length=4,head_width=2.6",
                                   color=CYAN, lw=1.1, zorder=4, mutation_scale=1))


def footer(c, y0):
    # metrics strip
    n = len(METRICS)
    x0, x1 = 56, W - 56
    sw = (x1 - x0) / n
    c.rbox(x0, y0, x1 - x0, 86, 18, "#0d1838", ec=GOLD, lw=0.5, alpha=1, z=2)
    for k, (num, label) in enumerate(METRICS):
        cx = x0 + sw * k + sw / 2
        nw, lw_ = c.width(num, fp(36, "bold")), c.width(label, fp(18))
        sx0 = cx - (nw + 12 + lw_) / 2                     # centre number + label as a group
        c.text(sx0, y0 + 43, num, fp(36, "bold"), GOLD, ha="left", va="center", zorder=4)
        c.text(sx0 + nw + 12, y0 + 45, label, fp(18), WHITE, ha="left", va="center", zorder=4)
        if k:
            sx = x0 + sw * k
            c.ax.plot([sx, sx], [y0 + 20, y0 + 66], color=WHITE, lw=0.4, alpha=0.2, zorder=3)
    c.text(W / 2, H - 22, "danyal-yousafzai.github.io/takht-i-bahi-digital-twin  ·  "
                          "Takht-i-Bahi AI Digital Twin | KPITB 2026",
           fp(15), MUTED, ha="center", va="bottom")


def main():
    c = Canvas()
    background(c)
    header(c)

    n = len(STAGES)
    left, right, top = 56, W - 56, 178
    gap = 46
    cw = (right - left - gap * (n - 1)) / n
    ch = 716
    for i, st in enumerate(STAGES):
        x = left + i * (cw + gap)
        end = stage_card(c, i, x, top, cw, ch, st)
        if end > top + ch - 120:
            print(f"warning: stage {i + 1} text runs close to its chips ({end:.0f}px)")
        if i < n - 1:
            arrow(c, x + cw + 7, x + cw + gap - 7, top + ch / 2)
    footer(c, top + ch + 22)

    os.makedirs(os.path.dirname(OUTPUTS[1]), exist_ok=True)
    c.fig.savefig(OUTPUTS[1], dpi=DPI, facecolor=NAVY)
    plt.close(c.fig)

    # verify size, stamp 300 DPI metadata, copy to the Desktop
    im = Image.open(OUTPUTS[1]).convert("RGB")
    assert im.size == (W, H), im.size
    for path in OUTPUTS:
        im.save(path, dpi=(DPI, DPI), optimize=True)
        print(f"saved {path}  {im.size[0]}x{im.size[1]} @ {DPI} dpi  "
              f"({os.path.getsize(path) / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
