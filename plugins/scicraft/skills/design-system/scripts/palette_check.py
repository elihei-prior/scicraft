#!/usr/bin/env python3
"""Separation of color families, in normal vision and in two color-blind views.

A figure's colors fall into families (one family per meaning: the categories of a column, a ramp for an amount, the
two ends of a signed scale). Two kinds of failure are measured:

  across families  a tone of one family close to a tone of another, so one meaning reads as another
  within a family  two categories of one column too close to tell apart

Distances are CIE76 delta E in CIELAB. Color-blind views use the Machado et al. (2009) matrices at full severity
(deuteranopia, protanopia). As a rough guide, below about 10 two colors are hard to tell apart side by side, and
below about 20 they are easy to confuse in small marks.

Usage:
    python3 scripts/palette_check.py families.json
    python3 scripts/palette_check.py '{"cell line": ["#E58AB9", "#9B8BE0"], "expression": ["#A6DCD5", "#2A9A90"]}'
    python3 scripts/palette_check.py families.json --min-across 20 --min-within 15    # exit 1 below these

families.json maps a family name to a list of hex colors. Standard library only.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import sys
from pathlib import Path

CVD = {
    "normal": ((1, 0, 0), (0, 1, 0), (0, 0, 1)),
    "deutan": ((0.367322, 0.860646, -0.227968), (0.280085, 0.672501, 0.047413), (-0.011820, 0.042940, 0.968881)),
    "protan": ((0.152286, 1.052583, -0.204868), (0.114503, 0.786281, 0.099216), (-0.003882, -0.048116, 1.051998)),
}
XYZ = ((0.4124, 0.3576, 0.1805), (0.2126, 0.7152, 0.0722), (0.0193, 0.1192, 0.9505))
WHITE = (0.95047, 1.0, 1.08883)


def linear(hexcol: str) -> tuple[float, float, float]:
    h = hexcol.lstrip("#")
    if len(h) != 6:
        raise ValueError(f"not a #RRGGBB color: {hexcol}")
    out = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255
        out.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return tuple(out)


def mat(m, v):
    return tuple(sum(m[r][k] * v[k] for k in range(3)) for r in range(3))


def lab(rgb_linear) -> tuple[float, float, float]:
    x, y, z = (a / w for a, w in zip(mat(XYZ, rgb_linear), WHITE))
    f = lambda t: t ** (1 / 3) if t > 216 / 24389 else (24389 / 27 * t + 16) / 116   # noqa: E731
    fx, fy, fz = f(x), f(y), f(z)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


def view(hexcol: str, name: str):
    v = tuple(min(1.0, max(0.0, c)) for c in mat(CVD[name], linear(hexcol)))
    return lab(v)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("families", help="a JSON file, or a JSON string, mapping family names to lists of hex colors")
    ap.add_argument("--min-across", type=float, default=None, help="fail when two families come closer than this")
    ap.add_argument("--min-within", type=float, default=None, help="fail when two tones of one family come closer")
    ap.add_argument("--show", type=int, default=5, help="how many closest cross-family pairs to print per view")
    a = ap.parse_args()

    src = Path(a.families)
    fam = json.loads(src.read_text() if src.is_file() else a.families)
    bad = 0
    for name in CVD:
        L = {f: [(h, view(h, name)) for h in hs] for f, hs in fam.items()}
        pairs = []
        for f, g in itertools.combinations(L, 2):
            d, hf, hg = min((math.dist(x, y), hx, hy) for hx, x in L[f] for hy, y in L[g])
            pairs.append((d, f, hf, g, hg))
        pairs.sort()
        print(f"[{name}] closest across families: " + "; ".join(f"{f} {hf} ~ {g} {hg}: {d:.0f}" for d, f, hf, g, hg in pairs[:a.show]))
        within = []
        for f, tones in L.items():
            if len(tones) > 1:
                d = min(math.dist(x, y) for (_, x), (_, y) in itertools.combinations(tones, 2))
                within.append((d, f))
        if within:
            print(f"[{name}] closest within a family: " + "; ".join(f"{f} {d:.0f}" for d, f in sorted(within)[:a.show]))
        if a.min_across is not None and pairs and pairs[0][0] < a.min_across:
            bad += 1
            print(f"FAIL [{name}] {pairs[0][1]} and {pairs[0][3]} at {pairs[0][0]:.1f} (asked {a.min_across})")
        if a.min_within is not None and within and min(within)[0] < a.min_within:
            bad += 1
            d, f = min(within)
            print(f"FAIL [{name}] two tones of {f} at {d:.1f} (asked {a.min_within})")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
