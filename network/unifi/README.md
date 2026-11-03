# UniFi (switch + APs)

| | |
|---|---|
| Controller | UniFi OS Server, UniFi Network 10.6.109, LXC 100 on Proxmox |
| URL | https://192.168.88.11:11443 |
| Site | Default |
| Read-only access | View Only admin `claude-ro` + API key, see [ACCESS.md](../../ACCESS.md#unifi); `make unifi-status` |

UniFi devices get their configuration **from the controller**. Replacing a dead UniFi device =
adopt the new one, the controller pushes the config. So the thing to protect is the controller.

## Devices

Switch "Sklep switch" (USW-24-PoE, basement) and APs "1 NP" / "2 NP" (U6 Pro, PoE from the switch).
Firmware, IPs and uplink ports: [inventory.md](../inventory.md).

## Backups

- Controller autobackup: **monthly** (1st of month, 00:30), stored inside the LXC.
  **Not in git** (`.unf` contains secrets).
- The whole LXC is backed up daily by Proxmox (see [Backups](../../servers/backups.md)).

## Settings (for rebuilding on non-UniFi hardware)

### Networks

| Name | VLAN | Type | Notes |
|------|------|------|-------|
| Default | 1 (untagged) | gateway-managed, router does DHCP | |
| IoT | 20 | VLAN only | router does DHCP |

IGMP snooping off on both. No zone-based firewall configured (the router does all filtering).

### WiFi

SSIDs, VLANs and bands: [inventory.md](../inventory.md#wifi). Real SSIDs: password manager.

Radios (1 NP): 2.4 GHz channel 1 / 20 MHz, 5 GHz channel 44 / 40 MHz, 802.11ax.

### Switch ports

No port overrides: every port uses the default "All" profile (native VLAN 1, all VLANs tagged).
Which device is on which port: [inventory.md](../inventory.md#physical-links). Ports 1-4 (cameras)
and 5, 9 (APs) power their device over PoE.
