# MikroTik router

| | |
|---|---|
| Model | hAP ac (RB962UiGS-5HacT2HnT), MIPS 720 MHz, 128 MB RAM, **16 MB flash** |
| RouterOS | 7.21.4 (long-term), RouterBOOT auto-upgrade on |
| Management | https://192.168.88.1 / Winbox / SSH, from VLAN 1 only |
| Credentials | password manager |
| Read-only account | `claude-ro` (group `readonly`, SSH key), see [ACCESS.md](../../ACCESS.md#mikrotik) |

## Ports

| Port | Use |
|------|-----|
| ether1 | WAN (DHCP client) |
| ether2 | Trunk to switch port 24: VLAN 1 untagged, VLAN 20 tagged |
| ether3-5, sfp1 | Bridge members, unused (ether5 has PoE out) |
| wlan1 | 2.4 GHz, IoT SSID, untagged VLAN 20 (`pvid=20`), channel 11 |
| wlan2 | 5 GHz, main SSID, VLAN 1, **disabled** |

## Config backup

1. **Text export (in git):** `make mikrotik-export` writes [`export.rsc`](export.rsc).
   Uses `~/.config/homelab/credentials.env` ([ACCESS.md](../../ACCESS.md)). Secrets are hidden by RouterOS (and the read-only user
   can't see them anyway); serial number, software ID, MAC addresses and SSIDs are stripped.
   **Always review the diff** before committing.
2. **Binary backup (not in git):** `/system backup save` and copy it off the router.
   The flash is only 16 MB, so don't keep backups on the router. Restores only onto the *same model*.

## Configuration walkthrough

What is configured, in the order you'd rebuild it on new hardware. Details: [Network overview](../README.md).

- [x] Bridge with VLAN filtering; `ether2` trunk (VLAN 20 tagged), `wlan1` access VLAN 20
- [x] VLAN interface `vlan20_iot` on the bridge
- [x] IP addresses: `192.168.88.1/24` on bridge, `192.168.20.1/24` on `vlan20_iot`
- [x] DHCP servers: `defconf` (pool .100-.254, 10 min lease), `dhcp_iot` (pool .100-.254)
- [x] DNS: allow remote requests, upstream 1.1.1.1 + 8.8.8.8, mDNS repeat between bridge and IoT
- [x] Interface lists: WAN (`ether1`), LAN (`bridge`, `vlan20_iot`), MGMT (`bridge`)
- [x] Firewall: see [Firewall intent](../README.md#firewall-intent)
- [x] NAT masquerade on WAN
- [x] Services: FTP, Telnet, API off; SSH/Winbox/WWW limited to 192.168.88.0/24; strong SSH crypto
- [x] Neighbor discovery and MAC server only on MGMT list
- [x] IPv6 disabled
- [x] NTP client (time1.google.com), time zone Europe/Prague
- [x] Netwatch: logs "Internet up/down" by pinging 8.8.8.8
- [x] WiFi `wlan1` (IoT, active) / `wlan2` (disabled), WPA2-PSK, WPS off
- [ ] Static DHCP leases for infrastructure (none today, see [Next steps](../../TODO.md#reserve-ip-addresses-for-infrastructure))
