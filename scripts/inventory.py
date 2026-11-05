#!/usr/bin/env python3
"""Render inventory.yaml as a D2 network diagram or Markdown tables.

Usage:
    inventory.py d2       inventory.yaml -o build/network.d2
    inventory.py markdown inventory.yaml -o network/inventory.md

The D2 file imports the shared look from assets/d2/style.d2; `make generate`
renders it to network/diagrams/network.svg.
"""

import argparse
import os
import sys
from pathlib import Path

import yaml

ASSETS = Path(__file__).resolve().parent.parent / "assets" / "d2"

# inventory type -> (style.d2 class, icon in assets/d2/icons/)
TYPE_STYLE = {
    "internet": ("internet", "world"),
    "router":   ("network", "router"),
    "switch":   ("switch", "topology-star-3"),
    "ap":       ("wireless", "access-point"),
    "server":   ("compute", "server"),
    "guest":    ("guest", None),
    "client":   ("client", None),
}
GUEST_ICON = {"LXC": "box", "VM": "cube"}
# Wired clients have no type of their own; pick an icon from the name/label.
CLIENT_ICON = (("camera", "device-cctv"), ("nvr", "video"), ("alarm", "shield-lock"))


def d2_str(s: str) -> str:
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


def device_lines(dev: dict) -> list[str]:
    lines = [dev["name"]]
    for key in ("label", "vendor", "model"):
        # Server vendor (Proxmox VE x.y) is already the title of its group box.
        if dev.get(key) and not (dev["type"] == "server" and key == "vendor"):
            lines.append(str(dev[key]))
    if dev.get("kind"):
        lines.append(f"{dev['kind']} {dev.get('vmid', '')}".strip())
    if dev.get("ip"):
        lines.append(dev["ip"] + (" (DHCP)" if dev.get("ip_mode") == "dhcp" else ""))
    return lines


def device_icon(dev: dict) -> str | None:
    cls, icon = TYPE_STYLE.get(dev["type"], ("guest", None))
    if dev["type"] == "guest":
        icon = GUEST_ICON.get(dev.get("kind", ""))
    if dev["type"] == "client":
        text = f"{dev['name']} {dev.get('label', '')}".lower()
        icon = next((i for word, i in CLIENT_ICON if word in text), None)
    return icon


def render_d2(inv: dict, out_dir: Path) -> str:
    vlans = {v["id"]: v for v in inv.get("vlans", [])}
    devices = inv.get("devices", [])
    rel = Path(os.path.relpath(ASSETS, out_dir.resolve()))
    out = [
        "# Generated from inventory.yaml by scripts/inventory.py - do not edit.",
        f"...@{(rel / 'style.d2').as_posix()}",
        "direction: down",
        "",
    ]

    def node(dev: dict, indent: str) -> list[str]:
        cls = TYPE_STYLE.get(dev["type"], ("guest", None))[0]
        if "TODO" in str(dev.get("ip", "")):
            cls = "todo"
        lines = device_lines(dev)
        icon = device_icon(dev)
        # D2 sizes icons to the shape, so size the card from its text and keep
        # the icon in a fixed column on the left.
        width = int(7.6 * max(len(line) for line in lines)) + (88 if icon else 40)
        height = 20 * len(lines) + 34
        body = [f"class: {cls}", f"width: {width}", f"height: {height}"]
        if icon:
            body += [f"icon: {(rel / 'icons' / (icon + '.svg')).as_posix()}",
                     "icon.near: center-left", "label.near: center-right"]
        pad = indent + "  "
        return ([f"{indent}{d2_str(dev['name'])}: {d2_str(chr(10).join(lines))} {{"]
                + [pad + b for b in body] + [f"{indent}}}"])

    guests_by_host: dict[str, list[dict]] = {}
    for dev in devices:
        if dev["type"] == "guest":
            guests_by_host.setdefault(dev["host"], []).append(dev)

    path: dict[str, str] = {}
    for dev in devices:
        if dev["type"] == "guest":
            continue
        guests = guests_by_host.get(dev["name"])
        if not guests:
            out += node(dev, "")
            path[dev["name"]] = d2_str(dev["name"])
            continue
        box = d2_str(dev["name"] + "-host")
        out.append(f"{box}: {d2_str(dev.get('vendor', dev['name']))} {{")
        out.append("  class: group")
        out += node(dev, "  ")
        path[dev["name"]] = f"{box}.{d2_str(dev['name'])}"
        for g in guests:
            out += node(g, "  ")
            out.append(f"  {d2_str(dev['name'])} -- {d2_str(g['name'])}: {{ class: soft }}")
        out.append("}")

    out.append("")
    for link in inv.get("links", []):
        carried = link.get("vlans", [])
        ports = " → ".join(p for p in (link.get("a_port"), link.get("b_port")) if p)
        parts = [ports] if ports else []
        if carried:
            parts.append("VLAN " + ",".join(str(v) for v in carried))
        edge = f"{path[link['a']]} -- {path[link['b']]}: {d2_str(' · '.join(parts))}"
        if len(carried) == 1:
            color = vlans.get(carried[0], {}).get("color", "#868E96")
            out.append(f'{edge} {{ class: cable; style.stroke: "{color}" }}')
        else:
            out.append(f"{edge} {{ class: {'trunk' if carried else 'cable'} }}")

    if vlans:
        out += ["", "vars: {", "  d2-legend: {"]
        for v in vlans.values():
            text = "VLAN {id} {name} · {subnet}".format(**v)
            color = d2_str(v.get("color", "#868E96"))
            out.append(f"    v{v['id']}: {d2_str(text)} {{ style: {{ fill: {color}; stroke: {color} }} }}")
        out.append('    trunk: "Trunk (several VLANs)" { style: { fill: "#495057"; stroke: "#495057" } }')
        out += ["  }", "}"]
    return "\n".join(out) + "\n"


def md_table(headers: list[str], rows: list[list]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    for row in rows:
        lines.append("| " + " | ".join("" if c is None else str(c) for c in row) + " |")
    return "\n".join(lines)


def render_markdown(inv: dict, out_dir: Path) -> str:
    devices = inv.get("devices", [])

    def name(d: dict) -> str:
        """Device name, linked to its docs page (path relative to repo root)."""
        if not d.get("docs"):
            return d["name"]
        return f"[{d['name']}]({os.path.relpath(d['docs'], out_dir)})"

    parts = [
        "<!-- Generated by `make generate` from inventory.yaml - do not edit. -->",
        "# Inventory",
        "",
        "> [!NOTE]",
        "> Generated from [`inventory.yaml`](" + os.path.relpath("inventory.yaml", out_dir) + ")."
        " Edit that file and run `make generate`, not this page.",
        "",
        "## VLANs",
        "",
        md_table(
            ["ID", "Name", "Subnet", "Gateway", "DHCP", "Purpose"],
            [[v["id"], v["name"], v["subnet"], v.get("gateway"), v.get("dhcp"), v.get("purpose")]
             for v in inv.get("vlans", [])],
        ),
        "",
        "## Devices",
        "",
        md_table(
            ["Name", "Type", "Vendor", "Model", "Firmware", "IP", "IP mode", "Location"],
            [[name(d), d["type"], d.get("vendor") or d.get("label"), d.get("model"), d.get("os"), d.get("ip"),
              d.get("ip_mode"), d.get("location")]
             for d in devices if d["type"] != "guest"],
        ),
        "",
        "## Proxmox guests",
        "",
        md_table(
            ["VMID", "Name", "Kind", "Host", "Runs", "IP", "IP mode", "VLANs"],
            [[d.get("vmid"), name(d), d.get("kind"), d.get("host"), d.get("vendor"), d.get("ip"),
              d.get("ip_mode"), ", ".join(str(v) for v in d.get("vlans", []))]
             for d in devices if d["type"] == "guest"],
        ),
        "",
        "## Physical links",
        "",
        md_table(
            ["A", "Port", "B", "Port", "VLANs"],
            [[l["a"], l.get("a_port"), l["b"], l.get("b_port"), ", ".join(str(v) for v in l.get("vlans", []))]
             for l in inv.get("links", [])],
        ),
        "",
        "## WiFi",
        "",
        md_table(
            ["SSID", "VLAN", "Bands", "Security", "Served by"],
            [[w["ssid"], w.get("vlan"), ", ".join(w.get("bands", [])), w.get("security"),
              ", ".join(w.get("served_by", []))]
             for w in inv.get("wifi", [])],
        ),
        "",
    ]
    return "\n".join(parts)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("format", choices=["d2", "markdown"])
    parser.add_argument("inventory", type=Path)
    parser.add_argument("-o", "--output", type=Path, required=True)
    args = parser.parse_args()

    inv = yaml.safe_load(args.inventory.read_text())
    if args.format == "d2":
        text = render_d2(inv, args.output.parent)
    else:
        text = render_markdown(inv, args.output.parent)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
