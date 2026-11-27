# Geometry: spheres, vectors, densities, fields, zoom

Geometry that a figure claims (a length, a direction, a density, which points are neighbors) is computed, and the
generator checks what the drawing asserts. The source's sphere generator asserts that its parallelogram closes in
the projected plane, that the drawn diagonal has the exact length, and that the projection is radial; a figure that
drew three unit arrows for a sum of unequal sets had to be rebuilt because the drawing asserted a law that is false.

**Contents**
1. The unit sphere of an embedding space
2. The sphere glyph of an overview
3. Resultants and mean directions in the plane
4. Densities as filled bands
5. A density on an axis
6. A vector field
7. A symmetry: a shape and its rotated copy
8. The zoom cascade

## 1. The unit sphere of an embedding space

```bash
python3 scripts/sphere.py --out sphere/ --preamble assets/preamble.tex     # writes sphere.tex, facts.json
pdflatex -output-directory sphere sphere/sphere.tex
```

The generator samples von Mises-Fisher clusters (three groups in the three point hues, subclusters as shades of
their group's hue), draws density rings at cap masses 0.50 and 0.85, and draws the composition of two sets A1 and
A2 at the common scale 1/n_A: the two resultants, the dashed parallelogram, the union's resultant whose length is
exactly the mean resultant length R_A, and the dashed radial projection out to the mean direction. It prints and
stores six checks and exits 1 if one fails.

- **Choose the pair by what the drawing must show.** The gap from the resultant's tip to the surface is 1 - R_A;
  a tight pair (R_A near 0.92) leaves 8 percent of the radius, foreshortened further by the projection. The
  generator selects R_A in [0.62, 0.78] and every drawn direction 37 to 66 degrees off the view axis, so no arrow
  points at the camera and projects short.
- **Labels are placed by score, never by eye**: candidate positions around each anchor, penalized for the points,
  lines and rings they cover, for overlapping a label already set, and for straddling the ball's outline. A label
  inside the ball sits on a white backdrop; one outside does not, so the backdrop never cuts the circle.
- **Name only the resultant on a leader line**, outside the ball; the two partial sums stay unlabeled because the
  parallelogram already shows the addition (naming them would also have to name the drawn scale).

## 2. The sphere glyph of an overview

```bash
python3 scripts/sphere.py --out frag/ --glyph          # frag/sphere_glyph.tex, radius 1.02 cm
```

```latex
% inside an overview:  \begin{scope}[shift={(7.2,9.25)}]\input{frag/sphere_glyph.tex}\end{scope}
```

Its graticule is computed (meridians every 30 degrees, parallels from -60 to 60 degrees, view elevation 15
degrees), clipped to the disk with no outline; three soft blobs of 16 concentric fills mark three directions.

## 3. Resultants and mean directions in the plane

Suggested, not yet tested in real work. The planar version of the sphere's construction, for a method section: unit
vectors of one set, their resultant at scale 1/n (shorter than 1 by exactly 1 - R), and the dashed radial
projection to the mean direction on the circle. The numbers are computed, never placed by eye: for the directions
0, 30, 60, 100 and 140 degrees, R = 0.663 and the mean direction is 64.5 degrees, so on a circle of radius 2 cm the
resultant ends at 1.326 cm (a first draft of this recipe put it at 1.70 by eye; the true value for its five
directions was 1.87).

```latex
\begin{tikzpicture}[paper]
  \draw[black!22, line width=0.45pt] (0,0) circle (2);
  \foreach \a in {0,30,60,100,140} {\draw[black!45, line width=0.45pt] (0,0) -- (\a:2); \fill[ptblue] (\a:2) circle (0.05);}
  % computed: R = |sum of the unit vectors| / 5 = 0.663, direction 64.5 degrees
  \draw[-{Stealth}, line width=1.45pt] (0,0) -- (64.5:1.326);
  \draw[-{Stealth}, line width=0.8pt, dash pattern=on 2.4pt off 1.9pt] (64.5:1.326) -- (64.5:2);
  \fill[ink] (64.5:2) circle (0.072);
  \fill[white] (0,0) circle (0.10); \draw[ink, line width=0.9pt] (0,0) circle (0.088); \fill[ink] (0,0) circle (0.04);
  \node[lbl, anchor=south] at (64.5:2.1) {$\bar\mu$};
  \node[lbl] at (84:1.25) {$R$};   % in the wedge between the resultant and the next direction, clear of both
\end{tikzpicture}
```

## 4. Densities as filled bands

A density is a kernel density estimate per category, drawn as three nested filled bands at relative levels 0.10,
0.36 and 0.66 with opacities 0.22, 0.42 and 0.72, the core last, in the wash tints of the point hues. Flat region
fills read as a "political map" and a blurred mask as "smeared paint"; both were rejected in earlier figures of
the author. `scripts/zoom_cascade.py` emits the bands with contourpy (filled polygons close along a window's edge;
`plot[smooth cycle]` coordinates are separated by spaces, never by `--`).

```latex
\begin{tikzpicture}[paper]
  \draw[crop] (-1,-1) rectangle (1,1);
  \fill[washblue, opacity=0.22] plot[smooth cycle, tension=0.6] coordinates {(-0.7,-0.3) (-0.2,-0.6) (0.3,-0.2) (0.1,0.4) (-0.5,0.3)};
  \fill[washblue, opacity=0.42] plot[smooth cycle, tension=0.6] coordinates {(-0.5,-0.25) (-0.2,-0.42) (0.12,-0.18) (0.0,0.2) (-0.38,0.18)};
  \fill[washblue, opacity=0.72] plot[smooth cycle, tension=0.6] coordinates {(-0.32,-0.2) (-0.15,-0.28) (0.0,-0.12) (-0.1,0.05) (-0.28,0.06)};
  \fill[washochre, opacity=0.22] plot[smooth cycle, tension=0.6] coordinates {(0.2,0.3) (0.7,0.2) (0.8,0.7) (0.4,0.85)};
  \fill[washochre, opacity=0.42] plot[smooth cycle, tension=0.6] coordinates {(0.35,0.4) (0.62,0.35) (0.68,0.65) (0.45,0.72)};
\end{tikzpicture}
```

## 5. A density on an axis

Suggested, not yet tested in real work. A plot drawn at its printed size with the package's axis style; the curve
in the hero color, the shaded interval in its tint, no frame, no legend.

```latex
\begin{tikzpicture}
  \begin{axis}[paperaxis, width=4.6cm, height=2.6cm, xmin=-3.2, xmax=3.2, ymin=0, ymax=0.45,
               xtick={-2,0,2}, ytick={0,0.2,0.4}, xlabel={$x$}, ylabel={density}, samples=120, domain=-3.2:3.2]
    \addplot[draw=none, fill=hero!18, domain=-1:1] {exp(-x^2/2)/sqrt(2*pi)} \closedcycle;
    \addplot[hero] {exp(-x^2/2)/sqrt(2*pi)};
  \end{axis}
\end{tikzpicture}
```

## 6. A vector field

Suggested, not yet tested in real work. Short arrows on a grid in the wire style, length proportional to the
field; the domain framed like a crop.

```latex
\begin{tikzpicture}[paper]
  \draw[crop] (-2,-2) rectangle (2,2);
  \foreach \x in {-1.5,-0.75,...,1.5} {\foreach \y in {-1.5,-0.75,...,1.5} {
    \draw[ink, line width=0.45pt, -{Stealth[length=2.6pt]}] (\x,\y) -- ++({-0.22*\y},{0.22*\x});}}
\end{tikzpicture}
```

## 7. A symmetry: a shape and its rotated copy

Suggested, not yet tested in real work. The same point set twice, the rotation as one curved arrow with its
symbol; equal hues mean equal points.

```latex
\begin{tikzpicture}[paper]
  \foreach \x/\y/\c in {0/0.6/ptblue, -0.5/-0.3/ptochre, 0.5/-0.3/ptpurple} {\fignode{\x,\y}{\c}}
  \draw[graphedge] (0,0.6) -- (-0.5,-0.3) -- (0.5,-0.3) -- cycle;
  \begin{scope}[shift={(3,0)}, rotate=50]
    \foreach \x/\y/\c in {0/0.6/ptblue, -0.5/-0.3/ptochre, 0.5/-0.3/ptpurple} {\fignode{\x,\y}{\c}}
    \draw[graphedge] (0,0.6) -- (-0.5,-0.3) -- (0.5,-0.3) -- cycle;
  \end{scope}
  \draw[flow] (0.9,0.75) to[bend left=30] (2.1,0.75);
  \node[lbl] at (1.5,1.25) {$R_\theta$};
\end{tikzpicture}
```

## 8. The zoom cascade

```bash
python3 scripts/zoom_cascade.py --out cascade/ --preamble assets/preamble.tex            # seeded synthetic field
python3 scripts/zoom_cascade.py --points field.csv --k 6 --radius 0.04 --out cascade/ --preamble assets/preamble.tex --views
```

- **One point field, nested crops.** Every level is a crop of the same field, so the clump marked on one level is
  the clump the next level shows. Never re-sample a level, and never thin the points of a level whose neighbors are
  computed on the full field, or a neighbor appears from nowhere.
- **The window is chosen by a stated rule** (default: the graph window with the highest category entropy among
  those holding at least 40 points), written to `facts.json` with every count.
- **Neighbors are computed on the full field**; edges to nodes outside the last frame run to the frame and stop
  there. The generator clips them itself: ink hidden under a TikZ clip is still in the PDF, and an audit reads it.
- **Fragments name their corners** (`field-box-ne`, `region-nw`, ...), so a figure that places the panels anywhere
  draws its dashed links between named coordinates.
