"""Interactive hints when typing special commands (arsenal-ng style)."""

from __future__ import annotations

from loadout.tui_theme import (
    COLOR_ACCENT,
    COLOR_DESC,
    COLOR_DIM,
    COLOR_PRIMARY,
    COLOR_SECONDARY,
    COLOR_SUCCESS,
    COMMON_VARIABLES,
)


def hint_for_query(raw: str) -> str | None:
    """Return Rich markup hint for special commands, or None to hide hints panel."""
    q = raw.strip().lower()

    if not q:
        return None

    if q in ("set", "set "):
        return _set_hints()

    if q.startswith("set ") and "=" not in q:
        partial = raw.strip()[4:].strip()
        return _set_suggestions(partial)

    if q.startswith("set ") and "=" in q:
        return f"[{COLOR_SUCCESS} bold]✓ Press Enter to save variable[/]"

    if q in ("unset", "unset "):
        return _unset_hints()

    if q.startswith("unset "):
        key = raw.strip()[6:].strip()
        if key:
            return f"[{COLOR_SUCCESS} bold]✓ Press Enter to unset '{key}'[/]"
        return _unset_hints()

    if q in ("variables", "variables "):
        return f"[{COLOR_SUCCESS} bold]✓ Press Enter to open variables panel[/]"

    if q == "tools":
        return f"[{COLOR_SUCCESS} bold]✓ Press Enter to browse all tools[/]"

    if q in ("help", "help "):
        return f"[{COLOR_SUCCESS} bold]✓ Press Enter to open help[/]"

    if q == "reload":
        return f"[{COLOR_SUCCESS} bold]✓ Press Enter to reload cheat pack[/]"

    if q.startswith("output "):
        return f"[{COLOR_SUCCESS} bold]✓ Press Enter to change output mode (saved to config)[/]"

    if q.startswith("set "):
        return None

    return None


def _set_hints() -> str:
    lines = [f"[{COLOR_PRIMARY} bold]💡 Common variables[/]", ""]
    for name, example, desc in COMMON_VARIABLES:
        lines.append(
            f"  [{COLOR_SECONDARY}]{name}[/]=[{COLOR_ACCENT}]{example}[/]  "
            f"[{COLOR_DIM}]{desc}[/]"
        )
    lines.append("")
    lines.append(f"[{COLOR_DIM}]Example: set ip=10.10.10.10[/]")
    return "\n".join(lines)


def _set_suggestions(partial: str) -> str:
    matches = [v for v in COMMON_VARIABLES if partial.lower() in v[0].lower()]
    if not matches:
        return f"[{COLOR_DIM}]Type set name=value (e.g. set ip=10.10.10.10)[/]"

    lines = [f"[{COLOR_PRIMARY} bold]Suggestions for '{partial}'[/]", ""]
    for name, example, desc in matches[:8]:
        lines.append(
            f"  [{COLOR_SECONDARY}]set {name}={example}[/]  [{COLOR_DIM}]{desc}[/]"
        )
    return "\n".join(lines)


def _unset_hints() -> str:
    names = ", ".join(v[0] for v in COMMON_VARIABLES[:6])
    return (
        f"[{COLOR_PRIMARY} bold]Unset a variable[/]\n\n"
        f"  [{COLOR_DIM}]Example: unset ip[/]\n"
        f"  [{COLOR_DIM}]Common keys: {names}…[/]"
    )
