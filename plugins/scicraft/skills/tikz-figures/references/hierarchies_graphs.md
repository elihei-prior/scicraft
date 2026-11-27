# Hierarchies, trees, graphs and partitions

A hierarchy panel puts three views of one multiscale structure on the same rows: the tree, an isometric pyramid of
tile grids, and the rows of tokens that the model computes per level, with the point graph at the bottom. Every
structural element comes from real code on a seeded input: a hand-drawn tree was called "some random tree", and a
uniform grid drawn as an adaptive partition misstated the method.

**Contents**
1. The generated hierarchy panel
2. What the panel must agree on
3. A tree with its selected path
4. A pyramid level by hand
5. A partition seen from above
6. One point and its k nearest neighbors
7. Message passing as a join
8. Plate notation and a Markov chain

## 1. The generated hierarchy panel

```bash
python3 scripts/hierarchy.py --out h/ --n 300 --capacity 6 --depth 6 --levels 4 --k 2 --seed 5
pdflatex h/hierarchy.tex          # assets/preamble.tex is read by the script; no \input needed
```

It builds a quadtree over seeded points spread evenly over the field (a tile splits while it holds more than
`--capacity` points), selects one point by a stated rule (the point nearest the center of the field), and draws:
the tree of the selected node's occupied children per level, the pyramid of every tile per level (the selected
tile strong, its siblings pale, the single top tile pale), the rows of tokens through a self-attention block and
pooling blocks with feedback rails, dashed rails and vertical dots for the levels not drawn, and the
k-nearest-neighbor graph of the points in the pyramid's isometric frame. `facts.json` records the counts, the path
and the rule. Replace the example quadtree with an import of your own partition code; keep the drawing.

The points are stratified (one per cell of a grid, jittered), 300 of them with two neighbors each, as the source's
graph was: uniform random points clump, and their graph blots under the pyramid instead of reading as a sheet.

## 2. What the panel must agree on

- **The tree, the pyramid and the rows share their rows.** Each tree level, each pyramid level and each level's row
  of tokens sit on one center line (78 bp apart in the source), so a reader reads a level across the panel.
- **The selected path is one color everywhere**: the tree's selected nodes, the pyramid's selected tiles and the
  leaf chips are `tilestrong` (the same yellow).
- **Data flow runs the way the code computes it.** In the source the hierarchy was built from the points up: the
  leaf tokens pool into the finest level, each level's output pools into the next coarser level. A rail leaves a
  level's output on the right, rises to the pooling block between the two levels, and the pooled tokens leave the
  block on the left and rise into the coarser level's input.
- **Levels that are not drawn are bridged, not hidden**: the rails into and out of the gap are dashed, and vertical
  dots stand under the tree and the pyramid.
- **Symbols per row**: each level's output tokens carry the paper's symbol above them ($X^{(\ell)}$ here); the
  tokens a block consumes carry none. The source tried column headers first and moved the symbols onto the rows.

## 3. A tree with its selected path

Edges are Bezier curves with vertical tangents from the parent's bottom to the child's top, 0.5 pt `treeedge`; the
selected path is drawn after them, 1.1 pt black. Nodes are 11.34 bp, 9.07 bp at the finest drawn level.

```latex
\begin{tikzpicture}[x=1bp, y=1bp, paper]
  \def\pr{5.67}
  \foreach \x in {20,60,140} {\draw[treeedge] (80,-\pr) .. controls (80,-39) and (\x,-39) .. (\x,-78+\pr);}
  \foreach \x in {75,90,120} {\draw[treeedge] (100,-78-\pr) .. controls (100,-117) and (\x,-117) .. (\x,-156+4.54);}
  \draw[treepath] (80,-\pr) .. controls (80,-39) and (100,-39) .. (100,-78+\pr);
  \draw[treepath] (100,-78-\pr) .. controls (100,-117) and (105,-117) .. (105,-156+4.54);
  \node[treenode, fill=tilestrong] at (80,0) {};
  \foreach \x in {20,60,140} {\node[treenode] at (\x,-78) {};}
  \node[treenode, fill=tilestrong] at (100,-78) {};
  \foreach \x in {75,90,120} {\node[treenode, minimum size=9.07bp] at (\x,-156) {};}
  \node[treenode, fill=tilestrong, minimum size=9.07bp] at (105,-156) {};
  \foreach \k in {0,5,10} {\fill[ink] (105,-176-\k) circle (0.8bp);}
\end{tikzpicture}
```

## 4. A pyramid level by hand

A level of the pyramid is a grid of isometric diamonds (2:1), separated by a hairline of white. The top tile is
137.44 x 68.72 bp; each level halves the tile.

```latex
\begin{tikzpicture}[x=1bp, y=1bp, paper]
  \isotile{0,0}{68.72}{tilepale}
  \foreach \i/\j/\f in {0/0/tilepale, 1/0/tilestrong, 0/1/tilepale, 1/1/tilepale} {
    \isotile{{(\i-\j)*34.36}, {-80+(1-\i-\j)*17.18-17.18}}{33.4}{\f}}
\end{tikzpicture}
```

## 5. A partition seen from above

Suggested, not yet tested in real work. The same quadtree flat: leaf cells as hairline squares, the selected
point's cell strong, its siblings pale. Generate the cells from the partition code (`scripts/hierarchy.py` holds a
working quadtree to start from).

```latex
\begin{tikzpicture}[x=1bp, y=1bp, paper]
  % audit-accept: CROSS at (  # the grid lines of a partition cross by construction; there is no wiring here
  % fills first, then every edge once (a cell outline drawn over the grid doubles the ink)
  \fill[tilepale] (64,64) rectangle (128,128);
  \fill[tilestrong] (96,64) rectangle (128,96);
  \draw[isotile] (0,0) rectangle (128,128) (64,0) -- (64,128) (0,64) -- (128,64)
                 (96,64) -- (96,128) (64,96) -- (128,96);
  \foreach \x/\y in {20/30, 40/90, 70/20, 101/80, 110/72, 75/110, 118/115, 30/50, 90/40} {\fill[ink] (\x,\y) circle (1.3bp);}
\end{tikzpicture}
```

## 6. One point and its k nearest neighbors

Suggested, not yet tested in real work in this style; the selection rule comes from earlier zoom figures of the
same author. Pick the center point by a rule (a neighbor radius near the 45th percentile of all points', and no
angular gap between its neighbors over 2.4 rad, so it is surrounded), compute the neighbors on the FULL field, draw
thin spokes and one light ring, and set the label without a leader line in the widest gap between spokes.
`scripts/zoom_cascade.py` computes neighbors this way for its graph level.

The ring is drawn large enough for the label: at 13 pt a symbol needs a gap about 0.8 cm wide, so the ring's
radius is 0.93 cm here. A label squeezed into a smaller ring touches the spokes on both sides.

```latex
\begin{tikzpicture}[paper]
  \draw[crop] (-1.5,-1.5) rectangle (1.5,1.5);
  \draw[black!22, line width=0.6pt] (0,0) circle (0.93);
  \foreach \x/\y/\c in {0.68/0.30/ptblue, -0.45/0.72/ptochre, -0.78/-0.27/ptblue, 0.15/-0.87/ptpurple, 0.75/-0.53/ptblue, -0.08/0.83/ptpurple}
    {\draw[graphedge, draw=ink, line width=0.45pt] (0,0) -- (\x,\y); \fignode{\x,\y}{\c}}
  \foreach \x/\y in {1.2/1.05, -1.2/1.12, 1.12/-1.2, -1.05/-1.12, 1.28/0.08} {\figpoint{\x,\y}{black!45}}
  \fill[ptblue] (0,0) circle (0.07);
  \node[lbl] at (240:0.61) {$z_u$};   % the middle of the widest gap between spokes (199 to 280 degrees), no leader
\end{tikzpicture}
```

## 7. Message passing as a join

Suggested, not yet tested in real work. The neighbors' messages enter the graph layer (`opgray`), its output and
the node's own token meet in a join, the node leaves updated. Each addend enters the join from its own side.

```latex
\begin{tikzpicture}[x=1bp, y=1bp, paper]
  \foreach \y in {30,0,-30} {\tokrow{0,\y}{tokblue}{4} \draw[wirebare] (10.6,\y) -- (30,\y);}
  \draw[wirebare] (30,30) -- (30,-30);
  \draw[wire] (30,0) -- (53,0);
  \node[note, anchor=base] at (0,40) {neighbors};
  \node[opbox=opgray, minimum width=92bp] at (100,0) {graph layer};
  \draw[wire] (146,0) -- (178.4,0);
  \joincircle{184,0}
  \tokrow{184,-48}{tokorange}{4}
  \node[note, anchor=base west] at (196,-52) {$h_i$};
  \draw[wire] (184,-45.8) -- (184,-6.6);
  \draw[wire] (189.6,0) -- (220,0);
  \tokrow{233,0}{tokblue}{4}
  \node[note, anchor=base] at (233,8) {$h_i'$};
\end{tikzpicture}
```

## 8. Plate notation and a Markov chain

Suggested, not yet tested in real work. Variables are circles at the tree node's size and weight (observed ones
filled pale); a plate is a hairline rounded rectangle with its count in the corner; edges are wires.

```latex
\begin{tikzpicture}[x=1bp, y=1bp, paper]
  \node[treenode, minimum size=22bp] (t) at (0,0) {$\theta$};
  \coordinate (z) at (60,0); \coordinate (x) at (120,0);
  \draw[card, fill=white] (38,-24) rectangle (146,26);   % the plate is a region: filled and drawn first
  \node[note, anchor=south east] at (144,-22) {$N$};
  \node[treenode, minimum size=22bp] at (60,0) {$z_i$};
  \node[treenode, minimum size=22bp, fill=tilepale] at (120,0) {$x_i$};
  \draw[wire] (t) -- ($(z)+(-11bp,0)$);
  \draw[wire] ($(z)+(11bp,0)$) -- ($(x)+(-11bp,0)$);
  \foreach \i/\x in {0/200, 1/250, 2/300} {\node[treenode, minimum size=22bp] (s\i) at (\x,0) {$s_\i$};}
  \draw[wire] (s0) -- (s1);
  \draw[wire] (s1) -- (s2);
  \draw[wire] (s2.east) -- (330,0);
\end{tikzpicture}
```
