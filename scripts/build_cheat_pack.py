#!/usr/bin/env python3
"""Compile loadout/cheats/*.yaml into loadout/cheats.pack for distribution."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
SOURCE = ROOT / "loadout" / "cheats"
OUTPUT = ROOT / "loadout" / "cheats.pack"


def main() -> int:
    if not SOURCE.is_dir():
        print(f"loadout: cheat source directory not found: {SOURCE}", file=sys.stderr)
        return 1

    from loadout.cheat_pack import build_pack

    try:
        count = build_pack(SOURCE, OUTPUT)
    except Exception as exc:
        print(f"loadout: {exc}", file=sys.stderr)
        return 1

    size_kb = OUTPUT.stat().st_size / 1024
    print(f"Wrote {OUTPUT} ({count} files, {size_kb:.1f} KiB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
