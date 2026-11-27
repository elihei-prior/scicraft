# Moving a figure between media

One work appears as paper figures, a poster, a deck and a web page. The type, palette, figures and animations stay
the same across them; the medium changes the ground, the density and the amount of explanation.

## 1. Paper figure to a dark slide or page

1. Render the figure page at 600 dpi: `pdftoppm -png -r 600 fig.pdf out`.
2. Crop to the panel that carries the claim.
3. Recolor for the ground: invert lightness, keep hue, raise chroma by 1.35 and lift pale fills clear of the
   ground. `talk-slides` ships the script (`dark_figure.py IN.png OUT.png --ground 141416 --ink F4F4F5 --chroma 1.35
   --crop x0,y0,x1,y1`).
4. Look for vanished pale fills and thin labels; lift them rather than redraw.
5. Check resolution: 2 px of image per slide px (a 3840 px PDF page), and text inside the panel at least 28 slide
   px (56 px when the panel is shown at half size).

A white plate behind the figure was rejected at once. If most renders sit on white, flip the medium to its light
variant instead.

## 2. Paper figure to a poster

- Place it unchanged as a vector PDF. Do not redraw it: new TikZ diagrams for a poster made the author "furious".
- Crop rows with LaTeX `trim` and `clip` (non-destructive).
- Recolor at most. Hide superseded strings under paint only when the source cannot be rebuilt.
- Inventory the paper's figures before laying out; the poster is mostly those figures.

## 3. Figure to a web page

- The web draws its own native charts and canvas figures, because they must respond to hover and click. They use
  the paper's numbers and the site's tokens.
- Gallery tiles are square with no labels; a dialog opens with the legend naming every color, including the gray of
  "other".
- Labels on a picture sit on a translucent ground plate `rgba(20,20,22,.78)`, in opposite corners so they never meet
  on a narrow screen.

## 4. Website animation to a slide

1. Serve a patched local copy: quiet grays to ink, thicker arrows, formulas removed for a non-specialist room.
2. For each frame set the time, call the render, read `canvas.toDataURL`. One figure at a time.
3. Composite on the slide ground, crop, encode H.264 yuv420p with even sizes, add 2 s of rest at the end.
4. Check that labels inside light boxes survived the patch.

Keep animations the author already liked and change their labels, never their drawing ("our older animations / vis
were close to perfect").

## 5. Comparisons and pictures with scale

- Two renders of one view: one picture split by a moving divider, preferred over two panels side by side.
- Text over a picture: on a plate in the ground color. Outlined text alone was unreadable.
- Every picture of a physical sample carries a scale bar on a plate inside the picture, and the size of the data
  (units, measurements) where the sample first appears. The general form for any data: units and denominators on the
  picture.
- Coarse blocks at zoom read as "pixelized": switch to a finer rendering when zoomed in.

## 6. Density by medium

| Medium | Density |
|---|---|
| paper figure | dense and flat: 5 to 7 pt type, many panels, captions in the caption file, no spare height; still no analysis dumps (six chart types in one figure) and no quarter-empty appendix figures |
| slide | one point and one picture, at most 25 words, 28 px type and up, three layouts |
| poster | mostly figures, a short verbatim abstract, one or two key sentences per section, body 22.7 pt printed, no white holes |
| web page | a few open blocks: about 40 words of opening, two headline numbers, one open figure per claim, the rest folded |
| schematic | a title, at most one subtitle, a small legend |

## 7. Audience

The audience changes the order, the formulas and the amount of background, never the look.

- **Machine-learning audience** (a conference paper, rebuttal figures, a poster at an ML venue): the paper's math is
  kept and typeset (definitions, a boxed core equation, the labeled loss); architectures are flat block diagrams
  with locked semantics (the role palette by default: ink outlines, pale fills that name the role, a red loss box;
  three-accent student blue, teacher teal, target amber as the alternative; dashed stop-gradient and EMA); benchmark results
  are rank heat maps with the value in each cell, and ratings as a dot with the value printed, the bootstrap IQR in the appendix table.
- **Domain audience** (clinicians, biologists, leadership): open with the raw data shown whole, then its scales;
  real samples in the expert's annotation colors with a legend; no formulas on mechanism slides ("drop the
  formulas"), the architecture as the website animation; the people who generated the data with photos. "figures
  sexy but slides scientific".
