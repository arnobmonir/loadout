"""Tests for TUI list row formatting."""

from pathlib import Path

from loadout.config import LoadoutConfig
from loadout.models import Action
from loadout.tui import LoadoutApp
from loadout.variables import VariableStore


def _app() -> LoadoutApp:
    config = LoadoutConfig.load()
    return LoadoutApp(config, VariableStore(defaults=config.default_vars))


def test_search_row_includes_description():
    app = _app()
    action = Action(
        tool="nmap",
        title="SYN stealth scan",
        command="nmap -sS {{ip}}",
        source_file=Path("cheats/02-scanning_and_enumeration/nmap.yaml"),
        desc="Stealth TCP SYN scan on target",
    )
    row = app._format_list_row(action, "", selected=False)
    assert "Stealth TCP SYN scan" in row


def test_browse_command_row_includes_description():
    from loadout.browse import BrowseRow

    app = _app()
    action = Action(
        tool="nmap",
        title="host discovery",
        command="nmap -sn {{ip}}/24",
        source_file=Path("cheats/02-scanning_and_enumeration/nmap.yaml"),
        desc="Ping sweep on subnet (authorized lab only)",
    )
    row = BrowseRow(level="command", label="host discovery", action=action)
    line = app._format_browse_row(row, selected=False)
    assert "Ping sweep on subnet" in line
