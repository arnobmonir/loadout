"""Tests for TUI theme and hints."""

from loadout.tui_hints import hint_for_query
from loadout.tui_theme import (
    highlight_command,
    highlight_match,
    render_header_line,
    render_stats_bar,
    render_tags,
    tag_color,
    tool_color,
)


def test_tag_color_consistent():
    assert tag_color("recon") == tag_color("recon")
    assert tag_color("recon") != tag_color("web")


def test_tool_color_is_hex():
    assert tool_color("nmap").startswith("#")


def test_render_tags_colored():
    markup = render_tags(("recon", "web"))
    assert "#recon" in markup
    assert "#web" in markup


def test_render_tags_empty():
    assert "no tags" in render_tags(())


def test_highlight_command_parts():
    out = highlight_command("nmap -sS {{ip}} -p {{port|80}}")
    assert "nmap" in out
    assert "{{ip}}" in out
    assert "|80" in out


def test_highlight_command_pipe():
    out = highlight_command("cat file | grep x")
    assert "|" in out


def test_highlight_match():
    out = highlight_match("SYN stealth scan", "syn")
    assert "bold" in out


def test_render_header_line():
    line = render_header_line(
        version="0.3.0",
        tool_count=47,
        cmd_count=129,
        var_count=2,
        output_mode="clipboard",
    )
    assert "LOADOUT" in line
    assert "CLIPBOARD" in line


def test_render_stats_bar():
    line = render_stats_bar(
        tool_count=47,
        command_count=129,
        category_count=15,
        tag_count=24,
        cheat_file_count=47,
        user_cheat_file_count=0,
        pack_version="4",
        updated_label="Jul 03, 2026",
        var_count=2,
    )
    assert "47" in line
    assert "tools" in line
    assert "cmds" in line
    assert "Jul 03, 2026" in line
    assert "vars" in line


def test_hint_for_set():
    assert hint_for_query("set ") is not None


def test_hint_for_set_partial():
    assert hint_for_query("set i") is not None


def test_hint_for_set_confirm():
    assert "Enter" in hint_for_query("set ip=10.0.0.1")


def test_hint_for_unset():
    assert hint_for_query("unset ") is not None


def test_hint_for_variables():
    assert hint_for_query("variables") is not None


def test_hint_for_tools():
    assert hint_for_query("tools") is not None


def test_hint_for_help():
    assert hint_for_query("help") is not None


def test_hint_for_reload():
    assert hint_for_query("reload") is not None


def test_hint_for_output():
    assert hint_for_query("output clipboard") is not None


def test_hint_empty_for_normal_search():
    assert hint_for_query("nmap scan") is None
