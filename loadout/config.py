"""Configuration paths and defaults."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from loadout.models import OutputMode

DEFAULT_WORDLIST = "/usr/share/wordlists/dirb/common.txt"


def _expand(path: str | Path) -> Path:
    return Path(os.path.expanduser(str(path))).resolve()


def get_config_dir() -> Path:
    return _expand(os.environ.get("LOADOUT_CONFIG_DIR", "~/.config/loadout"))


def get_cache_dir() -> Path:
    return _expand(os.environ.get("LOADOUT_CACHE_DIR", "~/.cache/loadout"))


def get_builtin_cheats_dir() -> Path:
    """Resolve built-in cheats whether installed editable or as a wheel."""
    pkg_cheats = Path(__file__).resolve().parent / "cheats"
    if pkg_cheats.is_dir() and any(pkg_cheats.rglob("*.yaml")):
        return pkg_cheats

    repo_cheats = Path(__file__).resolve().parent.parent / "cheats"
    if repo_cheats.is_dir():
        return repo_cheats

    raise FileNotFoundError(
        "Built-in cheat pack not found. Reinstall loadout-cli or run from the project root."
    )


def get_user_cheats_dir() -> Path:
    return get_config_dir() / "cheats"


def get_vars_path() -> Path:
    return get_config_dir() / "vars.json"


def get_config_path() -> Path:
    return get_config_dir() / "config.yaml"


@dataclass(slots=True)
class LoadoutConfig:
    output_mode: OutputMode = OutputMode.CLIPBOARD
    cheat_paths: list[Path] = field(default_factory=list)
    default_vars: dict[str, str] = field(default_factory=dict)

    @classmethod
    def load(cls) -> LoadoutConfig:
        config_dir = get_config_dir()
        config_path = config_dir / "config.yaml"
        data: dict = {}

        if config_path.is_file():
            with config_path.open(encoding="utf-8") as fh:
                loaded = yaml.safe_load(fh)
                if loaded:
                    data = loaded

        output_raw = data.get("output_mode", OutputMode.CLIPBOARD.value)
        try:
            output_mode = OutputMode(output_raw)
        except ValueError:
            output_mode = OutputMode.CLIPBOARD

        cheat_paths_raw = data.get("cheat_paths")
        if cheat_paths_raw:
            cheat_paths = [_expand(p) for p in cheat_paths_raw]
        else:
            cheat_paths = [get_user_cheats_dir()]

        default_vars = dict(data.get("default_vars") or {})
        if "wordlist" not in default_vars:
            default_vars.setdefault("wordlist", DEFAULT_WORDLIST)

        return cls(
            output_mode=output_mode,
            cheat_paths=cheat_paths,
            default_vars=default_vars,
        )

    def ensure_dirs(self) -> None:
        """Create config and user cheat directories if missing."""
        get_config_dir().mkdir(parents=True, exist_ok=True)
        for path in self.cheat_paths:
            path.mkdir(parents=True, exist_ok=True)

    def all_cheat_paths(self) -> list[Path]:
        """Builtin cheats first, then user paths (later overrides earlier)."""
        return [get_builtin_cheats_dir(), *self.cheat_paths]

    def save(self) -> None:
        """Persist current settings to config.yaml (merges with existing file)."""
        path = get_config_path()
        data: dict = {}
        if path.is_file():
            with path.open(encoding="utf-8") as fh:
                loaded = yaml.safe_load(fh)
                if isinstance(loaded, dict):
                    data = loaded

        data["output_mode"] = self.output_mode.value
        data["cheat_paths"] = [str(p) for p in self.cheat_paths]
        data["default_vars"] = self.default_vars

        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as fh:
            yaml.safe_dump(data, fh, default_flow_style=False, sort_keys=False)

    def set_output_mode(self, mode: OutputMode) -> None:
        self.output_mode = mode
        self.save()
