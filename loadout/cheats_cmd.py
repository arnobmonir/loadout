"""User cheat file scaffolding."""

from __future__ import annotations

from pathlib import Path

from loadout.config import get_user_cheats_dir

_TEMPLATE = """\
tool: {tool}
tags: []
exam_hint: ""
docs: []

actions:
  - title: example action
    desc: Authorized lab only.
    command: "{tool} {{ip}}"
"""


def scaffold_user_cheat(tool: str, *, dest_dir: Path | None = None) -> Path:
    """Create a new user cheat YAML from the built-in template."""
    name = tool.strip()
    if not name:
        raise ValueError("tool name must be non-empty")

    directory = dest_dir or get_user_cheats_dir()
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{name}.yaml"

    if path.exists():
        raise FileExistsError(f"cheat file already exists: {path}")

    path.write_text(_TEMPLATE.format(tool=name), encoding="utf-8")
    return path
