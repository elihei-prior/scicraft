#!/usr/bin/env python3
"""Generate the unit sphere of an embedding space as TikZ: clusters, density rings, and the composition of two
sets' resultants drawn to scale, with the checks the drawing has to pass.

What it draws (orthographic view, radius R cm, view elevation EL degrees):
  * a white ball with a hairline graticule (meridians every 30 degrees, parallels from -60 to 60 degrees) and a
    faint radial shading;
  * clusters of unit vectors sampled from von Mises-Fisher distributions, three groups in the three point hues,
    subclusters as shades of their group's hue; density rings at cap masses 0.50 and 0.85; bridges of mixed points
    between clusters of a group;
  * two sets A1 and A2 (two clusters) and their union A: the resultants S(A1) and S(A2) drawn at the common scale
    1/n_A, closed by a dashed parallelogram onto S(A)/n_A, whose length is exactly the mean resultant length R_A;
    a dashed radial projection from that tip out to the mean direction mu(A) on the sphere; dashed ties from each
    set's resultant to its own mean direction; the geodesic between the two mean directions.

The pair is chosen by the one quantity the drawing must make legible: R_A in [0.62, 0.78] (a tight pair with
R_A near 0.92 leaves a gap of 8 percent of the radius, foreshortened further by the projection), every drawn
direction 37 to 66 degrees off the view axis (an arrow toward the camera projects short), and the union's
direction away from every cluster center.

Checks the generator runs on itself (exit 1 if one fails): S(A) equals S(A1) + S(A2); the drawn parallelogram
closes in the PROJECTED plane; the drawn diagonal has length R_A; the projection is radial; the angles add up.

--glyph writes the small sphere glyph of an overview instead: graticule clipped to the disk, no outline, three soft
blobs (16 concentric fills each) at the projected positions of three directions.

Notation is the textbook one of directional statistics: S(A) the resultant, R_A = |S(A)|/n_A the mean resultant
length, mu(A) = S(A)/|S(A)| the mean direction.

Needs numpy and scipy. Writes OUT/sphere.tex (or sphere_glyph.tex) and OUT/facts.json.

Usage:
    python3 sphere.py --out sphere/ --preamble ../assets/preamble.tex
    python3 sphere.py --out frag/ --glyph
"""
from __future__ import annotations

import argparse
import json
import sys
sys.dont_write_bytecode = True        # importing a sibling must not leave __pycache__ in the skill
from pathlib import Path

import numpy as np
from scipy.optimize import brentq

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "assets"))
import figkit  # noqa: E402

HUES = {"ptblue": (0x5C, 0x8C, 0xC4), "ptochre": (0xC9, 0x8F, 0x3D), "ptpurple": (0x94, 0x75, 0xB5)}
LV = (0.50, 0.85)          # cap masses of the two density rings
HALO = "fill=white, inner sep=0.8pt"   # labels inside the ball sit on a white backdrop over the hairlines


class View:
    """Orthographic projection onto the screen plane at elevation `el` degrees, radius R (cm)."""

    def __init__(self, R: float, el: float):
        e = np.radians(el)
        self.R = R
        self.C = np.array([np.cos(e), 0.0, np.sin(e)])                 # toward the viewer
        er = np.cross([0, 0, 1.0], self.C)
        self.ER = er / np.linalg.norm(er)
        self.EU = np.cross(self.C, self.ER)

    def P(self, p):
        return (self.R * p @ self.ER, self.R * p @ self.EU)

    def vis(self, p):
        return p @ self.C > 1e-4

    def roll(self, d):
        """Rotate the screen axes so direction d projects to the positive x axis (frames the fan)."""
        a = np.arctan2(d @ self.EU, d @ self.ER)
        self.ER, self.EU = (np.cos(a) * self.ER + np.sin(a) * self.EU, -np.sin(a) * self.ER + np.cos(a) * self.EU)


def frame(m, C, EU):
    a = np.cross(m, C)
    if np.linalg.norm(a) < 1e-6:
        a = np.cross(m, EU)
    a /= np.linalg.norm(a)
    return a, np.cross(m, a)


def vmf_sample(m, kap, rng, C, EU):
    a, b = frame(m, C, EU)
    u = rng.random()
    w = 1 + np.log(u + (1 - u) * np.exp(-2 * kap)) / kap
    t = rng.random() * 2 * np.pi
    return w * m + np.sqrt(max(0.0, 1 - w * w)) * (np.cos(t) * a + np.sin(t) * b)


def slerp(a, b, t):
    w = np.arccos(np.clip(a @ b, -1, 1))
    return (np.sin((1 - t) * w) * a + np.sin(t * w) * b) / np.sin(w) if w > 1e-6 else a


def ring(m, a, b, th, n=161):
    return [np.cos(th) * m + np.sin(th) * (np.cos(u) * a + np.sin(u) * b) for u in np.linspace(0, 2 * np.pi, n)]


def runs(v: View, pts):
    out, cur = [], []
    for p in pts:
        if v.vis(p):
            cur.append(v.P(p))
        elif cur:
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    return out


def path(xy):
    return " -- ".join(f"({x:.3f},{y:.3f})" for x, y in xy)


def graticule(v: View, style: str):
    o = []
    for lo in np.arange(0, 360, 30):
        L = np.radians(lo)
        for sg in runs(v, [np.array([np.sin(np.pi * s) * np.cos(L), np.sin(np.pi * s) * np.sin(L), np.cos(np.pi * s)])
                           for s in np.linspace(0, 1, 201)]):
            if len(sg) > 1:
                o.append(f"\\draw[{style}] {path(sg)};\n")
    for la in np.arange(-60, 61, 30):
        B = np.radians(la)
        for sg in runs(v, [np.array([np.cos(B) * np.cos(t), np.cos(B) * np.sin(t), np.sin(B)])
                           for t in np.linspace(0, 2 * np.pi, 241)]):
            if len(sg) > 1:
                o.append(f"\\draw[{style}] {path(sg)};\n")
    return o


def shade(rgb, t):
    """Mix a hue toward white: t=1 is the hue, t=0 white."""
    return tuple(1 + t * (c / 255.0 - 1) for c in rgb)


def glyph(args) -> int:
    """The overview's sphere glyph: graticule clipped to the disk and three soft blobs."""
    v = View(args.radius, args.el)
    dirs = [(np.radians(28), np.radians(115)), (np.radians(40), np.radians(-55)), (np.radians(52), np.radians(-150))]
    o = [f"% sphere glyph, radius {args.radius} cm, written by sphere.py --glyph; place it in a shifted scope\n",
         "\\begin{scope}\n", f"\\clip (0,0) circle ({args.radius});\n"]
    o += graticule(v, "graticule, line width=0.32pt")
    blobs = []
    for (off, az), (name, rgb), r in zip(dirs, HUES.items(), (0.52, 0.46, 0.40)):
        m = np.cos(off) * v.C + np.sin(off) * (np.cos(az) * v.ER + np.sin(az) * v.EU)
        x, y = v.P(m / np.linalg.norm(m))
        rr = r * args.radius / 1.02
        for k in range(16):                                   # 16 concentric fills, white-ish to the soft hue
            t = 0.06 + 0.60 * k / 15
            c = shade(rgb, t)
            o.append(f"\\definecolor{{gly{name}{k}}}{{rgb}}{{{c[0]:.3f},{c[1]:.3f},{c[2]:.3f}}}"
                     f"\\fill[gly{name}{k}] ({x:.3f},{y:.3f}) circle ({rr * (1 - k / 16):.3f});\n")
        blobs.append({"hue": name, "center_cm": [round(x, 3), round(y, 3)], "radius_cm": round(rr, 3)})
    o.append("\\end{scope}\n")
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "sphere_glyph.tex").write_text("".join(o))
    (out / "facts_glyph.json").write_text(json.dumps({"radius_cm": args.radius, "elevation_deg": args.el,
                                                      "blobs": blobs}, indent=1) + "\n")
    print(f"ok  sphere glyph: radius {args.radius} cm, {len(blobs)} blobs -> {out / 'sphere_glyph.tex'}")
    return 0


def full(args) -> int:
    v = View(args.radius, args.el)
    R = args.radius
    rng = np.random.default_rng(args.seed)
    # three groups (one per point hue), subclusters as shades of the group's hue: (offset, azimuth), members
    # (shade t, kappa, n)
    G = [((0.62, 0.55), "ptochre", [(1.00, 150, 64), (0.70, 170, 46), (0.45, 210, 26)]),
         ((0.92, 2.98), "ptblue", [(1.00, 90, 72), (0.75, 200, 30), (0.45, 240, 14)]),
         ((0.88, 4.24), "ptpurple", [(1.00, 110, 58), (0.65, 230, 24)])]
    MU, COL, KAP, NN, GRP = [], [], [], [], []
    for gi, ((goff, gaz), hue, mem) in enumerate(G):
        gc = np.cos(goff) * v.C + np.sin(goff) * (np.cos(gaz) * v.ER + np.sin(gaz) * v.EU)
        gc /= np.linalg.norm(gc)
        a, b = frame(gc, v.C, v.EU)
        for t, (sh, kap, n) in enumerate(mem):
            ang = 2 * np.pi * t / len(mem) + 0.4 * gi
            sp = 0.30 if len(mem) > 2 else 0.20
            m = np.cos(sp) * gc + np.sin(sp) * (np.cos(ang) * a + np.sin(ang) * b)
            MU.append(m / np.linalg.norm(m))
            COL.append(tuple(c / 255.0 * sh + (1 - sh) * 0.15 for c in HUES[hue]))   # deeper shades, not paler
            KAP.append(kap)
            NN.append(n)
            GRP.append(gi)
    MEM = {i: [vmf_sample(MU[i], KAP[i], rng, v.C, v.EU) for _ in range(NN[i])] for i in range(len(MU))}

    # ---- choose the pair by R_A, the quantity the drawing has to make legible
    def pairs(gmin, vmin):
        out = []
        for i in range(len(MU)):
            for j in range(i + 1, len(MU)):
                if MU[i] @ v.C < vmin or MU[j] @ v.C < vmin or NN[i] < 20 or NN[j] < 20:
                    continue
                S1, S2 = sum(MEM[i]), sum(MEM[j])
                SA = S1 + S2
                RA = np.linalg.norm(SA) / (NN[i] + NN[j])
                if not (args.r_lo < RA < args.r_hi):
                    continue
                pa = SA / np.linalg.norm(SA)
                gp = min(np.degrees(np.arccos(np.clip(pa @ m, -1, 1))) for m in MU)
                if gp < gmin:
                    continue
                if not all(0.40 < d @ v.C < 0.80 for d in (S1 / np.linalg.norm(S1), S2 / np.linalg.norm(S2), pa)):
                    continue
                out.append((gp, RA, i, j, pa, S1, S2))
        return out

    cands = []
    for gmin, vmin in ((16, .40), (12, .35), (8, .30)):
        cands = pairs(gmin, vmin)
        if cands:
            break
    if not cands:
        print("FAIL no pair meets the R_A window and the view constraints; change --seed or widen --r-lo/--r-hi")
        return 1
    gap, RA_sel, i1, i2, PA, S1, S2 = max(cands, key=lambda t: t[0])
    v.roll(PA)                                             # frame the fan: the union points to the right

    o = [f"\\shade[inner color=white, outer color=black!2] (0,0) circle ({R});\n",
         f"\\begin{{scope}}\n\\clip (0,0) circle ({R});\n"]
    o += graticule(v, "black!15, line width=0.3pt")
    pts, RINGPTS = [], []
    for i, m in enumerate(MU):
        if m @ v.C < -0.30:
            continue
        a, b = frame(m, v.C, v.EU)
        cap = lambda t, k=KAP[i]: (np.exp(k) - np.exp(k * np.cos(t))) / (np.exp(k) - np.exp(-k))
        ths = [brentq(lambda t: cap(t) - q, 1e-9, np.pi) for q in LV]
        if all(v.vis(p) for p in ring(m, a, b, ths[-1], 60)):
            for j, th in enumerate(reversed(ths)):
                t = 1 - j / len(ths)
                c = tuple(1 + .30 * t * (COL[i][k] - 1) for k in range(3))
                o.append(f"\\definecolor{{sf{i}x{j}}}{{rgb}}{{{c[0]:.3f},{c[1]:.3f},{c[2]:.3f}}}"
                         f"\\path[fill=sf{i}x{j}, fill opacity=0.30] {path([v.P(p) for p in ring(m, a, b, th)])} -- cycle;\n")
        k6 = tuple(.60 * c for c in COL[i])
        o.append(f"\\definecolor{{sk{i}}}{{rgb}}{{{k6[0]:.3f},{k6[1]:.3f},{k6[2]:.3f}}}\n")
        for th in ths:
            for sg in runs(v, ring(m, a, b, th)):
                if len(sg) > 1:
                    o.append(f"\\draw[sk{i}, line width=0.35pt] {path(sg)};\n")
                    RINGPTS.extend(sg[::4])          # the label placer keeps clear of the rings too
        pts += [(p, COL[i]) for p in MEM[i] if v.vis(p)]
    for i in range(len(MU)):                                  # mixtures: bridges between clusters of a group
        for j in range(i + 1, len(MU)):
            nb = 26 if GRP[i] == GRP[j] else (11 if MU[i] @ MU[j] > 0.50 else 0)
            if (min(i, j), max(i, j)) == (min(i1, i2), max(i1, i2)):
                nb = max(nb, 22)
            for _ in range(nb):
                t = rng.beta(1.45, 1.45)
                p = vmf_sample(slerp(MU[i], MU[j], t), 110, rng, v.C, v.EU)
                c = tuple(min(1.0, .05 + .95 * ((1 - t) * COL[i][k] + t * COL[j][k])) for k in range(3))
                if v.vis(p):
                    pts.append((p, c))
    SCR = []
    for k, (p, c) in enumerate(pts):
        x, y = v.P(p)
        SCR.append((x, y))
        o.append(f"\\definecolor{{z{k}}}{{rgb}}{{{c[0]:.3f},{c[1]:.3f},{c[2]:.3f}}}\\fill[z{k}] ({x:.3f},{y:.3f}) circle (0.032);\n")
    o.append("\\end{scope}\n")
    o.append(f"\\draw[black!22, line width=0.45pt] (0,0) circle ({R});\n")

    # ---- the composition, drawn to the common scale 1/n_A
    P1, P2 = S1 / np.linalg.norm(S1), S2 / np.linalg.norm(S2)
    n1, n2 = len(MEM[i1]), len(MEM[i2])
    nA = n1 + n2
    m1, m2 = S1 / nA, S2 / nA
    mA = m1 + m2
    RA = float(np.linalg.norm(mA))
    o.append("\\fill[white] (0,0) circle (0.150);\n\\draw[ink, line width=0.9pt] (0,0) circle (0.132);\n")
    for a_, b_ in ((m1, mA), (m2, mA)):                        # the two open sides of the parallelogram
        (ax, ay), (bx, by) = v.P(a_), v.P(b_)
        o.append(f"\\draw[black!45, line width=0.5pt, dash pattern=on 2.2pt off 1.8pt] ({ax:.3f},{ay:.3f}) -- ({bx:.3f},{by:.3f});\n")
    for m, d in ((m1, P1), (m2, P2)):                          # each set: its resultant and its mean direction
        (mx, my), (dx, dy) = v.P(m), v.P(d)
        o.append(f"\\draw[black!45, line width=0.45pt, dash pattern=on 1.6pt off 1.6pt] ({mx:.3f},{my:.3f}) -- ({dx:.3f},{dy:.3f});\n")
        o.append(f"\\draw[-{{Stealth}}, line width=0.95pt] (0,0) -- ({mx:.3f},{my:.3f});\n")
        o.append(f"\\draw[ink, fill=white, line width=0.6pt] ({dx:.3f},{dy:.3f}) circle (0.062);\n")
    (Ax, Ay), (Px, Py) = v.P(mA), v.P(PA)
    o.append(f"\\draw[-{{Stealth}}, line width=1.45pt] (0,0) -- ({Ax:.3f},{Ay:.3f});\n")
    o.append(f"\\draw[-{{Stealth}}, line width=0.8pt, dash pattern=on 2.4pt off 1.9pt] ({Ax:.3f},{Ay:.3f}) -- ({Px:.3f},{Py:.3f});\n")
    o.append(f"\\fill[ink] ({Ax:.3f},{Ay:.3f}) circle (0.075);\n\\fill[ink] ({Px:.3f},{Py:.3f}) circle (0.072);\n")
    o.append("\\draw[black!55, line width=0.55pt, dash pattern=on 2pt off 1.8pt] "
             + path([v.P(slerp(P1, P2, t)) for t in np.linspace(0, 1, 90)]) + ";\n")
    o.append("\\fill[ink] (0,0) circle (0.058);\n")

    # ---- labels, placed by how few points and lines they cover
    LINES = []
    for vec in (m1, m2, mA):
        ex, ey = v.P(vec)
        LINES += [(t * ex, t * ey) for t in np.linspace(0, 1, 70)]
    for a_, b_ in ((m1, mA), (m2, mA), (m1, P1), (m2, P2), (mA, PA)):
        (ax, ay), (bx, by) = v.P(a_), v.P(b_)
        LINES += [(ax + t * (bx - ax), ay + t * (by - ay)) for t in np.linspace(0, 1, 40)]
    for t in np.linspace(0, 1, 70):
        g = (1 - t) * P1 + t * P2
        LINES.append(v.P(g / np.linalg.norm(g)))
    LINES += RINGPTS
    # reserved: the top-left corner label, the bottom-right corner label (its top clears the circle at its left
    # edge; 2.57 cm wide at 13 pt in Computer Modern, measured from the compiled PDF, against 2.16 cm in the
    # source's sans font) and the row of the two definitions under the ball
    x_left = R - 2.57
    y_top = -np.sqrt(max(R * R - x_left * x_left, 0.0)) - 0.12
    taken = [(-R + 0.50, R + 0.16, 1.32), (R - 1.29, y_top - 0.22, 2.57),
             (-R + 1.70, -R - 0.74, 3.40), (R - 1.45, -R - 0.74, 2.90)]

    def inside(lx, ly, w, h=0.44):
        return np.hypot(abs(lx) + w / 2, abs(ly) + h / 2) < R - 0.05

    def place(x, y, w, h=0.44, dists=(0.50, 0.68, 0.86, 1.06, 1.26, 1.50, 1.75), arc=None):
        best = None
        for dist in dists:
            for ang in (arc if arc is not None else np.linspace(0, 2 * np.pi, 24, endpoint=False)):
                lx, ly = x + dist * np.cos(ang), y + dist * np.sin(ang)
                if np.hypot(lx, ly) > R + 0.90:
                    continue
                hit = sum(1 for px, py in SCR if abs(px - lx) < w / 2 + .05 and abs(py - ly) < h / 2 + .05)
                hit += 3 * sum(1 for px, py in LINES if abs(px - lx) < w / 2 + .06 and abs(py - ly) < h / 2 + .06)
                hit += 40 * sum(1 for tx, ty, tw in taken if abs(tx - lx) < (tw + w) / 2 and abs(ty - ly) < h)
                # a label must not straddle the ball's outline: its backdrop would cut the circle
                cx_, cy_ = max(abs(lx) - w / 2, 0.0), max(abs(ly) - h / 2, 0.0)
                dmin, dmax = np.hypot(cx_, cy_), np.hypot(abs(lx) + w / 2, abs(ly) + h / 2)
                hit += 40 * (dmin - 0.06 < R < dmax + 0.06)
                sc = 3.0 * hit + 1.0 * dist + 0.9 * max(0, np.hypot(lx, ly) - R)
                if best is None or sc < best[0]:
                    best = (sc, lx, ly)
        taken.append((best[1], best[2], w))
        return best[1], best[2]

    for d, lab, w in ((P1, r"$\bar\mu(A_1)$", 1.26), (P2, r"$\bar\mu(A_2)$", 1.26), (PA, r"$\bar\mu(A)$", 1.08)):
        x, y = v.P(d)
        lx, ly = place(x, y, w)
        backdrop = HALO if inside(lx, ly, w) else "inner sep=0.8pt"   # a backdrop only where it cannot cut the circle
        o.append(f"\\node[{backdrop}, font=\\fLabel] at ({lx:.2f},{ly:.2f}) {{{lab}}};\n")
    base = np.arctan2(Ay, Ax)                                 # the resultant's label sits outside on a leader
    best = None
    for off in np.linspace(-1.5, 1.5, 61):
        ex, ey = (R + 0.66) * np.cos(base + off), (R + 0.66) * np.sin(base + off)
        seg = [(Ax + t * (ex - Ax), Ay + t * (ey - Ay)) for t in np.linspace(0, 1, 60)]
        hit = sum(1 for sx, sy in seg for px, py in SCR if abs(px - sx) < 0.16 and abs(py - sy) < 0.16)
        hit += 25 * sum(1 for tx, ty, tw in taken if abs(tx - ex) < (tw + 1.00) / 2 and abs(ty - ey) < 0.52)
        # the leader itself must not cross a label already set (the ported placer checked only its end)
        hit += 25 * sum(1 for tx, ty, tw in taken for sx, sy in seg[:54]
                        if abs(tx - sx) < tw / 2 + 0.05 and abs(ty - sy) < 0.27)
        sc = hit + 1.5 * abs(off)
        if best is None or sc < best[0]:
            best = (sc, base + off)
    Lx, Ly = (R + 0.66) * np.cos(best[1]), (R + 0.66) * np.sin(best[1])
    ln = np.hypot(Lx - Ax, Ly - Ay)
    ux, uy = (Lx - Ax) / ln, (Ly - Ay) / ln
    stop = min(0.50 / max(abs(ux), 1e-6), 0.24 / max(abs(uy), 1e-6)) + 0.10   # the label's box edge plus a gap
    o.append(f"\\draw[black!45, line width=0.45pt] ({Ax:.3f},{Ay:.3f}) -- ({Lx - stop * ux:.3f},{Ly - stop * uy:.3f});\n")
    o.append(f"\\node[inner sep=1pt, font=\\fLabel] at ({Lx:.2f},{Ly:.2f}) {{$S(A)$}};\n")
    taken.append((Lx, Ly, 1.00))
    ox_, oy_ = place(0, 0, 0.36, 0.40, (0.40, 0.52, 0.66), arc=np.linspace(np.pi * 1.05, np.pi * 1.95, 12))
    o.append(f"\\node[{HALO}, font=\\fLabel] at ({ox_:.2f},{oy_:.2f}) {{$O$}};\n")
    o.append(f"\\node[anchor=north east, inner sep=1pt, font=\\fLabel] at ({R:.2f},{y_top:.2f}) {{$A = A_1 \\cup A_2$}};\n")
    o.append(f"\\node[anchor=north west, font=\\fLabel] at ({-R:.2f},{R + 0.16:.2f}) {{$\\mathbb{{S}}^{{d-1}}$}};\n")
    o.append(f"\\node[anchor=north west, inner sep=1pt, font=\\fLabel] at ({-R:.2f},{-R - 0.52:.2f}) "
             f"{{$\\bar\\mu(A)=S(A)/\\lVert S(A)\\rVert$}};\n")
    o.append(f"\\node[anchor=north east, inner sep=1pt, font=\\fLabel] at ({R:.2f},{-R - 0.52:.2f}) "
             f"{{$R_A=\\lVert S(A)\\rVert/n_A$}};\n")

    # ---- checks on the algebra and on what the drawing claims
    SA = S1 + S2
    checks = {
        "S(A) = S(A1) + S(A2)": bool(np.allclose(SA, sum(MEM[i1] + MEM[i2]), atol=1e-9)),
        "drawn parallelogram closes (projected)": bool(np.allclose(np.array(v.P(mA)), np.array(v.P(m1)) + np.array(v.P(m2)), atol=1e-9)),
        "drawn diagonal length = R_A": bool(abs(np.linalg.norm(mA) - np.linalg.norm(SA) / nA) < 1e-12),
        "projection is radial": bool(np.linalg.norm(mA / np.linalg.norm(mA) - PA) < 1e-12),
    }
    nrm = np.cross(P1, P2)
    nrm /= np.linalg.norm(nrm)
    a12 = float(np.degrees(np.arccos(np.clip(P1 @ P2, -1, 1))))
    a1a = float(np.degrees(np.arccos(np.clip(P1 @ PA, -1, 1))))
    a2a = float(np.degrees(np.arccos(np.clip(P2 @ PA, -1, 1))))
    checks["angles add up (mu(A) between mu(A1) and mu(A2))"] = bool(abs(a1a + a2a - a12) < 1e-6)
    checks["mu(A) in the plane of mu(A1), mu(A2)"] = bool(abs(PA @ nrm) < 1e-9)
    for k, ok in checks.items():
        print(f"{'ok  ' if ok else 'FAIL'} {k}")
    facts = {"seed": args.seed, "radius_cm": R, "elevation_deg": args.el, "clusters": len(MU), "points_drawn": len(pts),
             "pair": {"n1": n1, "n2": n2, "R1": round(float(np.linalg.norm(S1) / n1), 3),
                      "R2": round(float(np.linalg.norm(S2) / n2), 3), "R_A": round(RA, 3),
                      "angle_A1_A2_deg": round(a12, 1), "nearest_cluster_to_mu_A_deg": round(float(gap), 1)},
             "gap_tip_to_surface_of_radius": round(1 - RA, 3), "checks": checks}
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "facts.json").write_text(json.dumps(facts, indent=1) + "\n")
    body = "\\begin{tikzpicture}[paper]\n" + "".join(o) + "\\end{tikzpicture}\n"
    if args.preamble:
        (out / "sphere.tex").write_text(figkit.header(Path(args.preamble), None) + body + "\\end{document}\n")
    else:
        (out / "sphere_body.tex").write_text(body)
    print(f"ok  {len(pts)} points, {len(MU)} clusters; pair n={n1}+{n2}, R_A={RA:.3f}, gap to the surface "
          f"{1 - RA:.2f} of the radius -> {out}")
    return 0 if all(checks.values()) else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="The unit sphere of an embedding space, or its small glyph, as TikZ.")
    ap.add_argument("--out", required=True, help="output folder")
    ap.add_argument("--preamble", help="write a standalone sphere.tex with this preamble on top")
    ap.add_argument("--glyph", action="store_true", help="write the overview glyph instead of the full figure")
    ap.add_argument("--seed", type=int, default=17, help="random seed (default 17)")
    ap.add_argument("--radius", type=float, default=None, help="radius in cm (default 4.05, glyph 1.02)")
    ap.add_argument("--el", type=float, default=None, help="view elevation in degrees (default 14, glyph 15)")
    ap.add_argument("--r-lo", type=float, default=0.62, help="lower bound of the union's R_A (0.62)")
    ap.add_argument("--r-hi", type=float, default=0.78, help="upper bound of the union's R_A (0.78)")
    a = ap.parse_args()
    if a.glyph:
        a.radius = 1.02 if a.radius is None else a.radius
        a.el = 15.0 if a.el is None else a.el
        return glyph(a)
    a.radius = 4.05 if a.radius is None else a.radius
    a.el = 14.0 if a.el is None else a.el
    return full(a)


if __name__ == "__main__":
    sys.exit(main())
