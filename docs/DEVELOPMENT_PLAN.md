# Loadout — Modular Development Plan

**Project:** Loadout (`loadout-cli` on PyPI)  
**Location:** `/home/arnob/CEH/loadout`  
**Last updated:** 2026-07-03 (v0.3.1 — Phase 2.5 nearly complete)

---

## 1. Vision

Build a **standalone**, **installable** command launcher for security practitioners and CEH learners:

- Search fuzzy across tool names, tags, and commands
- Set global variables once (`ip`, `domain`, `wordlist`, …)
- Select a command → **menu stays open** (unlike arsenal-ng)
- Ship a growing **built-in cheat pack** (target 200–300 runnable CLI templates)
- Let users add **`~/.config/loadout/cheats/*.yaml`** without forking the project

**Non-goals for v1:** Obsidian integration, GUI, TIOCSTI prefill. Run launches in a subterminal without a confirm modal; **Copy** still confirms destructive commands.

**Reference competitor:** arsenal-ng — Loadout differentiates by persistent menu, global vars, and a curated CEH-oriented pack.

---

## 2. Success criteria

| Milestone | Done when |
|-----------|-----------|
| **v0.1** | `pip install -e .` works; TUI loops; 1 built-in cheat (`nmap`); clipboard output |
| **v0.2** | 30 built-in cheats; `set` / `variables` in TUI; user cheat path |
| **v0.5** | 100 cheats; `loadout cheats validate`; tags filter |
| **v1.0** | 200+ cheats; PyPI publish; `doctor`, `--study`, index cache |
| **v2.0** | Optional Go binary; same YAML pack embedded |

**Versioning:** [SemVer](https://semver.org/) on PyPI package `loadout-cli`. Cheat pack bumps tracked in `cheats/manifest.yaml` (`version` field) and invalidated by M9 cache.

---

## 2.1 Toolchain & prerequisites

| Item | Choice | Notes |
|------|--------|-------|
| Python | **3.11+** | `pyproject.toml` `requires-python` |
| TUI | **Textual** | Persistent screen + built-in input; no prompt-toolkit fork |
| CLI parsing | **typer** or **argparse** | Pick at M8; typer if subcommands grow past v0.2 |
| Fuzzy search | **rapidfuzz** | `token_set_ratio` over concatenated fields |
| YAML | **PyYAML** | Safe load only (`yaml.safe_load`) |
| Clipboard | **pyperclip** | Graceful degrade to `print` |
| Test runner | **pytest** | + `pytest-cov` for M11 gate |
| Lint (optional v0.2+) | **ruff** | Format + import sort in CI |

**Dev install (target):**
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

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

**Phase 1.5 (v0.3 — done):**
- `launch_command()` — open tmux pane or terminal emulator window (gnome-terminal, konsole, kitty, …)
- `doctor` checks: python, clipboard, subterminal backend, builtin cheats path
- Status-bar feedback only (no toast popups)

**Phase 2 (v0.5+):**
- `tmux` — send-keys to other pane (distinct from subterminal launch)
- `prefill` — TIOCSTI (opt-in, documented)

**`loadout doctor` checks:**
- Python version ≥ 3.11
- Clipboard backend available (or warn + install hint: `xclip` / `wl-clipboard`)
- Subterminal backend (tmux pane or terminal emulator)
- Builtin cheats dir resolvable

**Acceptance:**
- [x] `loadout doctor` reports checks above with pass/warn/fail
- [x] Graceful fallback to `print` if clipboard fails
- [x] `launch_command` opens subterminal without blocking TUI

---

### M7 — TUI (core differentiator)

**Purpose:** Persistent interactive menu.

**Library:** Textual (locked — see §2.1).

**Behavior:**
1. Fuzzy search (rapidfuzz) over tool, title, tags, command, desc
2. **Browse:** category → tool → command (15 CEH phases, empty categories visible)
3. **Enter** on a command → resolve `{{vars}}` → **run in subterminal**; **Copy** chip → clipboard/print (destructive confirm on copy only)
4. Command **descriptions** shown in list rows and detail panel (all 95 actions have `desc`)
5. Detail panel: command preview + compact **Copy** / **Run** chips beside command
6. Feedback via **status bar** only (no toasts)
7. **Return to menu** — do not exit after run/copy
8. `q` / `Esc` → quit or back

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
- [x] 10 consecutive command picks without relaunching `loadout`
- [x] Filter by tag via search or `--tag` / `tag:` prefix
- [x] Study mode hides `command`, shows `exam_hint` only (`--study`)
- [x] Enter runs command in subterminal; Copy chip for clipboard/print

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
- Index stores: tool, title, tags, file path, action index — full commands loaded on selection (lazy per-file parse)
- Cache key: hash of `(manifest.version, builtin cheat mtimes, user cheat mtimes, config.cheat_paths)`

**Acceptance:**
- [ ] Cold start &lt; 200ms with 300 files (target; measure on dev machine, document in README)
- [ ] Invalidates when manifest version or any watched file mtime changes

---

### M10 — Cheat pack (content module)

**Purpose:** Built-in YAML library shipped with package.

**Structure (CEH v13 — 15 phases):**
```
loadout/cheats/
├── manifest.yaml          # version, counts, category descriptions
├── 01-reconnaissance/
├── 02-scanning_and_enumeration/
├── 03-vulnerability_assessment/
├── 04-exploitation/
├── 05-post_exploitation_and_privilege_escalation/
├── 06-defense_and_monitoring/
├── 07-cryptography_and_hashing/
├── 08-malware_analysis_and_reverse_engineering/
├── 09-social_engineering_and_phishing/
├── 10-cloud_iot_and_infrastructure/
├── 11-system_and_network_tools/
├── 12-wireless_and_network_attacks/
├── 13-authentication_and_access_control/
├── 14-mobile_and_endpoint_security/
├── 15-compliance_and_reporting/
└── conceptual/            # exam_hint only, no commands (T4)
```

**Current pack (manifest v4):** 47 cheat files · 129 actions · 15 categories populated

**Growth tiers:**

| Tier | Count | Content | Target version |
|------|-------|---------|----------------|
| T0 | 1 | `nmap.yaml` | v0.1 |
| T1 | 30 | CEH high-yield CLI | v0.2 |
| T2 | 100 | Common Kali tools | v0.5 |
| T3 | 200+ | Full CLI coverage | v1.0 |
| T4 | +conceptual | Exam awareness entries | v1.x |

**Rules:**
- One YAML per `tool` name (filename should match `tool` field)
- Multiple `actions` per file (not one file per action)
- Runnable vs study-only clearly separated
- User cheats: later paths in `cheat_paths` override earlier; user dir always wins over builtin

**T1 seed list (v0.2 — 30 tools):**  
`nmap`, `masscan`, `rustscan`, `gobuster`, `ffuf`, `nikto`, `sqlmap`, `hydra`, `john`, `hashcat`, `enum4linux`, `smbclient`, `rpcclient`, `ldapsearch`, `dig`, `host`, `whois`, `theHarvester`, `subfinder`, `amass`, `wpscan`, `searchsploit`, `msfconsole`, `nc`, `socat`, `curl`, `wget`, `tcpdump`, `wireshark` (cli/tshark), `responder`  
_Author 29 new files + expand `nmap`; conceptual entries count toward T4, not T1._

**manifest.yaml:**
```yaml
version: 3
cheat_files: 30
action_count: 95
categories:
  reconnaissance:
    description: "DNS/WHOIS, subdomain enum, OSINT …"
    strategy: "Passive sources first …"
```

Category metadata is loaded by `loadout/categories.py` and shown in the TUI browse detail panel. All 15 CEH phases appear in browse even when empty.

**Acceptance:**
- [x] Every action has a non-empty `desc` (enforced in tests)
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

**CI (GitHub Actions — add in Phase 1.7):**
```yaml
# .github/workflows/ci.yml — on push/PR to main
# - setup-python 3.11, 3.12 matrix
# - pip install -e ".[dev]"
# - ruff check (when added)
# - pytest --cov=loadout --cov-fail-under=80 -k "not slow"
```

**Acceptance:**
- [ ] pytest in CI on push
- [ ] Coverage on M3, M4, M5 minimum 80%
- [ ] Fixture cheats in `tests/fixtures/cheats/` cover valid, invalid, and study-only YAML

---

### M12 — Packaging

**Purpose:** `pip install loadout-cli` and editable dev install.

**Deliverables:**
- `pyproject.toml` with `requires-python = ">=3.11"`
- `[project.scripts] loadout = loadout.__main__:main`
- `[project.optional-dependencies] dev = ["pytest", "pytest-cov", ...]`
- Package data: `cheats/**/*.yaml` via `[tool.setuptools.package-data]`
- `pipx` install documented in README

**Acceptance:**
- [ ] `pip install -e .` from repo root
- [ ] `loadout` on PATH after install
- [ ] Wheel includes all builtin cheats (verify with `unzip -l dist/*.whl`)

---

## 5. Development phases

### Phase 0 — Planning

- [x] Name: Loadout
- [x] Architecture doc
- [x] Cheat schema doc
- [x] Modular development plan
- [x] `.gitignore`
- [x] Cheat scaffold (`cheats/_template.yaml`, `cheats/manifest.yaml`)
- [x] License (MIT) — `LICENSE` file
- [x] `git init` (first commit: docs scaffold)
- [ ] Full codebase commit + push to remote
- [ ] Resolve PyPI name `loadout-cli` (search/register before v1.0)

### Phase 1 — Framework skeleton (v0.1) — **done**

**Goal:** Prove the loop with one cheat.

| Step | Module | Task | Status |
|------|--------|------|--------|
| 1.1 | M12 | `pyproject.toml`, `loadout/` package dirs | Done |
| 1.2 | M1, M2 | config + models | Done |
| 1.3 | M3, M4, M5, M6 | loader, substitute, vars, output | Done |
| 1.4 | M10 T0 | `cheats/01-recon/nmap.yaml` | Done |
| 1.5 | M7 | minimal persistent TUI | Done |
| 1.6 | M8 | `loadout` entry + `--version` | Done |
| 1.7 | M11 | tests for substitute + loader; `.github/workflows/ci.yml` | Done |

### Phase 2 — Usable daily driver (v0.2) — **done**

| Step | Module | Task | Status |
|------|--------|------|--------|
| 2.1 | M7 | special commands (`set`, `variables`, `tools`, `help`) | Done |
| 2.2 | M1 | user `cheat_paths` in config | Done |
| 2.3 | M10 T1 | 30 CEH high-yield YAML files | Done |
| 2.4 | M8 | `cheats list`, `vars` subcommands | Done |
| 2.5 | M8 | `doctor` | Done |

### Phase 2.5 — UX & core features — **nearly done**

**Goal:** Polish UI and utilities before scaling cheat content to 100+.

| Step | Module | Task | Status |
|------|--------|------|--------|
| 2.5.1 | M7 | Split-pane TUI, detail preview, keybindings, status bar feedback | Done |
| 2.5.2 | M7 | Hierarchical browse; `tag:` / `tool:` filters; command desc in list | Done |
| 2.5.3 | M7/M10 | Category descriptions (manifest v3); pack stats bar | Done |
| 2.5.4 | M1/M8 | Config save; `output clipboard\|print`; `loadout config` | Done |
| 2.5.5 | M8 | `loadout cheats add <tool>` scaffold user cheats | Done |
| 2.5.6 | M6/M7 | Subterminal run (`launch_command`); Enter = run; Copy chip | Done |
| 2.5.7 | M7 | Study mode polish | Done |
| 2.5.8 | M6 | Optional `tmux` send-keys output mode | Not started |
| 2.5.9 | M9 | Index cache (when UX is stable) | Deferred |
| 2.5.10 | M10 | Seed empty CEH categories (17 new tools) | Done |

### Phase 3 — Scale content (v0.5) — **next**

| Step | Module | Task |
|------|--------|------|
| 3.1 | M10 T2 | 100 cheat files |
| 3.2 | M8 | `cheats validate`, `cheats add` enhancements |
| 3.3 | M7 | `--tag` filter (CLI flag; TUI has tag: search) |
| 3.4 | M9 | index cache |
| 3.5 | M6 | optional `tmux` output mode |

### Phase 4 — Release (v1.0)

| Step | Module | Task | Status |
|------|--------|------|--------|
| 4.1 | M10 T3 | 200+ runnable cheats | Not started |
| 4.2 | M7 | `--study` mode | Done |
| 4.3 | M12 | PyPI publish `loadout-cli` | Not started |
| 4.4 | — | README, screenshots, contributing guide | Partial |

### Phase 5 — Optional (v2.0)

- Go port (`cmd/loadout`) embedding same `cheats/` via `embed.FS`
- GitHub Actions release binaries (linux amd64/arm64)
- Community cheat PR template

---

## 6. Cheat authoring workflow (M10)

For each new tool:

1. Copy `loadout/cheats/_template.yaml` → `loadout/cheats/<NN-category>/<tool>.yaml`
2. Fill `tool`, `tags`, `actions` per [CHEAT_SCHEMA.md](CHEAT_SCHEMA.md)
3. Run `loadout cheats validate cheats/<category>/<tool>.yaml`
4. Run `loadout` and smoke-test search + run (Enter) + copy chip
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
| Scope creep (800 tools vs 200–300 CLI) | Tier T0–T4; study-only `conceptual/` entries; T1 seed list caps v0.2 |
| TIOCSTI broken on Linux 6.2+ | Clipboard default; prefill opt-in |
| Duplicate tool names in pack | `cheats validate` checks duplicates |
| Large repo / slow TUI | M9 index cache; lazy load |
| Legal / misuse | Descriptions note authorized use; Copy confirms destructive commands; Run opens subterminal immediately |
| PyPI name taken | Register `loadout-cli` early |

---

## 8. Next actions (immediate)

**You are here:** Phase 2.5 wrap-up → Phase 3 content scale.

| Priority | Task | Module | Notes |
|----------|------|--------|-------|
| 1 | Populate empty CEH categories | M10 | 7 categories have no tools yet — source from `ceh-v13-notebook/Tools/` |
| 2 | Study mode polish | M7 | Exam-hint-first detail; hide run/copy chips |
| 3 | `cheats validate --all` in CI | M8/M11 | Done |
| 4 | Git commit + push | — | Full codebase still mostly uncommitted |
| 5 | T2 pack (100 tools) | M10 | Phase 3 primary goal |
| 6 | Index cache | M9 | When cheat count slows startup |

**Rough timeline (solo dev):** Phase 2.5 finish ≈ 1 day · Phase 3 (100 cheats) ≈ 2 weeks · Phase 4 (v1.0) ≈ 2–4 weeks.

---

## 9. Related docs

- [ARCHITECTURE.md](ARCHITECTURE.md) — dependency graph and paths
- [CHEAT_SCHEMA.md](CHEAT_SCHEMA.md) — YAML contract
- [../README.md](../README.md) — project overview

---

## 10. Progress tracker

| Module | Status | Version / notes |
|--------|--------|-----------------|
| M1 Config | Done | paths, cheat_paths, save |
| M2 Models | Done | Action, CheatFile, OutputMode |
| M3 Loader | Done | merge, study-only, warnings |
| M4 Substitute | Done | `{{var}}`, `{{var\|default}}` |
| M5 Variables | Done | persist vars.json |
| M6 Output | Done | clipboard, print, `launch_command`, doctor |
| M7 TUI | Done | browse, search, run/copy chips, subterminal run, no toasts |
| M8 CLI | Done | vars, cheats, doctor, config, `--study` |
| M9 Index | Deferred | v0.5 |
| M10 Cheats | T1+ seed | 47 tools, 129 actions, all 15 CEH categories |
| M11 Tests | Done | 84 tests, 18 files, CI (3.11 + 3.12) |
| M12 Packaging | Done | v0.3.1, `loadout-cli` |

**Supporting modules:** `browse.py`, `categories.py`, `pack_stats.py`, `search.py`, `guard.py`, `tui_theme.py`, `tui_screens.py`, `tui_hints.py`, `cheats_cmd.py`

**Phase status:** Phase 2.5 complete · Phase 3 started (47/100 tools)

**Milestone vs plan:**

| Target | Plan | Actual |
|--------|------|--------|
| v0.1 | Framework + 1 cheat | Done |
| v0.2 | 30 cheats, vars, user path | Done (v0.3.1) |
| v0.5 | 100 cheats, validate, cache | Not started |
| v1.0 | 200+ cheats, PyPI, study | Partial (`--study`, `doctor` done) |

_Update this table as modules land._
