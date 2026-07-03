"""Placeholder parsing and variable substitution."""

from __future__ import annotations

import re

from loadout.models import Placeholder, SubstituteResult

_PLACEHOLDER_RE = re.compile(
    r"\{\{([a-zA-Z_][a-zA-Z0-9_]*)(?:\|([^}]*))?\}\}"
)


def parse_placeholders(command: str) -> list[Placeholder]:
    """Return placeholders in left-to-right order (duplicates preserved)."""
    placeholders: list[Placeholder] = []
    for match in _PLACEHOLDER_RE.finditer(command):
        name = match.group(1)
        default = match.group(2)
        placeholders.append(Placeholder(name=name, default=default))
    return placeholders


def substitute(command: str, vars: dict[str, str]) -> SubstituteResult:
    """Replace {{var}} and {{var|default}} tokens; report unresolved required vars."""
    missing: list[str] = []
    seen_missing: set[str] = set()

    def replacer(match: re.Match[str]) -> str:
        name = match.group(1)
        default = match.group(2)
        if name in vars and vars[name] != "":
            return vars[name]
        if default is not None:
            return default
        if name not in seen_missing:
            seen_missing.add(name)
            missing.append(name)
        return match.group(0)

    result = _PLACEHOLDER_RE.sub(replacer, command)
    return SubstituteResult(command=result, missing=missing)
