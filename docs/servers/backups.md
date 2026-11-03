# Backups

Git holds **intent** (docs, text configs, source). Full/binary backups hold **state** and
secrets, so they live on backup storage, never in git.

| What | How | Where | Schedule / retention | Offsite |
|------|-----|-------|----------------------|---------|
| Proxmox guests | vzdump (snapshot, zstd) | SSD 2 | TODO | TODO |
| Home Assistant | HA built-in backups | TODO | TODO | TODO (e.g. Google Drive / Nextcloud add-on) |
| UniFi controller | `.unf` autobackup | TODO | TODO | TODO |
| MikroTik | `.backup` (binary) + `export.rsc` (git) | TODO | on change | git |
| Proxmox host config | `/etc/pve`, `/etc/network/interfaces` | TODO | TODO | TODO |
| Secrets | password manager | - | - | password manager sync |

!!! warning "A second disk in the same machine is not a backup of the machine"
    SSD 2 protects against SSD 1 failing. It does not protect against PSU surge, theft,
    fire or ransomware. Keep at least one copy off the box (3-2-1 rule): e.g. Proxmox Backup
    Server on another device, or encrypted `rclone` sync to cloud storage.

## Restore tests

| Date | What was restored | Result |
|------|-------------------|--------|
| TODO | | |
