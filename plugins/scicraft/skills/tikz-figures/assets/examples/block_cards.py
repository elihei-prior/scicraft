#!/usr/bin/env python3
"""Worked example of the kit: two block cards side by side, built in two passes.

Card a is a cross-attention pooling block (K learned seed tokens attend over a set's tokens and become K tokens
that summarize the set); card b is a neighborhood self-attention block. Both are pre-norm transformer blocks with
an attention sub-block and an FFN sub-block, each wrapped by a residual.

What the drawing asserts, and why it is drawn this way:
  * cross-attention normalizes queries and keys separately, so card a has TWO LayerNorms; self-attention shares
    one norm over its input, so card b has ONE wide LayerNorm that both drops enter;
  * the residual taps the QUERY stream before its norm (the seeds in card a), never the keys;
  * a set of K vectors is a stack of K rows, never a row of n chips; the width is bracketed over the back row
    ($d$), the count along the stack's own diagonal ($K$);
  * position rotation is written where it is applied (card b rotates queries and keys);
  * a chip color names a kind of token: seeds purple, the set's tokens blue, the tokens a self-attention block
    consumes orange, its output blue.

Run:  python3 block_cards.py --out DIR      (writes DIR/block_cards.tex and .pdf; needs pdflatex and PyMuPDF or
                                            pdftotext for the name measurement)
"""
from __future__ import annotations

import argparse
import sys
sys.dont_write_bytecode = True        # importing a sibling must not leave __pycache__ in the skill
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import figkit as K  # noqa: E402

CW, CARD_GAP, MARGIN = 244.0, 14.0, 2.5
QX, KX, CX = 0.25, 0.72, 0.47                       # the two streams and the trunk, as fractions of CW
ST = K.Stations().replace(out=398.0, outcap=424.0)  # no injection join here, so the output moves up
CH = ST.outcap + 18.0 - ST.top                      # card height: 18 bp under the output caption
FOOT_Y = ST.top + CH + 19.0
PANEL_W = 2 * CW + CARD_GAP + 2 * MARGIN
PANEL_H = FOOT_Y + 12.0
NAMES = ("Cross-Attention Pooling", "Neighborhood Self-Attention")


def card(f: K.Figure, ox: float, kind: str) -> None:
    s = f.s
    pool = kind == "pool"
    cx, qx, kx = ox + CX * CW, ox + QX * CW, ox + KX * CW
    f.card(ox, ST.top, CW, CH, NAMES[0] if pool else NAMES[1])
    f.mini("pool" if pool else "mix", ox, CW, ST.mini)

    # ---- the two input streams: caption, gloss, stack
    if pool:
        f.two_level(qx, ST.cap, ST.sub, "queries", r"$K$ seed tokens")
        f.two_level(kx, ST.cap, ST.sub, "keys, values", r"the set's tokens")
        f.tokens(qx, ST.stack, "tokpurple")
        f.tokens(kx, ST.stack, "tokblue")
        f.width_brace(qx, ST.stack, r"$d$")      # the two directions, named once on the first glyph
        f.depth_brace(qx, ST.stack, r"$K$")
    else:
        f.two_level(qx, ST.cap, ST.sub, "queries", "every token")
        f.two_level(kx, ST.cap, ST.sub, "keys, values", "its neighborhood")
        f.tokens(qx, ST.stack, "tokorange")
        f.tokens(kx, ST.stack, "tokorange")

    # ---- into the norm(s); the residual taps the query drop above its norm
    ln_top, ln_bot = ST.ln1 - s.box_h / 2, ST.ln1 + s.box_h / 2
    f.arrow(qx, f.tok_bot(ST.stack), qx, ln_top - 1)
    f.arrow(kx, f.tok_bot(ST.stack), kx, ln_top - 1)
    if pool:                                    # cross-attention: one norm per stream
        f.box(qx, ST.ln1, "LayerNorm")
        f.box(kx, ST.ln1, "LayerNorm")
    else:                                       # self-attention: ONE norm, wide enough for both drops
        f.box((qx + kx) / 2, ST.ln1, "LayerNorm", w=kx - qx + 64.0)

    # ---- into the attention, the same way on both cards
    at_top, at_bot = ST.att - s.op_h / 2, ST.att + s.op_h / 2
    f.line([(qx, ln_bot), (qx, ST.conv), (cx - 30, ST.conv)])
    f.line([(kx, ln_bot), (kx, ST.conv), (cx + 30, ST.conv)])
    f.arrow(cx - 30, ST.conv, cx - 30, at_top - 1)
    f.arrow(cx + 30, ST.conv, cx + 30, at_top - 1)
    f.note(cx - 34, ST.qklbl, r"$q$", "base east")
    f.note(cx + 34, ST.qklbl, r"$k, v$", "base west")
    if pool:
        f.opbox(cx, ST.att, r"Multi-Head\\Cross-Attention", "oppeach")
    else:
        f.opbox(cx, ST.att, r"Multi-Head\\Self-Attention", "opmint")
        f.note(ox + 12.0, ST.note, r"RoPE on $q, k$", "base west")

    # ---- attention residual, then the FFN sub-block with its own residual
    f.arrow(cx, at_bot, cx, ST.add1 - s.join_r - 1)
    f.residual(qx, ST.tap, cx, ST.add1, ox + 7.0)
    f.join(cx, ST.add1)
    f.arrow(cx, ST.add1 + s.join_r, cx, ST.ln2 - s.box_h / 2 - 1)
    # the FFN residual taps the trunk halfway between the join and the start of the next arrowhead; tapped at
    # the midpoint of the gap (as in the source) it left the trunk 0.4 bp above the arrowhead (an audit stub)
    tap2 = (ST.add1 + s.join_r + ST.ln2 - s.box_h / 2 - 1 - s.head_l) / 2
    f.residual(cx, tap2, cx, ST.add2, ox + CW - 7.0)
    f.box(cx, ST.ln2, "LayerNorm")
    f.arrow(cx, ST.ln2 + s.box_h / 2, cx, ST.ffn - s.box_h / 2 - 1)
    f.box(cx, ST.ffn, "FFN (GELU)")
    f.note(cx + s.box_w / 2 + 6.0, ST.ffn + s.pt_note * 0.34, r"$4d$", "base west")
    f.arrow(cx, ST.ffn + s.box_h / 2, cx, ST.add2 - s.join_r - 1)
    f.join(cx, ST.add2)

    # ---- output and its caption
    f.arrow(cx, ST.add2 + s.join_r, cx, f.tok_top(ST.out) - 1)
    if pool:
        f.tokens(cx, ST.out, "tokorange")
        f.text(cx, ST.outcap, r"$K$ tokens that summarize the set", s.pt_cap, gloss=True)
    else:
        f.tokens(cx, ST.out, "tokblue")
        f.text(cx, ST.outcap, "every token, updated", s.pt_cap, gloss=True)


def make(names: dict) -> K.Figure:
    f = K.Figure(PANEL_W, PANEL_H, names=names)
    card(f, MARGIN, "pool")
    card(f, MARGIN + CW + CARD_GAP, "mix")
    # one legend line under the cards defines every symbol they use
    f.text(MARGIN + 8.0, FOOT_Y, r"$K$: number of seed tokens \quad $d$: token width", f.s.pt_cap, "base west")
    return f


def main() -> int:
    ap = argparse.ArgumentParser(description="Build the two-card example in two passes (names measured, then masked).")
    ap.add_argument("--out", type=Path, default=Path("."), help="output folder (default: here)")
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    pdf, widths, msgs = K.build(make, a.out / "block_cards.tex")
    print(f"wrote {pdf} ({PANEL_W:.0f} x {PANEL_H:.0f} bp); name ink: {widths}")
    for m in msgs:
        print("WARN ", m)
    return 1 if msgs else 0


if __name__ == "__main__":
    raise SystemExit(main())
