"""Arsenal-ng inspired colors, tags, and command syntax highlighting for Rich markup."""

from __future__ import annotations

import re

# UI palette (from arsenal-ng theme)
COLOR_PRIMARY = "#FF6B6B"
COLOR_SECONDARY = "#4ECDC4"
COLOR_ACCENT = "#FFE66D"
COLOR_DIM = "#666666"
COLOR_BRIGHT = "#FFFFFF"
COLOR_DESC = "#888888"
COLOR_SUCCESS = "#98D8C8"
COLOR_ERROR = "#FF6B6B"
COLOR_INFO = "#7aa2f7"
COLOR_PURPLE = "#AA96DA"
COLOR_CORAL = "#F38181"

# Browse / selection backgrounds
COLOR_SEL_CATEGORY = "#6A0572"
COLOR_SEL_TOOL = "#2d6a6a"
COLOR_SEL_COMMAND = "#4a4e8a"

_CATEGORY_ICONS = (
    "📁", "🔍", "📡", "🎯", "💥", "🔐", "🛡️", "🔑", "🦠", "🎣",
    "☁️", "🔧", "📶", "🔒", "📋", "⚡", "🌐", "🧪",
)

# Command syntax
COLOR_CMD_TOOL = "#FF6B6B"
COLOR_CMD_FLAG = "#4ECDC4"
COLOR_CMD_ARG = "#FFE66D"
COLOR_CMD_DEFAULT = "#FF8C00"
COLOR_CMD_STRING = "#98D8C8"
COLOR_CMD_VAR = "#F7DC6F"
COLOR_CMD_NORMAL = "#CCCCCC"
COLOR_CMD_PIPE = "#BB8FCE"

TAG_COLORS = (
    "#FF6B6B",
    "#4ECDC4",
    "#FFE66D",
    "#95E1D3",
    "#F38181",
    "#AA96DA",
    "#78C4D4",
    "#F9ED69",
    "#F08A5D",
    "#B83B5E",
    "#6A0572",
    "#00B8A9",
    "#F6416C",
    "#FCBAD3",
    "#A8D8EA",
)

COMMON_VARIABLES = (
    ("ip", "10.10.10.10", "Target IP address"),
    ("domain", "target.htb", "Target domain / hostname"),
    ("url", "http://10.10.10.10", "Target URL"),
    ("port", "443", "Port number"),
    ("user", "administrator", "Username"),
    ("pass", "Password123", "Password"),
    ("lhost", "10.10.14.5", "Your local IP (reverse shells)"),
    ("lport", "4444", "Local listener port"),
    ("wordlist", "/usr/share/wordlists/...", "Wordlist path"),
    ("output", "results.txt", "Output file"),
)

_TOKEN_RE = re.compile(
    r"(\{\{[a-zA-Z_][a-zA-Z0-9_]*(?:\|[^}]*)?\}\}|\"[^\"]*\"|'[^']*'|\S+|\s+)"
)
_PIPE_OPS = frozenset({"|", ">", "<", ">>", "&&", "||", ";"})


def _hash_color(name: str) -> str:
    h = 0
    for ch in name:
        h = h * 31 + ord(ch)
    return TAG_COLORS[abs(h) % len(TAG_COLORS)]


def category_icon(name: str) -> str:
    h = sum(ord(ch) for ch in name.lower())
    return _CATEGORY_ICONS[h % len(_CATEGORY_ICONS)]


def format_selected(text: str, *, width: int | None = None, level: str = "command") -> str:
    """Highlight a selected list row with a level-colored background."""
    bg = {
        "category": COLOR_SEL_CATEGORY,
        "tool": COLOR_SEL_TOOL,
        "command": COLOR_SEL_COMMAND,
        "search": COLOR_SEL_COMMAND,
    }.get(level, COLOR_SEL_COMMAND)
    inner = text if width is None else f"{text:{width}}"
    return f"[#FFFFFF bold on {bg}] {inner} [/]"


def render_welcome_panel() -> tuple[str, str, str]:
    """Friendly empty-state copy for the detail panel."""
    title = f"[{COLOR_PRIMARY} bold]👋 Welcome to Loadout[/]"
    desc = (
        f"[{COLOR_BRIGHT}]Browse CEH phases on the left, or type to search.[/]\n\n"
        f"[{COLOR_DIM}]Try [/][{COLOR_SECONDARY} bold]nmap[/]"
        f"[{COLOR_DIM}] · [/][{COLOR_ACCENT} bold]tag:recon[/]"
        f"[{COLOR_DIM}] · [/][{COLOR_SUCCESS} bold]set ip=10.0.0.1[/]"
    )
    hint = (
        f"[{COLOR_ACCENT}]💡[/] Press [{COLOR_SECONDARY}]?[/] for help  "
        f"[{COLOR_DIM}]·[/]  [{COLOR_ACCENT}]v[/] for variables  "
        f"[{COLOR_DIM}]·[/]  [{COLOR_INFO}]Ctrl+T[/] to browse"
    )
    return title, desc, hint


def tool_color(tool: str) -> str:
    return _hash_color(tool)


def tag_color(tag: str) -> str:
    return _hash_color(tag)


def render_tags(tags: tuple[str, ...] | list[str]) -> str:
    if not tags:
        return f"[{COLOR_DIM}]no tags[/]"
    parts = [f"[{tag_color(t)}]#{t}[/]" for t in tags]
    return " ".join(parts)


def highlight_match(text: str, query: str) -> str:
    """Bold-accent the first case-insensitive substring match."""
    if not query or not text:
        return text
    low_text, low_q = text.lower(), query.lower()
    idx = low_text.find(low_q)
    if idx < 0:
        return text
    before, match, after = text[:idx], text[idx : idx + len(query)], text[idx + len(query) :]
    return f"{before}[{COLOR_ACCENT} bold]{match}[/]{after}"


def highlight_command(command: str) -> str:
    """Syntax-highlight a shell command as Rich markup."""
    tokens = _TOKEN_RE.findall(command)
    parts: list[str] = []
    first_token = True

    for token in tokens:
        if not token:
            continue
        if token.isspace():
            parts.append(token)
            continue

        if token.startswith("{{") and token.endswith("}}"):
            color = COLOR_CMD_DEFAULT if "|" in token else COLOR_CMD_ARG
            parts.append(f"[{color} bold]{token}[/]")
            continue

        if first_token and not token.startswith(("-", "|")):
            parts.append(f"[{COLOR_CMD_TOOL} bold]{token}[/]")
            first_token = False
            continue

        if token.startswith("--") or (token.startswith("-") and len(token) > 1):
            parts.append(f"[{COLOR_CMD_FLAG}]{token}[/]")
            continue

        if token in _PIPE_OPS:
            parts.append(f"[{COLOR_CMD_PIPE}]{token}[/]")
            first_token = True
            continue

        if token.startswith(("'", '"')):
            parts.append(f"[{COLOR_CMD_STRING}]{token}[/]")
            continue

        if token.startswith("$"):
            parts.append(f"[{COLOR_CMD_VAR} bold]{token}[/]")
            continue

        parts.append(f"[{COLOR_CMD_NORMAL}]{token}[/]")
        if token.strip():
            first_token = False

    return "".join(parts)


def badge(label: str, value: str, color: str = COLOR_SECONDARY) -> str:
    return f"[{color} bold]{label}[/][{COLOR_BRIGHT}] {value}[/]"


def render_header_line(
    *,
    version: str,
    tool_count: int,
    cmd_count: int,
    var_count: int,
    output_mode: str,
    study: bool = False,
) -> str:
    mode = "STUDY" if study else output_mode.upper()
    mode_color = COLOR_ACCENT if study else COLOR_SUCCESS
    parts = [
        f"[{COLOR_PRIMARY} bold]◆ LOADOUT[/]",
        f"[{COLOR_DIM}]v{version}[/]",
        f"[{COLOR_SECONDARY} bold]{tool_count}[/][{COLOR_DIM}] tools[/]",
        f"[{COLOR_DIM}]·[/]",
        f"[{COLOR_CORAL} bold]{cmd_count}[/][{COLOR_DIM}] cmds[/]",
        f"[{COLOR_DIM}]·[/]",
        f"[{COLOR_ACCENT} bold]{var_count}[/][{COLOR_DIM}] vars[/]",
        f"[{mode_color} bold]▸ {mode}[/]",
    ]
    return "  ".join(parts)


def render_stats_bar(
    *,
    tool_count: int,
    command_count: int,
    category_count: int,
    tag_count: int,
    cheat_file_count: int,
    user_cheat_file_count: int,
    pack_version: str,
    updated_label: str,
    var_count: int = 0,
) -> str:
    """Permanent bottom stats bar above key hints."""
    user_part = (
        f"  [{COLOR_DIM}]·[/]  [{COLOR_ACCENT}]{user_cheat_file_count} user cheats[/]"
        if user_cheat_file_count
        else ""
    )
    return (
        f"[{COLOR_SECONDARY} bold]📊[/] "
        f"[{COLOR_SECONDARY}]{tool_count}[/][{COLOR_DIM}] tools[/]  "
        f"[{COLOR_DIM}]·[/] "
        f"[{COLOR_CORAL}]{command_count}[/][{COLOR_DIM}] cmds[/]  "
        f"[{COLOR_DIM}]·[/] "
        f"[{COLOR_PURPLE}]{category_count}[/][{COLOR_DIM}] cats[/]  "
        f"[{COLOR_DIM}]·[/] "
        f"[{COLOR_INFO}]{tag_count}[/][{COLOR_DIM}] tags[/]  "
        f"[{COLOR_DIM}]·[/] "
        f"[{COLOR_DIM}]pack[/] [{COLOR_ACCENT}]v{pack_version}[/]  "
        f"[{COLOR_DIM}]·[/] "
        f"[{COLOR_DIM}]updated[/] [{COLOR_SUCCESS}]{updated_label}[/]  "
        f"[{COLOR_DIM}]·[/] "
        f"[{COLOR_ACCENT}]{var_count}[/][{COLOR_DIM}] vars[/]"
        f"{user_part}"
    )
