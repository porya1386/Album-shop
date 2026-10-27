#!/usr/bin/env python3
"""Make the site's CSS theme-able.

Your CSS writes the three brand colours as fixed numbers (rgba(10,16,12,.7),
#f0c060, ...). A theme can only change a colour if the CSS asks for a variable.
This script rewrites those fixed numbers to the variables --night / --ink / --gold:

    rgba(10, 16, 12, .74)   ->  color-mix(in srgb, var(--night) 74%, transparent)
    #f0c060                 ->  var(--gold)

Usage (from the project folder):
    python tools/themeify.py            # dry run: only shows what would change
    python tools/themeify.py --write    # really change the files (a .orig copy is kept)

It never touches root.css or themes.css (they DEFINE the variables) and never
touches lines that define a custom property (--something: ...).
"""
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(".")
SKIP_DIRS = {".venv", "venv", "node_modules", ".git", "staticfiles", "static_root", "__pycache__", "admin", "rest_framework", "drf_yasg"}
SKIP_FILES = {"root.css", "themes.css"}

NIGHT = (10, 16, 12)      # #0a100c
INK = (253, 246, 232)     # #fdf6e8
GOLD = (240, 192, 96)     # #f0c060
DARK_PANELS = ("0c130e", "162019", "1a221c")      # dark green panels
PLACEHOLDERS = ("2a3a2e", "223027", "16241a")     # image placeholders / page tint

NAMES = {NIGHT: "--night", INK: "--ink", GOLD: "--gold"}


def pct(alpha: str) -> str:
    value = round(float(alpha) * 100, 1)
    return f"{int(value)}%" if value == int(value) else f"{value}%"


def mix(var: str, alpha: str) -> str:
    a = float(alpha)
    if a >= 1:
        return f"var({var})"
    return f"color-mix(in srgb, var({var}) {pct(alpha)}, transparent)"


def convert_line(line: str):
    count = 0

    def rgba_repl(m):
        nonlocal count
        rgb = (int(m.group(1)), int(m.group(2)), int(m.group(3)))
        if rgb in NAMES and m.group(4) is not None:
            count += 1
            return mix(NAMES[rgb], m.group(4))
        return m.group(0)

    line = re.sub(r"rgba\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*([\d.]+)\s*\)", rgba_repl, line)

    def hex_repl(m):
        nonlocal count
        h = m.group(1).lower()
        if h == "0a100c":
            out = "var(--night)"
        elif h == "fdf6e8":
            out = "var(--ink)"
        elif h == "f0c060":
            out = "var(--gold)"
        elif h in DARK_PANELS:
            out = "color-mix(in srgb, var(--night) 94%, var(--ink))"
        elif h in PLACEHOLDERS:
            out = "color-mix(in srgb, var(--night) 82%, var(--ink))"
        else:
            return m.group(0)
        count += 1
        return out

    line = re.sub(r"#([0-9a-fA-F]{6})\b", hex_repl, line)
    return line, count


def main():
    write = "--write" in sys.argv
    total_files = total = 0
    for path in sorted(ROOT.rglob("*.css")):
        if set(path.parts) & SKIP_DIRS or path.name in SKIP_FILES or path.name.endswith(".orig"):
            continue
        text = path.read_text(encoding="utf-8")
        out_lines, n = [], 0
        for line in text.split("\n"):
            if re.match(r"\s*--[\w-]+\s*:", line):        # a variable definition: leave it
                out_lines.append(line)
                continue
            new, c = convert_line(line)
            out_lines.append(new)
            n += c
        if n:
            total_files += 1
            total += n
            print(f"{'changed' if write else 'would change'}: {path}  ({n} colours)")
            if write:
                shutil.copy2(path, str(path) + ".orig")
                path.write_text("\n".join(out_lines), encoding="utf-8")
    print(f"\n{total} colours in {total_files} file(s).", "Done." if write else "Dry run: nothing was changed. Add --write to apply.")


if __name__ == "__main__":
    main()

# Yea nobody getting a JOB when ai write code like this in SECENDS 