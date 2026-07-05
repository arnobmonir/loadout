"""TUI variable editor tests."""

import asyncio

from textual.widgets import Input

from loadout.config import LoadoutConfig
from loadout.models import OutputMode
from loadout.tui import LoadoutApp
from loadout.variables import VariableStore


async def _v_opens_editor_from_search() -> None:
    config = LoadoutConfig.load()
    config.output_mode = OutputMode.PRINT
    store = VariableStore(defaults=config.default_vars)
    app = LoadoutApp(config, store)
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        assert getattr(app.focused, "id", None) == "search"
        await pilot.press("v")
        await pilot.pause()
        assert app.screen.__class__.__name__ == "VariablesScreen"
        await pilot.press("escape")
        await pilot.pause()


async def _set_command_from_search(tmp_path) -> None:
    config = LoadoutConfig.load()
    config.output_mode = OutputMode.PRINT
    store = VariableStore(path=tmp_path / "vars.json", defaults=config.default_vars)
    app = LoadoutApp(config, store)
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        search = app.query_one("#search")
        search.value = "set ip=10.0.0.1"
        search.post_message(Input.Submitted(search, "set ip=10.0.0.1"))
        await pilot.pause()
        assert store.get("ip") == "10.0.0.1"


async def _editor_saves_value(tmp_path) -> None:
    config = LoadoutConfig.load()
    config.output_mode = OutputMode.PRINT
    store = VariableStore(path=tmp_path / "vars.json", defaults=config.default_vars)
    app = LoadoutApp(config, store)
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        app.action_show_variables()
        await pilot.pause()
        ip_input = app.screen.query_one("#var-ip")
        ip_input.value = "192.168.1.50"
        app.screen.action_save()
        await pilot.pause()
        assert store.get("ip") == "192.168.1.50"


def test_v_opens_editor_from_search():
    asyncio.run(_v_opens_editor_from_search())


def test_set_command_from_search(tmp_path):
    asyncio.run(_set_command_from_search(tmp_path))


def test_editor_saves_value(tmp_path):
    asyncio.run(_editor_saves_value(tmp_path))
