# Changelog

All notable changes to this project are recorded here. Versions follow
[semantic versioning](https://semver.org/).

## 0.1.0 (release candidate)

First release of the general part: 40 skills in two plugins (research craft and
machine learning), with scripts, templates and test cases.

- Distilled from one researcher's year of work with Claude Code.
- Audited item by item against the source records, then repaired.
- Checked by an independent pass for private or unpublished material.

Changed since the first candidate (26 Nov 2026):

- `tikz-figures` was rewritten from scratch in one style, the look of the author's
  latest paper figures: Computer Modern type, white hairline boxes with one pastel
  operation box per block, token stacks, cards named on their top border, a training
  overview with one loss box, a hierarchy panel, a unit sphere, composed panels with
  data tiles. It now ships a Python kit and generators for real geometry, a layout
  audit that reads the compiled PDF, a print-scale check, and seven example figures
  that one script builds and checks. Its earlier four-tone sans theme and the serif
  twin are gone.
- `canvas-schematics`: the default theme of the architecture pack is `pastel`, the
  role palette of those figures. The `three-accent` theme is unchanged.
- `design-system`: the architecture colors are that role palette, and TikZ figures
  are set in the TeX default font.
