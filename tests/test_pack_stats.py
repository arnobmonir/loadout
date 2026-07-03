"""Tests for cheat pack statistics."""

from pathlib import Path

from loadout.pack_stats import collect_pack_stats
from loadout.models import Action


def _action(tool: str, title: str, folder: str, *, tags: tuple[str, ...] = ()) -> Action:
    return Action(
        tool=tool,
        title=title,
        command=f"{tool} {{ip}}",
        source_file=Path(f"cheats/{folder}/{tool}.yaml"),
        tags=tags,
    )


def test_collect_pack_stats_from_actions():
    actions = [
        _action("nmap", "syn", "01-recon", tags=("recon",)),
        _action("nmap", "udp", "01-recon", tags=("recon", "scanning")),
        _action("masscan", "fast", "02-scanning", tags=("scanning",)),
    ]
    stats = collect_pack_stats(actions, cheat_paths=[])
    assert stats.tool_count == 2
    assert stats.command_count == 3
    assert stats.category_count == 15
    assert stats.tag_count == 2
    assert stats.pack_version != "?"
    assert stats.updated_label
