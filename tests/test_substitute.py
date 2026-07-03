"""Tests for loadout.substitute."""

from loadout.substitute import parse_placeholders, substitute


def test_parse_placeholders_required_and_default():
    ph = parse_placeholders("nmap -p {{port|80}} {{ip}}")
    assert len(ph) == 2
    assert ph[0].name == "port"
    assert ph[0].default == "80"
    assert ph[1].name == "ip"
    assert ph[1].required


def test_substitute_all_present():
    result = substitute("nmap -sS {{ip}}", {"ip": "10.0.0.1"})
    assert result.ok
    assert result.command == "nmap -sS 10.0.0.1"
    assert result.missing == []


def test_substitute_uses_default():
    result = substitute("nmap -p {{port|443}} {{ip}}", {"ip": "10.0.0.1"})
    assert result.ok
    assert result.command == "nmap -p 443 10.0.0.1"


def test_substitute_reports_missing():
    result = substitute("nmap {{ip}}", {})
    assert not result.ok
    assert result.missing == ["ip"]
    assert "{{ip}}" in result.command


def test_substitute_mixed():
    result = substitute(
        "curl {{url|http://localhost}} -H 'Host: {{domain}}'",
        {"domain": "lab.local"},
    )
    assert result.ok
    assert "lab.local" in result.command
    assert "http://localhost" in result.command
