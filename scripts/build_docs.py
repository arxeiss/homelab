#!/usr/bin/env python3
"""Collect diagrams and ESPHome device READMEs into docs/generated/ for MkDocs.

- network/diagrams/*.{svg,png}       -> docs/generated/network/
- esphome/devices/<dev>/README.md    -> one section in docs/generated/esphome-devices.md
- esphome/devices/<dev>/ assets      -> docs/generated/esphome/<dev>/
Device folders starting with "_" (templates) are skipped.
"""

import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GEN = ROOT / "docs" / "generated"
ASSET_SUFFIXES = {".svg", ".png", ".jpg", ".jpeg", ".webp", ".gif", ".pdf"}
# Relative markdown links/images: ](path) that are not URLs, anchors or absolute
REL_LINK = re.compile(r"(\]\()(?!https?://|#|/)([^)\s]+)(\))")


def copy_network_diagrams() -> None:
    dst = GEN / "network"
    dst.mkdir(parents=True, exist_ok=True)
    for f in (ROOT / "network" / "diagrams").iterdir():
        if f.suffix in {".svg", ".png"}:
            shutil.copy2(f, dst / f.name)


def rewrite_readme(body: str, dev_name: str) -> str:
    """Demote headings one level and point relative links at copied assets (skips code fences)."""
    out, in_fence = [], False
    for line in body.splitlines():
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
        elif not in_fence:
            if line.startswith("#"):
                line = "#" + line
            line = REL_LINK.sub(lambda m: f"{m[1]}esphome/{dev_name}/{m[2]}{m[3]}", line)
        out.append(line)
    return "\n".join(out)


def build_esphome_page() -> None:
    devices_dir = ROOT / "esphome" / "devices"
    devices = sorted(d for d in devices_dir.iterdir() if d.is_dir() and not d.name.startswith("_"))
    parts = [
        "# ESPHome devices",
        "",
        "!!! note",
        "    Generated from `esphome/devices/*/README.md` - edit those files, not this page.",
        "",
    ]
    if not devices:
        parts.append("No devices yet. Copy `esphome/devices/_template/` to start one.")

    for dev in devices:
        asset_dst = GEN / "esphome" / dev.name
        asset_dst.mkdir(parents=True, exist_ok=True)
        for f in dev.rglob("*"):
            if f.is_file() and f.suffix.lower() in ASSET_SUFFIXES:
                target = asset_dst / f.relative_to(dev)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, target)

        readme = dev / "README.md"
        body = readme.read_text() if readme.exists() else f"# {dev.name}\n\n_No README yet._\n"
        parts += [rewrite_readme(body, dev.name).rstrip(), ""]

    (GEN / "esphome-devices.md").write_text("\n".join(parts) + "\n")


def main() -> int:
    GEN.mkdir(parents=True, exist_ok=True)
    copy_network_diagrams()
    build_esphome_page()
    return 0


if __name__ == "__main__":
    sys.exit(main())
