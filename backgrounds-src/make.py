#!/usr/bin/env python3
"""Generate the Aperture 1976 wallpapers as SVG (3840x2400).

Render with ./render.sh. Everything here is drawn from scratch; colours come
from ../colors.toml.
"""
import math
import os
import random

W, H = 3840, 2400
CX, CY = W / 2, H / 2
HERE = os.path.dirname(os.path.abspath(__file__))

WALNUT = "#2a211a"
WALNUT_DK = "#211a14"
WALNUT_DKR = "#18130e"
WALNUT_LT = "#3a2e24"
CREAM = "#e8dcc0"
CREAM_LT = "#f6eedb"
CREAM_DK = "#9c8b70"
BROWN = "#7a4a2a"
ORANGE = "#e0782a"
BLUE = "#4a9bb5"
MUSTARD = "#d4a13a"
AVOCADO = "#8a9a3b"
BRICK = "#dd6a50"
FONT = "Liberation Sans, Adwaita Sans, sans-serif"
MONO = "Liberation Mono, monospace"


def svg(body, defs=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}">\n<defs>{defs}</defs>\n{body}\n</svg>\n'
    )


def grain(id_, freq, opacity, seed=3):
    """Film/paper grain overlay filter."""
    return (
        f'<filter id="{id_}" x="0" y="0" width="100%" height="100%">'
        f'<feTurbulence type="fractalNoise" baseFrequency="{freq}" numOctaves="3" seed="{seed}"/>'
        f'<feColorMatrix type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 {opacity} 0"/>'
        f'</filter>'
    )


def aperture_logo(cx, cy, r, fg, bg, blades=8, gap=None, hole=0.42, rot=-22.5):
    """The aperture iris: a disc split into blades around a polygonal hole.

    Each blade edge starts at a vertex of the inner polygon and runs along
    the extension of the polygon side until it meets the outer circle.
    """
    gap = gap or r * 0.075
    ri = r * hole
    out = [f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fg}"/>']
    verts = []
    for i in range(blades):
        a = math.radians(rot + i * 360 / blades)
        verts.append((cx + ri * math.cos(a), cy + ri * math.sin(a)))
    for i in range(blades):
        x0, y0 = verts[i]
        x1, y1 = verts[(i + 1) % blades]
        dx, dy = x1 - x0, y1 - y0
        n = math.hypot(dx, dy)
        dx, dy = dx / n, dy / n
        # Solve |p0 + t*d - c| = r for the forward intersection.
        px, py = x0 - cx, y0 - cy
        b = px * dx + py * dy
        c = px * px + py * py - r * r
        t = -b + math.sqrt(b * b - c)
        ex, ey = x0 + dx * (t + gap), y0 + dy * (t + gap)
        out.append(
            f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{ex:.1f}" y2="{ey:.1f}" '
            f'stroke="{bg}" stroke-width="{gap:.1f}" stroke-linecap="butt"/>'
        )
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in verts)
    out.append(f'<polygon points="{pts}" fill="{bg}"/>')
    return "\n".join(out)


def walnut_panels(rng, x0=0, x1=W, y0=0, y1=H, plank=256):
    out = [f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="{WALNUT}"/>']
    x = x0
    while x < x1:
        w = plank + rng.randint(-30, 30)
        shade = rng.choice([WALNUT, WALNUT, "#2e241c", "#271f18"])
        out.append(f'<rect x="{x}" y="{y0}" width="{w}" height="{y1 - y0}" fill="{shade}"/>')
        # Grain: long wavering strokes along the plank.
        for _ in range(14):
            gx = x + rng.uniform(8, w - 8)
            pts = []
            for yy in range(y0, y1 + 1, 120):
                gx += rng.uniform(-6, 6)
                pts.append(f"{gx:.1f},{yy}")
            col = rng.choice([WALNUT_LT, WALNUT_DK, "#33281f"])
            out.append(
                f'<polyline points="{" ".join(pts)}" fill="none" stroke="{col}" '
                f'stroke-width="{rng.uniform(1.5, 5):.1f}" opacity="{rng.uniform(0.35, 0.8):.2f}"/>'
            )
        # Groove between planks.
        out.append(f'<rect x="{x + w - 6}" y="{y0}" width="6" height="{y1 - y0}" fill="{WALNUT_DKR}"/>')
        out.append(f'<rect x="{x + w}" y="{y0}" width="2" height="{y1 - y0}" fill="#3d3026" opacity="0.6"/>')
        x += w
    return "\n".join(out)


def chip(rng, cx, cy, size):
    """An irregular enamel chip exposing dark steel."""
    pts = []
    n = rng.randint(7, 11)
    for i in range(n):
        a = 2 * math.pi * i / n + rng.uniform(-0.2, 0.2)
        rr = size * rng.uniform(0.5, 1.0)
        pts.append(f"{cx + rr * math.cos(a):.1f},{cy + rr * math.sin(a):.1f}")
    p = " ".join(pts)
    return (
        f'<polygon points="{p}" fill="#3b3833" stroke="{CREAM_DK}" stroke-width="3" opacity="0.95"/>'
    )


# --------------------------------------------------------------------------
# 1. Enamel plate (default wallpaper, sits behind the lock card)
# --------------------------------------------------------------------------
def enamel_plate():
    rng = random.Random(1976)
    pw, ph = 2080, 1440
    px, py = CX - pw / 2, CY - 820
    defs = grain("grain", 0.9, 0.10) + (
        f'<linearGradient id="enamel" x1="0" y1="0" x2="0.35" y2="1">'
        f'<stop offset="0" stop-color="{CREAM_LT}"/><stop offset="1" stop-color="#ddcfaf"/></linearGradient>'
        f'<radialGradient id="vignette" cx="0.5" cy="0.5" r="0.75">'
        f'<stop offset="0.55" stop-color="#000" stop-opacity="0"/>'
        f'<stop offset="1" stop-color="#000" stop-opacity="0.55"/></radialGradient>'
        f'<filter id="shadow" x="-10%" y="-10%" width="120%" height="130%">'
        f'<feGaussianBlur in="SourceAlpha" stdDeviation="28"/><feOffset dy="26"/>'
        f'<feComponentTransfer><feFuncA type="linear" slope="0.6"/></feComponentTransfer>'
        f'<feMerge><feMergeNode/><feMergeNode in="SourceGraphic"/></feMerge></filter>'
        f'<linearGradient id="brass" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="#e6c27a"/><stop offset="1" stop-color="#8a6a2e"/></linearGradient>'
    )
    b = [walnut_panels(rng)]

    plate = []
    # Steel backing, brown enamel border band, cream field.
    plate.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="60" fill="#4a463f"/>')
    plate.append(f'<rect x="{px + 10}" y="{py + 10}" width="{pw - 20}" height="{ph - 20}" rx="52" fill="{BROWN}"/>')
    plate.append(f'<rect x="{px + 58}" y="{py + 58}" width="{pw - 116}" height="{ph - 116}" rx="30" fill="url(#enamel)"/>')
    plate.append(
        f'<rect x="{px + 78}" y="{py + 78}" width="{pw - 156}" height="{ph - 156}" rx="18" '
        f'fill="none" stroke="{BROWN}" stroke-width="6"/>'
    )

    # Header: logo + wordmark.
    lx, ly, lr = px + 360, py + 300, 170
    plate.append(aperture_logo(lx, ly, lr, WALNUT, CREAM_LT))
    tx = lx + lr + 90
    plate.append(
        f'<text x="{tx}" y="{ly + 30}" font-family="{FONT}" font-weight="bold" font-size="196" '
        f'letter-spacing="10" fill="{WALNUT}">APERTURE</text>'
    )
    plate.append(
        f'<text x="{tx + 6}" y="{ly + 140}" font-family="{FONT}" font-size="76" '
        f'letter-spacing="31" fill="{BROWN}">LABORATORIES</text>'
    )

    # Divider with the gel colours.
    dy = py + 540
    plate.append(f'<rect x="{px + 140}" y="{dy}" width="{pw - 280}" height="14" fill="{BLUE}"/>')
    plate.append(f'<rect x="{px + 140}" y="{dy + 22}" width="{pw - 280}" height="14" fill="{ORANGE}"/>')

    # The blank authentication field the lock card lands on (screen centre).
    fw, fh = 960, 170
    fx, fy = CX - fw / 2, CY - fh / 2
    plate.append(
        f'<text x="{CX}" y="{fy - 40}" text-anchor="middle" font-family="{FONT}" font-weight="bold" '
        f'font-size="44" letter-spacing="14" fill="{WALNUT}">EMPLOYEE AUTHENTICATION</text>'
    )
    plate.append(f'<rect x="{fx - 8}" y="{fy - 8}" width="{fw + 16}" height="{fh + 16}" rx="16" fill="{BROWN}"/>')
    plate.append(f'<rect x="{fx}" y="{fy}" width="{fw}" height="{fh}" rx="10" fill="{WALNUT_DK}"/>')
    plate.append(f'<rect x="{fx}" y="{fy}" width="{fw}" height="14" rx="7" fill="#000" opacity="0.35"/>')

    # Footer copy.
    fy2 = py + ph - 200
    plate.append(
        f'<text x="{CX}" y="{fy2}" text-anchor="middle" font-family="{FONT}" font-size="40" '
        f'letter-spacing="9" fill="{BROWN}">AUTHORIZED PERSONNEL AND TEST SUBJECTS ONLY</text>'
    )
    plate.append(
        f'<text x="{CX}" y="{fy2 + 70}" text-anchor="middle" font-family="{FONT}" font-size="34" '
        f'letter-spacing="8" fill="{CREAM_DK}">FACILITY PLATE No. 1976  ·  DO NOT REMOVE  ·  DO NOT LICK</text>'
    )

    # Brass screws.
    for sx, sy in [(px + 34, py + 34), (px + pw - 34, py + 34), (px + 34, py + ph - 34), (px + pw - 34, py + ph - 34)]:
        a = rng.uniform(0, math.pi)
        plate.append(f'<circle cx="{sx}" cy="{sy}" r="22" fill="url(#brass)" stroke="#5a4520" stroke-width="3"/>')
        plate.append(
            f'<line x1="{sx - 15 * math.cos(a):.1f}" y1="{sy - 15 * math.sin(a):.1f}" '
            f'x2="{sx + 15 * math.cos(a):.1f}" y2="{sy + 15 * math.sin(a):.1f}" stroke="#4a3818" stroke-width="5"/>'
        )

    # Chips along the edges, a few strays on the field.
    for _ in range(14):
        side = rng.choice("tblr")
        if side in "tb":
            x = rng.uniform(px + 90, px + pw - 90)
            y = py + rng.uniform(8, 70) if side == "t" else py + ph - rng.uniform(8, 70)
        else:
            y = rng.uniform(py + 90, py + ph - 90)
            x = px + rng.uniform(8, 70) if side == "l" else px + pw - rng.uniform(8, 70)
        plate.append(chip(rng, x, y, rng.uniform(10, 34)))
    for x, y, s in [(px + pw - 200, py + 150, 18), (px + 200, py + ph - 330, 12), (px + pw - 230, py + ph - 330, 15)]:
        plate.append(chip(rng, x, y, s))

    defs += f'<clipPath id="plateclip"><rect x="{px}" y="{py}" width="{pw}" height="{ph}" rx="60"/></clipPath>'
    b.append(f'<g filter="url(#shadow)"><g clip-path="url(#plateclip)">{"".join(plate)}</g></g>')
    b.append(f'<rect width="{W}" height="{H}" fill="url(#vignette)"/>')
    b.append(f'<rect width="{W}" height="{H}" filter="url(#grain)"/>')
    return svg("\n".join(b), defs)


# --------------------------------------------------------------------------
# 2. Gel test chamber blueprint
# --------------------------------------------------------------------------
def gel_blueprint():
    rng = random.Random(7)
    PAPER = "#1d2f35"
    INK = "#a9c9d2"
    defs = grain("grain", 0.75, 0.13, seed=9) + (
        f'<radialGradient id="fade" cx="0.45" cy="0.45" r="0.8">'
        f'<stop offset="0" stop-color="#2a4048"/><stop offset="1" stop-color="#14232a"/></radialGradient>'
        f'<pattern id="grid" width="80" height="80" patternUnits="userSpaceOnUse">'
        f'<path d="M80 0H0V80" fill="none" stroke="{INK}" stroke-width="1" opacity="0.13"/></pattern>'
        f'<pattern id="grid5" width="400" height="400" patternUnits="userSpaceOnUse">'
        f'<path d="M400 0H0V400" fill="none" stroke="{INK}" stroke-width="2" opacity="0.18"/></pattern>'
        f'<pattern id="hatch" width="24" height="24" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
        f'<line x1="0" y1="0" x2="0" y2="24" stroke="{INK}" stroke-width="3" opacity="0.55"/></pattern>'
    )
    b = [
        f'<rect width="{W}" height="{H}" fill="{PAPER}"/>',
        f'<rect width="{W}" height="{H}" fill="url(#fade)"/>',
        f'<rect width="{W}" height="{H}" fill="url(#grid)"/>',
        f'<rect width="{W}" height="{H}" fill="url(#grid5)"/>',
    ]
    s = f'stroke="{INK}" fill="none"'
    sk = f'stroke="{INK}"'

    # Chamber section: walls hatched, interior open.
    x0, y0, x1, y1 = 560, 560, 2960, 1880
    wall = 70
    b.append(f'<path d="M{x0 - wall} {y0 - wall}H{x1 + wall}V{y1 + wall}H{x0 - wall}Z M{x0} {y0}V{y1}H{x1}V{y0}Z" fill="url(#hatch)" fill-rule="evenodd"/>')
    b.append(f'<rect x="{x0 - wall}" y="{y0 - wall}" width="{x1 - x0 + 2 * wall}" height="{y1 - y0 + 2 * wall}" {s} stroke-width="5"/>')
    b.append(f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" {s} stroke-width="4"/>')

    # Interior panel grid (the familiar test-chamber tiling).
    for gx in range(x0 + 300, x1, 300):
        b.append(f'<line x1="{gx}" y1="{y0}" x2="{gx}" y2="{y1}" stroke="{INK}" stroke-width="1.5" opacity="0.3" stroke-dasharray="14 10"/>')
    for gy in range(y0 + 300, y1, 300):
        b.append(f'<line x1="{x0}" y1="{gy}" x2="{x1}" y2="{gy}" stroke="{INK}" stroke-width="1.5" opacity="0.3" stroke-dasharray="14 10"/>')

    # Raised platform on the right, step on the left.
    b.append(f'<rect x="2280" y="1480" width="680" height="400" fill="#1d2f35" {sk} stroke-width="4"/>')
    b.append(f'<rect x="2280" y="1480" width="680" height="400" fill="url(#hatch)" opacity="0.5"/>')

    # Gel pipes from the ceiling.
    def pipe(x, color, length, label):
        out = [
            f'<rect x="{x - 46}" y="{y0 - wall - 90}" width="92" height="{90 + wall + length}" fill="{color}" opacity="0.85"/>',
            f'<rect x="{x - 46}" y="{y0 - wall - 90}" width="92" height="{90 + wall + length}" {s} stroke-width="4"/>',
            f'<rect x="{x - 70}" y="{y0 + length - 30}" width="140" height="50" fill="#1d2f35" {sk} stroke-width="4"/>',
            f'<text x="{x + 80}" y="{y0 - wall - 30}" font-family="{MONO}" font-size="40" fill="{INK}">{label}</text>',
        ]
        return out

    b += pipe(1000, BLUE, 220, "REPULSION · R-7")
    b += pipe(1750, ORANGE, 160, "PROPULSION · P-3")

    # Falling blobs.
    for i in range(6):
        y = y0 + 300 + i * 150 + rng.uniform(-20, 20)
        r = 26 - i * 1.5
        b.append(f'<ellipse cx="{1000 + rng.uniform(-8, 8):.1f}" cy="{y:.1f}" rx="{r:.1f}" ry="{r * 1.3:.1f}" fill="{BLUE}" opacity="0.9"/>')
    for i in range(8):
        y = y0 + 240 + i * 130 + rng.uniform(-20, 20)
        r = 24 - i * 1.2
        b.append(f'<ellipse cx="{1750 + rng.uniform(-8, 8):.1f}" cy="{y:.1f}" rx="{r:.1f}" ry="{r * 1.3:.1f}" fill="{ORANGE}" opacity="0.9"/>')

    # Gel coatings on the floor.
    b.append(f'<path d="M760 {y1} Q 1000 {y1 - 34} 1240 {y1} Z" fill="{BLUE}"/>')
    b.append(f'<rect x="1500" y="{y1 - 16}" width="760" height="16" fill="{ORANGE}"/>')

    # A cube, mid-flight, with its trajectory.
    b.append(f'<path d="M1060 {y1 - 40} Q 2360 300 2420 1400" {s} stroke-width="3" stroke-dasharray="20 14"/>')
    b.append(f'<g transform="translate(2050 960) rotate(18)">'
             f'<rect x="-80" y="-80" width="160" height="160" fill="#1d2f35" {sk} stroke-width="5"/>'
             f'<circle r="34" {s} stroke-width="4"/><rect x="-80" y="-80" width="36" height="36" {s} stroke-width="3"/>'
             f'<rect x="44" y="-80" width="36" height="36" {s} stroke-width="3"/>'
             f'<rect x="-80" y="44" width="36" height="36" {s} stroke-width="3"/>'
             f'<rect x="44" y="44" width="36" height="36" {s} stroke-width="3"/></g>')

    # Dimension lines.
    def dim_h(xa, xb, y, text):
        return [
            f'<line x1="{xa}" y1="{y}" x2="{xb}" y2="{y}" {s} stroke-width="2.5"/>',
            f'<line x1="{xa}" y1="{y - 24}" x2="{xa}" y2="{y + 24}" {s} stroke-width="2.5"/>',
            f'<line x1="{xb}" y1="{y - 24}" x2="{xb}" y2="{y + 24}" {s} stroke-width="2.5"/>',
            f'<text x="{(xa + xb) / 2}" y="{y - 18}" text-anchor="middle" font-family="{MONO}" font-size="36" fill="{INK}">{text}</text>',
        ]

    def dim_v(ya, yb, x, text):
        return [
            f'<line x1="{x}" y1="{ya}" x2="{x}" y2="{yb}" {s} stroke-width="2.5"/>',
            f'<line x1="{x - 24}" y1="{ya}" x2="{x + 24}" y2="{ya}" {s} stroke-width="2.5"/>',
            f'<line x1="{x - 24}" y1="{yb}" x2="{x + 24}" y2="{yb}" {s} stroke-width="2.5"/>',
            f'<text transform="translate({x - 22} {(ya + yb) / 2}) rotate(-90)" text-anchor="middle" font-family="{MONO}" font-size="36" fill="{INK}">{text}</text>',
        ]

    b += dim_h(x0, x1, y1 + wall + 110, "24'-0\"")
    b += dim_v(y0, y1, x0 - wall - 110, "13'-2\"")
    b += dim_h(2280, 2960, 1400, "6'-10\"")

    # Callouts.
    for (ax, ay, tx, ty, t) in [
        (1000, y1 - 20, 640, 2170, "A  REPULSION GEL, FLOOR COAT (BOUNCE)"),
        (1750, y1 - 8, 1500, 2240, "B  PROPULSION GEL, RUNWAY (SPEED)"),
        (2050, 960, 2250, 700, "C  STORAGE CUBE, IN TRANSIT"),
    ]:
        b.append(f'<line x1="{ax}" y1="{ay}" x2="{tx}" y2="{ty - 40}" {s} stroke-width="2"/>')
        b.append(f'<circle cx="{ax}" cy="{ay}" r="9" fill="{INK}"/>')
        b.append(f'<text x="{tx}" y="{ty}" font-family="{MONO}" font-size="38" fill="{INK}">{t}</text>')

    # Title block.
    bx, by, bw, bh = 3080, 1640, 680, 680
    b.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" {s} stroke-width="5"/>')
    for yy in (by + 260, by + 380, by + 480, by + 580):
        b.append(f'<line x1="{bx}" y1="{yy}" x2="{bx + bw}" y2="{yy}" {s} stroke-width="3"/>')
    b.append(aperture_logo(bx + 140, by + 130, 90, INK, "#1f343b"))
    b.append(f'<text x="{bx + 260}" y="{by + 120}" font-family="{FONT}" font-weight="bold" font-size="62" letter-spacing="4" fill="{INK}">APERTURE</text>')
    b.append(f'<text x="{bx + 262}" y="{by + 180}" font-family="{FONT}" font-size="31" letter-spacing="10" fill="{INK}">LABORATORIES</text>')
    rows = [
        ("CHAMBER 07 · GEL DELIVERY", by + 335),
        ("SECTION A–A   SCALE 1:48", by + 445),
        ("DRAWN  C.J.  1976-03-14", by + 545),
        ("SHEET 4 OF 11   REV. C", by + 645),
    ]
    for t, yy in rows:
        b.append(f'<text x="{bx + 36}" y="{yy}" font-family="{MONO}" font-size="38" fill="{INK}">{t}</text>')

    # Header note, top left.
    b.append(f'<text x="560" y="200" font-family="{FONT}" font-weight="bold" font-size="64" letter-spacing="12" fill="{INK}">GEL DISTRIBUTION · CROSS SECTION</text>')
    b.append(f'<text x="560" y="262" font-family="{MONO}" font-size="36" fill="{INK}" opacity="0.8">NOTE: SUBJECTS ARE NOT TO INGEST GEL. SUBJECTS ARE NOT TO BE INGESTED BY GEL.</text>')

    b.append(f'<rect width="{W}" height="{H}" filter="url(#grain)"/>')
    return svg("\n".join(b), defs)


# --------------------------------------------------------------------------
# 3. 1970s employee brochure
# --------------------------------------------------------------------------
def brochure():
    defs = grain("grain", 0.85, 0.11, seed=21) + (
        f'<pattern id="dots" width="36" height="36" patternUnits="userSpaceOnUse" patternTransform="rotate(30)">'
        f'<circle cx="18" cy="18" r="7" fill="{CREAM}" opacity="0.10"/></pattern>'
        f'<radialGradient id="dotmask" cx="0.85" cy="0.15" r="0.55">'
        f'<stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#000"/></radialGradient>'
        f'<mask id="dm"><rect width="{W}" height="{H}" fill="url(#dotmask)"/></mask>'
    )
    b = [f'<rect width="{W}" height="{H}" fill="{WALNUT}"/>']
    b.append(f'<rect width="{W}" height="{H}" fill="url(#dots)" mask="url(#dm)"/>')

    # Racing stripes: run in from the left, bend up around a rounded corner.
    stripes = [BROWN, BRICK, ORANGE, MUSTARD, BLUE]
    sw = 120
    corner_x = 2760
    base_y = 2080
    R = 520
    for i, col in enumerate(stripes):
        off = i * sw
        y = base_y - off
        r = R - off
        x = corner_x + (len(stripes) - 1 - i) * 0
        # Centre line of the stripe: horizontal to corner, quarter arc, then up.
        cx_, cy_ = corner_x, base_y - R
        d = (
            f"M -20 {y} H {cx_} "
            f"A {r} {r} 0 0 0 {cx_ + r} {cy_} V -20"
        )
        b.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{sw + 1}"/>')

    # Copy block, upper left.
    lx, ly = 300, 360
    b.append(aperture_logo(lx + 130, ly + 130, 130, CREAM, WALNUT))
    b.append(f'<text x="{lx + 320}" y="{ly + 140}" font-family="{FONT}" font-weight="bold" font-size="120" letter-spacing="6" fill="{CREAM}">APERTURE</text>')
    b.append(f'<text x="{lx + 324}" y="{ly + 220}" font-family="{FONT}" font-size="48" letter-spacing="19" fill="{CREAM_DK}">LABORATORIES</text>')

    b.append(f'<text x="{lx}" y="{ly + 520}" font-family="{FONT}" font-weight="bold" font-size="150" fill="{CREAM}">Science you</text>')
    b.append(f'<text x="{lx}" y="{ly + 680}" font-family="{FONT}" font-weight="bold" font-size="150" fill="{ORANGE}">can stand on.</text>')
    b.append(
        f'<text x="{lx + 6}" y="{ly + 800}" font-family="{FONT}" font-size="46" letter-spacing="3" fill="{CREAM_DK}">'
        f'Propulsion. Repulsion. Progress.</text>'
    )
    lines = [
        "Welcome to the Aperture family. In this brochure you will",
        "find everything you need to know about your new position,",
        "except the parts you are not cleared for.",
    ]
    for i, t in enumerate(lines):
        b.append(f'<text x="{lx + 6}" y="{ly + 920 + i * 62}" font-family="{FONT}" font-size="40" fill="{CREAM}" opacity="0.75">{t}</text>')

    # Footer strip.
    b.append(
        f'<text x="{lx + 6}" y="{H - 70}" font-family="{FONT}" font-size="32" letter-spacing="8" fill="{CREAM_DK}">'
        f'EMPLOYEE ORIENTATION SERIES · VOL. 3 · 1976</text>'
    )
    b.append(f'<rect width="{W}" height="{H}" filter="url(#grain)"/>')
    return svg("\n".join(b), defs)


if __name__ == "__main__":
    for name, fn in [("1-enamel-plate", enamel_plate), ("2-gel-blueprint", gel_blueprint), ("3-brochure", brochure)]:
        with open(os.path.join(HERE, f"{name}.svg"), "w") as f:
            f.write(fn())
        print(name)
