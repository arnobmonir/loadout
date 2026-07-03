"""Tests for loadout.guard."""

from loadout.guard import is_destructive


def test_destructive_rm_rf():
    assert is_destructive("rm -rf /")


def test_destructive_dd():
    assert is_destructive("dd if=/dev/zero of=/dev/sda")


def test_safe_command():
    assert not is_destructive("nmap -sS 10.0.0.1")
