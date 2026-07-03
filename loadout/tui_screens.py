"""Modal screens for the Loadout TUI."""

from __future__ import annotations

from textual import on
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Input, Label, Static

from loadout import __version__
from loadout.models import Action
from loadout.tui_theme import (
    COLOR_ACCENT,
    COLOR_DIM,
    COLOR_PRIMARY,
    COLOR_SECONDARY,
    COLOR_SUCCESS,
)


class ConfirmDestructive(ModalScreen[bool]):
    """Confirm before copying a potentially destructive command."""

    DEFAULT_CSS = """
    ConfirmDestructive {
        align: center middle;
    }
    #confirm-dialog {
        width: 76;
        height: auto;
        border: thick #FF6B6B;
        background: #1f2335;
        padding: 1 2;
    }
    #confirm-cmd {
        margin: 1 0;
        padding: 1;
        background: #16161e;
        border-left: tall #FF6B6B;
    }
    """

    BINDINGS = [
        Binding("escape", "deny", "Cancel", show=False),
        Binding("enter", "confirm", "Copy", show=False),
        Binding("y", "confirm", "Yes", show=False),
        Binding("n", "deny", "No", show=False),
    ]

    def __init__(self, command_markup: str) -> None:
        super().__init__()
        self._command_markup = command_markup

    def compose(self) -> ComposeResult:
        with Vertical(id="confirm-dialog"):
            yield Label(f"[{COLOR_PRIMARY} bold]⚠ Destructive command[/]", markup=True)
            yield Static(self._command_markup, id="confirm-cmd", markup=True)
            yield Static(
                f"[{COLOR_DIM}]Enter/Y copy · Esc/N cancel[/]",
                markup=True,
            )
            with Horizontal():
                yield Button("Copy [Enter]", variant="error", id="yes")
                yield Button("Cancel [Esc]", id="no")

    def action_confirm(self) -> None:
        self.dismiss(True)

    def action_deny(self) -> None:
        self.dismiss(False)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "yes")


class ConfirmRun(ModalScreen[bool]):
    """Confirm before running a command in the shell."""

    DEFAULT_CSS = """
    ConfirmRun {
        align: center middle;
    }
    #run-dialog {
        width: 76;
        height: auto;
        border: thick #4ECDC4;
        background: #1f2335;
        padding: 1 2;
    }
    #run-cmd {
        margin: 1 0;
        padding: 1;
        background: #16161e;
        border-left: tall #4ECDC4;
    }
    """

    BINDINGS = [
        Binding("escape", "deny", "Cancel", show=False),
        Binding("enter", "confirm", "Run", show=False),
        Binding("y", "confirm", "Yes", show=False),
        Binding("n", "deny", "No", show=False),
    ]

    def __init__(self, command_markup: str, *, destructive: bool = False) -> None:
        super().__init__()
        self._command_markup = command_markup
        self._destructive = destructive

    def compose(self) -> ComposeResult:
        title = (
            f"[{COLOR_PRIMARY} bold]⚠ Run destructive command[/]"
            if self._destructive
            else f"[{COLOR_ACCENT} bold]▶ Run in shell[/]"
        )
        with Vertical(id="run-dialog"):
            yield Label(title, markup=True)
            yield Static(self._command_markup, id="run-cmd", markup=True)
            yield Static(
                f"[{COLOR_DIM}]Enter/Y run · Esc/N cancel[/]",
                markup=True,
            )
            with Horizontal():
                yield Button("Run [Enter]", variant="error" if self._destructive else "primary", id="yes")
                yield Button("Cancel [Esc]", id="no")

    def action_confirm(self) -> None:
        self.dismiss(True)

    def action_deny(self) -> None:
        self.dismiss(False)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "yes")


class PlaceholderForm(ModalScreen[dict[str, str] | None]):
    """Prompt for missing {{var}} values."""

    DEFAULT_CSS = """
    PlaceholderForm {
        align: center middle;
    }
    #form-dialog {
        width: 66;
        height: auto;
        border: thick #4ECDC4;
        background: #1f2335;
        padding: 1 2;
    }
    .var-label {
        margin-top: 1;
        color: #4ECDC4;
        text-style: bold;
    }
    .var-input {
        margin-bottom: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "cancel", "Cancel", show=False),
    ]

    def __init__(self, placeholders: list[str], existing: dict[str, str]) -> None:
        super().__init__()
        self._names = placeholders
        self._existing = existing

    def compose(self) -> ComposeResult:
        with Vertical(id="form-dialog"):
            yield Label(f"[{COLOR_SECONDARY} bold]Missing variables[/]", markup=True)
            yield Static(
                f"[{COLOR_DIM}]Tab/↓ next field · Enter apply · Esc cancel[/]",
                markup=True,
            )
            for name in self._names:
                value = self._existing.get(name, "")
                yield Label(name, classes="var-label")
                yield Input(value=value, placeholder=name, id=f"var-{name}", classes="var-input")
            with Horizontal():
                yield Button("Apply [Enter]", variant="primary", id="ok")
                yield Button("Cancel [Esc]", id="no")

    def on_mount(self) -> None:
        if self._names:
            self.query_one(f"#var-{self._names[0]}", Input).focus()

    def action_cancel(self) -> None:
        self.dismiss(None)

    def action_submit(self) -> None:
        values = {name: self.query_one(f"#var-{name}", Input).value for name in self._names}
        self.dismiss(values)

    @on(Input.Submitted)
    def on_input_submitted(self, event: Input.Submitted) -> None:
        if not event.input.classes or "var-input" not in event.input.classes:
            return
        current_idx = self._names.index(event.input.id.removeprefix("var-"))
        if current_idx < len(self._names) - 1:
            next_name = self._names[current_idx + 1]
            self.query_one(f"#var-{next_name}", Input).focus()
        else:
            self.action_submit()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "ok":
            self.action_submit()
        else:
            self.action_cancel()


class VariablesScreen(ModalScreen[None]):
    """Show all session variables."""

    DEFAULT_CSS = """
    VariablesScreen {
        align: center middle;
    }
    #vars-dialog {
        width: 74;
        height: 22;
        border: thick #FFE66D;
        background: #1f2335;
        padding: 1 2;
    }
    #vars-table {
        height: 1fr;
    }
    DataTable {
        background: #16161e;
    }
    """

    BINDINGS = [
        Binding("escape", "close", "Close", show=False),
        Binding("enter", "close", "Close", show=False),
        Binding("q", "close", "Close", show=False),
    ]

    def __init__(self, variables: dict[str, str], user_keys: set[str]) -> None:
        super().__init__()
        self._variables = variables
        self._user_keys = user_keys

    def compose(self) -> ComposeResult:
        with Vertical(id="vars-dialog"):
            yield Label(f"[{COLOR_ACCENT} bold]🌐 Global variables[/]", markup=True)
            yield DataTable(id="vars-table", zebra_stripes=True, cursor_type="row")
            yield Static(f"[{COLOR_DIM}]↑↓ browse · Enter/Esc close[/]", markup=True)

    def on_mount(self) -> None:
        table = self.query_one("#vars-table", DataTable)
        table.focus()
        table.add_columns("Key", "Value", "Source")
        for key in sorted(self._variables):
            source = "user" if key in self._user_keys else "default"
            table.add_row(key, self._variables[key], source)

    def action_close(self) -> None:
        self.dismiss(None)


class ToolsScreen(ModalScreen[str | None]):
    """Grouped tool listing; dismisses with selected tool filter or None."""

    DEFAULT_CSS = """
    ToolsScreen {
        align: center middle;
    }
    #tools-dialog {
        width: 76;
        height: 24;
        border: thick #4ECDC4;
        background: #1f2335;
        padding: 1 2;
    }
    #tools-table {
        height: 1fr;
    }
    """

    BINDINGS = [
        Binding("escape", "close", "Close", show=False),
        Binding("enter", "filter_selected", "Filter", show=False),
        Binding("f", "filter_selected", "Filter", show=False),
    ]

    def __init__(self, actions: list[Action]) -> None:
        super().__init__()
        self._actions = actions
        self._tools: list[str] = []

    @staticmethod
    def _category_name(action: Action) -> str:
        raw = action.source_file.parent.name
        if "-" in raw:
            _, _, raw = raw.partition("-")
        return raw.replace("_", " ").title()

    def compose(self) -> ComposeResult:
        with Vertical(id="tools-dialog"):
            yield Label(
                f"[{COLOR_SECONDARY} bold]📊 Tools by category[/]",
                markup=True,
            )
            yield DataTable(id="tools-table", zebra_stripes=True, cursor_type="row")
            yield Static(
                f"[{COLOR_DIM}]↑↓ navigate · Enter/F filter · Esc close[/]",
                markup=True,
            )

    def on_mount(self) -> None:
        grouped: dict[str, list[Action]] = {}
        for action in self._actions:
            grouped.setdefault(action.tool, []).append(action)

        category_tools: dict[str, list[str]] = {}
        for tool, actions in grouped.items():
            category = self._category_name(actions[0])
            category_tools.setdefault(category, []).append(tool)

        table = self.query_one("#tools-table", DataTable)
        table.add_columns("Category", "Tool", "Actions", "Tags")
        self._tools = []
        for category in sorted(category_tools):
            for tool in sorted(category_tools[category]):
                sample = grouped[tool][0]
                tags = " ".join(f"#{t}" for t in sample.tags) if sample.tags else "—"
                table.add_row(category, tool, str(len(grouped[tool])), tags)
                self._tools.append(tool)
        table.focus()

    def action_close(self) -> None:
        self.dismiss(None)

    def action_filter_selected(self) -> None:
        table = self.query_one("#tools-table", DataTable)
        if table.cursor_row is not None and table.cursor_row < len(self._tools):
            self.dismiss(f"tool:{self._tools[table.cursor_row]}")
        else:
            self.dismiss(None)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        if event.data_table.id == "tools-table":
            self.action_filter_selected()


class HelpScreen(ModalScreen[None]):
    """Keyboard shortcuts and special commands."""

    DEFAULT_CSS = """
    HelpScreen {
        align: center middle;
    }
    #help-dialog {
        width: 80;
        height: 28;
        border: thick #AA96DA;
        background: #1f2335;
        padding: 1 2;
    }
    #help-body {
        height: 1fr;
    }
    """

    BINDINGS = [
        Binding("escape", "close", "Close", show=False),
        Binding("enter", "close", "Close", show=False),
        Binding("q", "close", "Close", show=False),
    ]

    HELP_TEXT = f"""\
[{COLOR_PRIMARY} bold]◆ LOADOUT[/] [{COLOR_DIM}]v{__version__}[/] — keyboard-first

[{COLOR_SECONDARY} bold]Layout[/]
  [{COLOR_ACCENT}]Top[/]                    Search bar (always available)
  [{COLOR_ACCENT}]Left[/]                   Category → Tool → Command list
  [{COLOR_ACCENT}]Right[/]                  Details for highlighted item
  [{COLOR_ACCENT}][ / ][/]                  Narrow / widen list pane
  Resize terminal window to reflow layout

[{COLOR_SECONDARY} bold]Browse[/] (empty search)
  [{COLOR_ACCENT}]Categories[/] → [{COLOR_ACCENT}]Tools[/] → [{COLOR_ACCENT}]Commands[/]
  [{COLOR_ACCENT}]Enter[/]                  Run command (or drill down in browse)
  [{COLOR_ACCENT}]r[/]                       Run in subterminal (same as Enter on command)
  [{COLOR_ACCENT}]Esc[/]                    Back one level (or quit)
  [{COLOR_ACCENT}]Ctrl+T[/]                 Jump to categories

[{COLOR_SECONDARY} bold]Detail panel[/]
  [{COLOR_ACCENT}]Copy[/] / [{COLOR_ACCENT}]Print[/]   Copy or print command
  [{COLOR_ACCENT}]Run[/]                  Launch subterminal immediately

  [{COLOR_ACCENT}]↑/↓[/] or [{COLOR_ACCENT}]Ctrl+P/N[/]   Move selection (even while searching)
  [{COLOR_ACCENT}]PgUp/PgDn[/]              Page through results
  [{COLOR_ACCENT}]j/k[/]                    Move (when list focused)
  [{COLOR_ACCENT}]/[/] or [{COLOR_ACCENT}]Ctrl+F[/]        Focus search
  [{COLOR_ACCENT}]Tab[/]                    Search ↔ list pane

[{COLOR_SECONDARY} bold]Shortcuts[/]
  [{COLOR_ACCENT}]?[/] help   [{COLOR_ACCENT}]v[/] vars   [{COLOR_ACCENT}]Ctrl+T[/] browse   [{COLOR_ACCENT}]Ctrl+R[/] reload

[{COLOR_SECONDARY} bold]Search[/] (top bar — focused on launch)
  text              Fuzzy match tool, title, tag, command
  [{COLOR_ACCENT}]tag:recon[/] / [{COLOR_ACCENT}]#recon[/]   Filter tag
  [{COLOR_ACCENT}]tool:nmap[/]            Filter tool
  [{COLOR_ACCENT}]Enter[/]                  Run selected result
  [{COLOR_ACCENT}]Esc[/]                    Clear search → browse
  [{COLOR_ACCENT}]Tab[/]                    Switch search ↔ list

[{COLOR_SECONDARY} bold]Special commands[/] (search + Enter)
  [{COLOR_SUCCESS}]set ip=10.0.0.1[/]  [{COLOR_SUCCESS}]unset ip[/]
  [{COLOR_SUCCESS}]variables[/]  [{COLOR_SUCCESS}]tools[/] (→ categories)  [{COLOR_SUCCESS}]reload[/]
  [{COLOR_SUCCESS}]output print[/]  [{COLOR_SUCCESS}]output clipboard[/]
"""

    def compose(self) -> ComposeResult:
        with Vertical(id="help-dialog"):
            yield Label(f"[{COLOR_ACCENT} bold]❓ Help[/]", markup=True)
            with VerticalScroll(id="help-body"):
                yield Static(self.HELP_TEXT, markup=True)
            yield Static(f"[{COLOR_DIM}]Enter / Esc / q to close[/]", markup=True)

    def action_close(self) -> None:
        self.dismiss(None)
