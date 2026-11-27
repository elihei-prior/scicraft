#!/usr/bin/env python3
"""Check, compile and render one TikZ figure to a versioned PNG, in one command.

Steps, stopping at the first failure:
  1. check_tikz_safety.py (same folder) on the source;
  2. pdflatex -interaction=nonstopmode -halt-on-error, with --texinputs added to TeX's search path so that
     \\input{preamble.tex} resolves from the skill's assets/ (or any folder) without copying;
  3. the log is read: errors, overfull boxes and missing characters are reported (the exit code alone hides
     some failures);
  4. pdftoppm renders every page to <name>_vNN-<page>.png, NN the next free version number, so a cached viewer
     never shows an old render;
  5. every PNG is measured: a page under 40 px on a side is reported as blank (a body compiled without its
     preamble), and in a frame deck every frame must have the same size (otherwise the animation jitters).

--inline OUT.tex writes a self-contained copy for delivery: every \\input is replaced by the file's text, and a
preamble (a file with a line starting "%%%% FIGURE BODY") contributes only the part above that line, so the
delivered figure needs no other file. It is compiled again in an empty folder to prove it.

Then open the PNG and look at it. This script cannot see overlap or crowding (scripts/audit_layout.py can).

Needs pdflatex and pdftoppm (poppler) on PATH. Python standard library only.

Usage:
    python3 render_figure.py fig.tex
    python3 render_figure.py fig.tex --texinputs ../assets --dpi 170
    python3 render_figure.py deck.tex --dpi 150                   # frame deck: checks frame sizes
    python3 render_figure.py fig.tex --texinputs ../assets --inline fig_final.tex
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import struct
import subprocess
import sys
sys.dont_write_bytecode = True        # importing a sibling must not leave __pycache__ in the skill
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
INPUT = re.compile(r"\\input\{([^}]+)\}")


def png_size(path: Path) -> tuple:
    with path.open("rb") as fh:
        head = fh.read(24)
    if head[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path} is not a PNG")
    return struct.unpack(">II", head[16:24])


def next_version(out: Path, stem: str) -> int:
    used = [int(m.group(1)) for p in out.glob(f"{stem}_v*-*.png") if (m := re.match(rf"{re.escape(stem)}_v(\d+)-", p.name))]
    return max(used, default=0) + 1


def find(name: str, dirs: list) -> Path | None:
    for d in dirs:
        for cand in (Path(d) / name, Path(d) / f"{name}.tex"):
            if cand.is_file():
                return cand
    return None


def inline(text: str, dirs: list, depth: int = 0) -> str:
    """Replace every \\input{...} by the file's text; a preamble contributes only what is above its body marker."""
    if depth > 8:
        raise RuntimeError("\\input nested more than 8 deep")
    out = []
    for line in text.splitlines(keepends=True):
        if re.match(r"\s*\\def\\figpreambleonly\{\}", line):
            continue                                       # not needed once the preamble is inlined
        m = INPUT.search(line.split("%", 1)[0])
        if not m:
            out.append(line)
            continue
        f = find(m.group(1), dirs)
        if f is None:
            raise RuntimeError(f"cannot inline {m.group(1)}: not found in {', '.join(map(str, dirs))}")
        body = f.read_text(encoding="utf-8", errors="replace")
        cut = re.search(r"^%%%% FIGURE BODY", body, re.M)
        if cut:
            body = body[:cut.start()]
        out.append(line[:m.start()] + inline(body, [f.parent] + dirs, depth + 1).rstrip("\n") + line[m.end():])
    return "".join(out)


def run_tex(tex: Path, cwd: Path, texinputs: list) -> tuple:
    env = dict(os.environ)
    if texinputs:
        env["TEXINPUTS"] = os.pathsep.join(str(Path(t).resolve()) for t in texinputs) + os.pathsep + env.get("TEXINPUTS", "")
    proc = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", tex.name],
                          cwd=cwd, capture_output=True, text=True, errors="replace", env=env)
    log_path = cwd / f"{tex.stem}.log"
    log = log_path.read_text(errors="replace") if log_path.exists() else ""
    return proc.returncode, log


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Safety check, compile and render a TikZ figure to versioned PNGs.")
    ap.add_argument("tex", help="the figure source")
    ap.add_argument("--texinputs", action="append", default=[], help="a folder TeX also searches (repeatable)")
    ap.add_argument("--dpi", type=int, default=170, help="PNG resolution (default 170)")
    ap.add_argument("--out", help="folder for the PNGs (default: next to the source)")
    ap.add_argument("--skip-check", action="store_true", help="do not run the static safety check")
    ap.add_argument("--inline", help="also write this self-contained copy (every \\input inlined) and compile it alone")
    args = ap.parse_args(argv)

    tex = Path(args.tex).resolve()
    if not tex.exists():
        print(f"ERROR: {tex} does not exist")
        return 1
    for tool in ("pdflatex", "pdftoppm"):
        if not shutil.which(tool):
            print(f"ERROR: {tool} not found on PATH")
            return 1
    if not args.skip_check:
        sys.path.insert(0, str(HERE))
        from check_tikz_safety import check_text  # noqa: E402
        errors, warnings = check_text(tex.read_text(encoding="utf-8", errors="replace"))
        for w in warnings:
            print(f"WARN:  safety: {w}")
        if errors:
            for e in errors:
                print(f"ERROR: safety: {e}")
            return 1
        print("ok     safety check")

    code, log = run_tex(tex, tex.parent, args.texinputs)
    tex_errors = [ln for ln in log.splitlines() if ln.startswith("!")]
    if code != 0 or tex_errors:
        print(f"ERROR: pdflatex failed (exit {code}); first lines of the log:")
        for ln in tex_errors[:4]:
            print(f"       {ln}")
        m = re.search(r"^l\.\d+.*$", log, re.M)
        if m:
            print(f"       {m.group(0)[:160]}")
        return 1
    overfull = len(re.findall(r"^Overfull \\[hv]box", log, re.M))
    missing = len(re.findall(r"Missing character", log))
    print(f"ok     pdflatex: {tex.stem}.pdf ({overfull} overfull boxes, {missing} missing characters)")
    if missing:
        print("WARN:  missing characters: a glyph is not in the font (check symbols such as arrows and Greek)")

    out = Path(args.out).resolve() if args.out else tex.parent
    out.mkdir(parents=True, exist_ok=True)
    prefix = out / f"{tex.stem}_v{next_version(out, tex.stem):02d}"
    subprocess.run(["pdftoppm", "-png", "-r", str(args.dpi), str(tex.with_suffix(".pdf")), str(prefix)], check=True)
    pngs = sorted(out.glob(f"{prefix.name}-*.png"), key=lambda p: int(p.stem.rsplit("-", 1)[1]))
    if not pngs:
        print("ERROR: pdftoppm wrote no PNG")
        return 1
    sizes = [png_size(p) for p in pngs]
    failed = False
    for p, (w, h) in zip(pngs, sizes):
        if min(w, h) < 40:
            print(f"ERROR: {p.name} is {w}x{h} px: blank page (was the body compiled without the preamble?)")
            failed = True
    if len(set(sizes)) > 1:
        print(f"ERROR: frames differ in size {sorted(set(sizes))}: lock the bounding box in every frame")
        failed = True
    print(f"ok     {len(pngs)} page(s) at {args.dpi} dpi, {sizes[0][0]}x{sizes[0][1]} px")
    print(f"look   {pngs[0]}")
    if len(pngs) > 2:
        print(f"look   {pngs[len(pngs) // 2]}")
        print(f"look   {pngs[-1]}")

    if args.inline:
        dirs = [tex.parent] + [Path(t).resolve() for t in args.texinputs]
        try:
            text = inline(tex.read_text(encoding="utf-8", errors="replace"), dirs)
        except RuntimeError as e:
            print(f"ERROR: {e}")
            return 1
        dest = Path(args.inline).resolve()
        dest.write_text(text, encoding="utf-8")
        with tempfile.TemporaryDirectory() as tmp:
            t = Path(tmp) / dest.name
            t.write_text(text, encoding="utf-8")
            for g in re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", text):   # images travel with it
                src = find(g, dirs + [Path(d) for d in re.findall(r"\\graphicspath\{\{([^}]+)\}", text)])
                if src is None:
                    src = next((Path(d) / g for d in dirs if (Path(d) / g).is_file()), None)
                if src is not None:
                    (Path(tmp) / g).parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy(src, Path(tmp) / g)
            code, log = run_tex(t, Path(tmp), [])
            if code != 0:
                print(f"ERROR: the inlined copy does not compile alone: "
                      + next((ln for ln in log.splitlines() if ln.startswith('!')), 'see its log'))
                return 1
        print(f"ok     inlined copy {dest.name} compiles alone in an empty folder")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
