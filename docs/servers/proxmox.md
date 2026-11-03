# Proxmox VE

| | |
|---|---|
| Hardware | TODO (CPU, RAM, NIC) |
| Disks | SSD 1: TODO (system + VMs) / SSD 2: TODO (backups) |
| PVE version | TODO |
| Web UI | https://192.168.1.10:8006 |

## Networking

TODO: `vmbr0` VLAN-aware bridge on `nic0`; guests pick VLAN via tag. Sanitized
`/etc/network/interfaces` can live in `servers/proxmox/`.

## Guests

See the [Inventory](../generated/inventory.md#proxmox-guests) for VMIDs and IPs.

| Guest | Notes |
|-------|-------|
| haos | Home Assistant OS VM. Needs USB passthrough? (Zigbee/Z-Wave stick: TODO) |
| unifi-controller | |
| gitlab-runner | Re-register if lost: `gitlab-runner register` with token from GitLab UI. `config.toml` is **not** in git. |

## Backup jobs

See [Backups](backups.md).
