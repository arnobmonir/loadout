# Loadout

**Persistent pentest command launcher** — search built-in cheat sheets, set variables once, copy commands from a menu that stays open.

## Status

**v0.3.1** — arsenal-ng inspired UI: syntax highlighting, colored tags, info box, command hints.

## Install

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Or with pipx (after PyPI publish):

```bash
pipx install loadout-cli
```

## Quick start

```bash
loadout
# In the TUI:
#   set ip=192.168.1.10
#   search "nmap" → Enter → command copied to clipboard
#   menu stays open for the next command
```

## CLI

```bash
loadout --version
loadout doctor
loadout vars set ip=10.10.10.5
loadout vars list
loadout cheats list
loadout cheats validate --all
loadout cheats list --source builtin
```

## Documentation

| Doc | Purpose |
|-----|---------|
| [docs/Index.md](docs/Index.md) | Documentation hub |
| [docs/DEVELOPMENT_PLAN.md](docs/DEVELOPMENT_PLAN.md) | Master plan — modules M1–M12 |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Package layout |
| [docs/CHEAT_SCHEMA.md](docs/CHEAT_SCHEMA.md) | YAML cheat contract |

## License

MIT — see [LICENSE](LICENSE).
