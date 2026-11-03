# MikroTik router

| | |
|---|---|
| Model | TODO |
| RouterOS | TODO (7.x) |
| Management | https://192.168.1.1 (TODO) |
| Credentials | password manager: `TODO entry name` |

## Config backup

Two layers:

1. **Text export (in git):** `make mikrotik-export ROUTER=admin@192.168.1.1` writes
   [`network/mikrotik/export.rsc`](https://github.com/arxeiss/homelab/blob/master/network/mikrotik/export.rsc).
   RouterOS 7 hides sensitive values by default; serial number and software ID lines are stripped.
   **Always review the diff** before committing.
2. **Binary backup (not in git):** `/system backup save` -> copy to backup storage.
   Restores only onto the *same model*.

## Configuration walkthrough

Vendor-neutral list of what is configured, in the order you'd rebuild it. Fill in as you go.

- [ ] Bridge + VLAN filtering (VLAN 1, 20) - TODO which ports are trunk/access
- [ ] IP addresses per VLAN interface
- [ ] DHCP servers per VLAN, static leases (keep MACs out of git: names only)
- [ ] DNS
- [ ] Firewall: see [Network overview](overview.md#firewall-intent)
- [ ] NAT / masquerade
- [ ] Services hardening (disable telnet, ftp, www; restrict winbox/ssh to VLAN 1)
- [ ] NTP client, time zone
- [ ] Admin user, SSH key
