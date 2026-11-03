# homelab

Documentation of my home network, servers and smart home.

<object data="generated/network/network.svg" type="image/svg+xml" style="width:100%">
  <img src="generated/network/network.png" alt="Network diagram">
</object>

*Click a device in the diagram to open its page.*

## Where to look

| I want to...                                  | Go to |
|-----------------------------------------------|-------|
| See IPs, VLANs, devices, port map             | [Inventory](generated/inventory.md) |
| Understand VLANs and firewall rules           | [Network overview](network/overview.md) |
| Rebuild the router on new hardware            | [Replace the router](servers/runbooks/replace-router.md) |
| Know what is backed up, where                 | [Backups](servers/backups.md) |
| Find how an ESPHome device is wired           | [ESPHome devices](generated/esphome-devices.md) |

## Conventions

- `inventory.yaml` is the source of truth; diagrams and tables are generated from it.
- No secrets in this repo. Secrets are referenced by name (e.g. `!secret wifi_password`)
  and stored in a password manager.
