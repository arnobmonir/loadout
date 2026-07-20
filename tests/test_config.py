"""Tests for loadout.config."""

from pathlib import Path

from loadout.config import LoadoutConfig, get_builtin_cheat_source


def test_builtin_cheat_source_exists():
    path = get_builtin_cheat_source()
    assert path.exists()
    if path.is_dir():
        assert any(path.rglob("nmap.yaml"))
    else:
        from loadout.cheat_pack import is_cheat_pack

        assert is_cheat_pack(path)


def test_loadout_config_defaults(tmp_path, monkeypatch):
    config_dir = tmp_path / "config"
    monkeypatch.setenv("LOADOUT_CONFIG_DIR", str(config_dir))
    cfg = LoadoutConfig.load()
    assert cfg.output_mode.value == "clipboard"
    assert "wordlist" in cfg.default_vars


def test_loadout_config_custom_yaml(tmp_path, monkeypatch):
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config_file = config_dir / "config.yaml"
    config_file.write_text(
        """\
output_mode: print
cheat_paths:
  - /tmp/custom-cheats
default_vars:
  wordlist: /custom/wordlist.txt
"""
    )
    monkeypatch.setenv("LOADOUT_CONFIG_DIR", str(config_dir))
    cfg = LoadoutConfig.load()
    assert cfg.output_mode.value == "print"
    assert str(cfg.cheat_paths[0]).endswith("custom-cheats")
    assert cfg.default_vars["wordlist"] == "/custom/wordlist.txt"


def test_all_cheat_paths_includes_builtin():
    cfg = LoadoutConfig()
    paths = cfg.all_cheat_paths()
    assert len(paths) >= 1
    assert any("cheat" in str(p).lower() for p in paths)


def test_ensure_dirs_creates_user_cheat_path(tmp_path, monkeypatch):
    config_dir = tmp_path / "config"
    monkeypatch.setenv("LOADOUT_CONFIG_DIR", str(config_dir))
    cfg = LoadoutConfig.load()
    cfg.ensure_dirs()
    assert cfg.cheat_paths[0].is_dir()


def test_config_save_roundtrip(tmp_path, monkeypatch):
    config_dir = tmp_path / "config"
    monkeypatch.setenv("LOADOUT_CONFIG_DIR", str(config_dir))
    cfg = LoadoutConfig.load()
    cfg.set_output_mode(cfg.output_mode)  # triggers save
    from loadout.models import OutputMode

    cfg.set_output_mode(OutputMode.PRINT)
    reloaded = LoadoutConfig.load()
    assert reloaded.output_mode == OutputMode.PRINT
