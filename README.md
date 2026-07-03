# Loadout

**Persistent pentest command launcher** — search built-in cheat sheets, set variables once, copy or run commands from a menu that stays open.

## Status

Pre-development. See the modular plan before writing feature code.

## Documentation

| Doc | Purpose |
|-----|---------|
| [docs/Index.md](docs/Index.md) | Documentation hub |
| [docs/DEVELOPMENT_PLAN.md](docs/DEVELOPMENT_PLAN.md) | **Master plan** — modules M1–M12, phases, acceptance criteria |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Package layout and module boundaries |
| [docs/CHEAT_SCHEMA.md](docs/CHEAT_SCHEMA.md) | YAML cheat file contract |

## Quick goals

- **pip install:** `loadout-cli` → `loadout` command
- **Built-in cheats:** grow from 1 → 30 → 200+ CLI templates
- **User cheats:** `~/.config/loadout/cheats/*.yaml`
- **UX:** persistent TUI (does not exit after each command)

## License

TBD (recommend MIT or GPL-3.0 to align with pentest tooling ecosystem).
