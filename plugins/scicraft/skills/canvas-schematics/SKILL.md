---
name: canvas-schematics
description: Builds method and concept schematics (graphical abstracts, cell and tissue cartoons and pipeline overviews, a datasets-used overview of a benchmark) as one HTML5 canvas rendered headless to a paired PDF and PNG at print size; for a model architecture figure use `tikz-figures` unless the user asks for canvas. Use it whenever a paper, preprint or book needs a schematic or overview figure, even when the user only says "make Figure 1", "rebuild this figure from the slide", "this looks like a slide", "the text is tiny in print", "it overlaps" or "camera-ready is Friday". Holds the print math (10 px per mm, 5 pt floor = 18 px), the anti-slide list, a tested renderer and core library with an architecture pack and a biology pack, the reproduce-the-reference procedure, real data as JS globals, one builder per region, and a QC checklist with lint and overlap scripts. Prefer data-figures for plotted results, tikz-figures for architecture figures or live vector text, figure-development for the figure's story.
---

# canvas-schematics

How to draw a schematic that sits in a journal next to dense data figures without looking like a
keynote: one canvas, laid out in millimeters, drawn through one shared library, rendered by a headless
browser to a PDF and a PNG. Distilled from a year of graphical abstracts, pipeline figures and model
overviews for machine-learning and biology papers, and from the figures the author threw out on the
way. Where the user's own house style differs, theirs wins; write it into SPEC.md and follow it.

> **PRIME DIRECTIVE: draw at the printed size, through one library, and look at the render.** Lay out
> at 10 px per mm so every size is a print size, let region code use only the library's tokens, and
> open the PNG after every change. Most failures below were visible in the first render nobody opened.

The failures that cost the most time:

1. **The slide.** Cards with shadows, pill tags, a big title over a gray subtitle, keynote fonts. The
   first attempts at every schematic in the source work came out this way (sections 3 and 4).
2. **Text that vanishes in print.** 18 px text on a 3200 px canvas printed at 2.9 pt; library tiers
   sat at 4.8 pt. Section 2 makes the floor a number and a script checks it.
3. **Re-deriving instead of reproducing.** Handed a reference, agents reinterpreted it, and the
   figure was "not the same figure". "Re-deriving ad-hoc is the #1 source of rework" (section 5).

## 0. Before starting

Ask first whether a schematic is wanted. The default for a results figure is none: "the data panels
should carry the story". In a book or any document built from an author's existing work, never make
new figures; reuse theirs (crop, place, resample) and say when no figure fits a slot.

Choose the medium next. **An ML architecture or method figure (encoder, predictor, loss, a
teacher-student diagram) goes to the sibling skill `tikz-figures` by default**, because the author
wants those as vector figures and rejected code-drawn ones ("bro no python!!"). Build it
here only when the user asks for canvas. Cell and tissue cartoons, pipeline overviews, graphical
abstracts and dataset overviews stay here. Typst is not shipped in this package; say so when a user
asks for it.

Collect by reading the project:

- the paper's finished figures (the house style the schematic must match) and any style module;
- a reference figure if one exists (a slide, an old version, a published exemplar);
- the method's code, for the mechanism and its notation (section 6);
- the venue's column width (`\the\textwidth` in its template) or the journal's 89 / 183 mm;
- the project's `GUARDRAILS.md` and `NARRATIVE.md` (defined in the sibling skill,
  `project-structure/references/governing-documents.md`). A figure's own SPEC.md and any figure-level
  guardrail or narrative file add to the project's and never relax them.

Ask in one message for what is missing: the printed width, the reference, the claim of each panel,
and whether a TikZ figure of the same paper exists (the canvas theme matches it; `pastel` by
default, section 4).

Work in a folder of its own beside the paper's figures (layout in `references/library.md`).

## 1. Scaffold and prove the pipeline

```bash
F=figN; A=<skill>/assets
mkdir -p $F/code/regions $F/code/data $F/code/_prep
cp $A/core_lib.js $A/pack_arch.js $A/pack_bio.js $A/render.js $A/package.json $F/code/
cp $A/layout_template.js $F/code/layout.js; cp $A/main_template.js $F/code/main.js
cp $A/figure_template.html $F/code/figure.html; cp $A/preview_template.html $F/code/preview.html
cp $A/spec_template.md $F/SPEC.md
cd $F/code && npm install                       # puppeteer and its Chrome, Node 18 or later
node render.js figure.html smoke 1830 1040 out --check && open out/smoke.png
```

- **Smoke-render before writing any region.** Placeholders render as dashed frames with the region
  name; confirm the proportions and the title band. Never fan out on an unproven pipeline.
- **`render.js` requires puppeteer from `package.json` beside it.** The source renderer loaded
  puppeteer from an absolute path inside another project and broke on every other machine.
- Uncomment a region's script line in `figure.html` when its file exists. For a first working region,
  copy `assets/region_example_arch.js` (model overview) or `assets/region_example_bio.js` (cells) to
  `regions/region_a.js` and render it.

## 2. Print math

Every size is chosen for paper. Detail and the conversion for other canvases in `references/print-maths.md`.

| Quantity | Value |
|---|---|
| layout | 10 logical px = 1 mm; 1830 px = 183 mm double column, 890 px = 89 mm single |
| 1 pt | 0.35278 mm = 3.528 px |
| tiers | panel letter 29 px (8.2 pt; 8 pt is the paper default, see `data-figures`), L1 25 px (7 pt), L2 21 px (6 pt), L3 18 px (5 pt, floor) |
| device scale | `CANVAS.S = 3`: PNG at 30 px/mm, about 760 dpi |
| PDF | one page, W/10 x H/10 mm, raster at device scale |

- **Nothing under 18 px**, subscripts included (`LIB.math` keeps them at the floor). The two source
  libraries used 17 px (4.8 pt) for the smallest tier; `core_lib.js` uses 18 px.
- **One panel letter size per paper**, across data, schematic and TikZ figures: 8 pt bold lowercase
  by default (29 px here, the nearest px above 8 pt). A venue's own letter size wins, and a paper may
  choose up to 10.5 pt once for all its figures; then set `FONT.LETTER` to match. The rule is owned by
  the sibling skill `data-figures` (`data-figures/references/style-tokens.md`).
- **Three tiers plus the letter, never a fourth size.** A subtitle is a lighter weight. If text does
  not fit, give the panel area or shorten the text; "shorten text, don't change size".
- **Draw at the width it prints.** Include the PDF at natural size. Rescaling changes every font, and
  two panels scaled separately drew "b and c are different font sizes".
- On an inherited canvas, compute the floor: `python3 scripts/print_maths.py --width-px 3200 --width-mm 180`
  gives 32 px. The old "every font at least 75 px (12 pt)" rule is obsolete.

## 3. Paper figure, not slide

Full list, failure gallery and the declutter standard in `references/paper-not-slide.md`.

- **Delete on sight**: shadows, glows, gradients, 3-D, pills and chips, cards holding text, a second
  title size, banners, gray filler subtitles, sentence titles, arrow narration, caption text inside
  the image, numbered discs as panel letters, filled boxes placed to fill space, panel background
  boxes, dividers, rainbow, monospace outside code. `lint_regions.py` finds most of them.
- **Three ways to fail**: the SLIDE (chrome), the CLINICAL BLOB (identical cold circles, called
  "ugly"), the CRAMPED CIRCUIT (overlap, "goes over each other"). The cure for the last is delete and
  align: fewer elements, a grid, whitespace budgeted first.
- **Panel letters** bold lowercase with no period, top left, on one baseline with a **left-aligned
  title** of at most four words. `main.js` draws both; regions never do.
- **All text black (`PAL.ink`), never gray.** A secondary gloss is a lighter weight; category labels
  may take their category color. The author, of gray glosses: "no small gray font, all black". Small
  step badges (`LIB.badge`) are allowed, sparingly.
- **Every symbol is defined**, in the legend or on the object, and a symbol the reader does not need
  is deleted (section 6 for numbers).
- **One accent, one meaning; structure gray, data color.** At most two dominant accents. Ordinal
  values on a single-hue ramp, categories in distinct hues, the second channel in line style
  (solid observed, dashed predicted or copied).
- **Minimal beats complete**: two to four clean panels; split a figure that is trying to be two. The
  exception is an architecture overview, where the author asked for "more meat": fill the canvas
  around the core mechanism, with three zoom levels for detail.
- **A dataset and its tasks drawn as tables** (an AnnData-style atlas, one small table per prediction
  task): categorical columns are colored icons, numerical columns are tiles on one ramp, each column
  type is its own group with its own ⋯, color marks what the model reads and gray what it does not.
  The grammar and the misreadings it prevents are in `references/table-schematics.md`.

## 4. One canvas, region functions, one library

The whole figure is one `<canvas>`. Each region is a function over one shared library, which is the
single style lever: "if it can't be slidy, the agents can't be slidy." API in `references/library.md`.

- **The region contract**: `drawRegion_<id>(ctx, W, H, R)` draws in local `[0,0]..[W,H]` through
  `PAL`, `FONT`, `LIB`, `SCENE` and its data global only. No hex, no font string, no literal size, no
  transform, no letter or title. Read existing region code before changing it; never guess coordinates.
- **Core** (`core_lib.js`): tokens, three tiers, units (`LIB.mm`, `LIB.pt`), seeded `LIB.rng`, ramps
  (the data figures' blue ramp `#F1F6FF` to `#003FBD`; signed values on blue-white-red `#0A84FF` to
  `#FF3B30` with a near-white plateau from .43 to .57 and values printed, the default; blue-white-orange
  `#2166AC`, `#F7F7F7`, `#D55E00` for a schematic matrix drawn without values or when red already
  means something; never red-green), text with audit boxes, math, arrows,
  elbows, flat frames, badges, heatmaps, strips, color bars, points with halos, legends.
- **Architecture pack** (`references/architecture-pack.md`): blocks, token rows, table cell grids,
  tensor stacks, towers, quadtrees, trees, dashed EMA arrows, stop-gradient marks, braces; semantic
  colors (method, teacher, target) under two themes. `pastel` is the default (ink outlines
  `#333333`, peach `#FBE0C2` method fills, gray `#E8E8EC` teacher fills, red `#D93025` for the loss
  as the one contrast), matched by `tikz-figures`; `three-accent` (`#0B6FB8`, `#0F8C7A`, `#D97A06`)
  is the named alternative, chosen once per paper. An ML architecture figure goes to `tikz-figures` by default (section 0); use this
  pack when the user asks for canvas.
- **Biology pack** (`references/biology-pack.md`): cells with character, white halos, nuclei,
  molecules of radius 3.0, organic dashed masks, cluster masks, ghost cells, color by cluster, one
  shared seeded scene for every panel of the same field.

## 5. Reproduce the reference first

Procedure in `references/reproduce-reference.md`.

1. If the reference came from code, rerun its generator. Otherwise measure it and match the aspect
   ratio within 2 %: `python3 scripts/ref_crops.py ref.png --suggest-width 1830`.
2. Cut one crop per region: `python3 scripts/ref_crops.py ref.png --out ref_crops a=0,0,0.55,0.42 ...`.
3. Set `layout.js` from the crops, uneven widths included; check with `--canvas 1830x<H>`.
4. Reproduce the idioms (a table as color columns, a model as block-arrow-block, losses as small
   matrices in a thin dashed frame). Improve only rendering quality. Deviate only where asked, and log
   each deviation in SPEC.md.
5. With no reference, name the house figures and two published exemplars and show a rendered sketch
   early: the user "is judging a look, not a spec".

For a datasets-used overview of a benchmark (one row per dataset, color for the group only, equal
cells with printed values and opacity for magnitude, every value from the provider's page), start
from `assets/region_example_overview.js`; the rules are in `references/reproduce-reference.md`.

## 6. Real data, real code, honest geometry

Detail in `references/real-data.md`.

- **Data comes in as a JS global**, because `file://` blocks `fetch`: a `_prep/` script writes
  `data/panel_b.js` (`window.PANEL_B = {...};`), loaded by a script tag. About 1,000 points per panel,
  coordinates normalized to [0, 1], one row per file in `PROVENANCE.md`.
- **Generate structures from the method's own code** (partitions, graphs, masks, neighborhoods) with a
  fixed seed: a hero set of about 230 points, a toy set of about 50 where every node must read.
- **Caption and SPEC first; mechanism before polish.** Derive every formula from the code and let a
  blind reader compare the figure with the implementation ("a 1:1 match"). Draw the operation with its
  operands (Q, K and V, the output), never a vague arrow.
- **Exact versus schematic**: measured-looking geometry is measured; illustrative geometry has no exact
  ticks or values and the caption says "schematic". No results in a concept schematic. Where a
  quantity is shown per object, the color encodes exactly the value the text aggregates.

## 7. Build: one builder per region, figure QA with the orchestrator

Brief template and review fan-out in `references/fan-out.md`; spawning mechanics in `agent-orchestration`.

- Write `SPEC.md` (`assets/spec_template.md`): caption, width, theme, rules, a "trap, then correct
  depiction" table, one section per region with its crop and data.
- For four or more regions, one builder per region. Each reads SPEC, the library and its crop, writes
  only its region file, and loops render, look, fix at least three times:
  ```bash
  node render.js "preview.html?region=b&data=panel_b" prev_b_v3 <w+48> <h+48> regions/out --check
  ```
- **Builders never edit the library, the layout or `main.js`.** A missing primitive comes back as a
  request and goes into the library once.
- **Figure-level QA stays with the orchestrator.** Builders see one tile and "will not catch 'the
  whole thing reads like a slide'". With the author, stage sign-off (layout, then density, then
  detail), show the PNG every turn, make the smallest change asked.

## 8. Check before anything is handed over

Full checklist in `references/qc.md`.

1. `python3 scripts/lint_regions.py code/regions/ --layout code/layout.js --main code/main.js`: 0 errors.
2. `node code/render.js figure.html figN 1830 <H> .. --check`: exit 0 (no text under 18 px, no
   overlapping text, no page or region errors, no missing font warning).
3. `python3 scripts/ref_crops.py ref.png --canvas 1830x<H>`: within 2 %, when there is a reference.
4. The PNG is W x 3 by H x 3 px; the PDF is one page of W/10 by H/10 mm.
5. `python3 scripts/check_clearance.py figN.pdf`: 0 fails, every warning read. It measures on ink:
   text on or within 0.25 mm of a graphic, labels closer than 0.35 mm, shapes nearly touching, and the
   white between panels and between table columns and rows. Its two PNGs box each flag.
6. Open the full PNG and every region at 2 to 3 times zoom: anti-slide list, overlaps the script cannot
   see (text under a later shape), one flow, one arrowhead, legends for every meaningful color,
   letters and titles, match with the crops, mechanism against the code. Three rounds that find nothing.
7. Report the paths and sizes, each gate's result, and what was not checked (for example the figure in
   the compiled paper, or the comparison with the code). Rebuild every rendered file after a rename.

## 9. What was thrown out, and what replaced it

| Thrown out | In the author's words | Replaced by |
|---|---|---|
| slide-deck infographics: cards with shadows, pills, numbered badges, gray subtitles, square canvas | "slide-deck infographics", "AI aesthetics" | a library that cannot draw chrome; flat frames; the reference's proportions |
| identical cold circles for cells | "ugly" | cells with character, warm pastels, white halos, natural scatter |
| a hand-laid diagram where boxes collided | "ugly… goes over each other" | a grid-aligned canvas, whitespace first, delete and align |
| a concept schematic drawn in matplotlib | "this is so bad", "drop the schematic" | a canvas schematic, or no schematic |
| 18 px text on a 3200 px canvas | "terrible, tiny text" | the 5 pt floor computed for the canvas, checked by script |
| a figure-wide 12 pt minimum (75 px) | superseded by the 7, 6, 5 pt tiers | three tiers and an 18 px floor at 10 px/mm |
| titles of a set at different sizes | "shorten text, don't change size" | one L1 size, shorter titles |
| two panels scaled independently | "b and c are different font sizes" | draw at print width, include at natural size |
| `#bbb` flow arrows | "too faint at publication scale" | `#999` |
| a reinterpreted reference | "do *that*" | measure, crop, reproduce, then polish |
| a hand-drawn tree; a partition that did not match the code | dismissed as arbitrary | structures generated from the method's code |
| vague arrows standing for a mechanism | "must be OBVIOUS" | the tensor operation with labeled operands |
| a filled algorithm box to fill empty space | banned after being prescribed | less canvas, or more meat in the core panel |
| centered titles over regions; badges inline before titles | superseded by the newest master | bold letter and left-aligned title on one baseline |
| a renderer loading puppeteer from another project's folder | broke on every other machine | `require('puppeteer')` with `package.json` beside it |
| categorical columns as shades of one hue | "it was categorical not numerical, you killed it" | colored icons for categories, tiles for amounts (`references/table-schematics.md`) |
| the icons removed when only their outlines were to go | "you didn't get it ... don't sabotage" | change only what was asked; recover a liked element exactly |
| one ⋯ across columns of different types | "4/5/6 are not same type columns" | one group per type, each with its own ⋯ |
| one key for the whole figure for a color only one task uses | "specific to 6 to all?" | the column header, the icon or the caption |
| panels 1.5 mm apart, judged by eye | "too packed specifically between a and b" | `scripts/check_clearance.py` with a gap asked for in mm |

## Reference files

- `references/print-maths.md`: px, mm and pt; tiers; other canvas widths; line weights; placing the PDF.
- `references/paper-not-slide.md`: the three failures, the anti-slide list, what stays, the declutter standard, taste words.
- `references/library.md`: project layout, the region contract, the core API, packs, preview and master commands.
- `references/architecture-pack.md`: themes and locked semantics, primitives, model-figure recipes.
- `references/biology-pack.md`: cell types, primitives, scene continuity, cluster colors, spacing.
- `references/reproduce-reference.md`: measure, crop, set the layout, reproduce idioms, a datasets-used overview, export parts.
- `references/real-data.md`: data as JS globals, generating structure from code, matching the implementation, exact versus schematic.
- `references/fan-out.md`: before fanning out, the builder brief, orchestrator QA, review fan-out, sweeps.
- `references/qc.md`: scripted gates, the eyes checklist, the report.
- `references/table-schematics.md`: a dataset and its prediction tasks drawn as tables; categorical against numerical, column groups, read against not read, words, misreadings.

Scripts (Python 3.9 or later; `ref_crops.py` needs Pillow) and assets:

- `scripts/print_maths.py`: tiers and floor for any canvas width; converts px to pt.
- `scripts/ref_crops.py`: reference size and aspect ratio, per-region crops, canvas comparison.
- `scripts/lint_regions.py`: region contract and anti-slide lint.
- `scripts/check_clearance.py`: clearance measured on the ink of the printed PDF (needs pymupdf, numpy, scipy, Pillow).
- `assets/render.js` with `assets/package.json`: the renderer (Node 18 or later, puppeteer).
- `assets/core_lib.js`, `assets/pack_arch.js`, `assets/pack_bio.js`: the library and the two packs.
- `assets/layout_template.js`, `assets/main_template.js`, `assets/figure_template.html`,
  `assets/preview_template.html`, `assets/scene_template.js`: the scaffold.
- `assets/region_example_arch.js`, `assets/region_example_bio.js`: worked regions.
- `assets/region_example_overview.js` with `assets/data_example_overview.js`: a datasets-used overview
  and its fictional data global.
- `assets/spec_template.md`: the builder contract.
