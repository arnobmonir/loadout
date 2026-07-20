"""Deliver finalized commands to clipboard, stdout, or a subterminal."""

from __future__ import annotations

import os
import shutil
import subprocess
from collections.abc import Callable, Sequence

from loadout.models import OutputMode

LaunchFn = Callable[[str, list[str]], tuple[bool, str]]


def clipboard_error() -> str | None:
    """Return a human-readable clipboard backend error, or None if available."""
    try:
        import pyperclip  # noqa: PLC0415

        pyperclip.copy("")
        return None
    except Exception as exc:
        return str(exc)


def clipboard_available() -> bool:
    return clipboard_error() is None


def deliver(command: str, mode: OutputMode) -> tuple[bool, str]:
    """
    Send command to the configured output target.

    Returns (success, message) for UI feedback.
    """
    if mode == OutputMode.PRINT:
        print(command)
        return True, f"Printed: {command}"

    try:
        import pyperclip  # noqa: PLC0415

        pyperclip.copy(command)
        return True, f"Copied: {command}"
    except Exception:
        print(command)
        return False, f"Clipboard unavailable; printed instead: {command}"


def interactive_shell_script(command: str) -> str:
    """Bash script that runs a command and keeps the subterminal open."""
    return (
        f"{command}\n"
        "code=$?\n"
        'echo\n'
        'printf "Exit code: %s\\n" "$code"\n'
        'read -r -p "Press Enter to close... " _\n'
        "exit $code\n"
    )


def shell_command_argv(command: str) -> list[str]:
    """Argv to run a command in bash and hold the terminal open."""
    return ["bash", "-lc", interactive_shell_script(command)]


def _spawn(argv: Sequence[str]) -> tuple[bool, str]:
    try:
        subprocess.Popen(
            list(argv),
            start_new_session=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as exc:
        return False, str(exc)
    return True, ""


def _launch_tmux(_command: str, shell_argv: list[str]) -> tuple[bool, str]:
    if not os.environ.get("TMUX"):
        return False, "not in tmux"
    if not shutil.which("tmux"):
        return False, "tmux not found"
    ok, detail = _spawn(["tmux", "split-window", "-h", *shell_argv])
    if not ok:
        return False, detail
    return True, "tmux pane"


def _launch_gnome_terminal(_command: str, shell_argv: list[str]) -> tuple[bool, str]:
    if not shutil.which("gnome-terminal"):
        return False, "gnome-terminal not found"
    ok, detail = _spawn(["gnome-terminal", "--", *shell_argv])
    if not ok:
        return False, detail
    return True, "gnome-terminal window"


def _launch_konsole(_command: str, shell_argv: list[str]) -> tuple[bool, str]:
    if not shutil.which("konsole"):
        return False, "konsole not found"
    ok, detail = _spawn(["konsole", "--hold", "-e", *shell_argv])
    if not ok:
        return False, detail
    return True, "konsole window"


def _launch_xfce_terminal(_command: str, shell_argv: list[str]) -> tuple[bool, str]:
    if not shutil.which("xfce4-terminal"):
        return False, "xfce4-terminal not found"
    ok, detail = _spawn(["xfce4-terminal", "--hold", "-e", *shell_argv])
    if not ok:
        return False, detail
    return True, "xfce4-terminal window"


def _launch_kitty(_command: str, shell_argv: list[str]) -> tuple[bool, str]:
    if not shutil.which("kitty"):
        return False, "kitty not found"
    ok, detail = _spawn(["kitty", *shell_argv])
    if not ok:
        return False, detail
    return True, "kitty window"


def _launch_alacritty(_command: str, shell_argv: list[str]) -> tuple[bool, str]:
    if not shutil.which("alacritty"):
        return False, "alacritty not found"
    ok, detail = _spawn(["alacritty", "-e", *shell_argv])
    if not ok:
        return False, detail
    return True, "alacritty window"


def _launch_wezterm(_command: str, shell_argv: list[str]) -> tuple[bool, str]:
    if not shutil.which("wezterm"):
        return False, "wezterm not found"
    ok, detail = _spawn(["wezterm", "start", "--", *shell_argv])
    if not ok:
        return False, detail
    return True, "wezterm window"


def _launch_xterm(_command: str, shell_argv: list[str]) -> tuple[bool, str]:
    if not shutil.which("xterm"):
        return False, "xterm not found"
    ok, detail = _spawn(["xterm", "-hold", "-e", *shell_argv])
    if not ok:
        return False, detail
    return True, "xterm window"


def _launch_from_terminal_env(_command: str, shell_argv: list[str]) -> tuple[bool, str]:
    terminal = os.environ.get("TERMINAL", "").strip()
    if not terminal:
        return False, "TERMINAL not set"
    ok, detail = _spawn([terminal, "-e", *shell_argv])
    if not ok:
        return False, detail
    return True, f"{terminal} window"


def subterminal_launchers() -> tuple[LaunchFn, ...]:
    """Ordered launch strategies for opening a subterminal."""
    return (
        _launch_tmux,
        _launch_gnome_terminal,
        _launch_konsole,
        _launch_xfce_terminal,
        _launch_kitty,
        _launch_alacritty,
        _launch_wezterm,
        _launch_xterm,
        _launch_from_terminal_env,
    )


def subterminal_backend() -> str | None:
    """Return the first available subterminal backend name, if any."""
    if os.environ.get("TMUX") and shutil.which("tmux"):
        return "tmux pane"
    for binary, label in (
        ("gnome-terminal", "gnome-terminal window"),
        ("konsole", "konsole window"),
        ("xfce4-terminal", "xfce4-terminal window"),
        ("kitty", "kitty window"),
        ("alacritty", "alacritty window"),
        ("wezterm", "wezterm window"),
        ("xterm", "xterm window"),
    ):
        if shutil.which(binary):
            return label
    terminal = os.environ.get("TERMINAL", "").strip()
    if terminal and shutil.which(terminal):
        return f"{terminal} window"
    return None


def launch_command(command: str) -> tuple[bool, str]:
    """
    Run a command in a new tmux pane or terminal window.

    Returns (success, message) for UI feedback.
    """
    shell_argv = shell_command_argv(command)
    errors: list[str] = []
    for launch in subterminal_launchers():
        ok, detail = launch(command, shell_argv)
        if ok:
            return True, f"Launched in {detail}: {command}"
        if detail:
            errors.append(detail)

    return False, (
        "No subterminal available "
        f"({'; '.join(errors[:3])}). Install tmux or a terminal emulator."
    )


def run_command(command: str) -> tuple[bool, str]:
    """
    Execute a command in the current terminal (fallback when no subterminal).

    Returns (success, message) for UI feedback.
    """
    try:
        result = subprocess.run(command, shell=True, check=False)
    except Exception as exc:
        return False, f"Failed to run: {exc}"
    if result.returncode == 0:
        return True, f"Finished (exit 0): {command}"
    return False, f"Finished (exit {result.returncode}): {command}"


def clipboard_install_hint() -> str:
    """Short install hint for the system clipboard helper."""
    session = os.environ.get("XDG_SESSION_TYPE", "").lower()
    if session == "wayland":
        return "sudo apt-get install -y wl-clipboard"
    return "sudo apt-get install -y xclip"


def doctor_report() -> list[tuple[str, str, str]]:
    """Return (check, status, detail) rows for loadout doctor."""
    import sys as _sys

    from loadout.config import get_builtin_cheat_source

    rows: list[tuple[str, str, str]] = []

    version = _sys.version_info
    if version >= (3, 11):
        rows.append(("python", "pass", f"{version.major}.{version.minor}.{version.micro}"))
    else:
        rows.append(("python", "fail", f"{version.major}.{version.minor} (need 3.11+)"))

    error = clipboard_error()
    if error is None:
        rows.append(("clipboard", "pass", "pyperclip backend available"))
    else:
        rows.append(
            (
                "clipboard",
                "warn",
                f"unavailable; use output_mode: print or install: {clipboard_install_hint()}",
            )
        )

    backend = subterminal_backend()
    if backend:
        rows.append(("subterminal", "pass", backend))
    else:
        rows.append(("subterminal", "warn", "no tmux pane or terminal emulator found for Run"))

    try:
        builtin = get_builtin_cheat_source()
        label = "compiled pack" if builtin.suffix == ".pack" else "source tree"
        rows.append(("builtin cheats", "pass", f"{builtin} ({label})"))
    except FileNotFoundError as exc:
        rows.append(("builtin cheats", "fail", str(exc)))

    return rows
