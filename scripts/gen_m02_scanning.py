#!/usr/bin/env python3
"""Generate Module 02 scanning and enumeration cheat YAML files."""

from __future__ import annotations

from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "loadout" / "cheats" / "02-scanning_and_enumeration"

# tool filename -> full YAML content
CHEATS: dict[str, str] = {}


def add(name: str, content: str) -> None:
    CHEATS[name] = content.strip() + "\n"


# ── Network Scanners ──────────────────────────────────────────────────────

add("traceroute", """
tool: traceroute
tags: [scanning, network, m02]
exam_hint: "traceroute shows every router (hop) between you and a target — reveals the network path and helps map infrastructure."
docs:
  - "man:traceroute"

actions:
  - title: Trace the path to a host
    desc: Shows each router hop from your machine to the target IP or domain. Useful for mapping network topology. Lab targets only.
    command: "traceroute {{domain}}"

  - title: Trace using ICMP instead of UDP
    desc: Uses ICMP echo packets for each hop — sometimes works when normal traceroute is blocked by firewalls.
    command: "traceroute -I {{domain}}"

  - title: Limit the maximum number of hops
    desc: Stops after 15 hops instead of the default 30 — faster when the target is close or unreachable.
    command: "traceroute -m 15 {{domain}}"

  - title: Trace to an IP address
    desc: Traces the network path to a specific IP instead of a domain name.
    command: "traceroute {{ip}}"
""")

add("traceroute-ng", """
tool: traceroute-ng
tags: [scanning, network, m02]
exam_hint: "traceroute-ng is an enhanced traceroute with better output formatting and export options for reports."
docs:
  - "man:traceroute"

actions:
  - title: Trace path with enhanced output
    desc: Runs traceroute-ng to show the network path to a target with cleaner, more detailed output. Lab targets only.
    command: "traceroute-ng {{domain}}"

  - title: Trace using ICMP packets
    desc: Uses ICMP for hop detection — alternative when UDP probes are filtered.
    command: "traceroute-ng --icmp {{domain}}"

  - title: Save trace results to a file
    desc: Runs the trace and saves the full hop-by-hop report to a text file for your assessment notes.
    command: "traceroute-ng --output {{output|trng-report.txt}} {{domain}}"
""")

add("unicornscan", """
tool: unicornscan
tags: [scanning, network, m02]
exam_hint: "unicornscan is a fast asynchronous port scanner — sends many probes in parallel for quick TCP/UDP sweeps."
docs:
  - https://www.kali.org/tools/unicornscan/

actions:
  - title: Scan TCP ports 1 through 1024
    desc: Performs a fast asynchronous TCP scan on the first 1024 ports. Much faster than nmap for quick sweeps. Lab targets only.
    command: "unicornscan -mT {{ip}}:1-1024"

  - title: Scan a custom port range
    desc: Scans a specific TCP port range you define — useful when you know which ports matter.
    command: "unicornscan -mT {{ip}}:{{port|1-65535}}"

  - title: UDP scan on common ports
    desc: Sends UDP probes to discover open UDP services like DNS (53) and SNMP (161).
    command: "unicornscan -mU {{ip}}:53,161,500"
""")

add("sx", """
tool: sx
tags: [scanning, network, m02]
exam_hint: "sx is a modern fast network scanner — ARP discovery and TCP port scanning with high performance."
docs:
  - https://github.com/v-byte-cpu/sx

actions:
  - title: Discover live hosts with ARP scan
    desc: Sends ARP requests to every IP on a subnet to find which machines are alive on the local network. Lab targets only.
    command: "sx arp {{ip}}/24"

  - title: Scan common web ports on a subnet
    desc: Checks ports 80 and 443 on every host in the subnet to find web servers quickly.
    command: "sx tcp -p 80,443 {{ip}}/24"

  - title: Scan specific ports on one host
    desc: TCP scan on custom ports against a single target IP.
    command: "sx tcp -p {{port|22,80,443,445,3389}} {{ip}}"
""")

add("pscan", """
tool: pscan
tags: [scanning, network, m02]
exam_hint: "pscan.c is a simple lightweight TCP port scanner — good for understanding how port scanning works at a low level."
docs: []

actions:
  - title: Compile the scanner
    desc: Builds the pscan.c source code into an executable binary you can run.
    command: "gcc pscan.c -o pscan"

  - title: Scan a port range on a target
    desc: Checks every TCP port in a range against one IP address. Simple and fast for small ranges. Lab targets only.
    command: "./pscan {{ip}} {{port|1}} {{port|1024}}"
""")

add("nemesis", """
tool: nemesis
tags: [scanning, network, m02]
exam_hint: "nemesis crafts custom network packets — inject TCP, UDP, ICMP, and ARP packets for low-level network testing."
docs:
  - https://github.com/troglobit/nemesis

actions:
  - title: Send a custom TCP packet
    desc: Crafts and sends a custom TCP packet with specific flags to a target port — used for firewall and IDS testing. Lab only.
    command: "nemesis tcp -S {{ip}} -D {{ip}} -fS -y {{port|80}}"

  - title: Send an ICMP echo request
    desc: Sends a custom ICMP ping packet to test host reachability with crafted packet options.
    command: "nemesis icmp -D {{ip}} -e echo-reply"

  - title: Send a custom ARP packet
    desc: Crafts ARP packets for network-layer testing on the local subnet.
    command: "nemesis arp -D {{ip}} -h {{ip}}"
""")

add("hunt", """
tool: hunt
tags: [scanning, network, m02]
exam_hint: "hunt passively monitors TCP connections on a network and can hijack or reset sessions — classic tool for understanding TCP attacks."
docs: []

actions:
  - title: Start hunt to monitor connections
    desc: Launches hunt in interactive mode to passively watch TCP sessions on the network. Requires root and promiscuous mode. Lab only.
    command: "sudo hunt"

  - title: Reminder — hunt interactive commands
    desc: Prints a reminder of hunt's interactive commands for listing, hijacking, and resetting TCP connections.
    command: "echo 'hunt: run as root, use l to list connections, a to analyze, h to hijack — authorized lab only'"
""")

add("advanced-ip-scanner", """
tool: advanced-ip-scanner
tags: [scanning, network, m02]
exam_hint: "Advanced IP Scanner discovers live hosts and open ports on a local network — popular GUI tool for Windows network mapping."
docs:
  - https://www.advanced-ip-scanner.com

actions:
  - title: Scan a subnet for live hosts
    desc: Scans every IP in a subnet range to find which devices are online and responding. Lab networks only.
    command: "advanced-ip-scanner {{ip}}/24"

  - title: Scan a specific IP range
    desc: Scans only the IPs between two addresses — useful for targeting a known DHCP range.
    command: "advanced-ip-scanner {{ip|192.168.1.100}}-{{ip|192.168.1.200}}"

  - title: Scan common ports on a subnet
    desc: Checks ports 22, 80, 443, and 3389 on every host in the subnet.
    command: "advanced-ip-scanner {{ip}}/24 -p 22,80,443,3389"

  - title: Save scan results to a file
    desc: Runs the scan and exports results to a text file for your report.
    command: "advanced-ip-scanner {{ip}}/24 -o {{output|results.txt}}"
""")

add("colasoft-packet-builder", """
tool: colasoft-packet-builder
tags: [scanning, network, m02]
exam_hint: "Colasoft Packet Builder is a Windows GUI tool for crafting custom network packets — useful for firewall and IDS testing."
docs:
  - https://www.colasoft.com

actions:
  - title: Open Colasoft Packet Builder
    desc: Opens the Colasoft website to download Packet Builder — a GUI for designing and sending custom TCP/UDP/ICMP packets. Lab only.
    command: "xdg-open https://www.colasoft.com/packet_builder/"

  - title: Craft packets with nemesis instead
    desc: CLI alternative — sends custom TCP packets from the command line when Colasoft GUI is not available.
    command: "nemesis tcp -S {{ip}} -D {{ip}} -fS -y {{port|80}}"
""")

add("colasoft-ping-tool", """
tool: colasoft-ping-tool
tags: [scanning, network, m02]
exam_hint: "Colasoft Ping Tool sends multiple ping types (ICMP, TCP, UDP) to check if hosts are alive — Windows GUI utility."
docs:
  - https://www.colasoft.com

actions:
  - title: Ping a host with ICMP
    desc: CLI equivalent — sends ICMP echo requests to check if the target is alive.
    command: "ping -c 4 {{ip}}"

  - title: Ping a specific TCP port
    desc: Checks if a host is alive by attempting a TCP connection to a port — works when ICMP is blocked.
    command: "nmap -sn -PS{{port|80}} {{ip}}"

  - title: Open Colasoft Ping Tool download page
    desc: Opens the Colasoft website for the GUI ping utility.
    command: "xdg-open https://www.colasoft.com/ping_tool/"
""")

add("mega-ping", """
tool: mega-ping
tags: [scanning, network, m02]
exam_hint: "MegaPing is a Windows GUI suite combining ping, traceroute, port scan, and hostname lookup in one tool."
docs:
  - https://www.megaping.com/

actions:
  - title: Open MegaPing website
    desc: Opens the MegaPing product page — Windows GUI for ping, port scan, and network discovery.
    command: "xdg-open https://www.megaping.com/"

  - title: CLI ping sweep equivalent
    desc: Discovers live hosts on a subnet using nmap ping sweep — CLI alternative to MegaPing.
    command: "nmap -sn {{ip}}/24"
""")

add("netscantools-pro", """
tool: netscantools-pro
tags: [scanning, network, m02]
exam_hint: "NetScanTools Pro is a Windows GUI suite with ping, DNS lookup, port scan, traceroute, and WHOIS tools."
docs:
  - https://www.netscantools.com/netscantools_pro.html

actions:
  - title: Open NetScanTools Pro website
    desc: Opens the product page for the Windows network toolkit.
    command: "xdg-open https://www.netscantools.com/netscantools_pro.html"

  - title: Full port scan equivalent
    desc: CLI nmap service scan — alternative when NetScanTools GUI is not available.
    command: "nmap -sV {{ip}}"
""")

add("oputils", """
tool: oputils
tags: [scanning, network, m02]
exam_hint: "ManageEngine OpUtils is an enterprise web-based toolkit for IP address management, port scanning, and network monitoring."
docs:
  - https://www.manageengine.com/products/oputils/

actions:
  - title: Open OpUtils product page
    desc: Opens the ManageEngine OpUtils website — enterprise IPAM and network scanner.
    command: "xdg-open https://www.manageengine.com/products/oputils/"

  - title: Subnet scan with nmap
    desc: CLI equivalent — ping sweep to discover live hosts on a subnet.
    command: "nmap -sn {{ip}}/24"
""")

add("pingplotter", """
tool: pingplotter
tags: [scanning, network, m02]
exam_hint: "PingPlotter continuously pings a target and graphs latency over time — great for finding intermittent network problems."
docs:
  - https://www.pingplotter.com

actions:
  - title: Open PingPlotter website
    desc: Opens PingPlotter download page — GUI tool for continuous ping and route monitoring.
    command: "xdg-open https://www.pingplotter.com"

  - title: Continuous ping from CLI
    desc: Sends continuous pings to monitor latency — CLI alternative to PingPlotter graphs.
    command: "ping {{domain}}"

  - title: Trace route with timing
    desc: Shows the network path with per-hop latency — similar to PingPlotter's route view.
    command: "traceroute {{domain}}"
""")

add("prtg", """
tool: prtg
tags: [scanning, network, m02]
exam_hint: "PRTG Network Monitor is enterprise software that continuously monitors servers, ports, bandwidth, and network health."
docs:
  - https://www.paessler.com/prtg

actions:
  - title: Open PRTG product page
    desc: Opens Paessler PRTG website — enterprise network monitoring with auto-discovery.
    command: "xdg-open https://www.paessler.com/prtg"

  - title: Discover live hosts on subnet
    desc: CLI nmap ping sweep — finds all live devices on a network segment.
    command: "nmap -sn {{ip}}/24"
""")

add("solarwinds-ets", """
tool: solarwinds-ets
tags: [scanning, network, m02]
exam_hint: "SolarWinds Engineer's Toolset is a Windows GUI bundle with over 60 network diagnostics tools — ping, scan, DNS, SNMP."
docs:
  - https://www.solarwinds.com/engineers-toolset

actions:
  - title: Open SolarWinds Toolset page
    desc: Opens the SolarWinds Engineer's Toolset product page.
    command: "xdg-open https://www.solarwinds.com/engineers-toolset"

  - title: Port scan equivalent with nmap
    desc: CLI nmap scan with service detection — covers many Toolset scanner features.
    command: "nmap -sV -sC {{ip}}"
""")

# ── Web Scanners ──────────────────────────────────────────────────────────

add("whatweb", """
tool: whatweb
tags: [scanning, web, m02]
exam_hint: "whatweb identifies what technologies a website uses — CMS, web server, JavaScript frameworks, analytics, and plugins."
docs:
  - https://github.com/urbanadventurer/WhatWeb

actions:
  - title: Identify technologies on a website
    desc: Scans a URL and reports the web server, CMS, frameworks, and plugins in use. Quick fingerprinting step. Lab targets only.
    command: "whatweb {{url|https://example.com}}"

  - title: Aggressive scan with plugin detection
    desc: Uses aggression level 3 for deeper plugin and version detection — sends more requests but finds more details.
    command: "whatweb -a 3 {{url|https://example.com}}"

  - title: Scan multiple URLs from a file
    desc: Reads a list of URLs and fingerprints each one — useful after subdomain discovery.
    command: "whatweb -i {{file|urls.txt}}"

  - title: Save results as JSON
    desc: Exports technology fingerprint results to a JSON file for reporting or further processing.
    command: "whatweb --log-json={{output|whatweb.json}} {{url|https://example.com}}"
""")

add("httprint", """
tool: httprint
tags: [scanning, web, m02]
exam_hint: "httprint fingerprints web servers by analyzing HTTP response headers — identifies Apache, IIS, nginx even when banners are hidden."
docs:
  - https://www.net-square.com/httprint.html

actions:
  - title: Fingerprint a web server
    desc: Sends HTTP requests and matches response signatures against a database to identify the web server type and version. Lab targets only.
    command: "httprint -h {{ip}} -s {{file|signatures.txt}} -P {{port|80}}"

  - title: Fingerprint over HTTPS
    desc: Same fingerprinting but targeting the HTTPS port with SSL enabled.
    command: "httprint -h {{ip}} -s {{file|signatures.txt}} -P {{port|443}} -S"

  - title: Use nmap http-server-header as alternative
    desc: CLI alternative — nmap probes HTTP and reads the Server header for web server identification.
    command: "nmap -p {{port|80,443}} --script http-server-header {{ip}}"
""")

add("httprecon", """
tool: httprecon
tags: [scanning, web, m02]
exam_hint: "httprecon performs passive and active web server fingerprinting to identify server software, OS, and technologies."
docs:
  - https://sourceforge.net/projects/httprecon/

actions:
  - title: Fingerprint web server by hostname
    desc: Analyzes HTTP responses to identify the web server software and operating system. Lab targets only.
    command: "httprecon -h {{domain}}"

  - title: Fingerprint by domain name
    desc: Runs httprecon against a domain to detect server type and version.
    command: "httprecon {{domain}}"

  - title: Use whatweb as modern alternative
    desc: whatweb provides similar web technology fingerprinting with better maintained signatures.
    command: "whatweb {{url|https://example.com}}"
""")

add("uniscan", """
tool: uniscan
tags: [scanning, web, m02]
exam_hint: "uniscan is an automated web vulnerability scanner — checks directories, files, SQL injection, and XSS on a target site."
docs:
  - https://github.com/yolosecurity/uniscan

actions:
  - title: Quick scan for directories and files
    desc: Runs a fast scan checking for common directories and files on the target web server. Lab targets only.
    command: "uniscan -u {{url|http://example.com}} -q"

  - title: Full scan with all checks
    desc: Runs all uniscan modules — directory brute-force, file checks, SQLi, XSS, and more. Thorough but noisy.
    command: "uniscan -u {{url|http://example.com}} -qv"

  - title: Scan for web directories only
    desc: Brute-forces common directory paths on the web server.
    command: "uniscan -u {{url|http://example.com}} -d"

  - title: Check for SQL injection and XSS
    desc: Tests web forms and parameters for SQL injection and cross-site scripting vulnerabilities.
    command: "uniscan -u {{url|http://example.com}} -s"

  - title: Save HTML report
    desc: Runs the scan and saves findings to an HTML report file.
    command: "uniscan -u {{url|http://example.com}} -o {{output|report.html}}"
""")

# ── Wireless Tools ────────────────────────────────────────────────────────

add("airodump-ng", """
tool: airodump-ng
tags: [scanning, wireless, m02]
exam_hint: "airodump-ng captures Wi-Fi traffic and lists nearby access points, clients, and signal strength — the first step in wireless auditing."
docs:
  - https://www.aircrack-ng.org/doku.php?id=airodump-ng

actions:
  - title: Enable monitor mode on wireless adapter
    desc: Puts your Wi-Fi adapter into monitor mode so it can capture all wireless traffic, not just your connected network. Lab only.
    command: "sudo airmon-ng start {{interface|wlan0}}"

  - title: Scan for nearby Wi-Fi networks
    desc: Lists all visible access points with BSSID, channel, encryption type, and connected clients. Lab only.
    command: "sudo airodump-ng {{interface|wlan0mon}}"

  - title: Capture traffic from one access point
    desc: Focuses on a specific access point by BSSID and saves captured packets to a file for analysis.
    command: "sudo airodump-ng -b {{mac|AA:BB:CC:DD:EE:FF}} --write {{output|capture}} {{interface|wlan0mon}}"

  - title: Capture on a specific channel
    desc: Locks to channel 6 and captures all wireless traffic on that channel.
    command: "sudo airodump-ng -c 6 -w {{output|capture}} {{interface|wlan0mon}}"

  - title: Save results as CSV for analysis
    desc: Captures wireless data and saves access point and client lists as CSV files.
    command: "sudo airodump-ng -w {{output|scan}} --output-format csv {{interface|wlan0mon}}"
""")

add("reaver", """
tool: reaver
tags: [scanning, wireless, m02]
exam_hint: "reaver brute-forces WPS PIN codes on Wi-Fi routers — can recover the WPA password if WPS is enabled."
docs:
  - https://github.com/t6x/reaver-wps-fork-t6x

actions:
  - title: Attack WPS PIN on an access point
    desc: Attempts to brute-force the 8-digit WPS PIN on a target router to recover the WPA password. Lab networks only.
    command: "sudo reaver -i {{interface|wlan0mon}} -b {{mac|AA:BB:CC:DD:EE:FF}} -vv"

  - title: Attack WPS without associating first
    desc: Runs the WPS attack without first connecting to the access point — useful when association fails.
    command: "sudo reaver -i {{interface|wlan0mon}} -b {{mac|AA:BB:CC:DD:EE:FF}} -vv --no-associate"

  - title: Ignore locked WPS state
    desc: Continues the WPS attack even if the router reports WPS as locked — some routers unlock after a timeout.
    command: "sudo reaver -i {{interface|wlan0mon}} -b {{mac|AA:BB:CC:DD:EE:FF}} -vv -N"

  - title: Use a known WPS PIN directly
    desc: If you already know the WPS PIN, use it directly to recover the WPA password.
    command: "sudo reaver -i {{interface|wlan0mon}} -b {{mac|AA:BB:CC:DD:EE:FF}} -p {{pin|12345678}}"
""")

add("kismet", """
tool: kismet
tags: [scanning, wireless, m02]
exam_hint: "kismet passively detects wireless networks and clients without connecting — captures SSIDs, encryption, and device types."
docs:
  - https://www.kismetwireless.net/

actions:
  - title: Start Kismet wireless detector
    desc: Launches Kismet to passively detect all wireless networks and clients in range. Lab only.
    command: "sudo kismet"

  - title: Monitor a specific wireless interface
    desc: Starts Kismet on your chosen Wi-Fi adapter to capture and log wireless activity.
    command: "sudo kismet -i {{interface|wlan0}}"

  - title: Enable monitor mode then start Kismet
    desc: Puts the adapter in monitor mode first, then starts Kismet on the monitor interface.
    command: "sudo airmon-ng start {{interface|wlan0}} && sudo kismet -i {{interface|wlan0mon}}"

  - title: Log wireless detections to file
    desc: Runs Kismet and saves detected networks and clients to log files for later analysis.
    command: "sudo kismet --log-types btsummary --log-title {{output|kismet}} -i {{interface|wlan0mon}}"
""")

add("airbase-ng", """
tool: airbase-ng
tags: [scanning, wireless, m02]
exam_hint: "airbase-ng creates a fake Wi-Fi access point (evil twin) to capture credentials from connecting clients."
docs:
  - https://www.aircrack-ng.org/doku.php?id=airbase-ng

actions:
  - title: Create a fake access point
    desc: Creates a rogue Wi-Fi network with a chosen name on channel 6. Clients may connect thinking it is legitimate. Lab only.
    command: "sudo airbase-ng -e {{ssid|FakeNetwork}} -c 6 -v {{interface|wlan0mon}}"

  - title: Fake AP with specific MAC address
    desc: Creates a rogue AP mimicking a real access point's MAC address — evil twin attack.
    command: "sudo airbase-ng -e {{ssid|FakeNetwork}} -a {{mac|00:11:22:33:44:55}} -c 6 {{interface|wlan0mon}}"

  - title: Set up DHCP for connected clients
    desc: After creating the fake AP, configure IP addressing so connecting clients get network access.
    command: "sudo ifconfig at0 {{ip|192.168.1.1}} netmask 255.255.255.0"

  - title: Capture traffic from fake AP clients
    desc: Records all network traffic from clients connected to your rogue access point.
    command: "sudo tcpdump -i at0 -w {{output|capture.pcap}}"
""")

# ── Service Enumeration ───────────────────────────────────────────────────

add("enum4linux-ng", """
tool: enum4linux-ng
tags: [enumeration, smb, m02]
exam_hint: "enum4linux-ng is the modern Python rewrite of enum4linux — enumerates SMB users, groups, shares, and policies on Windows/Linux Samba hosts."
docs:
  - https://github.com/cddmp/enum4linux-ng

actions:
  - title: Run all enumeration checks
    desc: Performs every available SMB/NetBIOS enumeration test against the target — users, groups, shares, policies. Lab targets only.
    command: "enum4linux-ng -A {{ip}}"

  - title: List SMB shares
    desc: Shows all shared folders on the target and whether they allow read or write access.
    command: "enum4linux-ng -M {{ip}}"

  - title: Enumerate user accounts
    desc: Lists all user accounts exposed through SMB/NetBIOS on the target.
    command: "enum4linux-ng -U {{ip}}"

  - title: Enumerate groups
    desc: Lists all groups and their members on the target system.
    command: "enum4linux-ng -G {{ip}}"

  - title: Check password policy
    desc: Retrieves the domain or local password policy — minimum length, complexity, lockout settings.
    command: "enum4linux-ng -P {{ip}}"

  - title: Try null session enumeration
    desc: Attempts enumeration using an anonymous/null session — works when SMB allows unauthenticated access.
    command: "enum4linux-ng --null-session {{ip}}"

  - title: Save results as YAML report
    desc: Runs full enumeration and exports structured results to a YAML file.
    command: "enum4linux-ng -A -oY {{output|enum4linux-ng.yaml}} {{ip}}"
""")

add("smbmap", """
tool: smbmap
tags: [enumeration, smb, m02]
exam_hint: "smbmap lists SMB shares on a target and shows read/write permissions — quickly find accessible file shares."
docs:
  - https://github.com/ShawnDEvans/smbmap

actions:
  - title: List shares with guest access
    desc: Shows all SMB shares on the target and whether guest/anonymous access is allowed. Lab targets only.
    command: "smbmap -H {{ip}}"

  - title: List shares with credentials
    desc: Authenticates with a username and password, then lists all accessible shares and permissions.
    command: "smbmap -u {{user|administrator}} -p {{pass|password}} -H {{ip}}"

  - title: Recursively list files in a share
    desc: Lists all files and folders inside a specific share — useful for finding sensitive documents.
    command: "smbmap -H {{ip}} -r {{share|C$}}"

  - title: Download a file from a share
    desc: Downloads a specific file from an accessible SMB share to your local machine.
    command: "smbmap -H {{ip}} --download '{{share|C$}}/path/to/file.txt'"
""")

add("smbeagle", """
tool: smbeagle
tags: [enumeration, smb, m02]
exam_hint: "SMBeagle searches SMB shares across a network for files containing passwords, secrets, and sensitive data."
docs:
  - https://github.com/punk-security/smbeagle

actions:
  - title: Scan SMB shares for sensitive files
    desc: Crawls accessible SMB shares and searches file contents for passwords, API keys, and credentials. Lab targets only.
    command: "SMBeagle -o {{output|results.csv}} -a {{user|administrator}} -p {{pass|password}} -d {{domain|WORKGROUP}}"

  - title: Scan with domain credentials
    desc: Authenticates with domain credentials and searches all reachable shares for sensitive content.
    command: "SMBeagle -o {{output|results.csv}} -u {{user|admin}} -p {{pass|password}} -d {{domain|CORP}}"
""")

add("nullinux", """
tool: nullinux
tags: [enumeration, smb, m02]
exam_hint: "nullinux automates SMB null session enumeration — finds users, groups, shares, and services without credentials."
docs:
  - https://github.com/m8r0wn/nullinux

actions:
  - title: Full null session enumeration
    desc: Uses anonymous SMB access to enumerate users, groups, shares, and OS info on the target. Lab targets only.
    command: "python3 nullinux.py {{ip}}"

  - title: Enumerate with verbose output
    desc: Same enumeration with detailed output showing each step and finding.
    command: "python3 nullinux.py {{ip}} -v"
""")

add("nmblookup", """
tool: nmblookup
tags: [enumeration, netbios, m02]
exam_hint: "nmblookup queries NetBIOS names on a network — finds Windows computer names, workgroups, and master browsers."
docs:
  - "man:nmblookup"

actions:
  - title: Look up NetBIOS name from IP
    desc: Queries the NetBIOS name registered to an IP address — reveals the Windows computer name. Lab targets only.
    command: "nmblookup -A {{ip}}"

  - title: Resolve a NetBIOS name to IP
    desc: Looks up the IP address for a known NetBIOS computer name on the network.
    command: "nmblookup {{hostname|TARGETPC}}"

  - title: Broadcast query for all NetBIOS names
    desc: Sends a broadcast request to discover all NetBIOS names on the local subnet.
    command: "nmblookup -B {{ip}} '*'"
""")

add("nbtscan", """
tool: nbtscan
tags: [enumeration, netbios, m02]
exam_hint: "nbtscan scans a subnet for NetBIOS name information — fast way to find Windows hosts and their workgroup names."
docs:
  - https://www.kali.org/tools/nbtscan/

actions:
  - title: Scan subnet for NetBIOS names
    desc: Scans every IP in a subnet and reports NetBIOS computer names, users, and workgroups. Lab targets only.
    command: "nbtscan {{ip}}/24"

  - title: Scan a single IP address
    desc: Queries NetBIOS information from one specific target IP.
    command: "nbtscan {{ip}}"

  - title: Scan in reverse order with verbose output
    desc: Scans the subnet in reverse IP order with detailed output for each host found.
    command: "nbtscan -r -v {{ip}}/24"
""")

add("nbtstat", """
tool: nbtstat
tags: [enumeration, netbios, m02]
exam_hint: "nbtstat is the Windows built-in NetBIOS query tool — lists computer names, workgroups, and cached sessions."
docs: []

actions:
  - title: Look up NetBIOS name table by IP
    desc: Windows command — shows the NetBIOS name table for a remote IP address including computer name and services.
    command: "nbtstat -A {{ip}}"

  - title: Look up NetBIOS name table by hostname
    desc: Queries NetBIOS information using the remote computer's hostname.
    command: "nbtstat -a {{hostname|TARGETPC}}"

  - title: Show local NetBIOS names
    desc: Lists NetBIOS names registered on the local Windows machine.
    command: "nbtstat -n"

  - title: Show cached NetBIOS name list
    desc: Displays the NetBIOS name cache showing recently resolved names and their IPs.
    command: "nbtstat -c"
""")

add("snmpwalk", """
tool: snmpwalk
tags: [enumeration, snmp, m02]
exam_hint: "snmpwalk queries an SNMP-enabled device and walks through all available management data — often reveals system info, network config, and processes."
docs:
  - "man:snmpwalk"

actions:
  - title: Walk SNMP tree with public community
    desc: Queries all SNMP data using the default 'public' community string — many devices still use this. Lab targets only.
    command: "snmpwalk -v2c -c public {{ip}}"

  - title: Walk SNMP with private community
    desc: Tries the 'private' community string which sometimes has read-write access to device settings.
    command: "snmpwalk -v2c -c private {{ip}}"

  - title: Walk a specific SNMP branch
    desc: Queries only the system information branch (OID 1.3.6.1.2.1.1) for hostname, uptime, and description.
    command: "snmpwalk -v2c -c public {{ip}} 1.3.6.1.2.1.1"

  - title: Save SNMP output to a file
    desc: Walks the full SNMP tree and saves all output to a file for offline analysis.
    command: "snmpwalk -v2c -c public {{ip}} > {{output|snmpwalk.txt}}"
""")

add("snmp-check", """
tool: snmp-check
tags: [enumeration, snmp, m02]
exam_hint: "snmp-check quickly summarizes SNMP-exposed information — system details, network interfaces, routing, and running processes."
docs:
  - https://www.kali.org/tools/snmp-check/

actions:
  - title: Check SNMP with public community
    desc: Runs a high-level SNMP assessment using the default 'public' community string. Shows system info and interfaces. Lab targets only.
    command: "snmp-check -t {{ip}} -c public"

  - title: Check SNMP with private community
    desc: Tries the 'private' community string for potentially more detailed or writable SNMP access.
    command: "snmp-check -t {{ip}} -c private"

  - title: Enumerate all SNMP information
    desc: Runs all available SNMP enumeration modules against the target.
    command: "snmp-check -t {{ip}} -c public -r"
""")

add("ike-scan", """
tool: ikescan
tags: [enumeration, vpn, m02]
exam_hint: "ike-scan discovers IPsec VPN endpoints and extracts pre-shared key hashes for offline cracking."
docs:
  - https://www.kali.org/tools/ike-scan/

actions:
  - title: Discover IPsec VPN on a host
    desc: Sends IKE probes to check if the target runs an IPsec VPN and identifies the VPN software. Lab targets only.
    command: "ike-scan {{ip}}"

  - title: Aggressive mode VPN fingerprint
    desc: Uses IKE aggressive mode to extract the pre-shared key hash — can be cracked offline with hashcat.
    command: "ike-scan --aggressive {{ip}}"

  - title: Show VPN vendor and version
    desc: Displays detailed vendor identification and IKE version information from the target.
    command: "ike-scan -M {{ip}}"
""")

add("udp-proto-scanner", """
tool: udp-proto-scanner
tags: [enumeration, udp, m02]
exam_hint: "udp-proto-scanner probes UDP ports to identify which services are running — finds DNS, SNMP, NTP, and other UDP services."
docs:
  - https://github.com/CiscoCXSecurity/udp-proto-scanner

actions:
  - title: Scan UDP services on a target
    desc: Sends UDP probes to common ports and identifies running services like DNS, SNMP, DHCP, and NTP. Lab targets only.
    command: "perl udp-proto-scanner.pl {{ip}}"

  - title: Scan UDP on a subnet
    desc: Runs UDP service detection across every host in a subnet range.
    command: "perl udp-proto-scanner.pl {{ip}}/24"
""")

add("puredns", """
tool: puredns
tags: [enumeration, dns, m02]
exam_hint: "puredns resolves massive subdomain wordlists quickly — filters out wildcard DNS responses for accurate results."
docs:
  - https://github.com/d3mondev/puredns

actions:
  - title: Brute-force subdomains from wordlist
    desc: Tries every name in a wordlist against the target domain and returns only subdomains that actually resolve. Lab targets only.
    command: "puredns bruteforce {{wordlist|/usr/share/wordlists/dnsmap.txt}} {{domain}}"

  - title: Brute-force with custom resolvers
    desc: Uses your own DNS resolver list for faster and more reliable subdomain resolution.
    command: "puredns bruteforce {{wordlist|wordlist.txt}} {{domain}} -r {{file|resolvers.txt}}"

  - title: Resolve a list of subdomains
    desc: Takes an existing subdomain list and validates which ones actually resolve to an IP address.
    command: "puredns resolve {{file|subs.txt}} -r {{file|resolvers.txt}}"

  - title: Brute-force with wildcard detection
    desc: Brute-forces subdomains while automatically detecting and filtering wildcard DNS responses.
    command: "puredns bruteforce {{wordlist|wordlist.txt}} {{domain}} --wildcard-detection"
""")

add("ntpdate", """
tool: ntpdate
tags: [enumeration, ntp, m02]
exam_hint: "ntpdate queries NTP time servers — can reveal NTP version and whether the server allows monlist queries (amplification risk)."
docs:
  - "man:ntpdate"

actions:
  - title: Query time from NTP server
    desc: Asks the target NTP server for the current time — confirms the service is running. Lab targets only.
    command: "ntpdate {{ip}}"

  - title: Query without setting local clock
    desc: Checks the NTP server response without changing your system clock — read-only query.
    command: "ntpdate -q {{ip}}"

  - title: Check if NTP port is open
    desc: Uses nmap to verify UDP port 123 (NTP) is open on the target before running NTP tools.
    command: "nmap -sU -p 123 {{ip}}"
""")

add("ntpq", """
tool: ntpq
tags: [enumeration, ntp, m02]
exam_hint: "ntpq queries NTP server status — shows peer connections, stratum level, and synchronization state."
docs:
  - "man:ntpq"

actions:
  - title: Show NTP peer status
    desc: Displays the NTP server's peer list and synchronization status. Lab targets only.
    command: "ntpq -p {{ip}}"

  - title: Read NTP server variables
    desc: Queries internal NTP configuration variables — may reveal version, peers, and reference clocks.
    command: "ntpq -c readvar {{ip}}"

  - title: List NTP associations
    desc: Shows all NTP associations and their reachability status.
    command: "ntpq -c associations {{ip}}"
""")

add("ntpdc", """
tool: ntpdc
tags: [enumeration, ntp, m02]
exam_hint: "ntpdc controls and queries NTP daemon — the monlist command can reveal all recent NTP clients (amplification attack vector)."
docs:
  - "man:ntpdc"

actions:
  - title: Get NTP monlist (client history)
    desc: Requests the list of recent NTP clients — reveals IPs that synced with this server. Known amplification vector. Lab only.
    command: "ntpdc -c monlist {{ip}}"

  - title: Show NTP peer information
    desc: Lists upstream NTP peers this server synchronizes with.
    command: "ntpdc -c peers {{ip}}"

  - title: List all NTP peers in detail
    desc: Detailed peer list including stratum, offset, and delay for each upstream server.
    command: "ntpdc -c listpeers {{ip}}"
""")

add("ntptrace", """
tool: ntptrace
tags: [enumeration, ntp, m02]
exam_hint: "ntptrace follows the NTP synchronization chain — shows which upstream time servers a target relies on."
docs:
  - "man:ntptrace"

actions:
  - title: Trace NTP synchronization path
    desc: Follows the chain of NTP servers from the target back to the primary time source. Lab targets only.
    command: "ntptrace {{ip}}"

  - title: Trace with maximum hop limit
    desc: Traces the NTP chain but stops after a set number of hops to avoid long traces.
    command: "ntptrace -m 5 {{ip}}"
""")

add("recon-ng", """
tool: recon-ng
tags: [enumeration, osint, m02]
exam_hint: "recon-ng is a modular OSINT framework — load modules to harvest contacts, hosts, domains, and credentials from public sources."
docs:
  - https://github.com/lanmaster53/recon-ng

actions:
  - title: Start recon-ng interactive shell
    desc: Opens the recon-ng framework where you load modules and run OSINT tasks. Lab targets only.
    command: "recon-ng"

  - title: Create a workspace for your target
    desc: Creates a named workspace to organize all findings for one engagement.
    command: "recon-ng -w {{keyword|acme_scope}}"

  - title: Search available modules
    desc: Lists all installable recon modules in the marketplace — contacts, hosts, credentials, and more.
    command: "echo 'recon-ng: marketplace search hosts | marketplace search domains | marketplace install <module>'"

  - title: Load a domain host enumeration module
    desc: Loads the Bing domain web module to find hosts associated with a target domain.
    command: "echo 'recon-ng: modules load recon/domains-hosts/bing_domain_web | options set SOURCE {{domain}} | run'"
""")

add("recon-dog", """
tool: recon-dog
tags: [enumeration, osint, m02]
exam_hint: "ReconDog is a simple all-in-one recon tool — enter a domain and it runs WHOIS, DNS, port scan, and CMS detection automatically."
docs:
  - https://github.com/s0md3v/ReconDog

actions:
  - title: Install ReconDog
    desc: Clones the ReconDog repository and prepares it for use. Lab targets only.
    command: "git clone https://github.com/s0md3v/ReconDog.git && cd ReconDog"

  - title: Run ReconDog interactive scanner
    desc: Starts the interactive menu — choose scan types for your target domain or IP.
    command: "python3 dog"

  - title: ReconDog workflow reminder
    desc: Prints the menu options available in ReconDog — WHOIS, DNS, port scan, CMS detect, and more.
    command: "echo 'ReconDog: python3 dog — select scan type, enter {{domain}} or {{ip}}'"
""")

add("superenum", """
tool: superenum
tags: [enumeration, osint, m02]
exam_hint: "SuperEnum automates multi-phase enumeration — combines port scanning, service detection, and OSINT in one workflow."
docs:
  - https://github.com/topics/enumeration

actions:
  - title: Quick enumeration of a domain
    desc: Runs a fast enumeration pass against a domain — ports, services, and basic OSINT. Lab targets only.
    command: "superenum --target {{domain}} --mode quick"

  - title: Full enumeration of a subnet
    desc: Comprehensive scan of every host in a subnet — all ports, services, and enumeration modules.
    command: "superenum --target {{ip}}/24 --mode full"

  - title: Save enumeration report
    desc: Runs enumeration and exports all findings to a report file.
    command: "superenum --target {{domain}} --output {{output|superenum-report.txt}}"
""")

add("svmap", """
tool: svmap
tags: [enumeration, voip, m02]
exam_hint: "svmap scans networks for SIP (VoIP) servers and extensions — finds IP phones and PBX systems on the network."
docs:
  - https://github.com/EnableSecurity/sipvicious

actions:
  - title: Scan subnet for SIP servers
    desc: Sends SIP OPTIONS probes across a subnet to discover VoIP servers and IP phones. Lab targets only.
    command: "svmap {{ip}}/24"

  - title: Scan a single IP for SIP
    desc: Checks one IP address for running SIP/VoIP services on common ports.
    command: "svmap {{ip}}"
""")

add("rpcscan", """
tool: rpcscan
tags: [enumeration, rpc, m02]
exam_hint: "rpcscan discovers RPC services running on a target — finds NFS shares, mountd, and other remote procedure call services."
docs: []

actions:
  - title: Scan for RPC services
    desc: Probes the target for running RPC services and lists available program numbers and versions. Lab targets only.
    command: "rpcscan {{ip}}"

  - title: Scan specifically for NFS exports
    desc: Checks if the target exports NFS file shares and lists accessible mount points.
    command: "rpcscan {{ip}} --nfs"

  - title: List NFS exports with showmount
    desc: Uses showmount to list directories the target exports via NFS — may allow unauthorized file access.
    command: "showmount -e {{ip}}"
""")

add("softperfect-scanner", """
tool: softperfect-scanner
tags: [enumeration, network, m02]
exam_hint: "SoftPerfect Network Scanner is a Windows GUI tool for ping sweeps, port scans, and remote shutdown of network devices."
docs:
  - https://www.softperfect.com/products/networkscanner/

actions:
  - title: Open SoftPerfect Network Scanner page
    desc: Opens the product page for the Windows network scanner GUI.
    command: "xdg-open https://www.softperfect.com/products/networkscanner/"

  - title: Ping sweep equivalent
    desc: CLI nmap ping sweep to discover live hosts — alternative to SoftPerfect GUI scan.
    command: "nmap -sn {{ip}}/24"
""")

add("nsauditor", """
tool: nsauditor
tags: [enumeration, network, m02]
exam_hint: "Nsauditor is a Windows network security auditor — scans for open ports, shares, services, and known vulnerabilities."
docs:
  - https://www.nsauditor.com

actions:
  - title: Open Nsauditor website
    desc: Opens the Nsauditor product page — Windows network security auditing suite.
    command: "xdg-open https://www.nsauditor.com"

  - title: Full service scan equivalent
    desc: CLI nmap scan with version detection and default scripts — covers many Nsauditor checks.
    command: "nmap -sV -sC {{ip}}"
""")

add("network-performance-monitor", """
tool: network-performance-monitor
tags: [enumeration, network, m02]
exam_hint: "SolarWinds Network Performance Monitor is enterprise software for continuous network device monitoring and discovery."
docs:
  - https://www.solarwinds.com/network-performance-monitor

actions:
  - title: Open NPM product page
    desc: Opens SolarWinds Network Performance Monitor website.
    command: "xdg-open https://www.solarwinds.com/network-performance-monitor"

  - title: Discover network devices with nmap
    desc: CLI equivalent — scans subnet for live hosts and open services.
    command: "nmap -sn {{ip}}/24"
""")

add("netbios-enumerator", """
tool: netbios-enumerator
tags: [enumeration, netbios, m02]
exam_hint: "NetBIOS Enumerator is a Windows GUI tool that scans for NetBIOS names, shares, and user accounts on a network."
docs: []

actions:
  - title: Scan subnet with nbtscan
    desc: CLI equivalent — scans for NetBIOS names and workgroups on a subnet.
    command: "nbtscan {{ip}}/24"

  - title: Full SMB enumeration with enum4linux
    desc: Comprehensive NetBIOS and SMB enumeration from the command line.
    command: "enum4linux -a {{ip}}"
""")

add("ntp-server-scanner", """
tool: ntp-server-scanner
tags: [enumeration, ntp, m02]
exam_hint: "NTP Server Scanner checks NTP servers for misconfigurations like open monlist — can enable amplification attacks."
docs:
  - https://www.softperfect.com

actions:
  - title: Check NTP monlist vulnerability
    desc: Tests if the NTP server responds to monlist queries — a known amplification attack vector. Lab only.
    command: "ntpdc -c monlist {{ip}}"

  - title: Verify NTP port is open
    desc: Confirms UDP port 123 is accessible before running NTP enumeration tools.
    command: "nmap -sU -p 123 {{ip}}"
""")

add("hyena", """
tool: hyena
tags: [enumeration, ad, m02]
exam_hint: "Hyena is a Windows GUI for Active Directory management — enumerate users, groups, computers, and policies in AD environments."
docs:
  - https://www.systemtools.com/hyena/

actions:
  - title: Open Hyena product page
    desc: Opens the SystemTools Hyena website — Windows AD management and enumeration GUI.
    command: "xdg-open https://www.systemtools.com/hyena/"

  - title: Enumerate AD users with ldapsearch
    desc: CLI equivalent — lists all user accounts in Active Directory via LDAP.
    command: "ldapsearch -x -H ldap://{{ip}} -b 'DC={{domain}},DC=local' '(objectClass=user)' cn"
""")

add("global-network-inventory", """
tool: global-network-inventory
tags: [enumeration, network, m02]
exam_hint: "Global Network Inventory is a Windows agent-based tool that scans and catalogs all hardware and software on network computers."
docs:
  - https://www.magnetosoft.com/product/global_network_inventory/

actions:
  - title: Open product page
    desc: Opens the Global Network Inventory website.
    command: "xdg-open https://www.magnetosoft.com/product/global_network_inventory/"

  - title: Network inventory with nmap
    desc: CLI equivalent — discovers hosts and identifies OS and services on the network.
    command: "nmap -A {{ip}}/24"
""")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name, content in sorted(CHEATS.items()):
        path = OUT / f"{name}.yaml"
        path.write_text(content, encoding="utf-8")
        print(f"wrote {path.name}")
    print(f"\nTotal new files: {len(CHEATS)}")


if __name__ == "__main__":
    main()
