# SPEC: [figure name]

The builder contract for this figure. Every region builder reads it before writing code.

## Figure

- Caption (written first): [one bold claim title, then one sentence per panel]
- Printed width: [183] mm, canvas [1830] x [H] px, device scale 3
- Reference: [path or "none"], aspect ratio [1.42], crops in `ref_crops/`
- House figures to match: [paths of the paper's finished figures]
- Packs: [arch | bio | both]; theme: [pastel | three-accent]
- Flow direction: [left to right]

## Rules (all regions)

- Draw only through `PAL`, `FONT`, `LIB`, `SCENE` and your data global. No hex, no font strings, no
  literal sizes. Never draw the panel letter or title. Stay inside your rect.
- Three tiers: L1 25 px, L2 21 px, L3 18 px (floor). All text black (`PAL.ink`); a secondary gloss is a lighter weight, never gray.
- Flat only: no shadows, gradients, pills, cards with text, second title size, banners, dividers,
  sentence titles, arrow narration, caption text inside the image.
- One accent, one meaning: [method color = ..., target color = ...].
- Render your preview with `--check`, open it beside your crop, fix the smallest defect, three times.
- `python3 lint_regions.py regions/region_<id>.js` must report 0 errors.

## Mechanism traps (trap, then correct depiction)

| Trap | Correct depiction | Source in code |
|---|---|---|
| [arrow labeled "attention"] | [Q from x, K and V from y, softmax, weighted sum] | [file:function] |

## Regions

### [a]: [title of at most four words]

- Rect: x [..], y [..], w [..], h [..]
- Shows: [content, in order of reading]
- Notation: [symbols exactly as in the paper]
- Data: [window.PANEL_A from _prep/build_panel_a.py, or "none"]
- Target: `ref_crops/orig_a.png`
- Left out on purpose: [..]

### [b]: [title]

- ...

## Deviations from the reference

- [region]: [what changed and who asked]
