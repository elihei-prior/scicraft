# Biology tier: cells, sections, molecules, sequences

The marked biology tier of this skill: glyphs for biological objects drawn in the grammar of the other files, with
hairline outlines, the three point hues for categories and gray glosses. The author's latest paper figures showed
tissue only as data (raster tiles, point fields, crops; `composition.md`, `geometry.md`), so **every recipe in
this file is suggested, not yet tested in real work**. For characterful tissue cartoons on an HTML canvas, use the
sibling `canvas-schematics`.

**Contents**
1. Rules of the tier
2. A cell with its nucleus and molecules
3. Observed and predicted outlines
4. A section, a crop and the cells in it
5. A skeletal molecule
6. A protein cartoon
7. An embedding of cells with direct labels
8. A double helix

## 1. Rules of the tier

- **Real images enter as tiles**, framed by the 0.4 pt `tileline` hairline with a baked scale bar (`tiles.py`). A
  glyph is a schematic, and the caption says "schematic".
- **Cells are outlines, never color fills.** The author asked three times for cells drawn as thin boundaries
  without fills ("cells should not be filled with colors ... white thin boundaries"): thin white boundaries over a
  dark render, thin `boxline` boundaries on white, 0.6 pt for a cell (the weight of a crop frame) and 0.45 pt for
  a nucleus. Color goes to the points, which carry the categories.
- **A hue names a kind** in every panel, as a chip color does: the three point hues are categories of points or
  cells, and a figure that uses them for categories uses them for nothing else. Every color has a key.
- **A second outline is a second hue, never a dash**: a dash already means a mask, a continuation or a weight copy
  in this grammar.
- **A glyph that claims a size carries a scale bar**: a black hairline bar with its length in gloss
  (`10 $\mu$m`).
- **One object, every zoom level.** A crop shows exactly what lies in its box on the parent, as in the zoom
  cascade; a zoom whose levels were drawn apart showed neighbors that came from nowhere and was rejected.

## 2. A cell with its nucleus and molecules

Suggested, not yet tested in real work. The molecules are seeded points inside an ellipse that the outline
contains; the count in the gloss is the number drawn.

```latex
\begin{tikzpicture}[paper]
  \draw[boxline, line width=0.6pt] plot[smooth cycle, tension=0.8] coordinates
    {(-1.5,0.1) (-0.8,1.0) (0.5,1.15) (1.45,0.45) (1.25,-0.75) (0.1,-1.15) (-1.1,-0.8)};
  \draw[boxline!70, line width=0.45pt] (-0.15,0.0) ellipse (0.55 and 0.42);
  \pgfmathsetseed{4}
  \foreach \k in {1,...,45} {
    \pgfmathsetmacro{\ang}{360*rnd}
    \pgfmathsetmacro{\rad}{sqrt(rnd)}
    \pgfmathsetmacro{\cat}{rnd}
    \ifdim \cat pt < 0.45pt \def\hue{ptblue}\else\ifdim \cat pt < 0.8pt \def\hue{ptochre}\else\def\hue{ptpurple}\fi\fi
    \figpoint{{1.1*\rad*cos(\ang)},{0.75*\rad*sin(\ang)}}{\hue}}
  \node[lbl, anchor=base west] at (1.75,0.25) {cell};
  \node[note, anchor=base west] at (1.75,-0.25) {45 molecules};
  \draw[black, line width=0.6pt] (-1.2,-1.45) -- (-0.2,-1.45);
  \node[note, anchor=base] at (-0.7,-1.95) {10 $\mu$m};
\end{tikzpicture}
```

## 3. Observed and predicted outlines

Suggested, not yet tested in real work. Black for the observed outline, `ptblue` for the prediction, both solid at
one weight; the legend line names both.

```latex
\begin{tikzpicture}[paper]
  \foreach \x/\y in {0/0, 2.3/0.3, 1.1/-1.9} {
    \draw[black, line width=0.6pt] plot[smooth cycle, tension=0.8] coordinates
      {({\x-0.9},{\y}) ({\x-0.3},{\y+0.75}) ({\x+0.7},{\y+0.6}) ({\x+0.9},{\y-0.2}) ({\x+0.2},{\y-0.8}) ({\x-0.6},{\y-0.6})};
    \draw[ptblue, line width=0.6pt] plot[smooth cycle, tension=0.8] coordinates
      {({\x-0.7},{\y+0.2}) ({\x-0.05},{\y+0.95}) ({\x+0.85},{\y+0.4}) ({\x+0.7},{\y-0.45}) ({\x-0.05},{\y-0.7}) ({\x-0.75},{\y-0.35})};}
  \node[capt, anchor=base west] at (-1.0,-3.35) {black: observed outline\quad \textcolor{ptblue}{blue}: predicted outline};
\end{tikzpicture}
```

## 4. A section, a crop and the cells in it

Suggested, not yet tested in real work. The cells are one list, drawn twice: small on the section, four times
larger in the crop. The crop keeps the cells whose disks lie wholly inside its frame, as `zoom_cascade.py` keeps
its nodes, so no ink hides under a clip.

```latex
\begin{tikzpicture}[paper]
  \newcommand\cells[3]{% x0, y0, scale: every cell of the section, mapped
    \foreach \i in {-5,...,5} \foreach \j in {-5,...,5} {
      \pgfmathsetmacro{\cx}{0.3*\i + 0.035*sin(97*\i + 53*\j)}
      \pgfmathsetmacro{\cy}{0.3*\j + 0.035*cos(71*\i + 29*\j)}
      \pgfmathsetmacro{\keep}{veclen(\cx,\cy) < 1.35 ? 1 : 0}
      \pgfmathsetmacro{\inbox}{(abs(\cx-0.45) < 0.3-0.11 && abs(\cy-0.45) < 0.3-0.11) ? 1 : 0}
      \ifdim #3pt > 1pt \pgfmathsetmacro{\keep}{\keep*\inbox}\fi
      \ifdim \keep pt > 0.5pt
        \draw[boxline, line width=0.45pt] ({#1+#3*\cx},{#2+#3*\cy}) circle ({#3*0.1});
        \draw[boxline!70, line width=0.35pt] ({#1+#3*\cx},{#2+#3*\cy}) circle ({#3*0.045});
      \fi}}
  \draw[cardline, line width=0.6pt] plot[smooth cycle, tension=0.8] coordinates
    {(-1.7,0.2) (-1.1,1.4) (0.3,1.65) (1.6,0.95) (1.75,-0.6) (0.6,-1.6) (-1.0,-1.45)};
  \cells{0}{0}{1}
  \draw[zoombox] (0.15,0.15) rectangle (0.75,0.75);
  \draw[crop] (2.6,-1.2) rectangle (5.0,1.2);
  \cells{2.0}{-1.8}{4}
  \draw[zoomlink] (0.75,0.75) -- (2.6,1.2);
  \draw[zoomlink] (0.75,0.15) -- (2.6,-1.2);
  \node[lbl, anchor=base] at (0,-2.2) {section};
  \node[lbl, anchor=base] at (3.8,-2.2) {cells};
\end{tikzpicture}
```

The crop maps the box (center 0.45, 0.45; half-width 0.3) onto the frame (center 3.8, 0; half-width 1.2): scale 4,
offset (3.8 - 4 x 0.45, 0 - 4 x 0.45) = (2.0, -1.8). Compute the offset; a crop placed by eye shows another place.

## 5. A skeletal molecule

Suggested, not yet tested in real work. Carbons are unlabeled vertices; only other atoms carry a letter, set in
the label size with the bond stopping short of it.

```latex
\begin{tikzpicture}[paper]
  \foreach \i in {0,...,5} \coordinate (a\i) at (\i*60+30:0.9);
  \coordinate (ctr) at (0,0);
  \draw[boxline, line width=0.7pt] (a0) -- (a1) -- (a2) -- (a3) -- (a4) -- (a5) -- cycle;
  \foreach \i/\j in {0/1, 2/3, 4/5}
    \draw[boxline, line width=0.7pt] ($($(a\i)!0.15!(a\j)$)!0.17!(ctr)$) -- ($($(a\j)!0.15!(a\i)$)!0.17!(ctr)$);
  \draw[boxline, line width=0.7pt] (a0) -- ++(30:0.72) node[lbl, anchor=west, inner sep=2pt] {OH};
  \draw[boxline, line width=0.7pt] (a3) -- ++(210:0.72) node[lbl, anchor=east, inner sep=2pt] {N};
  \draw[boxline, line width=0.7pt] (a5) -- ++(330:0.72) node[lbl, anchor=north west, inner sep=2pt] {Cl};
\end{tikzpicture}
```

## 6. A protein cartoon

Suggested, not yet tested in real work. A helix as a coil, a strand as a broad arrow, a loop as a curve, residues
as points; each part named in gloss under it.

```latex
\begin{tikzpicture}[paper]
  \draw[boxline, line width=0.6pt, domain=0:2160, samples=240, variable=\t]
    plot ({\t/360*0.32 + 0.14*sin(\t)}, {0.28*cos(\t)});
  \draw[boxline, line width=0.6pt, fill=washochre]
    (2.3,-0.12) -- (3.4,-0.12) -- (3.4,-0.3) -- (3.9,0) -- (3.4,0.3) -- (3.4,0.12) -- (2.3,0.12) -- cycle;
  \draw[boxline, line width=0.6pt] (1.92,0.28) to[out=0, in=180] (2.3,0);
  \draw[boxline, line width=0.6pt] (3.9,0) to[out=0, in=200] (5.1,0.45);
  \foreach \x/\y in {5.25/0.52, 5.55/0.6, 5.85/0.56} {\fignode{\x,\y}{ptblue}}
  \node[note, anchor=base] at (1.0,-0.9) {helix};
  \node[note, anchor=base] at (3.1,-0.9) {strand};
  \node[note, anchor=base] at (4.6,-0.9) {loop};
  \node[note, anchor=base west] at (6.1,0.47) {residues};
\end{tikzpicture}
```

## 7. An embedding of cells with direct labels

Suggested, not yet tested in real work. Seeded clusters in the three point hues, a label beside each cluster and no
legend, two short arrows for the axes of the embedding.

```latex
\begin{tikzpicture}[paper]
  \pgfmathsetseed{11}
  \foreach \cx/\cy/\hue in {0/0/ptblue, 2.4/0.7/ptochre, 1.2/-1.7/ptpurple} {
    \foreach \k in {1,...,60} {
      \pgfmathsetmacro{\ang}{360*rnd}
      \pgfmathsetmacro{\rad}{0.7*sqrt(rnd)}
      \figpoint{{\cx+\rad*cos(\ang)},{\cy+0.8*\rad*sin(\ang)}}{\hue}}}
  \node[lbl, anchor=east] at (-0.85,0) {type A};
  \node[lbl, anchor=west] at (3.25,0.7) {type B};
  \node[lbl, anchor=west] at (2.05,-1.7) {type C};
  \draw[flow] (-1.6,-2.8) -- (-0.7,-2.8);
  \draw[flow] (-1.6,-2.8) -- (-1.6,-1.9);
  \node[note, anchor=north west] at (-1.6,-2.9) {UMAP 1};
  \node[note, anchor=base west, rotate=90] at (-1.75,-2.8) {UMAP 2};
\end{tikzpicture}
```

## 8. A double helix

Suggested, not yet tested in real work. Two strands half a turn apart, rungs as hairlines between them.

```latex
\begin{tikzpicture}[paper]
  \foreach \x in {0.3,0.7,...,3.9}
    \draw[black!30, line width=0.4pt] (\x,{0.4*sin(deg(3*\x))}) -- (\x,{0.4*sin(deg(3*\x)+180)});
  \draw[boxline, line width=0.7pt, domain=0:4, samples=120, smooth] plot (\x, {0.4*sin(deg(3*\x))});
  \draw[ptblue, line width=0.7pt, domain=0:4, samples=120, smooth] plot (\x, {0.4*sin(deg(3*\x)+180)});
\end{tikzpicture}
```
