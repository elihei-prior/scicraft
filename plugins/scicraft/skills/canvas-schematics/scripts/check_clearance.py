"""Clearance check of a figure, on the printed vector PDF and its rendered ink, not on layout boxes.

render.js --check looks only at text boxes against text boxes. This script also catches text running onto a tile, an
icon or a brace, shapes that nearly touch, and panels or tables crowding each other. The page is rendered twice at
DPI: once as printed, once with every text span redacted (graphics kept). Text ink is where the two differ, graphic ink
is every non-white pixel of the second.

Checks (all distances measured on ink, in mm):
  text over graphic      FAIL  text ink on graphic ink
  text near graphic      FAIL  gap below --text-gap
  text near text         FAIL  two labels (different lines) closer than --text-text
  shapes nearly touching WARN  two separate ink islands closer than --shape-gap
  panel gap              FAIL  white between the ink of panel a and of panel b narrower than --panel-gap
  gutters of b           FAIL  white between the table columns (--col-gap) or rows (--row-gap) of b narrower than asked;
                               0 turns the measure off (a data figure has no table gutters)

Two labels of one text object (a label on two lines) are never compared with each other. With --cells, text that sits
inside one filled shape with a margin on every side (a value in a heat-map cell) is not counted as text on a graphic.

Writes <out>_clearance.png (every flag boxed: red FAIL, orange WARN) and <out>_islands.png (each ink island in its own
color, so two objects that touch show as one color). Exit 1 on any FAIL.

  python3 scripts/check_clearance.py figure.pdf            # needs pymupdf, numpy, scipy, pillow
  python3 scripts/check_clearance.py figure.pdf --panel-gap 6 --col-gap 4 --row-gap 4

The panel letters must be the single characters 'a' and 'b' in the PDF text for the panel and gutter measures; the
other checks work on any page.
"""
from __future__ import annotations

import argparse
import itertools
import sys
from pathlib import Path

import pymupdf as fitz
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage

MM_PER_PT = 25.4 / 72


def render(page: fitz.Page, dpi: int) -> np.ndarray:
    pix = page.get_pixmap(dpi=dpi, alpha=False)
    return np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, :3].astype(np.int16)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf")
    ap.add_argument("--dpi", type=int, default=600)
    ap.add_argument("--text-gap", type=float, default=0.25, help="mm of white between text ink and graphic ink")
    ap.add_argument("--text-text", type=float, default=0.35, help="mm between two labels")
    ap.add_argument("--shape-gap", type=float, default=0.12, help="mm between two ink islands")
    ap.add_argument("--panel-gap", type=float, default=9.0, help="mm of white between panel a and panel b")
    ap.add_argument("--col-gap", type=float, default=6.0, help="mm between the table columns of b")
    ap.add_argument("--row-gap", type=float, default=5.0, help="mm between the two rows of b")
    ap.add_argument("--cells", action="store_true",
                    help="allow text set inside one filled shape (values in heat-map cells, a symbol in its tile)")
    ap.add_argument("--out", default=None, help="prefix of the two PNGs (default: next to the PDF)")
    a = ap.parse_args()

    pdf = Path(a.pdf)
    doc = fitz.open(pdf)
    page = doc[0]
    px_mm = a.dpi / 25.4
    full = render(page, a.dpi)

    # text spans, by line (spans of one line are one label: a bold number and its unit)
    spans = []
    for b in page.get_text("dict")["blocks"]:
        for li, line in enumerate(b.get("lines", [])):
            for s in line["spans"]:
                if s["text"].strip():
                    spans.append({"text": s["text"].strip(), "bbox": fitz.Rect(s["bbox"]), "line": (b["number"], li),
                                  "block": b["number"]})

    art_doc = fitz.open(pdf)
    art_page = art_doc[0]
    for s in spans:
        art_page.add_redact_annot(s["bbox"], fill=False)
    art_page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE, graphics=fitz.PDF_REDACT_LINE_ART_NONE,
                              text=fitz.PDF_REDACT_TEXT_REMOVE)
    art = render(art_page, a.dpi)

    text_ink = np.abs(full - art).max(axis=2) > 40
    art_ink = art.min(axis=2) < 244                              # white tiles are not ink, their faint outline is
    H, W = art_ink.shape
    to_mm = lambda v: v / px_mm                                  # noqa: E731
    box_px = lambda r, pad=0: (max(0, int(r.x0 * a.dpi / 72) - pad), max(0, int(r.y0 * a.dpi / 72) - pad),  # noqa: E731
                               min(W, int(np.ceil(r.x1 * a.dpi / 72)) + pad), min(H, int(np.ceil(r.y1 * a.dpi / 72)) + pad))

    fails, warns = [], []
    dist_to_art = ndimage.distance_transform_edt(~art_ink)       # px to the nearest graphic ink
    lab, n = ndimage.label(art_ink, structure=np.ones((3, 3)))
    objs = ndimage.find_objects(lab)
    margin = int(round(0.15 * px_mm))

    def inside_one_shape(x0, y0, x1, y1) -> bool:
        """True when all graphic ink around the text belongs to one island that encloses the text with margin."""
        ids = np.unique(lab[y0:y1, x0:x1]); ids = ids[ids > 0]
        if len(ids) != 1:
            return False
        sy, sx = objs[ids[0] - 1]
        return sx.start <= x0 - margin and sx.stop >= x1 + margin and sy.start <= y0 - margin and sy.stop >= y1 + margin

    # 1. text against graphics
    for s in spans:
        x0, y0, x1, y1 = box_px(s["bbox"], pad=2)
        mine = text_ink[y0:y1, x0:x1]
        if not mine.any():
            continue
        over = (mine & art_ink[y0:y1, x0:x1]).sum()
        gap = to_mm(dist_to_art[y0:y1, x0:x1][mine].min())
        s["ink"] = (x0, y0, x1, y1)
        if a.cells and inside_one_shape(x0, y0, x1, y1):
            continue                                             # a label set inside its own cell or tile
        if over > 4:
            fails.append((f"text over graphic: '{s['text']}' ({over} px of ink under it) at x {to_mm(x0):.1f}, y {to_mm(y0):.1f} mm", (x0, y0, x1, y1)))
        elif gap < a.text_gap:
            fails.append((f"text {gap:.2f} mm from a graphic: '{s['text']}' at x {to_mm(x0):.1f}, y {to_mm(y0):.1f} mm", (x0, y0, x1, y1)))

    cache = {}
    def own_ink(sp):                                             # the ink of one span alone
        k = id(sp)
        if k not in cache:
            d = fitz.open(pdf); pg = d[0]
            for o in spans:
                if o is not sp:
                    pg.add_redact_annot(o["bbox"], fill=False)
            pg.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE, graphics=fitz.PDF_REDACT_LINE_ART_NONE,
                                text=fitz.PDF_REDACT_TEXT_REMOVE)
            cache[k] = np.abs(render(pg, a.dpi) - art).max(axis=2) > 40
        return cache[k]

    # 2. text against text (labels on different lines)
    for p, q in itertools.combinations([s for s in spans if "ink" in s], 2):
        if p["line"] == q["line"] or p["block"] == q["block"]:
            continue                                             # one text object, such as a label on two lines
        dx = max(0.0, max(p["bbox"].x0, q["bbox"].x0) - min(p["bbox"].x1, q["bbox"].x1))
        dy = max(0.0, max(p["bbox"].y0, q["bbox"].y0) - min(p["bbox"].y1, q["bbox"].y1))
        if dx * MM_PER_PT < a.text_text and dy * MM_PER_PT < a.text_text:
            # the span boxes include ascender and descender space: measure on ink before calling it
            pm, qm = own_ink(p), own_ink(q)
            if pm.any() and qm.any():
                d = to_mm(ndimage.distance_transform_edt(~pm)[qm].min())
                if d < a.text_text:
                    fails.append((f"text {d:.2f} mm from text: '{p['text']}' / '{q['text']}'", box_px(p["bbox"] | q["bbox"])))

    # 3. ink islands that nearly touch
    reach = int(np.ceil(a.shape_gap * px_mm)) + 1
    near = []
    for i, sl in enumerate(objs, start=1):
        y0, y1 = max(0, sl[0].start - reach), min(H, sl[0].stop + reach)
        x0, x1 = max(0, sl[1].start - reach), min(W, sl[1].stop + reach)
        win = lab[y0:y1, x0:x1]
        mine = win == i
        grown = ndimage.binary_dilation(mine, iterations=reach)
        for j in np.unique(win[grown & (win > 0) & ~mine]):
            if j > i:
                d = to_mm(ndimage.distance_transform_edt(~mine)[win == j].min())
                if d < a.shape_gap:
                    near.append((d, i, j, (x0, y0, x1, y1)))
    for d, i, j, box in near:
        yi, xi = objs[i - 1]; yj, xj = objs[j - 1]
        where = f"at x {to_mm((xi.start + xj.stop) / 2):.1f}, y {to_mm((yi.start + yj.stop) / 2):.1f} mm"
        size = f"{to_mm(xi.stop - xi.start):.1f} x {to_mm(yi.stop - yi.start):.1f} and {to_mm(xj.stop - xj.start):.1f} x {to_mm(yj.stop - yj.start):.1f} mm"
        warns.append((f"two shapes {d:.2f} mm apart {where} (sizes {size})", box))

    # 4. panel gap and the gutters of b, on all ink
    ink = art_ink | text_ink
    letters = {s["text"]: s["bbox"] for s in spans if s["text"] in ("a", "b")}
    gaps = {}
    if "b" in letters:
        bx = int(letters["b"].x0 * a.dpi / 72)
        cols = ink.any(axis=0)
        lim = min(W, bx + int(3 * px_mm))
        white = [k for k in range(lim) if not cols[k]]
        runs_a, start = [], None
        for k in range(lim):
            if not cols[k] and start is None:
                start = k
            elif cols[k] and start is not None:
                runs_a.append((start, k)); start = None
        runs_a = [r for r in runs_a if r[0] > 0]
        if runs_a:
            r0, r1 = runs_a[-1]                                  # the white just before panel b's first ink
            gaps["a to b"] = to_mm(r1 - r0)
            if gaps["a to b"] < a.panel_gap:
                fails.append((f"panel a to b: {gaps['a to b']:.1f} mm of white (asked {a.panel_gap})", (r0, 0, r1, H)))
        else:
            gaps["a to b"] = 0.0
            fails.append(("panel a to b: no white column between them", (bx - 20, 0, bx + 20, H)))
        # gutters of b: white columns and rows inside b, below its title line
        top = int((letters["b"].y1 + 2 / MM_PER_PT) * a.dpi / 72)
        sub = ink[top:, bx:]
        def runs(v):
            out, start = [], None
            for k, x in enumerate(v):
                if not x and start is None:
                    start = k
                elif x and start is not None:
                    out.append((start, k)); start = None
            return out
        colruns = [r for r in runs(sub.any(axis=0)) if r[0] > 0] if a.col_gap > 0 else []
        inner = [r for r in colruns if r[1] < sub.shape[1]]
        big = sorted(inner, key=lambda r: r[1] - r[0], reverse=True)[:2]
        for r0, r1 in sorted(big):
            g = to_mm(r1 - r0)
            gaps[f"b column gutter at {to_mm(bx + r0):.0f} mm"] = g
            if g < a.col_gap:
                fails.append((f"b column gutter {g:.1f} mm (asked {a.col_gap})", (bx + r0, top, bx + r1, H)))
        rowruns = [r for r in runs(sub.any(axis=1)) if 0 < r[0] and r[1] < sub.shape[0]] if a.row_gap > 0 else []
        if rowruns:
            r0, r1 = max(rowruns, key=lambda r: r[1] - r[0])
            g = to_mm(r1 - r0)
            gaps["b row gutter"] = g
            if g < a.row_gap:
                fails.append((f"b row gutter {g:.1f} mm (asked {a.row_gap})", (bx, top + r0, W, top + r1)))

    # pictures for the eye
    prefix = Path(a.out) if a.out else pdf.with_suffix("")
    img = Image.fromarray(full.astype(np.uint8))
    dr = ImageDraw.Draw(img)
    for msg, (x0, y0, x1, y1) in warns:
        dr.rectangle([x0 - 6, y0 - 6, x1 + 6, y1 + 6], outline=(255, 150, 0), width=4)
    for msg, (x0, y0, x1, y1) in fails:
        dr.rectangle([x0 - 6, y0 - 6, x1 + 6, y1 + 6], outline=(230, 0, 0), width=5)
    img.save(f"{prefix}_clearance.png")
    rng = np.random.default_rng(1)
    pal = np.vstack([[255, 255, 255], rng.integers(30, 220, size=(n, 3))]).astype(np.uint8)
    Image.fromarray(pal[lab]).save(f"{prefix}_islands.png")

    print(f"clearance of {pdf.name}: {len(spans)} text spans, {n} ink islands, at {a.dpi} dpi")
    for k, v in gaps.items():
        print(f"  {k}: {v:.1f} mm")
    for msg, _ in fails:
        print("FAIL", msg)
    for msg, _ in warns:
        print("WARN", msg)
    print(f"{len(fails)} fail(s), {len(warns)} warning(s); pictures: {prefix}_clearance.png, {prefix}_islands.png")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
