# Proxmox

Sanitized config snippets for rebuilding the host, e.g.:

- `interfaces` - copy of `/etc/network/interfaces`
- `storage.cfg` - copy of `/etc/pve/storage.cfg` (remove any credentials!)
- `vzdump-jobs.txt` - output of `cat /etc/pve/jobs.cfg`

Docs: [docs/servers/proxmox.md](../../docs/servers/proxmox.md)
