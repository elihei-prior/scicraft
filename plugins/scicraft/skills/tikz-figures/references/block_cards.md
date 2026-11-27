# Block cards

A block card draws one computational block (an attention block, a pooling block, a readout) read top to bottom:
its inputs as stacks of tokens with a two-level caption, its norms, its one operation box, its residuals, its
output. Cards of one figure share their stations, so their blocks align across the row. The source cards were
redrawn three times before they matched the code; every rule below comes from one of those corrections.

**Contents**
1. Check the mechanism against the code first
2. Anatomy and stations
3. The kit: a card from Python, names measured in two passes
4. A hand-written card: one self-attention block
5. A join that enters a condition or an embedding
6. A wider card for a main-figure slot
7. Names, symbols and the legend line

## 1. Check the mechanism against the code first

The source's first cards had five errors that a reader of the code would catch: one norm drawn for a
cross-attention block, a self-attention block labeled cross-attention, both input streams merged into one norm
and one bypass, register tokens that the configuration did not use, and a count written as a trailing sentence
where the code adds it to the tokens. Before drawing, read the block's code and fill this table; draw only what
the table says.

| Question | Where it shows in the code | What it changes in the card |
|---|---|---|
| Do queries and keys get their own norms? | separate norm modules for the query and key streams, or one shared | cross-attention: two LayerNorm boxes; self-attention: one wide LayerNorm both drops enter |
| What does the residual add back? | the tensor in `x + attn(norm(x))` | the residual taps THAT stream (the queries), above its norm, never the keys |
| Where is position applied? | which of q and k is rotated, and with what offset | write it where it acts: "RoPE on $k$" if only keys rotate |
| Is anything added between blocks? | `tokens + mlp(t)`, `tokens + embedding[c]` | a join with each addend as its own input, at the place it happens |
| How wide is each token, how many per set? | the model dimension, the number of seeds or tokens | a stack of K rows; the width and the count bracketed once |
| How deep is the block? | the number of repeats | say it in the caption if it matters; the card draws one |

- **A mechanism is drawn as the code computes it.** A self-attention block shares one norm; a cross-attention
  block has two; the residual taps the query stream; position rotation is drawn where it is applied; a count that
  enters as a join is drawn as a join.
- **Labels follow the paper's wording, even where a config differs.** When the code and the paper disagree (in
  the source, a graph rule named one way in the paper and configured another way in the code), the figure uses
  the paper's words and the discrepancy goes to the author; never relabel the figure on your own.
- **Drop what is true but not needed.** Gains of a qk-norm, the block count, a fixed neighbor count: the author
  dropped each, and the fixed count was also wrong in general, since it silently fixed a radius that the
  configuration sets.

## 2. Anatomy and stations

From the top of a card: the name on the border and the mini icon (top right); two captions (queries, keys and
values) each with a gray gloss; the input stacks (width brace and count brace on the first glyph of the figure);
the norm or norms; the two wires that meet above the operation box with $q$ and $k, v$ beside them; the operation
box; the first join with the residual from the query tap; the second norm and the FFN with its width; the second
join with the residual from a tap under the first join; the output stack and its caption.

All stations are in `references/style.md`, section 5, and in `figkit.Stations`. The streams sit at 0.25 and 0.72
of the card width and the trunk at 0.47. The residuals run 7 bp inside the card's left and right edges.

## 3. The kit: a card from Python, names measured in two passes

`assets/examples/block_cards.py` is the worked example: two cards, a cross-attention pooling block and a
neighborhood self-attention block, built with `assets/figkit.py`. Its core:

```python
import figkit as K
ST = K.Stations().replace(out=398.0, outcap=424.0)
def make(names):                      # names: card name -> ink width from the first pass
    f = K.Figure(507, 473, names=names)
    f.card(2.5, ST.top, 244, 432, "Cross-Attention Pooling")
    f.mini("pool", 2.5, 244, ST.mini)
    f.two_level(63.5, ST.cap, ST.sub, "queries", r"$K$ seed tokens")
    f.tokens(63.5, ST.stack, "tokpurple")
    ...
    return f
pdf, widths, problems = K.build(make, out / "block_cards.tex")   # compile, measure the names, compile again
```

- **Two passes for the names.** The border is masked behind the name's ink; only the compiled PDF knows the ink,
  so `build()` compiles without masks, measures each name (PyMuPDF, or `pdftotext -bbox`), and compiles again.
  A fixed mask once left a larger name's descenders on the frame line. `build()` also reports a name that does
  not fit its card with 12 bp of frame visible on the right.
- **Coordinates are bp, y downward, the page is the figure.** An audit finding at (x, y) is the generator's (x, y).
- **No module state.** Sizes come from `Style.from_preamble()`; a wider card is `Style.scaled(...)`; stations are a
  `Stations` table. The source rebound module globals and function defaults to widen one card; the kit does not.

## 4. A hand-written card: one self-attention block

A standard pre-norm self-attention block as one card, written with the preamble's macros. One stream: the tokens
are queries, keys and values at once, so the card has one stack, one norm and one wire that splits into $q$ and
$k, v$.

```latex
\begin{tikzpicture}[x=1bp, y=1bp, paper]
  \card{0,0}{220}{416}{Self-Attention Block}
  \minimix{163,-10}
  \twolevel{103,-44}{tokens}{queries, keys and values}
  \tokstack{103,-96}{tokorange}
  \tokwidthbrace{103,-96}{$d$}
  \tokdepthbrace{103,-96}{$N$}
  \coordinate (tap) at (103,-112);
  \node[box] (ln1) at (103,-144) {LayerNorm};
  \draw[wire] (103,-98.2) -- (103,-129);
  \draw[wirebare] (ln1.south) -- (103,-170) -- (73,-170);
  \draw[wirebare] (103,-170) -- (133,-170);
  \draw[wire] (73,-170) -- (73,-185);
  \draw[wire] (133,-170) -- (133,-185);
  \node[note, anchor=base east] at (69,-181) {$q$};
  \node[note, anchor=base west] at (137,-181) {$k, v$};
  \node[opbox=opmint] (att) at (103,-206) {Multi-Head\\Self-Attention};
  \node[note, anchor=base west] at (12,-238) {RoPE on $q, k$};
  \coordinate (j1) at (103,-252);
  \draw[wire] (att.south) -- (103,-245.4);
  \coordinate (side) at (7,0);
  \residual{tap}{side}{j1}
  \joincircle{j1}
  \draw[wire] (103,-257.6) -- (103,-283);
  \node[box] at (103,-298) {FFN (GELU)};
  \node[note, anchor=base west] at (155,-302) {$4d$};
  \coordinate (j2) at (103,-330);
  \draw[wire] (103,-312) -- (103,-323.4);
  \coordinate (tap2) at (103,-268);
  \coordinate (side2) at (213,0);
  \residual{tap2}{side2}{j2}
  \joincircle{j2}
  \draw[wire] (103,-335.6) -- (103,-354.4);
  \tokstack{103,-366}{tokblue}
  \node[capt, gloss, anchor=base] at (110,-398) {every token, updated};
\end{tikzpicture}
```

This recipe merges the FFN's norm into the FFN box to stay short; a real card draws the second LayerNorm as its
own box, as the worked example does ("separate layer norm from ffn").

## 5. A join that enters a condition or an embedding

When the code adds something to the tokens between blocks, draw the addition: the tokens come down into a join,
each addend enters from a side with its symbol, and the result leaves as a new kind of token (its chip color
changes exactly here). The source wrote such an addition (a count) as a trailing sentence first; the author asked
for it drawn. The recipe shows a generic case: a diffusion step through its MLP and a class embedding.

```latex
\begin{tikzpicture}[x=1bp, y=1bp, paper]
  \tokstack{120,0}{tokpurple}
  \node[note, anchor=base west] at (143.6,-4.4) {$\widetilde{Z}$};
  \coordinate (j) at (120,-40);
  \draw[wire] (120,-2.2) -- (120,-33.4);
  \node[box, minimum width=66bp, font=\fNote] (mlp) at (63,-40) {time MLP};
  \draw[wire] (10,-40) -- (29,-40);
  \node[note, anchor=base] at (17,-33) {$t$};
  \draw[wire] (mlp.east) -- (113.4,-40);
  \draw[wire] (166,-40) -- (126.6,-40);
  \node[note, anchor=base] at (146,-33.5) {$e_c$};
  \joincircle{j}
  \draw[wire] (120,-45.6) -- (120,-71);
  \tokstack{120,-84}{tokorange}
  \node[note, anchor=base west] at (143.6,-88.4) {$Z$};
  \node[capt, anchor=base west] at (0,-120) {$t$: diffusion step\quad $e_c$: learned class embedding};
\end{tikzpicture}
```

## 6. A wider card for a main-figure slot

A card that stands alone beside another panel in a main figure is drawn wider with larger type, and every size
changes together. The source's readout card used width 360 bp, boxes 118 x 34, the operation box 184 x 48, type
20, 19, 18.5 and 18 pt, chips 5.2 with gap 1.8 and offset 3.6, join radius 6.5, mini cells 8 with gap 2, and its
own stations over the same card height. With the kit:

```python
wide = K.Style.from_preamble().scaled(box_w=118, box_h=34, op_w=184, op_h=48, pt_name=20, pt_cap=19,
                                      pt_box=18.5, pt_note=18, chip=5.2, chip_gap=1.8, stack_off=3.6,
                                      join_r=6.5, mini=8, mini_gap=2)
f = K.Figure(365, 533, style=wide)
```

Check the printed sizes after composing (`scripts/print_scale.py`): the readout card's 18 pt notes printed at
6.2 pt beside a panel whose box labels printed at 4.8 pt (`references/style.md`, section 10).

## 7. Names, symbols and the legend line

- **Names as a reader meets them.** Card names are the published names of the mechanism or plain words
  ("Cross-Attention Pooling"); captions say what each stream is ("$K$ seed tokens", "its neighborhood"), never a
  variable name from the code.
- **Symbols are the paper's notation and every one is defined once**, either by the caption over its glyph or in
  one legend line under the cards ("$K$: number of seed tokens \quad $d$: token width"), set at the caption size
  in black.
- **A symbol sits beside its glyph**: right of a stack at the front row's height, centered over a single row, 8.5 bp
  above the back row of a stack it names. At 6 bp a subscript touched a chip; at 4.5 bp above a tap, a subscript
  crossed the wire, and 10 bp cleared it.
- **The output caption says what the block returns** in gray ("$K$ tokens that summarize the set"), with one word
  in italic when the contrast matters (the source: "for the *parent* tile" against "for the *same* tile").
