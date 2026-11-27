#!/usr/bin/env python3
"""Compile every LaTeX recipe of the reference files.

Each fenced ```latex block that holds a tikzpicture is put behind the preamble (assets/preamble.tex, the part above
its body marker) and compiled with pdflatex in a temporary folder. A block that is a complete document (it has a
\\documentclass, or \\input{preamble.tex}) is compiled as written, with assets/ on TeX's search path. Run it after
any change to the preamble or to a reference file: a recipe that no longer compiles no longer works.

A block without a tikzpicture that defines colors, styles or macros (\\definecolor, \\colorlet, \\tikzset,
\\pgfplotsset, \\newcommand) is its file's setup: it is placed after \\begin{document} for every later block of the
same file, as the file tells a reader to do. Any other block without a tikzpicture is listed as skipped. A block
with more than one tikzpicture, and every block of animation.md, is compiled as a frame deck (multi=tikzpicture).

  compile_snippets.py                               every reference file
  compile_snippets.py references/grammar.md         one file
  compile_snippets.py --keep out/ --png --sheet out/sheet.png    keep PDFs, render PNGs, one contact sheet
  compile_snippets.py --safety --audit              also run the safety check and the layout audit on each

Exit 0 when every recipe compiles (and, with --audit, reads 0 findings or only accepted ones), 1 otherwise. A
recipe that audits with known residues names them in a comment line `% audit-accept: KIND substring  # reason`.

Needs pdflatex on PATH; --png needs pdftoppm; --sheet needs Pillow; --audit needs PyMuPDF.
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import os
import re
import shutil
import subprocess
import sys
sys.dont_write_bytecode = True        # importing a sibling must not leave __pycache__ in the skill
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
sys.path.insert(0, str(SKILL / "assets"))
import figkit  # noqa: E402

FENCE = re.compile(r"(?ms)^```latex[^\n]*\n(.*?)^```\s*$")
SETUP = re.compile(r"\\(definecolor|colorlet|tikzset|pgfplotsset|newcommand|renewcommand)")
ACCEPT = re.compile(r"%\s*audit-accept:\s*(\S+)\s+(.*?)\s*(?:#\s*(.*))?$", re.M)


def snippets(md: Path):
    text = md.read_text(encoding="utf-8")
    return [(n, text.count("\n", 0, m.start()) + 1, m.group(1)) for n, m in enumerate(FENCE.finditer(text), 1)]


def assemble(body: str, deck: bool, pre: str) -> str:
    if "\\documentclass" in body or "\\input{preamble" in body:
        return body
    p = pre
    if deck:
        p = re.sub(r"\\documentclass\[border=([^\]]*)\]", r"\\documentclass[multi=tikzpicture,border=\1]", p, 1)
    return p + body + "\n\\end{document}\n"


def first_error(log: str) -> str:
    lines = log.splitlines()
    for i, ln in enumerate(lines):
        if ln.startswith("!"):
            where = next((x for x in lines[i + 1: i + 8] if x.startswith("l.")), "")
            return (ln + " " + where).strip()[:200]
    return "no error line in the log (timeout, or pdflatex missing)"


def build(job):
    md, n, line, body, pre, keep, png, safety, audit = job
    name = f"{md.stem}_{n:03d}"
    deck = md.stem == "animation" or body.count("\\begin{tikzpicture}") > 1
    note = ""
    with tempfile.TemporaryDirectory() as tmp:
        tex = Path(tmp) / f"{name}.tex"
        tex.write_text(assemble(body, deck, pre), encoding="utf-8")
        if safety:
            r = subprocess.run([sys.executable, str(HERE / "check_tikz_safety.py"), str(tex)], capture_output=True, text=True)
            if r.returncode != 0:
                note += " | safety: " + (r.stdout.strip().splitlines() or ["failed"])[0][-140:]
        env = dict(os.environ, TEXINPUTS=str(SKILL / "assets") + os.pathsep + os.environ.get("TEXINPUTS", ""))
        try:
            r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", tex.name], cwd=tmp,
                               capture_output=True, text=True, errors="replace", timeout=240, env=env)
            ok = r.returncode == 0 and (Path(tmp) / f"{name}.pdf").exists()
            err = "" if ok else first_error(r.stdout)
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            ok, err = False, type(e).__name__
        audit_bad = False
        if ok and audit and not deck:
            res = Path(tmp) / "accept.txt"
            res.write_text("\n".join(f"{k} {s}  # {why or ''}" for k, s, why in ACCEPT.findall(body)) + "\n")
            r = subprocess.run([sys.executable, str(HERE / "audit_layout.py"), str(Path(tmp) / f"{name}.pdf"),
                                "--accept", str(res)], capture_output=True, text=True)
            if r.returncode != 0:
                audit_bad = True
                first = [ln for ln in r.stdout.splitlines() if ln and not ln.startswith(("accepted", "stale"))][:2]
                note += " | audit: " + "; ".join(first)[:200]
        if ok and keep:
            keep.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(Path(tmp) / f"{name}.pdf", keep / f"{name}.pdf")
            if png:
                subprocess.run(["pdftoppm", "-r", "150", "-png", "-singlefile", "-f", "1", "-l", "1",
                                str(keep / f"{name}.pdf"), str(keep / name)], capture_output=True)
    return md.name, n, line, ok, err + note, audit_bad


def contact_sheet(pngs: list, out: Path, width: int = 420, cols: int = 4) -> None:
    from PIL import Image, ImageDraw
    tiles = []
    for p in pngs:
        im = Image.open(p).convert("RGB")
        r = min(1.0, width / im.width)
        tiles.append((p.stem, im.resize((max(1, int(im.width * r)), max(1, int(im.height * r))))))
    rows = [tiles[i:i + cols] for i in range(0, len(tiles), cols)]
    H = sum(max(im.height for _, im in row) + 22 for row in rows)
    sheet = Image.new("RGB", (cols * (width + 12), H), "white")
    d = ImageDraw.Draw(sheet)
    y = 0
    for row in rows:
        x = 0
        for name, im in row:
            sheet.paste(im, (x, y + 18))
            d.text((x + 2, y + 3), name, fill=(90, 90, 90))
            x += width + 12
        y += max(im.height for _, im in row) + 22
    sheet.save(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0], epilog=__doc__.split("\n\n", 1)[1],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="*", type=Path, help="markdown files (default: every file in references/)")
    ap.add_argument("--jobs", type=int, default=4, help="compilations in parallel (default 4)")
    ap.add_argument("--keep", type=Path, help="folder that receives the compiled PDFs")
    ap.add_argument("--png", action="store_true", help="with --keep: render page 1 of each PDF to PNG (pdftoppm)")
    ap.add_argument("--sheet", type=Path, help="with --keep --png: one contact sheet of every render (Pillow)")
    ap.add_argument("--safety", action="store_true", help="run check_tikz_safety.py on each assembled file")
    ap.add_argument("--audit", action="store_true", help="run audit_layout.py on each compiled recipe")
    a = ap.parse_args()
    if shutil.which("pdflatex") is None:
        print("compile_snippets: pdflatex is not on PATH")
        return 1
    files = a.files or sorted((SKILL / "references").glob("*.md"))
    pre = figkit.header(SKILL / "assets" / "preamble.tex", None)
    jobs, skipped, n_setup = [], [], 0
    for md in files:
        setup = ""
        for n, line, body in snippets(md):
            if "\\begin{tikzpicture}" not in body:
                if "\\documentclass" not in body and SETUP.search(body):
                    setup += body + "\n"
                    n_setup += 1
                else:
                    skipped.append(f"{md.name}#{n} (line {line})")
                continue
            jobs.append((md, n, line, setup + body if "\\documentclass" not in body else body, pre,
                         a.keep, a.png, a.safety, a.audit))
    failed, audited_bad = [], 0
    with cf.ThreadPoolExecutor(max_workers=max(1, a.jobs)) as ex:
        for name, n, line, ok, err, abad in ex.map(build, jobs):
            if not ok:
                failed.append(f"FAIL {name}#{n} (line {line}): {err}")
            elif err:
                print(f"note {name}#{n} (line {line}){err}")
            audited_bad += abad
    for f in failed:
        print(f)
    print(f"compile_snippets: {len(jobs)} recipes, {len(jobs) - len(failed)} compiled, {len(failed)} failed; "
          f"{n_setup} setup blocks used; {len(skipped)} blocks without a tikzpicture skipped"
          + (f"; {audited_bad} with audit findings" if a.audit else ""))
    if a.sheet and a.keep and a.png:
        pngs = sorted(p for p in a.keep.glob("*.png") if p.resolve() != a.sheet.resolve())
        if pngs:
            try:
                contact_sheet(pngs, a.sheet)
                print(f"contact sheet: {a.sheet} ({len(pngs)} renders)")
            except ImportError:
                print("contact sheet skipped: Pillow is not installed")
    return 1 if failed or audited_bad else 0


if __name__ == "__main__":
    sys.exit(main())
