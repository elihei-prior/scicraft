#!/usr/bin/env python3
"""Static checks on a TikZ figure source, to run before compiling it.

Each rule is one small function that returns a message or None, so a rule can be added or removed without
touching the others. Every rule comes from a failure met in real figure work. Standard library only.

Errors (exit status 1):
  no-class       a tikzpicture but no \\documentclass and no \\input before \\begin{document}: compiled alone it
                 gives a blank 12 x 12 pt page; put the preamble on top
  no-body        \\begin{document} but no tikzpicture or axis after it
  no-figure      neither a tikzpicture nor an axis anywhere
  edge-label     "-- node {..}" with no position: the label sits on the line
  env-balance    begin/end counts of tikzpicture or axis differ
  brace-balance  unescaped { and } counts differ
  smooth-dash    plot[smooth cycle] coordinates joined by "--" (does not parse)
  newpage        \\newpage in a standalone file (frame decks need multi=tikzpicture)
  loop-var       a \\foreach variable that is a TeX macro (\\fi, \\o, \\c, \\d ...)
  foreach-body   a \\foreach whose body is an unbraced macro (\\foreach \\x in {1,2} \\figpoint{..}{..}): \\foreach
                 reads its body up to the next literal semicolon, so the command after the macro runs once per
                 item (a label printed three times over itself); brace the body
  sans-font      a sans text or sans math package, mathastext, or a sans \\familydefault: the style is the TeX
                 default font, decided once (a switch to a sans face and back cost a day of figure work)
Warnings (exit status 0 unless --strict):
  seedless-rand  rand or rnd with no \\pgfmathsetseed: the figure moves on every build
  frame-lock     a multi=tikzpicture deck with no "use as bounding box": the frames jitter
  t1-fontenc     \\usepackage[T1]{fontenc}: without cm-super the fonts come out as bitmaps
  long-label     a node text of 70 characters or more and no "text width": prose inside a figure, or a legend
                 line (one line that defines every symbol is part of the style and may be long)

Usage:
    python3 check_tikz_safety.py figure.tex [more.tex ...]
    python3 check_tikz_safety.py figures/            # every .tex below the folder
    python3 check_tikz_safety.py --strict figure.tex
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Callable, Optional

MACRO_LOOP_VARS = ("fi", "o", "O", "c", "d", "l", "L", "ss", "aa", "AA", "ae", "oe")
# Sans text and sans math packages. The names are written in two parts on purpose: the package keeps the
# retired sans theme out of this folder with a text search for these names, and this rule must not trip it.
SANS_PACKAGES = ("hel" "vet", "sans" "math", "sans" "mathfonts", "mathastext")
# Commands that end at their own semicolon, so a \foreach may take one as its body without braces.
PATH_COMMANDS = {"draw", "fill", "filldraw", "path", "node", "coordinate", "clip", "shade", "shadedraw", "pic",
                 "foreach", "addplot", "useasboundingbox", "matrix", "graph"}


def strip_comments(src: str) -> str:
    """Remove TeX comments (an unescaped % to the end of the line)."""
    return "\n".join(re.split(r"(?<!\\)%", line, maxsplit=1)[0] for line in src.splitlines())


def has_figure(code: str) -> bool:
    return "\\begin{tikzpicture}" in code or "\\begin{axis}" in code


def head(code: str) -> str:
    return code.split("\\begin{document}", 1)[0]


# ---------------------------------------------------------------- error rules
def rule_no_figure(code: str) -> Optional[str]:
    return None if has_figure(code) else "no-figure: no tikzpicture or axis environment in the file"


def rule_no_class(code: str) -> Optional[str]:
    if has_figure(code) and "\\documentclass" not in code and "\\input" not in head(code):
        return "no-class: no \\documentclass and no preamble \\input; put the preamble on top (alone it renders a blank page)"
    return None


def rule_no_body(code: str) -> Optional[str]:
    if "\\begin{document}" in code and not has_figure(code.split("\\begin{document}", 1)[1]):
        return "no-body: \\begin{document} is not followed by a figure"
    return None


def rule_edge_label(code: str) -> Optional[str]:
    for stmt in code.split(";"):
        if "\\draw" in stmt and re.search(r"--\s*node\s*\{", stmt):
            return "edge-label: '-- node {..}' without a position; write node[above], node[midway, right=4pt] ..."
    return None


def rule_long_label(code: str) -> Optional[str]:
    for m in re.finditer(r"\\node\b", code):
        stmt = code[m.start():code.find(";", m.start()) + 1]
        texts = re.findall(r"\{([^{}]*)\}\s*;?\s*$", stmt)
        if texts and len(texts[-1]) >= 70 and "text width" not in stmt:
            return (f"long-label: node text of {len(texts[-1])} characters without text width (fine for a one-line "
                    f"legend, not for prose): {' '.join(texts[-1].split())[:60]!r}")
    return None


def rule_env_balance(code: str) -> Optional[str]:
    for env in ("tikzpicture", "axis", "scope"):
        b, e = code.count(f"\\begin{{{env}}}"), code.count(f"\\end{{{env}}}")
        if b != e:
            return f"env-balance: {b} \\begin{{{env}}} against {e} \\end{{{env}}}"
    return None


def rule_brace_balance(code: str) -> Optional[str]:
    plain = code.replace("\\\\", "").replace("\\{", "").replace("\\}", "")   # drop \\ first
    if plain.count("{") != plain.count("}"):
        return f"brace-balance: {plain.count('{')} opening against {plain.count('}')} closing braces"
    return None


def rule_smooth_dash(code: str) -> Optional[str]:
    for m in re.finditer(r"smooth cycle[^\]]*\]\s*coordinates\s*\{", code):
        end = code.find("}", m.end())
        if "--" in code[m.end():end]:
            return "smooth-dash: plot[smooth cycle] coordinates must be separated by spaces, not '--'"
    return None


def rule_newpage(code: str) -> Optional[str]:
    if "{standalone}" in code and "\\newpage" in code:
        return "newpage: \\newpage in a standalone file; add multi=tikzpicture to the class options instead"
    return None


def rule_loop_var(code: str) -> Optional[str]:
    for var in re.findall(r"\\foreach\s*\\([A-Za-z]+)", code):
        if var in MACRO_LOOP_VARS:
            return f"loop-var: \\foreach \\{var} redefines a TeX macro; use \\x, \\y, \\k, \\n or \\ff"
    return None


def rule_foreach_body(code: str) -> Optional[str]:
    head_re = re.compile(r"\\foreach\s*\\[A-Za-z]+(?:\s*/\s*\\[A-Za-z]+)*\s*(?:\[[^\]]*\])?\s*in\s*\{")
    for m in head_re.finditer(code):
        depth, i = 1, m.end()
        while i < len(code) and depth:
            depth += {"{": 1, "}": -1}.get(code[i], 0) if code[i - 1] != "\\" else 0
            i += 1
        body = re.match(r"\s*\\([A-Za-z]+)", code[i:])
        if body and body.group(1) not in PATH_COMMANDS:
            return (f"foreach-body: \\foreach body \\{body.group(1)} is not braced; the loop runs to the next ';' and "
                    f"repeats the command after it; write {{\\{body.group(1)}...}}")
    return None


def rule_sans_font(code: str) -> Optional[str]:
    h = head(code)
    for name in SANS_PACKAGES:
        if re.search(r"\\usepackage(\[[^\]]*\])?\{" + name + r"\}", h):
            return f"sans-font: {name} in the preamble; the style is the TeX default font (Computer Modern, default math)"
    if re.search(r"\\familydefault\}\{\\sfdefault", h):
        return "sans-font: \\sfdefault as the family; the style is the TeX default font (Computer Modern, default math)"
    return None


# ---------------------------------------------------------------- warning rules
def rule_seedless_rand(code: str) -> Optional[str]:
    if re.search(r"\b(rand|rnd)\b", code) and "\\pgfmathsetseed" not in code:
        return "seedless-rand: rand/rnd with no \\pgfmathsetseed; the figure changes on every build"
    return None


def rule_frame_lock(code: str) -> Optional[str]:
    if "multi=tikzpicture" in code and has_figure(code) and "use as bounding box" not in code \
            and "useasboundingbox" not in code:
        return "frame-lock: frame deck without \\path[use as bounding box]; frames will jitter"
    return None


def rule_t1_fontenc(code: str) -> Optional[str]:
    if re.search(r"\\usepackage\[T1\]\{fontenc\}", head(code)):
        return "t1-fontenc: T1 fontenc without cm-super gives bitmap fonts; the style loads no fontenc"
    return None


ERRORS: list[Callable[[str], Optional[str]]] = [
    rule_no_figure, rule_no_class, rule_no_body, rule_edge_label, rule_env_balance,
    rule_brace_balance, rule_smooth_dash, rule_newpage, rule_loop_var, rule_foreach_body, rule_sans_font,
]
WARNINGS: list[Callable[[str], Optional[str]]] = [rule_seedless_rand, rule_frame_lock, rule_t1_fontenc, rule_long_label]


def check_text(src: str) -> tuple[list[str], list[str]]:
    """Return (errors, warnings) for one source text."""
    code = strip_comments(src)
    return [m for r in ERRORS if (m := r(code))], [m for r in WARNINGS if (m := r(code))]


def collect(paths: list[str]) -> list[Path]:
    out: list[Path] = []
    for p in map(Path, paths):
        out.extend(sorted(p.rglob("*.tex")) if p.is_dir() else [p])
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Static checks on TikZ figure sources before compiling.")
    ap.add_argument("paths", nargs="+", help=".tex files or folders (searched recursively)")
    ap.add_argument("--strict", action="store_true", help="warnings fail the run too")
    args = ap.parse_args(argv)
    files = collect(args.paths)
    bad = n_warn = 0
    for f in files:
        if not f.is_file():
            print(f"ERROR: {f}: no such file")
            bad += 1
            continue
        errs, warns = check_text(f.read_text(encoding="utf-8", errors="replace"))
        for msg in errs:
            print(f"ERROR: {f}: {msg}")
        for msg in warns:
            print(f"WARN:  {f}: {msg}")
        n_warn += len(warns)
        if errs or (args.strict and warns):
            bad += 1
    if bad:
        print(f"FAILED: {bad} of {len(files)} file(s)")
        return 1
    print(f"OK: {len(files)} file(s) pass ({n_warn} warning(s)).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
