#!/usr/bin/env python3
"""Generate loadout cheat YAML from CEH v13 notebook markdown files."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = Path("/home/arnob/CEH/ceh-v13-notebook/Tools")
CHEATS = ROOT / "loadout" / "cheats"
MANIFEST = CHEATS / "manifest.yaml"

MODULES: list[tuple[str, str, str, list[str]]] = [
    ("05 Post Exploitation and Privilege Escalation", "05-post_exploitation_and_privilege_escalation", "m05", ["post", "privesc"]),
    ("06 Defense and Monitoring", "06-defense_and_monitoring", "m06", ["defense", "monitoring"]),
    ("07 Cryptography and Hashing", "07-cryptography_and_hashing", "m07", ["crypto", "hash"]),
    ("08 Malware Analysis and Reverse Engineering", "08-malware_analysis_and_reverse_engineering", "m08", ["malware", "re"]),
    ("09 Social Engineering and Phishing", "09-social_engineering_and_phishing", "m09", ["social", "phishing"]),
    ("10 Cloud IoT and Infrastructure", "10-cloud_iot_and_infrastructure", "m10", ["cloud", "iot"]),
    ("11 System and Network Tools", "11-system_and_network_tools", "m11", ["network", "cli"]),
    ("12 Wireless and Network Attacks", "12-wireless_and_network_attacks", "m12", ["wireless", "attack"]),
    ("13 Authentication and Access Control", "13-authentication_and_access_control", "m13", ["auth", "ad"]),
    ("14 Mobile and Endpoint Security", "14-mobile_and_endpoint_security", "m14", ["mobile", "endpoint"]),
]

SKIP_SLUGS: set[str] = set()  # populated at runtime for cross-module dupes we skip creating

# Extra commands for tools whose notebook pages are thin or GUI-only
EXTRA: dict[str, list[tuple[str, str, str]]] = {
    "impacket": [
        ("Dump secrets from remote host", "Extracts SAM/LSA/NTDS hashes when you have domain creds on a lab DC or member.", "impacket-secretsdump {{domain|lab.local}}/{{user|admin}}:{{pass|password}}@{{ip}}"),
        ("Kerberoast service accounts", "Requests TGS tickets for SPN accounts — crack offline with hashcat mode 13100.", "impacket-GetUserSPNs -request -dc-ip {{ip}} {{domain|lab.local}}/{{user|user}}:{{pass|pass}}"),
        ("Remote shell via psexec", "Gets a semi-interactive shell on a Windows lab host using SMB exec.", "impacket-psexec {{domain|lab.local}}/{{user|administrator}}:{{pass|password}}@{{ip}}"),
        ("Remote shell via wmiexec", "Stealthier than psexec — runs commands over WMI on authorized Windows targets.", "impacket-wmiexec {{domain|lab.local}}/{{user|admin}}:{{pass|pass}}@{{ip}}"),
        ("Remote shell via smbexec", "Fileless-ish execution returning command output over SMB.", "impacket-smbexec {{domain|lab.local}}/{{user|admin}}:{{pass|pass}}@{{ip}}"),
    ],
    "crackmapexec": [
        ("Enumerate SMB hosts on subnet", "Sprays SMB check across a CIDR to find live Windows hosts and signing status.", "crackmapexec smb {{ip}}/24"),
        ("List shares with credentials", "Shows accessible SMB shares after you have valid lab creds.", "crackmapexec smb {{ip}} -u {{user|admin}} -p {{pass|password}} --shares"),
        ("Password spray one password", "Tries one password against many users — watch lockout policy on lab AD.", "crackmapexec smb {{ip}} -u {{users|users.txt}} -p {{pass|Password1}} --continue-on-success"),
        ("Execute command on host via WinRM", "Runs one command on a target where WinRM is open and creds work.", "crackmapexec winrm {{ip}} -u {{user|admin}} -p {{pass|password}} -x {{cmd|whoami}}"),
        ("Pass-the-hash over SMB", "Uses NTLM hash instead of password for lateral movement in lab AD.", "crackmapexec smb {{ip}} -u {{user|administrator}} -H {{hash|NTLMHASH}}"),
    ],
    "winpeas": [
        ("Run WinPEAS locally on Windows", "Upload winPEAS.exe to lab box and run — highlights privesc paths (services, tokens, creds).", "winPEAS.exe"),
        ("Run WinPEAS quiet mode", "Less verbose output — good for logging to file on constrained shells.", "winPEAS.exe quiet"),
        ("Run linPEAS on Linux pivot", "If you landed on Linux, use linPEAS from PEASS-ng for the same enum workflow.", "curl -L https://github.com/carlospolop/PEASS-ng/releases/latest/download/linpeas.sh | sh"),
    ],
    "peass-ng": [
        ("Download and run linPEAS", "Automated Linux privesc enum — run first after shell on lab Linux host.", "curl -L https://github.com/carlospolop/PEASS-ng/releases/latest/download/linpeas.sh | sh"),
        ("Run winPEAS on Windows lab host", "Windows variant — checks services, unquoted paths, AlwaysInstallElevated, etc.", "winPEAS.exe"),
    ],
    "hashcat": [
        ("Identify hash type", "Before cracking, confirm hash mode with hashid or hashcat example hashes.", "hashid {{hash|hash.txt}}"),
        ("Crack NTLM hashes mode 1000", "Offline crack Windows NT hashes from secretsdump or mimikatz output.", "hashcat -m 1000 {{hashes|ntlm.txt}} {{wordlist|/usr/share/wordlists/rockyou.txt}}"),
        ("Crack Kerberos TGS mode 13100", "Kerberoast output — run after GetUserSPNs in lab AD.", "hashcat -m 13100 {{hashes|tgs.txt}} {{wordlist|/usr/share/wordlists/rockyou.txt}}"),
        ("Show cracked passwords", "Displays recovered plaintext after a hashcat session completes.", "hashcat -m 1000 {{hashes|ntlm.txt}} --show"),
    ],
    "john": [
        ("Crack hashes with wordlist", "Classic offline password cracker — auto-detects many hash formats.", "john --wordlist={{wordlist|/usr/share/wordlists/rockyou.txt}} {{hashes|hashes.txt}}"),
        ("Show cracked passwords", "Prints recovered credentials after john completes.", "john --show {{hashes|hashes.txt}}"),
        ("Extract hash from shadow file", "Prepare unshadowed file from /etc/shadow and passwd on Linux lab dump.", "unshadow passwd shadow > {{output|unshadowed.txt}} && john {{output|unshadowed.txt}}"),
    ],
    "bloodhound": [
        ("Ingest SharpHound data", "Import collection JSON into BloodHound CE/legacy for AD attack path analysis.", "bloodhound --collectionmethod All --domain {{domain|lab.local}}"),
        ("Run SharpHound from Windows lab", "Collects ACLs, sessions, and paths — run on domain-joined lab machine.", "SharpHound.exe -c All -d {{domain|lab.local}}"),
    ],
    "kerberoasting": [
        ("Request kerberoastable SPN tickets", "Uses Impacket to pull TGS hashes for accounts with SPNs — crack offline in lab AD.", "impacket-GetUserSPNs -request -dc-ip {{ip}} {{domain|lab.local}}/{{user|user}}:{{pass|pass}}"),
        ("Crack TGS hashes with hashcat", "Mode 13100 for Kerberos 5 TGS-REP — run after GetUserSPNs on lab domain.", "hashcat -m 13100 {{hashes|tgs.txt}} {{wordlist|/usr/share/wordlists/rockyou.txt}}"),
        ("Kerberoast with Rubeus on Windows", "On domain-joined lab host, export roastable hashes to file.", "Rubeus.exe kerberoast /outfile:{{output|hashes.txt}}"),
        ("Find SPN accounts via ldapsearch", "Lists users with servicePrincipalName set before roasting — lab DC only.", "ldapsearch -LLL -H ldap://{{ip}} -x -D '{{domain|lab.local}}\\{{user|user}}' -w {{pass|password}} '(&(samAccountType=805306368)(servicePrincipalName=*))' servicePrincipalName"),
    ],
    "slowloris": [
        ("Run Slowloris against owned lab web server", "Opens many partial HTTP connections to test server resilience — authorized lab infra only.", "slowloris -dns {{target|lab.local}} -port {{port|80}} -timeout {{timeout|240}} -s {{sockets|500}}"),
        ("Slow HTTP test with slowhttptest", "Alternative slowloris-style test using slowhttptest on infrastructure you control.", "slowhttptest -c {{connections|500}} -H -g -o {{output|slowloris}} -i {{interval|10}} -r {{rate|200}} -t GET -u {{target|http://192.168.1.10/}} -x {{timeout|24}}"),
    ],
    "nmap": [
        ("Quick SYN scan top ports", "Fast port discovery on lab target — first step in network mapping.", "nmap -sS -T4 --top-ports 1000 {{ip}}"),
        ("Service version detection", "Banner and version grab on open ports found in prior scan.", "nmap -sV -p {{ports|22,80,443,445}} {{ip}}"),
        ("Run default NSE scripts", "Safe default scripts on discovered services — good after -sV.", "nmap -sC -sV -p {{ports|80,443}} {{ip}}"),
    ],
    "curl": [
        ("Fetch URL with response headers", "Quick HTTP check — see status code, server header, and cookies.", "curl -i {{target|http://192.168.1.10/}}"),
        ("POST JSON to API endpoint", "Send lab API requests during web or cloud testing.", "curl -X POST {{target|http://192.168.1.10/api}} -H 'Content-Type: application/json' -d '{\"key\":\"value\"}'"),
        ("Download file to disk", "Stage tools or exfil test files on authorized lab hosts.", "curl -o {{output|file.bin}} {{target|http://192.168.1.10/file.bin}}"),
    ],
    "tcpdump": [
        ("Capture on interface", "Record packets on pivot interface during lab attack demo — filter to reduce noise.", "sudo tcpdump -i {{interface|eth0}} -w {{output|capture.pcap}}"),
        ("Capture only host traffic", "BPF filter limits capture to one lab target IP.", "sudo tcpdump -i {{interface|eth0}} host {{ip}} -w {{output|host.pcap}}"),
    ],
    "aircrack-ng": [
        ("Capture WPA handshake", "Monitor mode capture until handshake from lab AP — authorized test network only.", "sudo airodump-ng -c {{channel|6}} --bssid {{bssid|AA:BB:CC:DD:EE:FF}} -w {{output|capture}} {{interface|wlan0mon}}"),
        ("Crack WPA key from capture", "Dictionary attack on .cap file after handshake collected.", "aircrack-ng -w {{wordlist|/usr/share/wordlists/rockyou.txt}} -b {{bssid|AA:BB:CC:DD:EE:FF}} {{capture|capture-01.cap}}"),
    ],
}


def slugify(name: str) -> str:
    name = Path(name).stem
    name = re.sub(r"\.(py|rb|exe|md)$", "", name, flags=re.I)
    name = name.lower()
    name = re.sub(r"[^a-z0-9]+", "-", name)
    return name.strip("-")


def clean_md(text: str) -> str:
    text = re.sub(r"\[\[([^\]|]+)(?:\|[^\]]+)?\]\]", r"\1", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def parse_markdown(path: Path) -> tuple[str, list[str], list[str]]:
    text = path.read_text(encoding="utf-8", errors="replace")
    desc = ""
    for pat in (
        r"## 🔍 Description\s*\n+(.*?)(?=\n## |\Z)",
        r"## Description\s*\n+(.*?)(?=\n## |\Z)",
        r"## Overview\s*\n+(.*?)(?=\n## |\Z)",
        r"# [^\n]+\n+(.*?)(?=\n## |\Z)",
    ):
        m = re.search(pat, text, re.DOTALL | re.I)
        if m:
            desc = clean_md(m.group(1))[:400]
            break

    commands: list[str] = []
    for block in re.findall(r"```(?:bash|sh|shell|cmd|powershell|ps1|zsh)?\n(.*?)```", text, re.DOTALL | re.I):
        for line in block.splitlines():
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("//"):
                continue
            if line.lower().startswith(("usage:", "note:", "example:")):
                continue
            commands.append(line)

    for m in re.finditer(r"Usage:\s*`([^`]+)`", text, re.I):
        commands.append(m.group(1).strip())
    for m in re.finditer(r"`([a-zA-Z0-9/_.-]+(?:\s+[-a-zA-Z0-9=./_{{}}|]+)+)`", text):
        cmd = m.group(1).strip()
        if any(c in cmd for c in (" ", "/", "-")) and len(cmd) > 8:
            commands.append(cmd)

    refs = list(dict.fromkeys(re.findall(r"https?://[^\s\)\]>'\"]+", text)))[:3]
    return desc, dedupe_cmds(commands), refs


def dedupe_cmds(cmds: list[str]) -> list[str]:
    joined: list[str] = []
    buf = ""
    for raw in cmds:
        line = raw.strip()
        if not line:
            continue
        if buf:
            if buf.endswith("\\"):
                buf = buf[:-1].rstrip() + " " + line
            else:
                joined.append(buf)
                buf = line
        else:
            buf = line
        if buf and not buf.endswith("\\"):
            joined.append(buf)
            buf = ""
    if buf:
        joined.append(buf.rstrip("\\").strip())

    seen: set[str] = set()
    out: list[str] = []
    for c in joined:
        c = re.sub(r"\s+", " ", c.strip())
        if len(c) < 5:
            continue
        if re.match(r"^\d+\.\s", c) and not re.search(r"[;/\\]|ldap|http|sudo|curl|nmap", c, re.I):
            continue
        if c.startswith('"') and "samAccountType" in c:
            continue
        if re.match(r"^-\w", c) and " " not in c.rstrip("\\"):
            continue
        if c.endswith("\\"):
            c = c.rstrip("\\").strip()
        if c and c not in seen:
            seen.add(c)
            out.append(c)
    return out


def cmd_title(cmd: str, idx: int) -> str:
    cmd = cmd.split("|")[0].strip()
    parts = cmd.split()
    if not parts:
        return f"Run command {idx + 1}"
    verb = parts[0].split("/")[-1]
    verb = re.sub(r"^(sudo|./)", "", verb)
    rest = " ".join(parts[1:3]) if len(parts) > 1 else ""
    title = f"{verb} {rest}".strip()[:60]
    return title[0].upper() + title[1:] if title else f"Run step {idx + 1}"


def cmd_desc(cmd: str, strategy: str, tool: str) -> str:
    base = f"Runs `{cmd.split()[0] if cmd.split() else tool}` as part of the CEH workflow. {strategy[:180]}"
    if len(base) > 320:
        base = base[:317] + "..."
    if "lab" not in base.lower() and "authoriz" not in base.lower():
        base += " Authorized lab targets only."
    return base


def quote_yaml(s: str) -> str:
    if not s:
        return '""'
    if "\\" in s or '"' in s or "\n" in s:
        return "'" + s.replace("'", "''") + "'"
    return f'"{s}"'


def load_category_strategies() -> dict[str, str]:
    if not MANIFEST.is_file():
        return {}
    with MANIFEST.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    cats = data.get("categories") or {}
    mapping = {
        "05-post_exploitation_and_privilege_escalation": "post_exploitation_and_privilege_escalation",
        "06-defense_and_monitoring": "defense_and_monitoring",
        "07-cryptography_and_hashing": "cryptography_and_hashing",
        "08-malware_analysis_and_reverse_engineering": "malware_analysis_and_reverse_engineering",
        "09-social_engineering_and_phishing": "social_engineering_and_phishing",
        "10-cloud_iot_and_infrastructure": "cloud_iot_and_infrastructure",
        "11-system_and_network_tools": "system_and_network_tools",
        "12-wireless_and_network_attacks": "wireless_and_network_attacks",
        "13-authentication_and_access_control": "authentication_and_access_control",
        "14-mobile_and_endpoint_security": "mobile_and_endpoint_security",
    }
    return {folder: str((cats.get(key) or {}).get("strategy") or "").strip() for folder, key in mapping.items()}


def find_existing(slug: str) -> Path | None:
    matches = list(CHEATS.rglob(f"{slug}.yaml"))
    if not matches:
        return None
    return matches[0]


def load_yaml(path: Path) -> dict | None:
    try:
        with path.open(encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
            return data if isinstance(data, dict) else None
    except yaml.YAMLError:
        return None


def fallback_commands(slug: str, tool: str) -> list[str]:
    if slug in EXTRA:
        return [c[2] for c in EXTRA[slug]]
    low = slug.replace("-", "")
    if re.match(r"^[a-z0-9-]+$", slug) and len(slug) < 20:
        return [
            f"{slug} --help",
            f"man {slug.split('-')[0]}" if "-" not in slug else f"{slug} -h",
        ]
    return [
        f"echo 'Open {tool} per CEH lab procedure — configure target {{ip}} in isolated environment.'",
    ]


def build_actions(
    slug: str,
    tool: str,
    commands: list[str],
    strategy: str,
) -> list[dict[str, str]]:
    actions: list[dict[str, str]] = []
    extras = EXTRA.get(slug, [])
    for title, desc, cmd in extras:
        actions.append({"title": title, "desc": desc, "command": cmd})

    src_cmds = commands if commands else fallback_commands(slug, tool)
    for i, cmd in enumerate(src_cmds[:12]):
        actions.append(
            {
                "title": cmd_title(cmd, i),
                "desc": cmd_desc(cmd, strategy, tool),
                "command": cmd,
            }
        )

    # dedupe by command string
    seen: set[str] = set()
    uniq: list[dict[str, str]] = []
    seen_titles: set[str] = set()
    for a in actions:
        if a["command"] in seen:
            continue
        title = a["title"]
        n = 2
        while title in seen_titles:
            title = f"{a['title']} ({n})"
            n += 1
        seen_titles.add(title)
        seen.add(a["command"])
        uniq.append({**a, "title": title})
    return uniq[:10] if len(uniq) > 10 else uniq


def render_yaml(data: dict) -> str:
    return yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True, width=1200)


def merge_cheat(existing: dict, new_actions: list[dict], new_tags: list[str], new_hint: str) -> dict:
    old_tags = list(existing.get("tags") or [])
    for t in new_tags:
        if t not in old_tags:
            old_tags.append(t)
    old_actions = list(existing.get("actions") or [])
    existing_cmds = {a.get("command") for a in old_actions if isinstance(a, dict)}
    seen_titles = {str(a.get("title")) for a in old_actions if isinstance(a, dict)}
    for a in new_actions:
        if a["command"] in existing_cmds:
            continue
        title = a["title"]
        n = 2
        while title in seen_titles:
            title = f"{a['title']} ({n})"
            n += 1
        seen_titles.add(title)
        existing_cmds.add(a["command"])
        old_actions.append({**a, "title": title})
    hint = str(existing.get("exam_hint") or "")
    if new_hint and new_hint[:80] not in hint:
        hint = f"{hint} {new_hint}".strip() if hint else new_hint
    existing["tags"] = old_tags
    existing["actions"] = old_actions[:14]
    existing["exam_hint"] = hint[:500]
    return existing


def process_module(
    nb_name: str,
    out_dir: str,
    mod_tag: str,
    extra_tags: list[str],
    strategy: str,
    *,
    dry_run: bool = False,
) -> tuple[int, int]:
    src = NOTEBOOK / nb_name
    if not src.is_dir():
        print(f"Missing notebook module: {src}", file=sys.stderr)
        return 0, 0

    out_path = CHEATS / out_dir
    out_path.mkdir(parents=True, exist_ok=True)
    written = merged = 0

    for md in sorted(src.rglob("*.md")):
        tool_name = md.stem
        slug = slugify(tool_name)
        if not slug:
            continue

        desc, commands, refs = parse_markdown(md)
        tags = [mod_tag, *extra_tags]
        hint = desc or f"{tool_name} — CEH {nb_name.split()[0]} module tool."
        if strategy:
            hint = f"{hint} Strategy: {strategy[:220]}"

        actions = build_actions(slug, tool_name, commands, strategy)
        docs = refs or []

        payload = {
            "tool": slug,
            "tags": tags,
            "exam_hint": hint[:500],
            "docs": docs,
            "actions": actions,
        }

        existing_path = find_existing(slug)
        if existing_path and existing_path.parent != out_path:
            if not dry_run:
                old = load_yaml(existing_path)
                if old:
                    merged_data = merge_cheat(old, actions, tags, hint[:200])
                    merged_data["tool"] = merged_data.get("tool") or slug
                    existing_path.write_text(render_yaml(merged_data), encoding="utf-8")
            merged += 1
            continue

        target = out_path / f"{slug}.yaml"
        if existing_path:
            target = existing_path
        if not dry_run:
            old = load_yaml(existing_path) if existing_path else None
            if old:
                payload = merge_cheat(old, actions, tags, hint[:200])
                payload["tool"] = payload.get("tool") or slug
            else:
                payload = {
                    "tool": slug,
                    "tags": tags,
                    "exam_hint": hint[:500],
                    "docs": docs,
                    "actions": actions,
                }
            target.write_text(render_yaml(payload), encoding="utf-8")
        written += 1

    return written, merged


def update_manifest() -> tuple[int, int]:
    from loadout.loader import load_cheats
    from loadout.config import get_builtin_cheats_dir

    actions = load_cheats([get_builtin_cheats_dir()], warn=False)
    files = sum(1 for p in CHEATS.rglob("*.yaml") if p.name not in {"manifest.yaml", "_template.yaml"})

    with MANIFEST.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}

    ver = int(data.get("version") or 8)
    data["version"] = ver + 1
    data["updated"] = "2026-07-05"
    data["cheat_files"] = files
    data["action_count"] = len(actions)

    with MANIFEST.open("w", encoding="utf-8") as fh:
        yaml.dump(data, fh, default_flow_style=False, sort_keys=False, allow_unicode=True)

    return files, len(actions)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--modules", nargs="*", help="Module numbers e.g. 05 06 or all")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    strategies = load_category_strategies()
    selected = MODULES
    if args.modules and "all" not in args.modules:
        nums = {m.zfill(2) for m in args.modules}
        selected = [m for m in MODULES if m[0][:2] in nums]

    total_w = total_m = 0
    for nb_name, out_dir, mod_tag, extra_tags in selected:
        strat = strategies.get(out_dir, "")
        w, mg = process_module(nb_name, out_dir, mod_tag, extra_tags, strat, dry_run=args.dry_run)
        print(f"{nb_name}: wrote/updated {w}, merged-into-existing {mg}")
        total_w += w
        total_m += mg

    if not args.dry_run:
        files, actions = update_manifest()
        print(f"\nManifest updated: {files} files, {actions} actions")


if __name__ == "__main__":
    main()
