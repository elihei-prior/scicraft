# QC checklist

Run in this order. Scripted gates first, then eyes, then the report.

## Scripted

| Gate | Command | Passes when |
|---|---|---|
| region contract and anti-slide | `python3 scripts/lint_regions.py code/regions/ --layout code/layout.js --main code/main.js` | 0 errors; each warning fixed or justified |
| text floor and overlaps | `node code/render.js figure.html figN 1830 <H> .. --check` | exit 0: no text under 18 px, no overlapping text, no page or region errors |
| aspect ratio | `python3 scripts/ref_crops.py reference.png --canvas 1830x<H>` | within 2 % of the reference |
| print sizes | `python3 scripts/print_maths.py --width-mm 183 --px <sizes used>` | nothing under the floor |
| outputs | the PNG is W x S by H x S px; the PDF is one page of W/10 by H/10 mm (within 0.1 mm) | both regenerate from one command |
| font | `render.js` printed no Helvetica Neue warning | or the fallback was accepted knowingly |
| clearance on ink | `python3 scripts/check_clearance.py figN.pdf [--panel-gap 9 --col-gap 6 --row-gap 5]` | 0 fails; every warning looked at in its `_clearance.png` |
| color separation | `python3 <design-system>/scripts/palette_check.py families.json` | no two meanings closer than about 20 in normal vision; the color-blind closest pairs read and accepted |

`render.js --check` compares text boxes with text boxes only. It cannot see a label running onto a tile, an ellipsis
pressed against its neighbors (0.08 mm in one figure), or two panels 1.5 mm apart. `check_clearance.py` renders the
PDF twice, as printed and with the text removed, so that it can measure text ink against graphic ink. It also
measures the white between ink islands and the widest white bands between panels and table columns. The
`_islands.png` it writes colors each island apart; two objects that touch show as one color.

## With eyes

Open the full PNG, then each region cropped at 2 to 3 times zoom.

- [ ] It belongs beside the paper's data figures: same density, flatness, near-black labels, ramp, type.
- [ ] Nothing on the anti-slide list (`references/paper-not-slide.md`).
- [ ] Nothing overlaps: blocks, arrows across labels, text against borders, text covered by a later
      shape (the script cannot see that last one).
- [ ] Every arrowhead the same shape; one dominant flow direction.
- [ ] Panel letters bold lowercase without a period, titles left-aligned on the same baseline, all
      titles one size.
- [ ] Every color that means something is in a legend or labeled on the object; one accent, one meaning.
- [ ] Each region matches its `ref_crops/orig_<id>.png` arrangement, where a reference exists.
- [ ] The mechanism is drawn as the operation and matches the code and the paper's notation.
- [ ] Illustrative geometry carries no exact-looking ticks or values; real data panels name their source.
- [ ] Biology: cells with character, organic masks, dot radius 3.0 throughout, colors consistent
      across panels, one scene.
- [ ] Three render-and-look rounds found nothing new.

## The report

Say what was delivered (paths and sizes), what each gate returned, and what was not checked: for
example that the figure was never seen in the compiled paper, that Helvetica Neue was missing on the
render machine, or that the mechanism was not compared with the code. A rename or a relabel is not
done until every rendered file is rebuilt; search the rendered sources and the PNG, not only the docs.
