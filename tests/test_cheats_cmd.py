"""Tests for user cheat scaffolding."""

import pytest

from loadout.cheats_cmd import scaffold_user_cheat


def test_scaffold_user_cheat(tmp_path):
    path = scaffold_user_cheat("customtool", dest_dir=tmp_path)
    assert path.is_file()
    assert "tool: customtool" in path.read_text()


def test_scaffold_refuses_duplicate(tmp_path):
    scaffold_user_cheat("dup", dest_dir=tmp_path)
    with pytest.raises(FileExistsError):
        scaffold_user_cheat("dup", dest_dir=tmp_path)
