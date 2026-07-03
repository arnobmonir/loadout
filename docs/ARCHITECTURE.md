# Loadout — Architecture

## High-level flow

```
cheats/**/*.yaml  ──┐
                    ├──► loader ──► index ──► tui ──► substitute ──► output
~/.config/...   ────┘         ▲
                              │
                         variables
                         (vars.json)
```

## Package layout (target)

```
loadout/
├── README.md
├── pyproject.toml
├── loadout/                    # Python package
│   ├── __init__.py
│   ├── __main__.py             # CLI entry (M8)
│   ├── config.py               # M1
│   ├── models.py               # M2
│   ├── loader.py               # M3
│   ├── substitute.py           # M4
│   ├── variables.py            # M5
│   ├── output.py               # M6
│   ├── index.py                # M9 (optional cache)
│   └── tui.py                  # M7
├── cheats/                     # M10 — built-in cheat pack
│   ├── manifest.yaml
│   └── <category>/*.yaml
├── tests/
└── docs/
```

## Module dependency graph

```
M1 config ─────────────────────────────┐
M2 models ◄── M3 loader ◄── M10 cheats │
         ◄── M4 substitute ◄── M5 vars  │
         ◄── M6 output                  │
M3 loader ──► M7 tui ──► M8 CLI        │
M3 loader ──► M9 index (optional)      │
M11 tests ── validates all modules     │
M12 packaging ── ships M1–M10        │
```

Build order: **M1 → M2 → M3 → M4 → M5 → M6 → M7 → M8**, then **M9**, **M10** in parallel with M7+, **M11** ongoing, **M12** at v0.1.

## Config locations

| Path | Owner | Purpose |
|------|-------|---------|
| `cheats/` (package) | Loadout | Built-in cheat pack |
| `~/.config/loadout/config.yaml` | User | Paths, output mode, defaults |
| `~/.config/loadout/vars.json` | User | Global variables (`ip`, `domain`, …) |
| `~/.config/loadout/cheats/` | User | Custom YAML cheats |
| `~/.cache/loadout/index.json` | Loadout | Optional search index cache |

## Design principles

1. **YAML is the extension API** — new tools = new files, no code changes.
2. **Modules are independently testable** — no circular imports.
3. **TUI loops** — selecting a command returns to the menu; exit only on `q` / `Esc`.
4. **Clipboard first** — avoid TIOCSTI until explicitly requested (M6 phase 2).
5. **One `tool` per file** — dedupe by filename / `tool` field; tags carry CEH module context.
