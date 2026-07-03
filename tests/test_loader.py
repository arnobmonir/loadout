"""Tests for loadout.loader."""

from pathlib import Path

import pytest

from loadout.loader import CheatLoadError, load_cheat_file, load_cheats

FIXTURES = Path(__file__).parent / "fixtures" / "cheats"


def test_load_cheat_file_sample():
    cheat = load_cheat_file(FIXTURES / "sample_nmap.yaml")
    assert cheat.tool == "nmap"
    assert len(cheat.actions) == 2
    assert cheat.actions[0].title == "SYN scan"
    assert cheat.actions[0].docs == ("https://nmap.org/",)


def test_load_study_only_cheat():
    cheat = load_cheat_file(FIXTURES / "study_only.yaml")
    assert cheat.tool == "nessus"
    assert cheat.actions == ()
    assert "vulnerability" in cheat.exam_hint


def test_load_cheats_merge_override(tmp_path):
    user_dir = tmp_path / "user"
    user_dir.mkdir()
    builtin_dir = FIXTURES
    user_file = user_dir / "nmap.yaml"
    user_file.write_text(
        """\
tool: nmap
actions:
  - title: SYN scan
    command: "nmap -sS {{ip|127.0.0.1}}"
"""
    )
    actions = load_cheats([builtin_dir, user_dir], warn=False)
    syn = next(a for a in actions if a.title == "SYN scan")
    assert "127.0.0.1" in syn.command


def test_invalid_yaml_raises(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text("tool: [unclosed")
    with pytest.raises(CheatLoadError, match="invalid YAML"):
        load_cheat_file(bad)


def test_missing_tool_raises(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text("actions: []\nexam_hint: x")
    with pytest.raises(CheatLoadError, match="tool"):
        load_cheat_file(bad)
