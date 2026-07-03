"""Tests for loadout.variables."""

from loadout.variables import VariableStore


def test_set_get_persist(tmp_path):
    path = tmp_path / "vars.json"
    store = VariableStore(path=path, defaults={"wordlist": "/tmp/w.txt"})
    store.set("ip", "10.10.10.5")
    assert store.get("ip") == "10.10.10.5"

    reloaded = VariableStore(path=path, defaults={"wordlist": "/tmp/w.txt"})
    assert reloaded.get("ip") == "10.10.10.5"


def test_defaults_not_overwritten_by_user_empty(tmp_path):
    path = tmp_path / "vars.json"
    store = VariableStore(path=path, defaults={"wordlist": "/default.txt"})
    assert store.get("wordlist") == "/default.txt"


def test_unset(tmp_path):
    path = tmp_path / "vars.json"
    store = VariableStore(path=path)
    store.set("ip", "1.2.3.4")
    assert store.unset("ip")
    assert store.get("ip") is None
    assert not store.unset("ip")
