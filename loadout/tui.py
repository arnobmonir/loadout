"""Textual TUI — persistent command launcher (arsenal-ng inspired)."""

from __future__ import annotations

from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, ScrollableContainer, Vertical
from textual.events import Click, Resize
from textual.widgets import Input, Label, ListItem, ListView, Static
from rich.markup import escape as markup_escape

from loadout import __version__
from loadout.browse import BrowseRow, build_browse_tree, rows_for_level
from loadout.categories import CategoryInfo, category_info_for, load_category_info, manifest_category_slugs
from loadout.config import LoadoutConfig
from loadout.guard import is_destructive
from loadout.loader import load_cheats
from loadout.models import Action, OutputMode
from loadout.output import clipboard_error, deliver, launch_command
from loadout.pack_stats import PackStats, collect_pack_stats
from loadout.search import RankedAction, parse_search_query, rank_actions
from loadout.substitute import parse_placeholders, substitute
from loadout.tui_hints import hint_for_query
from loadout.tui_screens import (
    ConfirmDestructive,
    HelpScreen,
    PlaceholderForm,
    VariablesScreen,
)
from loadout.tui_theme import (
    COLOR_ACCENT,
    COLOR_BRIGHT,
    COLOR_DESC,
    COLOR_DIM,
    COLOR_PRIMARY,
    COLOR_SECONDARY,
    COLOR_SUCCESS,
    highlight_command,
    highlight_match,
    render_header_line,
    render_stats_bar,
    render_tags,
    tool_color,
)
from loadout.variables import VariableStore


class LoadoutApp(App[None]):
    """Arsenal-ng style vertical layout with info box and syntax highlighting."""

    TITLE = "Loadout"
    SUB_TITLE = "pentest command launcher"

    CSS = """
    Screen {
        background: #1a1b26;
    }

    #header-strip {
        dock: top;
        height: 1;
        padding: 0 1;
        background: #24283b;
        color: #c0caf5;
    }

    #search-row {
        dock: top;
        height: 3;
        padding: 0 1;
        background: #24283b;
        border-bottom: solid #3b4261;
    }

    #search-prompt {
        width: 2;
        content-align: center middle;
        color: #4ECDC4;
        text-style: bold;
    }

    #search {
        width: 1fr;
    }

    #hints-panel {
        dock: top;
        height: auto;
        max-height: 6;
        margin: 0 1;
        padding: 0 1;
        background: #1f2335;
        border: round #6A0572;
        display: none;
    }

    #hints-panel.visible {
        display: block;
    }

    #content-split {
        height: 1fr;
        margin: 0 1 1 1;
    }

    #left-pane {
        width: 45%;
        min-width: 16;
        border: solid #3b4261;
        background: #1a1b26;
    }

    #browse-path {
        height: 1;
        padding: 0 1;
        background: #24283b;
        color: #7aa2f7;
        text-style: bold;
    }

    #results {
        height: 1fr;
        min-height: 4;
        background: #1a1b26;
    }

    #right-pane {
        width: 1fr;
        min-width: 16;
        border: solid #4ECDC4;
        background: #1f2335;
    }

    #info-box {
        height: 1fr;
        padding: 1 2;
    }

    #info-title {
        text-style: bold;
        color: #FF6B6B;
    }

    #info-desc {
        color: #888888;
        text-style: italic;
        margin-top: 1;
    }

    #info-tags {
        margin: 1 0 0 0;
    }

    #info-command-row {
        margin-top: 1;
        height: auto;
        align: left top;
    }

    #info-command {
        width: 1fr;
        padding: 0 1;
        background: #16161e;
        border-left: tall #BB8FCE;
    }

    #info-hint {
        color: #FFE66D;
        margin-top: 1;
    }

    #info-actions {
        width: auto;
        height: 1;
        display: none;
    }

    #info-actions.visible {
        display: block;
    }

    .info-action {
        width: auto;
        height: 1;
        margin-left: 1;
        content-align: center middle;
    }

    .info-action:hover {
        text-style: bold;
    }

    ListItem {
        padding: 0 1;
    }

    ListItem.-highlight {
        background: #3D3D3D;
    }

    #bottom-panel {
        dock: bottom;
        height: 2;
        width: 100%;
        layout: vertical;
    }

    #stats-bar {
        height: 1;
        padding: 0 1;
        background: #1f2335;
        color: #4ECDC4;
        text-style: bold;
        border-top: solid #4ECDC4;
    }

    #keys-bar {
        height: 1;
        padding: 0 1;
        background: #16161e;
        color: #c0caf5;
    }

    .study-mode #info-command-row {
        display: none;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("escape", "go_back", "Back"),
        Binding("slash", "focus_search", "Search", show=False),
        Binding("ctrl+f", "focus_search", "Search", show=False),
        Binding("question_mark", "show_help", "Help"),
        Binding("v", "show_variables", "Vars", show=False),
        Binding("ctrl+t", "browse_categories", "Browse"),
        Binding("ctrl+r", "reload", "Reload"),
        Binding("tab", "toggle_focus", "Toggle", priority=True, show=False),
        # Navigate list from anywhere (priority over search input)
        Binding("down", "cursor_down", "Down", priority=True, show=False),
        Binding("up", "cursor_up", "Up", priority=True, show=False),
        Binding("ctrl+n", "cursor_down", "Down", priority=True, show=False),
        Binding("ctrl+p", "cursor_up", "Up", priority=True, show=False),
        Binding("page_down", "page_down", "PgDn", priority=True, show=False),
        Binding("page_up", "page_up", "PgUp", priority=True, show=False),
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
        Binding("[", "shrink_left_pane", "List -", show=False),
        Binding("]", "grow_left_pane", "List +", show=False),
    ]

    def __init__(
        self,
        config: LoadoutConfig,
        var_store: VariableStore,
        *,
        tag_filter: str | None = None,
        tool_filter: str | None = None,
        study_mode: bool = False,
    ) -> None:
        super().__init__()
        self.config = config
        self.var_store = var_store
        self._cli_tag = tag_filter
        self._cli_tool = tool_filter
        self.study_mode = study_mode
        self.actions: list[Action] = []
        self.ranked: list[RankedAction] = []
        self._selected: Action | None = None
        self._mode: str = "browse"  # browse | search
        self._browse_level: str = "category"  # category | tool | command
        self._selected_category: str | None = None
        self._selected_tool: str | None = None
        self._browse_tree: dict[str, dict[str, list[Action]]] = {}
        self._category_sort: dict[str, str] = {}
        self._browse_rows: list[BrowseRow] = []
        self._left_pane_ratio = 0.45
        self._stack_panes = False
        self._pack_stats: PackStats | None = None
        self._category_info: dict[str, CategoryInfo] = {}
        self._manifest_slugs: tuple[str, ...] = ()
        self._stats_markup = ""
        self._hint_markup = (
            f"[{COLOR_SUCCESS}]●[/] Ready — "
            f"[{COLOR_DIM}]Enter select · Esc back · / search[/]"
        )
        self._keys_markup = (
            "[dim]q[/] quit  [dim]esc[/] back  [dim]enter[/] run  "
            "[dim]?[/] help  [dim]^t[/] browse  [dim]^r[/] reload  [dim]v[/] vars"
        )

    def compose(self) -> ComposeResult:
        yield Static("", id="header-strip", markup=True)
        with Horizontal(id="search-row"):
            yield Static("❯", id="search-prompt")
            yield Input(
                placeholder="Search tool, tag, command · tag:recon · tool:nmap · empty = browse",
                id="search",
            )
        yield Static("", id="hints-panel", markup=True)
        with Horizontal(id="content-split"):
            with Vertical(id="left-pane"):
                yield Static("Categories", id="browse-path", markup=True)
                yield ListView(id="results")
            with Vertical(id="right-pane"):
                with ScrollableContainer(id="info-box", can_focus=False):
                    yield Static("", id="info-title", markup=True)
                    yield Static("", id="info-desc", markup=True)
                    yield Static("", id="info-tags", markup=True)
                    with Horizontal(id="info-command-row"):
                        yield Static("", id="info-command", markup=True)
                        with Horizontal(id="info-actions"):
                            yield Static("", id="copy-btn", markup=True, classes="info-action")
                            yield Static("", id="run-btn", markup=True, classes="info-action")
                    yield Static("", id="info-hint", markup=True)
        with Vertical(id="bottom-panel"):
            yield Static("", id="stats-bar", markup=True)
            yield Static("", id="keys-bar", markup=True)

    def on_mount(self) -> None:
        if self.study_mode:
            self.add_class("study-mode")
        self._apply_output_fallback()
        self.reload_actions()
        self._apply_layout()
        self.action_focus_search()

    def _search_input(self) -> Input:
        return self.query_one("#search", Input)

    @on(Resize)
    def on_resize(self, event: Resize) -> None:
        """Reflow panes when the terminal window is resized."""
        self._apply_layout(width=event.size.width)
        if not self._item_count():
            return
        idx = self._current_index()
        if self._mode == "search":
            self._rehighlight_rows(idx)
        else:
            self._rehighlight_browse_rows(idx)

    def _apply_layout(self, *, width: int | None = None) -> None:
        """Adapt split-pane layout to the current terminal size."""
        split = self.query_one("#content-split")
        left = self.query_one("#left-pane")
        right = self.query_one("#right-pane")
        terminal_width = width if width is not None else self.size.width
        stacked = terminal_width < 85
        self._stack_panes = stacked
        ratio_pct = int(self._left_pane_ratio * 100)

        if stacked:
            split.styles.layout = "vertical"
            left.styles.width = "100%"
            right.styles.width = "100%"
            left.styles.height = f"{ratio_pct}%"
            right.styles.height = "1fr"
        else:
            split.styles.layout = "horizontal"
            left.styles.width = f"{ratio_pct}%"
            right.styles.width = "1fr"
            left.styles.height = "1fr"
            right.styles.height = "1fr"

    def _rebuild_browse_tree(self) -> None:
        self._browse_tree, self._category_sort = build_browse_tree(self.actions)

    def _apply_output_fallback(self) -> None:
        """Avoid noisy clipboard failures in headless/terminal-only environments."""
        if self.config.output_mode != OutputMode.CLIPBOARD:
            return

        error = clipboard_error()
        if error is None:
            return

        self.config.output_mode = OutputMode.PRINT

    def reload_actions(self) -> None:
        self._category_info = load_category_info()
        self._manifest_slugs = manifest_category_slugs()
        self.actions = load_cheats(self.config.all_cheat_paths())
        if self._cli_tool:
            self.actions = [a for a in self.actions if a.tool == self._cli_tool]
        if self._cli_tag:
            self.actions = [a for a in self.actions if self._cli_tag in a.tags]
        self._pack_stats = collect_pack_stats(
            self.actions,
            cheat_paths=self.config.all_cheat_paths(),
        )
        self._rebuild_browse_tree()
        self._apply_cli_browse_filters()
        self._update_pack_stats()
        self._refresh_display(self.query_one("#search", Input).value)

    def _update_pack_stats(self) -> None:
        stats = self._pack_stats
        if stats is None:
            return
        var_count = len(self.var_store.list_user())
        line = render_stats_bar(
            tool_count=stats.tool_count,
            command_count=stats.command_count,
            category_count=stats.category_count,
            tag_count=stats.tag_count,
            cheat_file_count=stats.cheat_file_count,
            user_cheat_file_count=stats.user_cheat_file_count,
            pack_version=stats.pack_version,
            updated_label=stats.updated_label,
            var_count=var_count,
        )
        self._stats_markup = line
        self._refresh_bottom_bar()

    def _refresh_bottom_bar(self) -> None:
        stats = self._stats_markup or f"[{COLOR_DIM}]Loading pack stats…[/]"
        keys_bar = (
            f"{self._hint_markup}  "
            f"[{COLOR_DIM}]│[/]  "
            f"{self._keys_markup}"
        )
        self.query_one("#stats-bar", Static).update(stats)
        self.query_one("#keys-bar", Static).update(keys_bar)

    def _apply_cli_browse_filters(self) -> None:
        """Jump browse view when launched with --tool."""
        if not self._cli_tool:
            return
        for cat, tools in self._browse_tree.items():
            if self._cli_tool in tools:
                self._selected_category = cat
                self._selected_tool = self._cli_tool
                self._browse_level = "command"
                return

    def _update_header(self, tool_count: int, cmd_count: int) -> None:
        var_count = len(self.var_store.list_user())
        line = render_header_line(
            version=__version__,
            tool_count=tool_count,
            cmd_count=cmd_count,
            var_count=var_count,
            output_mode=self.config.output_mode.value,
            study=self.study_mode,
        )
        self.query_one("#header-strip", Static).update(line)
        self._update_pack_stats()

    def _truncate_desc(self, desc: str, max_len: int = 44) -> str:
        text = desc.strip()
        if len(text) <= max_len:
            return text
        return f"{text[: max_len - 1]}…"

    def _row_description(self, action: Action) -> str:
        if self.study_mode:
            return action.exam_hint or action.desc
        return action.desc

    def _format_desc_suffix(self, desc: str, *, max_len: int = 44) -> str:
        text = self._truncate_desc(desc, max_len)
        if not text:
            return ""
        return f"  [{COLOR_DIM}]{markup_escape(text)}[/]"

    def _format_list_row(self, action: Action, query_text: str, *, selected: bool) -> str:
        tc = tool_color(action.tool)
        tool = f"[{tc} bold]{action.tool:12}[/]"
        title = highlight_match(action.title, query_text) if query_text else action.title

        if selected:
            title_part = f"[#FFFFFF bold on #3D3D3D] {title:28} [/]"
        else:
            title_part = f" {title:28} "

        desc = self._format_desc_suffix(self._row_description(action), max_len=36)
        return f"▸ {tool} {title_part}{desc}"

    def _format_browse_row(self, row: BrowseRow, *, selected: bool) -> str:
        marker = "▸" if selected else " "
        if row.level == "category":
            if selected:
                return (
                    f"{marker} [#FFFFFF bold on #3D3D3D] {row.label} [/]  "
                    f"[{COLOR_DIM}]{row.tool_count} tools · {row.command_count} cmds[/]"
                )
            return (
                f"{marker} [{COLOR_SECONDARY} bold]{row.label}[/]  "
                f"[{COLOR_DIM}]{row.tool_count} tools · {row.command_count} cmds[/]"
            )
        if row.level == "tool":
            if selected:
                return (
                    f"{marker} [#FFFFFF bold on #3D3D3D] {row.label} [/]  "
                    f"[{COLOR_DIM}]{row.command_count} cmds[/]"
                )
            tc = tool_color(row.label)
            return (
                f"{marker} [{tc} bold]{row.label}[/]  "
                f"[{COLOR_DIM}]{row.command_count} cmds[/]"
            )
        # command level
        title = row.label
        if selected:
            title = f"[#FFFFFF bold on #3D3D3D] {title} [/]"
        else:
            title = f" {title} "
        desc = ""
        if row.action:
            desc = self._format_desc_suffix(self._row_description(row.action))
        return f"{marker} {title}{desc}"

    def _category_meta(self, category: str) -> CategoryInfo:
        return category_info_for(category, self._category_info)

    def _tool_overview(self, actions: list[Action]) -> str:
        descriptions = [action.desc.strip() for action in actions if action.desc.strip()]
        if descriptions:
            return descriptions[0]
        return "Browse commands below to pick the action that matches your target and scope."

    def _format_tool_docs(self, docs: tuple[str, ...]) -> str:
        if not docs:
            return ""
        joined = "  ".join(markup_escape(doc) for doc in docs[:3])
        return f"[{COLOR_DIM}]Docs:[/] {joined}"

    def _show_browse_detail(self, row: BrowseRow) -> None:
        if row.level == "category":
            meta = self._category_meta(row.label)
            self._clear_detail()
            self.query_one("#info-title", Static).update(
                f"[{COLOR_SECONDARY} bold]📁 {row.label}[/]"
            )
            description = meta.description or "Browse the tools in this category."
            self.query_one("#info-desc", Static).update(
                f"[{COLOR_DESC}]{description}[/]"
            )
            self.query_one("#info-tags", Static).update(
                f"[{COLOR_DIM}]{row.tool_count} tools · {row.command_count} commands[/]"
            )
            self.query_one("#info-command", Static).update(
                f"[{COLOR_DIM}]Press Enter to browse tools in this category[/]"
            )
            self.query_one("#info-hint", Static).update(
                f"[{COLOR_ACCENT}]📖 Strategy:[/] {meta.strategy}"
            )
            return

        if row.level == "tool" and row.category and row.tool:
            actions = self._browse_tree[row.category][row.tool]
            sample = actions[0]
            tc = tool_color(row.tool)
            self.query_one("#info-title", Static).update(
                f"[{tc} bold]{row.tool}[/]  [{COLOR_PRIMARY} bold]›[/]  "
                f"[{COLOR_BRIGHT}]{row.category}[/]"
            )
            self.query_one("#info-desc", Static).update(
                f"[{COLOR_DESC}]{row.command_count} commands available[/]"
            )
            overview = self._tool_overview(actions)
            tags = render_tags(sample.tags)
            docs = self._format_tool_docs(sample.docs)
            if tags and docs:
                self.query_one("#info-tags", Static).update(f"{tags}\n{docs}")
            else:
                self.query_one("#info-tags", Static).update(tags or docs)
            self.query_one("#info-command", Static).update(
                f"[{COLOR_DIM}]Overview:[/] {overview}"
            )
            hint = sample.exam_hint or self._category_meta(row.category).strategy
            self.query_one("#info-hint", Static).update(
                f"[{COLOR_ACCENT}]📖 Strategy:[/] {hint}" if hint else ""
            )
            return

        if row.level == "command" and row.action:
            self._show_detail(row.action)

    def _refresh_display(self, raw_query: str) -> None:
        query = parse_search_query(raw_query)
        list_view = self.query_one("#results", ListView)
        hints = self.query_one("#hints-panel", Static)
        search = self._search_input()
        preserve_search_focus = (
            getattr(self.focused, "id", None) == "search" or bool(raw_query.strip())
        )
        try:
            list_view.clear()
            self.ranked = []
            self._browse_rows = []

            hint_markup = hint_for_query(raw_query)
            if hint_markup:
                hints.update(hint_markup)
                hints.add_class("visible")
            else:
                hints.remove_class("visible")
                hints.update("")

            if raw_query.strip().lower().startswith("set ") and "=" in raw_query:
                self._set_status("Press Enter to apply variable")
                return

            # Search mode when user types (not empty, not a special-only hint)
            if raw_query.strip() and not hint_markup:
                self._mode = "search"
                self.ranked = rank_actions(self.actions, query)
                tool_count = len({r.action.tool for r in self.ranked})
                self._update_header(tool_count, len(self.ranked))
                self._update_browse_path(search_query=raw_query)

                for i, ranked in enumerate(self.ranked):
                    line = self._format_list_row(
                        ranked.action,
                        query.text,
                        selected=(i == 0),
                    )
                    list_view.append(ListItem(Label(line, markup=True)))

                if self.ranked:
                    list_view.index = 0
                    self._show_detail(self.ranked[0].action)
                    self._set_status(
                        f"[{COLOR_SUCCESS}]●[/] Search: {len(self.ranked)} match(es) — "
                        f"[{COLOR_DIM}]Esc clears · Enter run[/]"
                    )
                else:
                    self._clear_detail()
                    self._set_status(f"[{COLOR_ACCENT}]No matches[/] for '{raw_query.strip()}'")
                return

            # Browse mode: category → tool → command
            self._mode = "browse"
            self._browse_rows = rows_for_level(
                self._browse_tree,
                self._category_sort,
                level=self._browse_level,
                category=self._selected_category,
                tool=self._selected_tool,
                manifest_slugs=self._manifest_slugs,
            )

            tool_count = len({a.tool for a in self.actions})
            self._update_header(tool_count, len(self.actions))
            self._update_browse_path()

            for i, row in enumerate(self._browse_rows):
                line = self._format_browse_row(row, selected=(i == 0))
                list_view.append(ListItem(Label(line, markup=True)))

            if self._browse_rows:
                list_view.index = 0
                self._show_browse_detail(self._browse_rows[0])
                breadcrumb = self._browse_breadcrumb()
                self._set_status(
                    f"[{COLOR_SUCCESS}]●[/] {breadcrumb} — "
                    f"[{COLOR_DIM}]Enter select · Esc back[/]"
                )
            else:
                self._clear_detail()
                self._set_status(f"[{COLOR_ACCENT}]No items at this level[/]")
        finally:
            if preserve_search_focus:
                search.focus()

    def _browse_breadcrumb(self) -> str:
        if self._browse_level == "category":
            return "Categories"
        if self._browse_level == "tool":
            return f"{self._selected_category} › Tools"
        return f"{self._selected_category} › {self._selected_tool} › Commands"

    def _update_browse_path(self, *, search_query: str = "") -> None:
        path = self.query_one("#browse-path", Static)
        if search_query.strip():
            path.update(f"[{COLOR_ACCENT}]Search results[/]")
            return
        breadcrumb = self._browse_breadcrumb()
        path.update(f"[{COLOR_SECONDARY}]{breadcrumb}[/]")

    def _preview_command(self, action: Action) -> str:
        return substitute(action.command, self.var_store.as_substitution_map()).command

    def _action_chip(self, label: str, *, bg: str) -> str:
        return f"[#1a1b26 on {bg}] {label} [/]"

    def _update_action_buttons(self, visible: bool) -> None:
        actions = self.query_one("#info-actions", Horizontal)
        if visible and not self.study_mode:
            copy_label = "Copy" if self.config.output_mode == OutputMode.CLIPBOARD else "Print"
            self.query_one("#copy-btn", Static).update(
                self._action_chip(copy_label, bg="#4ECDC4")
            )
            self.query_one("#run-btn", Static).update(self._action_chip("Run", bg="#7aa2f7"))
            actions.add_class("visible")
        else:
            actions.remove_class("visible")

    def _show_detail(self, action: Action) -> None:
        self._selected = action
        tc = tool_color(action.tool)

        title = (
            f"[{tc} bold]{action.tool}[/]  "
            f"[{COLOR_PRIMARY} bold]›[/]  "
            f"[{COLOR_BRIGHT}]{action.title}[/]"
        )
        self.query_one("#info-title", Static).update(title)
        self.query_one("#info-tags", Static).update(render_tags(action.tags))

        if self.study_mode:
            hint = action.exam_hint or action.desc or "(no exam hint)"
            self.query_one("#info-title", Static).update(
                f"[{COLOR_ACCENT} bold]📖 Study[/]  "
                f"[{tc} bold]{action.tool}[/]  "
                f"[{COLOR_PRIMARY} bold]›[/]  "
                f"[{COLOR_BRIGHT}]{action.title}[/]"
            )
            self.query_one("#info-desc", Static).update(f"[{COLOR_BRIGHT}]{hint}[/]")
            self.query_one("#info-command", Static).update("")
            self.query_one("#info-hint", Static).update(
                f"[{COLOR_DIM}]Command hidden in study mode[/]"
            )
            self._update_action_buttons(False)
            return

        self.query_one("#info-desc", Static).update(
            f"[{COLOR_DESC} italic]{action.desc or 'No description'}[/]"
        )
        preview = self._preview_command(action)
        self.query_one("#info-command", Static).update(highlight_command(preview))
        if action.exam_hint:
            self.query_one("#info-hint", Static).update(
                f"[{COLOR_ACCENT}]📖[/] {action.exam_hint}"
            )
        else:
            self.query_one("#info-hint", Static).update("")

        self._update_action_buttons(True)

    def _clear_detail(self) -> None:
        self._selected = None
        for wid in ("info-title", "info-desc", "info-tags", "info-command", "info-hint"):
            self.query_one(f"#{wid}", Static).update("")
        self._update_action_buttons(False)

    def _results_list(self) -> ListView:
        return self.query_one("#results", ListView)

    def _current_index(self) -> int:
        lv = self._results_list()
        return lv.index if lv.index is not None else 0

    def _item_count(self) -> int:
        if self._mode == "search":
            return len(self.ranked)
        return len(self._browse_rows)

    def _set_index(self, idx: int) -> None:
        count = self._item_count()
        if count == 0:
            return
        idx = max(0, min(idx, count - 1))
        lv = self._results_list()
        lv.index = idx

        if self._mode == "search":
            self._show_detail(self.ranked[idx].action)
            self._rehighlight_rows(idx)
        else:
            self._show_browse_detail(self._browse_rows[idx])
            self._rehighlight_browse_rows(idx)

        if lv.children and idx < len(lv.children):
            lv.scroll_to_widget(lv.children[idx], force=True)

    def _activate_index(self, idx: int) -> None:
        if self._mode == "search":
            if 0 <= idx < len(self.ranked):
                action = self.ranked[idx].action
                if self.study_mode:
                    self._notify_result(f"{action.tool} — {action.title}: {action.exam_hint or action.desc or '(no study hint)'}")
                else:
                    self._run_action_shell(action)
            return

        if not (0 <= idx < len(self._browse_rows)):
            return
        row = self._browse_rows[idx]
        if row.level == "category":
            self._selected_category = row.category
            self._browse_level = "tool"
            self._selected_tool = None
            self._refresh_display(self.query_one("#search", Input).value)
            self._results_list().focus()
        elif row.level == "tool":
            self._selected_tool = row.tool
            self._browse_level = "command"
            self._refresh_display(self.query_one("#search", Input).value)
            self._results_list().focus()
        elif row.level == "command" and row.action:
            if self.study_mode:
                action = row.action
                self._notify_result(
                    f"{action.tool} — {action.title}: {action.exam_hint or action.desc or '(no study hint)'}"
                )
            else:
                self._run_action_shell(row.action)

    @on(Click, "#copy-btn")
    def on_copy_click(self, _event: Click) -> None:
        if self._selected:
            self._copy_action(self._selected)

    @on(Click, "#run-btn")
    def on_run_click(self, _event: Click) -> None:
        if self._selected:
            self._run_action_shell(self._selected)

    def action_run_selected(self) -> None:
        if self._selected:
            self._run_action_shell(self._selected)

    def _rehighlight_browse_rows(self, selected_idx: int) -> None:
        list_view = self._results_list()
        for i, row in enumerate(self._browse_rows):
            if i >= len(list_view.children):
                break
            line = self._format_browse_row(row, selected=(i == selected_idx))
            list_view.children[i].query_one(Label).update(line)

    def action_cursor_down(self) -> None:
        focused_id = getattr(self.focused, "id", None)
        if focused_id not in {"search", "results"}:
            return
        self._set_index(self._current_index() + 1)

    def action_cursor_up(self) -> None:
        focused_id = getattr(self.focused, "id", None)
        if focused_id not in {"search", "results"}:
            return
        self._set_index(self._current_index() - 1)

    def action_page_down(self) -> None:
        focused_id = getattr(self.focused, "id", None)
        if focused_id not in {"search", "results"}:
            return
        self._set_index(self._current_index() + 10)

    def action_page_up(self) -> None:
        focused_id = getattr(self.focused, "id", None)
        if focused_id not in {"search", "results"}:
            return
        self._set_index(self._current_index() - 10)

    def action_go_back(self) -> None:
        """Esc: drill up browse levels, clear search, or quit."""
        search = self.query_one("#search", Input)
        raw = search.value.strip()

        if raw:
            search.value = ""
            self._browse_level = "category"
            self._selected_category = None
            self._selected_tool = None
            self._refresh_display("")
            self._results_list().focus()
            return

        if self._mode == "search":
            self._browse_level = "category"
            self._selected_category = None
            self._selected_tool = None
            self._refresh_display("")
            self._results_list().focus()
            return

        if self._browse_level == "command":
            self._browse_level = "tool"
            self._selected_tool = None
            self._refresh_display("")
            self._results_list().focus()
            return

        if self._browse_level == "tool":
            self._browse_level = "category"
            self._selected_category = None
            self._refresh_display("")
            self._results_list().focus()
            return

        self.action_quit()

    def _set_status(self, message: str) -> None:
        self._hint_markup = message
        self._refresh_bottom_bar()

    def _notify_result(self, message: str, *, severity: str = "information") -> None:
        icon = f"[{COLOR_SUCCESS}]✓[/]" if severity == "information" else f"[{COLOR_PRIMARY}]![/]"
        self._set_status(f"{icon} {message}")

    @on(Input.Changed, "#search")
    def on_search_changed(self, event: Input.Changed) -> None:
        self._refresh_display(event.value)

    @on(Input.Submitted, "#search")
    def on_search_submitted(self, event: Input.Submitted) -> None:
        raw = event.value.strip()
        if self._handle_special(raw):
            event.input.value = ""
            self._refresh_display("")
            return

        self._activate_index(self._current_index())
        if self._mode == "search":
            event.input.value = ""
            self._browse_level = "category"
            self._selected_category = None
            self._selected_tool = None
            self._refresh_display("")

    @on(ListView.Selected, "#results")
    def on_result_selected(self, event: ListView.Selected) -> None:
        """Run/drill only when the list itself is focused (Enter on a row)."""
        if getattr(self.focused, "id", None) != "results":
            return
        idx = event.list_view.index
        if idx is not None:
            self._activate_index(idx)

    @on(ListView.Highlighted, "#results")
    def on_result_highlighted(self, event: ListView.Highlighted) -> None:
        idx = event.list_view.index
        if idx is None:
            return
        if self._mode == "search" and 0 <= idx < len(self.ranked):
            self._show_detail(self.ranked[idx].action)
            self._rehighlight_rows(idx)
        elif self._mode == "browse" and 0 <= idx < len(self._browse_rows):
            self._show_browse_detail(self._browse_rows[idx])
            self._rehighlight_browse_rows(idx)

    def _rehighlight_rows(self, selected_idx: int) -> None:
        query = parse_search_query(self.query_one("#search", Input).value)
        list_view = self.query_one("#results", ListView)
        for i, ranked in enumerate(self.ranked):
            if i >= len(list_view.children):
                break
            line = self._format_list_row(
                ranked.action,
                query.text,
                selected=(i == selected_idx),
            )
            item = list_view.children[i]
            label = item.query_one(Label)
            label.update(line)

    def _handle_special(self, raw: str) -> bool:
        lower = raw.lower()

        if lower.startswith("set ") and "=" in raw:
            key, _, value = raw[4:].partition("=")
            key, value = key.strip(), value.strip()
            if key:
                self.var_store.set(key, value)
                self._notify_result(f"Set {key}={value}")
                self._refresh_display("")
            return True

        if lower.startswith("unset "):
            key = raw[6:].strip()
            if key and self.var_store.unset(key):
                self._notify_result(f"Unset {key}")
            else:
                self._set_status(f"Variable not set: {key}")
            return True

        if lower == "variables":
            self.action_show_variables()
            return True

        if lower == "tools":
            self.action_browse_categories()
            return True

        if lower == "reload":
            self.action_reload()
            return True

        if lower == "help":
            self.action_show_help()
            return True

        if lower == "output clipboard":
            self.config.set_output_mode(OutputMode.CLIPBOARD)
            self._notify_result("Output mode: clipboard")
            return True

        if lower == "output print":
            self.config.set_output_mode(OutputMode.PRINT)
            self._notify_result("Output mode: print")
            return True

        return False

    async def _resolve_command(self, action: Action) -> str | None:
        """Substitute variables and prompt for missing placeholders."""
        if self.study_mode:
            hint = action.exam_hint or action.desc or "(no study hint)"
            self._notify_result(f"{action.tool} — {action.title}: {hint}")
            return None

        vars_map = self.var_store.as_substitution_map()
        placeholders = parse_placeholders(action.command)
        required_missing = [
            p.name
            for p in placeholders
            if p.required and (p.name not in vars_map or vars_map[p.name] == "")
        ]

        if required_missing:
            filled = await self.push_screen_wait(PlaceholderForm(required_missing, vars_map))
            if filled is None:
                self._set_status("Cancelled")
                return None
            for key, value in filled.items():
                if value:
                    self.var_store.set(key, value)
            vars_map = self.var_store.as_substitution_map()

        sub = substitute(action.command, vars_map)
        if not sub.ok:
            self._set_status(f"Missing variables: {', '.join(sub.missing)}")
            return None
        return sub.command

    @work
    async def _copy_action(self, action: Action) -> None:
        command = await self._resolve_command(action)
        if command is None:
            return

        if is_destructive(command):
            confirmed = await self.push_screen_wait(
                ConfirmDestructive(highlight_command(command))
            )
            if not confirmed:
                self._set_status("Cancelled destructive command")
                return

        ok, message = deliver(command, self.config.output_mode)
        severity = "information" if ok else "warning"
        self._notify_result(message, severity=severity)
        self._show_detail(action)
        tool_count = len({a.tool for a in self.actions})
        self._update_header(tool_count, len(self.actions))
        self._results_list().focus()

    @work
    async def _run_action_shell(self, action: Action) -> None:
        command = await self._resolve_command(action)
        if command is None:
            return

        ok, message = launch_command(command)
        if not ok:
            self._set_status(f"[{COLOR_PRIMARY}]! {message} — use Copy and run manually[/]")
            return

        self._notify_result(message)
        self._show_detail(action)
        self._results_list().focus()

    def action_focus_search(self) -> None:
        self._search_input().focus()

    def action_browse_categories(self) -> None:
        """Reset to top-level category browse."""
        search = self._search_input()
        search.value = ""
        self._browse_level = "category"
        self._selected_category = None
        self._selected_tool = None
        self._refresh_display("")
        self._results_list().focus()

    def action_grow_left_pane(self) -> None:
        self._left_pane_ratio = min(0.75, self._left_pane_ratio + 0.05)
        self._apply_layout()

    def action_shrink_left_pane(self) -> None:
        self._left_pane_ratio = max(0.25, self._left_pane_ratio - 0.05)
        self._apply_layout()

    def action_toggle_focus(self) -> None:
        if self.focused and getattr(self.focused, "id", None) == "search":
            lv = self._results_list()
            lv.focus()
            if self._item_count() and lv.index is None:
                self._set_index(0)
        else:
            self.action_focus_search()

    def action_show_help(self) -> None:
        self.push_screen(HelpScreen())

    def action_show_variables(self) -> None:
        self.push_screen(
            VariablesScreen(
                self.var_store.list_all(),
                set(self.var_store.list_user()),
            )
        )

    def action_reload(self) -> None:
        self.reload_actions()
        tool_count = len({a.tool for a in self.actions})
        self._notify_result(f"Reloaded {tool_count} tools, {len(self.actions)} commands")

    def action_quit(self) -> None:
        self.exit()


def run_tui(
    config: LoadoutConfig,
    var_store: VariableStore,
    *,
    tag: str | None = None,
    tool: str | None = None,
    study: bool = False,
) -> None:
    app = LoadoutApp(config, var_store, tag_filter=tag, tool_filter=tool, study_mode=study)
    app.run(mouse=True)
