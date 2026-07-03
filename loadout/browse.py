"""Category → tool → command browse tree."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from loadout.models import Action


@dataclass(frozen=True, slots=True)
class BrowseRow:
    """One row in the hierarchical browser."""

    level: str  # category | tool | command
    label: str
    category: str | None = None
    tool: str | None = None
    action: Action | None = None
    tool_count: int = 0
    command_count: int = 0
    tags: tuple[str, ...] = ()


def category_slug_from_path(path: Path) -> str:
    """Return manifest category slug from a cheat file path."""
    folder = path.parent.name
    if "-" in folder:
        _, _, name = folder.partition("-")
        return name.lower()
    return folder.lower()


def category_display_from_slug(slug: str) -> str:
    """Human-readable category label from a manifest slug."""
    return slug.replace("_", " ").title()


def category_from_path(path: Path) -> tuple[str, str]:
    """Return (sort_key, display_name) from a cheat file path."""
    folder = path.parent.name
    if "-" in folder:
        prefix, _, name = folder.partition("-")
        return prefix, category_display_from_slug(name.lower())
    return folder, folder.title()


def build_browse_tree(actions: list[Action]) -> tuple[dict[str, dict[str, list[Action]]], dict[str, str]]:
    """
    Build category → tool → actions tree.

    Returns (tree, category_sort_keys).
    """
    tree: dict[str, dict[str, list[Action]]] = {}
    sort_keys: dict[str, str] = {}

    for action in actions:
        sort_key, category = category_from_path(action.source_file)
        sort_keys[category] = sort_key
        tree.setdefault(category, {}).setdefault(action.tool, []).append(action)

    for category in tree:
        for tool in tree[category]:
            tree[category][tool].sort(key=lambda a: a.title)

    return tree, sort_keys


def sorted_categories(
    tree: dict[str, dict[str, list[Action]]],
    sort_keys: dict[str, str],
    *,
    manifest_slugs: tuple[str, ...] = (),
) -> list[str]:
    if not manifest_slugs:
        return sorted(tree.keys(), key=lambda c: sort_keys.get(c, c))

    ordered: list[str] = []
    seen: set[str] = set()
    for slug in manifest_slugs:
        display = category_display_from_slug(slug)
        ordered.append(display)
        seen.add(display)
    for display in sorted(tree.keys(), key=lambda c: sort_keys.get(c, c)):
        if display not in seen:
            ordered.append(display)
    return ordered


def rows_for_level(
    tree: dict[str, dict[str, list[Action]]],
    sort_keys: dict[str, str],
    *,
    level: str,
    category: str | None = None,
    tool: str | None = None,
    manifest_slugs: tuple[str, ...] = (),
) -> list[BrowseRow]:
    """Build list rows for the current browse level."""
    if level == "category":
        rows: list[BrowseRow] = []
        for cat in sorted_categories(tree, sort_keys, manifest_slugs=manifest_slugs):
            tools = tree.get(cat, {})
            cmd_count = sum(len(v) for v in tools.values())
            rows.append(
                BrowseRow(
                    level="category",
                    label=cat,
                    category=cat,
                    tool_count=len(tools),
                    command_count=cmd_count,
                )
            )
        return rows

    if level == "tool" and category and category in tree:
        rows = []
        for tool_name in sorted(tree[category]):
            actions = tree[category][tool_name]
            sample = actions[0]
            rows.append(
                BrowseRow(
                    level="tool",
                    label=tool_name,
                    category=category,
                    tool=tool_name,
                    command_count=len(actions),
                    tags=sample.tags,
                )
            )
        return rows

    if level == "command" and category and tool and category in tree and tool in tree[category]:
        return [
            BrowseRow(
                level="command",
                label=action.title,
                category=category,
                tool=tool,
                action=action,
                tags=action.tags,
            )
            for action in tree[category][tool]
        ]

    return []
