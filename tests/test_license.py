import re
from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_project_uses_gplv3_only_metadata_and_license_text():
    metadata = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    license_text = (ROOT / "LICENSE").read_text(encoding="utf-8")

    assert re.search(r'^license = "GPL-3\.0-only"$', metadata, re.MULTILINE)
    assert "GNU GENERAL PUBLIC LICENSE" in license_text
    assert "Version 3, 29 June 2007" in license_text
    assert "MIT License" not in license_text


def test_readmes_publish_the_gplv3_badge_and_terms():
    english = (ROOT / "README.md").read_text(encoding="utf-8")
    chinese = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")

    assert "License-GPLv3-blue.svg" in english
    assert "GNU General Public License version 3" in english
    assert "License-GPLv3-blue.svg" in chinese
    assert "GNU General Public License version 3" in chinese
