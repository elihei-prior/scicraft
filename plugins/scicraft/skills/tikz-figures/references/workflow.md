# Workflow and failure catalog

The process that turns a request into a figure the author would put in a paper, and the failures that compile
cleanly and still look or read wrong. The recipes live in the other references; this file owns the loop, the gates
and the catalog. The loop's shape (a static check before compiling, render and look, an exact-versus-schematic
decision, a bounded repair loop) uses ideas credited in `THIRD_PARTY.md`; the numbers and the failures come from
the author's figure work.

**Contents**
1. The loop
2. Before drawing: exact or schematic
3. Mimic mode: reproduce a reference first
4. Check the drawing against the code
5. One change at a time, staged sign-off, the PNG every turn
6. The bounded repair loop
7. When the style keeps failing: copy one named exemplar
8. The last look, as a fresh reader
9. What each script catches
10. The catalog: compiles, and is still wrong
11. A minimal TeX tree
12. Delivering

## 1. The loop

```
request -> exact or schematic -> sketch on a grid -> draft -> safety check -> compile -> PNG -> LOOK
        -> audit -> print scale -> repair the smallest defect -> render again
```

```bash
python3 scripts/render_figure.py fig.tex --texinputs <skill>/assets      # fig_v01-1.png, then fig_v02-1.png
python3 scripts/audit_layout.py fig.pdf                                    # 0 findings, or named residues
python3 scripts/print_scale.py fig.pdf --print-width 0.98x396bp            # no base type under 5 pt
```

`render_figure.py` runs the safety check, compiles with `pdflatex -halt-on-error`, fails on a log with errors,
overfull boxes or missing characters, writes the PNG under a new version number and fails on a blank page.
Versioned names matter: a cached viewer once showed an old PNG, and a fix was reported that had not landed.

A figure file during work reads the preamble from the skill and its generated parts from files:

```latex
\def\figpreambleonly{}
\input{preamble.tex}
\begin{document}
\begin{tikzpicture}[x=1bp, y=1bp, paper]
  \node[box] (a) at (0,0) {LayerNorm};
  \node[opbox=oppeach] (b) at (0,-60) {Cross-Attention};
  \draw[wire] (a.south) -- ([yshift=1bp]b.north);
\end{tikzpicture}
\end{document}
```

Then open the PNG and look, in this order: text over text or over a wire; a label or an arrowhead cut at the page
edge; a wire that stops short of its box or runs into it; crowding; a hue that is not a role color; type smaller
than its neighbors; a symbol defined nowhere; a line that holds a single word.

## 2. Before drawing: exact or schematic

Visual plausibility is not correctness. Decide first, for every curve, distribution, threshold, length, tree,
partition or neighborhood in the figure, whether it is **exact** (computed from stated equations, data or the
method's code) or **schematic** (a qualitative sketch).

| | Exact | Schematic |
|---|---|---|
| geometry | computed by the code or plotted from the data file, with a seed | hand-placed, plainly qualitative |
| ticks and numbers | real values, copied from `facts.json` or the records | none that look measured |
| lengths, angles, brackets | measure the real object | none |
| a density drawn as exact | integrates to 1 | no such claim |
| caption | names the source | says "schematic" |

If the math cannot be specified or the code cannot run, the figure is schematic, and it shows no precise-looking
geometry. A hand-drawn tree was called "some random tree", and a uniform grid drawn as an adaptive partition
misstated the method (`generators.md`).

## 3. Mimic mode: reproduce a reference first

When the user shows a figure to match (a screenshot, a page of a paper, an earlier version of theirs):

1. **List every visual element before writing code**: each shape with its fill and outline, each arrow style, each
   label word for word, the arrangement and the spacing. A guess from a caption is a fallback and is named as one.
2. **Measure the reference.** Its aspect ratio (match within about 2 percent), and, when it is a PDF, its fills,
   strokes and type sizes with PyMuPDF (`style.md`, section 1, shows how).
3. **Reproduce it first, polish second.** Keep its arrangement and its idioms, and deviate only where asked.
4. **Put the two renders side by side** at the same height, and compare weights, colors, spacing and type until a
   reader would take them for the same paper.

## 4. Check the drawing against the code

A block diagram is a claim about the code. The source cards had several mechanisms wrong until each was checked
file by file against the module that computes it, and the table keeps what the first draft got wrong.

| Check | Rule | What the first draft got wrong |
|---|---|---|
| how many norms, and where | self-attention shares one norm for queries, keys and values; cross-attention normalizes its two streams apart | one norm on the cross-attention block, and the self-attention block labeled cross-attention |
| which stream the residual taps | the query stream, before its norm (pre-norm) | both input streams merged into one norm and one bypass |
| where a position encoding acts | on the stream and the box where the code applies it, read from the code | not recorded |
| how an addend enters | anything the code adds to the tokens is a join, with the small block that embeds it | a count written as a trailing sentence |
| what a set is | K vectors are a stack of K rows | a row of n chips, which asserts a width the figure does not mean |
| what exists | draw only modules the configuration uses | register tokens drawn that the configuration did not use |
| names | as a reader meets them in the paper; the paper's notation for symbols | code names on the cards |

When the paper's wording and the code disagree (a graph rule named one way in the text and configured another
way), draw the paper's wording and report the disagreement to the author instead of choosing one.

## 5. One change at a time, staged sign-off, the PNG every turn

- **The smallest change asked.** Change what was asked and nothing else; do not improve several things at once.
- **Staged sign-off**: layout first, then density, then the zooms; one panel at a time, each signed off before the
  next.
- **Show the PNG every turn** (or the changed page of the paper). The author judges a figure by looking at it and
  cannot judge a description.
- **Keep the author's drawing.** A pass that rewrote a panel in words and moved its encoders was rejected ("super
  ugly encoders, do not drift from the previous version so much") and rolled back (`patching.md`).
- **Decide the font once.** Every label is audited again after any font change: a font change moves every width.
- **A main figure has an appendix twin.** A fix to one is a fix to the other and to both captions.

## 6. The bounded repair loop

On a compile error or a visual defect:

1. Read the exact error, or name the specific defect ("the tap label touches the wire at (120, 154)").
2. Find the smallest region of the source responsible for it.
3. Change only that region.
4. Run the check that failed again.
5. Continue from the current source; never rewrite the whole figure to fix one defect.

**Two strikes.** If the same kind of failure survives two focused repairs, step back: simplify the figure or split
it into two. A figure that tries to be two figures (an architecture and a result) is split.

## 7. When the style keeps failing: copy one named exemplar

A schematic that stays ugly over several rounds is rarely fixed by another rule. The move that worked, after about
three weeks of rejected schematics in the author's earlier project, was to stop and copy ONE named exemplar the
author approved (a panel the author drew, or a named figure of a named paper) in its layout and idioms, then
change content only. In this skill the exemplars are the seven examples that `scripts/build_examples.py` builds
from `assets/examples/` and the generators (`SKILL.md`, section 11).

The causes the author named in those weeks are the failures to avoid from the start: a look like a web page or a
plotting library, too much text, overlaps, an unfaithful algorithm (a quadtree that was not one), domain words in a
general figure, panel letters nobody asked for, content dropped while decluttering, and changes too small to see
between rounds.

## 8. The last look, as a fresh reader

After the last edit, look at every PNG again as a reader who did not make it, and who hunts:

- overlaps and clipped text, at 100 percent and zoomed in on every dense spot;
- crowding, and a quarter of the area left empty (an appendix figure that left a quarter empty was sent back);
- a stray hue, a chip color that means two kinds of token, a color without a key;
- type under the floor (`print_scale.py`), and text set smaller than its neighbors;
- text off the center line of its row, row labels that do not start at the panel's left edge, panel bottoms that
  are not level (the author checks these at the pixel);
- a line with a single word, a sentence used as a title, a gray subtitle, a dagger, bold used to mark significance;
- a symbol, a number or a word in the figure that the caption or the paper does not define.

When a second agent is available, give it the PNG and the caption and nothing else, and loop until it finds no
discrepancy.

## 9. What each script catches

| Script | Catches | Misses |
|---|---|---|
| `check_tikz_safety.py` | a body without the preamble, unbalanced environments or braces, edge labels without a position, `--` inside a smooth plot, `\newpage` in a standalone file, a loop variable that shadows a TeX macro, an unbraced macro as a loop body, a sans font package; warns on unseeded `rand`, a frame deck without a locked box, T1 encoding, a long label without a width | everything visual |
| `render_figure.py` | compile errors, overfull boxes, missing characters, a blank page, frame decks of unequal size | everything visual |
| `audit_layout.py` | text over text, a stroke through text, text off the page, doubled ink, crossings, stubs | a wrong mechanism, a stray hue, crowding that does not overlap, text hidden under paint |
| `print_scale.py` | printed type under the floor, a figure drawn for half size and placed at full width | text baked into a raster |
| the generators' checks | geometry that does not add up (`facts.json` records each check) | a showcase choice that is an artifact of the seed |
| looking | all of the above, and whether the figure says the right thing | nothing, when done as section 8 says |

## 10. The catalog: compiles, and is still wrong

| What you see | Why | Fix |
|---|---|---|
| an empty 12 x 12 pt PDF | a body compiled without the preamble | compile preamble plus body as one file |
| a label sitting on its arrow | `\draw (a) -- node {x} (b)` places the node on the path | `node[midway, above]`, or a separate node 4 bp beside the wire |
| a label or arrowhead cut at the edge | the standalone crop follows the ink | a larger `border`, or move the element in |
| "Cannot parse this coordinate" from a macro | the preamble's macros take bare coordinates, `\tokrow{0,5}{...}` | drop the parentheses |
| a style that silently does something else | a style named like a TikZ key (`name`, `label`, `edge`, `cap`) | the preamble uses `capt`, `lbl`, `graphedge` |
| a figure that moves on every compile | `rand` reseeds each run | `\pgfmathsetseed{N}`, or points from Python with a seed |
| "Cannot parse this coordinate" in a plot | `plot[smooth cycle] coordinates` with `--` between points | separate the points by spaces |
| "Unknown operator 'a'" | `\pgfmathsetmacro` concatenated numbers in `ellipse (rx and ry)` | compute in Python and emit numbers |
| frames that jitter | each frame cropped to its own ink | the same `use as bounding box` in every frame |
| a loop that breaks on `\c`, `\d`, `\o`, `\fi` | the variable shadows an accent, a letter or a primitive | `\x \y \k \n \ff` |
| a label darker than its neighbors, reported as text over text | an unbraced macro as the body of a `\foreach`: the loop reads to the next semicolon, so the command after the macro runs once per item | brace the body, `{\fignode{\x,\y}{ptblue}}`; the safety check reports it |
| type at 3.5 pt on the page | design width never compared with print width | `print_scale.py` before drawing (`composition.md`) |
| bitmap-looking type | T1 font encoding without its scalable fonts | leave the default encoding, as the preamble does |
| uppercase Greek printed as empty boxes, nothing in the log | a sans math package | the default math; the style has no sans option |
| a wiped label still found by search | paint hides text from the eye, not from the text layer | crop the source PDF or redraw (`patching.md`) |
| a panel drawn under a crop frame disappears | the frame style is filled white | draw that frame with `fill=none`, or draw it first |
| graph edges beyond a clip found by the audit | a TikZ clip hides segments, the PDF keeps them | clip in the generator (`generators.md`) |
| a residual that joins a wire 0.4 bp above the next arrowhead | the tap was placed by eye | put the tap in the middle of the gap between two blocks |
| hairline gaps where wires meet frames | wire ends typed by hand 0.01 to 0.03 cm off the frame | start wires on the frame's named coordinate |
| a white label backdrop that cuts a circle | the label straddles the outline | place labels fully inside or fully outside (`geometry.md`) |
| a corner label that overflows its box | its width was guessed in another font | measure it from the compiled PDF |
| a baked scale-bar label running off a small tile | the label centered over a bar near the edge | right-align it to the bar's end (`tiles.py` does) |
| a zoom box over a scale bar | the window chosen without the bar's corner | exclude the corner and a margin from the window rule |
| an auditor reporting 0 crossings where there are some | it excused every crossing inside any rounded box, the card frame included | excuse only small shapes and join circles |
| axis lines with arrowheads | the PGFPlots default for `axis lines=left` | `paperaxis` turns them off |
| "Undefined control sequence" at `\end{axis}` | a `\foreach` inside an axis: PGFPlots runs the body later, when `\x` is gone | `\pgfplotsinvokeforeach{1,2,3}{... #1 ...}`, or explicit nodes |
| a bracket in an axis at the wrong length | relative coordinates inside an axis are axis units | absolute axis coordinates for both ends |
| a heat matrix colored by row index | `matrix plot` without `point meta=explicit` | give the meta column explicitly |
| white numbers lost on pale cells | one text color for every cell | split the text color by the cell's rank |
| a doubled stroke where two boxes meet | two outlines drawn on one line | draw shared edges once |
| a generated body that ignores regeneration | it was appended once with `cat >>` | `\input` while iterating, inline at delivery |
| four nearly equal readouts that look different | the color mapping refit per tile | one mapping for every tile, or say so in the caption |
| a caption a line too long | a fourth caption line in a wrapped figure pushed the text over the page | three lines; cut words |
| a color nobody can read | no key, no caption line | "if you use a color explain what it is" |
| a label true in one frame shown in all | the label was drawn outside the frame logic | draw it only in the frames where it holds (`animation.md`) |

## 11. A minimal TeX tree

The preamble needs `standalone`, TikZ with `arrows.meta`, `decorations.pathreplacing` and `calc`, `pgfplots` with
`fillbetween`, `fix-cm`, `amsmath`, `amssymb` and `graphicx`. A full TeX Live has all of them. On a basic tree
(the BasicTeX scheme of TeX Live 2025, where this skill was built) `standalone` and `pgfplots` were missing:

```bash
kpsewhich standalone.cls pgfplots.sty fix-cm.sty     # an empty line is a missing file
kpsewhich -var-value TEXMFHOME                        # the user tree, where a missing package can be unpacked
```

Install a missing package with `tlmgr`, or unpack it into the user tree and run `mktexlsr` when `tlmgr` cannot
write. Neither was run in this build: both packages were already in the user tree.

`fix-cm` ships with LaTeX itself. The type is Computer Modern, which every tree has, so no font package is needed.
`preview.sty` was absent and the standalone class compiled without it. A failure from a missing file is not a
recipe bug and not a broken preamble.

## 12. Delivering

A figure is done when:

- the safety check passes and the log has zero errors, overfull boxes and missing characters;
- the PNG is not blank and has been looked at, by you and then as section 8 says;
- the audit reads 0, or every finding is a named residue with its reason;
- no base type prints under 5 pt at the figure's print width;
- every quantitative element is marked exact or schematic, and every number shown matches `facts.json`;
- generated geometry came from the method's code or the data with a fixed seed;
- the delivered file is self-contained (`render_figure.py --inline`) and compiled alone in an empty folder;
- the `.tex` and `.pdf` are handed back (the PNG is a preview), with one line on what was not checked.

Record the outcome of the design pass in one word: keep, simplify, split or redo.
