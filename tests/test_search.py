"""Tests for loadout.search."""

from loadout.models import Action
from loadout.search import parse_search_query, rank_actions, score_action
from pathlib import Path


def _action(tool: str, title: str, tags: tuple[str, ...] = (), command: str = "") -> Action:
    return Action(
        tool=tool,
        title=title,
        command=command or f"{tool} {{ip}}",
        source_file=Path("x.yaml"),
        tags=tags,
    )


def test_parse_tag_filter():
    q = parse_search_query("tag:recon nmap")
    assert q.tag == "recon"
    assert q.text == "nmap"


def test_parse_hash_tag():
    q = parse_search_query("#web scan")
    assert q.tag == "web"
    assert q.text == "scan"


def test_parse_tool_filter():
    q = parse_search_query("tool:nmap syn")
    assert q.tool == "nmap"
    assert q.text == "syn"


def test_rank_by_tag():
    actions = [
        _action("nmap", "syn", ("recon",)),
        _action("hydra", "ssh", ("brute-force",)),
    ]
    ranked = rank_actions(actions, parse_search_query("tag:recon"))
    assert len(ranked) == 1
    assert ranked[0].action.tool == "nmap"


def test_score_prefers_tool_match():
    action = _action("nmap", "syn scan", ("recon",), "nmap -sS {{ip}}")
    high = score_action(action, "nmap")
    low = score_action(action, "zzz")
    assert high > low
