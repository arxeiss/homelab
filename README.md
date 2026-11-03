# homelab

Documentation and configuration-as-code for my home network, servers and Home Assistant.

- **Docs site:** https://arxeiss.github.io/homelab/ (built from `docs/` by GitHub Actions)
- **Source of truth for the network:** [`inventory.yaml`](inventory.yaml)

> This repo is public. It contains **no secrets**: passwords live in a password manager,
> device secrets in git-ignored `secrets.yaml` files. Binary backups (Proxmox, UniFi `.unf`,
> MikroTik `.backup`, HA backups) live on backup storage, never here.
> See [docs/servers/backups.md](docs/servers/backups.md).

## Layout

```
inventory.yaml            devices, IPs, VLANs, links -> diagram + tables
network/
  mikrotik/export.rsc     `make mikrotik-export` (text config, secrets hidden)
  unifi/                  notes / exported settings (no .unf!)
  diagrams/               generated network.svg + hand-written *.dot
servers/proxmox/          sanitized host / guest config snippets
home-assistant/config/    HA YAML config (packages, automations, ...)
esphome/
  common/                 shared YAML (wifi, api, ota, ...)
  devices/<name>/         <name>.yaml + wiring.yaml + README.md + photos/
docs/                     MkDocs site (GitHub Pages)
scripts/                  generators used by the Makefile
```

## Quick start

```bash
sudo apt install graphviz   # needed for all diagrams
make setup                  # Python venv: mkdocs-material, wireviz, pre-commit
make hooks                  # pre-commit hooks incl. gitleaks secret scanning
make diagrams               # render network + wiring diagrams (SVG + PNG)
make serve                  # preview the docs at http://127.0.0.1:8000
make                        # list all targets
```

## Disaster? Start here

- Router died -> [docs/servers/runbooks/replace-router.md](docs/servers/runbooks/replace-router.md)
- Proxmox host died -> [docs/servers/runbooks/restore-proxmox.md](docs/servers/runbooks/restore-proxmox.md)
