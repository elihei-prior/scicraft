---
name: tikz-figures
description: Draws paper figures in TikZ and PGFPlots in one measured style, the style of the author's latest paper figures (Computer Modern type, white hairline boxes with one pastel operation box per block, token chips and K-deep stacks, cards named on their top border, orthogonal hairline wiring, encoder slabs with one loss box, crops with zoom connectors, an isometric hierarchy pyramid, a unit sphere, composed panels with data tiles). Use it whenever a figure is drawn in LaTeX, even when the user only says "draw my architecture", "make Figure 1", "the block diagram is wrong", "the text is tiny in print", "it overlaps" or "camera-ready is Friday". Holds the preamble, a Python kit and generators for real geometry, a PDF layout audit, a print-scale check, seven examples and a failure catalog. For matplotlib panels use data-figures, for HTML-canvas schematics canvas-schematics, for the whole loop of a results figure figure-development, for tokens shared across media design-system.
---

# tikz-figures

How to draw a paper figure in TikZ that its author puts in the paper without redrawing it. Distilled from the
figures of the author's latest paper (block cards, a training overview, a hierarchy panel, an embedding sphere, a
composed figure with data tiles), each measured, checked against the code it depicts and audited until the audit
read 0, and from two figure skills the author threw out before this one. There is one style: every value in it was
measured from those figures, and every rule keeps the reason the author gave. Typst output is not covered.

> **PRIME DIRECTIVE: draw with the preamble's styles only, draw only what the code or the data computes, and look at
> the compiled PNG and its audit at print size before showing anything.**

Three failures cost the most time in the source work. Guard against them from the first minute:

1. **Type that vanishes in print.** The figures are drawn large and printed small, and every version of the source
   figures before the print-scale rule shipped type at 3.5 pt on the page. Compute the printed size of every type
   size before drawing (section 2).
2. **A drawing that misstates the method.** One norm where the code has two, a residual from the wrong stream, a
   hand-drawn tree, zoom levels drawn apart: each looked right and was wrong. Read the code first, and let code
   draw every structure that claims real geometry (sections 4 and 6).
3. **Drift from the look.** A new theme, a sans face for one day, a panel rewritten in words: each was rolled back.
   Keep the measured style and the author's drawing, and change only what was asked (sections 1 and 9).

## 0. Before starting

Collect by reading the project. Ask only for what cannot be found, in one message:

- **Where the figure goes**: the text width (an ICLR-style text block is 5.5 in = 396 bp), the slot (full width at
  `.98\linewidth`, half, wrapped beside its paragraph, an appendix twin), and the page budget.
- **The paper's notation and wording**, and its other figures: a chip color names one kind of token across all of
  them, and symbols are the paper's.
- **The code behind every mechanism drawn** (the module and the function), and **the data or seed behind every
  generated geometry** (a CSV, the method's own function).
- **A reference figure**, when the user names one: then work in mimic mode (`references/workflow.md`, section 3).
- **Who checks the PNG, and when**: the deadline decides how many rounds there are.

Work in a folder per figure, outside the skill:

```
figures/<figure>/
  <figure>.tex        \def\figpreambleonly{} \input{preamble.tex}, \begin{document}, one tikzpicture
  gen_<figure>.py     when any geometry is computed (it writes frag/ and facts.json)
  frag/*.tex          generated fragments, read with \input while iterating
  facts.json          every number the figure or its caption shows
```

```bash
python3 <skill>/scripts/render_figure.py <figure>.tex --texinputs <skill>/assets       # compile, PNG, gates
python3 <skill>/scripts/render_figure.py <figure>.tex --texinputs <skill>/assets --inline <figure>_final.tex
```

The scripts need Python 3.9 or later. `render_figure.py`, `check_tikz_safety.py`, `compile_snippets.py`,
`build_examples.py` and the kit's emitter use the standard library; the audit, the print-scale check and
`compose.py` need PyMuPDF; the generators need numpy and scipy (`zoom_cascade.py` also contourpy, `tiles.py` also
matplotlib); contact sheets need Pillow. TeX needs `pdflatex` with `standalone` and `pgfplots`, and `pdftoppm`.

## 1. The style

- **One preamble, one knob.** `assets/preamble.tex` holds the type, every role color, every style and macro.
  Copy it above its line `%%%% FIGURE BODY`, or `\input` it as above and inline at delivery. A paper that needs
  another value redefines that one color after the preamble (`\definecolor{oppeach}{HTML}{...}`); there is no
  theme switch and no sans option.
- **Type is the TeX default**: Computer Modern text and default math, `fix-cm` for arbitrary sizes, `amsmath`,
  `amssymb`, the micro sign as `$\mu$`. The author asked for a sans face one morning and reversed it that evening
  ("make both figures default tikz/tex font"). Re-audit every label after any font change.
- **Text is black; secondary text is `black!70`** (`glossink`): the gloss under a name, wire labels, symbols beside
  glyphs, output captions. A label has two levels, a black name and a gray gloss 15 bp under it ("queries" over
  "$K$ seed tokens"). The gray is one short second level, never prose.
- **One filled box per block.** The operation (attention, pooling, graph layer) carries the pastel; every other box
  is white with a hairline outline.
- **A chip color names a kind of token** and keeps that meaning in every panel of the paper.
- **Wiring is orthogonal**: horizontal and vertical segments meeting at right angles. A crossing claims that two
  wires do not connect, so each one is removed or named.

Design sizes (they print at the scale of section 2):

| Element | Value |
|---|---|
| card type | name 14.0 pt, captions 13.6, in boxes 13.2, notes 13.0 |
| overview type | labels 13 pt, two-line slab labels 10 pt, gloss 11 pt |
| composition type | titles 16 pt, tile labels 13.5 pt, counts and captions 12.5 pt, bare letters 20 bp bold |
| card strokes | frame 0.40 pt, chip 0.40, wire 0.45, residual 0.40, mini icon 0.35; head `Triangle[length=3.9bp, width=3.0bp]` |
| card parts | plain box 92 x 28 bp, operation box 136 x 40 bp, corners 1.6 bp; card corner 3.0 bp; join radius 5.6 bp; dot radius 1.0 bp |
| tokens | chip 4.4 bp, gap 1.2; a token is a row of 4 cells; a set of K is 4 rows stacked, each 2.8 bp up and right |
| overview strokes | wires 0.7 pt `Stealth`; crop 0.6 pt `black!45` corners 2 pt; query box 0.6 pt `black!55` corners 3 pt; loss 0.9 pt |

Colors by role (every value and the figure it was measured in: `references/style.md`):

| Role | Tokens |
|---|---|
| outlines | `boxline` #333333 boxes, `chipline` #404040 chips, `miniline` #666666 icons, `cardline` #B2B2B2 cards |
| token kinds | `tokblue` #93B4D8, `tokorange` #F0B060, `tokpurple` #B9A3DC, `tokgreen` #8FBFA0, `tokyellow` #F5D36B |
| operations | `oppeach` #FBE0C2 cross-attention and pooling, `opmint` #D8E9DF self-attention, `opgray` #E8E8E8 graph layer |
| overview | `slabgray` #E8E8EC encoder slab, `wheat` #F5E2B0 predictor, `lossline` #D93025 on `lossfill` #FBE9E7 |
| points | `ptblue` #5C8CC4, `ptochre` #C98F3D, `ptpurple` #9475B5; washes #A9C3E2, #E6D4AE, #CDBBDF; edges `black!40` |
| frames | crop `black!45`, query `black!55`, zoom box `black!75`, zoom connector `black!30` dashed, mask `black!40` dashed on `black!5`, tile `black!28`, rule `black!22` |
| hierarchy | `tilepale` #FCEFC4, `tilestrong` #F5D36B, tree edges `black!55` |
| plots | `hero` #0072B2 the paper's method, `rival` #E69F00 the strongest comparator, `othergray`, `basegray`; heat matrices on `ramp1` to `ramp5` (all from the sibling `data-figures`) |

The style never has: a sans face, shadows, bevels, pills, badges, banners, gradients (except the sphere's stepped
blobs and shading), a legend on an overview, prose inside a figure, illustrative numbers, or a row of n chips for a
set of K vectors.

## 2. Plan: exact or schematic, and the printed size

- **Decide exact or schematic for every quantitative element.** Exact means computed from the code, the data or a
  stated equation, with real ticks and real lengths; schematic means plainly qualitative, with no number that looks
  measured and a caption that says "schematic". If the math cannot be specified, the element is schematic.
- **Compute the printed size of every type size before drawing**: printed pt = design pt x print width / design
  width. The floor is 5 pt for any base size; in-cell values of a dense matrix may go to 3.3 pt; the tiers of the
  package are 7, 6 and 5 pt with an 8 pt bold letter (sibling `data-figures`). Give a panel more width before
  shrinking one label.

```bash
python3 scripts/print_scale.py --design-width 850 --print-width 0.98x396bp --sizes 14,13.6,13.2,13   # plan
python3 scripts/print_scale.py figure.pdf --print-width 0.98x396bp                                    # measure
```

| Figure in the source | Design width | Printed at | Smallest base type on the page |
|---|---|---|---|
| block cards, three in a row | 752 bp | 388 bp (x0.516) | 6.7 pt |
| hierarchy panel plus readout card | 871 bp | 388 bp (x0.446) | 4.8 pt, accepted once (below) |
| composed figure with data tiles | 894.96 bp | 396 bp (x0.443) | 5.1 pt; baked scale-bar labels about 4.5 pt |

The one accepted case under the floor was a patch over artwork whose source was lost, with boxes fixed by the
surrounding drawing, where the author chose an upright figure over a sideways page. A new figure has no such
constraint. Text baked into a raster is invisible to the measure mode; `scripts/tiles.py` sizes it from the final
print scale.

- **Sketch on a grid before coding**: bp (`x=1bp, y=1bp`) for cards, generated geometry and patches (a TeX point is
  0.375 percent smaller than a bp, enough to slide a patch off its artwork); cm for an overview, as the source drew
  it. Cards of one figure share their vertical stations, so their blocks align across the row.

## 3. The grammar

Every element is a style or a macro of the preamble. Macros take bare coordinates: `\tokrow{0,5}{tokblue}{4}`.

| Element | Style or macro | Rule |
|---|---|---|
| plain box | `box` | white, `boxline`; one size for every LayerNorm, FFN, MLP |
| operation box | `opbox=oppeach`, `opbox=opmint`, `opbox=opgray` | the one filled box of a block |
| token, set of K tokens | `\tokrow{c}{fill}{n}`, `\tokstack[rows]{c}{fill}` | a set is a stack, never a row of n chips |
| width and count braces | `\tokwidthbrace[rows]{c}{$d$}`, `\tokdepthbrace[rows]{c}{$K$}` | once per figure, on the first stack |
| join, junction | `\joincircle{c}`, `\junction{c}` | a join where streams add; a dot where a wire splits |
| residual | `\residual{tap}{margin point}{join}` | pre-norm bypass along the card margin, tapping the query stream |
| wires | `wire`, `wirebare`, `flow`, `flowbare` | heads stop 1 bp short of a box in cards |
| rails | `rail`, `railcont` | feedback between levels; dashed into a level not drawn |
| weight copy, stop-gradient | `ema`, `\stopgrad[angle]{c}` | a dashed EMA wire; two short slashes across the target's wire |
| card | `\card{top left}{w}{h}{name}`, `\twolevel{c}{name}{gloss}` | the name on the top border, the border masked behind it |
| mini icon | `\minipool`, `\minimix`, `\miniread`, `\unitsphere{c}{r}` | top right of a card: what the block does |
| overview modules | `\slab{bl}{w}{label}`, `\dcap{bl}{w}{h}{label}`, `qbox`, `loss` | gray domed encoders, a wheat predictor, one query box, one loss box |
| crops and zooms | `crop`, `maskbox`, `zoombox`, `zoomlink`, `\figpoint`, `\figmasked`, `\fignode`, `graphedge` | every crop shows exactly what its box holds |
| hierarchy | `treenode`, `treeedge`, `treepath`, `\isotile{c}{hw}{fill}` | the selected path strong, its siblings pale |
| composition | `\tile{x}{y}{w}{file}`, `tilelabel`, `tilecount`, `panelrule`, `\paneltitle{c}{a}{Name}`, `\panelletter{c}{a}` | titles of two to four words, letters one size on one baseline |
| text | `capt`, `lbl`, `note`, `glossnote` | black names, gray glosses, one legend line under cards |
| plots | `paperaxis`, colormap `rank5` | section 7 |

```latex
\begin{tikzpicture}[x=1bp, y=1bp, paper]
  \tokstack{0,0}{tokpurple}
  \tokwidthbrace{0,0}{$d$}
  \tokdepthbrace{0,0}{$K$}
  \draw[wire] (0,-2.2) -- (0,-27);
  \node[box] at (0,-42) {LayerNorm};
  \draw[wire] (0,-56) -- (0,-81);
  \node[opbox=oppeach] at (0,-102) {Cross-Attention};
  \draw[wirebare] (0,-122) -- (0,-142.4);
  \joincircle{0,-148}
  \residual{0,-14}{-80,0}{0,-148}
  \draw[wire] (0,-153.6) -- (0,-176.4);
  \tokstack{0,-186}{tokorange}
\end{tikzpicture}
```

`references/grammar.md` has a recipe for every element; `references/style.md` has every value.

## 4. Block cards

- **Read the block's code before drawing it**, and draw the mechanism as the code computes it. A self-attention
  block shares one norm; a cross-attention block normalizes its two streams apart; the residual taps the query
  stream before its norm; a position encoding is drawn where the code applies it; anything the code adds to the
  tokens (a count, a step, an embedding) is a join. The source's first cards had five such errors, and the same
  review asked to "separate layer norm from ffn".
- **A set of K vectors is a stack** with its width and count bracketed once ("if you wanna show it's K then show
  multiple behind each other").
- **Names as a reader meets them**, never the code's variable names; symbols in the paper's notation; one legend
  line under the cards defines every symbol, and a symbol defined nowhere is deleted.
- **The card's name sits on its top border**, the border masked behind the glyphs. The mask is sized from the
  compiled ink in a second pass: `figkit.build()` compiles, measures each name, and compiles again. A fixed mask
  once left a larger name's descenders on the frame line.
- **One width for every card of a figure, shared stations**, a mini icon at the top right, an output caption.
  A wider card for a main-figure slot changes all its numbers together (`Style.scaled`).

```bash
python3 assets/examples/block_cards.py --out build/      # the two-card example, built in two passes
```

`assets/figkit.py` (standard library emitter; PyMuPDF or `pdftotext` to measure) gives `Figure` with `box`,
`opbox`, `tokens`, `width_brace`, `depth_brace`, `arrow`, `join`, `junction`, `residual`, `card`, `mini`,
`two_level`, and reads every size and color from the preamble, so a generated card and a hand-written one look the
same. Details: `references/block_cards.md`.

## 5. Overviews and pipelines

- **One loss box, no legend, no glosses.** The author's direction for the overview: "drop different losses, drop
  the legend ... go back to the abstract's one L loss". The loss box sits where the two compared quantities meet;
  the caption carries the full objective.
- **Encoders are gray domed slabs, the predictor a wheat box with a D cap, the query a white box**; the weight copy
  is the dashed EMA wire between the encoders; stop-gradient is two slashes on the target's riser into the loss.
- **Inputs are crops of one field**: one crop with dashed masked regions, one with a category grayed out, both the
  same crop, which is itself a crop of the field shown on the left. `scripts/zoom_cascade.py --views` writes them.
- **Keep the author's drawing.** A pass that rewrote the overview in words and moved its encoders was rejected
  ("super ugly encoders, do not drift from the previous version so much") and rolled back.
- **Wires start and end on named coordinates** of the fragments they join; a wire typed by hand ended 0.01 to
  0.03 cm short of its frame.

`assets/examples/overview.tex` is the complete example; `references/overviews.md` has pipelines, two inputs that
join, a shared trunk with heads, an encoder-decoder and an agent loop in the same grammar.

## 6. Geometry that must be real

Every structure that claims something about real geometry (a tree, a partition, neighbors, a direction, a length)
is computed by code on a seeded input and emitted as TikZ, with every number written to `facts.json`. A hand-drawn
quadtree was answered with "this is not real quadtree on the points I'm seeing"; a zoom whose levels were drawn
apart showed neighbors from nowhere.

| Script | Writes | Checks it runs |
|---|---|---|
| `scripts/hierarchy.py` | a quadtree over seeded points, its tree, the isometric pyramid, rows of chips through blocks with rails, the point graph | the selected path holds the selected point at every level |
| `scripts/sphere.py` (`--glyph` for the overview) | von Mises-Fisher clusters on the unit sphere, density rings, two sets' resultants and their sum, the radial projection | the parallelogram closes, the resultant's length is exact, the projection is radial |
| `scripts/zoom_cascade.py` (`--points` a CSV) | field, region, crop and k-nearest-neighbor graph of one point field; `--views` the masked views | neighbors found on the full field; edges clipped by the generator |
| `scripts/tiles.py` | raster tiles of one sample at twice print size, pooled bins, baked scale bars, counts as macros | every printed count from the records; baked label size at print; a bin pitch that is a whole number of raster cells |

```bash
python3 scripts/zoom_cascade.py --out frag/ --points points.csv --k 6 --preamble assets/preamble.tex
python3 scripts/hierarchy.py --out frag/ --seed 5 --levels 4
```

- **Every random choice has a seed and every showcase choice a stated rule** (the window of highest category
  entropy, the point nearest the center of the field), both in `facts.json`. A choice made by eye is a choice a
  reviewer can call cherry-picked.
- **Replace the example computation with the method's own function** and keep the drawing.
- **Clip in the generator.** Ink hidden under a TikZ clip is still in the PDF, and the audit reads it.
- **Iterate with `\input`, deliver inlined** (`render_figure.py --inline`), compiled alone in an empty folder.
- **When the real code cannot run here, say so** and draw from its exported output, or mark the figure schematic.

Details: `references/generators.md`, `references/geometry.md` (sphere, vectors, densities, fields, zoom),
`references/hierarchies_graphs.md` (trees, pyramids, graphs, partitions).

## 7. Plots in the same style

PGFPlots with the preamble's `paperaxis`: left and bottom axis lines without arrowheads, ticks outside, type set at
its printed size (5, 6 and 7 pt), frameless legends. Results panels assembled with matplotlib panels belong to
`data-figures`.

- **A direct label where it fits**, no legend ("the legend is AI slop").
- **Panel titles of two to four words** ("make it clear one thing and go").
- **Significance is an asterisk after the number**, drawn as its own text so the number stays centered, explained
  in the caption ("instead of bolding you can add star"). No bold in a matrix, and no dagger.
- **A heat matrix carries the value in every cell** on the package's sequential ramp, with scale brackets over
  column groups; it was the model of the author's results figures ("the heat map one is super cool").
- **Sorted thin bars with the value at the bar end** replace lollipops and forest plots ("just a line plot of
  continuing things").
- **Curves with bands come from the CSV**, mean and spread computed from the records, with the band named in the
  caption.

Recipes: `references/plots.md`.

## 8. Composition and placing in the paper

```bash
python3 scripts/compose.py fig.tex a.pdf b.pdf c.pdf --titles "Point field|Training scheme|Embedding map" \
    --rules --print-width 396bp --compile
python3 scripts/tiles.py --out tiles/ --print-scale 0.443 --label-pt 5.5
```

- **A composition is written by the script from the panels' real page sizes**: panels set to one height on one
  row, a 20 bp gap, letters or titles set in the preamble's type on one baseline, the scale and smallest printed
  type of each panel reported. Rebuild a panel, rerun the script.
- **Two title styles, one per figure**: a bare bold letter, or a bold letter with a parenthesis and a name of two to
  four words ("a)  Point field"). One letter size per paper.
- **Data tiles**: a hairline frame, a label above, the real count of what the tile shows below, a caption that says
  what the color means ("if you use a color explain what it is"), scale bars baked into the raster, one color
  mapping for every tile.
- **A main figure has an appendix twin.** A fix to one is a fix to the other and to both captions.
- **Placing**: full width at `.98\linewidth` by default; a figure wrapped beside the paragraph that discusses it
  at 0.43 to 0.46 of the line width ("I want them left or right of their corresponding text"), its caption at three
  lines at most.

Details: `references/composition.md`.

## 9. Patching a figure and editing the author's file

- **A figure whose source is lost is artwork.** Include the PDF at natural size, wipe only what changes (0.6 bp
  around a glyph), re-set text at the measured origins in bp, and apply one measured offset to every redrawn
  element.
- **Paint hides text from the eye, not from the text layer.** A patched figure kept its wiped labels and a clipped
  old panel searchable in the PDF. Crop the source PDF to the visible region when hidden text must not be read.
- **Patch an author's hand-made file by exact entries**, each asserted to occur once, never by counting lines. An
  edit by line count asserted on the wrong lines and left the file unchanged.
- **Keep every accepted version reachable**, and roll back to the last accepted one when a revision drifts.

Details: `references/patching.md`.

## 10. Animation and the biology tier

- **Animate only when motion is the argument**, as a frame deck with one locked bounding box, a label shown only in
  the frames where it is true, and a last frame that stands as the figure (`references/animation.md`; suggested,
  not yet tested in real work).
- **Biological objects** (cells, sections, molecules, sequences) are a marked tier with the same strokes: cells as
  outlines, never color fills ("cells should not be filled with colors ... white thin boundaries"), color on the
  points, a scale bar on anything that claims a size (`references/biology_tier.md`; suggested, not yet tested in
  real work). Characterful tissue cartoons go to `canvas-schematics`.

## 11. The loop

```
request -> exact or schematic -> printed sizes -> sketch -> draft -> render -> LOOK -> audit -> repair -> render
```

- **Render and look every round.** The compiler cannot see overlap, clipping, crowding or a mislabeled curve.
  `render_figure.py` writes versioned PNGs (`fig_v03-1.png`), so a cached viewer cannot show an old one.
- **Audit the PDF**: `python3 scripts/audit_layout.py fig.pdf` reports text over text, a stroke through text, text
  off the page, doubled ink, crossings and stubs, and exits 1. A known residue is accepted by name with its reason
  (`--accept residues.txt`); never run it unrestricted on a patched figure (`--region`).
- **Mimic mode** when there is a reference: list every element of it before coding, match its aspect ratio within
  about 2 percent, reproduce it first and polish second.
- **The smallest change asked, staged sign-off** (layout, then density, then zooms, one panel at a time), and **the
  PNG every turn**: the author judges a figure by looking at it and cannot judge a description.
- **Two strikes.** If the same kind of failure survives two focused repairs, simplify the figure or split it.
- **When the style keeps failing, copy one named exemplar**: one of the seven examples, or a figure the author
  approved, in layout and idioms, then change content only. After three weeks of rejected schematics in an earlier
  project this was the move that worked.

The full loop, the scripts' reach and the catalog of failures that compile cleanly: `references/workflow.md`.

## 12. Check before anything is handed over

Scripted gates first:

1. `check_tikz_safety.py` passes, and the log has 0 errors, 0 overfull boxes and 0 missing characters
   (`render_figure.py` reports all four).
2. `audit_layout.py` reads 0 findings, or each finding is a named residue with its reason.
3. `print_scale.py fig.pdf --print-width <the slot>` reports no base type under 5 pt, and the baked labels of any
   tile are computed at 5 pt or more (or the exception is stated, as in section 2).
4. Every number the figure or caption shows matches `facts.json`; every generated element came from code or data
   with a fixed seed.
5. The inlined `.tex` compiles alone in an empty folder (`render_figure.py --inline`).

Then with eyes, on the PNG at 100 percent and zoomed into every dense spot:

6. Nothing overlaps, nothing is clipped at the page edge, no wire stops short of its box or runs into it.
7. Every color is a role color with one meaning and a key; no stray hue.
8. Every mechanism matches the code; every symbol is defined in the legend line or the caption.
9. Text sits on the center line of its row, panel bottoms are level, no line holds a single word.
10. A last look as a fresh reader, by a second agent when one is available, given only the PNG and the caption.

Then say what was not checked: a mechanism whose code was not available, a geometry drawn schematic, a print width
assumed, a baked label not measured.

## 13. What was thrown out, and what replaced it

| Thrown out | The author's words | Replaced by |
|---|---|---|
| this skill's previous look: a blue and mustard-gold four-tone sans theme with a serif twin | the author called the "blue mustard" look ugly and asked to remove all of it | the measured style of the author's latest paper figures (section 1) |
| a sans face for the figures, for one day | "make both figures default tikz/tex font" | Computer Modern and default math, decided once |
| a panel rewritten in words, its encoders moved | "super ugly encoders, do not drift from the previous version so much" | the author's drawing kept; patches by exact entries |
| an overview with several losses, symbols and a legend | "drop different losses, drop the legend ... go back to the abstract's one L loss" | one loss box; the caption carries the objective |
| type printed at 3.5 pt | "make the minimum size text 2x, and make others proportionally to the minimum one bigger" | printed sizes computed from the design width; a 5 pt floor |
| a hand-drawn quadtree | "this is not real quadtree on the points I'm seeing" | a quadtree computed over seeded points (`hierarchy.py`) |
| illustrative numbers in a figure | "don't give numerical examples like 0.69" | only real values from the records |
| a set drawn as a row of chips | "if you wanna show it's K then show multiple behind each other" | a K-deep stack with a count brace |
| LayerNorm inside the FFN box | "separate layer norm from ffn" | the norm as its own box, the block read top to bottom |
| long gray explanations inside a figure | "grey long explainations in my beautiful clean figure" | a two-level label; the rest in the caption |
| a legend where labels fit | "the legend is AI slop" | direct labels |
| long panel titles | "make it clear one thing and go" | two to four words |
| bold and daggers for significance | "instead of bolding you can add star"; a dagger is a "clear AI slop flag" | an asterisk after the number, explained in the caption |
| lollipop and forest panels | "just a line plot of continuing things" | a heat matrix with values, sorted thin bars |
| two figures side by side in the text | "I want them left or right of their corresponding text" | a figure wrapped beside its paragraph |
| a color with no key | "if you use a color explain what it is" | a key or a caption line for every color |
| the house figure skill used after it kept failing | "try to just plot it using the guidelines in this not our tikz skill, maybe that's the problem" | copy one named exemplar the author approved |

## Reference files

- `references/style.md`: every token with its value and the figure it was measured in; sizes, stations, design
  widths. Read before changing any value.
- `references/grammar.md`: a compiled recipe for every element of the grammar.
- `references/block_cards.md`: the code check, the anatomy and stations, the kit, a hand-written card, joins, wider
  cards, names and the legend line.
- `references/overviews.md`: the training overview and pipelines, joins, shared trunks, encoder-decoders, loops.
- `references/hierarchies_graphs.md`: trees beside isometric pyramids, rows with rails, point graphs, partitions.
- `references/geometry.md`: the sphere, vectors and resultants, densities, fields, symmetry, the zoom cascade.
- `references/plots.md`: PGFPlots in the style: curves with bands, sorted bars, the heat matrix, the dot plot.
- `references/composition.md`: design width, `compose.py`, tiles, titles and letters, twins, placing in a paper.
- `references/math_layout.md`: which symbols may appear, gaps and leading, a loss with braced terms.
- `references/generators.md`: the generator pattern, seeds and stated rules, `facts.json`, the kit's calls.
- `references/patching.md`: a figure whose source is lost, the text layer, exact-entry patches, rollback.
- `references/animation.md`: frame decks with a locked bounding box (suggested, not yet tested in real work).
- `references/biology_tier.md`: the marked biology tier (suggested, not yet tested in real work).
- `references/workflow.md`: the loop, mimic mode, the code check, staged sign-off, two strikes, the exemplar, the
  scripts' reach, the failure catalog, a minimal TeX tree, delivering.

Scripts (each answers `--help`): `render_figure.py`, `check_tikz_safety.py`, `audit_layout.py`, `print_scale.py`,
`compose.py`, `hierarchy.py`, `sphere.py`, `zoom_cascade.py`, `tiles.py`, `compile_snippets.py` (compiles every
recipe of the references, `--audit --safety`), `build_examples.py` (builds, renders, audits and size-checks the
seven examples). Assets: `preamble.tex`, `figkit.py`, and `examples/` (`block_cards.py`, `overview.tex`,
`panel_points.tex`, `panel_field.tex`, `tile_row.tex`; the hierarchy, sphere, zoom cascade and composition come
from the scripts, as `build_examples.py` shows).
