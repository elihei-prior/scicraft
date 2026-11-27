#!/usr/bin/env python3
"""Compose panel PDFs into one figure: one row, every panel set to one height, letters one size on one baseline.

The composition is written by this script from the panels' REAL page sizes, so it cannot drift when a panel
changes: rebuild a panel, rerun this, recompile. Two looks, both from the source figures:
  letters   a bare bold letter per panel (20 bp, its baseline 17 bp under the top), the first at the left edge, the
            others right-aligned to their panel's left edge in the gap before it;
  titles    "a)  Name" over each panel (16 pt, bold letter and parenthesis, two spaces, a name of two to four
            words), all on one baseline, with thin rules (0.4 pt black!22) between the panels.
It reports the scale on the page and the smallest printed type of every panel (PyMuPDF), and fails when a base
size prints under the floor.

The preamble is read for the type, so the letters and titles are in the figures' own font.

Needs pdfinfo (poppler) or PyMuPDF for the page sizes, PyMuPDF for the type report, pdflatex with --compile.

Usage:
    python3 compose.py fig.tex a.pdf b.pdf --letters a,b --print-width 0.98x396bp --compile
    python3 compose.py fig.tex a.pdf b.pdf c.pdf --titles "Point field|Training|Embedding map" --rules \\
        --height 380 --print-width 13.97cm --compile
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
sys.dont_write_bytecode = True        # importing a sibling must not leave __pycache__ in the skill
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from print_scale import classify, spans, to_bp  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "assets"))
import figkit  # noqa: E402

PREAMBLE = HERE.parent / "assets" / "preamble.tex"


def page_size(pdf: Path):
    try:
        import fitz
        r = fitz.open(str(pdf))[0].rect
        return r.width, r.height
    except ImportError:
        out = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
        w, _, h = out.split("Page size:")[1].split("\n")[0].split()[:3]
        return float(w), float(h)


def smallest_base(pdf: Path):
    try:
        _, sp = spans(pdf)
    except ImportError:
        return None
    kinds = classify(sp)
    base = [s[2] for s, k in zip(sp, kinds) if k == "base"]
    return min(base) if base else None


def main() -> int:
    ap = argparse.ArgumentParser(description="Compose panel PDFs into one row at one height, with letters or titles.")
    ap.add_argument("out", type=Path, help="the composition .tex to write")
    ap.add_argument("panels", nargs="+", type=Path, help="panel PDFs, left to right")
    ap.add_argument("--height", type=float, help="common panel height in bp (default: the first panel's)")
    ap.add_argument("--gap", type=float, default=20.0, help="gap between panels, bp (default 20; it holds a letter)")
    ap.add_argument("--letters", help="comma-separated letters, e.g. a,b,c (bare bold letters)")
    ap.add_argument("--titles", help="names separated by |, e.g. 'Point field|Training' (letter) Name titles")
    ap.add_argument("--rules", action="store_true", help="thin vertical rules between panels")
    ap.add_argument("--letter-pt", type=float, default=20.0, help="bare letter size, bp (default 20)")
    ap.add_argument("--print-width", default="0.98x396bp", help="width on the page (default 0.98x396bp)")
    ap.add_argument("--floor", type=float, default=5.0, help="smallest printed base size, pt (default 5)")
    ap.add_argument("--preamble", type=Path, default=PREAMBLE, help="preamble for the type (default: the skill's)")
    ap.add_argument("--compile", action="store_true", help="run pdflatex on the result")
    a = ap.parse_args()
    sizes = [page_size(p) for p in a.panels]
    H = a.height or sizes[0][1]
    scales = [H / h for _, h in sizes]
    widths = [w * s for (w, _), s in zip(sizes, scales)]
    n = len(a.panels)
    titles = a.titles.split("|") if a.titles else None
    letters = a.letters.split(",") if a.letters else ([chr(ord("a") + i) for i in range(n)] if titles else None)
    if letters and len(letters) != n:
        raise SystemExit(f"{n} panels but {len(letters)} letters")
    top = 26.0 if titles else 0.0                       # the title band above the panels
    xs, x = [], 0.0
    for w in widths:
        xs.append(x)
        x += w + a.gap
    W = x - a.gap
    Htot = H + top + 4.0
    rel = os.path.relpath
    lines = [f"% written by compose.py from the panels' page sizes; do not edit by hand",
             f"% panels set to {H:.1f} bp high: " + ", ".join(f"{p.name} x{s:.3f}" for p, s in zip(a.panels, scales))]
    lines.append(figkit.header(a.preamble, 0.0).rstrip("\n"))
    lines.append("\\begin{tikzpicture}[x=1bp, y=1bp]")
    lines.append(f"\\useasboundingbox (0,0) rectangle ({W:.2f},{-Htot:.2f});")
    for p, xx, s in zip(a.panels, xs, scales):
        path = rel(p.resolve(), a.out.resolve().parent)
        lines.append(f"\\node[anchor=north west, inner sep=0pt] at ({xx:.2f},{-top:.2f}) "
                     f"{{\\includegraphics[scale={s:.4f}]{{{path}}}}};")
    if titles:
        for i, (xx, t) in enumerate(zip(xs, titles)):
            lines.append(f"\\node[paneltitle, anchor=base west, inner sep=0pt] at ({xx:.2f},{-17.0:.2f}) "
                         f"{{\\textbf{{{letters[i]})}}\\ \\ {t}}};")
    elif letters:
        for i, (xx, lt) in enumerate(zip(xs, letters)):
            anchor, lx = ("base west", 0.0) if i == 0 else ("base east", xx - 2.0)
            lines.append(f"\\node[anchor={anchor}, inner sep=0pt, font=\\fontsize{{{a.letter_pt:g}}}{{24}}\\selectfont\\bfseries] "
                         f"at ({lx:.2f},{-17.0:.2f}) {{{lt}}};")
    if a.rules:
        for i in range(1, n):
            rx = xs[i] - a.gap / 2
            lines.append(f"\\draw[panelrule] ({rx:.2f},{-top + 2:.2f}) -- ({rx:.2f},{-Htot + 2:.2f});")
    lines += ["\\end{tikzpicture}", "\\end{document}"]
    a.out.write_text("\n".join(lines) + "\n")
    pw = to_bp(a.print_width)
    page = pw / W
    print(f"wrote {a.out}: {W:.1f} x {Htot:.1f} bp; on the page at {pw:.1f} bp: scale {page:.3f}")
    bad = 0
    for p, s in zip(a.panels, scales):
        sm = smallest_base(p)
        if sm is None:
            print(f"  {p.name}: x{s:.3f} (type not measured: needs PyMuPDF)")
            continue
        printed = sm * s * page
        flag = "ok" if printed >= a.floor - 1e-9 else "UNDER THE FLOOR"
        bad += flag != "ok"
        print(f"  {p.name}: x{s:.3f}; smallest base type {sm:.2f} bp -> {printed:.2f} pt on the page  {flag}")
    if titles or letters:
        lp = (16.0 if titles else a.letter_pt) * page
        print(f"  letters print at {lp:.2f} pt (the package's default letter is 8 pt; one size for every figure of a paper)")
    if a.compile:
        r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", a.out.name],
                           cwd=a.out.resolve().parent, capture_output=True, text=True, errors="replace")
        if r.returncode:
            print("pdflatex failed:", next((ln for ln in r.stdout.splitlines() if ln.startswith("!")), "see the log"))
            return 1
        print(f"  compiled {a.out.with_suffix('.pdf').name}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
