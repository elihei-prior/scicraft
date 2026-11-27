# Generators and determinism

Every structural element of a figure that claims something about real geometry (a tree, a partition, a graph,
which points are neighbors, a direction, a length) is computed by the method's own code on a fixed-seed input and
emitted as TikZ, with every number it shows written to `facts.json`. A hand-drawn tree was called "some random
tree"; a uniform grid drawn as an adaptive partition misstated the method; a zoom whose levels were re-sampled
showed neighbors that came from nowhere.

**Contents**
1. The pattern
2. The shipped generators
3. The kit for emitting TikZ
4. Seeds and stated rules
5. Emitting TikZ that compiles and audits
6. facts.json
7. Iterate with \input, deliver inlined
8. When the real code cannot run here

## 1. The pattern

```
figures/<figure>/
  gen_<figure>.py     imports the method's own function, runs it on a seeded input, writes the fragments
  frag/*.tex          TikZ fragments in local coordinates
  facts.json          every number the figure shows or depends on, and every rule that chose something
  <figure>.tex        the figure: preamble, layout, \input{frag/...}
```

Two inputs when needed: a hero set (about 230 points) for density, and a toy set (about 50 points) for a tree or an
address a reader follows. Panels come in one at a time, each signed off before the next.

## 2. The shipped generators

| Script | What it computes | Checks it runs |
|---|---|---|
| `scripts/hierarchy.py` | a quadtree over seeded points, its tree, the isometric pyramid, the rows with rails, the point graph | the selected path is the tile holding the selected point at every level |
| `scripts/sphere.py` | von Mises-Fisher clusters on a sphere, density rings, the composition of two sets' resultants, the overview glyph | additivity, the projected parallelogram closes, the diagonal's length is R_A, the projection is radial, the angles add up |
| `scripts/zoom_cascade.py` | one point field's field, region, crop and k-nearest-neighbor graph, the masked views | neighbors on the full field; edges clipped at the frame by the generator |
| `scripts/tiles.py` | raster tiles of one synthetic sample, pooled bins, baked scale bars | every printed count from the records; baked label size at print |
| `assets/examples/block_cards.py` | two block cards through the kit | the card names fit (two passes) |

Each takes a CSV or a seed, writes `facts.json`, and answers `--help`. Replace the example computation (the
quadtree in `hierarchy.py`, the synthetic field in `zoom_cascade.py`) with an import of your own function and keep
the drawing.

## 3. The kit for emitting TikZ

`assets/figkit.py` (standard library) reads every size from the preamble and emits TikZ in bp with y downward:

| Call | Draws |
|---|---|
| `Figure(w, h, style=None, names={})` | a picture of w x h bp; `tex()`, `write(path)` |
| `box(x, y, label, w, h, fill, pt)`, `opbox(x, y, label, fill)` | the plain box, the operation box; return (top, bottom) |
| `tokens(xc, y, fill, rows, cols)`, `tok_top`, `tok_bot`, `tok_right` | a K-deep stack; where arrows stop and start |
| `width_brace`, `depth_brace`, `brace` | the stack's width, its count, any brace with a gray label |
| `arrow`, `line`, `join`, `junction`, `residual` | wires, the join circle, the dot, the pre-norm bypass |
| `card(ox, top, w, h, name)`, `mini(kind, ox, w, y0)`, `two_level` | the card with its name on the border, the icon, a name over its gloss |
| `text`, `note` | black text, gray secondary text |
| `Style.from_preamble().scaled(...)`, `Stations().replace(...)` | sizes changed together; shared stations |
| `build(make, tex)` | two passes: compile, measure the card names, compile again |

## 4. Seeds and stated rules

- **Every random choice has a seed**: `numpy.random.default_rng(seed)` in Python, `\pgfmathsetseed{N}` before any
  `rand` in TikZ. The seed goes into `facts.json`. An unseeded `rand` moved the figure on every compile.
- **Every showcase choice has a stated rule** in the code and in `facts.json`: the window with the highest category
  entropy, the point nearest the center of the field, the pair whose resultant length lies in a window, the
  center point whose neighbors surround it. A choice made by eye is a choice a reviewer can call cherry-picked.
- **A chosen example is checked for being an artifact** (an edge of the domain, an empty window, a cluster that
  exists only at this seed) before it is drawn.

```latex
\begin{tikzpicture}[paper]
  \pgfmathsetseed{7}
  \draw[crop] (0,0) rectangle (2,2);
  \foreach \k in {1,...,40} {\figpoint{{0.1+1.8*rnd},{0.1+1.8*rnd}}{ptblue}}
\end{tikzpicture}
```

## 5. Emitting TikZ that compiles and audits

- **Coordinates in bp, the page is the figure** (`border=0`, `\useasboundingbox` from (0,0)), so an audit finding at
  (x, y) is the generator's (x, y). TeX points differ from bp by 0.375 percent, enough to slide a patch.
- **Fixed decimals** (`f"{x:.3f}"`); `plot[smooth cycle] coordinates` separated by spaces, never by `--`.
- **Clip in the generator.** A segment hidden under a TikZ clip is still in the PDF; clip it before emitting
  (Liang-Barsky in `zoom_cascade.py`), and drop a node whose disk would cross the frame.
- **Compute what TikZ cannot do safely.** A `\foreach` with `\pgfmathsetmacro` concatenated numbers in an ellipse
  radius and failed ("Unknown operator 'a'"); a projected graticule needs a visibility test per point. Compute in
  Python and emit coordinates.
- **Name what another figure will attach to**: fragments name their corners (`\coordinate (crop-nw)`), so links
  are drawn between named coordinates wherever the fragment is placed.
- **Text the layout depends on is measured, not guessed**: `figkit.build()` compiles, reads the ink width of each
  card name from the PDF and compiles again. A label width guessed for one font is wrong in another (a corner label
  reserved at 2.16 cm in a sans font was 2.57 cm in Computer Modern).

## 6. facts.json

Every number the figure or its caption shows (counts, k, radii, seeds, window centers, the rule that chose each
example, check results) is written by the generator. The caption's numbers are copied from `facts.json`, and the
final check compares them. A tile's count (`tiles/counts.tex`) is read into the figure as a macro, so no count is
typed by hand.

## 7. Iterate with \input, deliver inlined

While iterating, the figure reads its fragments with `\input{frag/...}` so a regenerated fragment takes effect
(appending a generated body once with `cat >>` froze a copy that later runs did not update). To deliver:

```bash
python3 scripts/render_figure.py figure.tex --texinputs <skill>/assets --inline figure_final.tex
```

It replaces every `\input` by the file's text (the preamble contributes only its header), writes
`figure_final.tex`, and compiles it alone in an empty folder. A figure that needs files the user does not have is not
delivered. Generated figures can reach about 0.5 MB of coordinates; say so when delivering.

## 8. When the real code cannot run here

Say so, and draw from the code's output instead (a CSV the user exports), or mark the figure schematic: no
measured-looking ticks, no exact lengths, the caption says "schematic". Never invent geometry that looks computed.
