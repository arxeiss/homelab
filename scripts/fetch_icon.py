#!/usr/bin/env python3
"""Download Tabler icons into assets/d2/icons/, made D2-compatible.

Usage:
    fetch_icon.py thermometer droplet ...     (names from https://tabler.io/icons)

D2 0.9 imports SVG icons as vector paths and rejects zero-length subpaths, which
Tabler uses in two places. Both are rewritten without changing how the icon looks:
  "M3 13m0 2..."   (move, then move again)  -> "M3 15..."
  "M17 17l0 .01"   (round-capped "dot")     -> small filled circle
The stroke colour is fixed because currentColor has no meaning inside a diagram.
"""

import re
import sys
import urllib.request
from pathlib import Path

VERSION = "3.24.0"
URL = "https://cdn.jsdelivr.net/npm/@tabler/icons@{v}/icons/outline/{name}.svg"
COLOR = "#3B4A5A"
OUT = Path(__file__).resolve().parent.parent / "assets" / "d2" / "icons"

NUM = r"(-?[\d.]+)"
DOUBLE_MOVE = re.compile(rf"M{NUM}[ ,]{NUM}m{NUM}[ ,]{NUM}")
DOT = re.compile(rf'<path d="M{NUM} {NUM}(?:l0 -?\.01|l-?\.01 0|v-?\.01|h-?\.01)"\s*/>')


def fix(svg: str) -> str:
    svg = svg.replace("currentColor", COLOR)
    svg = re.sub(r'\s*class="[^"]*"', "", svg)
    svg = DOUBLE_MOVE.sub(
        lambda m: f"M{float(m[1]) + float(m[3]):g} {float(m[2]) + float(m[4]):g}", svg)
    return DOT.sub(
        lambda m: f'<circle cx="{m[1]}" cy="{m[2]}" r="1.2" fill="{COLOR}" stroke="none" />', svg)


def main(names: list[str]) -> int:
    if not names:
        print(__doc__)
        return 1
    OUT.mkdir(parents=True, exist_ok=True)
    for name in names:
        with urllib.request.urlopen(URL.format(v=VERSION, name=name)) as resp:
            svg = resp.read().decode()
        (OUT / f"{name}.svg").write_text(fix(svg).rstrip() + "\n")
        print(f"assets/d2/icons/{name}.svg")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
