/* Worked example (architecture pack): a teacher-student pretraining region for a
 * model over table rows, drawn in the I-JEPA grammar. Region rect about 880 x 900.
 *   top rail:    masked rows -> student encoder -> predictor -> predicted embeddings
 *   bottom rail: full rows   -> teacher encoder (EMA copy) -> sg -> target embeddings
 *   right:       latent loss between predicted and target embeddings
 * Uses only PAL, FONT and LIB. The master draws the panel letter and title.
 * Copy it to regions/region_a.js and rename the function to match LAYOUT. */
function drawRegion_a(ctx, W, H, R) {
  const P = PAL, F = FONT, rng = LIB.rng(7);

  // ---- input table: 8 rows x 6 features, about 30 % of cells masked -------------
  const tx = 40, ty = 330, rows = 8, cols = 6;
  const masked = [];
  for (let r = 0; r < rows; r++) { masked.push([]); for (let c = 0; c < cols; c++) masked[r].push(rng() < 0.3); }
  const g = LIB.cellGrid(ctx, tx, ty, rows, cols, {
    cw: 26, ch: 20, gap: 3,
    fill: (r, c) => LIB.rank(0.15 + 0.55 * rng()),
    masked: (r, c) => masked[r][c],
  });
  LIB.text(ctx, 'Input rows', tx, ty - 18, { size: F.L2, weight: F.medium });
  LIB.brace(ctx, tx, ty + g.h + 8, g.w, 'down');
  LIB.text(ctx, 'features', tx + g.w / 2, ty + g.h + 46, { size: F.L3, align: 'center' });

  // ---- rails ---------------------------------------------------------------------
  const bx = 300, bw = 190, bh = 86, topY = 140, botY = 610, midTop = topY + bh / 2, midBot = botY + bh / 2;
  const tableMid = ty + g.h / 2, out = tx + g.w + 14;
  LIB.line(ctx, out - 6, tableMid, 250, tableMid, P.line, 2.0);
  LIB.elbow(ctx, 250, tableMid, bx - 6, midTop, 'vh', { color: P.line });
  LIB.elbow(ctx, 250, tableMid, bx - 6, midBot, 'vh', { color: P.line });
  LIB.text(ctx, 'masked', 240, midTop + 30, { size: F.L3, align: 'right' });
  LIB.text(ctx, 'full', 240, midBot - 22, { size: F.L3, align: 'right' });

  LIB.block(ctx, bx, topY, bw, bh, { label: 'Student encoder', sublabel: 'trained', fill: P.methodFill, stroke: P.method });
  LIB.block(ctx, bx, botY, bw, bh, { label: 'Teacher encoder', sublabel: 'EMA of student', fill: P.teacherFill, stroke: P.teacher });
  LIB.emaArrow(ctx, bx + bw / 2, topY + bh + 8, bx + bw / 2, botY - 10, 'EMA', { lx: bx + bw / 2 + 14, ly: (topY + bh + botY) / 2, align: 'left' });

  const px = 560, pw = 150;
  LIB.arrow(ctx, bx + bw + 6, midTop, px - 6, midTop, { color: P.method });
  LIB.block(ctx, px, topY, pw, bh, { label: 'Predictor', fill: P.methodFill, stroke: P.method });

  // embeddings as token rows
  const ts = 20, tg = 4, tokX = 735;
  LIB.arrow(ctx, px + pw + 6, midTop, tokX - 8, midTop, { color: P.method });
  LIB.tokenSeq(ctx, tokX, midTop - ts / 2, 5, ts, { gap: tg, colors: () => P.methodFill, stroke: P.method });
  LIB.text(ctx, 'predicted', tokX, midTop - ts / 2 - 12, { size: F.L3 });

  LIB.arrow(ctx, bx + bw + 6, midBot, tokX - 8, midBot, { color: P.teacher });
  LIB.stopGrad(ctx, 620, midBot, { color: P.ink });
  LIB.tokenSeq(ctx, tokX, midBot - ts / 2, 5, ts, { gap: tg, colors: () => P.teacherFill, stroke: P.teacher });
  LIB.text(ctx, 'target', tokX, midBot + ts / 2 + 26, { size: F.L3 });

  // ---- loss: the one contrast colour ------------------------------------------------
  const lx = 715, ly = 365, lw = 150, lh = 110, lcx = lx + lw / 2;
  LIB.arrow(ctx, lcx, midTop + ts / 2 + 6, lcx, ly - 6, { color: P.line });
  LIB.arrow(ctx, lcx, midBot - ts / 2 - 6, lcx, ly + lh + 6, { color: P.line });
  LIB.block(ctx, lx, ly, lw, lh, { fill: P.targetFill, stroke: P.target });
  LIB.text(ctx, 'Latent loss', lcx, ly + 38, { size: F.L2, weight: F.semibold, align: 'center', baseline: 'middle' });
  LIB.math(ctx, lcx, ly + 76, [{ t: 'L' }, { t: '(', italic: false }, { t: 'z', sub: 'pred' }, { t: ',', italic: false }, { t: ' z', sub: 'tgt' }, { t: ')', italic: false }], F.L2, 'center');

  // ---- legend ------------------------------------------------------------------------
  LIB.legend(ctx, 40, H - 40, [
    { shape: 'block', color: P.method, fill: P.methodFill, label: 'student path' },
    { shape: 'block', color: P.teacher, fill: P.teacherFill, label: 'teacher path' },
    { shape: 'dash', color: P.teacher, label: 'EMA weight copy' },
    { shape: 'block', color: P.mask, fill: P.paper, label: 'masked cell' },
  ], { horizontal: true });
}
