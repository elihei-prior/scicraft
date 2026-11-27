#!/usr/bin/env python3
"""Build the seven example figures from the shipped sources, render them, audit them, check their printed type.

  a  block cards     assets/examples/block_cards.py (the kit, two passes)
  b  training overview  assets/examples/overview.tex with fragments from zoom_cascade.py --views and sphere.py --glyph
  c  hierarchy       scripts/hierarchy.py
  d  sphere          scripts/sphere.py
  e  zoom cascade    scripts/zoom_cascade.py
  f  composed figure tiles.py, panel_points.tex, panel_field.tex, the overview, compose.py
  g  tile row        assets/examples/tile_row.tex with the tiles of f

Every figure is compiled with pdflatex -halt-on-error, rendered to <name>.png, run through audit_layout.py (text
and lines) and print_scale.py at the width it is meant to print at. The summary says what passed. Use it after any
change to the preamble, the kit or a generator, and as the template for a project's own build script.

Needs pdflatex, pdftoppm, numpy, scipy, matplotlib (with contourpy) and PyMuPDF.

Usage:
    python3 build_examples.py --out examples_build/
    python3 build_examples.py --out examples_build/ --only a,c --dpi 200
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
sys.dont_write_bytecode = True        # importing a sibling must not leave __pycache__ in the skill
from pathlib import Path

HERE = Path(__file__).resolve().parent
ASSETS = HERE.parent / "assets"
EX = ASSETS / "examples"
PY = sys.executable
# the width each example is meant to print at
PRINT = {"a": "0.98x396bp", "b": "204bp", "c": "0.98x396bp", "d": "0.5x396bp", "e": "0.98x396bp",
         "f": "396bp", "g": "396bp"}


def run(cmd, cwd, label):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, errors="replace",
                       env=dict(os.environ, TEXINPUTS=str(ASSETS) + os.pathsep + os.environ.get("TEXINPUTS", "")))
    if r.returncode != 0:
        tail = (r.stdout + r.stderr).strip().splitlines()[-3:]
        raise RuntimeError(f"{label} failed: " + " | ".join(tail))
    return r.stdout


def tex(cwd: Path, name: str):
    run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", f"{name}.tex"], cwd, f"pdflatex {name}")
    return cwd / f"{name}.pdf"


def main() -> int:
    ap = argparse.ArgumentParser(description="Build, render, audit and size-check the seven example figures.")
    ap.add_argument("--out", required=True, type=Path, help="build folder (created; files are overwritten)")
    ap.add_argument("--only", default="a,b,c,d,e,f,g", help="comma-separated letters (default all)")
    ap.add_argument("--dpi", type=int, default=170, help="PNG resolution (default 170)")
    a = ap.parse_args()
    out = a.out.resolve()
    out.mkdir(parents=True, exist_ok=True)
    want = set(a.only.split(","))
    built = {}
    try:
        if "a" in want:
            run([PY, str(EX / "block_cards.py"), "--out", str(out)], out, "block cards")
            built["a"] = out / "block_cards.pdf"
        if want & {"b", "f"}:
            run([PY, str(HERE / "zoom_cascade.py"), "--out", str(out / "frag"), "--views"], out, "zoom cascade (views)")
            run([PY, str(HERE / "sphere.py"), "--out", str(out / "frag"), "--glyph"], out, "sphere glyph")
            shutil.copy(EX / "overview.tex", out / "overview.tex")
            built["b"] = tex(out, "overview")
        if "c" in want:
            run([PY, str(HERE / "hierarchy.py"), "--out", str(out)], out, "hierarchy")
            built["c"] = tex(out, "hierarchy")
        if "d" in want:
            run([PY, str(HERE / "sphere.py"), "--out", str(out / "sphere"), "--preamble", str(ASSETS / "preamble.tex")], out, "sphere")
            built["d"] = tex(out / "sphere", "sphere")
        if "e" in want:
            run([PY, str(HERE / "zoom_cascade.py"), "--out", str(out / "cascade"), "--preamble", str(ASSETS / "preamble.tex")], out, "cascade")
            built["e"] = tex(out / "cascade", "cascade")
        if want & {"f", "g"}:
            run([PY, str(HERE / "tiles.py"), "--out", str(out / "tiles")], out, "tiles")
        if "f" in want:
            for name in ("panel_points", "panel_field"):
                shutil.copy(EX / f"{name}.tex", out / f"{name}.tex")
                tex(out, name)
            run([PY, str(HERE / "compose.py"), str(out / "composed.tex"), str(out / "panel_points.pdf"),
                 str(out / "overview.pdf"), str(out / "panel_field.pdf"), "--titles",
                 "Point field|Training scheme|Embedding map", "--rules", "--print-width", PRINT["f"], "--compile"], out, "compose")
            built["f"] = out / "composed.pdf"
        if "g" in want:
            shutil.copy(EX / "tile_row.tex", out / "tile_row.tex")
            built["g"] = tex(out, "tile_row")
    except RuntimeError as e:
        print(f"FAIL {e}")
        return 1
    bad = 0
    print(f"{'':2s} {'figure':18s} {'audit':28s} printed type")
    for k in sorted(built):
        pdf = built[k]
        subprocess.run(["pdftoppm", "-png", "-r", str(a.dpi), "-singlefile", str(pdf), str(pdf.with_suffix(""))], check=True)
        au = subprocess.run([PY, str(HERE / "audit_layout.py"), str(pdf)], capture_output=True, text=True)
        ps = subprocess.run([PY, str(HERE / "print_scale.py"), str(pdf), "--print-width", PRINT[k]], capture_output=True, text=True)
        a_line = au.stdout.strip().splitlines()[-1].split("->")[-1].strip()
        p_line = ps.stdout.strip().splitlines()[-1]
        bad += (au.returncode != 0) + (ps.returncode != 0)
        print(f"{k:2s} {pdf.name:18s} {a_line:28s} {p_line} (at {PRINT[k]})")
    print(f"\n{len(built)} figure(s) built in {out}; " + ("all audits at 0 and all type at or above the floor" if not bad
                                                         else f"{bad} check(s) failed: run the two scripts on the figure"))
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
