# UniFi (switch + APs)

| | |
|---|---|
| Controller | UniFi Network Application in LXC on Proxmox - see [Inventory](../generated/inventory.md) |
| Version | TODO |
| Switch | TODO model |
| APs | 2x TODO model |

UniFi devices get their configuration **from the controller**. Replacing a dead UniFi device =
adopt the new one, the controller pushes the config. So the thing to protect is the controller.

## Backups

- Controller autobackup (`.unf`), Settings -> System -> Backups: TODO schedule.
  Copied to backup storage + offsite (see [Backups](../servers/backups.md)). **Not in git** (contains secrets).
- Proxmox vzdump of the controller LXC.

## Settings (for rebuilding on non-UniFi hardware)

### Networks

| Name | VLAN | Notes |
|------|------|-------|
| Default | 1 | |
| IoT | 20 | TODO: client isolation? |

### WiFi

| SSID | VLAN | Bands | Security | Notes |
|------|------|-------|----------|-------|
| TODO-home | 1 | 2.4 + 5 GHz | WPA2/WPA3 | password: password manager |
| TODO-iot | 20 | 2.4 GHz | WPA2 | ESPs are 2.4 GHz only |

### Switch port profiles

| Port | Device | Profile (native / tagged) | PoE |
|------|--------|---------------------------|-----|
| 1 | router | TODO | |
| 2 | ap-1 | TODO | yes |
| 3 | ap-2 | TODO | yes |
| 4 | pve | TODO | |
