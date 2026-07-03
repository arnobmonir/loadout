"""Tests for loadout.models."""

from pathlib import Path

from loadout.models import Action, LoadoutIndex


def test_action_search_text():
    action = Action(
        tool="nmap",
        title="SYN scan",
        command="nmap -sS {{ip}}",
        source_file=Path("nmap.yaml"),
        tags=("recon",),
        desc="stealth",
    )
    assert "nmap" in action.search_text
    assert "recon" in action.search_text


def test_loadout_index_by_tool():
    a1 = Action("nmap", "syn", "cmd", Path("a.yaml"))
    a2 = Action("nmap", "udp", "cmd2", Path("a.yaml"))
    a3 = Action("curl", "get", "cmd3", Path("b.yaml"))
    index = LoadoutIndex(actions=[a1, a2, a3])
    grouped = index.by_tool()
    assert len(grouped["nmap"]) == 2
    assert len(grouped["curl"]) == 1
