# Loadout

**CEH v13 pentest command launcher** — browse 787 tools and 2,976 ready-to-run commands from a persistent terminal UI. Set variables once, search or drill down by category, copy commands to your clipboard, and keep working without restarting the menu.

Built from the CEH v13 notebook tool list covering reconnaissance through mobile security, with plain-language descriptions and per-phase strategy hints.

## Cheat pack at a glance

| | |
|---|---|
| **Pack version** | v12 |
| **Tools** | 787 |
| **Commands** | 2,976 |
| **Categories** | 15 (CEH exam phases) |

| Category | Tools | Strategy (when to use) |
|---|---|---|
| Reconnaissance | 68 | Passive OSINT first; validate with DNS/WHOIS before active probes |
| Scanning & enumeration | 63 | Host sweep → service version → protocol-specific enum (445→SMB, 80→HTTP) |
| Vulnerability assessment | 51 | Map versions to CVEs; confirm with searchsploit before exploiting |
| Exploitation | 53 | Tie exploits to confirmed findings; set LHOST/LPORT/RHOST explicitly |
| Post-exploitation & privesc | 35 | Stable shell → local/domain enum → cred dump → lateral movement |
| Defense & monitoring | 10 | Baseline traffic; honeypots on decoy VLANs; correlate IDS with PCAP |
| Cryptography & hashing | 95 | Identify hash mode; targeted wordlists; crack service accounts first |
| Malware analysis & RE | 62 | Static first; dynamic only in isolated VMs with snapshots |
| Social engineering | 30 | Scope recipients; isolated infra; track opens/clicks within authorization |
| Cloud, IoT & infrastructure | 13 | Public bucket/IAM enum; container CVE scan; segment IoT VLANs |
| System & network tools | 248 | nc/socat relays; curl/wget staging; tcpdump/tshark with BPF filters |
| Wireless & network attacks | 31 | Monitor mode + channel lock; spoofing on test VLANs only |
| Authentication & access control | 8 | BloodHound paths first; AS-REP/kerberoast; respect lockout thresholds |
| Mobile & endpoint security | 18 | Static APK/IPA before dynamic; emulators without prod accounts |
| Compliance & reporting | 2 | Map findings to framework controls; retain logs and authorization docs |

## Install

**Requirements:** Python 3.11+

```bash
git clone https://github.com/arnobmonir/loadout.git
cd loadout
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e .
```

Optional dev dependencies (tests, lint):

```bash
pip install -e ".[dev]"
```

## Quick start

```bash
loadout
```

1. Set lab variables once: `set ip=192.168.1.10` and `set wordlist=/usr/share/wordlists/rockyou.txt`
2. **Search** — type a tool or keyword (e.g. `nmap`, `tool:hydra`, `tag:m04`)
3. **Browse** — `Ctrl+T` → category → tool → command
4. **Enter** on a command — copies the filled command to your clipboard
5. **Esc** — go back (selection is preserved at each level)

### TUI keys

| Key | Action |
|---|---|
| `/` or start typing | Focus search |
| `Enter` | Select / run command in subterminal |
| `c` | Copy or print selected command |
| `r` | Run selected command in subterminal |
| `Ctrl+T` | Browse by category |
| `Esc` | Back one level |
| `v` | Variable editor |
| `Ctrl+R` | Reload cheat pack |
| `?` | Help overlay |
| `q` | Quit |

### Output modes

Configure in `~/.config/loadout/config.yaml`:

- **copy** (default) — command goes to clipboard
- **print** — print to terminal (useful in Cursor/SSH without a clipboard)
- **subterminal** — run in tmux split or external terminal (requires tmux or a desktop terminal emulator)

Run `loadout doctor` to see which output backends are available on your system.

## CLI reference

```bash
loadout --version
loadout doctor
loadout vars set ip=10.10.10.5
loadout vars set domain=lab.local
loadout vars list
loadout cheats list
loadout cheats list --source builtin
loadout cheats validate --all
loadout cheats add mytool          # scaffold ~/.local/share/loadout/cheats/
loadout --study                    # exam hints without copying commands
loadout --tag m04                  # filter by CEH module tag
loadout --tool nmap
```

## Variables

Commands use `{{placeholders}}` filled from your saved variables:

```yaml
command: "nmap -sV -p 22,80,443 {{ip}}"
command: "hydra -l {{user|admin}} -P {{wordlist}} ssh://{{ip}}"
```

- `{{ip}}` — required; prompts if unset
- `{{user|admin}}` — optional default if unset

Variables persist in `~/.config/loadout/vars.yaml`.

## Adding your own cheats

User cheats live in `~/.local/share/loadout/cheats/<category>/<tool>.yaml` and merge with the built-in pack.

```bash
loadout cheats add mytool
```

Minimal file shape:

```yaml
tool: mytool
tags: [custom, m04]
exam_hint: "One-line reminder of what this tool does and when to use it."
docs:
  - https://example.com/docs
  - "man:mytool"

actions:
  - title: Scan the lab target
    desc: What this command does and when to use it. Authorized lab only.
    command: "mytool --target {{ip}}"
```

Rules: one tool name per file; unique action titles; every action needs a `desc` and `command`.

Validate after editing:

```bash
loadout cheats validate ~/.local/share/loadout/cheats/
```

## Project layout

```
loadout/
├── loadout/           # Python package (TUI, loader, config)
│   └── cheats.pack    # Built-in CEH cheat pack (compiled; not plain YAML)
├── tests/
├── scripts/           # Generators and build_cheat_pack.py
├── pyproject.toml
└── README.md
```

Built-in cheats ship as a single **AES-256-GCM encrypted** `cheats.pack` file. The cheat library is only readable through Loadout (TUI/CLI), not as plain YAML on disk or in the repository.

### Rebuilding the cheat pack (maintainers)

YAML sources live locally under `loadout/cheats/` (not committed). After editing sources:

```bash
python scripts/build_cheat_pack.py
pytest
```

## Development

```bash
pip install -e ".[dev]"
pytest
ruff check loadout tests
```

## License

MIT — see [LICENSE](LICENSE).
