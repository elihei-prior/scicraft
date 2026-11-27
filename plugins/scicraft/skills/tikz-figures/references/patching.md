# Patching: a figure whose source is lost, and an author's hand-made file

Two jobs that look like redrawing and are not. When a figure's source is lost, the original PDF is the artwork:
include it at natural size and paint only the edits on top. When the author drew a file by hand, it is theirs:
change only the entries asked for, by exact text. A pass that rewrote a panel in words and moved its encoders was
rejected ("super ugly encoders, do not drift from the previous version so much") and rolled back.

**Contents**
1. A figure whose source is lost
2. Measuring what to cover and where to re-set
3. Cutting a column narrower
4. Registration: bp, and one offset for everything
5. The text layer keeps what the paint hides
6. An author's hand-made file: exact-entry patches
7. Versions and rollback

## 1. A figure whose source is lost

The source's hierarchy panel existed only as a compiled PDF. It was included at natural size and three edits were
painted on: a removed block was covered and its wire redrawn across the gap, the level labels were re-set larger at
the original baseline offsets, and three boxes were redrawn at one size on one axis. Everything else stayed the
original artwork, path for path.

```latex
\begin{tikzpicture}[x=1bp, y=1bp, paper]
  % the artwork at natural size; in a real patch:
  %   \node[anchor=north west, inner sep=0pt] at (0,0) {\includegraphics{original.pdf}};
  \begin{scope}
    \node[box, minimum width=46bp, minimum height=23bp] at (60,-30) {old};
    \draw[wire] (0,-30) -- (36,-30);
    \node[anchor=base west, font=\fNote] at (110,-34) {retired label};
  \end{scope}
  % audit-accept: TEXT/TEXT 'retired'  # the wiped label stays in the text layer under the paint (section 5)
  % audit-accept: TEXT/TEXT 'label' x 'label'  # the same
  % audit-accept: TEXT/TEXT 'old'  # the wiped box name, the same
  % audit-accept: OVERLAP h at  # the old box's outline lies under the wipe and under the redrawn box
  % audit-accept: OVERLAP v at  # the same
  % wipe what changes, a little larger than it (0.6 bp around a glyph's box, more around a stroked box)
  \fill[white] (36.5,-42.2) rectangle (83.6,-17.8);
  \fill[white] (109.4,-37.5) rectangle (203,-22.5);
  % redraw the box on its own center line with its new name; re-set the label at the measured origin
  \node[box, minimum width=46bp, minimum height=23bp] at (60,-30) {block};
  \node[anchor=base west, font=\fNote] at (110,-34) {new label};
\end{tikzpicture}
```

## 2. Measuring what to cover and where to re-set

```python
import fitz
page = fitz.open("original.pdf")[0]
for b in page.get_text("dict")["blocks"]:          # every glyph run: its box, its baseline origin, font, size
    for line in b.get("lines", []):
        for s in line["spans"]:
            print(s["text"], s["font"], round(s["size"], 2), [round(v, 2) for v in s["bbox"]], s["origin"])
for d in page.get_drawings():                      # boxes, wires, fills: rect, color, width
    print(d["rect"], d.get("fill"), d.get("color"), d.get("width"))
```

- **Re-set text at the measured origin** (`anchor=base west` at the span's origin), at the measured size or a stated
  multiple of it; keep the original's baseline offsets between lines. The source re-set its level labels at twice
  their size about the same center line, its gray size line still gray.
- **Wipe 0.6 bp around a glyph's box** and a little more around a box (the stroke is half outside the path).
- **One size for every box after the patch**: the source's redrawn boxes took the measured size of one of them
  (45.36 x 22.68 bp) and its center line, so they stacked on one axis.

## 3. Cutting a column narrower

To narrow a panel, include the artwork in clipped pieces and butt them together, removing a vertical band:

```latex
% keep [0, 507] and [549, 625] of a 625 bp panel: the band 507 to 549 bp goes
% \node[anchor=north west, inner sep=0pt] at (0,0)   {\includegraphics[trim=0 0 615.562 0, clip]{original.pdf}};
% \node[anchor=north west, inner sep=0pt] at (507,0) {\includegraphics[trim=549 0 497.562 0, clip]{original.pdf}};
```

- **Cut only through a band crossed by horizontal segments and no text**, and prove it on the content stream
  before cutting: a vertical or diagonal segment in the band would be severed.
- **Paint over the seam.** Two clip edges on one coordinate leave a one-sample antialiasing seam in every
  rasterizer; a white strip 1 bp wide over the join hides it, and the wires that cross it are redrawn whole.
- **Leave room**: a first band left a row of chips 2.7 bp from a rail ("too tight"); the cut moved 10 bp.

## 4. Registration: bp, and one offset for everything

- **Draw the patch in bp** (`x=1bp, y=1bp`). A TeX point is 0.375 percent smaller than a bp, enough to slide a
  patch off the artwork it is meant to cover.
- **Measure the offset between the redraw and the artwork at high resolution** (the source rendered at 2400 dpi,
  where a pixel is 0.03 bp) and apply it as ONE constant to every redrawn element: wires, boxes, chips and wipes
  move together. The source found its redraw 0.21 bp off; at a 0.6 bp stroke that is a third of the line width,
  and it showed as a kink in every rail where the redraw met the original.

## 5. The text layer keeps what the paint hides

A white rectangle hides text from the eye and not from `pdftotext`: the patched source figure still carried, in
its text layer, the wiped labels and the whole old panel that the clip had cut away, including labels that had been
removed because they were wrong. Run this on every patched figure:

```bash
pdftotext figure.pdf - | grep -i -E 'retired name|removed label|old title'
```

If something hidden must not be readable (a retired name, an unpublished detail, a superseded number), crop the
source PDF to the visible region before including it, or redraw the panel. Keep the line audit off a patched
figure (its clipped-away paths are still in the page) and check its re-set text with
`scripts/audit_layout.py figure.pdf --only text --region x0,y0,x1,y1`.

## 6. An author's hand-made file: exact-entry patches

Patch by exact text, never by counting lines. The source's patch script kept a list of (old, new) pairs and
asserted that each old text occurred exactly once before replacing it; an earlier attempt that removed lines by
count asserted on the wrong lines and silently left the file unchanged.

```python
EDITS = (
    (r"\node[] at (3.20,6.83) {multi-scale\\context encoder};",
     r"\node[font=\fB] at (3.20,6.83) {context\\encoder};"),
    (r"\node[] at (6.56,7.11) {ema};", r"\node[] at (6.56,7.11) {EMA};"),
)
text = src.read_text()
for old, new in EDITS:
    assert text.count(old) == 1, f"not found exactly once: {old[:60]}"
    text = text.replace(old, new, 1)
dst.write_text(text)
```

- **A generator kept as long raw strings** (a dossier, a caption bank) is patched with exact substrings too, and
  checked with `ast.parse` afterwards: a replacement that wrote `\"` into a raw string broke it silently.
- **Change the wording to the paper's, not the code's**, and report a disagreement between them to the author
  instead of choosing one.

## 7. Versions and rollback

Keep every accepted version reachable (`_v2`, `_v3`, a folder of earlier designs). When a revision drifts, roll
back to the last accepted one and apply only the asked change ("the previous b was way better"; "go back roll
back"). Show the PNG of each version the author is judging; they cannot judge a description.
