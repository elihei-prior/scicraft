# Color

Color belongs to the data. Structure is ink and gray; one accent marks the work's own method or term; every other
hue encodes something and has a key.

## 1. Palettes

| Use | Colors | Why |
|---|---|---|
| categories | Okabe-Ito `#0072B2 #E69F00 #009E73 #CC79A7 #56B4E9 #D55E00 #999999` | distinguishable under the common color-vision deficiencies |
| extra categories | `#785EF0` (violet), `#AA4499`, `#DDAA33` | violet replaced a neon lime `#76FF03` |
| magnitude, ordinal | `#F1F6FF #C7DCFF #8FB9FF #4D97FF #003FBD` | one hue, lightness carries the order; the same ramp in every figure, schematic and table |
| rank on a dark page | `#b7d3f6 #5598e7 #256abf #1d4f93 #23252d` (rank 1, 2, 3, 4 to 7, 8 and worse) | |
| signed values | `#0A84FF` to `#FF3B30`, white from 0.43 to 0.57; alternative `#2166AC #F7F7F7 #D55E00` | blue-white-red with a wide white plateau (blue-white-orange when red is taken); both avoid red-green |
| match versus mismatch | white to red only | a blue end was "confusing" there |
| missing | face `#DDDDDD`, edge `#888888`, hatch `//` | hatch reads without color |
| Apple-like system hues | slightly muted (about 0.9 alpha) | "too shiny" at full strength, "too muted" below that |

Categorical colors are saturated; metadata (tissue class, dataset icon, role) is pastel or from a different hue
family. The two systems never touch.

## 2. Roles and locks

- **The method palette is locked for the whole work**: the same hue for the same method in every figure, the
  poster, the deck and the site ("make sure the color palette of this (methods) and figure 4 are matching"). Keep it
  in one file (a `palettes.py` or the `tokens.json` of this skill) and import it; a copy pasted into an HTML file
  drifted.
- **No other categorical axis may resemble a method color.** An orange sender and blue receiver were read as two
  methods; roles moved to violet `#7E3FF2`, teal `#00B3B3` and red `#FF2D55`. A cell-type palette was built to avoid
  blue and amber entirely; dataset icons took a teal-to-violet family.
- **One cell-type (or class) map across all supplements.**
- **Separate semantic roles get separate hues**: the recovered object in amber `#EBA02E` everywhere, the raw
  unassigned state in vermillion `#E5553B`.
- **Red carries one meaning per figure** (removed, bad, forbidden in the source). Red marks go on top of other marks.
  A category that clashes with red moves to mustard or orange.
- **Your own method gets its hue and no extra weight**: same marker, line width and fill; no fill on its radar trace
  when the others have none; no star on its bar. A thin gray line at its median is the allowed comparison aid.
- **At most one rival color** (`#e69f00`) when a strongest comparator is named. Everything else is gray (`#5c5c64` on
  a dark page).

## 3. Color-blind safety

- Okabe-Ito for categories, a single-hue ramp for magnitude, blue-white-red with a wide white plateau for signed values
  (blue-white-orange when red is taken).
- **Never red against green** for good versus bad. Valence is a pale green "expected" band and a pink "unexpected"
  band behind the data, or a mark (an asterisk). Green and red bars broke the rule.
- **Line style carries a difference when two hues might merge.** The schematics keep a green positive edge and a
  red negative edge because the negative is dashed; keep the dash if you keep the pair.
- **Ordinal means a lightness ramp, categorical means distinct hues, emphasis means weight and drawing order**, never
  a louder hue.
- **A categorical column never takes shades of one hue.** Shades read as an order. In one schematic, cell lines in
  four pinks and drugs in four golds were taken for numbers: "it was categorical not numerical, you killed it". Give
  categories distinct hues and, where icons are used, a shape per variable (a cell, a pill).
- **Gray means "not given".** In a schematic of model inputs, an icon in color is read by the model and a gray one
  only says what the row is. Keep gray free of any other meaning in that figure.
- **Keep categorical colors out of the hue families of the numerical scales** shown beside them. Class colors in
  the green, blue and red families were read as viability, down and up.
- The author works in a color-blind-friendly dark terminal theme; check every palette the same way.
  `scripts/palette_check.py` gives the closest pairs across families and within each family in normal vision,
  deuteranopia and protanopia (CIE76 delta E, Machado et al. 2009). Below about 20 two meanings are easy to confuse
  in small marks. Where a collision cannot be removed, let shape or position carry the difference.

## 4. Keys

- Every color in view has a key: a dot and a name for each category (the ten most frequent, plus the gray of
  "other"), or words for a continuous scale.
- A key is redundant when row labels or direct labels already name the series; remove it then.
- A key is shared when the same series repeat across small panels: one legend for the row, or a strip between two
  rows that keys panels above and below.
- One legend font across panels.
- "If you color on one side then color other side": a color used in one half of a comparison is used in the other.

## 5. Dense pictures

- Thousands of categories (genes, tokens) render as gray density with a few chosen ones in color.
- Many objects that tessellate a view get thin outlines or a fill near alpha 0.2 (0.38 already "buried" the outline
  color); masks without outlines at alpha 0.26 behind and 0.52 in front.
- At the finest zoom, thin light outlines over the points, never filled translucent shapes.
- An embedding mapped to RGB is rendered over the whole sample at 50 to 150 µm per pixel. A 3 mm central window of
  the same embedding looked like confetti and a good run was judged bad.

## 6. Contradictions between sources, and how they resolve

| Question | Earlier | Later | Use |
|---|---|---|---|
| signed scale | blue-white-orange in the libraries; white-to-red for match and mismatch | blue-white-red with the median at white, the plateau widened (a figure round of May 2026); blue-orange was judged near iso-luminant and flat | blue-white-red with a wide white plateau by default; blue-white-orange for unprinted schematic matrices; never red-green |
| accent on the own method versus no emphasis | the web gives the method the accent | figures forbid thicker lines, bigger points, stars | the method keeps its locked hue; size, weight and fill stay equal |
| legend | "label inline, kill the legend" | a shared legend across small panels; then "the legend is AI slop" for a redundant one | label inline when a panel stands alone; share a legend when series repeat; delete one that repeats the rows |
| gray text | captions in quiet gray on the web | no gray text on slides or in figures | gray on the web only; in a LaTeX table the ± SD may be tiny gray |
| figure tile ground | dark suggested by a reviewer agent | white demanded | white or off-white for print figures |
| staining channel | red nucleus on black | gray on white, "max gray not black" | light gray for supplements; a recolored channel where the main figure already set one |
