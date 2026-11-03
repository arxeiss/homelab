# Home Assistant

| | |
|---|---|
| Install | Home Assistant OS, VM on Proxmox |
| URL | http://192.168.1.20:8123 (TODO) |
| Version | TODO |

## What is in git

`home-assistant/config/` mirrors the YAML parts of HA's `/config`:

- `configuration.yaml`, `packages/` (one file per feature: automations, scripts, helpers together)
- YAML automations / scripts you care about versioning

**Not in git:** `.storage/` (UI-created config + tokens), databases, logs, `secrets.yaml`.
Anything created in the UI lives in `.storage/` and is covered only by HA backups. Write
it in YAML (a package) if you want it versioned here.

!!! warning "Check before committing"
    `zone.home` latitude/longitude reveals your address. Put it in `secrets.yaml`.

## Syncing config with this repo

Options (pick one, TODO):

- **Studio Code Server add-on**: edit in HA, commit + push from its terminal.
- **Git pull add-on**: edit here, HA pulls from the repo.
- **Manual**: Samba/SSH add-on, copy files.

## Integrations

| Integration | Configured via | Notes |
|-------------|----------------|-------|
| ESPHome | UI | devices in VLAN 20, see [ESPHome](../esphome/index.md) |
| TODO | | |
