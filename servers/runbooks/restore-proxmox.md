# Runbook: restore the Proxmox host

1. Install Proxmox VE on new hardware/disk. Node name from the password manager, management IP `192.168.88.10/24` on `vmbr0` (bridge on the onboard NIC), gateway `192.168.88.1`.
2. Recreate networking (`vmbr0`, not VLAN-aware today) - see [Proxmox](../proxmox/README.md#networking).
3. Recreate storage (see [Proxmox](../proxmox/README.md#disks-and-storage)). Backups of the LXCs are on SSD 1 (`local`), of HA on SSD 2 (`backup-disk2`).
4. Restore guests from vzdump: Datacenter -> Storage -> Backups -> Restore. Order:
    1. 100 unifi-os-server (network management)
    2. 102 homeassistant
    3. 101 gitlab-runner (or just reinstall + re-register)
5. Recreate backup jobs (see [Backups](../backups.md)).
6. **Verify:**
    - [ ] All guests start on boot
    - [ ] HA reachable, integrations OK
    - [ ] UniFi controller sees all devices
    - [ ] Backup job runs successfully
