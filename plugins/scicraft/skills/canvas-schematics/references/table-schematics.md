# Schematics of tables: a dataset and the tasks it supports

Some schematics show what a dataset is and which prediction tasks it supports. A single-cell atlas drawn the AnnData
or MuData way is one; so is a table and its tasks for a tabular model. In such a figure the reader has to decode the
kind of every column at a glance. The rules below come from one panel that went through about twenty versions in a
day: a single-cell drug screen as one table (cell metadata beside gene expression), then six prediction tasks, one
small table each. Every rule answers something the author rejected.

## 1. The grammar

| Element | Draw it as | Why |
|---|---|---|
| a row (a cell, a sample, a cell line under a drug, a gene) | the row's own icons at its left: a cell, a pill, a gene | says what one row is without a subtitle |
| a categorical column (cell line, drug, class) | a filled icon, one distinct hue per category, no box and no outline | shades of one hue read as an order: "it was categorical not numerical, you killed it" |
| a numerical column (expression, viability, change) | a rounded tile on one single-hue lightness ramp, white for zero; blue, white and red for a signed value | the tiles were the part he liked: "I like how table cells are shown" |
| an amount that belongs to a category (a dose) | a ring in that category's color, sized by the amount, standing alone | a ring inside a boxed tile drew "dose circles inside cell outlines?" |
| columns or rows not drawn | ⋯ in a full cut column, centered, on every row; ⋮ in a cut band under the head rows | the way pandas and polars print a long table |
| the dimensions | braces close to the block, labeled with the real count from the records, the row count in bold ("**82.4M** rows") | sizes are rows × columns, never "cells" of a table |
| the target | the last column, set apart by the widest gap of the table, headed by what is predicted | "instead of saying to predict, say what that prediction is" |
| a categorical target | the category's own icon in the class color | it reads as the same kind of thing as the metadata |
| a numerical target | a shaded tile with a small ink icon inside (a pulse for viability, ↑ or ↓ for a change) | the icon names the target, the shade gives the value |
| the held-out row | below the cut band, its target a "?" in a dashed tile | the "?" alone says what is predicted |

Categories take hue and shape; amounts take lightness or size. Before drawing a column, name its data type, then
its encoding. A design that coded "source" by hue and "which one" by shade was rejected, although it looked tidy:
cell line, drug and mechanism became three tints that read as numbers.

## 2. One group per column type

- **⋯ means "more of the same type".** A single ⋯ across columns of different types was the complaint "4/5/6 are
  not same type columns". In a mixed table, draw one group per type. Each group has its own ⋯, and the gap
  between groups is wider than the gap between tiles and wider than the cut column.
- **Draw each group in proportion to its share of the columns.** Read the make-up from the code that builds the
  table, not from memory. A group can be left out only when the caption names it.
- **Label each group of a mixed table with a footer of one or two words** under it, such as "baseline expression"
  or "other cell lines". Tiny header icons over the columns (about 0.6 mm in print) did not explain anything. A
  footer that does not fit breaks onto two lines at a space.
- **Metadata shown at the left of a row is not drawn again as columns.** His words: "if you say the metadata
  already on left no need to put it in columns anymore". The braces then show which of those icons the model reads.

## 3. Color means read, gray means not read

- **Color a row icon only where the model reads it as a column.** An icon that only says what the row is gets
  gray. A colored pill in a row whose target is the drug's class gives the answer away: "for 3 we already have the
  drugs in the metadata no?"
- **Hide the target everywhere in its row.** When the cell line is the answer, the row's cell icon is gray.
- **A feature tile never repeats its target's shade in every training row.** A critic read that as a leak.
- **When the dose is read and its drug is not, draw the dose ring in ink.** Gray would say it is not read; the drug's
  color would say the drug is known.
- **The held-out row's category must be new.** For an unseen cell line, use a color no training row has, and one far
  from them in color-blind views too.

## 4. Words

- **Titles say the task and what is unseen at test time**, for example "Class of unseen drugs, single cells". Tasks
  without that word read as random splits. No subtitles: "drop this single cells, 50 classes and so on".
- **Headers name the prediction in plain, in-domain words**, the words a domain lab would use ("drug class",
  "surviving cells", "gene's change under drug").
  - A term the figure has not shown was rejected as new ("drug target is new, was it in metadata or gene metadata or
    what?").
  - A bare "mechanism of action" was rejected as unclear.
- **No key for the whole figure when only one task uses an encoding.** Explain it by the header, the icon or the
  caption: "one below control / above control legend which is specific to 6 to all?"
- **Every dataset-level number comes from the records,** asserted when the figure is built.

## 5. How readers misread these figures

Critics who had not drawn the figure were asked for a cold read, once as a biologist and once as a machine-learning
reader. They found:

| Drawn | Misread as | Fix |
|---|---|---|
| two pills for a drug class | a drug combination | one pill in the class color |
| a gray pill for a hidden drug | the vehicle control | define gray in the caption; avoid it where a control row exists |
| a gene icon in the expression teal | an expression value | identity icons in gray or ink |
| class colors in the green, blue or red family | viability, down, up | class colors outside the numerical families |
| a colored icon outside the brace | an input column | braces cover exactly the columns read, and the caption says so |
| "47.1k" in bold at page size | "471k" | check small bold numbers at print size |

## 6. Process

- **Before building, write the author's requests in his own words into SPEC.md** (a request ledger). Every
  correction adds a numbered rule; a retracted rule stays visible as retracted.
- **When something he liked disappears, recover it exactly**, from an earlier render or the session's file history,
  and change only what was asked. "Drop the cell outlines" meant the outlines, not the cell icons.
- **Gate the build with `scripts/check_clearance.py`.** It measures on the ink of the printed PDF: text against
  graphics, text against text, shapes that nearly touch, and the white between panels and between table columns
  and rows. "Too packed between a and b" measured 1.5 mm; the gate now asks for 9 mm.
- **Check color separation, color-blind views included,** with the palette check of the design-system skill.
- **Review with three critics before a final audit:**
  - logic against the code that builds the tables;
  - a cold read by both audiences;
  - measured design.

  Verify each finding in the code before acting on it. Fixes change wording, color or geometry and add no new
  element.
