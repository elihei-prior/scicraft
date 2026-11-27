#!/usr/bin/env python3
"""figkit: draw paper-style figures from Python and emit TikZ in PDF big points.

Figures with many aligned parts (block cards, the rows of a hierarchy, anything with shared stations) are easier
to get right from code than by hand. The kit reads every size from assets/preamble.tex (the lines of the form
\\newcommand\\figName{number}) and writes TikZ that uses the preamble's own color names and styles, so a figure
drawn here and one written by hand look the same. Change a value in the preamble and both follow.

Coordinates are bp (PDF big points), x to the right and y DOWNWARD from the top of the figure, as the source
generators measured them; the writer flips y. The page is exactly the figure (border 0, an explicit bounding box),
so a coordinate in the generator is the coordinate in the compiled PDF and an audit finding maps back to the code.

Two passes for card names. A card's name sits on its top border with the border masked behind the glyphs. The mask
must clear the name's ink, which only the compiled PDF knows, so build() compiles once without masks, measures each
name's ink from the PDF (PyMuPDF when installed, otherwise poppler's pdftotext -bbox), then writes the masks and
compiles again. It also reports whether each name fits its card.

There is no module state: a Style (sizes) and a Stations table (shared y values) travel with each Figure, and a
wider card is Style.from_preamble().scaled(...), never a rebinding of globals.

Standard library only for emitting. Measuring needs PyMuPDF or pdftotext; compiling needs pdflatex.

Usage:
    python3 figkit.py --tokens                 # the numbers read from the preamble
    python3 figkit.py --tokens --preamble P    # from another copy of the preamble
The worked example that rebuilds a two-card figure is examples/block_cards.py next to this file.
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Callable, Iterable

HERE = Path(__file__).resolve().parent
PREAMBLE = HERE / "preamble.tex"
TOKEN_RE = re.compile(r"^\\newcommand\\fig([A-Za-z]+)\{([-\d.]+)\}", re.M)


# ---------------------------------------------------------------------------------------------- the preamble
def read_tokens(preamble: Path = PREAMBLE) -> dict:
    """Every \\newcommand\\figName{number} line of the preamble, as {'BoxW': 92.0, ...}."""
    return {m.group(1): float(m.group(2)) for m in TOKEN_RE.finditer(Path(preamble).read_text())}


def preamble_text(preamble: Path = PREAMBLE) -> str:
    """Everything above the line that starts with %%%% FIGURE BODY: the preamble without its smoke test."""
    text = Path(preamble).read_text()
    m = re.search(r"^%%%% FIGURE BODY", text, re.M)
    if not m:
        raise ValueError(f"{preamble}: no line starts with %%%% FIGURE BODY")
    return text[:m.start()]


def header(preamble: Path = PREAMBLE, border_bp: float | None = 0.0) -> str:
    """The preamble and \\begin{document}. border_bp sets the class border (0 for an exact page whose
    coordinates are the generator's); None keeps the preamble's own."""
    head = preamble_text(preamble)
    if border_bp is not None:
        head = re.sub(r"\\documentclass\[border=[^\]]*\]", f"\\\\documentclass[border={border_bp:g}bp]", head, 1)
    return head + "\\begin{document}\n"


@dataclasses.dataclass(frozen=True)
class Style:
    """Sizes of the card family (bp; line widths and type in TeX pt)."""
    box_w: float
    box_h: float
    op_w: float
    op_h: float
    box_r: float
    card_r: float
    head_l: float
    head_w: float
    join_r: float
    dot_r: float
    chip: float
    chip_gap: float
    chip_cols: int
    stack_rows: int
    stack_off: float
    mini: float
    mini_gap: float
    name_inset: float
    name_drop: float
    lw_card: float
    lw_chip: float
    lw_wire: float
    lw_res: float
    lw_mini: float
    pt_name: float
    pt_cap: float
    pt_box: float
    pt_note: float

    @classmethod
    def from_preamble(cls, preamble: Path = PREAMBLE) -> "Style":
        t = read_tokens(preamble)
        return cls(box_w=t["BoxW"], box_h=t["BoxH"], op_w=t["OpW"], op_h=t["OpH"], box_r=t["BoxR"],
                   card_r=t["CardR"], head_l=t["HeadL"], head_w=t["HeadW"], join_r=t["JoinR"], dot_r=t["DotR"],
                   chip=t["Chip"], chip_gap=t["ChipGap"], chip_cols=int(t["ChipCols"]),
                   stack_rows=int(t["StackRows"]), stack_off=t["StackOff"], mini=t["Mini"],
                   mini_gap=t["MiniGap"], name_inset=t["NameInset"], name_drop=t["NameDrop"],
                   lw_card=t["LwCard"], lw_chip=t["LwChip"], lw_wire=t["LwWire"], lw_res=t["LwRes"],
                   lw_mini=t["LwMini"], pt_name=t["PtName"], pt_cap=t["PtCap"], pt_box=t["PtBox"],
                   pt_note=t["PtNote"])

    def scaled(self, **changes) -> "Style":
        """A copy with some sizes changed together (a wider card for a main-figure slot)."""
        return dataclasses.replace(self, **changes)

    @property
    def tok_w(self) -> float:
        return self.chip_cols * self.chip + (self.chip_cols - 1) * self.chip_gap


@dataclasses.dataclass(frozen=True)
class Stations:
    """Vertical stations shared by every card of a figure (y downward from the figure top, bp).

    The defaults are the source's: every card of a figure uses one table, so their blocks align."""
    top: float = 10.0
    mini: float = 20.0
    cap: float = 54.0
    sub: float = 69.0
    stack: float = 106.0
    tap: float = 122.0
    ln1: float = 154.0
    conv: float = 184.0
    qklbl: float = 195.0
    att: float = 218.0
    note: float = 250.0
    add1: float = 268.0
    ln2: float = 298.0
    ffn: float = 334.0
    add2: float = 366.0
    pool: float = 396.0
    inj: float = 426.0
    out: float = 458.0
    outcap: float = 484.0

    def replace(self, **changes) -> "Stations":
        return dataclasses.replace(self, **changes)


# ---------------------------------------------------------------------------------------------- the figure
class Figure:
    """One tikzpicture in bp with y downward. Every primitive appends TikZ to self.o."""

    def __init__(self, width: float, height: float, style: Style | None = None,
                 preamble: Path = PREAMBLE, names: dict | None = None):
        self.w, self.h = float(width), float(height)
        self.preamble = Path(preamble)
        self.s = style or Style.from_preamble(self.preamble)
        self.names = dict(names or {})        # card name -> measured ink width (bp), from the first pass
        self.cards: list = []                 # (ox, top, w, name) of every card, for measuring and fit checks
        self.o: list = []

    # ---- basics
    def add(self, s: str) -> None:
        self.o.append(s + "\n")

    @staticmethod
    def p(x: float, y: float) -> str:
        return f"({x:.2f},{-y:.2f})"

    @staticmethod
    def font(pt: float, bold: bool = False) -> str:
        return f"\\fontsize{{{pt:g}}}{{{pt * 1.2:.1f}}}\\selectfont" + ("\\bfseries" if bold else "")

    def text(self, x: float, y: float, s: str, pt: float | None = None, anchor: str = "base",
             gloss: bool = False, bold: bool = False) -> None:
        pt = self.s.pt_cap if pt is None else pt
        col = "glossink" if gloss else "ink"
        self.add(rf"\node[anchor={anchor}, inner sep=0pt, text={col}, align=center, "
                 rf"font={self.font(pt, bold)}] at {self.p(x, y)} {{{s}}};")

    def note(self, x: float, y: float, s: str, anchor: str = "base") -> None:
        """A gloss, wire label or symbol: note size, gloss ink."""
        self.text(x, y, s, self.s.pt_note, anchor, gloss=True)

    # ---- boxes
    def box(self, x: float, y: float, label: str, w: float | None = None, h: float | None = None,
            fill: str = "white", pt: float | None = None) -> tuple:
        """A box centered on (x, y). Every plain box takes one size; returns (top, bottom)."""
        s = self.s
        w = s.box_w if w is None else w
        h = s.box_h if h is None else h
        pt = s.pt_box if pt is None else pt
        self.add(rf"\node[box, fill={fill}, minimum width={w:g}bp, minimum height={h:g}bp, "
                 rf"rounded corners={s.box_r:g}bp, line width={s.lw_wire:g}pt, font={self.font(pt)}] "
                 rf"at {self.p(x, y)} {{{label}}};")
        return y - h / 2, y + h / 2

    def opbox(self, x: float, y: float, label: str, fill: str = "oppeach") -> tuple:
        """The one filled box of a block (attention, pooling, graph layer)."""
        return self.box(x, y, label, self.s.op_w, self.s.op_h, fill)

    # ---- tokens
    def tokens(self, xc: float, y: float, fill: str, rows: int | None = None, cols: int | None = None) -> None:
        """A set of tokens: `rows` rows of `cols` cells stacked behind one another, each row offset up and
        right; (xc, y) is the FRONT row's center. rows=1 is a single token."""
        s = self.s
        rows = s.stack_rows if rows is None else rows
        cols = s.chip_cols if cols is None else cols
        w = cols * s.chip + (cols - 1) * s.chip_gap
        for i in reversed(range(rows)):                   # back rows first
            x0, y0 = xc - w / 2 + i * s.stack_off, y - s.chip / 2 - i * s.stack_off
            for c in range(cols):
                xa = x0 + c * (s.chip + s.chip_gap)
                self.add(rf"\draw[chip, fill={fill}, line width={s.lw_chip:g}pt] "
                         rf"{self.p(xa, y0)} rectangle {self.p(xa + s.chip, y0 + s.chip)};")

    def tok_top(self, y: float, rows: int | None = None) -> float:
        """Top of the BACK row: where an incoming arrow stops."""
        rows = self.s.stack_rows if rows is None else rows
        return y - self.s.chip / 2 - (rows - 1) * self.s.stack_off

    def tok_bot(self, y: float) -> float:
        """Bottom of the FRONT row: where an outgoing arrow starts."""
        return y + self.s.chip / 2

    def tok_right(self, xc: float, rows: int | None = None) -> float:
        rows = self.s.stack_rows if rows is None else rows
        return xc + self.s.tok_w / 2 + (rows - 1) * self.s.stack_off

    def width_brace(self, xc: float, y: float, label: str, rows: int | None = None) -> None:
        """The token width, bracketed over the stack's back row."""
        rows = self.s.stack_rows if rows is None else rows
        bx = xc + (rows - 1) * self.s.stack_off
        top = self.tok_top(y, rows) - 1.5
        self.add(rf"\draw[bracegloss] {self.p(bx - self.s.tok_w / 2, top)} -- {self.p(bx + self.s.tok_w / 2, top)};")
        self.note(bx, top - 8.5, label)

    def depth_brace(self, xc: float, y: float, label: str, rows: int | None = None,
                    clear: float = 2.2, gap: float = 7.0) -> None:
        """The stack's COUNT along its own diagonal, drawn back to front so it bulges away from the stack."""
        s = self.s
        rows = s.stack_rows if rows is None else rows
        x1, y1 = xc + s.tok_w / 2 + (rows - 1) * s.stack_off, y - s.chip / 2 - (rows - 1) * s.stack_off
        x0, y0 = xc + s.tok_w / 2, y - s.chip / 2
        d = clear * 0.7071
        self.add(rf"\draw[bracegloss=0.8bp] {self.p(x1 + d, y1 + d)} -- {self.p(x0 + d, y0 + d)};")
        mx, my = (x0 + x1) / 2 + d, (y0 + y1) / 2 + d
        self.note(mx + gap * 0.7071, my + gap * 0.7071 + s.pt_note * 0.34, label, "base west")

    def brace(self, x0: float, y0: float, x1: float, y1: float, label: str, gap: float = 6.0) -> None:
        """A brace along (x0,y0)->(x1,y1): left to right it bulges up, top to bottom it bulges right."""
        self.add(rf"\draw[bracegloss] {self.p(x0, y0)} -- {self.p(x1, y1)};")
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        if abs(y1 - y0) < abs(x1 - x0):
            self.note(mx, my - gap, label)
        else:
            self.note(mx + gap, my + self.s.pt_note * 0.34, label, "base west")

    # ---- wires
    def arrow(self, x0: float, y0: float, x1: float, y1: float, residual: bool = False) -> None:
        style = "resid" if residual else "wire"
        self.add(rf"\draw[{style}] {self.p(x0, y0)} -- {self.p(x1, y1)};")

    def line(self, pts: Iterable, residual: bool = False) -> None:
        style = "residbare" if residual else "wirebare"
        self.add(rf"\draw[{style}] " + " -- ".join(self.p(*q) for q in pts) + ";")

    def join(self, x: float, y: float) -> None:
        """The join circle with a plus: a residual or any other addition."""
        r, a = self.s.join_r, self.s.join_r * 0.55
        self.add(rf"\draw[ink, fill=white, line width={self.s.lw_wire:g}pt] {self.p(x, y)} circle ({r:g}bp);")
        self.add(rf"\draw[ink, line width={self.s.lw_chip:g}pt] {self.p(x - a, y)} -- {self.p(x + a, y)};")
        self.add(rf"\draw[ink, line width={self.s.lw_chip:g}pt] {self.p(x, y - a)} -- {self.p(x, y + a)};")

    def junction(self, x: float, y: float) -> None:
        self.add(rf"\fill[ink] {self.p(x, y)} circle ({self.s.dot_r:g}bp);")

    def residual(self, x_from: float, y_from: float, x_to: float, y_to: float, side: float) -> None:
        """The pre-norm bypass: tap the stream (a junction dot), run out to the margin x `side`, come back into
        the face of the join that looks at the margin."""
        self.junction(x_from, y_from)
        self.line([(x_from, y_from), (side, y_from), (side, y_to)], residual=True)
        face = x_to + self.s.join_r if side > x_to else x_to - self.s.join_r
        self.arrow(side, y_to, face, y_to, residual=True)

    # ---- cards
    def card(self, ox: float, top: float, w: float, h: float, name: str) -> None:
        """The card: a gray rounded frame with its name ON the top border. The border is masked behind the
        name's ink as measured in the first pass; without a measurement the name is drawn unmasked."""
        s = self.s
        self.cards.append((ox, top, w, name))
        self.add(rf"\draw[card, rounded corners={s.card_r:g}bp, line width={s.lw_card:g}pt] "
                 rf"{self.p(ox, top)} rectangle {self.p(ox + w, top + h)};")
        ink = self.names.get(name)
        if ink:
            self.add(rf"\fill[white] {self.p(ox + s.name_inset - 3.0, top - 0.68 * s.pt_name)} rectangle "
                     rf"{self.p(ox + s.name_inset + ink + 3.0, top + 0.62 * s.pt_name)};")
        self.text(ox + s.name_inset, top + s.name_drop * s.pt_name, name, s.pt_name, "base west")

    def mini(self, kind: str, ox: float, w: float, y0: float) -> float:
        """The what-it-does icon inside a card at the top right: 'pool' (four children to one parent),
        'mix' (a tile and its neighborhood to that tile) or 'read' (tiles coarse to fine to one point).
        Returns the icon's width."""
        s = self.s
        sz, g = s.mini, s.mini_gap
        pitch = sz + g

        def cell(x, y, fill, size=sz, stroke="mini"):
            self.add(rf"\draw[{stroke}, fill={fill}, line width={s.lw_mini:g}pt] "
                     rf"{self.p(x, y)} rectangle {self.p(x + size, y + size)};")

        def feed(x, yc):
            self.add(rf"\fill[ink] {self.p(x, yc - 2.0)} -- {self.p(x + 4.0, yc)} -- {self.p(x, yc + 2.0)} -- cycle;")

        if kind == "pool":
            n, h = 2, 2 * pitch - g
            width = n * pitch - g + 10.0 + h
            x0 = ox + w - 12.0 - width
            for i in range(n):
                for j in range(n):
                    cell(x0 + i * pitch, y0 + j * pitch, "tokblue")
            feed(x0 + n * pitch - g + 3.0, y0 + h / 2)
            cell(x0 + n * pitch - g + 10.0, y0, "tokorange", size=h, stroke="chip")
        elif kind == "mix":
            n, h = 3, 3 * pitch - g
            width = n * pitch - g + 10.0 + sz
            x0 = ox + w - 12.0 - width
            for i in range(n):
                for j in range(n):
                    cell(x0 + i * pitch, y0 + j * pitch, "tokorange!70!black" if (i, j) == (1, 1) else "tokorange")
            feed(x0 + n * pitch - g + 3.0, y0 + h / 2)
            cell(x0 + n * pitch - g + 10.0, y0 + pitch, "tokblue")
        elif kind == "read":
            width = 3 * pitch - g + 3.0 + 9.0 + 2.2
            x0 = ox + w - 12.0 - width
            for i in range(3):
                side = sz * (1.0 - 0.2 * i)
                cell(x0 + i * pitch, y0 + (sz - side) / 2, "tokblue", size=side)
            xa = x0 + 3 * pitch - g + 3.0
            feed(xa, y0 + sz / 2)
            self.add(rf"\fill[chipline] {self.p(xa + 9.0, y0 + sz / 2)} circle (2.2bp);")
        else:
            raise ValueError(f"unknown mini icon {kind!r}")
        return width

    def two_level(self, x: float, y_name: float, y_gloss: float, name: str, gloss: str) -> None:
        """A black name over its gray gloss."""
        self.text(x, y_name, name, self.s.pt_cap, "base")
        self.note(x, y_gloss, gloss, "base")

    # ---- output
    def tex(self) -> str:
        body = "".join(self.o)
        return (header(self.preamble)
                + "\\begin{tikzpicture}[x=1bp, y=1bp, paper]\n"
                + f"\\useasboundingbox (0,0) rectangle ({self.w:.2f},{-self.h:.2f});\n"
                + body + "\\end{tikzpicture}\n\\end{document}\n")

    def write(self, path: Path) -> Path:
        path = Path(path)
        path.write_text(self.tex())
        return path


# ---------------------------------------------------------------------------------------------- build
def compile_tex(tex: Path) -> Path:
    """pdflatex -halt-on-error in the file's folder; returns the PDF or raises with the first error line."""
    tex = Path(tex).resolve()
    r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", tex.name],
                       cwd=tex.parent, capture_output=True, text=True, errors="replace")
    pdf = tex.with_suffix(".pdf")
    if r.returncode != 0 or not pdf.exists():
        err = next((ln for ln in r.stdout.splitlines() if ln.startswith("!")), "no error line in the log")
        raise RuntimeError(f"pdflatex failed on {tex.name}: {err}")
    return pdf


def _spans(pdf: Path) -> list:
    """[(x0, y0, x1, y1, text)] of every word or span on page 1, y from the top, bp."""
    try:
        import fitz  # PyMuPDF
        page = fitz.open(str(pdf))[0]
        return [(*sp["bbox"], sp["text"]) for b in page.get_text("dict")["blocks"]
                for ln in b.get("lines", []) for sp in ln["spans"] if sp["text"].strip()]
    except ImportError:
        if not shutil.which("pdftotext"):
            raise RuntimeError("measuring names needs PyMuPDF or poppler's pdftotext")
        out = subprocess.run(["pdftotext", "-bbox", "-f", "1", "-l", "1", str(pdf), "-"],
                             capture_output=True, text=True).stdout
        rx = re.compile(r'xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">(.*?)</word>')
        return [(float(a), float(b), float(c), float(d), t) for a, b, c, d, t in rx.findall(out)]


def measure_names(pdf: Path, cards: list, style: Style) -> dict:
    """Ink width of each card's name: the spans that cross the card's top border inside its x range."""
    spans = _spans(pdf)
    out = {}
    for ox, top, w, name in cards:
        xs = [sp for sp in spans if ox <= sp[0] < ox + w and sp[1] < top + 1.0 and sp[3] > top - 1.0]
        if xs:
            out[name] = round(max(sp[2] for sp in xs) - min(sp[0] for sp in xs), 2)
    return out


def check_names(fig: Figure) -> list:
    """Messages for names that do not fit their card (12 bp of frame left visible on each side)."""
    msgs = []
    for ox, top, w, name in fig.cards:
        ink = fig.names.get(name)
        if ink is None:
            msgs.append(f"name not measured: {name!r}")
        elif fig.s.name_inset + ink + 12.0 > w:
            msgs.append(f"name {name!r} is {ink:.1f} bp wide; the card leaves {w - fig.s.name_inset - 12.0:.1f} bp")
    return msgs


def build(make: Callable[[dict], Figure], tex: Path, keep_widths: Path | None = None) -> tuple:
    """Two passes: make({}) is written and compiled, the card names are measured from the PDF, then
    make(widths) is written and compiled again. Returns (pdf, widths, messages)."""
    tex = Path(tex)
    fig = make({})
    fig.write(tex)
    pdf = compile_tex(tex)
    widths = measure_names(pdf, fig.cards, fig.s)
    fig = make(widths)
    fig.write(tex)
    pdf = compile_tex(tex)
    if keep_widths:
        Path(keep_widths).write_text(json.dumps(widths, indent=1) + "\n")
    return pdf, widths, check_names(fig)


def main() -> int:
    ap = argparse.ArgumentParser(description="The paper-style figure kit: print the numbers it reads from the "
                                             "preamble. Import it to draw (see examples/block_cards.py).")
    ap.add_argument("--tokens", action="store_true", help="print every number read from the preamble")
    ap.add_argument("--preamble", type=Path, default=PREAMBLE, help="the preamble to read (default: next to this file)")
    a = ap.parse_args()
    if a.tokens:
        for k, v in read_tokens(a.preamble).items():
            print(f"{k:12s} {v:g}")
        s = Style.from_preamble(a.preamble)
        print(f"token row width {s.tok_w:g} bp ({s.chip_cols} cells)")
        return 0
    ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
