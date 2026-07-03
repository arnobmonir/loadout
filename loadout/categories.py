"""Category metadata from the cheat pack manifest."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

from loadout.config import get_builtin_cheats_dir

_DEFAULT_STRATEGY = (
    "Review the tool details, then choose the smallest command that answers your question."
)


@dataclass(frozen=True, slots=True)
class CategoryInfo:
    """Display text for a cheat pack category."""

    description: str = ""
    strategy: str = _DEFAULT_STRATEGY


def category_key(display_name: str) -> str:
    """Map a browse-tree display name to a manifest category key."""
    return display_name.strip().lower().replace(" ", "_")


def manifest_category_slugs(cheats_dir: Path | None = None) -> tuple[str, ...]:
    """Return manifest category slugs in YAML definition order."""
    cheats_dir = cheats_dir or get_builtin_cheats_dir()
    manifest = cheats_dir / "manifest.yaml"
    if not manifest.is_file():
        return ()
    try:
        with manifest.open(encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
    except yaml.YAMLError:
        return ()
    raw_categories = data.get("categories")
    if not isinstance(raw_categories, dict):
        return ()
    return tuple(
        key.strip().lower()
        for key in raw_categories
        if isinstance(key, str) and isinstance(raw_categories[key], dict)
    )


def load_category_info(cheats_dir: Path | None = None) -> dict[str, CategoryInfo]:
    """Load category descriptions and strategies from manifest.yaml."""
    cheats_dir = cheats_dir or get_builtin_cheats_dir()
    manifest = cheats_dir / "manifest.yaml"
    if not manifest.is_file():
        return {}

    try:
        with manifest.open(encoding="utf-8") as fh:
            data = yaml.safe_load(fh) or {}
    except yaml.YAMLError:
        return {}

    raw_categories = data.get("categories")
    if not isinstance(raw_categories, dict):
        return {}

    info: dict[str, CategoryInfo] = {}
    for key, value in raw_categories.items():
        if not isinstance(key, str):
            continue
        normalized = key.strip().lower()
        if isinstance(value, dict):
            description = str(value.get("description") or "").strip()
            strategy = str(value.get("strategy") or "").strip() or _DEFAULT_STRATEGY
            info[normalized] = CategoryInfo(description=description, strategy=strategy)
    return info


def category_info_for(
    display_name: str,
    catalog: dict[str, CategoryInfo] | None = None,
) -> CategoryInfo:
    """Return metadata for a category display name, with safe fallbacks."""
    catalog = catalog if catalog is not None else load_category_info()
    return catalog.get(category_key(display_name), CategoryInfo())
