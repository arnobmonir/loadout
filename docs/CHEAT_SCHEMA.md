# Cheat file schema

Every built-in and user cheat is a YAML file. One file = one tool (binary or product name).

## Required structure

```yaml
tool: nmap
tags: [recon, scanning, m03]
exam_hint: "Network mapper — host/port/service/OS discovery"
docs:
  - https://nmap.org/book/man.html
  - "man:nmap"

actions:
  - title: host discovery
    desc: Ping sweep on subnet
    command: "nmap -sn {{ip}}/24"

  - title: SYN stealth scan
    command: "nmap -sS {{ip}}"
```

## Fields

| Field | Required | Type | Notes |
|-------|----------|------|-------|
| `tool` | Yes | string | CLI binary or canonical tool name |
| `tags` | No | string[] | Search/filter (`recon`, `web`, `m04`) |
| `exam_hint` | No | string | Shown in `--study` mode |
| `docs` | No | string[] | URLs or `man:toolname` |
| `actions` | Yes* | list | At least one for runnable tools |

\* Study-only entries may use `actions: []` if `exam_hint` is set.

### Action object

| Field | Required | Type |
|-------|----------|------|
| `title` | Yes | string — unique per file |
| `command` | Yes | string — supports placeholders |
| `desc` | No | string — detail panel in TUI |

## Placeholders

| Syntax | Meaning |
|--------|---------|
| `{{name}}` | Required; prompt if unset |
| `{{name\|default}}` | Optional; use default if unset |

Global variables from `set ip=10.10.10.5` or `loadout vars set` fill matching names.

## Common variables (convention)

`ip`, `domain`, `url`, `port`, `user`, `pass`, `hash`, `lhost`, `lport`, `wordlist`, `output`, `target`

`target` is an alias-friendly name; maps to `ip` or `domain` only if user sets it.

## File placement

```
cheats/
├── 01-recon/nmap.yaml
├── 02-scanning/masscan.yaml
├── 03-enumeration/enum4linux.yaml
└── conceptual/nessus.yaml      # exam_hint only
```

## Validation rules (`loadout cheats validate` — M8; enforced in tests — M11)

- `tool` must be non-empty
- `actions[].title` unique within file
- `actions[].command` non-empty when present
- Placeholders must match `{{word}}` or `{{word|default}}`
- No duplicate `tool` across builtin pack (user override by `tool` + `title` wins)
