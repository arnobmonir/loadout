#!/usr/bin/env python3
"""Generate Module 01 reconnaissance cheat YAML files."""

from __future__ import annotations

from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "loadout" / "cheats" / "01-reconnaissance"

# tool filename -> YAML content (without leading ---)
CHEATS: dict[str, str] = {}

def add(name: str, content: str) -> None:
    CHEATS[name] = content.strip() + "\n"


# --- Passive Scanning ---
add("builtwith", """
tool: builtwith
tags: [recon, passive, osint, m01]
exam_hint: "Passive tech-stack profiler — CMS, analytics, hosting, frameworks from a domain"
docs:
  - https://builtwith.com

actions:
  - title: open profile
    desc: Open BuiltWith technology profile for domain (authorized lab)
    command: "xdg-open https://builtwith.com/{{domain}}"

  - title: curl profile
    desc: Fetch BuiltWith page HTML for offline review
    command: "curl -sL https://builtwith.com/{{domain}} -o {{output|builtwith.html}}"
""")

add("viewdns-reverse-ip", """
tool: viewdns-reverse-ip
tags: [recon, passive, dns, m01]
exam_hint: "Reverse IP lookup — find all domains hosted on a shared IP"
docs:
  - https://viewdns.info/reverseip/

actions:
  - title: reverse IP lookup
    desc: Open reverse IP domain list for target IP (authorized lab)
    command: "xdg-open https://viewdns.info/reverseip/?host={{ip}}&t=1"

  - title: save reverse IP page
    desc: Download reverse IP results HTML
    command: "curl -sL 'https://viewdns.info/reverseip/?host={{ip}}&t=1' -o {{output|reverse-ip.html}}"
""")

add("mxtoolbox-reverse", """
tool: mxtoolbox-reverse
tags: [recon, passive, dns, m01]
exam_hint: "MXToolbox reverse DNS/IP lookup — map IP to associated domains"
docs:
  - https://mxtoolbox.com/ReverseLookup.aspx

actions:
  - title: reverse lookup
    desc: Open MXToolbox reverse lookup for IP (authorized lab)
    command: "xdg-open https://mxtoolbox.com/ReverseLookup.aspx"

  - title: PTR super tool
    desc: Run PTR lookup via MXToolbox SuperTool
    command: "xdg-open https://mxtoolbox.com/SuperTool.aspx?action=ptr%3a{{ip}}"
""")

add("domaintools-whois", """
tool: domaintools-whois
tags: [recon, passive, whois, m01]
exam_hint: "Premium WHOIS portal with historical domain intel — cross-check CLI whois"
docs:
  - https://whois.domaintools.com/

actions:
  - title: domain whois portal
    desc: Open DomainTools WHOIS for domain (authorized lab)
    command: "xdg-open https://whois.domaintools.com/{{domain}}"

  - title: IP whois portal
    desc: Open DomainTools WHOIS for IP block
    command: "xdg-open https://whois.domaintools.com/{{ip}}"
""")

add("mxtoolbox-whois", """
tool: mxtoolbox-whois
tags: [recon, passive, whois, m01]
exam_hint: "WHOIS plus DNS/MX health indicators in one MXToolbox UI"
docs:
  - https://mxtoolbox.com/whois.aspx

actions:
  - title: whois super tool
    desc: Run WHOIS lookup via MXToolbox (authorized lab)
    command: "xdg-open https://mxtoolbox.com/SuperTool.aspx?action=whois%3a{{domain}}"

  - title: DNS health check
    desc: Open MXToolbox DNS lookup for domain
    command: "xdg-open https://mxtoolbox.com/SuperTool.aspx?action=dns%3a{{domain}}"
""")

add("verisign-whois", """
tool: verisign-whois
tags: [recon, passive, whois, m01]
exam_hint: "Authoritative registry WHOIS for Verisign TLDs (.com, .net)"
docs:
  - https://www.verisign.com/en_US/domain-names/whois/

actions:
  - title: verisign portal
    desc: Open Verisign WHOIS search portal (authorized lab)
    command: "xdg-open https://www.verisign.com/en_US/domain-names/whois/index.xhtml"

  - title: CLI cross-check
    desc: Compare Verisign portal against CLI whois output
    command: "whois {{domain}} | tee {{output|whois-verisign.txt}}"
""")

# --- Domain Research CLI ---
add("dnsrecon", """
tool: dnsrecon
tags: [recon, dns, m01]
exam_hint: "DNS enum, subdomain brute-force, and zone transfer (-t axfr) testing"
docs:
  - https://github.com/darkoperator/dnsrecon

actions:
  - title: standard enum
    desc: Enumerate DNS records for domain (authorized lab)
    command: "dnsrecon -d {{domain}}"

  - title: subdomain brute
    desc: Brute-force subdomains with wordlist
    command: "dnsrecon -d {{domain}} -D {{wordlist|/usr/share/wordlists/dnsmap.txt}} -t brt"

  - title: zone transfer
    desc: Attempt AXFR against discovered nameservers
    command: "dnsrecon -d {{domain}} -t axfr"

  - title: save report
    desc: Write XML report to file
    command: "dnsrecon -d {{domain}} -x {{output|dnsrecon.xml}}"
""")

add("nslookup", """
tool: nslookup
tags: [recon, dns, m01]
exam_hint: "Built-in DNS resolver — use -type=mx for mail server discovery"
docs:
  - "man:nslookup"

actions:
  - title: forward lookup
    desc: Resolve hostname to addresses
    command: "nslookup {{domain}}"

  - title: MX records
    desc: Query mail exchange records
    command: "nslookup -type=mx {{domain}}"

  - title: NS records
    desc: Query authoritative nameservers
    command: "nslookup -type=ns {{domain}}"

  - title: custom resolver
    desc: Query via specific DNS server
    command: "nslookup {{domain}} {{ip}}"
""")

add("fierce", """
tool: fierce
tags: [recon, dns, m01]
exam_hint: "DNS recon with --traverse (IP range) and --wide (neighbor IP scan)"
docs:
  - https://github.com/mschwager/fierce

actions:
  - title: basic enum
    desc: Basic domain and subdomain enumeration (authorized lab)
    command: "fierce --domain {{domain}}"

  - title: target subdomains
    desc: Enumerate specific subdomain names
    command: "fierce --domain {{domain}} --subdomains admin mail www"

  - title: traverse IPs
    desc: Traverse IP ranges around discovered hosts
    command: "fierce --domain {{domain}} --subdomains mail --traverse 10"

  - title: wide scan
    desc: Scan neighboring IP space (noisy — lab only)
    command: "fierce --domain {{domain}} --wide"
""")

add("sublist3r", """
tool: sublist3r
tags: [recon, dns, m01]
exam_hint: "Passive subdomain enum from search engines; -b enables brute-force"
docs:
  - https://github.com/aboul3la/Sublist3r

actions:
  - title: passive enum
    desc: Enumerate subdomains from search engines (authorized lab)
    command: "sublist3r -d {{domain}}"

  - title: save output
    desc: Write discovered subdomains to file
    command: "sublist3r -d {{domain}} -o {{output|sublist3r.txt}}"

  - title: with ports
    desc: Enumerate and check common ports on discovered hosts
    command: "sublist3r -d {{domain}} -p 80,443,8080"

  - title: brute force
    desc: Enable DNS brute-force mode
    command: "sublist3r -d {{domain}} -b"
""")

add("turbolist3r", """
tool: turbolist3r
tags: [recon, dns, m01]
exam_hint: "Faster Sublist3r fork — multi-threaded passive enum plus DNS brute-force"
docs:
  - https://github.com/fleetcaptain/Turbolist3r

actions:
  - title: passive enum
    desc: Multi-threaded passive subdomain discovery (authorized lab)
    command: "python3 turbolist3r.py -d {{domain}}"

  - title: with brute force
    desc: Passive enum plus DNS brute-force with wordlist
    command: "python3 turbolist3r.py -d {{domain}} -b -w {{wordlist|/usr/share/wordlists/dnsmap.txt}}"

  - title: save output
    desc: Write results to output file
    command: "python3 turbolist3r.py -d {{domain}} -o {{output|turbolist3r.txt}}"
""")

add("knockpy", """
tool: knockpy
tags: [recon, dns, m01]
exam_hint: "DNS subdomain brute-forcer — knockpy resolves wordlist candidates to live hosts"
docs:
  - https://github.com/guelfoweb/knock

actions:
  - title: default wordlist
    desc: Brute-force subdomains with built-in wordlist (authorized lab)
    command: "knockpy {{domain}}"

  - title: custom wordlist
    desc: Brute-force with custom subdomain wordlist
    command: "knockpy -w {{wordlist|/usr/share/wordlists/dnsmap.txt}} {{domain}}"

  - title: save JSON
    desc: Export results as JSON
    command: "knockpy {{domain}} --json {{output|knockpy.json}}"
""")

add("photon", """
tool: photon
tags: [recon, web, m01]
exam_hint: "Fast web crawler — --extract-emails, --extract-js, --level for crawl depth"
docs:
  - https://github.com/s0md3v/Photon

actions:
  - title: basic crawl
    desc: Crawl target URL and collect links (authorized lab)
    command: "python3 photon.py -u {{url|https://example.com}}"

  - title: extract emails
    desc: Crawl and extract email addresses
    command: "python3 photon.py -u {{url|https://example.com}} --extract-emails"

  - title: extract JS
    desc: Crawl and extract JavaScript file URLs
    command: "python3 photon.py -u {{url|https://example.com}} --extract-js"

  - title: depth 2 crawl
    desc: Crawl with depth 2 and 20 threads
    command: "python3 photon.py -u {{url|https://example.com}} --level 2 -t 20"
""")

add("sudomy", """
tool: sudomy
tags: [recon, dns, m01]
exam_hint: "Subdomain enum from 30+ sources; --httpx probes live hosts"
docs:
  - https://github.com/screetsec/Sudomy

actions:
  - title: passive enum
    desc: Passive subdomain enumeration (authorized lab)
    command: "sudomy -d {{domain}}"

  - title: with httpx
    desc: Passive enum plus live host probing
    command: "sudomy -d {{domain}} --httpx"

  - title: save output
    desc: Write results to output directory
    command: "sudomy -d {{domain}} -o {{output|sudomy-results}}"

  - title: specific sources
    desc: Limit to Shodan and Certspotter sources
    command: "sudomy -d {{domain}} --source shodan,certspotter"
""")

add("cloud_enum", """
tool: cloud_enum
tags: [recon, cloud, m01]
exam_hint: "Multi-cloud bucket/endpoint discovery by keyword — AWS, Azure, GCP"
docs:
  - https://github.com/initstring/cloud_enum

actions:
  - title: keyword enum
    desc: Enumerate cloud assets by organization keyword (authorized lab)
    command: "python3 cloud_enum.py -k {{keyword|examplecorp}}"

  - title: with wordlist
    desc: Keyword enum with custom mutation wordlist
    command: "python3 cloud_enum.py -k {{keyword|examplecorp}} -w {{wordlist|words.txt}}"

  - title: save report
    desc: Save enumeration report to file
    command: "python3 cloud_enum.py -k {{keyword|examplecorp}} -l {{output|cloud-enum.txt}}"
""")

add("gcp_service_enum", """
tool: gcp_service_enum
tags: [recon, cloud, m01]
exam_hint: "Enumerate publicly reachable GCP services and artifacts for a target"
docs:
  - https://cloud.google.com/security

actions:
  - title: keyword scan
    desc: GCP service enum by keyword (authorized lab)
    command: "gcp_service_enum -k {{keyword|examplecorp}}"

  - title: domain scan
    desc: GCP service enum focused on domain
    command: "gcp_service_enum -d {{domain}}"

  - title: save output
    desc: Write findings to file
    command: "gcp_service_enum -d {{domain}} -o {{output|gcp-enum.txt}}"
""")

add("orb", """
tool: orb
tags: [recon, passive, m01]
exam_hint: "Passive attack-surface mapper via CT logs and passive DNS — JSON output"
docs:
  - https://github.com/reewardius/Orb

actions:
  - title: asset enum
    desc: Passive asset enumeration for domain (authorized lab)
    command: "orb -d {{domain}}"

  - title: save JSON
    desc: Export results to JSON file
    command: "orb -d {{domain}} -o {{output|orb.json}}"

  - title: verbose
    desc: Verbose passive enumeration
    command: "orb -d {{domain}} -v"
""")

add("ldns", """
tool: ldns
tags: [recon, dns, m01]
exam_hint: "drill = dig alternative; ldns-walk = DNSSEC zone walking"
docs:
  - https://www.nlnetlabs.nl/projects/ldns/

actions:
  - title: drill A record
    desc: Query A record with drill (authorized lab)
    command: "drill {{domain}} A"

  - title: drill MX
    desc: Query MX records with drill
    command: "drill {{domain}} MX"

  - title: zone transfer test
    desc: Attempt zone transfer via drill
    command: "drill -T {{domain}} @{{ip}}"

  - title: DNSSEC zone walk
    desc: Walk DNSSEC zone for record enumeration
    command: "ldns-walk {{domain}}"
""")

add("email-spider", """
tool: email-spider
tags: [recon, osint, m01]
exam_hint: "Crawl websites to harvest email addresses for social engineering recon"
docs:
  - https://github.com/needforspeed/emailspider

actions:
  - title: basic harvest
    desc: Extract emails from target website (authorized lab)
    command: "email-spider {{url|https://example.com}}"

  - title: save to file
    desc: Harvest emails and save to file
    command: "email-spider {{url|https://example.com}} -o {{output|emails.txt}}"

  - title: recursive crawl
    desc: Recursive crawl with depth limit
    command: "email-spider {{url|https://example.com}} --depth 3 -o {{output|emails.txt}}"
""")

add("golddigger", """
tool: golddigger
tags: [recon, osint, dorking, m01]
exam_hint: "Search-engine dork automation — finds indexed sensitive files and admin paths"
docs:
  - https://www.exploit-db.com/google-hacking-database

actions:
  - title: files preset
    desc: Search for exposed indexed files (authorized lab)
    command: "golddigger --domain {{domain}} --preset files"

  - title: admin preset
    desc: Search for exposed login and admin paths
    command: "golddigger --domain {{domain}} --preset admin"

  - title: export results
    desc: Export dork results for review
    command: "golddigger --domain {{domain}} --export {{output|golddigger.txt}}"
""")

add("message-digester", """
tool: message-digester
tags: [recon, hashing, m01]
exam_hint: "File integrity hashing — sha256sum for modern workflows; compare against VT feeds"
docs:
  - https://csrc.nist.gov/projects/hash-functions

actions:
  - title: SHA-256
    desc: Compute SHA-256 hash of file
    command: "sha256sum {{file|sample.bin}}"

  - title: SHA-1
    desc: Compute SHA-1 hash of file
    command: "sha1sum {{file|sample.bin}}"

  - title: MD5
    desc: Compute MD5 hash of file (legacy compatibility)
    command: "md5sum {{file|sample.bin}}"
""")

add("dnsdumpster", """
tool: dnsdumpster
tags: [recon, passive, dns, m01]
exam_hint: "Free passive DNS/subdomain mapper with visual hierarchy — no install required"
docs:
  - https://dnsdumpster.com

actions:
  - title: open portal
    desc: Open DNSdumpster for manual domain lookup (authorized lab)
    command: "xdg-open https://dnsdumpster.com"

  - title: note workflow
    desc: Reminder — enter domain in portal, solve CAPTCHA, export results
    command: "echo 'DNSdumpster: search {{domain}} at https://dnsdumpster.com — export subdomain map'"
""")

add("foca", """
tool: foca
tags: [recon, metadata, m01]
exam_hint: "Extracts metadata from public Office/PDF docs — usernames, paths, internal hostnames"
docs:
  - https://www.elevenpaths.com/labstools/foca

actions:
  - title: workflow note
    desc: FOCA is GUI-only — search public docs by domain, extract metadata
    command: "echo 'FOCA GUI: search {{domain}} for public Office/PDF files; review metadata for usernames and paths'"

  - title: exiftool fallback
    desc: CLI metadata extraction from downloaded document
    command: "exiftool {{file|document.pdf}}"
""")

add("searchdiggity", """
tool: searchdiggity
tags: [recon, osint, dorking, m01]
exam_hint: "Bishop Fox GUI for Google/Bing dork packs — automates search-engine recon"
docs:
  - https://www.bishopfox.com/tools/

actions:
  - title: workflow note
    desc: SearchDiggity is GUI-driven — set domain, select dork packs, export results
    command: "echo 'SearchDiggity: target {{domain}}, select query packs, export results for validation'"

  - title: manual dork
    desc: Example Google dork for exposed files on domain
    command: "xdg-open 'https://www.google.com/search?q=site%3A{{domain}}+filetype%3Apdf'"
""")

add("codiga", """
tool: codiga
tags: [recon, sast, m01]
exam_hint: "SAST code analysis in CI — detects insecure coding patterns during recon of code repos"
docs:
  - https://www.codiga.io/

actions:
  - title: analyze project
    desc: Run Codiga static analysis on project path (authorized lab)
    command: "codiga analyze --path {{path|./project}}"

  - title: JSON report
    desc: Export analysis report as JSON
    command: "codiga analyze --path {{path|./project}} --format json > {{output|codiga-report.json}}"
""")

add("sysdig", """
tool: sysdig
tags: [recon, monitoring, m01]
exam_hint: "Runtime system visibility — captures syscalls for threat hunting and IR"
docs:
  - https://docs.sysdig.com/

actions:
  - title: capture trace
    desc: Capture 10-second syscall trace (authorized lab host)
    command: "sudo sysdig -M 10"

  - title: filter process
    desc: Filter events by process name
    command: "sudo sysdig proc.name={{process|nginx}}"

  - title: save capture
    desc: Save capture to file for later analysis
    command: "sudo sysdig -w {{output|sysdig-capture.scap}}"
""")

add("falco", """
tool: falco
tags: [recon, monitoring, m01]
exam_hint: "Runtime threat detection for containers/K8s — alerts on shell spawns and privilege abuse"
docs:
  - https://falco.org/

actions:
  - title: default rules
    desc: Run Falco with default ruleset (authorized lab)
    command: "sudo falco"

  - title: custom rules
    desc: Run Falco with custom rules file
    command: "sudo falco -r {{file|custom_rules.yaml}}"

  - title: version check
    desc: Verify Falco installation
    command: "falco --version"
""")

# --- OSINT ---
add("shodan", """
tool: shodan
tags: [recon, osint, m01]
exam_hint: "Google for IoT — search port:, country:, org:, vuln:CVE- for exposed services"
docs:
  - https://www.shodan.io

actions:
  - title: org search
    desc: Search Shodan for organization (authorized lab)
    command: "xdg-open https://www.shodan.io/search?query=org%3A%22{{domain}}%22"

  - title: IP lookup
    desc: Open Shodan host page for IP
    command: "xdg-open https://www.shodan.io/host/{{ip}}"

  - title: CLI search
    desc: Shodan CLI search (requires API key)
    command: "shodan search 'hostname:{{domain}}'"

  - title: CLI host info
    desc: Shodan CLI host lookup
    command: "shodan host {{ip}}"
""")

add("censys", """
tool: censys
tags: [recon, osint, m01]
exam_hint: "Certificate transparency and internet-wide scan data — alternative to Shodan for SSL/host discovery"
docs:
  - https://search.censys.io

actions:
  - title: host search
    desc: Search Censys hosts for domain (authorized lab)
    command: "xdg-open https://search.censys.io/search?resource=hosts&q={{domain}}"

  - title: cert search
    desc: Search certificate transparency for domain
    command: "xdg-open https://search.censys.io/search?resource=certificates&q=parsed.names%3A{{domain}}"

  - title: CLI search
    desc: Censys CLI host search (requires API key)
    command: "censys search '{{domain}}' --index hosts"
""")

add("zoomeye", """
tool: zoomeye
tags: [recon, osint, m01]
exam_hint: "Shodan alternative with stronger Asia coverage — search ip:, port:, service:, app:"
docs:
  - https://www.zoomeye.org

actions:
  - title: domain search
    desc: Search ZoomEye for domain (authorized lab)
    command: "xdg-open https://www.zoomeye.org/search?q={{domain}}"

  - title: IP search
    desc: Search ZoomEye for IP address
    command: "xdg-open https://www.zoomeye.org/search?q=ip%3A{{ip}}"

  - title: CLI search
    desc: ZoomEye CLI search (requires API key)
    command: "zoomeye search '{{domain}}'"
""")

add("raccoon", """
tool: raccoon
tags: [recon, osint, m01]
exam_hint: "All-in-one Python recon — DNS, WHOIS, subdomains, ports, WAF detection"
docs:
  - https://github.com/evyatarmeged/Raccoon

actions:
  - title: basic recon
    desc: Full recon against domain (authorized lab)
    command: "raccoon {{domain}}"

  - title: output directory
    desc: Save all results to output directory
    command: "raccoon {{domain}} --outdir {{output|results}}"

  - title: skip dns brute
    desc: Passive recon skipping DNS brute-force
    command: "raccoon {{domain}} --skip-dns-brute"

  - title: tor routing
    desc: Route traffic through Tor for anonymized investigation
    command: "raccoon {{domain}} --tor-routing"
""")

add("scout-suite", """
tool: scout-suite
tags: [recon, cloud, m01]
exam_hint: "Multi-cloud config auditor (AWS/Azure/GCP) — finds public S3 buckets, weak IAM"
docs:
  - https://github.com/nccgroup/ScoutSuite

actions:
  - title: AWS audit
    desc: Audit AWS account configuration (authorized lab credentials)
    command: "scout aws --report-dir {{output|scout-aws}}"

  - title: Azure audit
    desc: Audit Azure subscription configuration
    command: "scout azure --report-dir {{output|scout-azure}}"

  - title: GCP audit
    desc: Audit GCP project configuration
    command: "scout gcp --report-dir {{output|scout-gcp}}"
""")

add("web-check", """
tool: web-check
tags: [recon, passive, web, m01]
exam_hint: "All-in-one passive site profiler — DNS, SSL, headers, tech stack, ports"
docs:
  - https://web-check.xyz

actions:
  - title: online check
    desc: Open Web Check for target URL (authorized lab)
    command: "xdg-open https://web-check.xyz/?url=https://{{domain}}"

  - title: self-host docker
    desc: Run Web Check locally via Docker
    command: "docker run -p 3000:3000 lissy93/web-check"

  - title: curl headers
    desc: Quick header check fallback
    command: "curl -sI https://{{domain}}"
""")

add("wayback", """
tool: wayback
tags: [recon, osint, m01]
exam_hint: "Wayback Machine recovers deleted pages, old emails, and historical site versions"
docs:
  - https://web.archive.org

actions:
  - title: calendar view
    desc: Open Wayback calendar for domain (authorized lab)
    command: "xdg-open https://web.archive.org/web/*/{{domain}}"

  - title: CDX API
    desc: Query Wayback CDX API for archived URLs (JSON)
    command: "curl -s 'https://web.archive.org/cdx/search/cdx?url={{domain}}&output=json'"

  - title: save snapshot
    desc: Save latest archived page HTML
    command: "curl -sL 'https://web.archive.org/web/{{domain}}' -o {{output|wayback.html}}"
""")

add("maltego", """
tool: maltego
tags: [recon, osint, m01]
exam_hint: "Graph-based OSINT link analysis — pivots domain to IP to email to person"
docs:
  - https://www.maltego.com

actions:
  - title: launch GUI
    desc: Launch Maltego desktop application (authorized lab)
    command: "maltego"

  - title: workflow note
    desc: Maltego transform workflow for domain footprinting
    command: "echo 'Maltego: new graph, seed {{domain}}, run Domain transforms (DNS, WHOIS, Email)'
""")

add("osint-framework", """
tool: osint-framework
tags: [recon, osint, m01]
exam_hint: "Tree-index of free OSINT tools by indicator type — (T)=local tool, (R)=registration"
docs:
  - https://osintframework.com

actions:
  - title: open framework
    desc: Open OSINT Framework tool directory
    command: "xdg-open https://osintframework.com"

  - title: domain tools
    desc: Open domain/username OSINT section
    command: "xdg-open https://osintframework.com/#!/search/domain"
""")

add("opencorporates", """
tool: opencorporates
tags: [recon, osint, m01]
exam_hint: "Global open corporate database — officers, subsidiaries, business relationships"
docs:
  - https://opencorporates.com/

actions:
  - title: company search
    desc: Search OpenCorporates for company name (authorized lab)
    command: "xdg-open https://opencorporates.com/companies?q={{keyword|example+corp}}"

  - title: API search
    desc: Query OpenCorporates API (requires API token)
    command: "curl -s 'https://api.opencorporates.com/v0.4/companies/search?q={{keyword|example}}&api_token=TOKEN'"
""")

add("exonerator", """
tool: exonerator
tags: [recon, osint, m01]
exam_hint: "Check if an IP was a Tor exit node at a given time — useful for traffic attribution"
docs:
  - https://metrics.torproject.org/exonerator.html

actions:
  - title: open portal
    desc: Open Tor ExoneraTor lookup portal (authorized lab)
    command: "xdg-open https://metrics.torproject.org/exonerator.html"

  - title: check IP note
    desc: Reminder to enter IP and date range in ExoneraTor portal
    command: "echo 'ExoneraTor: check if {{ip}} was a Tor exit node on target date'"
""")

add("dorkgpt", """
tool: dorkgpt
tags: [recon, osint, dorking, m01]
exam_hint: "Natural-language to Google dork converter — passive recon for indexed sensitive content"
docs:
  - https://dorkgpt.com

actions:
  - title: open portal
    desc: Open DorkGPT to generate Google dorks (authorized lab)
    command: "xdg-open https://dorkgpt.com"

  - title: example dork
    desc: Manual dork for exposed PDFs on domain
    command: "xdg-open 'https://www.google.com/search?q=site%3A{{domain}}+filetype%3Apdf'"
""")

add("dorkgenius", """
tool: dorkgenius
tags: [recon, osint, dorking, m01]
exam_hint: "AI Google dork generator — finds exposed files, admin panels, credentials in indexes"
docs:
  - https://dorkgenius.com

actions:
  - title: open portal
    desc: Open DorkGenius dork generator (authorized lab)
    command: "xdg-open https://dorkgenius.com"

  - title: admin panel dork
    desc: Search for admin login pages on domain
    command: "xdg-open 'https://www.google.com/search?q=site%3A{{domain}}+inurl%3Aadmin+login'"
""")

add("darkgpt", """
tool: darkgpt
tags: [recon, osint, m01]
exam_hint: "GPT assistant for querying breach/leaked databases — authorized defensive exposure only"
docs:
  - https://github.com/luijait/DarkGPT

actions:
  - title: install
    desc: Clone DarkGPT repository (authorized lab)
    command: "git clone https://github.com/luijait/DarkGPT && cd DarkGPT && pip install -r requirements.txt"

  - title: configure env
    desc: Copy and edit environment file with API keys
    command: "cp .env.example .env"

  - title: run
    desc: Launch DarkGPT interactive assistant
    command: "python main.py"
""")

add("google-reverse-image", """
tool: google-reverse-image
tags: [recon, osint, m01]
exam_hint: "Upload or paste image URL to find origin and similar images — phishing attribution"
docs:
  - https://images.google.com/

actions:
  - title: open search
    desc: Open Google reverse image search (authorized lab)
    command: "xdg-open https://images.google.com/"

  - title: search by URL
    desc: Reverse image search by image URL
    command: "xdg-open 'https://www.google.com/searchbyimage?image_url={{url|https://example.com/image.jpg}}'"
""")

add("google-word-sniper", """
tool: google-word-sniper
tags: [recon, osint, m01]
exam_hint: "Refines Google search keywords and operators for precise OSINT queries"
docs:
  - https://googlewordsniper.eu

actions:
  - title: open portal
    desc: Open Google Word Sniper keyword tool (authorized lab)
    command: "xdg-open https://googlewordsniper.eu"

  - title: site search
    desc: Refined site-restricted Google search
    command: "xdg-open 'https://www.google.com/search?q=site%3A{{domain}}+{{keyword|password}}'"
""")

add("social-searcher", """
tool: social-searcher
tags: [recon, osint, m01]
exam_hint: "Real-time social media aggregator across Twitter, Facebook, Instagram, LinkedIn"
docs:
  - https://www.social-searcher.com

actions:
  - title: mention search
    desc: Search social mentions for keyword (authorized lab)
    command: "xdg-open https://www.social-searcher.com/social-buzz/?q={{keyword|example}}"

  - title: domain mentions
    desc: Search social mentions for domain
    command: "xdg-open https://www.social-searcher.com/social-buzz/?q={{domain}}"
""")

add("social-catfish", """
tool: social-catfish
tags: [recon, osint, m01]
exam_hint: "People-search OSINT — reverse email, phone, and image lookup"
docs:
  - https://socialcatfish.com

actions:
  - title: open portal
    desc: Open Social Catfish people search (authorized lab)
    command: "xdg-open https://socialcatfish.com"

  - title: reverse email note
    desc: Reminder to search email in Social Catfish portal
    command: "echo 'Social Catfish: reverse lookup for {{email|target@example.com}}'"
""")

add("hunchly", """
tool: hunchly
tags: [recon, osint, m01]
exam_hint: "Auto-captures every visited page with hashes and timestamps — court-grade OSINT evidence"
docs:
  - https://www.hunch.ly/

actions:
  - title: open site
    desc: Open Hunchly documentation and install page
    command: "xdg-open https://www.hunch.ly/"

  - title: workflow note
    desc: Hunchly Chrome extension workflow for evidence capture
    command: "echo 'Hunchly: install Chrome extension, start capture before OSINT session on {{domain}}'"
""")

add("anypicker", """
tool: anypicker
tags: [recon, osint, m01]
exam_hint: "No-code visual web scraper with AI — point-and-click OSINT data extraction"
docs:
  - https://app.anypicker.com

actions:
  - title: open app
    desc: Open AnyPicker visual scraper (authorized lab)
    command: "xdg-open https://app.anypicker.com"
""")

add("bardeen", """
tool: bardeen
tags: [recon, osint, m01]
exam_hint: "No-code browser automation for OSINT — scrape LinkedIn and directories into Sheets"
docs:
  - https://www.bardeen.ai

actions:
  - title: open site
    desc: Open Bardeen.ai automation platform
    command: "xdg-open https://www.bardeen.ai"
""")

add("bright-data", """
tool: bright-data
tags: [recon, osint, m01]
exam_hint: "Residential and datacenter proxy API — route OSINT scrapes through geo-diverse IPs"
docs:
  - https://brightdata.com/products/proxy-api

actions:
  - title: curl via proxy
    desc: Fetch URL through Bright Data proxy (authorized lab, API key required)
    command: "curl -x http://USER:PASS@brd.superproxy.io:22225 -sL https://{{domain}}"

  - title: open docs
    desc: Open Bright Data proxy API documentation
    command: "xdg-open https://brightdata.com/products/proxy-api"
""")

add("chatpdf", """
tool: chatpdf
tags: [recon, osint, m01]
exam_hint: "AI Q&A over uploaded PDFs — extract names, IPs, and tech from corporate reports"
docs:
  - https://chatpdf.com

actions:
  - title: open portal
    desc: Open ChatPDF for document analysis (authorized lab)
    command: "xdg-open https://chatpdf.com"
""")

add("corporationwiki", """
tool: corporationwiki
tags: [recon, osint, m01]
exam_hint: "Corporate intelligence — executive tracking, subsidiary mapping, relationships"
docs:
  - https://www.corporationwiki.com

actions:
  - title: company search
    desc: Search CorporationWiki for company (authorized lab)
    command: "xdg-open https://www.corporationwiki.com/search?query={{keyword|example+corp}}"
""")

add("cylect", """
tool: cylect
tags: [recon, osint, m01]
exam_hint: "AI OSINT aggregator — single search across breach, social, and domain databases"
docs:
  - https://cylect.io

actions:
  - title: open portal
    desc: Open Cylect.io OSINT search (authorized lab)
    command: "xdg-open https://cylect.io"
""")

add("explore-ai", """
tool: explore-ai
tags: [recon, osint, m01]
exam_hint: "Semantic search across YouTube transcripts — find when names or topics are mentioned"
docs:
  - https://exploreai.vercel.app

actions:
  - title: open portal
    desc: Open Explore AI YouTube transcript search
    command: "xdg-open https://exploreai.vercel.app"
""")

add("oss-insight", """
tool: oss-insight
tags: [recon, osint, m01]
exam_hint: "GPT-powered GitHub analytics — natural-language queries over GHArchive data"
docs:
  - https://ossinsight.io

actions:
  - title: open portal
    desc: Open OSS Insight GitHub analytics (authorized lab)
    command: "xdg-open https://ossinsight.io"

  - title: repo search
    desc: Search GitHub repos related to keyword
    command: "xdg-open https://ossinsight.io/analyze/{{keyword|nmap}}"
""")

add("cobwebs", """
tool: cobwebs
tags: [recon, osint, m01]
exam_hint: "Enterprise AI OSINT platform — automated multi-source collection and link analysis"
docs:
  - https://cobwebs.com

actions:
  - title: open portal
    desc: Open PenLink Cobwebs platform info
    command: "xdg-open https://cobwebs.com"
""")

add("taranis-ai", """
tool: taranis-ai
tags: [recon, osint, m01]
exam_hint: "AI/NLP OSINT platform — auto-collects news/RSS, extracts IOCs, generates reports"
docs:
  - https://github.com/taranis-ai/taranis-ai

actions:
  - title: clone repo
    desc: Clone Taranis AI repository (authorized lab)
    command: "git clone https://github.com/taranis-ai/taranis-ai"

  - title: docker deploy note
    desc: Deploy Taranis AI via Docker Compose
    command: "echo 'Taranis AI: see docker-compose.yml in repo for full deployment'"
""")

add("videoreverser", """
tool: videoreverser
tags: [recon, osint, m01]
exam_hint: "Reverses video playback to reveal hidden or obfuscated frames in media forensics"
docs:
  - https://www.videoreverser.com/

actions:
  - title: open portal
    desc: Open VideoReverser.com for frame analysis (authorized lab)
    command: "xdg-open https://www.videoreverser.com/"
""")

add("osint-link", """
tool: osint-link
tags: [recon, osint, m01]
exam_hint: "Curated OSINT portal bookmarks — HIBP for breaches, namechk for username enum"
docs:
  - https://osintframework.com

actions:
  - title: HIBP check
    desc: Check if email appears in known breaches (authorized lab)
    command: "xdg-open https://haveibeenpwned.com/account/{{email|target@example.com}}"

  - title: username enum
    desc: Check username across social platforms via namechk
    command: "xdg-open https://namechk.com/"

  - title: email verify
    desc: Verify email deliverability via trumail
    command: "curl -s https://trumail.io/api/v1/lookups/{{email|target@example.com}}"
""")

add("osint-privacy-tools", """
tool: osint-privacy-tools
tags: [recon, osint, m01]
exam_hint: "Reference table — OpenCorporates, Orbot (Tor proxy), and pod-slurping awareness"
docs:
  - https://opencorporates.com/

actions:
  - title: opencorporates
    desc: Open OpenCorporates for corporate OSINT
    command: "xdg-open https://opencorporates.com/companies?q={{keyword|example}}"

  - title: tor orbot
    desc: Open Tor Project Android download for anonymous OSINT
    command: "xdg-open https://www.torproject.org/download/#android"
""")

add("osint-sh", """
tool: osint-sh
tags: [recon, osint, m01]
exam_hint: "Shell-script OSINT automation — aggregates whois, DNS, breaches, Shodan"
docs:
  - https://osintframework.com

actions:
  - title: basic recon script
    desc: Example OSINT shell pipeline for domain (authorized lab)
    command: "whois {{domain}}; dig {{domain}} ANY +short; host -t mx {{domain}}"

  - title: save recon bundle
    desc: Save whois and DNS output to file
    command: "{ whois {{domain}}; dig {{domain}} ANY; } > {{output|osint-recon.txt}}"
""")

add("cat", """
tool: cat
tags: [recon, linux, m01]
exam_hint: "File viewer — cat -A reveals hidden characters in suspicious configs during recon"
docs:
  - "man:cat"

actions:
  - title: view file
    desc: Display file contents
    command: "cat {{file|/etc/hosts}}"

  - title: show hidden chars
    desc: Reveal tabs, line endings, and non-printing characters
    command: "cat -A {{file|suspicious.txt}}"

  - title: number lines
    desc: View file with line numbers
    command: "cat -n {{file|config.txt}}"

  - title: grep log errors
    desc: View auth log and filter failed logins
    command: "cat /var/log/auth.log | grep Failed"
""")

add("od", """
tool: od
tags: [recon, linux, m01]
exam_hint: "Octal dump — od -tx1 -N 16 reveals file magic bytes (ELF, PE, JPEG)"
docs:
  - "man:od"

actions:
  - title: hex bytes
    desc: Show first 16 bytes as hex (file type identification)
    command: "od -tx1 -N 16 {{file|/usr/bin/ls}}"

  - title: ASCII view
    desc: Show file as ASCII with escape sequences
    command: "od -c -N 64 {{file|sample.bin}}"

  - title: skip offset
    desc: Dump bytes starting at offset 1024
    command: "od -tx1 -j 1024 -N 256 {{file|firmware.bin}}"
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
