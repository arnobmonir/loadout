"""Cheat pack statistics for the TUI and CLI."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import yaml

from loadout.browse import build_browse_tree
from loadout.categories import manifest_category_slugs
from loadout.cheat_pack import count_pack_cheat_files, is_cheat_pack, load_pack_manifest
from loadout.config import get_builtin_cheat_source
from loadout.loader import _SKIP_FILES
from loadout.models import Action


@dataclass(frozen=True, slots=True)
class PackStats:
    """Summary counts for the loaded cheat pack."""

    tool_count: int
    command_count: int
    category_count: int
    tag_count: int
    cheat_file_count: int
    user_cheat_file_count: int
    pack_version: str
    updated_at: datetime

    @property
    def updated_label(self) -> str:
        return self.updated_at.strftime("%b %d, %Y")


def _yaml_cheat_files(path: Path) -> list[Path]:
    if not path.is_dir():
        return []
    files: list[Path] = []
    for pattern in ("*.yaml", "*.yml"):
        files.extend(path.rglob(pattern))
    return [f for f in files if f.name not in _SKIP_FILES]


def _load_manifest_version(cheat_source: Path) -> str:
    if is_cheat_pack(cheat_source):
        data = load_pack_manifest(cheat_source)
    else:
        manifest = cheat_source / "manifest.yaml"
        if not manifest.is_file():
            return "?"
        try:
            with manifest.open(encoding="utf-8") as fh:
                data = yaml.safe_load(fh) or {}
        except yaml.YAMLError:
            return "?"
    version = data.get("version")
    return str(version) if version is not None else "?"


def _builtin_cheat_file_count(cheat_source: Path) -> int:
    if is_cheat_pack(cheat_source):
        return count_pack_cheat_files(cheat_source)
    return len(_yaml_cheat_files(cheat_source))


def _latest_mtime(paths: list[Path]) -> datetime | None:
    latest: float | None = None
    for path in paths:
        if not path.is_file():
            continue
        mtime = path.stat().st_mtime
        if latest is None or mtime > latest:
            latest = mtime
    if latest is None:
        return None
    return datetime.fromtimestamp(latest)


def collect_pack_stats(
    actions: list[Action],
    *,
    cheat_paths: list[Path] | None = None,
) -> PackStats:
    """Derive pack statistics from loaded actions and cheat directories."""
    cheat_paths = cheat_paths or []
    builtin_source = get_builtin_cheat_source()

    tree, _ = build_browse_tree(actions)
    tags = {tag.lower() for action in actions for tag in action.tags}
    manifest_slugs = manifest_category_slugs(builtin_source)
    category_count = len(manifest_slugs) if manifest_slugs else len(tree)

    builtin_file_count = _builtin_cheat_file_count(builtin_source)
    user_files: list[Path] = []
    for path in cheat_paths:
        if path.resolve() == builtin_source.resolve():
            continue
        user_files.extend(_yaml_cheat_files(path))

    if is_cheat_pack(builtin_source):
        updated_at = datetime.fromtimestamp(builtin_source.stat().st_mtime)
    else:
        manifest_mtime = _latest_mtime([builtin_source / "manifest.yaml"])
        content_mtime = _latest_mtime(_yaml_cheat_files(builtin_source) + user_files)
        updated_at = content_mtime or manifest_mtime or datetime.now()

    return PackStats(
        tool_count=len({a.tool for a in actions}),
        command_count=len(actions),
        category_count=category_count,
        tag_count=len(tags),
        cheat_file_count=builtin_file_count,
        user_cheat_file_count=len(user_files),
        pack_version=_load_manifest_version(builtin_source),
        updated_at=updated_at,
    )
