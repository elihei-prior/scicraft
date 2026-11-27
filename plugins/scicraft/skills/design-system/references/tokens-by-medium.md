# Tokens by medium

Every value the author's artifacts used, with the role it plays. The tables in SKILL.md section 3 are the short form;
`assets/tokens.json` holds the same values for scripts. The source of each block is the artifact type it came from
(a project website starter, a talk-deck builder, a conference poster, two canvas schematic libraries, a matplotlib
style module).

## Contents
1. Shared family and weights
2. Data figure
3. Schematic
4. Slide
5. Poster
6. Web page
7. Variants: light deck, light teaching deck, serif homepage, LaTeX document
8. Tables in documents

## 1. Shared family and weights

| Role | Setting |
|---|---|
| stack | `'Helvetica Neue', Helvetica, Inter, Arial, sans-serif` (the web self-hosts Inter as woff2 for machines without Helvetica Neue) |
| text | Light 300 |
| titles, emphasis, names | Medium 500 |
| poster title | Bold 700; poster big numbers Thin 100 |
| figure subtitles (technology names, secondary titles) | Light, smaller; main titles Regular or Bold |
| mono | IBM Plex Mono 400/500, web only: one-line meta facts, fold summaries, code |
| math | Latin Modern Math (`Scale=MatchLowercase`, `mathrm=sym`) or Computer Modern |
| LaTeX (owner of this setup across the package) | `\setmainfont{Helvetica Neue}[UprightFont=* Light, BoldFont=* Medium]` with `fontspec` under xelatex; `helvet` is a clone and looks foreign next to the real face |
| hall computer | a copy of the deck in Arial at 96% of the size keeps the line breaks (`talk-slides` has the script) |
| PDF | every font embedded; check with `pdffonts`; matplotlib may name Helvetica without embedding it, so re-embed |

## 2. Data figure

| Token | Value | Role |
|---|---|---|
| widths | 89 mm, 183 mm | journal single and double column |
| panel size | exact printed mm, from a mock-up with placeholders and panel letters | no stretch or shrink at assembly, so every font is its true pt |
| mosaic | panels in one row share a height; a tall panel may span whole rows; same-kind panels get identical plot boxes | regular grid, never patchwork heights |
| alignment | plot areas (axes rectangles) align, titles center over the axes rectangle | label boxes vary, grids must not |
| tiers | 7 / 6 / 5 pt | title, body, small |
| heat map labels | row labels and titles about 2x the cell text | |
| panel letter | 8 pt (8 to 9) bold lowercase, in a 3.5 mm band above the panels, content starts just after it horizontally | one letter per conceptual row or panel, not per tile |
| figure title (when the figure has one) | at most 6 words, large and bold | |
| panel titles | 2 to 4 words ("Elo rating", "Mean rank by scale", "Change in score") | a y label that says it makes the title unnecessary |
| text | `#000000`, all of it | no gray, no in-plot prose; a single count in a corner may stay |
| spines | left and bottom, `#111111`, 0.9 pt; ticks outward 0.9 wide, 3.4 long; axes lw 0.95 | |
| grid | none; a faint 0.3 to 0.4 pt gray guide only where needed | |
| bars | thin (a third of the slot or less), no border, vertical; error bars show the IQR for descriptive strips | |
| dots with intervals | a dot with its 95% whisker and the value printed; never a stem from the axis origin | |
| legend | outside the plot, below or right, left-aligned to the panel and no wider than it; circle markers; entries in the order of the stack; a mask glyph is an irregular cell shape | |
| shared legend | when the same series repeat across small panels: one legend, about 9 mm gaps between 26 mm boxes on 183 mm | inline labels at 5 pt collided |
| scale bars | one helper; same drawn length and position in every panel, only the number changes; on the reference tile only | |
| leaders | `#9AA1AA`, 0.3 pt, alpha 0.75 | |
| tradeoff scatter | background `#2CA25F` at alpha 0.05, diagonal `#5A5A5A` 1.0 pt alpha 0.48 | |
| scale bracket ends | at least 0.8 mm | |
| example tiles | white or off-white `#FEFCF9`, no border, method name above the tile | a dark tile background was rejected |
| faint guide | a dashed ring or a light density cloud when a structure is not legible at panel size | |
| dpi | 220 on screen, 320 on save; `bbox_inches=None, pad_inches=0` | |
| composer | places panel PDFs at exact mm (`keep_proportion=True`); matched panels share one scale; captions live in the caption file | |

Reference figure: name one figure per paper as the gold standard, profile its constants (tile mm, font pt, frame
color and width) and compare each new panel against it. `data-figures` holds the plotting module.

## 3. Schematic

Two coordinate contracts were in use. Pick one per figure and size all type from it. Both use the 7 / 6 / 5 pt tiers of
the data figures with a 5 pt floor, computed for the canvas (`canvas-schematics/references/print-maths.md` owns them).

| Contract | Canvas | Print | Conversion | Floor |
|---|---|---|---|---|
| A4 template | 3200 px | 180 mm | 1 px = 0.05625 mm; 5 pt = 1.76 mm = 31.4 px | 5 pt floor (32 px) |
| figure library | 1830 px | 183 mm | 10 px per mm; 1 pt = 3.53 px | 5 pt floor (18 px = 5.10 pt; an older 17 px L3 printed at 4.82 pt) |

| Token | Value |
|---|---|
| tiers, bio library | letter 29 px (8.2 pt), L1 24, L2 20, L3 18 |
| tiers, architecture library | letter 29 px (8.2 pt), L1 26 (7.5 pt), L2 21 (6 pt), L3 18 |
| family | Helvetica Neue 300/400/500; italic for gene and variable letters; a grid mode drops bold |
| ink | `#2b2b2b` bio, `#1a1a1a` architecture; soft `#6b6b6b` sparingly |
| titles in a set | all one size (44 px in the A4 template); shorten text, never shrink |
| numbered steps | a numbered circle inline left of the title, same baseline |
| cell pastels {fill, mark, boundary} | orange `#fadbb2 #ea9f37 #d66a2b`; blue `#d9eefb #3498db #2980b9`; green `#c1e1c1 #489e34 #2d911b`; mustard `#fbf2d9 #f1c40f #b38822`; teal `#d1efe8 #46a596 #138774`; lavender `#e4d5f0 #8e5db8 #6e3d9e`; rose `#f8d9e6 #d83a73 #b62e5f` |
| cells | few, soft, organic (Voronoi or a smoothed blob), a white halo between touching cells, a nucleus dot, scattered points |
| masks | gray dashed outline, or a colored organic polygon; never circles |
| noise points | `#999` / `#9aa0a6`; point radius 3.0 everywhere |
| arrows | `#999`, 3.5 px, head 16 px (`#bbb` was too faint) |
| edges | similarity high `#FF9500`, low `#5AC8FA`; positive `#2d911b` solid, negative `#d32f2f` dashed |
| architecture blocks | fills `#f4f6f8 #e9f1fb #e6f3f0 #fdf1df #efeafb`; stroke `#3a3f47` 1.6 px; flat, no shadow, no gradient; token squares radius 1.5 px; leaders `#9aa0a6` |
| architecture semantics | the role palette by default: ink outlines `#333333` (chips `#404040`), token fills `#93B4D8 #F0B060 #B9A3DC #8FBFA0 #F5D36B` that each name a kind of token, operation fills peach `#FBE0C2` and mint `#D8E9DF`, module gray `#E8E8EC`, card frame `#B2B2B2`, secondary text 70% black, the loss in red `#D93025` on `#FBE9E7` as the one saturated mark (`tikz-figures` owns these values); three-accent as the named alternative, chosen once per paper: method or student `#0B6FB8`, teacher or EMA `#0F8C7A`, target `#D97A06`; violet `#6D4AA7` rarely; stop-gradient and EMA dashed (`canvas-schematics/references/architecture-pack.md` owns the canvas themes) |
| heat maps inside | the blue ramp; a signed matrix drawn without values may use blue-white-orange `#2166AC #F7F7F7 #D55E00`; with values printed, blue-white-red with a wide white plateau |
| layout | no panel background boxes, no dividers |
| render | one HTML file with one function per figure; puppeteer viewport at the canvas width, `deviceScaleFactor: 3`, wait for a done flag and 800 ms more for fonts, PNG screenshot and `page.pdf` at the same px size with zero margins; `protocolTimeout: 120000` for large canvases |

Default to no schematic when the data panels carry the story. `canvas-schematics` and `tikz-figures` build them.

## 4. Slide

| Token | Value |
|---|---|
| canvas | 1920 x 1080 px; 30 px = 15 pt |
| ground, ink, hairline | `#141416`, `#F4F4F5`, `#34343B` |
| title slide name | 150 px Medium |
| title | 54 to 58 px Medium, a full sentence of at most 10 words |
| line under title | 40 px Light |
| body sentence | 44 to 48 px Light |
| statement slide | 84 px Medium, width 1300 px, centered between top and band |
| big number / unit | 56 to 96 / 32 to 40 px Light |
| labels, legend | 28 to 32 px Light; legend dot 26 px |
| names / name lists | 26 to 28 px Medium / 24 px |
| floor | 28 px (24 px in name lists) |
| band | hairline at y = 990, 30 px, Medium for section and page; section left, event with place and date center, host logo, page n/N far right; no fill |
| margins | 110 px left and right; title at y = 58; content ends at y = 956 |
| layouts | column 780 px plus a 956 x 956 square at (964, 0); title plus one picture; title plus an equal grid; statement |
| plate label | 30 px Medium on a ground-colored plate, 18 px padding |
| portraits | round crop from a 420 px source; QR code 900 px |
| transition | plain fade |
| clips | H.264 yuv420p, even sizes, CRF 18 to 22, 24 to 30 fps, smoothstep easing, 1 s holds at both ends |
| stills | 2 px per slide px; PDF pages at 3840 px; JPEG quality 92 without chroma subsampling |

`talk-slides` holds the builder and the audit that enforces these.

## 5. Poster

Design page 1000 x 1414.2 mm (A0 aspect), placed on 841 x 1189 mm with `\includepdf` so nothing is rasterized. Every
design size prints at 0.841 of itself. An earlier poster canvas was 100 x 130 cm.

| Role | Design pt | Printed pt | Face |
|---|---|---|---|
| title | 88/98 | 74 | Bold; accent on the name and the coined term |
| authors | 35/42 | 29.4 | Light; own name underlined |
| affiliations | 23/29 | 19.3 | Light, slate |
| section title | 46/54 | 38.7 | Medium |
| abstract | 33/42.5 | 27.8 | Light, justified |
| body | 27/35 | 22.7 | Light, justified |
| caption | 25/31 | 21.0 | Light, slate |
| brace labels in math | 22/26 | 18.5 | slate |
| big numbers | 72 | 60.6 | Thin, accent |
| references | 18/22.5 | 15.1 | slate |
| floor | | 14 | checked on the PDF |

| Token | Value |
|---|---|
| ink, slate, accent | `#1A1A1A`, `#4A4F5A`, one accent (the host's color in the source) |
| margins | 3 cm sides, 2 cm top, 1.25 cm bottom (design) |
| columns | 2 x 45.85 cm, gutter 2.3 cm, full width 94 cm |
| rules | header and footer 0.2 cm ink, full width; 0.09 cm under each section title; 0.75 cm below each piece |
| clearance | at least 0.2 cm between any two boxes, checked from logged box coordinates |
| tables | booktabs, heavy 2 pt, light 1.1 pt, `\arraystretch` 1.28 |
| boxed definition | `\fcolorbox{accent}{accent!7}`, rule 2.2 pt, separation 0.27 cm; one per poster |
| text | fully justified ("same length every line"), `\hyphenpenalty=1000 \exhyphenpenalty=1000` (5000 left loose lines), `\emergencystretch=2em`; no runts, no hyphenated bold titles |
| content | mostly the paper's own figures placed unchanged; verbatim text; no white holes beside figures; bottom columns end level |
| footer | run-on references above the footer rule, contacts on one line |

`poster` holds the template and the box and layout checks.

## 6. Web page

| Token | Value | Role |
|---|---|---|
| `--bg` | `#141416` | equals the ground of the data renders |
| `--ink` | `#f4f4f5` | names, claims, the opening claim |
| `--body` | `#d2d2d7` | sentences |
| `--quiet` | `#8b8b93` | captions, labels, meta |
| opening statements | `#86868e` | a few statements in gray, then the main claim in ink |
| `--rule` | `#2e2e34`, 1 px | section hairline |
| link hover | `#8cbcf3` | |
| `--ours` | `#8ec9ff` | the one accent; progress line, the method's bars and rows |
| `--rival` | `#e69f00` | the strongest comparator, when one is named |
| chart others, axis | `#5c5c64`, `#3a3a42` | |
| loss ramp | `#184f95 #256abf #5598e7 #b7d3f6` | |
| body text | 300 18 px / 1.62; 16 px on phones; bold is 500 | |
| h1 | 500 clamp(54px, min(7.2vw, 13vh), 104px) / 0.9, tracking -0.045 em, white | the name |
| subtitle | 300 clamp(18px, 1.72vw, 24px) / 1.28 | rest of the title |
| h2 | 500 clamp(28px, 3.3vw, 42px) / 1.08, tracking -0.028 em | |
| opening, main claim | 300 clamp(22px, 2.6vw, 34px) / 1.3 | |
| claim | 500 22 px / 1.3 | |
| big numbers | 300 clamp(34px, 4.6vw, 60px), tracking -0.035 em; the winning one 700 in the accent | |
| caption | 13.5 px quiet | |
| chart text, ticks | 12.5 px, 11.5 px, tabular figures | |
| mono meta | 400 12 px | |
| column, gutter | 1080 px, 24 px (16 px on phones) | |
| bar | 60 px (50 on phones); blurred backdrop after scroll; 1 px progress line in the accent | |
| section rhythm | 136 px top padding (88 on phones); hairline then 26 px; results 104 px apart | |
| radius | 999 px for the call-to-action pill only | |
| shadows | tooltip and dialog only | |
| motion | `cubic-bezier(.2,.7,.2,1)`; rise 14 px once; 80 ms stagger; charts 1300 ms ease-out cubic from 35% visible; only headings, numbers and statements animate | |
| folds | native `<details>`, a plus that turns into a minus; never nested, never open by default | |
| footer | logos only, 30 px, opacity .85 | |
| line breaks | `text-wrap: balance` on short blocks; `&nbsp;` before the last two or three words of longer ones and between number and unit | |

`paper-website` holds the starter that implements these.

## 7. Variants

**Light deck.** Ground `#FFFFFF`, ink `#111111`, rule `#D0D0D5`, every other slide rule unchanged. Pictures of
fluorescence on black need a deliberate frame; clips meant for a white slide are whitened to pure white (encoded
white decodes as 253 and shows as a box).

**Light teaching deck** (an earlier Markdown deck): Helvetica Neue Light, near-black ink, one orange accent
`#d66a2b`. Its cards, uppercase eyebrows, numbered steps and pills are on the later machine-made list; keep the
type and the single accent, drop those.

**Serif personal homepage.** The one place the author left Helvetica Neue, for a personal site: paper `#fcfdfe`,
ink `#242424`, secondary `#585858`, link `#296b9f` (hover `#1d517a`), hairline rgba(36,36,36,.10); Source Serif 4 for text (fallback Georgia), Inter 400/500/600 for interface text only;
oldstyle figures for dates; italic for venue and book titles; one quiet animated motif behind the prose
(`#6ea8d4`/`#93c1e2`) that honors reduced motion. Treat it as an example of a personal brand, not a default.

**LaTeX document.** One accent for links, citations and box rules, ink and grays for the rest:
`\hypersetup{colorlinks=true,citecolor=accent,linkcolor=accent,urlcolor=accent}`. Accents in use: muted green
`#26735B` with pale `#F2F8F5` and rule `#BFD8CD`, ink `#202020`, soft `#616161`; teal `#228B8B`; navy `#1C2449` with
link blue `#3A5BA6` and box tint `#F2F4F9`. A box is a pale tint of the accent with a 1.6 to 2 pt left rule, frame
hidden, sharp corners. In a citation-dense document give citations the darker shade. A venue submission keeps the
venue's typography and adds only accent links and callouts. Revision marking uses one blue (RGB 70,130,180) for all
changes, never a color per round. `latex-typesetting` has the preamble.

## 8. Tables in documents

From a benchmark table in a submitted paper: booktabs; `\scriptsize`; group rows as an italic label spanning the
width instead of a category column repeated down every row; rank fills first `#D3ECE3`, second `#D8EBFF`, third
`#FDEDCE` plus a superscript rank; ± SD in tiny gray (`black!62`); direction arrows in the header ("mean rank ↓",
"Elo ↑"); bold only when the adjusted p is below the stated threshold, and that rule applied to every cell alike;
narrow text columns ragged-right (below about 40 characters justification leaves holes). On a poster the rank text
colors were first `#08704D`, second `#0064C8`, third `#9A6200`. The rank fills are pale and carry a printed rank, so
they do not depend on hue alone.
