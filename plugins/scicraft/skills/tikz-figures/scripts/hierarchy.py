#!/usr/bin/env python3
"""Generate a hierarchy panel as TikZ from a REAL quadtree over seeded points: the tree, the isometric pyramid of
tile grids, the per-level rows of tokens through blocks with feedback rails, and the point graph at the bottom.

What is computed, not drawn by hand:
  * the quadtree: a tile splits while it holds more than --capacity points, down to --depth levels;
  * the selected point, by a stated rule: the point nearest the center of the field; its path (the tile holding
    it at every level) is filled strong in the pyramid and in the tree;
  * the tree: the selected node's OCCUPIED children at every drawn level (an empty child is not a node);
  * the pyramid: every tile of every drawn level; the selected tile strong, its siblings pale, the rest white;
  * the point graph: the k nearest neighbors of every point, drawn in the pyramid's isometric frame.
Every number goes to facts.json.

The rows run up the hierarchy as the encoder computes it: at each drawn level the level's tokens (orange) pass
through a self-attention block (mint) and leave as the level's output (blue); a pooling block (peach) between two
levels takes the finer level's output from the right and feeds the coarser level's input from the left. Levels
that are not drawn are bridged by dashed rails ("continues below") and vertical dots.

Layout follows the measured hierarchy panel (bp, y downward): rows 78 bp apart, the tree and the pyramid levels on
the rows' center lines, the top tile 137.44 x 68.72 bp, tree nodes 11.34 bp, tree edges 0.5 pt black!55 with the
selected path 1.1 pt, rails 0.6 pt.

Needs numpy and scipy (cKDTree). Imports assets/figkit.py for the row primitives.

Usage:
    python3 hierarchy.py --out hierarchy/ --preamble ../assets/preamble.tex
    python3 hierarchy.py --out h/ --n 400 --capacity 6 --seed 5 --levels 4 --depth 6 --k 3 --preamble P
"""
from __future__ import annotations

import argparse
import json
import math
import sys
sys.dont_write_bytecode = True        # importing a sibling must not leave __pycache__ in the skill
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "assets"))
import figkit as K  # noqa: E402

# measured geometry of the source panel (bp, y downward)
ROW0, ROW_DY = 48.6, 78.0          # first row's center line and the row pitch
TOP_HALF_W = 68.72                 # the top tile: 137.44 x 68.72 bp
TILE_GAP = 2.0                     # white between the tiles of a level, bp
GRAPH_HALF_W = 0.9 * TOP_HALF_W    # the point graph's frame, a little smaller than a level (measured 124 x 61 bp)
NODE_D = 11.34                     # tree node diameter; 9.07 at the finest drawn level (measured)
NODE_D_LAST = 9.07
TREE_X0, TREE_W = 18.0, 101.0      # tree column: its last node stays 20 bp clear of the pyramid's left tip
PYR_CX = 215.0                     # pyramid center line
LBL_X = 298.0                      # level labels, left edge
CHIP, CHIP_GAP, CHIPS = 6.8, 1.13, 5
COL_IN, COL_BOX, COL_OUT = 391.0, 455.0, 525.0   # centers: input chips, block, output chips
RAIL_L, RAIL_R = 362.0, 560.0      # the left (up into a row) and right (up into a pool block) rails
ROW_BOX_W, ROW_BOX_H = 58.0, 24.0
PT_LEVEL, PT_SIZE, PT_ROWBOX, PT_SYM = 17.9, 15.9, 12.0, 14.0


def quadtree(pts, capacity, depth):
    """{(level, i, j): [point indices]} for every occupied tile, splitting while a tile holds > capacity."""
    tiles = {}

    def rec(level, i, j, idx):
        tiles[(level, i, j)] = idx
        if level == depth - 1 or len(idx) <= capacity:
            return
        n = 2 ** (level + 1)
        for di in (0, 1):
            for dj in (0, 1):
                ci, cj = 2 * i + di, 2 * j + dj
                sub = [k for k in idx if int(pts[k, 0] * n) == ci and int(pts[k, 1] * n) == cj]
                if sub:
                    rec(level + 1, ci, cj, sub)

    rec(0, 0, 0, list(range(len(pts))))
    return tiles


def stratified(rng, n):
    """n points spread evenly over the unit square: one per cell of a grid, jittered inside its cell, with a few
    cells left empty. Uniform random points clump, and their neighbor graph blots under the pyramid; evenly spread
    points give a graph that reads as a sheet, as the source's did."""
    g = int(math.ceil(math.sqrt(n * 1.12)))
    cell = rng.permutation(g * g)[:n]
    jit = rng.uniform(-0.34, 0.34, size=(n, 2))
    return (np.column_stack([cell // g, cell % g]) + 0.5 + jit) / g


def iso(u, v, cx, cy, hw):
    """Isometric map of the unit square: (0,0) the front (bottom) vertex, (1,1) the back (top) vertex."""
    return cx + (u - v) * hw, cy + (1 - u - v) * hw / 2


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Hierarchy panel from a real quadtree over seeded points, as TikZ.")
    ap.add_argument("--out", required=True, help="output folder")
    ap.add_argument("--preamble", default=str(K.PREAMBLE), help="the preamble (default: assets/preamble.tex)")
    ap.add_argument("--n", type=int, default=300, help="points (default 300)")
    ap.add_argument("--seed", type=int, default=5, help="seed (default 5)")
    ap.add_argument("--capacity", type=int, default=6, help="a tile splits while it holds more (default 6)")
    ap.add_argument("--depth", type=int, default=6, help="levels of the quadtree (default 6)")
    ap.add_argument("--levels", type=int, default=4, help="levels drawn, coarsest first (default 4)")
    ap.add_argument("--k", type=int, default=2, help="neighbors in the point graph (default 2)")
    a = ap.parse_args(argv)
    if a.levels > a.depth:
        raise SystemExit("--levels cannot exceed --depth")
    rng = np.random.default_rng(a.seed)
    pts = stratified(rng, a.n)
    tiles = quadtree(pts, a.capacity, a.depth)

    # ---- the selected point, by a stated rule: the point nearest the center of the field
    sel = int(np.argmin(np.hypot(pts[:, 0] - 0.5, pts[:, 1] - 0.5)))
    path = [(lv, int(pts[sel, 0] * 2 ** lv), int(pts[sel, 1] * 2 ** lv)) for lv in range(a.depth)]
    path = [t for t in path if t in tiles]

    f = K.Figure(570.0, 410.0, preamble=Path(a.preamble))
    rows = [ROW0 + lv * ROW_DY for lv in range(a.levels)]
    graph_y = rows[-1] + 90.0

    # ---- the tree: the selected node's occupied children at every drawn level
    tree_nodes = {}                                  # tile -> (x, y)
    tree_nodes[path[0]] = (TREE_X0 + TREE_W / 2, rows[0])
    spacing = [TREE_W / 3.0, 20.0, 12.5, 9.0, 7.0]
    edges = []
    for lv in range(a.levels - 1):
        parent = path[lv]
        px, _ = tree_nodes[parent]
        # occupied children, left to right in the order the pyramid shows them (isometric x = i - j)
        kids = sorted((t for t in tiles if t[0] == lv + 1 and t[1] // 2 == parent[1] and t[2] // 2 == parent[2]),
                      key=lambda t: (t[1] - t[2], t[1] + t[2]))
        sp = spacing[min(lv, len(spacing) - 1)]
        x0 = px - sp * (len(kids) - 1) / 2
        x0 = min(max(x0, TREE_X0), TREE_X0 + TREE_W - sp * (len(kids) - 1))
        for q, kid in enumerate(kids):
            tree_nodes[kid] = (x0 + q * sp, rows[lv + 1])
            edges.append((parent, kid))
    def node_d(t):
        return NODE_D_LAST if t[0] == a.levels - 1 else NODE_D

    for par, kid in edges:                           # edges first, the selected path last and on top
        on = par in path and kid in path
        (x0, y0), (x1, y1) = tree_nodes[par], tree_nodes[kid]
        ym = (y0 + y1) / 2
        style = "treepath" if on else "treeedge"
        f.add(rf"\draw[{style}] {f.p(x0, y0 + node_d(par) / 2)} .. controls {f.p(x0, ym)} and {f.p(x1, ym)} .. "
              rf"{f.p(x1, y1 - node_d(kid) / 2)};")
    for t, (x, y) in tree_nodes.items():
        fill = "tilestrong" if t in path else "white"
        f.add(rf"\node[treenode, fill={fill}, minimum size={node_d(t):g}bp] at {f.p(x, y)} {{}};")

    # ---- the pyramid: every tile of every drawn level
    n_tiles = {}
    for lv in range(a.levels):
        n = 2 ** lv
        hw = TOP_HALF_W
        sel_t = path[lv] if lv < len(path) else None
        g = TILE_GAP / (2 * hw) * n if lv else 0.0  # the gap as a fraction of a tile
        for i in range(n):
            for j in range(n):
                u0, u1 = i / n + g / n / 2, (i + 1) / n - g / n / 2
                v0, v1 = j / n + g / n / 2, (j + 1) / n - g / n / 2
                corners = [iso(u0, v0, PYR_CX, rows[lv], hw), iso(u1, v0, PYR_CX, rows[lv], hw),
                           iso(u1, v1, PYR_CX, rows[lv], hw), iso(u0, v1, PYR_CX, rows[lv], hw)]
                if lv > 0 and sel_t and (lv, i, j) == sel_t:     # the single top tile stays pale
                    fill = "tilestrong"
                elif lv == 0 or (sel_t and i // 2 == sel_t[1] // 2 and j // 2 == sel_t[2] // 2):
                    fill = "tilepale"
                else:
                    fill = "white"
                lw = "0.55pt" if lv == 0 else "0.35pt"
                f.add(rf"\draw[isotile, fill={fill}, line width={lw}] " + " -- ".join(f.p(x, y) for x, y in corners) + " -- cycle;")
        n_tiles[lv] = n * n
    # the selected tile once more on top, so its outline is not under a neighbor's
    for lv in range(1, a.levels):
        if lv < len(path):
            n = 2 ** lv
            _, i, j = path[lv]
            g = TILE_GAP / (2 * TOP_HALF_W) * n
            u0, u1, v0, v1 = i / n + g / n / 2, (i + 1) / n - g / n / 2, j / n + g / n / 2, (j + 1) / n - g / n / 2
            corners = [iso(u0, v0, PYR_CX, rows[lv], TOP_HALF_W), iso(u1, v0, PYR_CX, rows[lv], TOP_HALF_W),
                       iso(u1, v1, PYR_CX, rows[lv], TOP_HALF_W), iso(u0, v1, PYR_CX, rows[lv], TOP_HALF_W)]
            f.add(r"\draw[isotile, fill=tilestrong, line width=0.55pt] " + " -- ".join(f.p(x, y) for x, y in corners) + " -- cycle;")
    # the tile size, bracketed under the top tile's two front edges
    b0, b1, b2 = iso(0, 1, PYR_CX, rows[0], TOP_HALF_W), iso(0, 0, PYR_CX, rows[0], TOP_HALF_W), iso(1, 0, PYR_CX, rows[0], TOP_HALF_W)
    off = 4.0
    f.add(rf"\draw[bracegloss] {f.p(b1[0] - 1.5, b1[1] + off)} -- {f.p(b0[0], b0[1] + off)};")
    f.add(rf"\draw[bracegloss] {f.p(b2[0], b2[1] + off)} -- {f.p(b1[0] + 1.5, b1[1] + off)};")
    f.text((b0[0] + b1[0]) / 2 - 3, (b0[1] + b1[1]) / 2 + off + 15.0, r"$W$", f.s.pt_note, "base", gloss=True)
    f.text((b1[0] + b2[0]) / 2 + 3, (b1[1] + b2[1]) / 2 + off + 15.0, r"$W$", f.s.pt_note, "base", gloss=True)

    # ---- the point graph under the pyramid, in the same isometric frame
    tree_kd = cKDTree(pts)
    _, nb = tree_kd.query(pts, k=a.k + 1)
    gx = [iso(u, v, PYR_CX, graph_y, GRAPH_HALF_W) for u, v in pts]
    seen = set()
    for i in range(len(pts)):
        for j in nb[i, 1:]:
            e = (min(i, int(j)), max(i, int(j)))
            if e not in seen:
                seen.add(e)
                f.add(rf"\draw[black!70, line width=0.22pt] {f.p(*gx[e[0]])} -- {f.p(*gx[e[1]])};")
    for x, y in gx:                                  # dots squashed by the isometric frame, as measured (2.62 x 1.31 bp)
        f.add(rf"\fill[ink] {f.p(x, y)} ellipse (1.31bp and 0.655bp);")

    # ---- vertical dots: levels that are not drawn
    for x in (tree_nodes[path[a.levels - 1]][0] if a.levels - 1 < len(path) else TREE_X0 + TREE_W / 2, PYR_CX):
        for d in (0, 5, 10):
            f.add(rf"\fill[ink] {f.p(x, rows[-1] + 41.0 + d)} circle (0.8bp);")

    # ---- level labels: the level and its tile size
    for lv in range(a.levels):
        f.text(LBL_X, rows[lv] - 2.0, rf"$\ell = {lv}$", PT_LEVEL, "base west")
        size = "W" if lv == 0 else rf"W\!/{2 ** lv}"
        f.text(LBL_X, rows[lv] + 16.0, rf"${size}$", PT_SIZE, "base west", gloss=True)

    # ---- rows: tokens through blocks, with feedback rails
    s = f.s.scaled(chip=CHIP, chip_gap=CHIP_GAP, chip_cols=CHIPS, stack_rows=1)
    row = K.Figure(f.w, f.h, style=s, preamble=Path(a.preamble))
    row_w = CHIPS * CHIP + (CHIPS - 1) * CHIP_GAP
    for lv in range(a.levels):
        y = rows[lv]
        row.tokens(COL_IN, y, "tokorange")
        row.arrow(COL_IN + row_w / 2 + 3, y, COL_BOX - ROW_BOX_W / 2 - 1, y)
        row.box(COL_BOX, y, "self-attn", ROW_BOX_W, ROW_BOX_H, "opmint", PT_ROWBOX)
        row.arrow(COL_BOX + ROW_BOX_W / 2, y, COL_OUT - row_w / 2 - 3, y)
        row.tokens(COL_OUT, y, "tokblue")
        row.text(COL_OUT, y - 9.4, rf"$X^{{({lv})}}$", PT_SYM, "base", gloss=True)
    leaf_y = graph_y
    pools = [(rows[lv] + rows[lv + 1]) / 2 for lv in range(a.levels - 1)] + [(rows[-1] + leaf_y) / 2]
    for lv, py in enumerate(pools):                 # pool block between level lv (coarser) and the one below
        last = lv == a.levels - 1                    # between the last drawn level and the leaves: dashed
        row.box(COL_BOX, py, "pool", ROW_BOX_W, ROW_BOX_H, "oppeach", PT_ROWBOX)
        below_y = rows[lv + 1] if not last else leaf_y
        up_y = rows[lv] if not last else rows[-1]
        rail_bare, rail = ("railcontbare", "railcont") if last else ("railbare", "rail")
        # in from the right: the finer level's output (or the leaf tokens) runs right, up, and left into the block
        row.add(rf"\draw[{rail_bare}] {row.p(COL_OUT + row_w / 2 + 3, below_y)} -- {row.p(RAIL_R, below_y)} -- {row.p(RAIL_R, py)};")
        row.add(rf"\draw[{rail}] {row.p(RAIL_R, py)} -- {row.p(COL_BOX + ROW_BOX_W / 2 + 1, py)};")
        # out to the left: up into the coarser level's input tokens
        row.add(rf"\draw[{rail_bare}] {row.p(COL_BOX - ROW_BOX_W / 2, py)} -- {row.p(RAIL_L, py)} -- {row.p(RAIL_L, up_y)};")
        row.add(rf"\draw[{rail}] {row.p(RAIL_L, up_y)} -- {row.p(COL_IN - row_w / 2 - 3, up_y)};")
    # the leaf row: the point graph into the graph layer, out as the leaf tokens
    row.text(COL_BOX - ROW_BOX_W / 2 - 42, leaf_y - 2.0, "point graph", 14.3, "base east")
    row.text(COL_BOX - ROW_BOX_W / 2 - 42, leaf_y + 12.0, r"$k$ nearest neighbors", 12.7, "base east", gloss=True)
    row.arrow(COL_BOX - ROW_BOX_W / 2 - 36, leaf_y, COL_BOX - ROW_BOX_W / 2 - 1, leaf_y)
    row.box(COL_BOX, leaf_y, "graph", ROW_BOX_W, ROW_BOX_H, "opgray", PT_ROWBOX)
    row.arrow(COL_BOX + ROW_BOX_W / 2, leaf_y, COL_OUT - row_w / 2 - 3, leaf_y)
    row.tokens(COL_OUT, leaf_y, "tokyellow")
    row.text(COL_OUT, leaf_y - 9.4, r"$x_i$", PT_SYM, "base", gloss=True)
    f.o += row.o

    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    f.write(out / "hierarchy.tex")
    occupied = {lv: sum(1 for t in tiles if t[0] == lv) for lv in range(a.depth)}
    facts = {"seed": a.seed, "n_points": int(len(pts)), "capacity": a.capacity, "depth": a.depth,
             "levels_drawn": a.levels, "tiles_drawn_per_level": n_tiles, "occupied_tiles_per_level": occupied,
             "selected_point": {"index": sel, "xy": [round(float(v), 4) for v in pts[sel]],
                                "rule": "the point nearest the center of the field"},
             "path": [list(t) for t in path], "tree_children_drawn": {str(p[0]): sum(1 for e in edges if e[0] == p) for p in path[:a.levels - 1]},
             "graph": {"k": a.k, "edges": len(seen)}}
    (out / "facts.json").write_text(json.dumps(facts, indent=1) + "\n")
    print(f"ok  {len(pts)} points, quadtree depth {a.depth} (capacity {a.capacity}); drawn levels {a.levels}; "
          f"selected point {sel} on path {[t[1:] for t in path]}; {len(seen)} graph edges -> {out / 'hierarchy.tex'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
