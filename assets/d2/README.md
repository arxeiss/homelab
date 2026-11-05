# Diagrams (D2)

Every `*.d2` file in the repo is rendered by `make generate` (D2 runs in Docker) to an `.svg` next to it.
Start a diagram with `...@<relative path>/assets/d2/style.d2` and use the classes from
[`style.d2`](style.d2). Example: [`proxmox-storage.d2`](../../network/diagrams/proxmox-storage.d2).

- When a shape has an icon, also set `width`/`height`, `icon.near: center-left` and
  `label.near: center-right`. Otherwise D2 makes the icon huge.
- Icons are from [Tabler](https://tabler.io/icons) ([MIT](icons/LICENSE)). To add one, run `make icon NAME="thermometer"`.
  Don't copy raw Tabler SVGs, because D2 can't import them.
