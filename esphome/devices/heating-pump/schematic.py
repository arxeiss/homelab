#!/usr/bin/env python3
"""Schematic for heating-pump -> schematic.svg (run by `make generate`, stdlib only).

Style: power rails (+5 V, +3.3 V on top, +12 V at the bottom), ground symbols instead of a
GND rail (all GND is one common net), modules as boxes with labelled pins.
Layout is hand-placed so that no two wires cross.
"""
import sys
from pathlib import Path

# ---- net colours -------------------------------------------------------------
C12 = "#D62828"   # +12 V
C5 = "#F08C00"    # +5 V
C33 = "#7B4FC9"   # +3.3 V
CGND = "#212529"  # GND
CPWM = "#2B8A3E"  # PWM
CDATA = "#1C7ED6"  # DHT data
# UTP wire colours (T568B)
UTP = {
    1: ("#F08C00", True), 2: ("#F08C00", False), 3: ("#2B8A3E", True), 4: ("#1C7ED6", False),
    5: ("#1C7ED6", True), 6: ("#2B8A3E", False), 7: ("#8B5A2B", True), 8: ("#8B5A2B", False),
}
FONT = "Helvetica, Arial, sans-serif"
STUB = 18  # pin lead length

out: list[str] = []


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(x, y, s, size=13, anchor="middle", weight="normal", color="#212529", italic=False):
    style = ' font-style="italic"' if italic else ""
    for i, line in enumerate(s.split("\n")):
        out.append(f'<text x="{x}" y="{y + i * (size + 3)}" font-size="{size}" text-anchor="{anchor}" '
                   f'font-weight="{weight}" fill="{color}" font-family="{FONT}"{style}>{esc(line)}</text>')


def wire(pts, color, width=2.5, dash=False):
    d = " ".join(f"{x},{y}" for x, y in pts)
    da = ' stroke-dasharray="10 5"' if dash else ""
    out.append(f'<polyline points="{d}" fill="none" stroke="{color}" stroke-width="{width}" '
               f'stroke-linejoin="round" stroke-linecap="round"{da}/>')


def dot(x, y, color):
    out.append(f'<circle cx="{x}" cy="{y}" r="4.5" fill="{color}"/>')


def gnd(x, y):
    """Ground symbol hanging from (x, y)."""
    wire([(x, y), (x, y + 14)], CGND)
    for i, w in enumerate((14, 9, 4)):
        wire([(x - w, y + 14 + i * 5), (x + w, y + 14 + i * 5)], CGND, 2)


def cap(x, y_top, y_bot, label):
    """Polarised capacitor between a rail at y_top and ground at y_bot (vertical)."""
    mid = (y_top + y_bot) / 2
    wire([(x, y_top), (x, mid - 5)], C33)
    wire([(x - 14, mid - 5), (x + 14, mid - 5)], C33, 3)
    out.append(f'<path d="M {x - 14} {mid + 9} Q {x} {mid + 1} {x + 14} {mid + 9}" fill="none" '
               f'stroke="{CGND}" stroke-width="3"/>')
    text(x - 20, mid - 10, "+", 13, "middle", "bold")
    wire([(x, mid + 5), (x, y_bot)], CGND)
    gnd(x, y_bot)
    text(x + 22, mid, label, 12, "start")


class Box:
    def __init__(self, x, y, w, h, title, sub="", fill="#FFFFFF", stroke="#495057", title_top=False):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.pins: dict[str, tuple[float, float]] = {}
        out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" '
                   f'stroke="{stroke}" stroke-width="2"/>')
        cy = y + 28 if title_top else y + h / 2 - (8 if sub else 0) - 6 * (title.count("\n"))
        text(x + w / 2, cy, title, 14, weight="bold")
        if sub:
            text(x + w / 2, cy + 18 + 17 * title.count("\n"), sub, 11, color="#495057")

    def pin(self, name, side, pos, label=None, color="#495057"):
        """pos = absolute x (top/bottom) or y (left/right). Returns the lead end point."""
        label = name if label is None else label
        if side == "top":
            p0, p1 = (pos, self.y), (pos, self.y - STUB)
            text(pos, self.y + 15, label, 11)
        elif side == "bottom":
            p0, p1 = (pos, self.y + self.h), (pos, self.y + self.h + STUB)
            text(pos, self.y + self.h - 7, label, 11)
        elif side == "left":
            p0, p1 = (self.x, pos), (self.x - STUB, pos)
            text(self.x + 6, pos + 4, label, 11, "start")
        else:
            p0, p1 = (self.x + self.w, pos), (self.x + self.w + STUB, pos)
            text(self.x + self.w - 6, pos + 4, label, 11, "end")
        wire([p0, p1], color, 2)
        self.pins[name] = p1
        return p1


def group(x, y, w, h, label):
    out.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="14" fill="#FAF8FD" '
               f'stroke="#B9A5DA" stroke-width="2" stroke-dasharray="8 5"/>')
    text(x + 16, y + 24, label, 15, "start", "bold", "#495057")


# ---- layout ------------------------------------------------------------------
W, H = 2870, 960
DX = 150  # pump side shift
Y5, Y33, Y12 = 70, 110, 740
TOP = 200  # top of the module row

group(20, 150, 1890, 650, "Controller board (in the rack)")
group(2000 + DX, 150, 700, 650, "At the pump (~5 m away)")

# rail labels
text(30, Y5 + 5, "+5 V", 14, "start", "bold", C5)
text(30, Y33 + 5, "+3.3 V", 14, "start", "bold", C33)
text(30, Y12 + 5, "+12 V", 14, "start", "bold", C12)

# 12 V input
psu = Box(40, 300, 130, 90, "12 V DC", "power supply", "#F1F3F5")
p12 = psu.pin("+12V", "bottom", 75, "+12V", C12)
pg = psu.pin("GND", "bottom", 135, "GND", CGND)
gnd(*pg)

# Buck 12 -> 5 V
buck = Box(230, TOP, 170, 130, "Buck 12 -> 5 V", "SET TO 5.0 V FIRST\n(dratek 3133)", "#F1EBF9", "#8E6CC0")
b_in = buck.pin("IN+", "bottom", 255, "IN+", C12)
b_ing = buck.pin("IN-", "bottom", 310, "IN-", CGND)
b_outg = buck.pin("OUT-", "bottom", 345, "OUT-", CGND)
b_out = buck.pin("OUT+", "top", 375, "OUT+", C5)
gnd(*b_ing)
gnd(*b_outg)

# AMS1117
ldo = Box(460, TOP, 150, 110, "AMS1117", "5 -> 3.3 V, 800 mA", "#F1EBF9", "#8E6CC0")
l_in = ldo.pin("VIN", "top", 485, "VIN", C5)
l_out = ldo.pin("VOUT", "top", 585, "VOUT", C33)
l_g = ldo.pin("GND", "bottom", 535, "GND", CGND)
gnd(*l_g)

# 470 uF bulk cap
cap(670, Y33, 300, "C1\n470 µF\n10 V")

# ESP8266
esp = Box(760, TOP, 220, 230, "ESP8266", "ESP-12F board\n(dratek 1351)", "#E6F6F4", "#2A9D8F")
e_vcc = esp.pin("VCC", "top", 800, "VCC (3V3)", C33)
e_g = esp.pin("GND", "bottom", 800, "GND", CGND)
e_14 = esp.pin("GPIO14", "right", 260, "GPIO14", CDATA)
e_12 = esp.pin("GPIO12", "right", 310, "GPIO12", CDATA)
e_5 = esp.pin("GPIO5", "right", 390, "GPIO5", CPWM)
gnd(*e_g)
text(870, TOP + 250, "GPIOs proposed - check\nonboard LED / buttons", 11, color="#868E96", italic=True)

# Level shifter
llc = Box(1080, TOP, 230, 180, "Level shifter", "BSS138, ch 3+4 unused\n(dratek 1481)", "#F1EBF9", "#8E6CC0")
s_lv = llc.pin("LV", "top", 1110, "LV", C33)
s_hv = llc.pin("HV", "top", 1280, "HV", C5)
s_lv1 = llc.pin("LV1", "left", 260, "LV1", CDATA)
s_lv2 = llc.pin("LV2", "left", 310, "LV2", CDATA)
s_hv1 = llc.pin("HV1", "right", 260, "HV1", CDATA)
s_hv2 = llc.pin("HV2", "right", 310, "HV2", CDATA)
s_g = llc.pin("GND", "bottom", 1195, "GND", CGND)
gnd(*s_g)

# Rack DHT22
dr = Box(1400, TOP, 160, 120, "DHT22 #1", "rack\n(module, pull-up on board)", "#E6F6F4", "#2A9D8F")
d1_v = dr.pin("VDD", "top", 1430, "VDD", C5)
d1_d = dr.pin("DATA", "left", 260, "DATA", CDATA)
d1_g = dr.pin("GND", "bottom", 1520, "GND", CGND)
gnd(*d1_g)

# MOSFET module
fet = Box(1480, 410, 230, 180, "MOSFET module", "FR120N\n(dratek 123950)", "#F1EBF9", "#8E6CC0",
          title_top=True)
f_sig = fet.pin("SIG", "left", 515, "SIG / PWM", CPWM)
f_cg = fet.pin("CG", "bottom", 1520, "GND", CGND)
f_vin = fet.pin("VIN", "bottom", 1590, "VIN+", C12)
f_pg = fet.pin("PG", "bottom", 1660, "VIN-", CGND)
f_op = fet.pin("OUT+", "right", 490, "OUT+ (=VIN+)", CPWM)
f_om = fet.pin("OUT-", "right", 540, "OUT- (switched)", CPWM)
gnd(*f_cg)
gnd(*f_pg)

# UTP terminals (same order at both ends, T568B pin numbers)
XPINS = [(4, "+5V", 230, C5), (3, "DATA", 340, CDATA), (1, "PWM+", 490, CPWM), (2, "PWM-", 540, CPWM),
         (5, "GND", 600, CGND), (6, "GND", 640, CGND), (7, "spare", 680, CGND), (8, "spare", 720, CGND)]
x1 = Box(1810, 190, 70, 570, "", "", "#FFFFFF")
x2 = Box(2030 + DX, 190, 70, 570, "", "", "#FFFFFF")
text(1845, 782, "X1", 13, weight="bold")
text(2065 + DX, 782, "X2", 13, weight="bold")
for n, name, y, col in XPINS:
    x1.pin(f"{n}", "left", y, "", col)
    x2.pin(f"{n}", "right", y, "", col)
    text(1845, y + 4, f"{n} {name}", 11)
    text(2065 + DX, y + 4, f"{n} {name}", 11)
    c, striped = UTP[n]
    # the cable itself: white base + colour (striped = white/colour)
    a, b = (1880, y), (2030 + DX, y)
    wire([a, b], "#ADB5BD" if striped else c, 6)
    if striped:
        wire([a, b], c, 6, dash=True)
text(1955 + DX / 2, 182, "UTP cat5e ~5 m", 13, weight="bold")
text(1955 + DX / 2, 790, "T568B colours\n(dashed = white/colour)", 11, color="#495057")

# ---- rails -------------------------------------------------------------------
wire([(b_out[0], Y5), (1790, Y5)], C5, 3.5)
wire([(l_out[0], Y33), (s_lv[0], Y33)], C33, 3.5)
wire([(p12[0], Y12), (f_vin[0], Y12)], C12, 3.5)

# drops to rails
for p, y, c in [(b_out, Y5, C5), (l_in, Y5, C5), (s_hv, Y5, C5), (d1_v, Y5, C5),
                (l_out, Y33, C33), (e_vcc, Y33, C33), (s_lv, Y33, C33),
                (p12, Y12, C12), (b_in, Y12, C12), (f_vin, Y12, C12)]:
    wire([p, (p[0], y)], c)
    if p not in (b_out, l_out, s_lv, p12, f_vin):  # T junctions only (rail ends are corners)
        dot(p[0], y, c)
dot(670, Y33, C33)

# ---- signals -----------------------------------------------------------------
wire([e_14, s_lv1], CDATA)
wire([e_12, s_lv2], CDATA)
wire([s_hv1, d1_d], CDATA)
# GPIO5 -> MOSFET SIG, under the level shifter
wire([e_5, (1010, 390), (1010, 515), f_sig], CPWM)
# HV2 -> X1 DATA, between the rack sensor and the MOSFET
wire([s_hv2, (1350, 310), (1350, 390), (1780, 390), (1780, 340), x1.pins["3"]], CDATA)
# +5 V -> X1
wire([(1790, Y5), (1790, 230), x1.pins["4"]], C5)
# MOSFET -> X1
wire([f_op, x1.pins["1"]], CPWM)
wire([f_om, x1.pins["2"]], CPWM)
# X1 GND pins 5-8 bussed, to ground (spare pair grounded at THIS end only)
wire([x1.pins["5"], (1772, 600), (1772, 720), x1.pins["8"]], CGND)
for n, y in [("6", 640), ("7", 680)]:
    wire([x1.pins[n], (1772, y)], CGND)
    dot(1772, y, CGND)
dot(1772, 600, CGND)
wire([(1772, 720), (1750, 720)], CGND)
gnd(1750, 720)

# ---- pump side -----------------------------------------------------------------
dp = Box(2230 + DX, 270, 170, 130, "DHT22 #2", "at the pump\n(module, pull-up on board)", "#E6F6F4", "#2A9D8F",
         title_top=True)
d2_v = dp.pin("VDD", "top", 2260 + DX, "VDD", C5)
d2_d = dp.pin("DATA", "left", 340, "DATA", CDATA)
d2_g = dp.pin("GND", "right", 375, "GND", CGND)

pump = Box(2290 + DX, 440, 260, 140, "Grundfos ALPHA1", "PWM signal cable - check\nwire colours on its label",
           "#FDF2E1", "#E09B3D", title_top=True)
pu_in = pump.pin("IN", "left", 490, "PWM in", CPWM)
pu_ref = pump.pin("REF", "left", 540, "signal GND / ref", CPWM)

wire([x2.pins["4"], (2260 + DX, 230), d2_v], C5)
wire([x2.pins["3"], d2_d], CDATA)
wire([x2.pins["1"], pu_in], CPWM)
wire([x2.pins["2"], pu_ref], CPWM)
# GND: X2 pins 5+6 -> DHT22 GND, routed round the pump
bx = 2130 + DX
wire([x2.pins["5"], (bx, 600), (bx, 640), x2.pins["6"]], CGND)
dot(bx, 600, CGND)
wire([(bx, 640), (bx, 660), (2600 + DX, 660), (2600 + DX, 375), d2_g], CGND)
dot(bx, 640, CGND)
text(bx - 5, 700, "7, 8 not connected - insulate", 11, "start", color="#868E96", italic=True)

# 230 V note
wire([(2420 + DX, 615), (2420 + DX, 580)], "#868E96", 2, dash=True)
text(2420 + DX, 632, "230 V mains: separate, NOT via this board", 11, color="#868E96", italic=True)

# ---- title + legend ------------------------------------------------------------
text(30, 30, "heating-pump - schematic", 20, "start", "bold")
lx = 1100
text(lx, 30, "Legend:", 12, "start", "bold")
for i, (c, name) in enumerate([(C12, "+12 V"), (C5, "+5 V"), (C33, "+3.3 V"), (CGND, "GND"),
                               (CPWM, "PWM"), (CDATA, "DHT data")]):
    x = lx + 70 + i * 110
    wire([(x, 26), (x + 30, 26)], c, 3.5)
    text(x + 36, 30, name, 12, "start")
gnd(lx + 760, 14)
text(lx + 782, 30, "= common GND (all connected)", 12, "start")
text(30, 850,
     "FR120N terminals: PWM/GND header, screw terminals VIN+ / VIN- / OUT- (OUT+ = VIN+). "
     "Match the silkscreen on the module.",
     12, "start", color="#495057")
text(30, 872, "Dots = junctions. Wires that touch without a dot are not connected (there are none here).",
     12, "start", color="#495057")

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H - 60}" viewBox="0 0 {W} {H - 60}">\n'
       f'<rect width="100%" height="100%" fill="#FFFFFF"/>\n' + "\n".join(out) + "\n</svg>\n")
dst = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("schematic.svg")
dst.write_text(svg)
