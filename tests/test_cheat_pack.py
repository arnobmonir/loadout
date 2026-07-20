"""Tests for compiled cheat pack."""

from pathlib import Path

import pytest

from loadout.cheat_pack import build_pack, is_cheat_pack, load_pack_files
from loadout.config import get_builtin_cheat_source
from loadout.loader import load_cheat_file, load_cheats


def test_builtin_uses_compiled_pack():
    source = get_builtin_cheat_source()
    assert is_cheat_pack(source)


def test_pack_roundtrip(tmp_path: Path):
    src = tmp_path / "cheats"
    src.mkdir()
    (src / "manifest.yaml").write_text("version: 1\ncategories: {}\n", encoding="utf-8")
    tool_dir = src / "01-reconnaissance"
    tool_dir.mkdir()
    (tool_dir / "demo.yaml").write_text(
        """\
tool: demo
tags: [recon]
actions:
  - title: ping host
    desc: Send one ICMP echo request.
    command: "ping -c 1 {{ip}}"
""",
        encoding="utf-8",
    )

    pack_path = tmp_path / "demo.pack"
    count = build_pack(src, pack_path)
    assert count == 2
    assert is_cheat_pack(pack_path)

    files = load_pack_files(pack_path)
    assert "01-reconnaissance/demo.yaml" in files

    actions = load_cheats([pack_path], warn=False)
    assert len(actions) == 1
    assert actions[0].tool == "demo"


def test_build_pack_requires_manifest(tmp_path: Path):
    src = tmp_path / "empty"
    src.mkdir()
    with pytest.raises(Exception):
        build_pack(src, tmp_path / "bad.pack")


def test_encrypted_pack_hides_plaintext(tmp_path: Path):
    src = tmp_path / "cheats"
    src.mkdir()
    (src / "manifest.yaml").write_text("version: 1\ncategories: {}\n", encoding="utf-8")
    tool_dir = src / "01-reconnaissance"
    tool_dir.mkdir()
    (tool_dir / "demo.yaml").write_text(
        """\
tool: demo
tags: [recon]
actions:
  - title: ping host
    desc: Send one ICMP echo request.
    command: "ping -c 1 {{ip}}"
""",
        encoding="utf-8",
    )

    pack_path = tmp_path / "secret.pack"
    build_pack(src, pack_path)
    raw = pack_path.read_bytes()
    assert b"tool: demo" not in raw
    assert b"ping -c 1" not in raw


def test_tampered_pack_rejected(tmp_path: Path):
    src = tmp_path / "cheats"
    src.mkdir()
    (src / "manifest.yaml").write_text("version: 1\ncategories: {}\n", encoding="utf-8")
    (src / "01-reconnaissance").mkdir()
    (src / "01-reconnaissance" / "demo.yaml").write_text(
        "tool: demo\nactions:\n  - title: t\n    desc: d\n    command: x\n",
        encoding="utf-8",
    )
    pack_path = tmp_path / "demo.pack"
    build_pack(src, pack_path)

    raw = bytearray(pack_path.read_bytes())
    raw[-1] ^= 0xFF
    pack_path.write_bytes(raw)

    with pytest.raises(Exception, match="authentication failed|corrupt"):
        load_pack_files(pack_path)

