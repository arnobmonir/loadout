"""Persistent global variable storage."""

from __future__ import annotations

import json
from pathlib import Path

from loadout.config import get_vars_path


class VariableStore:
    """Read/write user variables with config defaults as fallbacks."""

    def __init__(self, path: Path | None = None, defaults: dict[str, str] | None = None):
        self.path = path or get_vars_path()
        self.defaults = dict(defaults or {})
        self._user: dict[str, str] = {}
        self.load()

    def load(self) -> None:
        if self.path.is_file():
            with self.path.open(encoding="utf-8") as fh:
                data = json.load(fh)
            if isinstance(data, dict):
                self._user = {str(k): str(v) for k, v in data.items()}
            else:
                self._user = {}
        else:
            self._user = {}

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as fh:
            json.dump(self._user, fh, indent=2, sort_keys=True)
            fh.write("\n")

    def get(self, key: str) -> str | None:
        if key in self._user:
            return self._user[key]
        return self.defaults.get(key)

    def set(self, key: str, value: str) -> None:
        self._user[key] = value
        self.save()

    def unset(self, key: str) -> bool:
        if key not in self._user:
            return False
        del self._user[key]
        self.save()
        return True

    def list_user(self) -> dict[str, str]:
        return dict(self._user)

    def list_all(self) -> dict[str, str]:
        merged = dict(self.defaults)
        merged.update(self._user)
        return merged

    def as_substitution_map(self) -> dict[str, str]:
        return {k: v for k, v in self.list_all().items() if v != ""}
