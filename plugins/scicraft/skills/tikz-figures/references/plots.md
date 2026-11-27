# Plots in the same style (PGFPlots)

Data plots that sit in a paper beside the style's schematics: Computer Modern type, hairline axes on the left and
bottom only, black text, the package's color roles and its sequential ramp. A plot is drawn at its PRINTED size
(unlike a schematic), so its type is the package's on-page tiers directly: 7 pt titles, 6 pt labels, 5 pt ticks,
annotations and in-cell values, an 8 pt bold letter (sibling skill `data-figures`, `references/style-tokens.md`).
The `paperaxis` style in the preamble sets them.

The PGFPlots recipes here are suggested, not yet tested in real work: the author's result figures were made in
matplotlib (sibling skill `data-figures`), and the rules below are the rules those figures followed.

**Contents**
1. Rules every plot follows
2. Curves with bands, read from a CSV
3. Sorted thin bars with the value at the bar end
4. A heat matrix of ranks with values, brackets and asterisks
5. A dot plot with direct labels

## 1. Rules every plot follows

- **Values come from the records.** A plot reads a CSV (`\addplot table {runs.csv}`); numbers are never typed into
  the `.tex`. The recipes below write their stand-in CSV with `filecontents*` so they compile alone; a real figure
  reads the project's file.
- **No legend where a direct label fits.** Name a curve at its end, a dot beside itself. A legend over a panel the
  labels already explain was called "AI slop".
- **Panel titles of two to four words** ("Validation loss", "Mean rank by scale"). A longer title was too long
  ("make it clear one thing and go").
- **Significance is an asterisk after the number**, set as its own text so the number stays centered, explained in
  the caption. No bold for significance, and no dagger anywhere (the author called a dagger a "clear AI slop flag").
- **At least three ticks per axis**, evenly spaced, their labels not touching ("for each x axis have at least 3
  ticks").
- **One color per compared item, the same item the same color in every panel.** `hero` for the paper's method,
  `rival` for the strongest comparator, `othergray` for the rest, `basegray` for a trivial baseline. Color for
  emphasis only where the values themselves are plotted or printed.
- **Every matrix has a head over its row labels** and a caption that says what a row is.

## 2. Curves with bands, read from a CSV

Mean over seeds with a band of one standard deviation; the caption says which (sample or population) and over how
many seeds. Direct labels at the right end.

```latex
\begin{filecontents*}[overwrite]{runs.csv}
step,ours,ours_sd,base,base_sd
0,1.00,0.040,1.00,0.040
2000,0.62,0.030,0.74,0.035
4000,0.45,0.025,0.61,0.030
6000,0.37,0.020,0.55,0.030
8000,0.32,0.020,0.52,0.028
10000,0.29,0.018,0.50,0.027
\end{filecontents*}
\begin{tikzpicture}
  \begin{axis}[paperaxis, width=4.6cm, height=3.0cm, title={Validation loss}, xlabel={step}, ylabel={loss},
      xmin=0, xmax=10000, ymin=0.2, ymax=1.05, xtick={0,5000,10000}, ytick={0.25,0.5,0.75,1.0},
      scaled x ticks=false, xticklabel style={/pgf/number format/fixed}]
    \addplot[name path=bu, draw=none, forget plot] table[x=step, y expr=\thisrow{base}+\thisrow{base_sd}, col sep=comma] {runs.csv};
    \addplot[name path=bl, draw=none, forget plot] table[x=step, y expr=\thisrow{base}-\thisrow{base_sd}, col sep=comma] {runs.csv};
    \addplot[fill=basegray!25, draw=none] fill between[of=bu and bl];
    \addplot[name path=ou, draw=none, forget plot] table[x=step, y expr=\thisrow{ours}+\thisrow{ours_sd}, col sep=comma] {runs.csv};
    \addplot[name path=ol, draw=none, forget plot] table[x=step, y expr=\thisrow{ours}-\thisrow{ours_sd}, col sep=comma] {runs.csv};
    \addplot[fill=hero!20, draw=none] fill between[of=ou and ol];
    \addplot[basegray] table[x=step, y=base, col sep=comma] {runs.csv} node[pos=1, anchor=west, font=\fontsize{5}{6}\selectfont] {baseline};
    \addplot[hero] table[x=step, y=ours, col sep=comma] {runs.csv} node[pos=1, anchor=west, font=\fontsize{5}{6}\selectfont] {ours};
  \end{axis}
\end{tikzpicture}
```

## 3. Sorted thin bars with the value at the bar end

Bars sorted by value, thin (about a third of the slot), the value printed at the bar's end, the paper's method in
`hero`, the rest `othergray`.

```latex
\begin{filecontents*}[overwrite]{deltas.csv}
part,delta
masking,-0.112
pooling,-0.081
graph,-0.054
position,-0.031
depth,-0.012
\end{filecontents*}
\begin{tikzpicture}
  \begin{axis}[paperaxis, xbar, width=3.6cm, height=2.8cm, title={Largest decrease}, xlabel={change in score},
      y dir=reverse, ytick=data, symbolic y coords={masking,pooling,graph,position,depth},
      yticklabel style={font=\fontsize{6}{7.2}\selectfont}, xmin=-0.14, xmax=0, xtick={-0.12,-0.08,-0.04,0},
      xticklabel style={/pgf/number format/.cd, fixed, precision=2, skip 0.}, bar width=3.2pt, axis x line*=bottom,
      axis y line*=right, ytick style={draw=none}, enlarge y limits=0.15,
      nodes near coords={\pgfmathprintnumber[fixed, precision=3, skip 0.]{\pgfplotspointmeta}},
      nodes near coords align={horizontal}, every node near coord/.append style={font=\fontsize{5}{6}\selectfont, anchor=east, xshift=-1pt},
      point meta=x]
    \addplot[fill=othergray, draw=none] table[x=delta, y=part, col sep=comma] {deltas.csv};
  \end{axis}
\end{tikzpicture}
```

## 4. A heat matrix of ranks with values, brackets and asterisks

The model of the author's results figures: filled cells on the package's sequential ramp (best darkest), the value
inside every cell, white text on the two darkest steps, an asterisk after a significant value as its own text, a
head over the row labels, and scale brackets over groups of columns with end rules at least 0.8 mm long. The
color shows rank; the printed value is the measurement, so color is emphasis on values that are printed.

```latex
\begin{filecontents*}[overwrite]{ranks.csv}
col,row,rank,value,star
0,0,1,0.81,1
1,0,1,0.77,1
2,0,2,0.64,0
3,0,1,0.58,1
0,1,2,0.79,0
1,1,3,0.70,0
2,1,1,0.69,1
3,1,2,0.55,0
0,2,4,0.61,0
1,2,2,0.73,0
2,2,3,0.60,0
3,2,3,0.52,0
0,3,3,0.66,0
1,3,4,0.62,0
2,3,4,0.57,0
3,3,4,0.49,0
\end{filecontents*}
\begin{tikzpicture}
  \begin{axis}[paperaxis, axis lines=none, width=3.6cm, height=2.4cm, y dir=reverse, enlargelimits=false,
      xmin=-0.5, xmax=3.5, ymin=-0.5, ymax=3.5, colormap name=rank5, point meta min=1, point meta max=5, clip=false]
    % audit-accept: OVERLAP v at  # PGFPlots strokes each cell in its own color so no white seam shows between cells
    % audit-accept: OVERLAP h at  # the same, along the rows
    \addplot[matrix plot*, mesh/cols=4, point meta=explicit] table[x=col, y=row, meta expr=6-\thisrow{rank}, col sep=comma] {ranks.csv};
    % values: black on the light steps, white on the two darkest
    \addplot[only marks, mark=none, nodes near coords={\pgfmathprintnumber[fixed, fixed zerofill, precision=2, skip 0.]{\pgfplotspointmeta}},
        every node near coord/.append style={anchor=center, font=\fontsize{5}{6}\selectfont, text=black}, point meta=explicit,
        y filter/.expression={\thisrow{rank}>2 ? y : nan}] table[x=col, y=row, meta=value, col sep=comma] {ranks.csv};
    \addplot[only marks, mark=none, nodes near coords={\pgfmathprintnumber[fixed, fixed zerofill, precision=2, skip 0.]{\pgfplotspointmeta}},
        every node near coord/.append style={anchor=center, font=\fontsize{5}{6}\selectfont, text=white}, point meta=explicit,
        y filter/.expression={\thisrow{rank}<=2 ? y : nan}] table[x=col, y=row, meta=value, col sep=comma] {ranks.csv};
    % significance: an asterisk right after the number, its own text, so the number stays centered in its cell
    % (a two-digit value at 5 pt is 8.4 pt wide: the asterisk starts 4.6 pt right of the cell's center); its ink
    % follows the cell like the number's
    \addplot[only marks, mark=none, nodes near coords={$^{*}$},
        every node near coord/.append style={anchor=west, inner sep=0pt, xshift=4.6pt, font=\fontsize{5}{6}\selectfont, text=white},
        y filter/.expression={\thisrow{star}>0 && \thisrow{rank}<=2 ? y : nan}] table[x=col, y=row, col sep=comma] {ranks.csv};
    \addplot[only marks, mark=none, nodes near coords={$^{*}$},
        every node near coord/.append style={anchor=west, inner sep=0pt, xshift=4.6pt, font=\fontsize{5}{6}\selectfont, text=black},
        y filter/.expression={\thisrow{star}>0 && \thisrow{rank}>2 ? y : nan}] table[x=col, y=row, col sep=comma] {ranks.csv};
    % row labels, a head over them, column labels, scale brackets (written out: a plain \foreach inside an
    % axis is deferred and its variable is not expanded)
    \node[anchor=east, font=\fontsize{6}{7.2}\selectfont] at (axis cs:-0.6,0) {ours};
    \node[anchor=east, font=\fontsize{6}{7.2}\selectfont] at (axis cs:-0.6,1) {method B};
    \node[anchor=east, font=\fontsize{6}{7.2}\selectfont] at (axis cs:-0.6,2) {method C};
    \node[anchor=east, font=\fontsize{6}{7.2}\selectfont] at (axis cs:-0.6,3) {method D};
    \node[anchor=east, font=\fontsize{6}{7.2}\selectfont] at (axis cs:-0.6,-0.95) {method};
    \node[font=\fontsize{5}{6}\selectfont] at (axis cs:0,-0.95) {task 1};
    \node[font=\fontsize{5}{6}\selectfont] at (axis cs:1,-0.95) {task 2};
    \node[font=\fontsize{5}{6}\selectfont] at (axis cs:2,-0.95) {task 3};
    \node[font=\fontsize{5}{6}\selectfont] at (axis cs:3,-0.95) {task 4};
    % brackets in axis units: a relative step such as ++(0,-1mm) is read in axis units inside an axis
    \draw[black!93, line width=0.4pt] (axis cs:-0.45,-1.28) -- (axis cs:-0.45,-1.45) -- (axis cs:1.45,-1.45) -- (axis cs:1.45,-1.28);
    \draw[black!93, line width=0.4pt] (axis cs:1.55,-1.28) -- (axis cs:1.55,-1.45) -- (axis cs:3.45,-1.45) -- (axis cs:3.45,-1.28);
    \node[font=\fontsize{6}{7.2}\selectfont] at (axis cs:0.5,-1.85) {small};
    \node[font=\fontsize{6}{7.2}\selectfont] at (axis cs:2.5,-1.85) {large};
  \end{axis}
\end{tikzpicture}
```

## 5. A dot plot with direct labels

One dot per method on one axis, one dot size for every method (no larger dot for the paper's own), the name beside
the dot and the value printed. No legend, no whisker unless an interval was asked for.

```latex
\begin{filecontents*}[overwrite]{scores.csv}
method,score,y
ours,0.812,0
method B,0.774,1
method C,0.741,2
baseline,0.602,3
\end{filecontents*}
\begin{tikzpicture}
  \begin{axis}[paperaxis, width=4.0cm, height=2.2cm, title={Mean score}, y dir=reverse, ymin=-0.6, ymax=3.6,
      axis y line=none, xmin=0.55, xmax=0.9, xtick={0.6,0.7,0.8}, xlabel={score},
      xticklabel style={/pgf/number format/.cd, fixed, precision=1, skip 0.}]
    % the value beside the dot, then the name: two label passes (the name is a string, a symbolic meta)
    \addplot[only marks, mark=*, mark size=1.3pt, othergray, y filter/.expression={y>0 ? y : nan},
        nodes near coords={\pgfmathprintnumber[fixed, precision=3, skip 0.]{\pgfplotspointmeta}},
        every node near coord/.append style={anchor=west, font=\fontsize{5}{6}\selectfont, text=black, xshift=1pt},
        point meta=x] table[x=score, y=y, col sep=comma] {scores.csv};
    \addplot[only marks, mark=*, mark size=1.3pt, hero, y filter/.expression={y==0 ? y : nan},
        nodes near coords={\pgfmathprintnumber[fixed, precision=3, skip 0.]{\pgfplotspointmeta}},
        every node near coord/.append style={anchor=west, font=\fontsize{5}{6}\selectfont, text=black, xshift=1pt},
        point meta=x] table[x=score, y=y, col sep=comma] {scores.csv};
    \addplot[only marks, mark=none, nodes near coords, point meta=explicit symbolic,
        every node near coord/.append style={anchor=west, font=\fontsize{5}{6}\selectfont, text=black, xshift=16pt}]
        table[x=score, y=y, meta=method, col sep=comma] {scores.csv};
  \end{axis}
\end{tikzpicture}
```
