# The grammar

Every element of the style, the style or macro that draws it, and a compiled recipe of each. All of them are
defined in `assets/preamble.tex`; the values and where they were measured are in `references/style.md`. Recipes
compile behind the preamble (`scripts/compile_snippets.py`); paste one into a figure file that starts with
`\def\figpreambleonly{}` and `\input{preamble.tex}`.

Macros take a coordinate WITHOUT parentheses (`\joincircle{115,-216}` or a named coordinate `\joincircle{j}`);
the macro adds them. Card-family recipes draw in bp (`x=1bp, y=1bp`), overview and composition recipes in cm.

**Contents**
1. The element table
2. Boxes, wires, joins and residuals
3. Tokens: a chip, a row, a K-deep stack, its two braces
4. The card: the name on the border, the mini icon, two-level labels, the legend line
5. Overview shapes: slab, D cap, query, loss, EMA, stop-gradient
6. Crops, masks, points, zoom boxes and links, the point graph
7. Hierarchy pieces: tree nodes and edges, isometric tiles, rails
8. Composition pieces: tile frame, rule, title, letter
9. The unit sphere glyph

## 1. The element table

| Element | Style or macro | Unit |
|---|---|---|
| plain box (one size for all) | `\node[box]` (92 x 28 bp, `boxline` 0.45 pt, corner 1.6 bp) | bp |
| the one operation box of a block | `\node[opbox=oppeach]`, `opmint`, `opgray` (136 x 40 bp) | bp |
| wire with a flat-backed head, bare wire | `\draw[wire]`, `\draw[wirebare]` (0.45 pt) | any |
| residual | `\residual{tap}{side}{join}` or `\draw[resid]` (0.40 pt) | any |
| join circle with a plus, junction dot | `\joincircle{c}`, `\junction{c}` | any |
| token row, K-deep stack | `\tokrow{c}{fill}{n}`, `\tokstack[rows]{c}{fill}` | any |
| width brace, depth (count) brace | `\tokwidthbrace[rows]{c}{label}`, `\tokdepthbrace[rows]{c}{label}` | any |
| card, name on the border | `\card{top-left}{w}{h}{name}` | bp |
| mini icons | `\minipool{c}`, `\minimix{c}`, `\miniread{c}` | any |
| two-level label | `\twolevel{c}{name}{gloss}` | any |
| overview wire, EMA, bare | `\draw[flow]`, `\draw[ema]`, `\draw[flowbare]` (0.7 pt, Stealth) | cm |
| encoder slab with a domed top | `\slab{bottom-left}{width cm}{label}` | cm |
| predictor with a D cap | `\dcap{bottom-left}{width cm}{height cm}{label}` | cm |
| query box, loss box | `\node[qbox]`, `\node[loss]` | cm |
| stop-gradient slashes | `\stopgrad{c}`, `\stopgrad[90]{c}` on a horizontal wire | cm |
| hierarchy rail, "continues below" | `\draw[rail]`, `\draw[railcont]` (0.6 pt) | bp |
| crop frame, mask, zoom box, zoom link | `\draw[crop]`, `\draw[maskbox]`, `\draw[zoombox]`, `\draw[zoomlink]` | cm |
| point, masked point, graph node, graph edge | `\figpoint{c}{color}`, `\figmasked{c}`, `\fignode{c}{color}`, `\draw[graphedge]` | cm |
| tree node, tree edge, selected path | `\node[treenode]`, `\draw[treeedge]`, `\draw[treepath]` | bp |
| isometric tile | `\isotile{center}{half-width bp}{fill}` | any |
| raster tile with its frame | `\tile{x}{y}{width cm}{file}` | cm |
| rule between panels, panel title, bare letter | `\draw[panelrule]`, `\paneltitle{c}{a}{Name}`, `\panelletter{c}{a}` | any |
| unit sphere glyph | `\unitsphere{c}{radius bp}` | any |

## 2. Boxes, wires, joins and residuals

A pre-norm sub-block: the stream enters a LayerNorm, the operation box, then a join; the residual taps the stream
ABOVE the norm (a junction dot), runs out to the margin and enters the join from the side that faces the margin.
The margin lies outside the widest box of the block (here 12 bp left of the operation box), so the bypass never
runs under a box. Arrowheads stop 1 bp short of a box.

```latex
\begin{tikzpicture}[x=1bp, y=1bp, paper]
  \coordinate (in) at (80,0);
  \coordinate (tap) at (80,-16);
  \node[box] (ln) at (80,-48) {LayerNorm};
  \node[opbox=opmint] (att) at (80,-104) {Multi-Head\\Self-Attention};
  \coordinate (j) at (80,-150);
  \coordinate (side) at (0,0);
  \draw[wire] (in) -- ($(ln.north)+(0,1bp)$);
  \draw[wire] (ln.south) -- ($(att.north)+(0,1bp)$);
  \draw[wire] (att.south) -- ($(j)+(0,6.6bp)$);
  \residual{tap}{side}{j}
  \joincircle{j}
  \draw[wire] ($(j)+(0,-5.6bp)$) -- (80,-178);
  \node[note, anchor=base west] at (85,-141.5) {$W_o$};   % midway between the box and the join
\end{tikzpicture}
```

## 3. Tokens: a chip, a row, a K-deep stack, its two braces

A token is a row of cells; a set of K tokens is K rows stacked behind one another, each offset up and right. A row
of n chips would assert a width the figure does not mean, so a set is always a stack. The width is bracketed over
the back row and the count along the stack's own diagonal, both once, on the first glyph of the figure.

```latex
\begin{tikzpicture}[x=1bp, y=1bp, paper]
  \tokrow{0,0}{tokyellow}{4}
  \node[note, anchor=base] at (0,9) {$x_i$};
  \tokstack{70,0}{tokpurple}
  \tokwidthbrace{70,0}{$d$}
  \tokdepthbrace{70,0}{$K$}
  \tokstack{150,0}{tokblue}
  \tokstack{220,0}{tokorange}
  \tokstack[8]{290,0}{tokblue}
  \tokdepthbrace[8]{290,0}{$L$}
\end{tikzpicture}
```

## 4. The card: the name on the border, the mini icon, two-level labels, the legend line

The card's name sits ON its top border; the border is masked by the name's own box, 3 bp to each side. The mini
icon at the top right shows what the block does (pool: children to a parent; mix: a token and its neighborhood to
that token; read: tiles coarse to fine to one point). A label has two levels: a black name over a gray gloss 15 bp
under it.

```latex
\begin{tikzpicture}[x=1bp, y=1bp, paper]
  \card{0,0}{244}{150}{Cross-Attention Pooling}
  \minipool{200,-10}
  \twolevel{61,-44}{queries}{$K$ seed tokens}
  \twolevel{176,-44}{keys, values}{the set's tokens}
  \tokstack{61,-96}{tokpurple}
  \tokstack{176,-96}{tokblue}
  \node[capt, anchor=base west] at (8,-140) {$K$: number of seed tokens};
  \card{258,0}{120}{150}{Mix}
  \minimix{333,-10}
  \card{392,0}{120}{150}{Read}
  \miniread{459,-12}
\end{tikzpicture}
```

## 5. Overview shapes: slab, D cap, query, loss, EMA, stop-gradient

```latex
\begin{tikzpicture}[paper]
  \slab{0,0}{3.0}{context\\encoder}
  \slab{4.6,0}{3.0}{target\\encoder}
  \draw[ema] (3.05,0.41) -- (4.55,0.41);
  \node[lbl] at (3.8,0.83) {EMA};
  \dcap{0.35,1.9}{2.0}{1.06}{predictor}
  \draw[flow] (1.5,1.19) -- (1.5,1.9);
  \node[qbox] (q) at (-1.0,2.43) {query\\$q(A)$};
  \draw[flow] (q.east) -- (0.35,2.43);
  \draw[flow] (2.88,2.43) -- (7.65,2.43);
  \node[lbl, anchor=south] at (5.3,2.5) {$\hat y$};
  \node[loss] at (8.1,2.43) {$\mathcal{L}$};
  % the target leaves the target slab's right side and rises into the loss from below
  \draw[flowbare] (7.6,0.55) -- (8.1,0.55);
  \draw[flow] (8.1,0.55) -- (8.1,2.01);
  \stopgrad{8.1,1.2}
  \node[lbl, anchor=west] at (8.24,1.62) {$y$};
\end{tikzpicture}
```

## 6. Crops, masks, points, zoom boxes and links, the point graph

Real figures take these from `scripts/zoom_cascade.py`; this recipe shows the pieces at hand-placed positions.

```latex
\begin{tikzpicture}[paper]
  \draw[crop] (0,0) rectangle (1.7,1.7);
  \draw[maskbox] (0.2,0.9) rectangle (0.75,1.45);
  \figmasked{0.4,1.2} \figmasked{0.6,1.05}
  \figpoint{1.2,1.3}{ptblue} \figpoint{1.4,0.5}{ptochre} \figpoint{0.5,0.3}{ptpurple}
  \draw[zoombox, rounded corners=1.5pt] (1.0,0.25) rectangle (1.5,0.75);
  \draw[zoomlink] (1.5,0.75) -- (2.4,1.7);
  \draw[zoomlink] (1.5,0.25) -- (2.4,0);
  \draw[crop] (2.4,0) rectangle (4.1,1.7);
  \draw[graphedge] (2.8,0.5) -- (3.3,1.1) -- (3.8,0.6) -- (2.8,0.5);
  \fignode{2.8,0.5}{ptochre} \fignode{3.3,1.1}{ptblue} \fignode{3.8,0.6}{ptpurple}
\end{tikzpicture}
```

## 7. Hierarchy pieces: tree nodes and edges, isometric tiles, rails

Tree edges are Bezier curves from the parent's bottom to the child's top with vertical tangents; the selected path
is drawn last, 1.1 pt black, and its nodes are `tilestrong`. A rail carries a level's output up the right side into
the pooling box between two levels and the pooled tokens out of its left side up into the coarser level; a rail
that comes from a level that is not drawn is dashed (`railcont`). Real trees, pyramids and rails come from
`scripts/hierarchy.py`.

```latex
\begin{tikzpicture}[x=1bp, y=1bp, paper]
  \foreach \x in {20,60,140} {\draw[treeedge] (80,-5.67) .. controls (80,-39) and (\x,-39) .. (\x,-72.33);}
  \draw[treepath] (80,-5.67) .. controls (80,-39) and (100,-39) .. (100,-72.33);
  \node[treenode, fill=tilestrong] at (80,0) {};
  \foreach \x in {20,60,140} {\node[treenode] at (\x,-78) {};}
  \node[treenode, fill=tilestrong] at (100,-78) {};
  \isotile{240,-20}{40}{tilepale}
  \isotile{220,-70}{19}{tilepale}
  \isotile{260,-70}{19}{tilestrong}
  % rails between two levels' rows; the dashed one rises from a level below that is not drawn
  \tokrow{340,0}{tokorange}{5}
  \tokrow{440,-78}{tokblue}{5}
  \node[opbox=oppeach, minimum width=58bp, minimum height=24bp] (pool) at (390,-39) {pool};
  \draw[railbare] (456.4,-78) -- (472,-78) -- (472,-39);
  \draw[rail] (472,-39) -- ($(pool.east)+(1bp,0)$);
  \draw[railbare] (pool.west) -- (310,-39) -- (310,0);
  \draw[rail] (310,0) -- (323.6,0);
  \draw[railcontbare] (400,-104) -- (400,-78);
  \draw[railcont] (400,-78) -- (423.6,-78);
\end{tikzpicture}
```

## 8. Composition pieces: tile frame, rule, title, letter

`\tile` places a raster and draws its hairline frame on the raster's edge. This recipe stands a gray square in for
the raster so it compiles without an image file.

```latex
\begin{tikzpicture}[paper]
  \paneltitle{0,4.3}{a}{Point field}
  \node[tilelabel] at (1.75,3.95) {whole sample};
  \fill[black!80] (0.25,0.7) rectangle (3.25,3.7);
  \draw[tileframe] (0.25,0.7) rectangle (3.25,3.7);
  \node[tilecount] at (1.75,0.35) {24{,}000 points};
  \draw[panelrule] (3.8,0) -- (3.8,4.3);
  \panelletter{4.2,4.0}{b}
\end{tikzpicture}
```

## 9. The unit sphere glyph

The card's output glyph: an outline, an equator, one unit vector's dot. The overview's embedding-space glyph is
generated (`scripts/sphere.py --glyph`).

```latex
\begin{tikzpicture}[x=1bp, y=1bp, paper]
  \unitsphere{0,0}{16}
  \node[note, anchor=west] at (22,0) {$z_i$};
\end{tikzpicture}
```
