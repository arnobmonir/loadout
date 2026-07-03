"""Tests for loadout.output."""

from loadout.models import OutputMode
from loadout.output import clipboard_available, clipboard_error, deliver, doctor_report


def test_deliver_print_mode(capsys):
    ok, message = deliver("nmap -sS 10.0.0.1", OutputMode.PRINT)
    captured = capsys.readouterr()
    assert ok
    assert "nmap -sS 10.0.0.1" in captured.out
    assert "Printed" in message


def test_doctor_report_includes_python():
    rows = doctor_report()
    checks = {name for name, _, _ in rows}
    assert "python" in checks
    assert "builtin cheats" in checks


def test_clipboard_helpers_return_consistent_types():
    error = clipboard_error()
    assert (error is None) == clipboard_available()
    if error is not None:
        assert isinstance(error, str)


def test_deliver_clipboard_fallback_message(capsys, monkeypatch):
    import loadout.output as output

    class BrokenClipboard:
        @staticmethod
        def copy(_: str) -> None:
            raise RuntimeError("no backend")

    monkeypatch.setattr(output, "pyperclip", BrokenClipboard(), raising=False)
    monkeypatch.setitem(__import__("sys").modules, "pyperclip", BrokenClipboard())

    ok, message = deliver("nmap -sS 10.0.0.1", OutputMode.CLIPBOARD)
    captured = capsys.readouterr()
    assert not ok
    assert "Clipboard unavailable; printed instead" in message
    assert "nmap -sS 10.0.0.1" in captured.out
