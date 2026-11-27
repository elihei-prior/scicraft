#!/usr/bin/env python3
"""Render synthetic raster tiles for a composed figure, with scale bars baked into the raster at a size that
survives the final print scale.

The tiles stand in for the data renders of a paper (a field map, a scatter of categorized points, a field pooled
at several pitches). They come from one seeded synthetic sample, so every count printed under a tile is the real
count of what the tile shows, and facts.json holds them.

  points_whole.png, points_zoom.png, points_fine.png    points colored by category, three nested windows
  field_whole.png,  field_zoom.png,  field_fine.png     a smooth three-channel field as RGB, same windows
  ladder_<w>_<pitch>.png                                the field pooled on square bins of each pitch, for
                                                        two windows (a resolution ladder); each window is 8
                                                        bins of the coarsest pitch wide, on that pitch's grid
                                                        and wholly inside the sample
  counts.tex                                            every count printed under a tile, as TeX macros

How tiles are made (the source's practice): rendered at SUP = 2 times their placed size and placed at that size;
a dark ground outside the sample; marker areas quoted in printed pt squared and drawn as area * SUP**2; the color
stretch is anchored at the 5 and 95 percentiles of the whole sample, one mapping for every window and every pitch,
so zooming in reads as zooming in.

Baked text is type too. The scale-bar label is set so that it prints at --label-pt (default 5.5 pt) after the tile
is placed at its size and the whole figure is scaled by --print-scale; the source set it at 10.5 pt at the tile's
size and it printed at about 4.5 pt. The script reports the printed size of every label it bakes.

A pitch is a whole number of raster cells (the sample is a 960 x 960 raster, 2.5 um per cell at the default size),
so a tile labeled 20 um is pooled on bins of exactly 20 um. The script exits when a pitch is not.

Needs numpy, scipy and matplotlib (cmr10 ships with matplotlib).

Usage:
    python3 tiles.py --out tiles/ --print-scale 0.443
    python3 tiles.py --out tiles/ --print-scale 1.0 --label-pt 6 --seed 3
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import matplotlib.patheffects as pe  # noqa: E402
from matplotlib.colors import hsv_to_rgb, rgb_to_hsv  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402
from scipy.ndimage import gaussian_filter  # noqa: E402

SUP, DPI = 2, 300
GROUND = "#141416"
CATS = {"category 1": "#5C8CC4", "category 2": "#C98F3D", "category 3": "#9475B5"}
plt.rcParams.update({"font.family": "serif", "font.serif": ["cmr10"], "mathtext.fontset": "cm",
                     "axes.formatter.use_mathtext": True, "pdf.fonttype": 42})


def smooth_field(rng, n, sigmas, weights):
    """Gaussian-filtered noise at several scales (sigmas as fractions of the side): smooth, with detail at every
    zoom."""
    f = np.zeros((n, n))
    for s, w in zip(sigmas, weights):
        g = gaussian_filter(rng.normal(size=(n, n)), s * n, mode="wrap")
        f += w * g / g.std()
    return f


def sample(seed, n=960):
    """A blob-shaped sample with a three-channel field and three category regions."""
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:n, 0:n] / (n - 1)
    th = np.arctan2(yy - 0.5, xx - 0.5)
    ph = rng.uniform(0, 2 * np.pi, 3)
    r0 = 0.43 * (1 + 0.10 * np.sin(3 * th + ph[0]) + 0.06 * np.sin(5 * th + ph[1]) + 0.04 * np.sin(8 * th + ph[2]))
    mask = np.hypot(xx - 0.5, yy - 0.5) < r0
    chans = [smooth_field(rng, n, (0.08, 0.025, 0.008), (1.0, 0.6, 0.35)) for _ in range(3)]
    cats = np.argmax(np.stack([smooth_field(rng, n, (0.06, 0.02), (1.0, 0.4)) for _ in range(3)], -1), -1)
    return rng, mask, np.stack(chans, axis=-1), cats


def to_rgb(F, lo, hi, sat=1.25):
    """One color per three-channel value: a soft stretch anchored at lo and hi (the 5 and 95 percentiles of the
    whole sample), a logistic curve that passes 0.05 and 0.95 there. A hard clip at the percentiles paints every
    place where all three channels are low one flat gray patch, which reads as missing data."""
    x = (F - lo) / (hi - lo)
    c = 1.0 / (1.0 + np.exp(-2.0 * np.log(19.0) * (x - 0.5)))
    h = rgb_to_hsv(c)
    h[..., 1] = np.clip(h[..., 1] * sat, 0, 1)
    h[..., 2] = 0.30 + 0.70 * h[..., 2]
    return hsv_to_rgb(h)


def tile_axes(cm):
    f = plt.figure(figsize=(cm / 2.54 * SUP, cm / 2.54 * SUP))
    ax = f.add_axes([0, 0, 1, 1])
    ax.set_facecolor(GROUND)
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)
    return f, ax


def scalebar(ax, length, width, label, label_pt, y=0.055, dy=0.032):
    """A white bar with a dark halo, its right end at 94 percent of the tile, the label centered over it."""
    lw = 1.8 * SUP
    frac = length / width
    x1, x0 = 0.94, 0.94 - frac
    ln, = ax.plot([x0, x1], [y, y], transform=ax.transAxes, color="white", lw=lw, solid_capstyle="butt",
                  zorder=50, clip_on=False)
    ln.set_path_effects([pe.withStroke(linewidth=lw + 1.0 * SUP, foreground=GROUND)])
    t = ax.text((x0 + x1) / 2, y + dy, label, transform=ax.transAxes, ha="center", va="bottom", color="white",
                fontsize=label_pt * SUP, zorder=51)
    # centered over a short bar, a large label runs off the tile; then it ends where the bar ends (the source
    # switched to that when its labels grew, and back to centered when they shrank)
    f = ax.figure
    f.canvas.draw()
    bb = t.get_window_extent().transformed(ax.transAxes.inverted())
    if bb.x1 > 0.97:
        t.set_position((x1, y + dy))
        t.set_ha("right")
    t.set_path_effects([pe.withStroke(linewidth=1.6 * SUP, foreground=GROUND)])


def save(f, path):
    f.savefig(path, dpi=DPI, facecolor=GROUND)
    plt.close(f)


def pooled(F, mask, pitch_um, L, lo, hi):
    """The field pooled on square bins of one pitch: (image, bins in the sample, extent in um). A bin belongs to
    the sample when at least 10 percent of it is sample (a bin clipped by the edge otherwise takes a full,
    saturated color and drags the stretch)."""
    n = mask.shape[0]
    k = cells(pitch_um, L, n)
    nb = n // k
    Fb = F[:nb * k, :nb * k].reshape(nb, k, nb, k, 3).mean(axis=(1, 3))
    Mb = mask[:nb * k, :nb * k].reshape(nb, k, nb, k).mean(axis=(1, 3)) >= 0.10
    img = to_rgb(Fb, lo, hi)
    img[~Mb] = matplotlib.colors.to_rgb(GROUND)
    return img, Mb, nb * k / n * L


def cells(pitch_um, L, n):
    """Raster cells in one bin. A pitch that is not a whole number of cells would be pooled at another pitch than
    the tile's label says, so it stops the run."""
    k = pitch_um / L * n
    if k < 1 or abs(k - round(k)) > 1e-6:
        raise SystemExit(f"a pitch of {pitch_um:g} um is {k:.3f} raster cells ({L / n:g} um each); "
                         "use a whole number of cells, or change --size-um")
    return int(round(k))


def round_bar(width_um, share=0.35):
    """The longest round length that is at most `share` of the tile's width."""
    steps = [m * 10 ** e for e in range(-1, 5) for m in (1, 2, 2.5, 5)]
    return max(v for v in steps if v <= share * width_um)


def thousands(v: int) -> str:
    return f"{v:,}".replace(",", "{,}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Synthetic raster tiles with baked scale bars, sized for the print scale.")
    ap.add_argument("--out", required=True, help="output folder")
    ap.add_argument("--seed", type=int, default=3, help="seed of the synthetic sample (default 3)")
    ap.add_argument("--size-um", type=float, default=2400.0,
                    help="side of the sample in micrometers (default 2400: 2.5 um per raster cell)")
    ap.add_argument("--points", type=int, default=24000, help="points in the sample (default 24000)")
    ap.add_argument("--whole-cm", type=float, default=6.9, help="placed width of the whole-sample tiles (6.9)")
    ap.add_argument("--zoom-cm", type=float, default=3.3, help="placed width of the zoom tiles (3.3)")
    ap.add_argument("--ladder-cm", type=float, default=3.48, help="placed width of the ladder tiles (3.48)")
    ap.add_argument("--pitches", default="80,40,20,10",
                    help="ladder bin pitches in micrometers, coarsest first (default 80,40,20,10)")
    ap.add_argument("--bin-um", type=float, default=20.0, help="bin pitch of the whole field tile (default 20)")
    ap.add_argument("--zoom-bin-um", type=float, default=5.0, help="bin pitch of the zoomed field tile (default 5)")
    ap.add_argument("--print-scale", type=float, default=0.443, help="scale from the composition to the page (0.443)")
    ap.add_argument("--label-pt", type=float, default=5.5, help="printed size of a baked label, pt (default 5.5)")
    a = ap.parse_args(argv)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    rng, mask, F, cat_map = sample(a.seed)
    n = mask.shape[0]
    L = a.size_um
    inside = F[mask]
    lo, hi = np.percentile(inside, 5, axis=0), np.percentile(inside, 95, axis=0)
    rgb = to_rgb(F, lo, hi)
    rgb[~mask] = matplotlib.colors.to_rgb(GROUND)
    # points drawn where the sample is, each with the category of the region it falls in
    m_idx = np.argwhere(mask)
    pick = m_idx[rng.choice(len(m_idx), a.points, replace=False)]
    jitter = rng.uniform(0, 1, size=(a.points, 2))
    pxy = (pick[:, ::-1] + jitter) / n * L                     # (x, y) in micrometers
    pcat = cat_map[pick[:, 0], pick[:, 1]]
    flip = rng.random(a.points) < 0.08                         # a few points of another category, as in real data
    pcat[flip] = rng.integers(0, 3, flip.sum())
    cols = np.array([matplotlib.colors.to_rgb(c) for c in CATS.values()])

    def label_size(placed_cm):
        # the label is set at label_pt / print_scale at the tile's placed size, so it prints at label_pt
        return a.label_pt / a.print_scale, placed_cm

    # three nested windows, chosen by a stated rule: among windows that lie wholly inside the sample, the one with
    # the highest category entropy (where the categories meet); the fine window by the same rule inside the zoom
    wz, wf = L / 4.0, L / 16.0

    def pick_window(w, cx_lo, cx_hi, cy_lo, cy_hi, parent=None):
        """parent = (x, y, side) of the tile the window's box is drawn on: the box keeps clear of that tile's
        scale-bar corner (the right 45 percent of its bottom 30 percent), so a box never covers the label."""
        best = None
        for cx in np.linspace(cx_lo, cx_hi, 21):
            for cy in np.linspace(cy_lo, cy_hi, 21):
                i0, i1 = int((cy - w / 2) / L * n), int((cy + w / 2) / L * n)
                j0, j1 = int((cx - w / 2) / L * n), int((cx + w / 2) / L * n)
                if i0 < 0 or j0 < 0 or i1 > n or j1 > n or not mask[i0:i1, j0:j1].all():
                    continue
                if parent:
                    px, py, pw = parent
                    if cx + w / 2 > px + pw * 0.05 and cy + w / 2 > py + pw * 0.20:
                        continue
                cnt = np.bincount(cat_map[i0:i1, j0:j1].ravel(), minlength=3) + 1e-9
                p = cnt / cnt.sum()
                e = float(-(p * np.log(p)).sum())
                if best is None or e > best[0] + 1e-9:
                    best = (e, cx, cy)
        return best

    ez, zx, zy = pick_window(wz, wz / 2, L - wz / 2, wz / 2, L - wz / 2, parent=(L / 2, L / 2, L))
    mg = 0.06 * wz                                         # a box keeps 6 percent of its tile clear at the edges
    ef, fx, fy = pick_window(wf, zx - wz / 2 + wf / 2 + mg, zx + wz / 2 - wf / 2 - mg,
                             zy - wz / 2 + wf / 2 + mg, zy + wz / 2 - wf / 2 - mg, parent=(zx, zy, wz))
    windows = {"whole": (L / 2, L / 2, L), "zoom": (zx, zy, wz), "fine": (fx, fy, wf)}
    bars = {"whole": (500.0, r"500 $\mu$m"), "zoom": (100.0, r"100 $\mu$m"), "fine": (20.0, r"20 $\mu$m")}
    facts = {"seed": a.seed, "sample_um": L, "points": int(a.points), "print_scale": a.print_scale,
             "label_pt_printed": a.label_pt, "tiles": {}}
    for kind in ("points", "field"):
        for name, (wx, wy, w) in windows.items():
            placed = a.whole_cm if name == "whole" else a.zoom_cm
            fsz, _ = label_size(placed)
            f, ax = tile_axes(placed)
            if kind == "field" and name != "fine":              # the field pooled on real bins
                img, Mb, ext = pooled(F, mask, a.bin_um if name == "whole" else a.zoom_bin_um, L, lo, hi)
                ax.imshow(img, extent=(0, ext, ext, 0), origin="upper", interpolation="nearest")
            elif kind == "field":                              # the finest level: each point by its own value
                inwin = (np.abs(pxy[:, 0] - wx) <= w / 2) & (np.abs(pxy[:, 1] - wy) <= w / 2)
                ij = np.clip((pxy[inwin][:, ::-1] / L * n).astype(int), 0, n - 1)
                val = F[ij[:, 0], ij[:, 1]] + rng.normal(0, 0.35, size=(int(inwin.sum()), 3))
                ax.scatter(pxy[inwin, 0], pxy[inwin, 1], s=5.0 * SUP ** 2, c=to_rgb(val, lo, hi), linewidths=0,
                           rasterized=True)
            else:
                inwin = (np.abs(pxy[:, 0] - wx) <= w / 2) & (np.abs(pxy[:, 1] - wy) <= w / 2)
                area = 0.22 if name == "whole" else (1.0 if name == "zoom" else 5.0)   # printed pt^2
                ax.scatter(pxy[inwin, 0], pxy[inwin, 1], s=area * SUP ** 2, c=cols[pcat[inwin]], linewidths=0,
                           rasterized=True)
            ax.set_xlim(wx - w / 2, wx + w / 2)
            ax.set_ylim(wy + w / 2, wy - w / 2)
            ax.set_aspect("equal")
            nxt = {"whole": "zoom", "zoom": "fine"}.get(name)
            if nxt:                                            # the box that marks the next window
                nx, ny, nw = windows[nxt]
                ax.add_patch(Rectangle((nx - nw / 2, ny - nw / 2), nw, nw, fill=False, edgecolor="white",
                                       lw=0.6 * SUP * (2 if name == "whole" else 1), zorder=7))
            blen, blab = bars[name]
            scalebar(ax, blen, w, blab, fsz)
            fn = f"{kind}_{name}.png"
            save(f, out / fn)
            entry = {"window_um": [round(wx, 1), round(wy, 1), round(w, 1)], "placed_cm": placed,
                     "label_pt_at_placed_size": round(fsz, 2), "label_pt_printed": round(fsz * a.print_scale, 2),
                     "scalebar_um": blen}
            if kind == "points" or name == "fine":
                inwin = (np.abs(pxy[:, 0] - wx) <= w / 2) & (np.abs(pxy[:, 1] - wy) <= w / 2)
                entry["points_shown"] = int(inwin.sum())
            else:
                entry["bin_um"] = a.bin_um if name == "whole" else a.zoom_bin_um
                if name == "whole":
                    entry["bins_in_sample"] = int(Mb.sum())
            facts["tiles"][fn] = entry

    # the resolution ladder: the field pooled on bins of each pitch, two windows, one color mapping.
    # A window is 8 bins of the coarsest pitch wide and sits on that pitch's grid, so no tile shows a cut bin, and
    # it lies wholly inside the sample, so no tile shows the ground. Which two, by a stated rule: the window whose
    # coarsest bins differ most in color, then the same among the windows that do not overlap it.
    pitches = sorted((float(p) for p in a.pitches.split(",")), reverse=True)
    for p in pitches:
        r = pitches[0] / p
        if abs(r - round(r)) > 1e-6:
            raise SystemExit(f"every pitch must divide the coarsest ({pitches[0]:g} um); {p:g} um does not")
    k0 = cells(pitches[0], L, n)
    side = 8 * k0                                           # window side in raster cells
    w = side / n * L
    cands = []
    for i0 in range(0, n - side + 1, k0):
        for j0 in range(0, n - side + 1, k0):
            if not mask[i0:i0 + side, j0:j0 + side].all():
                continue
            bins = F[i0:i0 + side, j0:j0 + side].reshape(8, k0, 8, k0, 3).mean(axis=(1, 3))
            cands.append((float(bins.reshape(-1, 3).var(axis=0).sum()), i0, j0))
    if not cands:
        raise SystemExit(f"no window of 8 bins of {pitches[0]:g} um lies inside the sample; use finer --pitches")
    cands.sort(key=lambda c: (-c[0], c[1], c[2]))
    first = cands[0]
    apart = [c for c in cands if abs(c[1] - first[1]) >= side or abs(c[2] - first[2]) >= side]
    if not apart:
        raise SystemExit(f"the sample holds one window of 8 bins of {pitches[0]:g} um but not two apart; "
                         "use finer --pitches")
    lad = {str(q + 1): ((c[2] + side / 2) / n * L, (c[1] + side / 2) / n * L, w) for q, c in enumerate((first, apart[0]))}
    facts["ladder"] = {"pitches_um": pitches, "window_um": round(w, 1),
                       "rule": "8 bins of the coarsest pitch wide, on its grid, wholly inside the sample; the "
                               "window whose coarsest bins differ most in color, then the same among the windows "
                               "that do not overlap it",
                       "windows_xy_um": {k: [round(v[0], 1), round(v[1], 1)] for k, v in lad.items()}}
    blen = round_bar(w)
    for wid, (wx, wy, w) in lad.items():
        for p in pitches:
            img, Mb, ext = pooled(F, mask, p, L, lo, hi)
            f, ax = tile_axes(a.ladder_cm)
            ax.imshow(img, extent=(0, ext, ext, 0), origin="upper", interpolation="nearest")
            ax.set_xlim(wx - w / 2, wx + w / 2)
            ax.set_ylim(wy + w / 2, wy - w / 2)
            ax.set_aspect("equal")
            fsz, _ = label_size(a.ladder_cm)
            if wid == "1" and p == pitches[0]:
                scalebar(ax, blen, w, rf"{blen:g} $\mu$m", fsz)
            fn = f"ladder_{wid}_{p:g}.png"
            save(f, out / fn)
            nb = Mb.shape[0]
            cx = (np.arange(nb) + 0.5) * ext / nb
            inx, iny = np.abs(cx - wx) <= w / 2, np.abs(cx - wy) <= w / 2
            facts["tiles"][fn] = {"window_um": [round(wx, 1), round(wy, 1), round(w, 1)], "pitch_um": p,
                                  "placed_cm": a.ladder_cm, "bins_in_window": int(Mb[np.ix_(iny, inx)].sum())}
            if wid == "1" and p == pitches[0]:
                facts["tiles"][fn]["scalebar_um"] = blen
    (out / "facts.json").write_text(json.dumps(facts, indent=1) + "\n")
    # every count a figure prints under a tile, as TeX macros, so no number is typed into a figure by hand
    T = facts["tiles"]
    macros = {"tilePointsWhole": T["points_whole.png"]["points_shown"], "tilePointsZoom": T["points_zoom.png"]["points_shown"],
              "tilePointsFine": T["points_fine.png"]["points_shown"], "tileBinsWhole": T["field_whole.png"]["bins_in_sample"]}
    (out / "counts.tex").write_text("% written by tiles.py from facts.json\n" + "".join(
        f"\\newcommand\\{k}{{{thousands(v)}}}\n" for k, v in macros.items())
        + f"\\newcommand\\tileBinUm{{{a.bin_um:g}}}\n\\newcommand\\tileZoomBinUm{{{a.zoom_bin_um:g}}}\n")
    lab = [(k, v["label_pt_printed"]) for k, v in facts["tiles"].items() if "label_pt_printed" in v]
    print(f"ok  {len(facts['tiles'])} tiles -> {out}; baked labels print at "
          + ", ".join(f"{v:.1f} pt" for _, v in lab[:1]) + f" (print scale {a.print_scale})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
