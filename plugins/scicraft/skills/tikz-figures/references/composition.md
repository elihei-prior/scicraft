# Composition: tiles, rules, titles, letters, print size, placing in a paper

A composed figure puts panels side by side: raster tiles of data with labels and counts, a schematic panel, thin
rules between them, a title over each. The composition is written by a script from the panels' real page sizes,
and the printed size of every type size is computed from the print width before anything is placed.

**Contents**
1. Design width decides type on the page
2. Composing panels with the script
3. A composed row by hand: tiles, labels, counts, rules, titles
4. Raster tiles: twice the size, real counts, scale bars baked in
5. Letters and titles
6. A main figure and its appendix twin
7. Placing a figure in a paper: full width, side by side, wrapped beside its paragraph

## 1. Design width decides type on the page

The source figures were drawn large and printed small: a card figure 850 bp wide set at 0.98 of a 396 bp text
block prints at 0.457, so its 13 pt notes printed at 5.9 pt; the composed Figure 1, 31.6 cm wide, printed at
13.97 cm (0.443), so its 16, 13.5 and 12.5 pt type printed near 7, 6 and 5.5 pt. Every version made before this
rule shipped type at 3.5 pt on the page.

```bash
python3 scripts/print_scale.py --design-width 850 --print-width 0.98x396bp --sizes 14,13.6,13.2,13   # plan
python3 scripts/print_scale.py figure.pdf --print-width 0.98x396bp                                    # check
```

- The floor is 5 pt for any base size; in-cell values of a dense matrix may go to 3.3 pt (`--cell-sizes`).
- When text is too small, give the panel more width; never shrink one label. A label that does not fit is
  shortened or given room.
- Raster text (a scale-bar label baked into a tile) is invisible to the check: `scripts/tiles.py` sizes it from the
  final print scale and reports it. The source's baked labels printed at about 4.5 pt.
- A schematic drawn for half-size printing and placed at full width prints its labels near 13 pt; the check warns
  above 10.5 pt.

## 2. Composing panels with the script

```bash
python3 scripts/compose.py fig.tex panel_a.pdf panel_b.pdf --letters a,b --print-width 0.98x396bp --compile
python3 scripts/compose.py fig.tex a.pdf b.pdf c.pdf --titles "Point field|Training scheme|Embedding map" \
    --rules --print-width 396bp --compile
```

It sets every panel to one height (the first panel's, or `--height`), lays them on one row with a 20 bp gap,
writes the TikZ that includes them, sets the letters or titles in the preamble's type, reports each panel's scale
and its smallest printed base type, and fails when one prints under the floor. Rebuild a panel, rerun the script:
the composition cannot drift from its panels.

## 3. A composed row by hand: tiles, labels, counts, rules, titles

The positions of the source composition (cm): a column 7.85 cm wide holds the whole-view tile (6.90 cm) with its
label 0.45 cm above and its count 0.43 cm below, then two tiles of 3.30 cm with labels above and one caption under
both; rules 0.4 pt `ruleline` between columns; titles 16 pt on one baseline. This recipe stands gray squares in
for the rasters so it compiles alone; `assets/examples/panel_points.tex` is the real column.

```latex
\begin{tikzpicture}[paper]
  \foreach \x/\y/\w in {3.925/11.40/6.90, 2.090/4.35/3.30, 5.760/4.35/3.30}
    {\fill[black!85] ({\x-\w/2},{\y-\w/2}) rectangle ({\x+\w/2},{\y+\w/2});
     \draw[tileframe] ({\x-\w/2},{\y-\w/2}) rectangle ({\x+\w/2},{\y+\w/2});}
  \node[tilelabel] at (3.925,15.30) {whole sample};
  \node[tilecount] at (3.925,7.52) {24{,}000 points};
  \node[tilelabel] at (2.090,6.55) {region};
  \node[tilelabel] at (5.760,6.55) {points};
  \node[tilecount] at (3.925,1.95) {colored by\\category};
  \draw[panelrule] (7.65,1.10) -- (7.65,15.50);
  \paneltitle{0.35,15.75}{a}{Point field}
  \paneltitle{8.20,15.75}{b}{Training scheme}
\end{tikzpicture}
```

- **The count under a tile is the real count of what the tile shows**, read from the records (`tiles/counts.tex`
  holds them as macros); write it with its unit ("24,000 points", "8,550 bins").
- **A caption under tiles says what the color means** ("colored by category"); a color without a key was the
  author's most repeated note on slides and pages ("if you use a color explain what it is").
- **Labels name what the tile is in two to four words**; a size is written with its unit and a thin space
  ("20 $\mu$m bins").

## 4. Raster tiles: twice the size, real counts, scale bars baked in

```bash
python3 scripts/tiles.py --out tiles/ --print-scale 0.443 --label-pt 5.5
```

- **Render at twice the placed size** (`SUP = 2`) and place at that size; quote marker areas in printed pt squared
  and draw them as `area * SUP**2`, or every marker prints at a quarter of its area.
- **A dark ground for data renders** whose colors need it, framed by the 0.4 pt `tileline` hairline; the figure
  page itself stays white ("always do transparent background" for paper figures).
- **One color mapping for every window and every pitch**, anchored at the 5 and 95 percentiles of the whole
  sample, so a zoom reads as a zoom. Refitting the mapping per tile made four nearly identical readouts look
  different; when a figure does refit per tile, its caption says so.
- **Windows are chosen by a stated rule** and a window's box never covers a scale bar or its label.
- **A tile labeled with a bin pitch is pooled at exactly that pitch.** `tiles.py` exits when a pitch is not a whole
  number of raster cells: the example's first raster pooled a tile labeled 20 $\mu$m on bins of 21.3 $\mu$m.
- **A row of pitches shows whole bins of the sample only**: each window is 8 bins of the coarsest pitch wide, on
  that pitch's grid and wholly inside the sample. A window placed by hand showed cut bins along two edges and the
  dark ground in a corner.
- **Scale bars**: a white bar with a dark halo, its right end at 94 percent of the tile width, 5.5 percent above the
  bottom, the label centered over the bar; when a label would run off the tile, it ends where the bar ends (the
  source switched to that when its labels grew, and back when they shrank).

## 5. Letters and titles

- **One letter size per paper, on one baseline.** The package default is an 8 pt bold lowercase letter (a paper may
  choose up to 10.5 pt once for all its figures). The source's Figure 3 letters were 20 bp bold at 17 bp under the
  top and printed at about 8.9 pt; its Figure 1 titles printed near 7.1 pt. Compute yours with `compose.py` and
  keep one size across the paper's figures.
- **Two title styles, one per figure**: a bare bold letter ("a"), or a letter with a parenthesis and a name of two to
  four words ("a)  Point field"). No sentence titles, no gray subtitles.
- **Wipe a letter baked into a reused panel** and set all letters in the composition, so they share size and
  baseline (`references/patching.md`).

## 6. A main figure and its appendix twin

The source split its figures: a main figure carried two panels and the appendix carried the full set (the block
cards moved to the appendix when the main figure became the hierarchy panel beside a readout card). **A fix to
one is a fix to the other, and to both captions.** Keep a map of which file is which twin, and rebuild both from
the same sources.

## 7. Placing a figure in a paper: full width, side by side, wrapped beside its paragraph

Full width at `.98\linewidth` is the default. Two figures side by side in one float each keep their own caption;
the author later preferred a figure wrapped beside the paragraph that discusses it ("I want them left or right of
their corresponding text, whatever the best papers do").

```latex
\documentclass{article}
\usepackage{graphicx,wrapfig,tikz}
\begin{document}
\begin{wrapfigure}{r}{0.45\linewidth}
  \vspace{-1.0\baselineskip}
  \centering
  \begin{tikzpicture}\draw[black!40] (0,0) rectangle (5,3);\end{tikzpicture}
  \caption{A figure beside its paragraph; three lines of caption at most.}
  \vspace{-1.0\baselineskip}
\end{wrapfigure}
The paragraph that discusses the figure. It must be at least as tall as the figure and its caption, or the
indentation leaks into the next heading. Repeat the sentence to fill the wrap. The paragraph that discusses the
figure. The paragraph that discusses the figure. The paragraph that discusses the figure. The paragraph that
discusses the figure. The paragraph that discusses the figure. The paragraph that discusses the figure. The
paragraph that discusses the figure. The paragraph that discusses the figure. The paragraph that discusses the
figure. The paragraph that discusses the figure. The paragraph that discusses the figure.
\end{document}
```

- **A wrapped figure takes 0.43 to 0.46 of the line width** with a baseline skip removed above and below; its
  caption stays at three lines (a fourth line pushed the main text over the page limit in the source).
- **Side by side in one float**: two `minipage`s, each with its own `\caption`, captions of equal length.
- **A figure that will not fit upright** can be set sideways on its own page (`rotating`, `sidewaysfigure`); the
  source computed that its cards printed at 5.5 pt sideways against 3.3 pt upright, and the author chose a
  different layout over the sideways page.
