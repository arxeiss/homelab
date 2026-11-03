# Backups

Git holds **intent** (docs, text configs, source). Full/binary backups hold **state** and
secrets, so they live on backup storage, never in git.

| What | How | Where | Schedule / retention | Offsite |
|------|-----|-------|----------------------|---------|
| LXC 100 unifi-os-server, LXC 101 gitlab-runner | vzdump, snapshot, zstd | `local` (SSD 1) | daily 03:00, keep last 2 | **none** |
| VM 102 homeassistant | vzdump, snapshot, zstd | `backup-disk2` (SSD 2) | daily 03:00, keep last 2 | **none** |
| Home Assistant (app level) | HA built-in backups | TODO (HA not deployed yet) | TODO | TODO |
| UniFi controller | `.unf` autobackup | inside LXC 100 | monthly (1st, 00:30) | via LXC backup only |
| MikroTik | `export.rsc` (git) + `.backup` (binary) | git / TODO | on change | git |
| Proxmox host config | `/etc/pve`, `/etc/network/interfaces` | TODO | TODO | TODO |
| Secrets | password manager | - | - | password manager sync |

Each guest is backed up to the **other** SSD (LXCs live on SSD 2 and back up to SSD 1, HA lives
on SSD 1 and backs up to SSD 2), so one dead SSD loses nothing. Good.

> [!WARNING]
> **Both SSDs are in the same machine.** This protects against one SSD failing. It does not
> protect against PSU surge, theft, fire or ransomware. Keep at least one copy off the box
> (3-2-1 rule): e.g. Proxmox Backup Server on another device, or encrypted `rclone` sync to
> cloud storage.

## Open points

See the [Next steps checklist](../TODO.md#backups).

## Restore tests

| Date | What was restored | Result |
|------|-------------------|--------|
| TODO | | |
