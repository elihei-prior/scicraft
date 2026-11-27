# Math and annotation layout

Math in a figure uses the paper's own notation, the default math font (so figure math and body math agree), and
only the symbols the figure needs. The author's rule for symbols, after a pass that crowded a figure with them:
"drop all symbols if not necessary other than losses ... then define them exactly". A week later the legend went
too, and the overview kept one loss and no glosses; the caption carries the rest.

**Contents**
1. What may appear
2. A symbol beside its glyph, and the one legend line
3. A label above a tap, a label beside a wire
4. A loss with braces under its terms
5. An arrow to a term
6. A commutative square
7. Gaps and leading, from the measured figures

## 1. What may appear

- **Only defined symbols.** A symbol is defined by the caption over its glyph, by the legend line, or by the
  figure's caption. A symbol defined nowhere is deleted.
- **No illustrative numbers** ("don't give numerical examples like 0.69"): a number appears only when it is the
  real value of what is drawn, read from the records.
- **Names as a reader meets them**, never variable names from the code; the paper's notation for symbols.
- **At most one boxed equation in a figure**, and only where the paper itself states it; an overview carries none.
- **Math is set in the document's math font.** The source figures moved from a sans math setup to the default
  math; uppercase Greek under a sans math package printed as empty boxes with no message in the log, one more
  reason the style has no sans option.

## 2. A symbol beside its glyph, and the one legend line

```latex
\begin{tikzpicture}[x=1bp, y=1bp, paper]
  \tokstack{0,0}{tokblue}
  \node[note, anchor=base west] at (23.6,-4.4) {$Z$};
  \tokrow{80,0}{tokyellow}{4}
  \node[note, anchor=base] at (80,8) {$x_i$};
  \node[capt, anchor=base west] at (-12,-34) {$Z$: the set's pooled tokens\quad $x_i$: the token of point $i$};
\end{tikzpicture}
```

## 3. A label above a tap, a label beside a wire

The source moved a residual's label from 4.5 bp to 10 bp above its tap because its subscript crossed the wire;
wire labels sit 4 bp beside the wire they name, base-aligned.

```latex
\begin{tikzpicture}[x=1bp, y=1bp, paper]
  \draw[wire] (60,0) -- (60,-60);
  \junction{60,-20}
  \draw[residbare] (60,-20) -- (10,-20) -- (10,-70);
  \node[note, anchor=base west] at (14,-10) {$W_r$};
  \node[note, anchor=base east] at (56,-45) {$q$};
\end{tikzpicture}
```

## 4. A loss with braces under its terms

Suggested, not yet tested in real work in a figure: the author kept the full objective in captions and posters.
When a poster or an appendix figure states it, brace each term with its name in gray under it.

```latex
\begin{tikzpicture}[paper]
  \node[lbl] at (0,0) {$\mathcal{L} \;=\; \underbrace{\mathcal{L}_{\mathrm{pred}}}_{\text{\textcolor{glossink}{prediction}}}
      \;+\; \lambda\,\underbrace{\mathcal{L}_{\mathrm{reg}}}_{\text{\textcolor{glossink}{regularizer}}}$};
\end{tikzpicture}
```

## 5. An arrow to a term

Suggested, not yet tested in real work. A hairline arrow from a gray note to one term of an equation; the note
stays clear of the equation by at least its own height.

```latex
\begin{tikzpicture}[paper]
  \node[lbl] (eq) at (0,0) {$\bar\mu(A) = S(A) / \lVert S(A) \rVert$};
  \node[glossnote, anchor=north] (n) at (0.35,-0.9) {the resultant};
  \draw[black!45, line width=0.45pt, -{Stealth[length=3pt]}] (n.north) -- (-0.28,-0.28);
\end{tikzpicture}
```

## 6. A commutative square

Suggested, not yet tested in real work. Objects as math labels, maps as wires with their symbols beside them.

```latex
\begin{tikzpicture}[paper]
  \node[lbl] (x) at (0,1.6) {$X$};
  \node[lbl] (y) at (2.6,1.6) {$Y$};
  \node[lbl] (gx) at (0,0) {$gX$};
  \node[lbl] (gy) at (2.6,0) {$gY$};
  \draw[flow] (x) -- (y) node[midway, above, font=\fLabel] {$f$};
  \draw[flow] (gx) -- (gy) node[midway, below, font=\fLabel] {$f$};
  \draw[flow] (x) -- (gx) node[midway, left, font=\fLabel] {$g$};
  \draw[flow] (y) -- (gy) node[midway, right, font=\fLabel] {$g$};
\end{tikzpicture}
```

## 7. Gaps and leading, from the measured figures

| Gap | Value at design scale | Source |
|---|---|---|
| a black name to its gray gloss | 15 bp between baselines at 13 to 13.6 pt (1.1 times the size) | block cards |
| a wire label to its wire | 4 bp, base-aligned | block cards |
| a label above a tap | 10 bp; at 4.5 bp the subscript crossed the wire | readout card |
| a symbol above a stack | 8.5 bp above the back row; at 6 bp a subscript touched a chip | readout card |
| an arrowhead to a box | 1 bp | block cards |
| a card name | 12 bp from the card's edge, baseline 0.32 of its size under the border | block cards |

A later skill by the same author gave the same laws at true size: arrows stop about 0.10 cm short of shapes and
0.14 cm short of text, text keeps 0.25 cm from unrelated ink, stacked lines need 0.40 cm of leading at 9.5 to 10
pt. At this style's design factor of about 2.2 those are 6, 9, 16 and 25 bp, looser than the paper's figures;
use the table above for this style and the audit as the gate.
