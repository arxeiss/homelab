# Next steps

Checklist from documenting the setup on 2026-11-04. Tick items off here (and update the
related docs page) as you go.

> [!TIP]
> **Changing the MikroTik safely:** before any change in the terminal, press **Ctrl+X** to enter
> *Safe Mode*. If you lock yourself out, the router reverts the changes when the session drops.
> Press Ctrl+X again to keep them.

## Network

### Reserve IP addresses for infrastructure

These devices get a **dynamic** DHCP lease today and can change IP:

| Device | Current IP |
|--------|------------|
| UniFi switch | 192.168.88.248 |
| AP "1 NP" | 192.168.88.243 |
| AP "2 NP" | 192.168.88.244 |
| gitlab-runner (LXC 101) | 192.168.88.103 |
| Jablotron alarm | 192.168.88.239 |

- [ ] Make their current leases static on the router (keeps the same IPs):
      ```
      /ip dhcp-server lease make-static [find address=192.168.88.248]
      /ip dhcp-server lease make-static [find address=192.168.88.243]
      /ip dhcp-server lease make-static [find address=192.168.88.244]
      /ip dhcp-server lease make-static [find address=192.168.88.103]
      /ip dhcp-server lease make-static [find address=192.168.88.239]
      ```
      Give each one a comment, e.g. `/ip dhcp-server lease set [find address=192.168.88.248] comment="UniFi switch"`.
- [ ] Do the same for Home Assistant once it runs (see [below](#home-assistant)).
- [ ] Check with `make mikrotik-status` (all infrastructure leases show `static`), update
      `ip_mode: dhcp` -> `static` in `inventory.yaml`, run `make generate`.

### Hardening

- [ ] **Remove the unused OpenVPN server.** It is disabled but configured with weak settings
      (MD5/SHA1, Blowfish):
      ```
      /interface ovpn-server server remove [find name=ovpn-server1]
      ```
- [ ] **Enable ingress filtering on the router bridge ports.** With VLAN filtering on, this drops
      frames with VLAN tags a port is not a member of. Use Safe Mode:
      ```
      /interface bridge port set [find bridge=bridge] ingress-filtering=yes
      ```
      Check afterwards: internet works, IoT devices and both APs are still online.
- [ ] **Limit VLANs on switch access ports.** Every switch port uses the "All" profile, so any wired
      device could tag itself into the IoT VLAN. In UniFi, set the ports below to native VLAN
      `Default` and tagged VLANs `Block All` (Devices -> Sklep switch -> Port Manager):

      | Ports | Device | Profile |
      |-------|--------|---------|
      | 1-4 | cameras | Default only |
      | 22 | NVR | Default only |
      | 23 | alarm | Default only |
      | 5, 9 | APs | keep "All" (IoT SSID is tagged VLAN 20) |
      | 24 | router | keep "All" (trunk) |
      | 21 | Proxmox | keep "All" if HA will get an IoT VLAN interface, else Default only |

- [ ] Then run `make mikrotik-export`, review the diff, update [UniFi](network/unifi/README.md) port profiles, commit.

## Backups

No second machine for offsite copies, so options that need no new hardware:

- [ ] **Check that backups exist** (the read-only token can't see them): Proxmox UI ->
      `local` and `backup-disk2` -> Backups. Note the sizes in [Backups](servers/backups.md).
- [ ] **Offsite copy to cloud storage, encrypted.** Use `rclone` with a `crypt` remote on the
      Proxmox host and sync the backup folders nightly after the 03:00 job. The backups are small
      (a few GB), so a free tier is enough: Google Drive (15 GB) or OneDrive (5 GB), or Backblaze B2
      (~$6/TB/month, pay per use). Store the rclone crypt password in the password manager:
      without it the copy is useless.
- [ ] **Or, as a low-tech alternative:** copy the latest backups to a USB stick / old disk you
      already own once a month and keep it outside the house.
- [ ] **Back up Proxmox host config** (not in any vzdump): nightly
      `tar czf /mnt/pve/backup-disk2/pve-host-$(date +%F).tar.gz /etc/pve /etc/network/interfaces /etc/hosts`
      via cron, included in the offsite sync. Keep the last few.
- [ ] **Keep more backup history.** `keep-last 2` means a mistake noticed after two days is
      already in both backups. In both Proxmox backup jobs (Datacenter -> Backup -> Edit ->
      Retention) set e.g. `keep-daily 7, keep-weekly 4`. The disks have room (backups are a few GB).
      The daily LXC 100 backup already covers the UniFi controller, so its own monthly `.unf`
      autobackup is only a portable extra (restores on any controller, without Proxmox).
- [ ] **Copy a MikroTik binary backup off the router** after each bigger change
      (`/system backup save`, download via Winbox/WebFig, store with the other backups).
- [ ] **Do one restore test**: restore the newest gitlab-runner backup as a new VMID (e.g. 901)
      without network, check it boots, delete it. Write the result into [Backups](servers/backups.md#restore-tests).

## Home Assistant

- [ ] Start VM 102, finish the onboarding.
- [ ] Give it a fixed IP (static DHCP lease), update `inventory.yaml` and [Home Assistant](home-assistant/README.md).
- [ ] Configure HA backups (Settings -> System -> Backups), ideally with the cloud target used above.
- [ ] Check that IoT devices are discovered (router repeats mDNS between VLANs).
- [ ] Pick how HA config gets into this repo (see [Home Assistant](home-assistant/README.md#syncing-config-with-this-repo)).
- [ ] Build the first ESPHome device from `esphome/devices/_template/`.

## Optional ideas

- [ ] Move the cameras and NVR into their own VLAN without internet access (cameras are a
      common weak spot). The NVR keeps working; view it from VLAN 1 via a firewall allow rule.
- [ ] Delete the read-only accounts (`claude-ro` on MikroTik and UniFi, token `claude@pve!docs`)
      when you no longer want automated access. Revoke and recreate: [ACCESS.md](ACCESS.md).
