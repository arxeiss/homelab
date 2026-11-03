# ESPHome

Each device lives in `esphome/devices/<name>/`:

| File | Content |
|------|---------|
| `<name>.yaml` | ESPHome config (firmware source) |
| `wiring.yaml` | [WireViz](https://github.com/wireviz/WireViz) wiring description -> `wiring.svg/png` via `make diagrams` |
| `README.md` | purpose, location, BOM, pinout, notes; shown on [ESPHome devices](../generated/esphome-devices.md) |
| `photos/` | photos of the actual build (strip EXIF GPS!) |
| `components/` | optional custom C++ components |

Shared config is in `esphome/common/` and included with `packages:`.

## New device

```bash
cp -r esphome/devices/_template esphome/devices/my-device
mv esphome/devices/my-device/_template.yaml esphome/devices/my-device/my-device.yaml
# edit name in substitutions, wiring.yaml, README.md
make diagrams
make esphome-run DEVICE=my-device     # first flash over USB: see README of the template
```

## Secrets

`esphome/secrets.yaml` (git-ignored) holds WiFi credentials and keys;
`esphome/secrets.example.yaml` documents the keys. `esphome/common/secrets.yaml` is a symlink to it,
because ESPHome resolves `!secret` relative to the file that uses it.

## Bigger projects

For custom PCBs or anything more than a few wires, use KiCad (text-based files, git-friendly)
in a `hardware/` subfolder of the device and export the schematic to PDF/SVG.
