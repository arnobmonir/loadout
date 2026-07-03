"""Tests for loadout.output run and subterminal launch."""

from loadout.output import (
    interactive_shell_script,
    launch_command,
    run_command,
    shell_command_argv,
    subterminal_backend,
)


def test_interactive_shell_script_includes_command_and_hold():
    script = interactive_shell_script("nmap -sn 10.0.0.0/24")
    assert "nmap -sn 10.0.0.0/24" in script
    assert "Press Enter to close" in script
    assert "exit $code" in script


def test_shell_command_argv_uses_bash_lc():
    argv = shell_command_argv("echo hi")
    assert argv[:2] == ["bash", "-lc"]
    assert "echo hi" in argv[2]


def test_launch_command_uses_first_working_backend(monkeypatch):
    calls: list[str] = []

    def fail(_cmd: str, _argv: list[str]) -> tuple[bool, str]:
        return False, "nope"

    def succeed(_cmd: str, _argv: list[str]) -> tuple[bool, str]:
        calls.append("ok")
        return True, "tmux pane"

    monkeypatch.setattr(
        "loadout.output.subterminal_launchers",
        lambda: (fail, succeed),
    )
    ok, message = launch_command("echo hello")
    assert ok
    assert calls == ["ok"]
    assert "tmux pane" in message


def test_launch_command_reports_when_no_backend(monkeypatch):
    monkeypatch.setattr(
        "loadout.output.subterminal_launchers",
        lambda: (lambda _c, _a: (False, "missing"),),
    )
    ok, message = launch_command("echo hello")
    assert not ok
    assert "No subterminal available" in message


def test_subterminal_backend_detects_tmux(monkeypatch):
    monkeypatch.setenv("TMUX", "/tmp/tmux-0")
    monkeypatch.setattr("loadout.output.shutil.which", lambda name: "/usr/bin/tmux" if name == "tmux" else None)
    assert subterminal_backend() == "tmux pane"


def test_subterminal_backend_detects_gnome_terminal(monkeypatch):
    monkeypatch.delenv("TMUX", raising=False)

    def which(name: str) -> str | None:
        return "/usr/bin/gnome-terminal" if name == "gnome-terminal" else None

    monkeypatch.setattr("loadout.output.shutil.which", which)
    assert subterminal_backend() == "gnome-terminal window"


def test_run_command_success(monkeypatch):
    class Result:
        returncode = 0

    monkeypatch.setattr(
        "loadout.output.subprocess.run",
        lambda *args, **kwargs: Result(),
    )
    ok, message = run_command("echo hello")
    assert ok
    assert "exit 0" in message


def test_run_command_nonzero_exit(monkeypatch):
    class Result:
        returncode = 2

    monkeypatch.setattr(
        "loadout.output.subprocess.run",
        lambda *args, **kwargs: Result(),
    )
    ok, message = run_command("false")
    assert not ok
    assert "exit 2" in message


def test_run_command_failure(monkeypatch):
    def boom(*args, **kwargs):
        raise OSError("permission denied")

    monkeypatch.setattr("loadout.output.subprocess.run", boom)
    ok, message = run_command("nmap localhost")
    assert not ok
    assert "Failed to run" in message
