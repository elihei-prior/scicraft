#!/usr/bin/env python3
"""Generate a zoom cascade over ONE point field as TikZ: field, region, crop, point graph.

Every level is a crop of the same field, so what one frame marks is what the next frame shows:
  level 1  field   the whole domain as a density wash (a KDE per category, three nested filled bands at
                   relative levels 0.10, 0.36, 0.66, opacity 0.22, 0.42, 0.72, core drawn last)
  level 2  region  a window of the field, still a wash
  level 3  crop    a window of the region: the individual points, over a faint wash
  level 4  graph   a window of the crop: its points as nodes and their k nearest neighbors as edges, computed on
                   the FULL field (a neighbor outside the window is still a neighbor; its edge is clipped at
                   the frame), optionally capped at a radius
A box on each level marks the next level's window, and dashed connectors run from the box to the next frame.

The window is chosen by a stated rule, never by eye: among windows of the graph's size whose center lies in the
middle 60 percent of the domain and that hold at least --min-points points, the one with the highest category
entropy (where the categories mix). The rule, the window and every count go to facts.json.

--views also writes the two masked input views of the crop that a training overview shows: one with rectangular
regions masked (dashed boxes, masked points gray) and one with a whole category grayed out.

Input: a CSV with columns x,y and optionally label (the real points), or a seeded synthetic field of clustered,
anisotropic lumps per category. The same input and seed give the same figure.

Outputs in --out:
  cascade.tex        the four levels in a row with connectors and labels (only with --preamble)
  frag_*.tex         each level, and each view, as a panel in local coordinates [-1,1]^2 with its frame; place it
                     with \\begin{scope}[shift={(x,y)}, x=S cm, y=S cm] where 2S is the panel's side
  facts.json         every number the figure shows or depends on

Needs numpy, scipy and contourpy (installed with matplotlib).

Usage:
    python3 zoom_cascade.py --out cascade/ --preamble ../assets/preamble.tex
    python3 zoom_cascade.py --points field.csv --k 6 --radius 0.04 --out cascade/ --preamble P --views
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
from pathlib import Path

import numpy as np
from contourpy import FillType, contour_generator
from scipy.ndimage import gaussian_filter
from scipy.spatial import cKDTree

import sys  # noqa: E402
sys.dont_write_bytecode = True        # importing a sibling must not leave __pycache__ in the skill
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "assets"))
import figkit  # noqa: E402

BANDS = [(0.10, 0.22), (0.36, 0.42), (0.66, 0.72)]     # (relative density, opacity), core last
POINT_COLORS = ["ptblue", "ptochre", "ptpurple"]
WASH_COLORS = ["washblue", "washochre", "washpurple"]
LUMPS = 5                                               # lumps per category in the synthetic field


def synthetic_field(n: int, n_cat: int, seed: int):
    """Clustered, anisotropic lumps; each category recurs in several separated places."""
    rng = np.random.default_rng(seed)
    pts, lab = [], []
    per = n // n_cat
    for c in range(n_cat):
        centers = rng.uniform(-0.8, 0.8, size=(LUMPS, 2))
        for j in range(LUMPS):
            m = per // LUMPS
            ang = rng.uniform(0, math.pi)
            sx, sy = rng.uniform(0.14, 0.32), rng.uniform(0.07, 0.16)
            rot = np.array([[math.cos(ang), -math.sin(ang)], [math.sin(ang), math.cos(ang)]])
            pts.append(rng.normal(size=(m, 2)) * [sx, sy] @ rot.T + centers[j])
            lab += [c] * m
    pts = np.vstack(pts)
    keep = np.all(np.abs(pts) <= 0.97, axis=1)
    return pts[keep], np.array(lab)[keep], [f"category {c + 1}" for c in range(n_cat)]


def read_field(path: Path):
    with path.open(newline="") as fh:
        rows = list(csv.DictReader(fh))
    if not rows or "x" not in rows[0] or "y" not in rows[0]:
        raise SystemExit(f"{path}: needs a header with columns x,y and optionally label")
    xy = np.array([[float(r["x"]), float(r["y"])] for r in rows])
    names = [r.get("label", "0") or "0" for r in rows]
    cats = sorted(set(names), key=names.index)
    lab = np.array([cats.index(s) for s in names])
    ctr = (xy.max(0) + xy.min(0)) / 2
    half = (xy.max(0) - xy.min(0)).max() / 2 or 1.0
    return (xy - ctr) / half * 0.95, lab, cats, float(half / 0.95), ctr


def kde(p, bw: float, grid: int):
    h = np.zeros((grid, grid))
    ix = np.clip(((p[:, 0] + 1) / 2 * (grid - 1)).astype(int), 0, grid - 1)
    iy = np.clip(((p[:, 1] + 1) / 2 * (grid - 1)).astype(int), 0, grid - 1)
    np.add.at(h, (iy, ix), 1)
    return gaussian_filter(h, sigma=bw * grid / 2)


def local(pts, c, h):
    return (np.asarray(pts) - c) / h


def window(c, h):
    h = min(h, 1.0)
    return np.clip(c, -1 + h, 1 - h), h


def wash(dens, colors, c, h, grid, opacity_scale=1.0):
    """Filled density bands of every category inside a window, in local coordinates."""
    xs = np.linspace(-1, 1, grid)
    i0 = max(0, int(np.searchsorted(xs, c[0] - h)) - 1)
    i1 = min(grid, int(np.searchsorted(xs, c[0] + h)) + 2)
    j0 = max(0, int(np.searchsorted(xs, c[1] - h)) - 1)
    j1 = min(grid, int(np.searchsorted(xs, c[1] + h)) + 2)
    out = []
    for d, col in zip(dens, colors):
        gen = contour_generator(xs[i0:i1], xs[j0:j1], d[j0:j1, i0:i1], fill_type=FillType.OuterOffset)
        for lev, op in BANDS:
            polys, _ = gen.filled(lev, np.inf)
            for poly in polys:
                if len(poly) < 8:
                    continue
                loc = local(poly[::2], c, h)
                pth = " ".join(f"({x:.3f},{y:.3f})" for x, y in loc)       # SPACE separated, never "--"
                out.append(f"\\fill[{col}, opacity={op * opacity_scale:.2f}] plot[smooth cycle, tension=0.6] coordinates {{{pth}}};")
    return out


def panel(body, frame_style, name, box=None):
    """A unit panel: clip, content, the box marking the next window, the frame on top. It names its corners
    (name-nw, name-ne, name-sw, name-se) and its box's (name-box-ne, name-box-se, ...): TikZ keeps a named
    coordinate in page coordinates, so a figure that places the panel anywhere can attach links to them."""
    s = ["\\begin{scope}", "\\clip[rounded corners=2pt] (-1,-1) rectangle (1,1);",
         "\\fill[white] (-1,-1) rectangle (1,1);"] + body + ["\\end{scope}"]
    if box is not None:
        (x0, y0), (x1, y1) = box
        s.append(f"\\draw[zoombox, rounded corners=1.5pt] ({x0:.3f},{y0:.3f}) rectangle ({x1:.3f},{y1:.3f});")
        s.append(f"\\coordinate ({name}-box-nw) at ({x0:.3f},{y1:.3f}); \\coordinate ({name}-box-ne) at ({x1:.3f},{y1:.3f});")
        s.append(f"\\coordinate ({name}-box-sw) at ({x0:.3f},{y0:.3f}); \\coordinate ({name}-box-se) at ({x1:.3f},{y0:.3f});")
    s.append(f"\\draw[{frame_style}, fill=none] (-1,-1) rectangle (1,1);")   # on top: never a fill
    s.append(f"\\coordinate ({name}-nw) at (-1,1); \\coordinate ({name}-ne) at (1,1); "
             f"\\coordinate ({name}-sw) at (-1,-1); \\coordinate ({name}-se) at (1,-1);")
    return "\n".join(s) + "\n"


def clip_segment(x0, y0, x1, y1, lo=-1.0, hi=1.0):
    """Liang-Barsky: the part of a segment inside the square [lo, hi]^2, or None. Clipping in the generator
    keeps hidden ink out of the PDF, where an audit would still find it under a TikZ clip."""
    dx, dy = x1 - x0, y1 - y0
    t0, t1 = 0.0, 1.0
    for p, q in ((-dx, x0 - lo), (dx, hi - x0), (-dy, y0 - lo), (dy, hi - y0)):
        if p == 0:
            if q < 0:
                return None
            continue
        t = q / p
        if p < 0:
            t0 = max(t0, t)
        else:
            t1 = min(t1, t)
        if t0 > t1:
            return None
    return x0 + t0 * dx, y0 + t0 * dy, x0 + t1 * dx, y0 + t1 * dy


def entropy(counts):
    p = np.asarray(counts, float)
    p = p[p > 0] / p.sum()
    return float(-(p * np.log(p)).sum())


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Zoom cascade over one point field (field, region, crop, point graph) as TikZ.")
    ap.add_argument("--out", required=True, help="output folder")
    ap.add_argument("--points", help="CSV with x,y[,label]; default a seeded synthetic field")
    ap.add_argument("--seed", type=int, default=7, help="seed of the synthetic field and the masks (default 7)")
    ap.add_argument("--n", type=int, default=4000, help="synthetic field size (default 4000)")
    ap.add_argument("--categories", type=int, default=3, help="synthetic categories (default 3)")
    ap.add_argument("--colors", default=",".join(POINT_COLORS), help="point color per category (preamble names)")
    ap.add_argument("--washes", default=",".join(WASH_COLORS), help="wash color per category (preamble names)")
    ap.add_argument("--k", type=int, default=5, help="neighbors per node in the graph (default 5)")
    ap.add_argument("--radius", type=float, default=None, help="cap the graph at this radius (field units)")
    ap.add_argument("--zoom", default="3.2,1.35,2.8", help="window ratios field:region, region:crop, crop:graph")
    ap.add_argument("--min-points", type=int, default=40, help="points the graph window must hold (default 40)")
    ap.add_argument("--bw", type=float, default=0.05, help="KDE bandwidth as a fraction of the domain (0.05)")
    ap.add_argument("--grid", type=int, default=480, help="KDE grid (default 480)")
    ap.add_argument("--frame-cm", type=float, default=2.1, help="panel side in cm (default 2.1)")
    ap.add_argument("--views", action="store_true", help="also write the two masked views of the crop")
    ap.add_argument("--masks", type=int, default=4, help="masked regions in the block view (default 4)")
    ap.add_argument("--preamble", help="write a standalone cascade.tex with this preamble on top")
    a = ap.parse_args(argv)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    colors = [c for c in a.colors.split(",") if c]
    washes = [c for c in a.washes.split(",") if c]
    if a.points:
        field, lab, names, unit, _ = read_field(Path(a.points))
        source = {"points": Path(a.points).name, "field_units_per_domain_half_width": unit}
    else:
        field, lab, names = synthetic_field(a.n, a.categories, a.seed)
        source = {"synthetic": True, "seed": a.seed, "n_requested": a.n}
    n_cat = int(lab.max()) + 1
    if len(colors) < n_cat or len(washes) < n_cat:
        raise SystemExit(f"{n_cat} categories need {n_cat} colors in --colors and --washes")
    dens = []
    for c in range(n_cat):
        d = kde(field[lab == c], a.bw, a.grid)
        dens.append(d / d.max() if d.max() > 0 else d)

    # ---- the windows, from the graph's outward; the graph window by the entropy rule
    f2, f3, f4 = (float(v) for v in a.zoom.split(","))
    h1 = 1.0
    h2 = h1 / f2
    h3 = h2 / f3
    h4 = h3 / f4
    tree = cKDTree(field)
    best = None
    for cx in np.linspace(-0.6, 0.6, 25):
        for cy in np.linspace(-0.6, 0.6, 25):
            c4 = np.array([cx, cy])
            inside = np.all(np.abs(field - c4) <= h4, axis=1)
            if inside.sum() < a.min_points:
                continue
            e = entropy(np.bincount(lab[inside], minlength=n_cat))
            if best is None or e > best[0] + 1e-12:
                best = (e, c4, int(inside.sum()))
    if best is None:
        raise SystemExit("no graph window holds --min-points points; lower it or change --zoom")
    ent, c4, n4 = best
    c3, h3 = window(c4, h3)
    c2, h2 = window(c3, h2)
    c1 = np.zeros(2)
    wins = [(c1, h1), (c2, h2), (c3, h3), (c4, h4)]

    def boxin(k):
        (pc, ph), (cc, ch) = wins[k], wins[k + 1]
        return tuple(map(tuple, (local(cc - ch, pc, ph), local(cc + ch, pc, ph))))

    frags = {}
    frags["frag_field.tex"] = panel(wash(dens, washes, c1, h1, a.grid), "zoombox", "field", boxin(0))
    frags["frag_region.tex"] = panel(wash(dens, washes, c2, h2, a.grid), "zoombox, rounded corners=2pt", "region", boxin(1))
    in3 = np.all(np.abs(field - c3) <= h3, axis=1)
    crop_pts = [f"\\figpoint{{{x:.3f},{y:.3f}}}{{{colors[l]}}}" for (x, y), l in zip(local(field[in3], c3, h3), lab[in3])]
    frags["frag_crop.tex"] = panel(wash(dens, washes, c3, h3, a.grid, 0.25) + crop_pts,
                                   "zoombox, rounded corners=2pt", "crop", boxin(2))
    # the graph: neighbors over the FULL field, drawn for the nodes inside the window
    in4 = np.where(np.all(np.abs(field - c4) <= h4 * 1.15, axis=1))[0]
    dist, idx = tree.query(field[in4], k=a.k + 1)
    edges = set()
    for row, i in enumerate(in4):
        for d, j in zip(dist[row, 1:], idx[row, 1:]):
            if a.radius is None or d <= a.radius:
                edges.add((min(i, j), max(i, j)))
    g = []
    # a node is drawn where its disk (0.052 cm) and 1 bp of air clear the frame; an edge is kept when each end
    # is a drawn node or lies outside the frame, so every edge ends at a node or at the frame itself
    inner = 1.0 - (0.052 / 2.54 * 72 + 1.0) / (a.frame_cm / 2 / 2.54 * 72)
    def end_ok(x, y):
        m = max(abs(x), abs(y))
        return m <= inner or m > 1.0
    for i, j in sorted(edges):
        (x0, y0), (x1, y1) = local(field[[i, j]], c4, h4)
        if not (end_ok(x0, y0) and end_ok(x1, y1)):
            continue
        seg = clip_segment(x0, y0, x1, y1)
        if seg and abs(seg[2] - seg[0]) + abs(seg[3] - seg[1]) > 1e-6:
            g.append(f"\\draw[graphedge] ({seg[0]:.3f},{seg[1]:.3f}) -- ({seg[2]:.3f},{seg[3]:.3f});")
    for (x, y), l in zip(local(field[in4], c4, h4), lab[in4]):
        if max(abs(x), abs(y)) <= inner:
            g.append(f"\\fignode{{{x:.3f},{y:.3f}}}{{{colors[l]}}}")
    frags["frag_graph.tex"] = panel(g, "crop", "graph")

    facts = {"source": source, "n_points": int(len(field)),
             "categories": {names[c]: int((lab == c).sum()) for c in range(n_cat)}, "colors": colors[:n_cat],
             "kde": {"bandwidth": a.bw, "grid": a.grid, "levels": [b for b, _ in BANDS], "opacities": [o for _, o in BANDS]},
             "window_rule": f"highest category entropy among graph windows with at least {a.min_points} points, "
                            f"centers on a 25 x 25 grid over the middle 60 percent of the domain",
             "windows": [{"level": n, "center": [round(float(v), 4) for v in c], "half_width": round(float(h), 4)}
                         for n, (c, h) in zip(("field", "region", "crop", "graph"), wins)],
             "graph": {"k": a.k, "radius_cap": a.radius, "nodes_in_window": n4, "entropy_nats": round(ent, 3),
                       "edges_drawn": len(edges), "neighbors_computed_on": "the full field"},
             "points_in_crop": int(in3.sum())}

    if a.views:
        rng = np.random.default_rng(a.seed + 1)
        masks, tries = [], 0
        while len(masks) < a.masks and tries < 500:
            tries += 1
            w, hh = rng.uniform(0.25, 0.65, 2)
            x0, y0 = rng.uniform(-0.92, 0.92 - w), rng.uniform(-0.92, 0.92 - hh)
            if all(x0 > m[2] + 0.08 or x0 + w < m[0] - 0.08 or y0 > m[3] + 0.08 or y0 + hh < m[1] - 0.08 for m in masks):
                masks.append((x0, y0, x0 + w, y0 + hh))
        loc3 = local(field[in3], c3, h3)
        lab3 = lab[in3]
        masked = np.array([any(m[0] <= x <= m[2] and m[1] <= y <= m[3] for m in masks) for x, y in loc3])
        body = [f"\\draw[maskbox] ({m[0]:.3f},{m[1]:.3f}) rectangle ({m[2]:.3f},{m[3]:.3f});" for m in masks]
        body += [f"\\figmasked{{{x:.3f},{y:.3f}}}" for (x, y), mk in zip(loc3, masked) if mk]
        body += [f"\\figpoint{{{x:.3f},{y:.3f}}}{{{colors[l]}}}" for (x, y), l, mk in zip(loc3, lab3, masked) if not mk]
        frags["frag_view_block.tex"] = panel(body, "crop", "viewblock")
        hidden = int(np.argmax(np.bincount(lab3, minlength=n_cat)))        # the most frequent category in the crop
        body = [f"\\figmasked{{{x:.3f},{y:.3f}}}" for (x, y), l in zip(loc3, lab3) if l == hidden]
        body += [f"\\figpoint{{{x:.3f},{y:.3f}}}{{{colors[l]}}}" for (x, y), l in zip(loc3, lab3) if l != hidden]
        frags["frag_view_category.tex"] = panel(body, "crop", "viewcategory")
        facts["views"] = {"block_masks_local": [[round(v, 3) for v in m] for m in masks],
                          "points_masked_in_block_view": int(masked.sum()),
                          "category_hidden_in_category_view": names[hidden],
                          "points_hidden_in_category_view": int((lab3 == hidden).sum())}

    for name, text in frags.items():
        (out / name).write_text(text)
    (out / "facts.json").write_text(json.dumps(facts, indent=1) + "\n")

    if a.preamble:
        s = a.frame_cm / 2
        step = a.frame_cm + 1.25
        xs = [i * step for i in range(4)]
        body = ["\\begin{tikzpicture}[paper]"]
        for k, name in enumerate(("frag_field.tex", "frag_region.tex", "frag_crop.tex", "frag_graph.tex")):
            sc = s * (0.82 if k == 0 else 1.0)                              # the field tile a little smaller
            body.append(f"\\begin{{scope}}[shift={{({xs[k]:.3f},0)}}, x={sc:.4f}cm, y={sc:.4f}cm]\n{frags[name]}\\end{{scope}}")
        for k, (fr, to) in enumerate((("field", "region"), ("region", "crop"), ("crop", "graph"))):
            body.append(f"\\draw[zoomlink] ({fr}-box-ne) -- ({to}-nw);")   # dashed links: box to the next frame
            body.append(f"\\draw[zoomlink] ({fr}-box-se) -- ({to}-sw);")
        gloss = r"$k$ nearest neighbors" if a.radius is None else r"$k$NN within radius $r$"
        for k, lab_ in enumerate(("field", "region", "crop", "point graph")):
            body.append(f"\\node[lbl, anchor=base] at ({xs[k]:.3f},{-s - 0.62:.3f}) {{{lab_}}};")
        body.append(f"\\node[glossnote, anchor=base] at ({xs[3]:.3f},{-s - 1.12:.3f}) {{{gloss}}};")
        body.append("\\end{tikzpicture}")
        (out / "cascade.tex").write_text(figkit.header(Path(a.preamble), None) + "\n".join(body) + "\n\\end{document}\n")
    print(f"ok  {len(field)} points, {n_cat} categories; graph window {n4} nodes, entropy {ent:.3f} nats, "
          f"{len(edges)} edges (k={a.k}); crop {int(in3.sum())} points -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
