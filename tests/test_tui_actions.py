"""TUI detail panel action button tests."""

import asyncio

from loadout.config import LoadoutConfig
from loadout.models import OutputMode
from loadout.tui import LoadoutApp
from loadout.variables import VariableStore


async def _action_buttons_on_command() -> None:
    config = LoadoutConfig.load()
    config.output_mode = OutputMode.PRINT
    app = LoadoutApp(config, VariableStore(defaults=config.default_vars))
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        await pilot.press("enter", "enter")
        await pilot.pause()
        assert app._browse_level == "command"
        actions = app.query_one("#info-actions")
        assert "visible" in actions.classes
        copy_btn = app.query_one("#copy-btn")
        assert "Print" in str(copy_btn.render())
        assert app.query_one("#run-btn") is not None


async def _action_buttons_hidden_on_category() -> None:
    config = LoadoutConfig.load()
    config.output_mode = OutputMode.PRINT
    app = LoadoutApp(config, VariableStore(defaults=config.default_vars))
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        actions = app.query_one("#info-actions")
        assert "visible" not in actions.classes


def test_action_buttons_visible_for_command():
    asyncio.run(_action_buttons_on_command())


def test_action_buttons_hidden_for_category():
    asyncio.run(_action_buttons_hidden_on_category())


async def _copy_shortcut_from_list() -> None:
    config = LoadoutConfig.load()
    config.output_mode = OutputMode.PRINT
    app = LoadoutApp(config, VariableStore(defaults=config.default_vars))
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        await pilot.press("enter", "enter", "tab")
        await pilot.pause()
        assert app._selected is not None
        copy_btn = app.query_one("#copy-btn")
        assert "Print" in str(copy_btn.render())
        run_btn = app.query_one("#run-btn")
        assert "Run" in str(run_btn.render())
        assert "[c]" in app._action_chip("Print", bg="#4ECDC4", shortcut="c")
        assert "[r]" in app._action_chip("Run", bg="#7aa2f7", shortcut="r")


def test_copy_shortcut_shown_on_command():
    asyncio.run(_copy_shortcut_from_list())
