#!/usr/bin/env python3
"""Read-only status of MikroTik, UniFi and Proxmox, for keeping inventory.yaml up to date.

Reads credentials from the environment (the Makefile loads ~/.config/homelab/credentials.env,
see credentials.env.example). Only GET requests / read-only commands are sent. Output goes to
the terminal only: it is not sanitized for the public repo, don't paste it into git as-is.

Usage:
    homelab_status.py check      test all three connections
    homelab_status.py mikrotik   RouterOS version, DHCP leases (dynamic vs static)
    homelab_status.py unifi      UniFi devices: model, firmware, IP, uplink; switch ports
    homelab_status.py pve        Proxmox version, guests, storage, disks, backup jobs
"""

import json
import os
import re
import ssl
import subprocess
import sys
import urllib.error
import urllib.request

MAC_RE = re.compile(r"([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}")


class AccessError(Exception):
    pass


def env(name: str, default: str | None = None) -> str:
    value = os.environ.get(name, default)
    if value is None or value == "":
        raise AccessError(f"{name} is not set (see credentials.env.example)")
    return value


def truthy(value: str) -> bool:
    return value.strip().lower() in ("1", "true", "yes")


def http_get(url: str, headers: dict, verify_tls: bool) -> dict | list:
    """GET only - this script must never change anything."""
    ctx = ssl.create_default_context()
    if not verify_tls:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(url, headers={"Accept": "application/json", **headers}, method="GET")
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        raise AccessError(f"GET {url} -> HTTP {e.code}") from None
    except (urllib.error.URLError, TimeoutError) as e:
        raise AccessError(f"GET {url} -> {getattr(e, 'reason', e)}") from None


def table(headers: list[str], rows: list[list]) -> None:
    rows = [["" if c is None else str(c) for c in r] for r in rows]
    widths = [max(len(h), *(len(r[i]) for r in rows)) if rows else len(h) for i, h in enumerate(headers)]
    print("  ".join(h.ljust(w) for h, w in zip(headers, widths)))
    print("  ".join("-" * w for w in widths))
    for r in rows:
        print("  ".join(c.ljust(w) for c, w in zip(r, widths)))
    print()


def gib(n: int | None) -> str:
    return f"{n / 2**30:.0f} GB" if n else ""


# ---- MikroTik (SSH, read-only user) -----------------------------------------

def mikrotik(command: str) -> str:
    key = os.path.expanduser(env("MIKROTIK_KEY"))
    target = f"{env('MIKROTIK_USER')}@{env('MIKROTIK_HOST')}"
    result = subprocess.run(
        ["ssh", "-i", key, "-o", "BatchMode=yes", "-o", "ConnectTimeout=5", target, command],
        capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        raise AccessError(f"ssh {target}: {result.stderr.strip() or 'exit ' + str(result.returncode)}")
    return result.stdout.replace("\r", "")


def mikrotik_status() -> None:
    res = mikrotik("/system resource print")
    for key in ("version", "board-name", "free-memory", "free-hdd-space"):
        m = re.search(rf"^\s*{key}: (.*)$", res, re.M)
        if m:
            print(f"{key:15} {m.group(1).strip()}")
    print()
    leases = mikrotik(":foreach l in=[/ip dhcp-server lease find] do={:put ([/ip dhcp-server lease get $l address] "
                      ". \";\" . [/ip dhcp-server lease get $l dynamic] . \";\" . [/ip dhcp-server lease get $l server] "
                      ". \";\" . [/ip dhcp-server lease get $l comment])}")
    rows = []
    for line in leases.splitlines():
        if line.count(";") >= 3:
            addr, dynamic, server, comment = line.split(";", 3)
            rows.append([addr, "dynamic" if dynamic == "true" else "static", server, comment])
    rows.sort(key=lambda r: tuple(int(x) for x in r[0].split(".")) if r[0].count(".") == 3 else (999,))
    print("DHCP leases (dynamic = IP can change; see TODO.md)")
    table(["Address", "Lease", "Server", "Comment"], rows)


# ---- UniFi (API key, GET only) ----------------------------------------------

def unifi_get(path: str):
    return http_get(env("UNIFI_URL").rstrip("/") + path, {"X-API-KEY": env("UNIFI_API_KEY")},
                    truthy(env("UNIFI_VERIFY_TLS", "false")))


def unifi_status() -> None:
    site = env("UNIFI_SITE", "default")
    classic = unifi_get(f"/proxy/network/api/s/{site}/stat/device")["data"]
    portconf = {p["_id"]: p.get("name") for p in unifi_get(f"/proxy/network/api/s/{site}/rest/portconf")["data"]}
    # Integration API has friendly model names; match by name.
    sites = unifi_get("/proxy/network/integration/v1/sites")["data"]
    site_id = next((s["id"] for s in sites if s.get("internalReference") == site), sites[0]["id"])
    friendly = {d["name"]: d for d in
                unifi_get(f"/proxy/network/integration/v1/sites/{site_id}/devices?limit=200")["data"]}

    rows = []
    for d in sorted(classic, key=lambda d: d.get("name", "")):
        f = friendly.get(d.get("name"), {})
        up = d.get("uplink", {})
        uplink = up.get("uplink_remote_port")
        rows.append([d.get("name"), f.get("model") or d.get("model"), d.get("version"), d.get("ip"),
                     f"port {uplink}" if uplink else f"{up.get('type', '')} (to router)", d.get("state") == 1 and "online" or "OFFLINE"])
    table(["Name", "Model", "Firmware", "IP", "Uplink", "State"], rows)

    for d in classic:
        if d.get("type") != "usw":
            continue
        overrides = {o["port_idx"]: o for o in d.get("port_overrides", [])}
        rows = []
        for p in d.get("port_table", []):
            if not p.get("up"):
                continue
            o = overrides.get(p["port_idx"], {})
            profile = portconf.get(o.get("portconf_id")) or ("custom" if o else "All (default)")
            rows.append([p["port_idx"], f"{p.get('speed')}M", "yes" if p.get("poe_enable") else "",
                         profile, MAC_RE.sub("MAC", p.get("name", ""))])
        print(f"Switch {d.get('name')}: ports that are up")
        table(["Port", "Speed", "PoE", "Profile", "Port name"], rows)


# ---- Proxmox (API token, PVEAuditor) ----------------------------------------

def pve_get(path: str):
    auth = f"PVEAPIToken={env('PVE_TOKEN_ID')}={env('PVE_TOKEN_SECRET')}"
    return http_get(env("PVE_URL").rstrip("/") + "/api2/json" + path, {"Authorization": auth},
                    truthy(env("PVE_VERIFY_TLS", "false")))["data"]


def pve_status() -> None:
    print(f"Proxmox VE {pve_get('/version')['version']}\n")
    for i, node in enumerate(pve_get("/nodes")):
        n = node["node"]  # not printed: the node name is kept out of the repo
        rows = []
        for kind in ("lxc", "qemu"):
            for g in pve_get(f"/nodes/{n}/{kind}"):
                cfg = pve_get(f"/nodes/{n}/{kind}/{g['vmid']}/config")
                rows.append([g["vmid"], g.get("name"), "LXC" if kind == "lxc" else "VM", g.get("status"),
                             "yes" if cfg.get("onboot") else "no", g.get("cpus") or g.get("maxcpu"),
                             gib(g.get("maxmem")), gib(g.get("maxdisk"))])
        print(f"Node {i + 1}: guests")
        table(["VMID", "Name", "Type", "Status", "On boot", "vCPU", "RAM", "Disk"], sorted(rows))

        rows = [[s["storage"], s.get("type"), s.get("content"), gib(s.get("used")), gib(s.get("total"))]
                for s in pve_get(f"/nodes/{n}/storage")]
        print("Storage")
        table(["Storage", "Type", "Content", "Used", "Total"], rows)

        rows = [[d.get("devpath"), d.get("model"), gib(d.get("size")), d.get("health"),
                 f"{d['wearout']} %" if isinstance(d.get("wearout"), int) else d.get("wearout")]
                for d in pve_get(f"/nodes/{n}/disks/list")]
        print("Disks (wearout = remaining life as reported by Proxmox)")
        table(["Disk", "Model", "Size", "SMART", "Wearout"], rows)

    rows = [[j.get("id"), "yes" if j.get("enabled", 1) else "no", j.get("schedule"),
             j.get("vmid") or ("all" if j.get("all") else ""), j.get("storage"), j.get("mode"),
             ", ".join(f"{k}={v}" for k, v in (j.get("prune-backups") or {}).items()) or "keep all"]
            for j in pve_get("/cluster/backup")]
    print("Backup jobs")
    table(["Job", "Enabled", "Schedule", "Guests", "Storage", "Mode", "Retention"], rows)


# ---- check ------------------------------------------------------------------

def check() -> int:
    tests = {
        "MikroTik": lambda: re.search(r"version: (.*)", mikrotik("/system resource print")).group(1).strip(),
        "UniFi": lambda: f"{len(unifi_get('/proxy/network/integration/v1/sites')['data'])} site(s)",
        "Proxmox": lambda: "PVE " + pve_get("/version")["version"],
    }
    failed = 0
    for name, test in tests.items():
        try:
            print(f"OK    {name:9} {test()}")
        except Exception as e:  # report every system, not just the first failure
            failed += 1
            print(f"FAIL  {name:9} {e}")
    return 1 if failed else 0


def main() -> int:
    commands = {"check": check, "mikrotik": mikrotik_status, "unifi": unifi_status, "pve": pve_status}
    if len(sys.argv) != 2 or sys.argv[1] not in commands:
        print(__doc__)
        return 2
    try:
        return commands[sys.argv[1]]() or 0
    except AccessError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
