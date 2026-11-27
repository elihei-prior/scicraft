#!/usr/bin/env python3
"""Printed size of every type size of a figure, from its design width and its print width. Fails under the floor.

Figures in this style are drawn large and printed small: a card figure 850 bp wide set at 0.98 of a 396 bp text
block prints at scale 0.457, so 13 pt notes print at 5.9 pt. Every version of the source figures before this was
computed shipped type at 3.5 pt on the page.

Two ways to run it:
  plan     --design-width and --sizes: before drawing, check the sizes you mean to use;
  measure  a compiled PDF: every text span is read (PyMuPDF), its size times the scale is its printed size.
           Sub- and superscripts (a span at most 0.8 of the size of a span it touches) are reported apart from
           base text: they follow TeX's script ratio and the floor applies to the base sizes they belong to.

Print width can be given in bp, pt, mm, cm or in (`388bp`, `13.97cm`) or as a fraction of a width
(`0.98x396bp`, the usual `.98\\linewidth` of a 5.5 in text block).

The floor (5 pt) and the tiers (7, 6, 5 pt, an 8 pt bold letter) are the package's (sibling skill data-figures);
in-cell values of a dense matrix may go to 3.3 pt (--cell-floor), never lower. Text baked into a raster (a scale-bar
label in a tile) is not in the text layer: compute it from the tile's own numbers (tiles.py reports it).

Needs PyMuPDF for the measure mode. Exit 1 when a base size prints under the floor.

Usage:
    python3 print_scale.py fig.pdf --print-width 0.98x396bp
    python3 print_scale.py --design-width 850 --print-width 388 --sizes 14,13.6,13.2,13,10.76
    python3 print_scale.py fig.pdf --print-width 13.97cm --floor 5 --cell-floor 3.3
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

UNIT = {"bp": 1.0, "pt": 72 / 72.27, "mm": 72 / 25.4, "cm": 72 / 2.54, "in": 72.0}


def to_bp(s: str) -> float:
    """'388bp', '13.97cm', '0.98x396bp', '396' (bp) -> bp."""
    s = s.strip().replace(" ", "")
    m = re.fullmatch(r"(?:([\d.]+)x)?([\d.]+)(bp|pt|mm|cm|in)?", s)
    if not m:
        raise SystemExit(f"cannot read the width {s!r}; use 388bp, 13.97cm or 0.98x396bp")
    frac = float(m.group(1)) if m.group(1) else 1.0
    return frac * float(m.group(2)) * UNIT[m.group(3) or "bp"]


def spans(pdf: Path, page: int = 1, region=None):
    import fitz
    pg = fitz.open(str(pdf))[page - 1]
    out = []
    for b in pg.get_text("dict")["blocks"]:
        for ln in b.get("lines", []):
            for sp in ln["spans"]:
                r = fitz.Rect(sp["bbox"])
                if sp["text"].strip() and (region is None or region.intersects(r)):
                    out.append((r, sp["text"].strip(), sp["size"], sp["font"]))
    return pg, out


def classify(sp):
    """Mark each span base or script. A script is at most 0.8 of the size of a span its box touches, or the same
    size as a script it touches (the far end of a long superscript touches only the rest of the superscript)."""
    import fitz
    grown = [fitz.Rect(r.x0 - 1.5, r.y0 - 1.5, r.x1 + 1.5, r.y1 + 1.5) for r, _, _, _ in sp]
    script = [any(j != i and grown[i].intersects(sp[j][0]) and sp[i][2] <= 0.8 * sp[j][2] for j in range(len(sp)))
              for i in range(len(sp))]
    changed = True
    while changed:
        changed = False
        for i in range(len(sp)):
            if not script[i] and any(script[j] and j != i and grown[i].intersects(sp[j][0])
                                     and abs(sp[i][2] - sp[j][2]) <= 0.05 * sp[j][2] for j in range(len(sp))):
                script[i] = changed = True
    return ["script" if s else "base" for s in script]


def tiers(sizes, tol=0.10):
    """Group printed sizes into tiers: sizes within 10 percent of a tier's smallest member join it."""
    out = []
    for s in sorted(sizes):
        if out and s <= out[-1][0] * (1 + tol):
            out[-1].append(s)
        else:
            out.append([s])
    return [(min(t), max(t)) for t in out]


def main() -> int:
    ap = argparse.ArgumentParser(description="Printed size of every type size of a figure; fails under the floor.",
                                 epilog=__doc__.split("Usage:")[0], formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf", nargs="?", type=Path, help="a compiled figure (measure mode)")
    ap.add_argument("--print-width", required=True, help="width on the page: 388bp, 13.97cm, 0.98x396bp")
    ap.add_argument("--design-width", type=float, help="design width in bp (default: the PDF's page width)")
    ap.add_argument("--sizes", help="plan mode: comma-separated design sizes in pt")
    ap.add_argument("--floor", type=float, default=5.0, help="smallest printed base size, pt (default 5)")
    ap.add_argument("--cell-floor", type=float, default=3.3, help="floor for --cell-sizes, pt (default 3.3)")
    ap.add_argument("--cell-sizes", help="design sizes used only for in-cell values of a dense matrix")
    ap.add_argument("--ceiling", type=float, default=10.5,
                    help="warn when base type prints above this, pt (default 10.5, the largest letter the package "
                         "allows): a figure drawn to print at half size and placed at full width")
    ap.add_argument("--page", type=int, default=1)
    ap.add_argument("--region", help="x0,y0,x1,y1 in bp: only text there (a patched figure keeps hidden text "
                                     "under its paint and outside its clips; the text layer reports it too)")
    a = ap.parse_args()
    pw = to_bp(a.print_width)
    bad = 0
    if a.sizes:
        if not a.design_width:
            raise SystemExit("plan mode needs --design-width")
        sc = pw / a.design_width
        print(f"design {a.design_width:.1f} bp -> print {pw:.1f} bp: scale {sc:.3f}")
        cells = {float(x) for x in a.cell_sizes.split(",")} if a.cell_sizes else set()
        for s in sorted({float(x) for x in a.sizes.split(",")} | cells, reverse=True):
            p = s * sc
            floor = a.cell_floor if s in cells else a.floor
            flag = "UNDER" if p < floor - 1e-9 else "ok"
            bad += flag == "UNDER"
            print(f"  {s:6.2f} pt -> {p:5.2f} pt  {flag}" + ("  (in-cell value)" if s in cells else ""))
        print(f"\n{'FAIL' if bad else 'ok'}: {bad} size(s) under the floor of {a.floor} pt")
        return 1 if bad else 0
    if not a.pdf:
        raise SystemExit("give a PDF, or --sizes with --design-width")
    try:
        import fitz
        region = fitz.Rect(*map(float, a.region.split(","))) if a.region else None
        pg, sp = spans(a.pdf, a.page, region)
    except ImportError:
        raise SystemExit("measure mode needs PyMuPDF: pip install pymupdf")
    dw = a.design_width or pg.rect.width
    sc = pw / dw
    kinds = classify(sp)
    rows = {}
    for (r, t, sz, fnt), k in zip(sp, kinds):
        key = (round(sz, 2), k)
        rows.setdefault(key, []).append(t)
    print(f"{a.pdf.name}: design {dw:.1f} bp -> print {pw:.1f} bp, scale {sc:.3f}")
    cells = {float(x) for x in a.cell_sizes.split(",")} if a.cell_sizes else set()
    for (sz, k), texts in sorted(rows.items(), key=lambda kv: -kv[0][0]):
        p = sz * sc
        in_cell = any(abs(sz - c * 72 / 72.27) < 0.05 for c in cells)
        floor = a.cell_floor if in_cell else a.floor
        flag = "ok"
        if p < floor - 1e-9:
            flag = "UNDER" if k == "base" else "script under the floor"
            bad += k == "base"
        ex = ", ".join(sorted(set(texts))[:4])
        print(f"  {sz:6.2f} bp {k:6s} -> {p:5.2f} pt  {flag:24s} {len(texts):3d} span(s): {ex[:60]}")
    base = [s for (s, k) in rows if k == "base"]
    if base and max(base) * sc > a.ceiling:
        print(f"  warn: base type prints up to {max(base) * sc:.1f} pt, above {a.ceiling} pt; the design width is too "
              f"small for this print width (draw it wider, or print it smaller)")
    if base:
        tl = tiers([s * sc for s in base])
        print(f"  base type in {len(tl)} tier(s) on the page: " + ", ".join(f"{lo:.1f}" + (f" to {hi:.1f}" if hi > lo else "") + " pt" for lo, hi in tl))
        if len(tl) > 4:
            print("  note: more than four tiers; the package allows three, four at most")
    try:
        widths = [d.get("width") for d in pg.get_drawings() if d.get("color") is not None and d.get("width")]
        if widths:
            print(f"  thinnest stroke {min(widths):.3f} bp -> {min(widths) * sc:.3f} pt on the page")
    except Exception:  # noqa: BLE001
        pass
    print("  raster text (labels baked into tiles) is not in the text layer and was not checked")
    print(f"\n{'FAIL' if bad else 'ok'}: {bad} base size(s) under the floor of {a.floor} pt")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
