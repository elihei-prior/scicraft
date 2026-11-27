# Third-party material

No code in this folder comes from someone else. The preamble, the kit, the scripts, the examples, the recipes and
the eval files were written for this skill. The audit, the print-scale check, the composer and the generators
generalize scripts the author wrote for the figures of their latest paper; `render_figure.py`,
`check_tikz_safety.py` and `compile_snippets.py` are rewritten from the previous version of this skill, which was
also the author's. The eval inputs (`pool_block.py`, `scan.csv`) were written and generated with a seed for the
evals.

| Item | Where it is used | Source | License or status |
|---|---|---|---|
| Okabe-Ito colors `#0072B2` and `#E69F00` (`hero`, `rival`) | `assets/preamble.tex`, plot recipes | Okabe and Ito, "Color Universal Design" (2008), through the sibling skill `data-figures` | color values, free to use; credited here |
| the sequential ramp `ramp1` to `ramp5` | `assets/preamble.tex`, the heat matrix recipe | the sibling skill `data-figures` (its five-step rank ramp) | color values from the same package |
| Computer Modern `cmr10` | baked scale-bar labels of `scripts/tiles.py` | shipped inside matplotlib's own data folder | not copied into this skill; used under matplotlib's distribution |

Ideas credited, with no text or code copied:

| Source | What was learned |
|---|---|
| Patrick-Healy/tikz-diagrams-skill (GitHub) | a static check before compiling; the render-and-inspect loop; the exact-versus-schematic distinction; a bounded repair loop (credit carried over from the previous version of this skill) |
