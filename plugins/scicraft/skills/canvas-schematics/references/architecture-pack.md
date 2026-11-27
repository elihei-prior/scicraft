# Architecture pack (`pack_arch.js`)

Default for ML architecture figures: the sibling `tikz-figures` skill (vector). Use this pack when the user asks for canvas.

For model and method overviews in the grammar of the I-JEPA Figure 1, DINOv2, MAE, Point
Transformer v3, Graphormer and the Evoformer figure: a few flat labeled blocks, clean directed
arrows, a token row, a small matrix, one or two accents, every label legible at 5 to 7 pt. The pack
exists because a hand-laid diagram "overlaps, looks ugly, and does not show what the model is".

## Themes and locked semantics

Colors are semantic tokens. `pastel` is the default and `three-accent` the named alternative.
Pick the theme once per paper, so a canvas Figure 1 and a TikZ figure from the `tikz-figures` skill
match. `pastel` carries the role palette of that skill: every outline is ink, a pale fill names the
role, and the loss is the one saturated mark.

| Token | `pastel` (default, newest) | `three-accent` | Means |
|---|---|---|---|
| `PAL.method`, `methodFill` | ink `#333333` on peach `#FBE0C2` | `#0B6FB8` blue | method, student, forward path |
| `PAL.teacher`, `teacherFill` | ink `#333333` on gray `#E8E8EC`, dashed EMA in ink | `#0F8C7A` teal | teacher, EMA copy |
| `PAL.target`, `targetFill` | red `#D93025` on `#FBE9E7` | `#D97A06` amber | loss, target, the one contrast |
| `PAL.mask` | dashed gray `#999999` | the target color | outline of a masked or held-out cell |
| `PAL.mark`, `markFill` | ink on yellow `#F5D36B` | the target color, 16% fill | the highlighted cell of a partition |
| `PAL.tok` | chips `#93B4D8`, `#F0B060`, `#B9A3DC`, `#8FBFA0`, `#F5D36B` | saturated hues | token fills by kind |
| `PAL.methodLight`, `targetLight` | `#F0B060`, `#FBE9E7` | lighter tints | fills, halos |

```js
LIB.setArchTheme('three-accent');   // before any drawing, in the first region or in main.js
```

- **One contrast, one meaning, in every panel and every figure of the paper.** Red (or amber in
  `three-accent`) marks only the loss or the target. If a second saturated hue appears, delete it.
- **A fill names a role and keeps it.** In `pastel` a token color names a kind of token and a block
  fill a kind of module, in every panel of the paper.
- **Structure is gray, data is color.** Data points stay neutral (`PAL.greyPt`), never rainbow.
- Matrices use the neutral ramps with black text (`LIB.rank`, `LIB.delta`).
- The fills of the `pastel` theme are the measured fills of the TikZ figures (`tikz-figures`). Check a
  canvas figure against the TikZ figures of the same paper before it ships. The `pastel` theme was
  rendered once with `assets/region_example_arch.js` (0 text under 18 px, 0 overlapping pairs); it has
  not yet been used in a paper.

## Primitives

| Element | Call | Grammar |
|---|---|---|
| module (encoder, predictor, block) | `LIB.block(ctx, x, y, w, h, {label, sublabel, fill, stroke})` | flat rectangle, 1.6 px border, light tint, label centered; sublabel in a light weight |
| token or patch sequence | `LIB.tokenSeq(ctx, x, y, n, s, {colors, stroke, masked, vertical})` | a row of small squares; masked tokens are white with a dashed border |
| table input | `LIB.cellGrid(ctx, x, y, rows, cols, {cw, ch, fill, masked, rowTag})` | rows by features; masked cells dashed in the target color (Suggested, not yet tested in real work) |
| feature tensor or batch | `LIB.tensor(ctx, x, y, w, h, {depth, dz})` | offset faded copies behind a front face |
| hierarchy of summaries | `LIB.tower(ctx, cx, yBottom, levels, {h, gap})` | widest level at the bottom, each tagged |
| partition | `LIB.quadtree(ctx, x, y, w, h, spec, {highlight})`, `LIB.treeLinks(ctx, nodes, edges)` | drawn from the partition the code produces |
| attention, bias or similarity | `LIB.heatmap` (core) | magnitude on `rank`, signed on `delta` |
| forward flow | `LIB.arrow`, `LIB.elbow` (core) | one head shape; orthogonal routing |
| EMA, momentum, weight copy | `LIB.emaArrow(ctx, x1, y1, x2, y2, 'EMA', {lx, ly, align})` | dashed [6, 5], teacher color, italic label |
| stop-gradient | `LIB.stopGrad(ctx, x, y, {vertical})` | a short bar across the path, italic "sg" |
| grouping | `LIB.brace(ctx, x, y, len, 'right'/'left'/'down'/'up')` | thin curly brace |
| math | `LIB.math(ctx, x, y, segs, FONT.L2, 'center')` (core) | italic with subscripts, the paper's notation exactly |

`assets/region_example_arch.js` uses most of them: a teacher-student pretraining region over table
rows (masked rows into a student encoder and predictor, full rows into an EMA teacher with a
stop-gradient, a latent loss in the contrast color, a legend). Render it before writing a new region.

## Recipes

- **Teacher-student (JEPA) layout**: two horizontal rails meeting at a loss node. The top rail is
  context encoder, predictor and predictions; the bottom rail is the EMA target encoder over the full
  input, with `sg`; a dashed EMA arrow from student to teacher.
- **Show the operation, not a hint of it.** A learned query, a pooling step or attention must be
  drawn as the tensor operation with its operands labeled (Q, then K and V, then the output), never
  as a vague arrow. Give the one non-obvious component a small inset (for example a relative-position
  bias indexed by the offset between two positions).
- **Three zoom levels for detail**: full model, one expanded block, sublayer insets, joined by thin
  dashed connectors.
- **Generic vocabulary for a general method**: point or element, feature id, region or group, raw
  signal. Name hierarchy levels by depth, not by a domain concept. Show the home domain as one
  example among peers.
- **Tabular models** (Suggested, not yet tested in real work): rows as `cellGrid` with a `rowTag` for
  context versus query rows, features as columns, held-out labels in the target color, row-wise and
  column-wise attention as two small matrices side by side.
