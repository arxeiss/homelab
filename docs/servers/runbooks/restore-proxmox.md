# Runbook: restore the Proxmox host

1. Install Proxmox VE on new hardware/disk. Set management IP to `192.168.1.10` (see Inventory).
2. Recreate networking (`vmbr0`, VLAN aware) - see [Proxmox](../proxmox.md#networking).
3. Add backup storage (SSD 2, or offsite copy if SSD 2 is gone).
4. Restore guests from vzdump: Datacenter -> Storage -> Backups -> Restore. Order:
    1. unifi-controller (network management)
    2. haos
    3. gitlab-runner (or just reinstall + re-register)
5. Recreate backup jobs (see [Backups](../backups.md)).
6. **Verify:**
    - [ ] All guests start on boot
    - [ ] HA reachable, integrations OK
    - [ ] UniFi controller sees all devices
    - [ ] Backup job runs successfully
