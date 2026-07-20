"""Encrypted built-in cheat pack (replaces shipping plain YAML)."""

from __future__ import annotations

import gzip
import hashlib
import json
import os
from functools import lru_cache
from pathlib import Path

import yaml
from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

_SKIP_FILES = frozenset({"manifest.yaml", "_template.yaml"})

PACK_SUFFIX = ".pack"
PACK_MAGIC = b"LOADOUTPK2\n"
_NONCE_SIZE = 12


class CheatPackError(Exception):
    """Raised when a cheat pack cannot be read or written."""


def is_cheat_pack(path: Path) -> bool:
    return path.is_file() and path.suffix == PACK_SUFFIX


def _pack_seed() -> bytes:
    """Obfuscated seed bytes; combined with SHA-256 to derive the AES-256 key."""
    encoded = (
        201,
        206,
        204,
        207,
        206,
        202,
        207,
        234,
        198,
        192,
        221,
        234,
        211,
        182,
        182,
        234,
        213,
        196,
        198,
        215,
        234,
        206,
        192,
        221,
        234,
        183,
        183,
        183,
        183,
        234,
        192,
        203,
    )
    return bytes(byte ^ 0xA5 for byte in encoded)


def _aes_key() -> bytes:
    return hashlib.sha256(_pack_seed()).digest()


def _encrypt_payload(plain: bytes) -> bytes:
    nonce = os.urandom(_NONCE_SIZE)
    ciphertext = AESGCM(_aes_key()).encrypt(nonce, plain, None)
    return nonce + ciphertext


def _decrypt_payload(blob: bytes) -> bytes:
    if len(blob) < _NONCE_SIZE + 16:
        raise CheatPackError("encrypted payload too short")
    nonce = blob[:_NONCE_SIZE]
    ciphertext = blob[_NONCE_SIZE:]
    try:
        return AESGCM(_aes_key()).decrypt(nonce, ciphertext, None)
    except InvalidTag as exc:
        raise CheatPackError("pack authentication failed (tampered or wrong key)") from exc


def _encode_files(files: dict[str, str]) -> bytes:
    payload = json.dumps({"files": files}, separators=(",", ":")).encode("utf-8")
    return _encrypt_payload(gzip.compress(payload, compresslevel=9))


def _decode_payload(blob: bytes) -> dict[str, str]:
    try:
        plain = gzip.decompress(_decrypt_payload(blob))
        data = json.loads(plain.decode("utf-8"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise CheatPackError(f"corrupt pack payload: {exc}") from exc

    files = data.get("files")
    if not isinstance(files, dict):
        raise CheatPackError("pack missing 'files' mapping")

    return {str(key): str(value) for key, value in files.items()}


@lru_cache(maxsize=4)
def _read_pack(path_str: str) -> dict[str, str]:
    path = Path(path_str)
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise CheatPackError(f"{path}: cannot read pack: {exc}") from exc

    if not raw.startswith(PACK_MAGIC):
        raise CheatPackError(f"{path}: not a loadout cheat pack")

    return _decode_payload(raw[len(PACK_MAGIC) :])


def load_pack_files(path: Path) -> dict[str, str]:
    """Return relative cheat paths → YAML text from a .pack file."""
    return _read_pack(str(path.resolve()))


def load_pack_manifest(path: Path) -> dict:
    """Parse manifest.yaml embedded in a cheat pack."""
    files = load_pack_files(path)
    manifest_text = files.get("manifest.yaml")
    if manifest_text is None:
        return {}
    try:
        data = yaml.safe_load(manifest_text) or {}
    except yaml.YAMLError:
        return {}
    return data if isinstance(data, dict) else {}


def iter_pack_cheat_entries(path: Path) -> list[tuple[Path, str]]:
    """Return (virtual_path, yaml_text) for tool cheat files in a pack."""
    entries: list[tuple[Path, str]] = []
    for rel_path, content in sorted(load_pack_files(path).items()):
        name = Path(rel_path).name
        if name in _SKIP_FILES:
            continue
        if not name.endswith((".yaml", ".yml")):
            continue
        entries.append((Path(rel_path), content))
    return entries


def count_pack_cheat_files(path: Path) -> int:
    return len(iter_pack_cheat_entries(path))


def build_pack(source_dir: Path, output_path: Path) -> int:
    """Compile a cheats directory into an encrypted .pack file. Returns file count."""
    if not source_dir.is_dir():
        raise CheatPackError(f"{source_dir}: not a directory")

    files: dict[str, str] = {}
    for pattern in ("*.yaml", "*.yml"):
        for cheat_path in sorted(source_dir.rglob(pattern)):
            rel = cheat_path.relative_to(source_dir).as_posix()
            files[rel] = cheat_path.read_text(encoding="utf-8")

    if "manifest.yaml" not in files:
        raise CheatPackError(f"{source_dir}: manifest.yaml is required")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(PACK_MAGIC + _encode_files(files))
    return len(files)
