# Runbook: replace the router

Use when the MikroTik is dead and you have new hardware (possibly a different model or vendor).

1. **Get online temporarily:** connect a laptop directly to the ISP modem if needed.
2. **Same model MikroTik?** Restore the binary `.backup` from backup storage. Done.
3. **Different MikroTik model:** open `network/mikrotik/export.rsc`, re-map interface names
   (`ether1` = WAN, `ether2` = trunk to switch, `wlan1`/`wlan2` WiFi), and paste section by section. Re-enter secrets
   (PPPoE, WiFi, WireGuard keys) from the password manager.
4. **Other vendor:** rebuild from [Network overview](../../network/README.md) and
   [Inventory](../../network/inventory.md): VLANs, subnets, DHCP, DNS, firewall intent, NAT.
5. **Verify:**
    - [ ] Clients on VLAN 1 get DHCP and internet
    - [ ] IoT devices on VLAN 20 reconnect, HA sees ESPHome devices
    - [ ] IoT -> default is blocked
    - [ ] UniFi devices are online in the controller
6. Update `inventory.yaml` (model), run `make generate` and `make mikrotik-export`, commit.
