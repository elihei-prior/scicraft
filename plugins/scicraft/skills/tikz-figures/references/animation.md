# Animation: frame decks

Most moving figures work better as a static row of panels. Animate only when motion is the argument: a token
traveling through a block, a zoom descending through scales, messages spreading over a graph, a figure built up
part by part. No animation was made in this style's real work; the recipes below are suggested, not yet tested in
real work, and the rules come from the author's earlier frame-deck figures.

**Contents**
1. The frame deck
2. Rules
3. A token traveling down a block
4. Messages spreading over a graph
5. Assembling the frames

## 1. The frame deck

One standalone file with `multi=tikzpicture` in its class options, one `\Frame{k}` macro that draws frame k, and a
loop that calls it. Every frame starts with the same `\path[use as bounding box]`, or the crop of each frame
follows its content and the frames jitter.

```bash
python3 scripts/render_figure.py deck.tex --texinputs <skill>/assets --dpi 150    # fails if frame sizes differ
```

It prints the first, a middle and the last frame to look at.

## 2. Rules

- **Lock the bounding box in every frame**, sized to the largest extent of any frame.
- **A label that asserts something appears only in frames where it is true** ("converged" on every frame was
  thrown out).
- **Pacing**: a highlight holds 0.5 to 1 s, a new structure 1 to 1.5 s, the final state 1.5 to 3 s.
- **One change per frame**, in the style's grammar: a highlight is the `tokyellow` path color or a stronger fill,
  never a new hue.
- **The last frame is a figure on its own**: it is what a reader of the PDF sees.

## 3. A token traveling down a block

```latex
\newcommand{\Frame}[1]{%
\begin{tikzpicture}[x=1bp, y=1bp, paper]
  \path[use as bounding box] (-60,10) rectangle (60,-150);
  \node[box] at (0,-30) {LayerNorm};
  \node[opbox=opmint, minimum width=100bp] at (0,-85) {Self-Attention};
  \draw[wire] (0,0) -- (0,-15);
  \draw[wire] (0,-44) -- (0,-64);
  \draw[wire] (0,-105) -- (0,-130);
  \ifcase#1 \tokrow{0,5}{tokyellow}{4}\or \tokrow{0,-54}{tokyellow}{4}\or \tokrow{0,-118}{tokyellow}{4}
     \node[note, anchor=west] at (14,-118) {updated};\fi
\end{tikzpicture}}
\foreach \ff in {0,1,2} {\Frame{\ff}}
```

## 4. Messages spreading over a graph

```latex
\newcommand{\Frame}[1]{%
\begin{tikzpicture}[paper]
  \path[use as bounding box] (-0.3,-0.3) rectangle (4.3,2.3);
  \draw[graphedge] (0,1) -- (1,2) -- (2,1) -- (1,0) -- cycle (2,1) -- (3,2) -- (4,1) -- (3,0) -- (2,1);
  \foreach \x/\y/\k in {0/1/0, 1/2/1, 1/0/1, 2/1/1, 3/2/2, 3/0/2, 4/1/3} {
    \ifnum\k>#1 \fignode{\x,\y}{othergray}\else \fignode{\x,\y}{ptblue}\fi}
\end{tikzpicture}}
\foreach \ff in {0,1,2,3} {\Frame{\ff}}
```

## 5. Assembling the frames

The frames are rendered to PNG by `pdftoppm` (through `render_figure.py`). Assembling them into a GIF or a video
needs ffmpeg, ImageMagick or gifsicle, none of which this skill ships or ran:

```bash
ffmpeg -framerate 2 -i deck_v01-%d.png -vf palettegen pal.png
ffmpeg -framerate 2 -i deck_v01-%d.png -i pal.png -lavfi paletteuse deck.gif
```

Check the frame count and order in the result, and look at the first, a middle and the last frame.
