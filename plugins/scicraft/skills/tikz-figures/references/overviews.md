# Overviews and pipelines

An overview shows how the parts of a method connect: inputs as crops of one field, encoder slabs, a predictor, one
loss. It is drawn in cm (as the source overview was) with 0.7 pt wires and Stealth heads, 13 pt labels and 10 pt
two-line labels inside slabs, and it is designed to print at about half its drawn size (the source overview was
400 bp wide and printed at 0.50 inside the composed Figure 1, so its 13 pt labels printed at 6.5 pt).

**Contents**
1. Rules of an overview
2. Teacher-student training overview
3. A linear pipeline
4. Two inputs converging on one block
5. A shared trunk with several heads
6. An encoder-decoder with skip connections
7. A loop between an agent and its environment

## 1. Rules of an overview

- **One loss box, no legend, no glosses.** The source's overview went from three loss boxes and a two-column legend
  to one box with $\mathcal{L}$ inside, at the author's direction ("drop the legend and make that figure bigger
  ... go back to the abstract's one L loss"). The full objective goes in the caption.
- **A loss box sits where the two compared quantities meet.** The prediction enters one face on the box's center
  line; the target enters another. An earlier version took two wires into one face at different heights and let a
  target rail cross a wire with no junction; both were removed.
- **The weight copy is a dashed wire labeled EMA; stop-gradient is two short slashes across the target's wire.**
  Nothing else in the overview is dashed except a link to a zoomed crop.
- **Inputs are crops of one field.** The masked views are the same crop masked two ways; the target encoder sees
  the crop unmasked. Draw them from `scripts/zoom_cascade.py --views`, never by hand.
- **Orthogonal wiring**: one wire leaves the crop, branches at right angles, and enters each consumer on its
  facing side. A wire starts on the frame it leaves; the source's 0.03 cm gaps showed in the audit.
- **Keep the author's drawing.** A pass that rewrote the overview in words and moved its encoders was rejected
  ("super ugly encoders, do not drift from the previous version so much") and rolled back. Change labels and
  wiring; do not move the shapes the author placed.

## 2. Teacher-student training overview

The complete figure is `assets/examples/overview.tex` (with generated crops, the cascade and the sphere glyph).
This recipe is its skeleton with hand-placed stand-ins, to show the geometry in one block.

```latex
\begin{tikzpicture}[paper]
  % inputs: one crop masked two ways (stand-ins; generate them for a real figure)
  \draw[crop] (1.10,3.90) rectangle (2.80,5.60);
  \draw[maskbox] (1.3,4.7) rectangle (1.9,5.3);
  \draw[crop] (3.80,3.90) rectangle (5.50,5.60);
  \node[lbl] at (1.95,3.40) {spatial};
  \node[lbl] at (4.65,3.40) {category};
  \draw[flow] (5.0,2.80) -- (0.55,2.80) -- (0.55,4.75) -- (1.06,4.75);
  \draw[flow] (5.0,2.80) -- (6.05,2.80) -- (6.05,4.75) -- (5.54,4.75);
  \draw[flow] (6.05,2.80) -- (9.80,2.80) -- (9.80,6.25);
  % encoders and the weight copy
  \slab{1.53,6.28}{3.35}{context\\encoder}
  \slab{8.28,6.28}{3.05}{target\\encoder}
  \draw[flow] (1.95,5.60) -- (1.95,6.28);
  \draw[flow] (4.65,5.60) -- (4.65,6.28);
  \draw[ema] (4.93,6.69) -- (8.24,6.69);
  \node[lbl] at (6.56,7.11) {EMA};
  % prediction, the one loss, the target with its stop-gradient
  \dcap{2.38,8.72}{2.31}{1.06}{predictor}
  \draw[flow] (3.80,7.47) -- (3.80,8.72);
  \node[qbox] (q) at (1.05,9.25) {query\\$q(A)$};
  \draw[flow] (q.east) -- (2.38,9.25);
  \draw[flow] (5.25,9.25) -- (11.94,9.25);
  \node[lbl, anchor=south] at (8.6,9.32) {$\hat y_A$};
  \draw[flowbare] (11.33,6.83) -- (12.44,6.83);
  \draw[flow] (12.44,6.83) -- (12.44,8.79);
  \stopgrad{12.44,7.75}
  \node[lbl, anchor=west] at (12.58,8.28) {$y_A$};
  \node[loss] at (12.44,9.25) {$\mathcal{L}$};
\end{tikzpicture}
```

## 3. A linear pipeline

Suggested, not yet tested in real work. Input, encoder, the set of tokens it returns, a head, the output; one
reading direction, left to right.

```latex
\begin{tikzpicture}[paper]
  \draw[crop] (0,0) rectangle (1.7,1.7);
  \foreach \x/\y/\c in {0.4/0.5/ptblue, 0.9/1.2/ptochre, 1.3/0.6/ptpurple, 0.6/1.4/ptblue, 1.2/1.0/ptochre}
    {\figpoint{\x,\y}{\c}}
  \node[lbl] at (0.85,-0.45) {input};
  \draw[flow] (1.75,0.85) -- (2.35,0.85);
  \slab{2.4,0.44}{2.6}{encoder}
  \draw[flow] (5.05,0.85) -- (5.65,0.85);
  \begin{scope}[x=1bp, y=1bp, shift={(6.2cm,0.85cm)}]
    \tokstack{0,0}{tokblue}
    \tokdepthbrace{0,0}{$N$}
  \end{scope}
  \draw[flow] (7.65,0.85) -- (8.25,0.85);
  \node[box, minimum width=1.9cm] at (9.25,0.85) {head};
  \draw[flow] (10.25,0.85) -- (10.85,0.85);
  \node[lbl, anchor=west] at (10.9,0.85) {$\hat y$};
\end{tikzpicture}
```

## 4. Two inputs converging on one block

Suggested, not yet tested in real work. Two encoders, their outputs added in a join, one block after it. The join
takes each addend on its own side.

```latex
\begin{tikzpicture}[paper]
  \slab{0,2.0}{2.6}{image\\encoder}
  \slab{0,0}{2.6}{text\\encoder}
  \coordinate (j) at (4.0,1.4);
  \draw[flowbare] (2.65,2.41) -- (4.0,2.41);
  \draw[flow] (4.0,2.41) -- (4.0,1.55);
  \draw[flowbare] (2.65,0.41) -- (4.0,0.41);
  \draw[flow] (4.0,0.41) -- (4.0,1.25);
  \begin{scope}[x=1bp, y=1bp, shift={(4.0cm,1.4cm)}, scale=0.75]
    \joincircle{0,0}
  \end{scope}
  \draw[flow] (4.15,1.4) -- (5.0,1.4);
  \node[opbox=oppeach, minimum width=2.6cm, minimum height=0.9cm] at (6.3,1.4) {fusion block};
\end{tikzpicture}
```

## 5. A shared trunk with several heads

Suggested, not yet tested in real work. One trunk wire, junction dots where it branches, one plain box per head.
Every head box takes one size.

```latex
\begin{tikzpicture}[paper]
  \slab{0,0.6}{2.6}{shared\\trunk}
  \draw[flowbare] (2.65,1.01) -- (3.4,1.01);
  \draw[flowbare] (3.4,-0.29) -- (3.4,2.31);
  \fill[ink] (3.4,1.01) circle (1.4pt);
  \foreach \y/\t in {2.31/segment, 1.01/detect, -0.29/classify} {
    \draw[flow] (3.4,\y) -- (4.05,\y);
    \node[box, minimum width=1.9cm] at (5.05,\y) {\t};}
\end{tikzpicture}
```

## 6. An encoder-decoder with skip connections

Suggested, not yet tested in real work. Encoder slabs step down, decoder slabs step up; each skip leaves the top
of its encoder, runs above the path and enters its decoder from above. A skip carries activations like any other
wire, so it is solid: in this style a dash means a weight copy or a level that is not drawn. The elbow of every
wire sits in the middle of its gap, so the last leg is longer than the arrowhead.

```latex
\begin{tikzpicture}[paper]
  \foreach \i/\x/\y in {1/0/2.4, 2/2.1/1.2, 3/4.2/0} {\slab{\x,\y}{1.5}{enc \i}}
  \foreach \i/\x/\y in {2/6.3/1.2, 1/8.4/2.4} {\slab{\x,\y}{1.5}{dec \i}}
  % the path: out of a slab's right side, down or up in the gap, into the next slab's left side
  \draw[flow] (1.5,2.7) -- (1.8,2.7) -- (1.8,1.7) -- (2.1,1.7);
  \draw[flow] (3.6,1.5) -- (3.9,1.5) -- (3.9,0.5) -- (4.2,0.5);
  \draw[flow] (5.7,0.5) -- (6.0,0.5) -- (6.0,1.7) -- (6.3,1.7);
  \draw[flow] (7.8,1.7) -- (8.1,1.7) -- (8.1,2.9) -- (8.4,2.9);
  % the skips: a slab's dome tops out 1.23 above its base (0.82 of side, 0.41 of dome)
  \draw[flow] (0.75,3.63) -- (0.75,4.2) -- (9.15,4.2) -- (9.15,3.65);
  \draw[flow] (2.85,2.43) -- (2.85,3.0) -- (7.05,3.0) -- (7.05,2.45);
  \node[glossnote] at (4.95,4.45) {skip};
\end{tikzpicture}
```

## 7. A loop between an agent and its environment

Suggested, not yet tested in real work. Two blocks and two orthogonal wires that close the loop; each wire carries
its symbol on the outside of the loop.

```latex
\begin{tikzpicture}[paper]
  \node[opbox=opmint, minimum width=3.2cm, minimum height=0.9cm] (a) at (0,1.6) {agent};
  \node[box, minimum width=3.2cm, minimum height=0.9cm] (e) at (0,0) {environment};
  \draw[flow] (a.east) -- (2.4,1.6) -- (2.4,0) -- (e.east);
  \draw[flow] (e.west) -- (-2.4,0) -- (-2.4,1.6) -- (a.west);
  \node[lbl, anchor=west] at (2.5,0.8) {$a_t$};
  \node[lbl, anchor=east] at (-2.5,0.8) {$s_{t+1}, r_t$};
\end{tikzpicture}
```
