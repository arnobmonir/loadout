"""Safety checks before copying destructive commands."""

from __future__ import annotations

import re

_DESTRUCTIVE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\brm\s+-rf\b", re.IGNORECASE),
    re.compile(r"\bmkfs\b", re.IGNORECASE),
    re.compile(r"\bdd\s+if=", re.IGNORECASE),
    re.compile(r"\bshutdown\b", re.IGNORECASE),
    re.compile(r"\breboot\b", re.IGNORECASE),
    re.compile(r":\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;", re.IGNORECASE),  # fork bomb
)


def is_destructive(command: str) -> bool:
    """Return True if the command matches a known destructive pattern."""
    return any(pattern.search(command) for pattern in _DESTRUCTIVE_PATTERNS)
