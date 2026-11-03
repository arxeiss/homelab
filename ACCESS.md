# Read-only access

Scripted (and AI-assisted) documentation work uses dedicated **read-only** accounts, never your
admin logins. Their credentials live in `~/.config/homelab/credentials.env` (outside the repo,
`chmod 600`); the template is [`credentials.env.example`](credentials.env.example).

| System | Account | Rights | Used by |
|---|---|---|---|
| MikroTik | user `claude-ro`, SSH key | group `readonly`: no write, reboot, policy or **sensitive** | `make mikrotik-export`, `make mikrotik-status` |
| UniFi OS Server | admin `claude-ro` (View Only) + API key | see the warning below | `make unifi-status` |
| Proxmox VE | token `claude@pve!docs` | role `PVEAuditor` (only `*.Audit`) | `make pve-status` |

```bash
make check-access   # test all three
make status         # print live state, compare with inventory.yaml
```

`make status` prints to the terminal only. The raw output contains client hostnames and DHCP
details, so copy what you need into `inventory.yaml` by hand. All scripts only send GET requests
or read-only commands.

## MikroTik

A group without `sensitive` means `/export` can't reveal secrets, even by mistake.

```
/user group add name=readonly policy=ssh,read,test,!local,!telnet,!ftp,!reboot,!write,!policy,!password,!web,!sniff,!sensitive,!api,!romon,!winbox,!rest-api
/user add name=claude-ro group=readonly address=192.168.88.0/24 password=<long random, never used>
```

Create a dedicated key on your PC, upload the `.pub` file to the router (Winbox/WebFig -> Files),
then import it:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/homelab-ro -C homelab-ro
```
```
/user ssh-keys import public-key-file=homelab-ro.pub user=claude-ro
```

Tighter: `address=<your-PC-IP>/32` instead of the whole subnet (today the whole VLAN 1 is allowed).

**Revoke:** `/user remove [find name=claude-ro]` (and `/user group remove [find name=readonly]`).

## UniFi

An API key gets the permissions of the admin who created it; there is no read-only flag on the key.

1. Settings -> Admins & Users -> add a local admin `claude-ro` with the **View Only** role
   (for both UniFi OS Server and Network).
2. Log in **as `claude-ro`** (private browser window), Settings -> Integrations -> create an API key.
3. Put it in `credentials.env` as `UNIFI_API_KEY`. It is shown only once.

> [!WARNING]
> Read-only was **not confirmed** for the current key: a test write to a non-existent device
> returned 404 (not 403), which proves nothing either way. Treat the key as possibly
> write-capable. The scripts here only send GET requests.

APIs used: the Integration API (`/proxy/network/integration/v1/...`, friendly model names) and the
classic API (`/proxy/network/api/s/<site>/...`, uplinks, port profiles). Both accept the
`X-API-KEY` header.

**Revoke:** delete the key in Settings -> Integrations and the `claude-ro` admin in Admins & Users.

## Proxmox

On the Proxmox host shell:

```bash
pveum user add claude@pve --comment "read-only docs access"
pveum acl modify / --users claude@pve --roles PVEAuditor
pveum user token add claude@pve docs --privsep 0   # prints the secret once -> PVE_TOKEN_SECRET
```

`PVEAuditor` can read guest configs, storage, disks and backup jobs. It can't list backup files
inside storage, and can't start, stop or change anything.

**Revoke:** `pveum user token remove claude@pve docs` and `pveum user delete claude@pve`.

## Not given

- **Home Assistant:** HA has no read-only tokens, any token can control devices. Share config
  files (Samba/SSH add-on) instead.
- Password manager, ISP modem, GitLab runner, any admin account.
