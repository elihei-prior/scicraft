#!/usr/bin/env python3
"""Geometric audit of a compiled figure: what overlaps what. Reads the PDF, so it checks what is painted.

Text checks
  TEXT/TEXT    two words overlap. A sub- or superscript is its own span in the PDF, so spans that touch and
               differ in size (one at most 0.8 of the other) are glued into one word first, and an accent glyph
               (a CMEX span, or a span of accent characters such as a hat or tilde) is glued to the letter it
               sits on. Without the gluing, H_a^{(l)} audits as three words colliding with each other.
  STROKE/TEXT  a drawn segment passes through a word. A word that sits on a filled shape of its own (a label
               inside a filled box, a card name on its white mask) is excused: the fill paints over whatever
               runs beneath it.
  OFF-PAGE     a word outside the page.
Line checks (strokes against strokes)
  OVERLAP      two collinear axis-aligned segments share more than TOL bp: ink painted on ink, saying nothing.
  CROSS        a horizontal and a vertical segment meet at interior points of both. In a block diagram a
               crossing claims that two wires do NOT connect, so each one is removed or accepted on purpose.
               A crossing inside a join circle is a junction and is excused.
  STUB         a segment end stops within STUB bp of another segment without touching it: a wire that looks
               connected and is not, or a hairline gap at a corner.

Known residues are accepted by name in a residue file, one per line:
    KIND  substring of the finding as printed   # reason
for example
    STROKE/TEXT  'radius'   # 0.3 pt fragment of the dashed zoom connector, no ink at the word
An accepted finding is printed with its reason; a residue line that matches nothing is reported as stale.

Do not run it on a figure that includes clipped PDF artwork (a patched panel): the clipped-away paths are still
in the page and are reported. Use --region to restrict it to what is visible.

Needs PyMuPDF (pip install pymupdf). Exit 1 when a finding is not accepted.

Usage:
    python3 audit_layout.py fig.pdf
    python3 audit_layout.py fig.pdf --accept fig.residues
    python3 audit_layout.py fig.pdf --only text --region 0,0,400,300
"""
from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:  # pragma: no cover
    sys.exit("audit_layout.py needs PyMuPDF: pip install pymupdf")

MIN_LEN = 1.5      # bp: shorter straight pieces are polyline approximations of curves, not wiring
SMALL = 8.0        # bp: a filled shape smaller than this (arrow tip, chip cell, marker) is not a stub target
TOUCH = 0.25       # bp: ink this close touches (half of a 0.45 pt stroke)
ACCENTS = set("ˆ˜¯˙¨´`ˇ˘→⃗~^")


def text_dict(page, line_boxes: bool):
    """Spans with accurate boxes when PyMuPDF offers them (TEXT_ACCURATE_BBOXES). Inside an included PDF a symbol
    font's line box came out twice the height of its glyph and reached past the box the glyph sits in; with the
    flag it is the glyph's. In a standalone PDF the flag returned the same line boxes, so the 0.6 bp slack stays."""
    flag = getattr(fitz, "TEXT_ACCURATE_BBOXES", 0)
    if line_boxes or not flag:
        return page.get_text("dict")
    return page.get_text("dict", flags=fitz.TEXTFLAGS_DICT | flag)


def words(page, glue: float, region, line_boxes: bool = False):
    """[(Rect, text, size)] with scripts and accents glued to their base."""
    raw = []
    for b in text_dict(page, line_boxes)["blocks"]:
        for ln in b.get("lines", []):
            for sp in ln["spans"]:
                t = sp["text"].strip()
                if not t:
                    continue
                r = fitz.Rect(sp["bbox"])
                if region and not region.intersects(r):
                    continue
                accent = sp["font"].upper().startswith("CMEX") or all(ch in ACCENTS for ch in t)
                raw.append((r, t, sp["size"], accent))
    out = []
    for r, t, sz, accent in sorted(raw, key=lambda q: q[3]):          # bases first, accents last
        for i, (rj, tj, sj) in enumerate(out):
            touching = fitz.Rect(rj.x0 - glue, rj.y0 - glue, rj.x1 + glue, rj.y1 + glue).intersects(r)
            script = min(sz, sj) <= 0.8 * max(sz, sj)    # TeX scripts run at 0.5 to 0.7 of the base size
            if touching and (script or accent):
                out[i] = (rj | r, tj + t, max(sz, sj))
                break
        else:
            out.append((r, t, sz))
    return out


def bezier(p0, p1, p2, p3, n=8):
    pts = []
    for k in range(n + 1):
        u = k / n
        a, b, c, d = (1 - u) ** 3, 3 * u * (1 - u) ** 2, 3 * u * u * (1 - u), u ** 3
        pts.append(fitz.Point(a * p0.x + b * p1.x + c * p2.x + d * p3.x, a * p0.y + b * p1.y + c * p2.y + d * p3.y))
    return list(zip(pts[:-1], pts[1:]))


def drawings(page, region):
    """Return (all, wires, straight, fills, joins).

    all       every stroked segment, curves sampled (for strokes through text);
    wires     straight segments of stroked paths WITHOUT a fill: the wiring (crossings, stub ends);
    straight  straight segments of every stroked path, wires and shape outlines (doubled ink, stub targets);
    fills     rectangles of filled shapes: a word inside one sits on its own backdrop;
    joins     small stroked circles (join circles): a crossing inside one is a junction.
    The outline of a filled shape is not a wire: stacked chips cross each other's edges behind their fills."""
    allseg, wires, straight, fills, joins, inks = [], [], [], [], [], []
    for d in page.get_drawings():
        r = d["rect"]
        if region and not region.intersects(r):
            continue
        items = d["items"]
        filled = d.get("fill") is not None
        if filled and r.width > 2 and r.height > 2:
            fills.append(fitz.Rect(r))
        if filled:
            inks.append(fitz.Rect(r))                  # any filled shape: a wire end on it is connected
        kinds = [it[0] for it in items]
        if kinds and all(k == "c" for k in kinds) and len(kinds) >= 4 and abs(r.width - r.height) < 0.6 \
                and r.width < 30 and d.get("color") is not None:
            joins.append(((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2, r.width / 2 + 1.0))
        if d.get("color") is None:                 # fill only (arrow tips, dots): not a stroke
            continue
        lines = []
        for it in items:
            if it[0] == "l":
                lines.append((it[1], it[2]))
            elif it[0] == "c":
                allseg.extend(bezier(it[1], it[2], it[3], it[4]))
            elif it[0] == "re":
                q = fitz.Rect(it[1])
                lines += [(fitz.Point(q.x0, q.y0), fitz.Point(q.x1, q.y0)), (fitz.Point(q.x1, q.y0), fitz.Point(q.x1, q.y1)),
                          (fitz.Point(q.x1, q.y1), fitz.Point(q.x0, q.y1)), (fitz.Point(q.x0, q.y1), fitz.Point(q.x0, q.y0))]
            elif it[0] == "qu":
                qd = it[1]
                pts = [qd.ul, qd.ur, qd.lr, qd.ll]
                lines += list(zip(pts, pts[1:] + pts[:1]))
        allseg += lines
        long = [(p, q) for p, q in lines if abs(p.x - q.x) + abs(p.y - q.y) >= MIN_LEN]
        if filled and (r.width < SMALL or r.height < SMALL):
            continue                               # arrow tips, chips, markers: not wiring, not stub targets
        straight += long
        if not filled:
            wires += long
    return allseg, wires, straight, fills, joins, inks


def hits(p0, p1, r):
    n = max(2, int(max(abs(p1.x - p0.x), abs(p1.y - p0.y)) / 0.4))
    return any(r.contains(fitz.Point(p0.x + (p1.x - p0.x) * t / n, p0.y + (p1.y - p0.y) * t / n)) for t in range(n + 1))


def text_findings(page, a, region):
    found = []
    ws = words(page, a.glue, region, a.line_boxes)
    segs, _, _, fills, _, _ = drawings(page, region)
    for i in range(len(ws)):
        for j in range(i + 1, len(ws)):
            ri = ws[i][0] + (a.pad, a.pad, -a.pad, -a.pad)
            if ri.intersects(ws[j][0]):
                found.append(("TEXT/TEXT", f"{ws[i][1]!r} x {ws[j][1]!r}"))
    for r, t, _ in ws:
        if any(f.contains(r + (0.5, 0.5, -0.5, -0.5)) for f in fills):
            continue
        rr = r + (a.pad, a.pad, -a.pad, -a.pad)
        if rr.is_empty:
            continue
        for p0, p1 in segs:
            if max(p0.x, p1.x) < rr.x0 or min(p0.x, p1.x) > rr.x1 or max(p0.y, p1.y) < rr.y0 or min(p0.y, p1.y) > rr.y1:
                continue
            if hits(p0, p1, rr):
                found.append(("STROKE/TEXT", f"{t!r} segment ({p0.x:.1f},{p0.y:.1f})-({p1.x:.1f},{p1.y:.1f})"))
                break
    R = region or page.rect
    for r, t, _ in ws:
        if r.x0 < R.x0 - 0.5 or r.y0 < R.y0 - 0.5 or r.x1 > R.x1 + 0.5 or r.y1 > R.y1 + 0.5:
            found.append(("OFF-PAGE", f"{t!r} {tuple(round(v, 1) for v in r)}"))
    return found, len(ws)


def lanes_of(segs, eps=0.05):
    """Axis-aligned segments grouped by their line: {('h', y) or ('v', x): [(lo, hi), ...]}."""
    lanes = defaultdict(list)
    for p, q in segs:
        if abs(p.y - q.y) < eps and abs(p.x - q.x) > eps:
            lanes[("h", round(p.y, 2))].append((min(p.x, q.x), max(p.x, q.x)))
        elif abs(p.x - q.x) < eps and abs(p.y - q.y) > eps:
            lanes[("v", round(p.x, 2))].append((min(p.y, q.y), max(p.y, q.y)))
    return lanes


def line_findings(page, a, region):
    _, wires, straight, _, joins, inks = drawings(page, region)
    eps = 0.05
    lanes = lanes_of(straight, eps)                # doubled ink: wires and outlines alike
    wlanes = lanes_of(wires, eps)                  # crossings: wire against wire
    found = []
    for (k, c), its in lanes.items():
        its.sort()
        for i in range(len(its)):
            for j in range(i + 1, len(its)):
                if its[j][0] > its[i][1]:
                    break
                lo, hi = max(its[i][0], its[j][0]), min(its[i][1], its[j][1])
                if hi - lo > a.tol:
                    found.append(("OVERLAP", f"{k} at {c} from {lo:.1f} to {hi:.1f} ({hi - lo:.1f} bp of doubled ink)"))
    H = [(c, lo, hi) for (k, c), its in wlanes.items() if k == "h" for lo, hi in its]
    V = [(c, lo, hi) for (k, c), its in wlanes.items() if k == "v" for lo, hi in its]
    for hy, hx0, hx1 in H:
        for vx, vy0, vy1 in V:
            if hx0 + a.tol < vx < hx1 - a.tol and vy0 + a.tol < hy < vy1 - a.tol:
                if any(abs(vx - jx) <= jr and abs(hy - jy) <= jr for jx, jy, jr in joins):
                    continue
                found.append(("CROSS", f"at ({vx:.1f},{hy:.1f})"))
    seen = set()
    # ends of axis-aligned wires only: the check is about orthogonal wiring; a diagonal graph edge that ends at
    # its node next to another edge is not a stub
    ends = [p for s in wires for p in s if abs(s[0].x - s[1].x) < eps or abs(s[0].y - s[1].y) < eps]
    for p in ends:
        if any(fitz.Rect(r.x0 - TOUCH, r.y0 - TOUCH, r.x1 + TOUCH, r.y1 + TOUCH).contains(p) for r in inks if r.width < SMALL):
            continue                                   # the end lies on a dot or an arrowhead: it is connected
        for (k, c), its in lanes.items():
            d = abs(p.y - c) if k == "h" else abs(p.x - c)
            if not TOUCH < d < a.stub:
                continue
            along = p.x if k == "h" else p.y
            if any(lo - a.tol < along < hi + a.tol for lo, hi in its):
                key = (round(p.x, 1), round(p.y, 1))
                if key not in seen:
                    seen.add(key)
                    found.append(("STUB", f"end ({p.x:.1f},{p.y:.1f}) stops {d:.2f} bp short of a {k} line"))
    return found, len(straight)


def read_residues(path):
    out = []
    for ln in Path(path).read_text().splitlines():
        body, _, reason = ln.partition("#")
        body = body.strip()
        if not body:
            continue
        kind, _, pat = body.partition(" ")
        out.append([kind.strip(), pat.strip(), reason.strip(), 0])
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Audit a compiled figure for text and line collisions (PyMuPDF).",
                                 epilog=__doc__.split("Usage:")[0], formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pdf", type=Path)
    ap.add_argument("--accept", type=Path, help="residue file: KIND  substring  # reason")
    ap.add_argument("--only", choices=["text", "lines"], help="run one family of checks")
    ap.add_argument("--region", help="x0,y0,x1,y1 in bp from the top left: audit only this part of the page")
    ap.add_argument("--page", type=int, default=1, help="page number (default 1)")
    ap.add_argument("--pad", type=float, default=0.6, help="slack inside a word box, bp (default 0.6)")
    ap.add_argument("--line-boxes", action="store_true",
                    help="use line boxes (font ascender to descender) instead of ink boxes, as the source auditors did")
    ap.add_argument("--glue", type=float, default=1.5, help="distance that glues a script to its base, bp (1.5)")
    ap.add_argument("--tol", type=float, default=0.35, help="shared length that counts as doubled ink, bp (0.35)")
    ap.add_argument("--stub", type=float, default=1.2, help="gap that counts as a stub, bp (1.2)")
    a = ap.parse_args()
    page = fitz.open(str(a.pdf))[a.page - 1]
    region = fitz.Rect(*map(float, a.region.split(","))) if a.region else None
    found, n_words, n_segs = [], 0, 0
    if a.only in (None, "text"):
        f, n_words = text_findings(page, a, region)
        found += f
    if a.only in (None, "lines"):
        f, n_segs = line_findings(page, a, region)
        found += f
    res = read_residues(a.accept) if a.accept else []
    bad = 0
    for kind, msg in found:
        hit = next((r for r in res if r[0] == kind and r[1] in f"{kind} {msg}"), None)
        if hit:
            hit[3] += 1
            print(f"accepted  {kind:11s} {msg}   ({hit[2]})")
        else:
            print(f"{kind:11s} {msg}")
            bad += 1
    for r in res:
        if r[3] == 0:
            print(f"stale residue (matches nothing): {r[0]} {r[1]}")
    print(f"\n{a.pdf.name}: {n_words} words, {n_segs} segments -> {bad} finding(s)"
          + (f", {len(found) - bad} accepted" if len(found) - bad else ""))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
