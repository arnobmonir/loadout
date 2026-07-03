"""Tests for duplicate tool detection and cheat pack quality."""

from loadout.loader import find_duplicate_tools, load_cheats


def test_no_duplicate_tools_in_builtin_pack():
    from loadout.config import get_builtin_cheats_dir

    dupes = find_duplicate_tools([get_builtin_cheats_dir()])
    assert dupes == []


def test_every_action_has_description():
    from loadout.config import get_builtin_cheats_dir

    actions = load_cheats([get_builtin_cheats_dir()])
    missing = [(a.tool, a.title) for a in actions if not a.desc.strip()]
    assert missing == []
    assert len(actions) >= 125
