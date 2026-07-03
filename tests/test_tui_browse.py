"""TUI browse interaction tests."""

import asyncio

from loadout.config import LoadoutConfig
from loadout.models import OutputMode
from loadout.tui import LoadoutApp
from loadout.variables import VariableStore


async def _browse_three_levels() -> None:
    config = LoadoutConfig.load()
    config.output_mode = OutputMode.PRINT
    app = LoadoutApp(config, VariableStore(defaults=config.default_vars))
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        assert app._browse_level == "category"
        await pilot.press("enter")
        await pilot.pause()
        assert app._browse_level == "tool"
        assert app._selected_category is not None
        await pilot.press("enter")
        await pilot.pause()
        assert app._browse_level == "command"
        assert app._selected_tool is not None


async def _resize_terminal() -> None:
    config = LoadoutConfig.load()
    config.output_mode = OutputMode.PRINT
    app = LoadoutApp(config, VariableStore(defaults=config.default_vars))
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        await pilot.resize_terminal(70, 24)
        await pilot.pause()
        assert app._stack_panes is True
        await pilot.resize_terminal(120, 40)
        await pilot.pause()
        assert app._stack_panes is False


async def _search_on_launch() -> None:
    config = LoadoutConfig.load()
    config.output_mode = OutputMode.PRINT
    app = LoadoutApp(config, VariableStore(defaults=config.default_vars))
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        assert getattr(app.focused, "id", None) == "search"
        stats = app.query_one("#stats-bar")
        keys = app.query_one("#keys-bar")
        assert "tools" in str(stats.render())
        assert "45" in str(stats.render()) or "47" in str(stats.render())
        assert "quit" in str(keys.render())
        assert keys.region.y == stats.region.y + 1
        assert keys.region.y == app.size.height - 1
        await pilot.press("t", "o", "o", "l", ":", "n", "m", "a", "p")
        await pilot.pause()
        assert app._mode == "search"
        assert app.query_one("#search").value == "tool:nmap"
        assert len(app.ranked) > 0
        assert all(r.action.tool == "nmap" for r in app.ranked)


def test_search_focused_on_launch():
    asyncio.run(_search_on_launch())


def test_enter_drills_category_tool_command():
    asyncio.run(_browse_three_levels())


def test_terminal_resize_reflows_layout():
    asyncio.run(_resize_terminal())
