# Loadout — Modular Development Plan

**Project:** Loadout (`loadout-cli` on PyPI)  
**Location:** `/home/arnob/CEH/loadout`  
**Last updated:** 2026-07-03  

---

## 1. Vision

Build a **standalone**, **installable** command launcher for security practitioners and CEH learners:

- Search fuzzy across tool names, tags, and commands
- Set global variables once (`ip`, `domain`, `wordlist`, …)
- Select a command → **menu stays open** (unlike arsenal-ng)
- Ship a growing **built-in cheat pack** (target 200–300 runnable CLI templates)
- Let users add **`~/.config/loadout/cheats/*.yaml`** without forking the project

**Non-goals for v1:** Obsidian integration, auto-running destructive commands without confirmation, GUI.

---

## 2. Success criteria

| Milestone | Done when |
|-----------|-----------|
| **v0.1** | `pip install -e .` works; TUI loops; 1 built-in cheat (`nmap`); clipboard output |
| **v0.2** | 30 built-in cheats; `set` / `variables` in TUI; user cheat path |
| **v0.5** | 100 cheats; `loadout cheats validate`; tags filter |
| **v1.0** | 200+ cheats; PyPI publish; `doctor`, `--study`, index cache |
| **v2.0** | Optional Go binary; same YAML pack embedded |

---

## 3. Module map

Each module is a **vertical slice of code** with clear inputs, outputs, and tests. Complete in order unless noted.

| ID | Module | Package path | Depends on | Est. |
|----|--------|--------------|------------|------|
| **M1** | Config | `loadout/config.py` | — | 0.5 d |
| **M2** | Models | `loadout/models.py` | — | 0.5 d |
| **M3** | Loader | `loadout/loader.py` | M1, M2 | 1 d |
| **M4** | Substitute | `loadout/substitute.py` | M2 | 0.5 d |
| **M5** | Variables | `loadout/variables.py` | M1, M2 | 0.5 d |
| **M6** | Output | `loadout/output.py` | M1 | 0.5 d |
| **M7** | TUI | `loadout/tui.py` | M3–M6 | 2 d |
| **M8** | CLI | `loadout/__main__.py` | M7 | 1 d |
| **M9** | Index cache | `loadout/index.py` | M3 | 1 d |
| **M10** | Cheat pack | `cheats/**` | M3 schema | ongoing |
| **M11** | Tests | `tests/` | all | ongoing |
| **M12** | Packaging | `pyproject.toml` | M1–M8 | 0.5 d |

**Parallel work:** M10 (YAML authoring) can start after M3 schema is frozen. M9 can slip to v0.5.

---

## 4. Module specifications

### M1 — Config

**Purpose:** Resolve paths and defaults for builtin cheats, user config, vars, cache.

**Deliverables:**
- `loadout/config.py` with `LoadoutConfig` dataclass
- Default paths: `~/.config/loadout/`, `~/.cache/loadout/`
- Load `config.yaml` if present; sensible defaults

**Config keys:**
```yaml
output_mode: clipboard    # clipboard | print
cheat_paths:
  - ~/.config/loadout/cheats/
default_vars:
  wordlist: /usr/share/wordlists/dirb/common.txt
```

**Acceptance:**
- [ ] `get_builtin_cheats_dir()` resolves when installed editable and as wheel
- [ ] Creates config dir on first run (optional helper)

---

### M2 — Models

**Purpose:** Shared dataclasses / types.

**Deliverables:**
- `Action`, `CheatFile`, `LoadoutIndex` (tool → actions)
- `OutputMode` enum

**Acceptance:**
- [ ] Immutable or clear mutation rules documented
- [ ] `Action` carries `source_file`, `tool`, `tags` for UI and debugging

---

### M3 — Loader

**Purpose:** Discover and parse all YAML cheats (builtin + user).

**Deliverables:**
- `load_cheats(paths) -> list[Action]` (flattened)
- `load_cheat_file(path) -> CheatFile`
- Merge: user cheats override same `tool` + `title`
- Skip invalid files with warning to stderr

**Acceptance:**
- [ ] Loads `cheats/recon/nmap.yaml` from package
- [ ] Loads `~/.config/loadout/cheats/*.yaml`
- [ ] Empty `actions` + `exam_hint` allowed (study-only)
- [ ] Raises clear error on malformed YAML (file path in message)

**Reference:** [CHEAT_SCHEMA.md](CHEAT_SCHEMA.md)

---

### M4 — Substitute

**Purpose:** Replace `{{var}}` and `{{var|default}}` in command strings.

**Deliverables:**
- `parse_placeholders(command) -> list[Placeholder]`
- `substitute(command, vars) -> SubstituteResult` with `missing: list[str]`

**Acceptance:**
- [ ] Unit tests for required, default, and mixed placeholders
- [ ] Unknown placeholder without default → listed in `missing`
- [ ] No shell injection in substitute logic (values inserted as-is; user responsibility)

---

### M5 — Variables

**Purpose:** Persist and manage global session variables.

**Deliverables:**
- `get`, `set`, `unset`, `list_all`
- Persist to `~/.config/loadout/vars.json`
- TUI specials: `set ip=10.10.10.5`, `unset ip`, `variables`

**Acceptance:**
- [ ] Survives process restart
- [ ] `config.default_vars` merged as fallbacks (not overwriting user vars)

---

### M6 — Output

**Purpose:** Deliver final command to user environment.

**Phase 1 (v0.1):**
- `clipboard` — pyperclip
- `print` — stdout only

**Phase 2 (v0.5+):**
- `tmux` — send-keys to other pane
- `prefill` — TIOCSTI (opt-in, documented)

**Acceptance:**
- [ ] `loadout doctor` reports clipboard availability
- [ ] Graceful fallback to `print` if clipboard fails

---

### M7 — TUI (core differentiator)

**Purpose:** Persistent interactive menu.

**Library:** Textual (preferred) or prompt-toolkit + rich.

**Behavior:**
1. Fuzzy search (rapidfuzz) over tool, title, tags, command, desc
2. Enter → if missing placeholders → mini-form → substitute → output
3. Toast: `Copied: nmap -sS 10.10.10.5`
4. **Return to search** — do not exit
5. `q` / `Esc` → quit

**Special commands in search input:**
| Input | Action |
|-------|--------|
| `set key=value` | M5 |
| `unset key` | M5 |
| `variables` | list vars panel |
| `tools` | grouped tool table |
| `help` | shortcuts |
| `reload` | re-run M3 loader |

**Acceptance:**
- [ ] 10 consecutive command picks without relaunching `loadout`
- [ ] Filter by tag via search or flag passthrough
- [ ] Study mode hides `command`, shows `exam_hint` only

---

### M8 — CLI

**Purpose:** Non-interactive and subcommands.

```bash
loadout                      # TUI default
loadout --version
loadout --tag recon
loadout --tool nmap
loadout --study

loadout vars set ip=10.10.10.5
loadout vars list
loadout vars unset ip

loadout cheats list [--source builtin|user|all]
loadout cheats validate [path]
loadout cheats add <file.yaml>

loadout doctor
loadout reload                 # bust cache if M9 enabled
```

**Acceptance:**
- [ ] `loadout --help` documents all subcommands
- [ ] Exit codes: 0 success, 1 user error, 2 internal error

---

### M9 — Index cache (v0.5+)

**Purpose:** Fast startup with 200+ cheat files.

**Deliverables:**
- Build `~/.cache/loadout/index.json` from cheat mtime + manifest version
- Index stores: tool, title, tags, file path, offset — not full commands if lazy-load desired

**Acceptance:**
- [ ] Cold start &lt; 200ms with 300 files (target)
- [ ] Invalidates when builtin version or user file mtime changes

---

### M10 — Cheat pack (content module)

**Purpose:** Built-in YAML library shipped with package.

**Structure:**
```
cheats/
├── manifest.yaml
├── 01-recon/
├── 02-scanning/
├── 03-enumeration/
├── 04-vuln/
├── 05-exploit/
├── 06-post/
├── 07-defense/
├── 08-malware/
├── 09-social/
├── 10-cloud/
├── 11-network/
├── 12-wireless/
├── 13-auth/
├── 14-mobile/
├── 15-crypto/
└── conceptual/          # exam_hint only, no commands
```

**Growth tiers:**

| Tier | Count | Content | Target version |
|------|-------|---------|----------------|
| T0 | 1 | `nmap.yaml` | v0.1 |
| T1 | 30 | CEH high-yield CLI | v0.2 |
| T2 | 100 | Common Kali tools | v0.5 |
| T3 | 200+ | Full CLI coverage | v1.0 |
| T4 | +conceptual | Exam awareness entries | v1.x |

**Rules:**
- One YAML per `tool` name
- Multiple `actions` per file (not one file per action)
- Runnable vs study-only clearly separated

**manifest.yaml:**
```yaml
version: 1
cheat_files: 30
action_count: 120
categories:
  recon: 8
```

**Acceptance:**
- [ ] `loadout cheats validate --all` passes in CI
- [ ] Each new file reviewed: authorized-lab wording in desc where needed

---

### M11 — Tests

**Purpose:** Regression safety as cheats grow.

**Layout:**
```
tests/
├── test_substitute.py
├── test_loader.py
├── test_variables.py
├── test_config.py
└── fixtures/cheats/
    └── sample_nmap.yaml
```

**Acceptance:**
- [ ] pytest in CI on push
- [ ] Coverage on M3, M4, M5 minimum 80%

---

### M12 — Packaging

**Purpose:** `pip install loadout-cli` and editable dev install.

**Deliverables:**
- `pyproject.toml` with `[project.scripts] loadout = loadout.__main__:main`
- Package data: `cheats/**/*.yaml`
- `pipx` install documented in README

**Acceptance:**
- [ ] `pip install -e .` from repo root
- [ ] `loadout` on PATH after install
- [ ] Wheel includes all builtin cheats

---

## 5. Development phases

### Phase 0 — Planning (current)

- [x] Name: Loadout
- [x] Architecture doc
- [x] Cheat schema doc
- [x] Modular development plan
- [ ] License choice (MIT recommended)
- [ ] Git init + `.gitignore`

### Phase 1 — Framework skeleton (v0.1)

**Goal:** Prove the loop with one cheat.

| Step | Module | Task |
|------|--------|------|
| 1.1 | M12 | `pyproject.toml`, package dirs, `.gitignore` |
| 1.2 | M1, M2 | config + models |
| 1.3 | M3, M4, M5, M6 | loader, substitute, vars, output |
| 1.4 | M10 T0 | `cheats/01-recon/nmap.yaml` |
| 1.5 | M7 | minimal persistent TUI |
| 1.6 | M8 | `loadout` entry + `--version` |
| 1.7 | M11 | tests for substitute + loader |

**Exit demo:**
```bash
pip install -e .
loadout
# set ip=192.168.1.10
# pick nmap SYN scan → clipboard → menu still open
```

### Phase 2 — Usable daily driver (v0.2)

| Step | Module | Task |
|------|--------|------|
| 2.1 | M7 | special commands (`set`, `variables`, `tools`, `help`) |
| 2.2 | M1 | user `cheat_paths` in config |
| 2.3 | M10 T1 | 30 CEH high-yield YAML files |
| 2.4 | M8 | `cheats list`, `vars` subcommands |
| 2.5 | M8 | `doctor` |

### Phase 3 — Scale content (v0.5)

| Step | Module | Task |
|------|--------|------|
| 3.1 | M10 T2 | 100 cheat files |
| 3.2 | M8 | `cheats validate`, `cheats add` |
| 3.3 | M7 | `--tag` filter |
| 3.4 | M9 | index cache |
| 3.5 | M6 | optional `tmux` output mode |

### Phase 4 — Release (v1.0)

| Step | Module | Task |
|------|--------|------|
| 4.1 | M10 T3 | 200+ runnable cheats |
| 4.2 | M7 | `--study` mode |
| 4.3 | M12 | PyPI publish `loadout-cli` |
| 4.4 | — | README, screenshots, contributing guide |

### Phase 5 — Optional (v2.0)

- Go port (`cmd/loadout`) embedding same `cheats/` via `embed.FS`
- GitHub Actions release binaries (linux amd64/arm64)
- Community cheat PR template

---

## 6. Cheat authoring workflow (M10)

For each new tool:

1. Copy `cheats/_template.yaml` → `cheats/<category>/<tool>.yaml`
2. Fill `tool`, `tags`, `actions` per [CHEAT_SCHEMA.md](CHEAT_SCHEMA.md)
3. Run `loadout cheats validate cheats/<category>/<tool>.yaml`
4. Run `loadout` and smoke-test search + copy
5. PR with one tool per commit (easy review)

**Template file** (create in Phase 1):

```yaml
tool: TOOL_NAME
tags: []
exam_hint: ""
docs: []

actions:
  - title: short label
    desc: Authorized lab only.
    command: "TOOL_NAME {{ip}}"
```

---

## 7. Risk register

| Risk | Mitigation |
|------|------------|
| 800 tools ≠ 800 CLI cheats | Tier T0–T4; study-only entries without commands |
| TIOCSTI broken on Linux 6.2+ | Clipboard default; prefill opt-in |
| Duplicate tool names in pack | `cheats validate` checks duplicates |
| Large repo / slow TUI | M9 index cache; lazy load |
| Legal / misuse | Descriptions note authorized use; no auto-exploit without user Enter |
| PyPI name taken | Register `loadout-cli` early |

---

## 8. Next actions (immediate)

1. `git init` in `/home/arnob/CEH/loadout`
2. Add `.gitignore` (Python, cache, venv)
3. **Phase 1.1–1.2:** `pyproject.toml` + empty `loadout/` package + M1/M2
4. Do **not** bulk-import 800 YAML files until Phase 1 exit demo passes

---

## 9. Related docs

- [ARCHITECTURE.md](ARCHITECTURE.md) — dependency graph and paths
- [CHEAT_SCHEMA.md](CHEAT_SCHEMA.md) — YAML contract
- [../README.md](../README.md) — project overview

---

## 10. Progress tracker

| Module | Status | Version |
|--------|--------|---------|
| M1 Config | Not started | — |
| M2 Models | Not started | — |
| M3 Loader | Not started | — |
| M4 Substitute | Not started | — |
| M5 Variables | Not started | — |
| M6 Output | Not started | — |
| M7 TUI | Not started | — |
| M8 CLI | Not started | — |
| M9 Index | Deferred | v0.5 |
| M10 Cheats | Not started | T0 in v0.1 |
| M11 Tests | Not started | — |
| M12 Packaging | Not started | v0.1 |

_Update this table as modules land._
