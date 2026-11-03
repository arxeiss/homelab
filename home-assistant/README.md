# Home Assistant

| | |
|---|---|
| Install | Home Assistant OS, VM 102 on Proxmox (2 vCPU, 4 GB RAM, 50 GB) |
| Status | **Planned.** VM created, not deployed yet. See [Next steps](../TODO.md#home-assistant) |
| URL | http://TODO:8123 |
| Version | TODO |

## What is in git

[`config/`](config/) mirrors the YAML parts of HA's `/config`:

- `configuration.yaml`, `packages/` (one file per feature: automations, scripts, helpers together)
- YAML automations / scripts you care about versioning

**Not in git:** `.storage/` (UI-created config + tokens), databases, logs, `secrets.yaml`.
Anything created in the UI lives in `.storage/` and is covered only by HA backups. Write
it in YAML (a package) if you want it versioned here.

> [!WARNING]
> `zone.home` latitude/longitude reveals your address. Put it in `secrets.yaml`
> ([`config/secrets.example.yaml`](config/secrets.example.yaml) lists the keys).

## Syncing config with this repo

Options (pick one, TODO):

- **Studio Code Server add-on**: edit in HA, commit + push from its terminal.
- **Git pull add-on**: edit here, HA pulls from the repo.
- **Manual**: Samba/SSH add-on, copy files.

## Integrations

| Integration | Configured via | Notes |
|-------------|----------------|-------|
| ESPHome | UI | devices in VLAN 20, discovered via the router mDNS repeater, see [ESPHome](../esphome/README.md) |
| TODO | | |
