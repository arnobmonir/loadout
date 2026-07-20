"""Discover and parse YAML cheat files."""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

from loadout.cheat_pack import is_cheat_pack, iter_pack_cheat_entries
from loadout.models import Action, CheatFile

_SKIP_FILES = {"manifest.yaml", "_template.yaml"}


class CheatLoadError(Exception):
    """Raised when a cheat file cannot be parsed."""


def _yaml_files(path: Path) -> list[Path]:
    if path.is_file() and path.suffix in {".yaml", ".yml"}:
        return [path]
    if not path.is_dir():
        return []
    files: list[Path] = []
    for pattern in ("*.yaml", "*.yml"):
        files.extend(path.rglob(pattern))
    return sorted({f for f in files if f.name not in _SKIP_FILES})


def load_cheat_file(path: Path, *, content: str | None = None) -> CheatFile:
    """Parse a single cheat YAML file (or in-memory YAML text from a pack)."""
    try:
        if content is None:
            with path.open(encoding="utf-8") as fh:
                data = yaml.safe_load(fh)
        else:
            data = yaml.safe_load(content)
    except yaml.YAMLError as exc:
        raise CheatLoadError(f"{path}: invalid YAML: {exc}") from exc

    if not isinstance(data, dict):
        raise CheatLoadError(f"{path}: expected a YAML mapping at top level")

    tool = data.get("tool")
    if not tool or not str(tool).strip():
        raise CheatLoadError(f"{path}: 'tool' must be non-empty")

    tool = str(tool).strip()
    tags = tuple(str(t) for t in (data.get("tags") or []))
    exam_hint = str(data.get("exam_hint") or "")
    docs = tuple(str(d) for d in (data.get("docs") or []))

    raw_actions = data.get("actions")
    if raw_actions is None:
        raw_actions = []
    if not isinstance(raw_actions, list):
        raise CheatLoadError(f"{path}: 'actions' must be a list")

    if not raw_actions and not exam_hint:
        raise CheatLoadError(f"{path}: need at least one action or an exam_hint")

    actions: list[Action] = []
    seen_titles: set[str] = set()
    for idx, item in enumerate(raw_actions):
        if not isinstance(item, dict):
            raise CheatLoadError(f"{path}: actions[{idx}] must be a mapping")

        title = item.get("title")
        if not title or not str(title).strip():
            raise CheatLoadError(f"{path}: actions[{idx}].title must be non-empty")
        title = str(title).strip()

        if title in seen_titles:
            raise CheatLoadError(f"{path}: duplicate action title '{title}'")
        seen_titles.add(title)

        command = item.get("command")
        if command is None or not str(command).strip():
            raise CheatLoadError(f"{path}: actions[{idx}].command must be non-empty")
        command = str(command).strip()

        desc = str(item.get("desc") or "")
        actions.append(
            Action(
                tool=tool,
                title=title,
                command=command,
                source_file=path,
                tags=tags,
                desc=desc,
                exam_hint=exam_hint,
                docs=docs,
            )
        )

    return CheatFile(
        tool=tool,
        source_file=path,
        actions=tuple(actions),
        tags=tags,
        exam_hint=exam_hint,
        docs=docs,
    )


def _iter_cheat_sources(base: Path) -> list[tuple[Path, str | None]]:
    """Yield (path, content) pairs; content is set when loading from a .pack file."""
    if is_cheat_pack(base):
        return [(path, text) for path, text in iter_pack_cheat_entries(base)]
    return [(path, None) for path in _yaml_files(base)]


def find_duplicate_tools(paths: list[Path]) -> list[str]:
    """Return tool names that appear in more than one cheat file."""
    tool_files: dict[str, list[Path]] = {}
    for base in paths:
        for cheat_path, content in _iter_cheat_sources(base):
            try:
                cheat = load_cheat_file(cheat_path, content=content)
            except CheatLoadError:
                continue
            tool_files.setdefault(cheat.tool, []).append(cheat_path)

    return sorted(tool for tool, files in tool_files.items() if len(files) > 1)


def load_cheats(paths: list[Path], *, warn: bool = True) -> list[Action]:
    """Load and merge cheat files from directories or compiled .pack files."""
    by_key: dict[tuple[str, str], Action] = {}
    order: list[tuple[str, str]] = []

    for base in paths:
        for cheat_path, content in _iter_cheat_sources(base):
            try:
                cheat = load_cheat_file(cheat_path, content=content)
            except CheatLoadError as exc:
                if warn:
                    print(f"loadout: warning: {exc}", file=sys.stderr)
                continue

            for action in cheat.actions:
                key = (action.tool, action.title)
                if key not in by_key:
                    order.append(key)
                by_key[key] = action

    return [by_key[key] for key in order]
