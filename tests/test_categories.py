"""Tests for category metadata loading."""

from pathlib import Path

import yaml

from loadout.categories import CategoryInfo, category_info_for, category_key, load_category_info, manifest_category_slugs


def test_category_key_normalizes_display_name():
    assert category_key("Reconnaissance") == "reconnaissance"
    assert category_key("Scanning And Enumeration") == "scanning_and_enumeration"


def test_load_category_info_from_builtin_manifest():
    catalog = load_category_info()
    assert "reconnaissance" in catalog
    recon = catalog["reconnaissance"]
    assert "dns" in recon.description.lower()
    assert "passive" in recon.strategy.lower()


def test_manifest_category_slugs_matches_ceh_phases():
    slugs = manifest_category_slugs()
    assert len(slugs) == 15
    assert slugs[0] == "reconnaissance"
    assert slugs[-1] == "compliance_and_reporting"


def test_category_info_for_unknown_category():
    info = category_info_for("Unknown", catalog={})
    assert info.description == ""
    assert "smallest command" in info.strategy


def test_category_info_for_display_name_with_spaces():
    catalog = {
        "scanning_and_enumeration": CategoryInfo(
            description="Port scans and service enum.",
            strategy="Sweep first.",
        )
    }
    info = category_info_for("Scanning And Enumeration", catalog)
    assert info.description == "Port scans and service enum."


def test_load_category_info_ignores_legacy_count_entries(tmp_path: Path):
    manifest = tmp_path / "manifest.yaml"
    manifest.write_text(
        yaml.dump(
            {
                "categories": {
                    "recon": 7,
                    "scanning": {
                        "description": "Port and host discovery.",
                        "strategy": "Sweep first.",
                    },
                }
            }
        ),
        encoding="utf-8",
    )
    catalog = load_category_info(tmp_path)
    assert "recon" not in catalog
    assert catalog["scanning"] == CategoryInfo(
        description="Port and host discovery.",
        strategy="Sweep first.",
    )
