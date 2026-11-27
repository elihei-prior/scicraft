/* =====================================================================
 * canvas-schematics architecture pack (load after core_lib.js)
 * ---------------------------------------------------------------------
 * Primitives for model and method figures in the grammar of the I-JEPA,
 * DINOv2, MAE, Point Transformer and Graphormer overview figures: flat
 * blocks with thin borders, token rows, offset tensor stacks, towers of
 * summary levels, partition trees, small matrices, dashed EMA arrows and
 * stop-gradient marks.
 *
 * Colours are SEMANTIC tokens, set by a theme:
 *   PAL.method / methodFill   method, student, forward path
 *   PAL.teacher / teacherFill teacher, EMA copy
 *   PAL.target / targetFill   target, loss, emergent read-out (the one contrast)
 *   PAL.mask                  outline of a masked or held-out cell
 *   PAL.mark / markFill       the highlighted cell of a partition
 * Call LIB.setArchTheme('pastel') or ('three-accent') before drawing.
 * ===================================================================== */
(function () {
  'use strict';
  if (!window.LIB) throw new Error('pack_arch.js needs core_lib.js loaded first');
  const PAL = window.PAL, FONT = window.FONT, LIB = window.LIB;

  const THEMES = {
    // Pastel theme: the role palette of the vector figures from the sibling skill tikz-figures.
    // Every outline is ink and the fill names the role; the loss is the one saturated mark.
    'pastel': {
      method: '#333333', methodFill: '#FBE0C2', methodLight: '#F0B060',
      teacher: '#333333', teacherFill: '#E8E8EC',
      target: '#D93025', targetFill: '#FBE9E7', targetLight: '#FBE9E7',
      extra: '#666666',
      mask: '#999999', mark: '#333333', markFill: '#F5D36B',
      tok: ['#93B4D8', '#F0B060', '#B9A3DC', '#8FBFA0', '#F5D36B'],
    },
    // Three-accent theme: blue student, teal teacher, amber target.
    'three-accent': {
      method: '#0B6FB8', methodFill: '#e9f1fb', methodLight: '#8FB9E3',
      teacher: '#0F8C7A', teacherFill: '#e6f3f0',
      target: '#D97A06', targetFill: '#fdf1df', targetLight: '#F3C27F',
      extra: '#6D4AA7',
      tok: ['#0B6FB8', '#0F8C7A', '#D97A06', '#6D4AA7', '#B0B6BE'],
    },
  };
  PAL.fillNeutral = '#f4f6f8';
  LIB.archThemes = THEMES;
  LIB.setArchTheme = function (name) {
    const t = THEMES[name]; if (!t) throw new Error('unknown theme ' + name + '; use ' + Object.keys(THEMES).join(' or '));
    Object.assign(PAL, t);
    // Optional tokens fall back to the target colour, so a theme that names none keeps one contrast.
    PAL.mask = t.mask || t.target; PAL.mark = t.mark || t.target; PAL.markFill = t.markFill || LIB.alpha(t.target, 0.16);
    PAL.archTheme = name; return name;
  };
  LIB.setArchTheme('pastel');

  // FLAT module block. opt {label, sublabel, fill, stroke, lw, radius, labelColor, labelSize, weight, dash, italic, mono}
  LIB.block = function (ctx, x, y, w, h, opt) {
    opt = opt || {}; ctx.save();
    const r = opt.radius == null ? 3 : opt.radius;
    LIB.roundRectPath(ctx, x, y, w, h, r);
    ctx.fillStyle = opt.fill || PAL.fillNeutral; ctx.fill();
    ctx.lineWidth = opt.lw || 1.6; ctx.strokeStyle = opt.stroke || PAL.line; ctx.setLineDash(opt.dash || []);
    LIB.roundRectPath(ctx, x, y, w, h, r); ctx.stroke(); ctx.setLineDash([]); ctx.restore();
    if (opt.label) {
      const hasSub = !!opt.sublabel, ls = opt.labelSize || FONT.L2;
      LIB.text(ctx, opt.label, x + w / 2, y + h / 2 + (hasSub ? -FONT.L3 * 0.5 : 0), { size: ls, weight: opt.weight || FONT.semibold, align: 'center', baseline: 'middle', color: opt.labelColor || PAL.ink, italic: opt.italic, mono: opt.mono });
      if (hasSub) LIB.text(ctx, opt.sublabel, x + w / 2, y + h / 2 + FONT.L3 * 0.8, { size: FONT.L3, align: 'center', baseline: 'middle', color: opt.subColor || PAL.ink, weight: FONT.light, italic: opt.subItalic });
    }
  };

  // Stacked tensor: offset copies behind a front face. Depth is a faded copy, never a blur.
  // opt {fill, stroke, depth, dz, lw, radius, label}
  LIB.tensor = function (ctx, x, y, w, h, opt) {
    opt = opt || {}; const d = opt.depth || 3, dz = opt.dz || 5, st = opt.stroke || PAL.method; ctx.save();
    for (let i = d - 1; i >= 0; i--) {
      const ox = x + i * dz, oy = y - i * dz;
      ctx.fillStyle = i === 0 ? (opt.fill || PAL.methodFill) : LIB.alpha(st, 0.10);
      ctx.strokeStyle = st; ctx.lineWidth = opt.lw || 1.3;
      LIB.roundRectPath(ctx, ox, oy, w, h, opt.radius == null ? 2 : opt.radius); ctx.fill(); ctx.stroke();
    }
    ctx.restore();
    if (opt.label) LIB.text(ctx, opt.label, x + w / 2, y + h / 2, { size: FONT.L3, align: 'center', baseline: 'middle' });
  };

  // Token row: a row (or column) of small squares. opt {gap, colors(i)->fill, strokes(i)->stroke, stroke, lw, vertical, radius, masked(i)->bool}
  LIB.tokenSeq = function (ctx, x, y, n, s, opt) {
    opt = opt || {}; const gap = opt.gap == null ? 3 : opt.gap; ctx.save();
    for (let i = 0; i < n; i++) {
      const px = opt.vertical ? x : x + i * (s + gap), py = opt.vertical ? y + i * (s + gap) : y;
      const masked = opt.masked && opt.masked(i);
      ctx.fillStyle = masked ? PAL.paper : (opt.colors ? opt.colors(i) : PAL.methodFill);
      ctx.strokeStyle = opt.strokes ? opt.strokes(i) : (opt.stroke || PAL.method); ctx.lineWidth = opt.lw || 1.2;
      ctx.setLineDash(masked ? [3, 2] : []);
      LIB.roundRectPath(ctx, px, py, s, s, opt.radius == null ? 1.5 : opt.radius); ctx.fill(); ctx.stroke();
    }
    ctx.setLineDash([]); ctx.restore();
    return opt.vertical ? y + n * (s + gap) - gap : x + n * (s + gap) - gap;
  };

  // Cell grid for tabular inputs: rows x cols of cells. opt {cw, ch, gap, fill(r,c), stroke, maskStroke, masked(r,c), rowTag(r)->color}
  // Suggested, not yet tested in real work.
  LIB.cellGrid = function (ctx, x, y, rows, cols, opt) {
    opt = opt || {}; const cw = opt.cw || 22, ch = opt.ch || 16, g = opt.gap == null ? 2 : opt.gap; ctx.save();
    for (let r = 0; r < rows; r++) {
      if (opt.rowTag) { ctx.fillStyle = opt.rowTag(r); ctx.fillRect(x - 8, y + r * (ch + g), 4, ch); }
      for (let c = 0; c < cols; c++) {
        const px = x + c * (cw + g), py = y + r * (ch + g), masked = opt.masked && opt.masked(r, c);
        ctx.fillStyle = masked ? PAL.paper : (opt.fill ? opt.fill(r, c) : PAL.fillNeutral);
        ctx.strokeStyle = masked ? (opt.maskStroke || PAL.mask) : (opt.stroke || PAL.guide); ctx.lineWidth = masked ? 1.4 : 1; ctx.setLineDash(masked ? [3, 2] : []);
        ctx.fillRect(px, py, cw, ch); ctx.strokeRect(px, py, cw, ch);
      }
    }
    ctx.setLineDash([]); ctx.restore();
    return { w: cols * (cw + g) - g, h: rows * (ch + g) - g };
  };

  // Tower: stacked bars, widest at the bottom, for a hierarchy of summary levels.
  // levels [{w, label, tag, fill, stroke, tagColor}] bottom first. opt {h, gap}. Returns the top y.
  LIB.tower = function (ctx, cx, yBottom, levels, opt) {
    opt = opt || {}; const h = opt.h || 26, gap = opt.gap == null ? 8 : opt.gap;
    let y = yBottom;
    levels.forEach((lv) => {
      const w = lv.w, x = cx - w / 2;
      LIB.block(ctx, x, y - h, w, h, { fill: lv.fill || PAL.methodFill, stroke: lv.stroke || PAL.method, lw: 1.4, radius: 2 });
      if (lv.label) LIB.text(ctx, lv.label, cx, y - h / 2, { size: FONT.L3, align: 'center', baseline: 'middle' });
      if (lv.tag) LIB.text(ctx, lv.tag, x + w + 8, y - h / 2, { size: FONT.L3, baseline: 'middle', color: lv.tagColor || PAL.ink, italic: true });
      y -= (h + gap);
    });
    return y;
  };

  // Recursive quadtree. spec: true/null for a leaf, or [tl, tr, bl, br]. opt {stroke, lw, highlight: path string like '14'}
  // Draw it from the partition your code actually produces, never by hand.
  LIB.quadtree = function (ctx, x, y, w, h, spec, opt) {
    opt = opt || {}; ctx.save();
    (function rec(x, y, w, h, node, depth, p) {
      ctx.strokeStyle = opt.stroke || PAL.guide; ctx.lineWidth = (opt.lw || 1.0) * Math.max(0.5, 1 - depth * 0.12);
      ctx.strokeRect(x, y, w, h);
      if (Array.isArray(node)) {
        const hw = w / 2, hh = h / 2;
        rec(x, y, hw, hh, node[0], depth + 1, p + '1'); rec(x + hw, y, hw, hh, node[1], depth + 1, p + '2');
        rec(x, y + hh, hw, hh, node[2], depth + 1, p + '3'); rec(x + hw, y + hh, hw, hh, node[3], depth + 1, p + '4');
      } else if (opt.highlight && p === opt.highlight) {
        ctx.save(); ctx.fillStyle = PAL.markFill; ctx.fillRect(x, y, w, h);
        ctx.strokeStyle = PAL.mark; ctx.lineWidth = 1.8; ctx.strokeRect(x, y, w, h); ctx.restore();
      }
    })(x, y, w, h, spec, 0, '');
    ctx.restore();
  };

  // Node-link tree. nodes [{x, y, r, fill, stroke, label}], edges [[i, j]]
  LIB.treeLinks = function (ctx, nodes, edges, opt) {
    opt = opt || {};
    edges.forEach(([a, b]) => LIB.line(ctx, nodes[a].x, nodes[a].y, nodes[b].x, nodes[b].y, opt.edge || PAL.line, opt.lw || 1.2));
    nodes.forEach(nd => {
      ctx.save(); ctx.beginPath(); ctx.arc(nd.x, nd.y, nd.r || 6, 0, Math.PI * 2);
      ctx.fillStyle = nd.fill || PAL.methodFill; ctx.fill(); ctx.lineWidth = 1.4; ctx.strokeStyle = nd.stroke || PAL.method; ctx.stroke(); ctx.restore();
      if (nd.label) LIB.text(ctx, nd.label, nd.x, nd.y - (nd.r || 6) - 7, { size: FONT.L3, align: 'center' });
    });
  };

  // EMA or weight-copy arrow: dashed, in the teacher colour, optional italic label.
  LIB.emaArrow = function (ctx, x1, y1, x2, y2, label, opt) {
    opt = opt || {}; const c = opt.color || PAL.teacher;
    LIB.arrow(ctx, x1, y1, x2, y2, { color: c, lw: opt.lw || 1.6, dash: [6, 5], head: opt.head || 7 });
    if (label) LIB.text(ctx, label, opt.lx != null ? opt.lx : (x1 + x2) / 2 + (opt.dx || 0), opt.ly != null ? opt.ly : (y1 + y2) / 2 - 6, { size: FONT.L3, align: opt.align || 'center', color: c, italic: true });
  };

  // Stop-gradient mark: a short bar across a path, labelled 'sg' by default.
  LIB.stopGrad = function (ctx, x, y, opt) {
    opt = opt || {}; const r = opt.r || 7, c = opt.color || PAL.ink, vertical = opt.vertical;
    ctx.save(); ctx.strokeStyle = c; ctx.lineWidth = 1.8; ctx.beginPath();
    if (vertical) { ctx.moveTo(x - r, y); ctx.lineTo(x + r, y); } else { ctx.moveTo(x, y - r); ctx.lineTo(x, y + r); }
    ctx.stroke(); ctx.restore();
    if (opt.label !== false) LIB.text(ctx, opt.label || 'sg', vertical ? x + r + 4 : x + 4, vertical ? y + 1 : y - r - 3, { size: FONT.L3, color: c, italic: true, baseline: vertical ? 'middle' : 'alphabetic' });
  };

  // Curly brace over a length. dir: 'right' | 'left' (vertical span starting at y) or 'down' | 'up' (horizontal span starting at x).
  LIB.brace = function (ctx, x, y, len, dir, opt) {
    opt = opt || {}; const b = opt.bulge || 7, t = len / 2, k = Math.min(t, 14);
    ctx.save(); ctx.strokeStyle = opt.color || PAL.line; ctx.lineWidth = opt.lw || 1.3; ctx.lineCap = 'round'; ctx.beginPath();
    if (dir === 'right' || dir === 'left') {
      const s = dir === 'right' ? 1 : -1;
      ctx.moveTo(x, y); ctx.quadraticCurveTo(x + s * b, y, x + s * b, y + k); ctx.lineTo(x + s * b, y + t - 12);
      ctx.quadraticCurveTo(x + s * b, y + t, x + s * b * 2, y + t); ctx.quadraticCurveTo(x + s * b, y + t, x + s * b, y + t + 12);
      ctx.lineTo(x + s * b, y + len - k); ctx.quadraticCurveTo(x + s * b, y + len, x, y + len);
    } else {
      const s = dir === 'down' ? 1 : -1;
      ctx.moveTo(x, y); ctx.quadraticCurveTo(x, y + s * b, x + k, y + s * b); ctx.lineTo(x + t - 12, y + s * b);
      ctx.quadraticCurveTo(x + t, y + s * b, x + t, y + s * b * 2); ctx.quadraticCurveTo(x + t, y + s * b, x + t + 12, y + s * b);
      ctx.lineTo(x + len - k, y + s * b); ctx.quadraticCurveTo(x + len, y + s * b, x + len, y);
    }
    ctx.stroke(); ctx.restore();
  };
})();
