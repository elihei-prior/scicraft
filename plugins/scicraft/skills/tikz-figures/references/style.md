# The paper style, measured

Every value of the style with the figure it was measured in. The source is the set of figures the author made for
their latest paper (an ML conference submission): a training overview, a hierarchy panel, two block cards, a readout
card, an embedding sphere, a composed Figure 1 with data tiles, and a row of tiles. Values were read from the
compiled PDFs with PyMuPDF (`page.get_drawings()` for fills, strokes and widths; `page.get_text("dict")` for fonts and
sizes) and checked against the scripts that drew them. `assets/preamble.tex` defines all of them under the role
names below.

**Contents**
1. How to measure a figure
2. Type
3. Colors by role
4. Strokes, dashes and heads
5. Block cards: sizes and stations
6. Training overview: shapes and marks
7. Hierarchy panel
8. Sphere glyph and sphere figure
9. Composition: tiles, rules, titles, letters
10. Design width and print scale
11. What the style never has

## 1. How to measure a figure

```python
import fitz                                   # PyMuPDF
page = fitz.open("figure.pdf")[0]
for d in page.get_drawings():                 # fill, color, width, dashes, rect, fill_opacity
    ...
for b in page.get_text("dict")["blocks"]:     # spans: font, size, color, bbox
    ...
```

- **PDF units are big points (bp).** A TeX point is 1/72.27 in and a bp 1/72 in, so a 0.4 pt TeX line reports as
  0.3985 bp and a 14 pt font as 13.95. The source scripts wrote coordinates in bp (`x=1bp, y=1bp`) because a patch
  drawn in TeX points over an included PDF slid off its artwork by 0.375 percent.
- **An included PDF keeps its clipped-away content.** `get_drawings()` on a patched figure also returns the artwork
  outside the clip. Restrict the measurement to the visible region.
- **Text colors come back rounded.** `black!70` reads as `#4C4D4C`, `black!68` as `#525252`.

## 2. Type

The TeX default: Computer Modern text (CMR10/12/17 in the PDF) and default math (CMMI, CMSY, CMEX), `fix-cm` for
arbitrary sizes, `amsmath` and `amssymb`. No font encoding package, no sans text or sans math package, no
`mathastext`, no `lmodern`. The micro sign is `$\mu$`. The author asked for a sans face one morning and reversed it
the same evening ("make both figures default tikz/tex font"); a figure in this style never offers a sans option.

| Role | Design size | Color | Measured in |
|---|---|---|---|
| card name on the border (`\fName`) | 14.0 pt | black | block cards |
| stream caption, output caption, legend line (`\fCap`) | 13.6 pt | black, output caption `glossink` | block cards |
| text inside boxes (`\fBox`) | 13.2 pt | black | block cards |
| gloss, wire label, symbol beside a glyph (`\fNote`) | 13.0 pt | `glossink` | block cards |
| overview label (`\fLabel`) | 13 pt | black | training overview |
| two-line label inside an encoder slab (`\fSlab`) | 10 pt | black | training overview |
| overview gloss (`\fGloss`) | 11 pt | `glossink` (the overview used `black!68`) | training overview |
| composition panel title (`\fTitle`) | 16 pt | black, letter bold | composed Figure 1 |
| label over a data tile (`\fTile`) | 13.5 pt | black | composed Figure 1, tile row |
| count or caption under a tile (`\fCount`) | 12.5 pt | black | composed Figure 1 |
| bare panel letter (`\fLetter`) | 20 bp bold | black | composed Figure 3 |

- **A label has two levels**: a black name and a gray gloss 15 bp under it ("queries" over "$K$ seed tokens").
  Leading 15 bp at 13 to 13.6 pt, 1.1 times the size.
- **Text is black. Secondary text is `black!70`**: the gloss under a name, wire labels ($q$, $k, v$), symbols beside
  glyphs, the output caption. Long gray explanations were rejected ("grey long explainations in my beautiful clean
  figure"); the gray is for one short second level, never prose. Data panels keep all text black (sibling skill
  `data-figures`).
- **Names as a reader meets them**, never internal names: "a token" and "its neighborhood", not the code's
  variable names. Symbols use the paper's own notation.

## 3. Colors by role

| Token | Value | Role | Measured in |
|---|---|---|---|
| `ink` | black | wires and text | everywhere |
| `glossink` | `black!70` (`#4C4D4C`) | secondary text, braces | block cards |
| `boxline` | `#333333` | outline of every box | block cards |
| `chipline` | `#404040` | outline of token chips | block cards |
| `miniline` | `#666666` | outline of the mini icon | block cards |
| `cardline` | `#B2B2B2` | card frame | block cards |
| `tokblue` | `#93B4D8` | token chips: a level's output tokens | block cards, hierarchy |
| `tokorange` | `#F0B060` | token chips: the tokens a block consumes | block cards, hierarchy |
| `tokpurple` | `#B9A3DC` | token chips: seed queries until they become the set's tokens | block cards |
| `tokgreen` | `#8FBFA0` | token chips: a fourth kind (an earlier card) | hierarchy source |
| `tokyellow` | `#F5D36B` | leaf chips; the selected path | hierarchy panel, readout card |
| `oppeach` | `#FBE0C2` | operation box: cross-attention, pooling | block cards, hierarchy |
| `opmint` | `#D8E9DF` | operation box: self-attention, neighborhood | block cards, hierarchy |
| `opgray` | `#E8E8E8` | operation box: graph layer | hierarchy panel |
| `slabgray` | `#E8E8EC` | encoder slab with a domed top | training overview |
| `wheat` | `#F5E2B0` | predictor with a D-shaped cap | training overview |
| `panelgray` | `#F4F4F5` | a faded module outside the claim (a grayed decoder after the loss in an earlier version; dropped from the final) | earlier training overview |
| `lossline`, `lossfill` | `#D93025`, `#FBE9E7` | the single loss box | training overview |
| `ptblue`, `ptochre`, `ptpurple` | `#5C8CC4`, `#C98F3D`, `#9475B5` | point categories in crops and graphs (drawn at opacity 0.9) | training overview |
| `washblue`, `washochre`, `washpurple` | `#A9C3E2`, `#E6D4AE`, `#CDBBDF` | density washes, about 45 percent tints of the point hues | training overview (the field tile) |
| `edgeline` | `black!40` | point-graph edges | training overview |
| `cropline` | `black!45` | crop frame | training overview |
| `queryline` | `black!55` | query box | training overview |
| `zoomboxline` | `black!75` | the box that marks the next crop | training overview |
| `zoomline` | `black!30` | dashed zoom connector | training overview |
| `maskline`, `maskfill`, `maskedpt` | `black!40`, `black!5`, `black!13` | masked region and masked points | training overview |
| `tileline` | `black!28` | data tile frame | composed Figure 1, tile row |
| `ruleline` | `black!22` | rules between panels | composed Figure 1 |
| `tilepale` | `#FCEFC4` | context tiles of the pyramid (the selected tile's siblings, the top tile) | hierarchy panel |
| `tilestrong` | `#F5D36B` (= `tokyellow`) | the selected tile at every level, the selected tree nodes | hierarchy panel |
| `treeedge` | `black!55` (`#737373`) | tree edges | hierarchy panel |
| `graticule` | `black!22` | sphere glyph graticule | training overview |
| `ramp1` to `ramp5` | `#F1F6FF #C7DCFF #8FB9FF #4D97FF #003FBD` | the package's sequential ramp (data-figures `RANK5`) for heat matrices | sibling skill |

- **A chip color names a kind of token and keeps that meaning in every panel.** In the source, seed queries were
  purple and stayed purple until the operation that turned them into the set's tokens, where they became orange;
  a level's output was blue in the cards and in the hierarchy panel alike.
- **One filled box per block.** The operation (attention, pooling, graph layer) carries the pastel; every other box
  is white with a `boxline` outline.
- **The yellow is one meaning.** The leaf chips, the selected tiles and the selected tree nodes share `#F5D36B`
  because they mark one point's own path through the hierarchy. The two tokens exist so a paper can change one role.
- To override a value for a paper, redefine the token after the preamble (`\definecolor{oppeach}{HTML}{...}`).
  That is the only knob.

## 4. Strokes, dashes and heads

| Element | Width | Color | Dash | Measured in |
|---|---|---|---|---|
| card frame | 0.40 pt | `cardline` | | block cards |
| chip outline | 0.40 pt | `chipline` | | block cards |
| box outline, wire | 0.45 pt | `boxline`, black | | block cards |
| residual | 0.40 pt | black | | block cards |
| mini icon, brace | 0.35 pt | `miniline`, `glossink` | | block cards |
| arrowhead (cards) | `Triangle[length=3.9bp, width=3.0bp]` | black | | block cards |
| overview wire | 0.70 pt, `Stealth` | black | | training overview |
| EMA wire | 0.70 pt, `Stealth` | black | `dashed` (3 pt on, 3 pt off) | training overview |
| stop-gradient slashes | 0.70 pt, two slashes 0.34 x 0.18 cm, 0.16 cm apart | black | | training overview |
| query box | 0.6 pt, corners 3 pt | `queryline` | | training overview |
| loss box | 0.9 pt, corners 3 pt | `lossline` | | training overview |
| crop frame | 0.6 pt, corners 2 pt | `cropline` | | training overview |
| mask | 0.6 pt | `maskline` | on 1.4 pt off 1.2 pt | training overview |
| zoom box | 0.55 pt | `zoomboxline` | | training overview |
| zoom connector | 0.45 pt | `zoomline` | on 2 pt off 1.8 pt | training overview |
| graph edge | 0.34 pt | `edgeline` | | training overview |
| hierarchy rail | 0.60 pt, `Stealth[length=3.9bp, width=2.9bp]` | black | continuation: on 2.989 bp off 2.989 bp | hierarchy panel |
| hierarchy box | 0.50 pt, corners 1.0 bp | black | | hierarchy panel |
| pyramid tile | 0.35 pt (top tile 0.55 pt) | black | | hierarchy panel |
| tree edge, tree node | 0.50 pt | `treeedge`, black | | hierarchy panel |
| selected tree path | 1.1 pt | black | | hierarchy panel |
| point graph under the pyramid | 0.22 pt | `black!70` | | hierarchy panel |
| sphere glyph graticule | 0.32 pt | `graticule` | | training overview |
| tile frame | 0.40 pt | `tileline` | | composed Figure 1 |
| panel rule | 0.40 pt | `ruleline` | | composed Figure 1 |

- **Wiring is orthogonal**: horizontal and vertical segments only, joined at right angles. A crossing claims that
  two wires do not connect, so every crossing is removed or named (`scripts/audit_layout.py` reports them).
- **Dashes mean two things**: a weight copy (EMA) and "continues below" (the rail into a level that is not drawn).
- **An arrowhead stops 1 bp short of a box** in the cards (a wire from y to `top - 1`); overview arrows end on the
  shape's edge.

## 5. Block cards: sizes and stations

Units are bp, y downward in the generator, TikZ y upward.

| Item | Value |
|---|---|
| card | 244 x 492, corner 3.0, frame 0.40 pt `cardline`; cards 14 apart, margin 2.5, top 10 |
| plain box | 92 x 28, corner 1.6 (every LayerNorm, FFN, MLP) |
| operation box | 136 x 40, corner 1.6, the one pastel box |
| chip cell | 4.4, gap 1.2; a token is a row of 4 cells (21.2 wide) |
| K-deep stack | 4 rows behind one another, each 2.8 up and right; back rows drawn first |
| width brace | over the back row, raised 1.4, amplitude 3.2, label 8.5 above |
| depth brace | along the stack's diagonal, back to front, 2.2 clear of the corners, amplitude 3.2, label 7 out |
| join circle | radius 5.6, white fill, 0.45 pt; the plus arms 0.55 r at 0.40 pt |
| junction dot | radius 1.0 |
| card name | 12 right of the card edge, baseline 0.32 x size below the border, border masked 3 to each side |
| mini icon | cells 6.0, gap 1.5, right edge 12 inside the card, top at the panel's y 20 |
| stream columns | queries at 0.25, keys at 0.72, trunk at 0.47 of the card width |

Vertical stations shared by every card (y from the panel top, card top at 10):

| Station | y | Station | y |
|---|---|---|---|
| mini icon | 20 | first join | 268 |
| caption | 54 | second norm | 298 |
| gloss | 69 | FFN | 334 |
| front stack row | 106 | second join | 366 |
| residual tap | 122 | pooled stack | 396 |
| first norm | 154 | injection join | 426 |
| wires meet | 184 | output stack | 458 |
| $q$, $k,v$ labels | 195 | output caption | 484 |
| operation box | 218 | legend line | 521 |
| position note | 250 | | |

- A card drawn wider for a main-figure slot changes its numbers together, never one at a time: the readout card
  ran at width 360, boxes 118 x 34, operation box 184 x 48, type 20, 19, 18.5 and 18 pt, chips 5.2 with gap 1.8 and
  offset 3.6, join radius 6.5, mini cells 8 with gap 2, its own stations over the same height 492
  (`assets/figkit.py`, `Style.scaled`).
- The name must fit the card with the mini icon beside it. A 225 bp name on a 244 bp card did not leave room, and
  the captions moved 6 bp down to give the icon its own row.

## 6. Training overview: shapes and marks

Units are cm, as the source drew them.

| Item | Value |
|---|---|
| encoder slab | `slabgray`, no outline; 3.35 wide, straight sides 0.82, domed top with Bezier controls 0.55 above the sides; two-line label at 10 pt, 0.55 above the base |
| predictor | `wheat`, no outline; straight part 2.31, D cap radius 0.53, left corners rounded 3 pt; label at 13 pt |
| query box | white, `queryline` 0.6 pt, corners 3 pt, inner separation 5 by 4 pt; two lines, name over its symbol |
| loss box | 0.90 x 0.84, `lossline` 0.9 pt on `lossfill`, corners 3 pt; only $\mathcal{L}$ inside |
| crop | 1.70 square, `cropline` 0.6 pt, corners 2 pt, white |
| point | radius 0.032, opacity 0.9; masked point radius 0.028 in `maskedpt` |
| graph node | radius 0.052, opacity 0.9; edges 0.34 pt `edgeline` |
| sphere glyph | radius 1.02, graticule 0.32 pt `graticule` clipped to the disk, three soft blobs |
| type | labels 13 pt, slab labels 10 pt, gloss 11 pt |

- **One loss box, no legend, no glosses on the overview.** The loss box sits where the two compared quantities meet:
  the prediction $\hat y$ enters one face, the target $y$ rises into another with the stop-gradient slashes on its
  riser. The full objective goes in the caption ("go back to the abstract's one L loss").
- **Inputs are crops of one field**: one crop with dashed masked regions, one with a category of points grayed out,
  both from the same crop, which in turn is a crop of the field (section 6 of `references/geometry.md`).

## 7. Hierarchy panel

| Item | Value |
|---|---|
| tree node | circle, diameter 11.34 bp, white, 0.5 pt black; selected nodes `tilestrong` |
| tree edge | Bezier from the parent's bottom to the child's top, 0.5 pt `treeedge`; the selected path 1.1 pt black |
| pyramid | one isometric grid per level, tiles 2:1 diamonds; top tile 137.44 x 68.72 bp; each level halves the tile; tiles are separate diamonds with a hairline of white between them |
| pyramid fills | the selected tile `tilestrong`, its siblings `tilepale`, every other tile white; the single top tile `tilepale` |
| level label | $\ell = L-1$ at 17.9 pt black, the tile size ($W$, $W/2$) under it at 15.9 pt `glossink` |
| chips in the rows | cells 6.8 bp, 0.40 pt black outline; five cells per row |
| boxes in the rows | 45.36 x 22.68 bp, 0.5 pt black, corners 1.0 bp, labels 10.76 pt |
| rails | 0.6 pt with Stealth heads; up the right side into the pooling box, out its left side into the next level's row; the rail into the lowest drawn level is dashed |
| point graph | dots radius 1.31 bp black, edges 0.22 pt `black!70` |

## 8. Sphere glyph and sphere figure

**Glyph** (training overview): radius 1.02 cm; 12 meridians every 30 degrees and parallels from -60 to 60 degrees at
a view elevation of about 15 degrees, 0.32 pt `graticule`, clipped to the disk, no outline; three blobs of 16
concentric fills each, from about 95 percent white to a soft hue (`#81A6D2`, `#D6A869`, `#AC94C6`), radii 0.53,
0.47 and 0.41 cm, centered at (-0.20, 0.38), (0.35, -0.53) and (-0.77, -0.43) cm from the center.
`scripts/sphere.py --glyph` emits it.

**Figure** (the embedding sphere): radius 4.05 cm, view elevation 14 degrees; graticule 0.3 pt `black!15`, outline
0.45 pt `black!22`; a radial shading from white to `black!2`; clusters drawn as von Mises-Fisher samples with
density rings at cap masses 0.50 and 0.85 (0.35 pt in 0.6 times the hue; fills tinted 30 percent at opacity 0.30);
points radius 0.032 cm; partial sums 0.95 pt and the resultant 1.45 pt black with Stealth heads; parallelogram sides
`black!45` 0.5 pt dash 2.2/1.8; ties to the surface `black!45` 0.45 pt dash 1.6/1.6; the radial projection 0.8 pt
dash 2.4/1.9; the geodesic between the two directions `black!55` 0.55 pt dash 2/1.8; origin a white disk 0.150 with
a 0.9 pt ring 0.132 and a dot 0.058; hollow surface dots 0.062 with a 0.6 pt outline.

## 9. Composition: tiles, rules, titles, letters

| Item | Value | Measured in |
|---|---|---|
| canvas | 31.57 x 16.03 cm (894.96 x 454.28 bp), printed at 13.97 cm | composed Figure 1 |
| tile frame | 0.4 pt `tileline`, drawn on the raster's edge | composed Figure 1 |
| tiles | the whole view 6.90 cm, the two views under it 3.30 cm; the tile row 3.48 cm at a pitch of 3.67 cm with 0.36 cm more between two groups | composed Figure 1, tile row |
| rules | 0.4 pt `ruleline`, vertical, from the captions' level to the titles' level | composed Figure 1 |
| panel title | `\textbf{a)}\ \ Point field`: bold letter and parenthesis, two spaces, a name of two to four words, 16 pt, anchor south west, one baseline for all titles | composed Figure 1 |
| tile label | 13.5 pt centered 0.45 to 0.55 cm above the tile edge; two lines allowed (11.5 pt) | composed Figure 1 |
| count | 12.5 pt centered 0.43 cm under the tile ("$\sim$24k points"), the real count of what the tile shows | composed Figure 1 |
| caption | 12.5 pt, two lines, under the tiles ("colored by" plus what) | composed Figure 1 |
| bare letter | 20 bp bold, every letter one size on one baseline 17 bp under the top | composed Figure 3 |
| scale bar | baked into the raster: white bar 1.8 pt wide (at print size) with a dark halo 1.0 pt wider, right end at 94 percent of the tile width, 5.5 percent above the bottom, label centered over the bar | tile helper of Figure 1 |

- Raster tiles are rendered at twice their print size (`SUP = 2`, 500 dpi) and placed at print size; marker areas
  are quoted in printed pt squared and drawn as `area * SUP**2`.
- **Baked text is type too.** The source's scale-bar labels were set at 10.5 pt at the tile's print size; the tile
  was then placed at 6.90 of its 7.15 cm and the composition printed at 0.443, so the labels printed at about
  4.5 pt, under the floor, and no PDF text audit could see it. `scripts/tiles.py` computes the baked size from the
  final print scale.

## 10. Design width and print scale

The figures are drawn large and printed small, so the design width decides the type on the page:

| Figure | Design width | Printed at | Scale | Smallest base type on the page |
|---|---|---|---|---|
| block cards, three in a row (an earlier layout) | 752 bp | 388 bp (0.98 of a 396 bp text block) | 0.516 | 6.7 pt (13.0 pt notes) |
| hierarchy panel plus readout card (final) | 871 bp | 388 bp | 0.446 | 4.8 pt (box labels of the patched panel); the card's 18 pt notes 6.2 pt |
| composed Figure 1 | 894.96 bp | 396 bp | 0.443 | 5.1 pt (11.5 pt two-line tile labels); baked scale-bar labels about 4.5 pt |

- **Compute the printed size of every type size from the print width before drawing**:
  printed pt = design pt x print width / design width. `scripts/print_scale.py` does it for a plan or for a compiled
  PDF and fails under the floor.
- **The floor is 5 pt**, and in-cell values of a dense matrix may go to 3.3 pt, never lower (sibling skill
  `data-figures`, `references/style-tokens.md`). The tiers there are 7, 6 and 5 pt with an 8 pt bold letter.
- **Every version of the source figures before this rule shipped type at 3.5 pt on the page.** The rule came from
  that.
- **Where the paper went under the floor, and why it was accepted.** The box labels of the hierarchy panel printed
  at 4.8 pt (4.9 pt in the 850 bp version). That panel was a patch over artwork whose source was lost; its labels
  were re-set at 1.2 times their original 8.97 pt inside boxes fixed by the surrounding artwork, and the author
  chose the upright layout over a sideways full page that would have printed the cards larger. A new figure has
  no such constraint: redraw or give the panel more width.

## 11. What the style never has

- A sans font, a theme switch, accent or contrast tokens.
- Shadows, 3-D bevels, pills, numbered badges, banners, a title over a gray subtitle.
- Gradients, except the stepped radial blobs of the sphere glyph and the shading of the sphere figure.
- A legend on an overview; prose inside a figure; illustrative numbers ("don't give numerical examples like 0.69").
- A row of n chips for a set of K vectors: that asserts a width the figure does not mean. A set is a stack.
