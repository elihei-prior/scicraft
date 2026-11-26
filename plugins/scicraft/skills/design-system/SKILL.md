---
name: design-system
description: Sets the visual design system for a research project across every medium (data figure, schematic, slide, poster, web page) and gives the list of what reads as machine-made. Use it whenever a visual deliverable is made, restyled or reviewed, even when the user does not name it: "make it cleaner", "nicer", "more minimal", "sexier", "this looks like AI", "the text is too small", "pick colors for the methods", "make the poster match the paper", "is 14 px big enough at 120 mm". Holds one token table per medium (typefaces with fallbacks, type scale, minimum sizes with the print or projection arithmetic, colors with roles, spacing, line weights), the invariants that hold across media, what minimal means as deletions, and a script that converts px, mm and pt and checks a minimum font size. Medium skills point here for cross-media rules; prefer data-figures, canvas-schematics, tikz-figures, talk-slides, poster or paper-website for building the artifact itself.
---

# design-system

The visual rules one researcher applied to every artifact of their work (paper figures, method schematics, talk decks,
a conference poster, project websites) over about a year, and the patterns they threw out. Each rule here was asked
for or came out of a rejected draft, so each carries its number and its reason. The person who shaped it is called
the author. Where the author of the work at hand has a house style, theirs wins: record it and keep the mechanism.

> **PRIME DIRECTIVE: one family, one accent for the work's own term, hierarchy from size, weight and space, and
> every color belongs to the data.** A request to make something cleaner is answered by removing things inside the
> look the author already has.

The failures that cost the most time:

1. **Restyling when asked to polish.** "Cleaner", "nicer" and "sexier" were answered three times with a new look (a
   new typeface, new layouts, a richer encoding). All three lost to the first version: "what you did before was
   better, bring that back". Section 6.
2. **Machine-made patterns.** Cards, pills, gradients, gray captions, "·" separators, taglines, stat tiles. The author
   spots them in a second and calls the whole thing "AI slop". Section 7.
3. **Type sized for the screen and printed at another size.** A schematic set at 18 px on a 3200 px canvas printed at
   180 mm came out near 3 pt. Size type from the final print or projection width, with the script (section 2).

## 0. Before starting

Collect by reading the project. Ask only for what cannot be found, in one message:

- **The reference artifact.** The figure, deck, poster or page the author already likes. Its look is the look. If
  they say "bring back" or "the original", restore that exact file from disk, never an approximation.
- **The medium and its final size.** Print width in mm (89 or 183 mm for a journal column, 180 mm on A4, A0 for a
  poster), canvas width in px, projection (1920 x 1080), screen.
- **The ground of the data renders.** Benchmark plots on white, embedding maps on a dark field, microscopy on black. The page or
  slide takes that ground (section 1).
- **Locked colors.** The method palette already used in the paper, category palettes in the supplements, the color
  that means "removed" or "bad".
- **The work's own term.** The one coined name that gets the accent (or italic) everywhere.
- **The house style of the venue or host**, if one is imposed (a venue template, a light corporate deck).

Copy `assets/tokens.json` into the project and edit the accent, method colors and host color there, so every script
and page reads one source.

## 1. Invariants across media

These hold in every medium. The per-medium tables in section 3 instantiate them.

- **One sans family: Helvetica Neue, Light (300) for text, Medium (500) for titles and emphasis.** It is the face of
  the poster, decks, website, schematics and matplotlib panels, and a restyle in Arial lost. Fallback chain
  `'Helvetica Neue', Helvetica, Inter, Arial, sans-serif`. Vary weight, never family. Math is Latin Modern or Computer
  Modern, never sans letters. A mono face (IBM Plex Mono) appears only on the web, for one-line meta facts. In
  LaTeX use `fontspec` with the real face; the `helvet` clone looks foreign beside it. Exceptions: a document set in
  the venue's serif keeps it, and TikZ figures inside it may take the document font so figure math and body math
  agree; a personal homepage may use a serif pair (references/tokens-by-medium.md, section 7).
- **One accent, given to the work's own method or term.** Web `--ours #8ec9ff`, a poster's one accent, a light teaching
  deck `#d66a2b`, a document's link color. At most one rival color (`#e69f00`) when a strongest comparator is named.
  Everything else is gray or belongs to the data. On slides the accent is never a text color.
- **Hierarchy from size, weight and space only.** No boxes, cards, shadows, gradients or icons. A section is a
  hairline with a large name under it (1 px `#2e2e34` on a dark page, a 0.09 cm rule on the poster). Shadows exist
  only on floating overlays (tooltip, dialog).
- **The ground matches the data renders.** The dark web and slide ground `#141416` is the ground of the field
  renders, "so their colors read as in the paper". Never put a white-ground figure on a dark page or the reverse
  ("Do not bring white background figs"): recolor it (section 5) or flip the theme.
- **Color-blind safe.** Categories from Okabe-Ito, magnitude on one blue ramp, signed values on blue-white-red with a wide white plateau,
  never red against green. Good versus bad is a background band or a mark, never a hue pair. Section 4.
- **Color belongs to the data, and every color in view has a key.** "If you use a color explain what it is." The same
  category keeps the same color on every panel, slide and page. Name a continuous scale in words ("cosine
  similarity").
- **Emphasis is weight on a phrase, italic only for the coined term.** No underline (except one's own name in an
  author list), no all caps, no colored punchline sentence, no boxed text. In figures, significance is an asterisk
  after the value, never bold.
- **Your own method gets its locked hue and nothing more.** Same marker size, line width and fill as every other
  method; no thicker line, no star on the best bar ("don't make [our] points or lines thicker ... let the results
  speak"). A thin gray reference line at its median is the allowed aid. Emphasis by color is allowed only because the
  values themselves are plotted to scale.
- **Reuse the author's figures and animations.** Change labels, colors and size, never the drawing: "do not make new
  diagrams ... don't make new plots!" The web is the exception; it draws native charts because they must respond.
- **Nothing overlaps, checked by script and by eye.** "Make sure things don't go over each other, this is QC."
- **No lone word on a last line, and a number stays bound to its unit** (`45&nbsp;µm`, `~` in LaTeX).

## 2. Size arithmetic

Every minimum size is a printed or projected size. Convert before drawing:

```
mm per px = print width (mm) / canvas width (px)
pt        = mm / 0.352778               (1 pt = 25.4 / 72 mm)
printed pt on a scaled vector page = design pt x (print width / design width)
```

`scripts/units.py` does this and checks a minimum (standard library, Python 3.9 or later):

```bash
python3 scripts/units.py --preset schematic-a4 min --pt 5                  # 5 pt = 31.4 px on 3200 px at 180 mm
python3 scripts/units.py --canvas-px 2400 --print-mm 120 check --min-pt 5 14px 36px   # 14 px = 1.98 pt: LOW, exit 1
python3 scripts/units.py --preset poster-a0 convert 27pt 18pt              # design pt to printed pt (x 0.841)
python3 scripts/units.py --preset schematic-a4 check --min-pt 5 --scan figure.html     # reads font sizes from the file
```

`--scan` reads `font:`/`font-size:`/`ctx.font` px sizes in HTML, CSS and JS, `\fontsize{N}` in LaTeX and
`fontsize=N` in matplotlib. Sizes computed at run time (`${s}px`) are not seen; check those with the rendered output.

| Medium | Canvas and print | Floor | Arithmetic |
|---|---|---|---|
| data figure | panels drawn at printed mm | 5 pt | true size: 1 pt drawn = 1 pt printed |
| schematic, A4 canvas | 3200 px at 180 mm | 5 pt = 32 px | 1 px = 0.05625 mm; 5 pt = 1.764 mm = 31.4 px |
| schematic library | 1830 px at 183 mm | 5 pt = 18 px | 10 px per mm; 1 pt = 3.528 px |
| slide | 1920 px on a 13.333 in slide | 28 px = 14 pt (24 px in name lists) | 2 px = 1 pt |
| poster | 1000 mm design page printed on A0 (841 mm) | 14 pt printed = 16.6 design pt | printed = design x 0.841 |
| web | CSS px at arm's length | 11.5 px chart ticks, 16 px body on phones | none; read on screen |

- **When text is unreadable, give the panel more area; do not raise one font.** The tiers stay uniform across the
  figure.
- **Three size levels per figure, four at most**, counted in the assembled figure, not in the script.
- Schematics use the same 7 / 6 / 5 pt tiers as data figures, computed for the canvas. Both libraries now use an 18 px
  floor (5.10 pt); see the sibling skill, `canvas-schematics/references/print-maths.md`.
- Before a resize, write an old-to-new table for every element class (title, label, legend, point, line), then
  rewrite. The A4 schematic rewrite went from 18 px to the 5 pt floor this way.

## 3. Token tables per medium

Full values, with sources and the components behind them, are in `references/tokens-by-medium.md`; the same values
are machine-readable in `assets/tokens.json`.

### 3.1 Data figure (print)

| Token | Value |
|---|---|
| widths | 89 mm single column, 183 mm double; each panel drawn at its exact printed mm, placed at native scale |
| type | Helvetica Neue Light; tiers 7 / 6 / 5 pt; panel letter 8 pt bold lowercase, no period, one size per paper (owner: `data-figures`); 5 pt floor (values inside cells may drop to about 3.3 pt) |
| text color | `#000000` for all text in print figures, never gray; spines and ticks `#111111`; in-plot notes (n, filters, thresholds) go to the caption |
| ground | transparent in print figures (reads as white), never dark; example tiles on white or off-white `#FEFCF9`, no border, method name above the tile |
| axes | left and bottom spines `#111111` at 0.9 pt, ticks outward (width 0.9, length 3.4), no grid |
| leaders | `#9AA1AA`, 0.3 pt, alpha 0.75 |
| spacing | about 9 mm between columns of small panels on a 183 mm canvas; plot areas aligned, not label boxes |
| legend | outside the plot, tight to its panel, no wider than it, circle markers |
| magnitude | blue ramp `#F1F6FF #C7DCFF #8FB9FF #4D97FF #003FBD` |
| methods | one locked palette (section 4) |
| missing | face `#DDDDDD`, edge `#888888`, hatch `//`, only for a value that cannot exist, defined in the key; a number that was never fetched goes on a fetch list (`data-figures`) |
| output | `bbox_inches=None, pad_inches=0`, 320 dpi PNG beside the PDF, every font embedded (`pdffonts`) |

### 3.2 Schematic (print)

| Token | Value |
|---|---|
| canvas | 3200 px for 180 mm on A4 (1 px = 0.05625 mm), or 1830 px for 183 mm (10 px per mm) |
| type | Helvetica Neue 300 / 400 / 500, never monospace; italic for gene and variable letters |
| floor | 32 px on the 3200 px canvas (5 pt); 18 px on the 1830 px canvas (5.10 pt) |
| tiers, library | bio: letter 29, L1 24, L2 20, L3 18 px; architecture: letter 29, L1 26, L2 21, L3 18 px (letter 29 px = 8.2 pt) |
| titles of a set | one size (44 px in the source); shorten the text rather than shrink it |
| ink | `#2b2b2b` (bio), `#1a1a1a` (architecture); soft `#6b6b6b` only sparingly |
| ground | white; no panel background boxes, no dividers |
| lines | arrows `#999`, 3.5 px, head 16 px; block stroke `#3a3f47` 1.6 px; leaders `#9aa0a6`; points radius 3.0 everywhere |
| architecture colors | four-tone by default: protagonist `#2B50AA`, fills `#9EBEE0`, target `#B8860B`, structure gray; three-accent (`#0B6FB8 #0F8C7A #D97A06`) as the alternative, chosen once per paper, rare fourth `#6D4AA7`; stop-gradient and EMA dashed; owner `canvas-schematics/references/architecture-pack.md` |
| edge pairs | high `#FF9500` / low `#5AC8FA`; positive `#2d911b` solid / negative `#d32f2f` dashed (the dash carries the difference) |
| render | puppeteer at 3x device scale, paired PDF and PNG, wait for a done flag plus 800 ms for fonts |

### 3.3 Slide (projection, dark default)

| Token | Value |
|---|---|
| canvas | 1920 x 1080 px; 2 px = 1 pt |
| colors | ground `#141416`, ink `#F4F4F5` (the only text color), hairline `#34343B`; light variant `#FFFFFF` / `#111111` / `#D0D0D5` |
| type px | name on title slide 150 Medium; title 54 to 58 Medium; line under title 40; body 44 to 48; statement 84 Medium; big number 56 to 96 with unit 32 to 40; labels and legend 28 to 32; band 30 |
| floor | 28 px = 14 pt (24 px in lists of names); no gray text |
| spacing | margins 110 px; title at y = 58; content ends at y = 956; band hairline at y = 990, content 34 px clear; text column 780 px beside a 956 px square |
| words | 25 per slide, 10 per title, 10 per line under it |
| data colors | first-deck accent `#8EC9FF`, warm `#F2A65A`, for data only |

### 3.4 Poster (print, A0)

| Token | Value |
|---|---|
| page | designed at 1000 x 1414.2 mm, placed on 841 x 1189 mm as vector (printed = design x 0.841) |
| type, design pt (printed) | title 88/98 Bold (74); authors 35/42 (29.4); section 46/54 Medium (38.7); abstract 33/42.5 (27.8); body 27/35 (22.7); caption 25/31 (21.0); references 18/22.5 (15.1); big numbers 72 Thin in the accent (60.6) |
| floor | 14 pt printed, checked on the PDF |
| colors | ground white, ink `#1A1A1A`, slate `#4A4F5A` for affiliations, captions and references, one accent (the source used the host's color) |
| spacing, design | margins 3 cm sides, 2 cm top, 1.25 cm bottom; two columns of 45.85 cm with a 2.3 cm gutter; at least 0.2 cm between boxes |
| rules | header and footer 0.2 cm ink, full width; 0.09 cm under each section title; tables booktabs 2 pt and 1.1 pt |
| text | fully justified, `\hyphenpenalty=1000 \exhyphenpenalty=1000`, `\emergencystretch=2em`; key phrases bold plus accent; one boxed core definition (2.2 pt accent rule, accent at 7% fill) |

### 3.5 Web page (screen, dark)

| Token | Value |
|---|---|
| colors | ground `#141416`, ink `#f4f4f5` (names, claims), body `#d2d2d7`, quiet `#8b8b93` (captions), rule `#2e2e34`, link hover `#8cbcf3`, accent `#8ec9ff`, rival `#e69f00`, chart others `#5c5c64`, axis `#3a3a42` |
| type | body 300 18 px / 1.62 (16 on phones); h1 500 54 to 104 px / 0.9, tracking -0.045 em; h2 500 28 to 42 px; claim 500 22 px; caption 13.5 px; chart text 12.5, ticks 11.5 px with tabular figures |
| spacing | column 1080 px, gutter 24 px (16 on phones), bar 60 px, sections 136 px apart (88 on phones), hairline then 26 px |
| shape | 1 px rules; radius 999 px for one call-to-action pill only; shadows only on tooltip and dialog |
| motion | ease `cubic-bezier(.2,.7,.2,1)`, rise 14 px once, 80 ms stagger, charts count up over 1300 ms once 35% is visible; reduced motion draws the final frame |
| footer | logos only, 30 px high, opacity .85 |

Gray text is allowed on the web and banned on slides and in figures. These do not conflict: a page is read at arm's
length, a slide from the back row, and a figure has a caption for everything secondary.

## 4. Color

Detail, the reasoning for each choice and the contradictions resolved are in `references/color.md`.

- **Categories: Okabe-Ito** `#0072B2 #E69F00 #009E73 #CC79A7 #56B4E9 #D55E00 #999999`, extras `#785EF0 #AA4499 #DDAA33`.
  Seven colors at most for arbitrary masks ("keep 7 different and nice colors ... don't go crazy"). A neon lime
  `#76FF03` was replaced by violet `#785EF0`.
- **Lock the method palette for the whole work** (example: ours `#0072B2`, then `#009E73`, `#E69F00`, `#163A5F`, the
  rest gray). No other categorical palette may resemble it: an orange-and-blue role pair was read as two methods.
  Keep the palette in one file that every panel imports.
- **Magnitude: one blue ramp everywhere** (`#F1F6FF` to `#003FBD`, five steps). On a dark page the rank ramp is
  `#b7d3f6 #5598e7 #256abf #1d4f93 #23252d`. Text in a filled cell is `#0b1526` when the fill's luminance is above
  0.2, else `#f1f4f9`.
- **Signed values: blue-white-red with a wide white plateau** (`#0A84FF` to `#FF3B30`, white from 0.43 to 0.57), values
  printed; blue-white-orange `#2166AC #F7F7F7 #D55E00` for a schematic matrix without values or when red means
  something else. Never red-green. The sibling skill owns the map: `data-figures/references/style-tokens.md`.
- **Red means one thing per figure** (in the source: removed, bad, forbidden). Recolor any category that clashes,
  such as a tumor class, to mustard.
- **Hierarchical classes: one hue per major class, its subclasses as lightness shades of that hue, parent darkest.**
  The reader then sees the family before the member (model families and their sizes in a benchmark, cell types and
  subtypes in a tissue map). Classes the claim rests on, and classes that border each other in the data, get hues far
  apart and dark enough to stand out: hues that sat too close to a neighbor were sent back in three separate rounds.
  The `tissue-figures` skill of the biology plugin ships `family_shades` for the spatial case.
- **Separate roles get separate colors**: the object (a recovered fragment, amber) and a raw state (unassigned,
  vermillion) never share a hue.
- **Many tessellating objects get outlines or a light fill** (alpha about 0.2); a solid fill becomes a carpet.
- **Show thousands of categories as gray density with a few in color.** Molecules colored by thousands of genes were
  "such a noise".

## 5. Moving a figure between media

The audience changes the order, the formulas and the amount of background explained. It never changes the type,
palette, figures or animations. `references/media-transfer.md` has each procedure.

| From, to | Treatment |
|---|---|
| paper figure to dark slide | render at 600 dpi (`pdftoppm -png -r 600`), crop to the panel that carries the claim, invert lightness and keep hue (chroma x 1.35, pale fills lifted off the ground); text inside at least 28 slide px |
| paper figure to poster | place unchanged as vector PDF; crop by trim and clip; recolor at most |
| figure to dark web page | draw natively on the page ground; labels on a translucent plate `rgba(20,20,22,.78)` in opposite corners |
| website animation to slide | record frames from a patched local copy (grays to ink, thicker arrows, formulas off), composite on the slide ground, H.264 yuv420p |
| two renders of one view | one picture split by a moving divider, preferred over two panels side by side |
| text over any picture | on a plate in the ground color; outlined text alone was unreadable |

Density by medium: a paper figure is dense and flat (5 to 7 pt, many panels, captions in the caption file); a slide
has one point and one picture; a poster is mostly figures with little verbatim text; a web page opens a few blocks
and folds the rest; a schematic carries a title, at most one subtitle and a small legend.

## 6. What minimal, cleaner and nicer mean

| The request | What to do |
|---|---|
| "cleaner", "more minimal", "less is more" | delete elements inside the existing look; keep typeface, palette, layout grid |
| "nicer", "sexier", "stronger", "cooler" | simpler and bolder: fewer encodings, the biggest thing larger; never add encodings (ten ablation cards for "nicer" were reverted to one heat map: "smells ai") |
| "professional" | aligned grids, equal gaps, nothing overlapping, nothing cut, no runts |
| "bring that back", "the original" | restore that exact file from disk |
| "1.2x", "0.8x", "a tad" | apply exactly that factor; "a tad" is about 1.1x; report the change in the same terms |
| "draw attention to the biggest things" | open the main result, fold the rest behind a click (web), move it to backup (slides) or the supplement (paper) |

Minimal never means removing a result. A weak or mixed result moves to a fold, backup slide or supplement with its
number; a redundant encoding of a number that stays printed elsewhere may go.

## 7. What reads as machine-made

Each of these was removed at the author's request. The full list by medium with its replacements is
`references/machine-made.md`.

- **Layout**: cards with rounded borders, three columns with bold headers, boxes joined by arrows for a method,
  numbered lists with large numerals, stat tiles in a row, a table and a heat map of the same data side by side,
  footers listing every section, panel background boxes.
- **Decoration**: gradients, drop shadows, glow, glass, decorative icons, pill labels, emoji, initials discs for a
  missing photo, neon accents.
- **Text**: taglines, eyebrows and result claims above the title, "·", "•", "|" or "/" between phrases, "A x B x C"
  chains, abstracts and TL;DRs on web pages, key-contribution lists, provenance captions under pictures, an
  accent-colored punchline, ALL-CAPS labels, fake-terminal flourishes, slogans.
- **Type**: gray or small text on slides and in figures, more than four sizes in a figure, a second family.
- **Figures**: legends inside the plot, legends that repeat what rows already say, "†", bold for significance, long
  panel titles (2 to 4 words is the target), dense dot plots, several near-identical bump charts in a row, filled
  translucent shapes where thin outlines show the objects, schematics drawn in matplotlib.

## 8. Check before anything is handed over

1. `python3 scripts/units.py --preset <medium> check --min-pt <floor> --scan <source files>` passes, or the sizes
   it cannot see (computed at run time) are measured on the render.
2. The medium's own overlap check passes (the poster's box and layout checks, the deck audit, the site audit in the
   sibling skills).
3. Grep the sources for text colors: on slides and figures every text color is the ink.
4. Every color in view has a key, and each category has the same color as in the other media of the work.
5. **Look at the render at its final size**: the figure at print width, the slide at 1600 px, the poster at 25%,
   the page at 375 px and 1440 px. Look for a second family, an accent used twice, a lone word, a cut label.
6. Put the render beside the reference artifact. If it does not look like the same work, it is wrong.
7. Say what was not checked (color-blind simulation, a printed proof, the hall projector).

## 9. What was thrown out, and what replaced it

| Thrown out | In the author's words | Replaced by |
|---|---|---|
| ten ablation cards for "nicer" | "go back to simpler versions, a heatmap would just fine" | one heat map |
| a restyle in Arial with new layouts | "what you did before was better" | the first look, polished |
| gray caption lines on slides and figures | "all black for text color" | one ink, 28 px floor on slides, caption file in figures |
| `·` between phrases | "never use AI slop like `·` in between things" | nothing, or one plain sentence |
| a tagline over the title | "cringe and vague and too AI slop" | the name, very large |
| a result claim at the top of the page | "you're more professional than that" | the claim beside its evidence |
| a 3 pt schematic label, then a 75 px (12 pt) floor on the 3200 px canvas | "tiny text (18px)" | the 5 pt floor computed for the canvas |
| paper figures on white plates in a dark deck | "Do not bring white background figs" | the same figures recolored |
| new diagrams for the poster | "I have the most beautiful figures in the paper" | the paper's figures, placed |
| a matplotlib concept schematic | "this is so bad" | a canvas schematic, or none |
| inline labels on ten small panels | rejected; they forced collisions at 5 pt | one shared legend and 9 mm gaps |
| a legend repeating the rows, "†" | "the legend is AI slop", "clear AI slop flag" | row labels; an asterisk |
| dense dot plots | "not obvious what they say" | values shown directly |
| an orange-blue role pair | read as two methods | roles in hues disjoint from the methods |
| neon lime and olive categories | "old neon-lime/olive/double-brown bad" | Okabe-Ito with violet |
| thicker line for the own method | "let the results speak" | same weight, locked hue |
| one hue per gene, thousands of them | "such a noise" | gray density plus marker genes |
| a central crop of an embedding field | read as confetti | the whole sample at 50 to 150 µm |
| outlined text over tissue | not readable | a plate in the ground color |

## Reference files

- `references/tokens-by-medium.md`: every token per medium with its source role, the light and serif variants, LaTeX settings.
- `references/color.md`: palettes, roles, color-blind safety, keys, the contradictions between sources and how they resolve.
- `references/machine-made.md`: the deletions list by medium with replacements, and the vocabulary for bad and good design.
- `references/media-transfer.md`: recoloring for dark grounds, recording animations, density and audience, the static twin.
- `scripts/units.py`: px, mm and pt at a canvas and print width; minimum size check; font-size scan.
- `scripts/palette_check.py`: closest color pairs across and within families, in normal and color-blind views.
- `assets/tokens.json`: all tokens, machine-readable.
