"""Tests for hierarchical browse tree."""

from pathlib import Path

from loadout.browse import (
    build_browse_tree,
    category_display_from_slug,
    rows_for_level,
    sorted_categories,
)
from loadout.models import Action


def _action(tool: str, title: str, folder: str) -> Action:
    return Action(
        tool=tool,
        title=title,
        command=f"{tool} {{ip}}",
        source_file=Path(f"cheats/{folder}/{tool}.yaml"),
    )


def test_build_browse_tree_groups_by_category_and_tool():
    actions = [
        _action("nmap", "syn", "01-reconnaissance"),
        _action("nmap", "udp", "01-reconnaissance"),
        _action("masscan", "fast", "02-scanning_and_enumeration"),
    ]
    tree, sort_keys = build_browse_tree(actions)
    assert "Reconnaissance" in tree
    assert "Scanning And Enumeration" in tree
    assert len(tree["Reconnaissance"]["nmap"]) == 2
    assert sorted_categories(tree, sort_keys) == [
        "Reconnaissance",
        "Scanning And Enumeration",
    ]


def test_sorted_categories_follows_manifest_order():
    actions = [
        _action("masscan", "fast", "02-scanning_and_enumeration"),
        _action("dig", "a", "01-reconnaissance"),
    ]
    tree, sort_keys = build_browse_tree(actions)
    slugs = ("reconnaissance", "scanning_and_enumeration", "exploitation")
    ordered = sorted_categories(tree, sort_keys, manifest_slugs=slugs)
    assert ordered == [
        "Reconnaissance",
        "Scanning And Enumeration",
        "Exploitation",
    ]


def test_rows_for_each_level():
    actions = [
        _action("nmap", "syn", "01-reconnaissance"),
        _action("nmap", "udp", "01-reconnaissance"),
        _action("masscan", "fast", "02-scanning_and_enumeration"),
    ]
    tree, sort_keys = build_browse_tree(actions)

    cats = rows_for_level(tree, sort_keys, level="category")
    assert cats[0].level == "category"
    assert cats[0].tool_count == 1

    tools = rows_for_level(tree, sort_keys, level="tool", category="Reconnaissance")
    assert len(tools) == 1
    assert tools[0].tool == "nmap"

    cmds = rows_for_level(
        tree, sort_keys, level="command", category="Reconnaissance", tool="nmap"
    )
    assert len(cmds) == 2
    assert cmds[0].level == "command"


def test_rows_for_level_includes_empty_manifest_categories():
    actions = [_action("dig", "a", "01-reconnaissance")]
    tree, sort_keys = build_browse_tree(actions)
    slugs = ("reconnaissance", "exploitation")
    rows = rows_for_level(
        tree,
        sort_keys,
        level="category",
        manifest_slugs=slugs,
    )
    assert len(rows) == 2
    assert rows[0].tool_count == 1
    assert rows[1].label == "Exploitation"
    assert rows[1].tool_count == 0


def test_category_display_from_slug():
    assert category_display_from_slug("post_exploitation_and_privilege_escalation") == (
        "Post Exploitation And Privilege Escalation"
    )
