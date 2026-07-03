"""Shared data models for Loadout."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class OutputMode(str, Enum):
    """How finalized commands are delivered to the user."""

    CLIPBOARD = "clipboard"
    PRINT = "print"


@dataclass(frozen=True, slots=True)
class Placeholder:
    """A {{name}} or {{name|default}} token in a command string."""

    name: str
    default: str | None = None

    @property
    def required(self) -> bool:
        return self.default is None


@dataclass(frozen=True, slots=True)
class Action:
    """A single runnable command entry from a cheat file."""

    tool: str
    title: str
    command: str
    source_file: Path
    tags: tuple[str, ...] = ()
    desc: str = ""
    exam_hint: str = ""
    docs: tuple[str, ...] = ()

    @property
    def search_text(self) -> str:
        parts = [self.tool, self.title, self.command, self.desc, *self.tags]
        return " ".join(parts).lower()


@dataclass(frozen=True, slots=True)
class CheatFile:
    """Parsed YAML cheat file (one tool per file)."""

    tool: str
    source_file: Path
    actions: tuple[Action, ...] = ()
    tags: tuple[str, ...] = ()
    exam_hint: str = ""
    docs: tuple[str, ...] = ()


@dataclass(slots=True)
class SubstituteResult:
    """Result of substituting variables into a command."""

    command: str
    missing: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.missing


@dataclass(slots=True)
class LoadoutIndex:
    """In-memory index of all loaded actions."""

    actions: list[Action] = field(default_factory=list)

    def by_tool(self) -> dict[str, list[Action]]:
        grouped: dict[str, list[Action]] = {}
        for action in self.actions:
            grouped.setdefault(action.tool, []).append(action)
        return grouped
