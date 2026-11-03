# by RouterOS 7.21.4
#
# model = RB962UiGS-5HacT2HnT
/interface bridge add admin-mac=XX:XX:XX:XX:XX:XX auto-mac=no comment=defconf dhcp-snooping=yes ingress-filtering=no name=bridge port-cost-mode=short vlan-filtering=yes
/interface wireless set [ find default-name=wlan1 ] band=2ghz-b/g/n comment=IoT country="czech republic" disabled=no distance=indoors frequency=2462 installation=indoor mode=ap-bridge ssid="<redacted>" station-roaming=enabled wireless-protocol=802.11 wps-mode=disabled
/interface wireless set [ find default-name=wlan2 ] band=5ghz-a/n/ac channel-width=20/40/80mhz-XXXX country="czech republic" distance=indoors frequency=auto installation=indoor mode=ap-bridge ssid="<redacted>" station-roaming=enabled wireless-protocol=802.11 wps-mode=disabled
/interface wireless manual-tx-power-table set wlan1 comment=IoT
/interface wireless nstreme set wlan1 comment=IoT
/interface vlan add interface=bridge name=vlan20_iot vlan-id=20
/interface list add comment=defconf name=WAN
/interface list add comment=defconf name=LAN
/interface list add comment="IoT blocking MGMT" name=MGMT
/interface lte apn set [ find default=yes ] ip-type=ipv4 use-network-apn=no
/interface wireless security-profiles set [ find default=yes ] authentication-types=wpa2-psk mode=dynamic-keys supplicant-identity=MikroTik
/ip pool add name=dhcp ranges=192.168.88.100-192.168.88.254
/ip pool add name=iot_pool ranges=192.168.20.100-192.168.20.254
/ip dhcp-server add address-pool=dhcp interface=bridge lease-time=10m name=defconf
/ip dhcp-server add address-pool=iot_pool interface=vlan20_iot name=dhcp_iot
/ip smb users set [ find default=yes ] disabled=yes
/system logging action set 0 memory-lines=10000
/user group add name=readonly policy=ssh,read,test,!local,!telnet,!ftp,!reboot,!write,!policy,!winbox,!password,!web,!sniff,!sensitive,!api,!romon,!rest-api
/interface bridge port add bridge=bridge comment=defconf ingress-filtering=no interface=ether2 internal-path-cost=10 path-cost=10
/interface bridge port add bridge=bridge comment=defconf ingress-filtering=no interface=ether3 internal-path-cost=10 path-cost=10
/interface bridge port add bridge=bridge comment=defconf ingress-filtering=no interface=ether4 internal-path-cost=10 path-cost=10
/interface bridge port add bridge=bridge comment=defconf ingress-filtering=no interface=ether5 internal-path-cost=10 path-cost=10
/interface bridge port add bridge=bridge comment=defconf ingress-filtering=no interface=sfp1 internal-path-cost=10 path-cost=10
/interface bridge port add bridge=bridge comment=defconf ingress-filtering=no interface=wlan1 internal-path-cost=10 path-cost=10 pvid=20
/interface bridge port add bridge=bridge comment=defconf ingress-filtering=no interface=wlan2 internal-path-cost=10 path-cost=10
/ip firewall connection tracking set udp-timeout=10s
/ip neighbor discovery-settings set discover-interface-list=MGMT
/ip settings set max-neighbor-entries=8192
/ipv6 settings set disable-ipv6=yes max-neighbor-entries=8192
/interface bridge vlan add bridge=bridge tagged=bridge,ether2 vlan-ids=20
/interface list member add comment=defconf interface=bridge list=LAN
/interface list member add comment=defconf interface=ether1 list=WAN
/interface list member add comment="IoT internet access" interface=vlan20_iot list=LAN
/interface list member add comment="IoT blocking MGMT" interface=bridge list=MGMT
/interface ovpn-server server add auth=sha1,md5 mac-address=XX:XX:XX:XX:XX:XX name=ovpn-server1
/ip address add address=192.168.88.1/24 comment=defconf interface=bridge network=192.168.88.0
/ip address add address=192.168.20.1/24 interface=vlan20_iot network=192.168.20.0
/ip dhcp-client add comment=defconf default-route-tables=main interface=ether1 use-peer-dns=no
/ip dhcp-server network add address=192.168.20.0/24 comment=IoT dns-server=192.168.20.1 gateway=192.168.20.1
/ip dhcp-server network add address=192.168.88.0/24 comment=defconf gateway=192.168.88.1
/ip dns set allow-remote-requests=yes mdns-repeat-ifaces=bridge,vlan20_iot servers=1.1.1.1,8.8.8.8
/ip dns static add address=192.168.88.1 comment=defconf name=router.lan type=A
/ip firewall filter add action=accept chain=input comment="defconf: accept established,related,untracked" connection-state=established,related,untracked
/ip firewall filter add action=drop chain=input comment="defconf: drop invalid" connection-state=invalid
/ip firewall filter add action=accept chain=input comment="defconf: accept ICMP" protocol=icmp
/ip firewall filter add action=accept chain=input comment="defconf: accept to local loopback (for CAPsMAN)" dst-address=127.0.0.1
/ip firewall filter add action=drop chain=input comment="Restricting Router Admin from IoT (restricted by IP->Services->www too)" dst-port=80,443,8291,22 protocol=tcp src-address=192.168.20.0/24
/ip firewall filter add action=accept chain=input comment="Allow mDNS repeater" dst-address=224.0.0.251 dst-port=5353 in-interface-list=LAN protocol=udp
/ip firewall filter add action=drop chain=input comment="defconf: drop all not coming from LAN" in-interface-list=!LAN
/ip firewall filter add action=accept chain=forward comment="defconf: accept in ipsec policy" ipsec-policy=in,ipsec
/ip firewall filter add action=accept chain=forward comment="defconf: accept out ipsec policy" ipsec-policy=out,ipsec
/ip firewall filter add action=fasttrack-connection chain=forward comment="defconf: fasttrack" connection-state=established,related
/ip firewall filter add action=accept chain=forward comment="defconf: accept established,related, untracked" connection-state=established,related,untracked
/ip firewall filter add action=drop chain=forward comment="defconf: drop invalid" connection-state=invalid
/ip firewall filter add action=drop chain=forward comment="defconf: drop all from WAN not DSTNATed" connection-nat-state=!dstnat connection-state=new in-interface-list=WAN
/ip firewall filter add action=drop chain=forward comment="Block IoT from Accessing Main LAN" dst-address=192.168.88.0/24 in-interface=vlan20_iot
/ip firewall filter add action=accept chain=forward comment="Allow IoT Internet Access" out-interface-list=WAN src-address=192.168.20.0/24
/ip firewall nat add action=masquerade chain=srcnat comment="defconf: masquerade" ipsec-policy=out,none out-interface-list=WAN
/ip ipsec profile set [ find default=yes ] dpd-interval=2m dpd-maximum-failures=5
/ip service set ftp disabled=yes
/ip service set ssh address=192.168.88.0/24
/ip service set telnet disabled=yes
/ip service set www address=192.168.88.0/24
/ip service set www-ssl address=192.168.88.0/24
/ip service set winbox address=192.168.88.0/24
/ip service set api disabled=yes
/ip service set api-ssl disabled=yes
/ip ssh set strong-crypto=yes
/routing bfd configuration add disabled=no interfaces=all min-rx=200ms min-tx=200ms multiplier=5
/system clock set time-zone-name=Europe/Prague
/system ntp client set enabled=yes
/system ntp client servers add address=time1.google.com
/system routerboard settings set auto-upgrade=yes silent-boot=yes
/tool bandwidth-server set enabled=no
/tool graphing interface add interface=wlan1
/tool graphing queue add
/tool graphing resource add
/tool mac-server set allowed-interface-list=MGMT
/tool mac-server mac-winbox set allowed-interface-list=MGMT
/tool netwatch add disabled=no down-script="log info \"Internet down\"" host=8.8.8.8 interval=1m timeout=1s type=simple up-script="log info \"Internet up\""
