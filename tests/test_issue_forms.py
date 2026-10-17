"""Every file in .github/ISSUE_TEMPLATE parses, and each issue form has GitHub's required keys."""

from pathlib import Path

import yaml

TEMPLATES = sorted((Path(__file__).parents[1] / ".github" / "ISSUE_TEMPLATE").glob("*.yml"))


def test_issue_forms():
    assert any(p.name != "config.yml" for p in TEMPLATES), "no issue forms found"
    for path in TEMPLATES:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert isinstance(data, dict), path.name
        if path.name == "config.yml":
            continue
        assert {"name", "description", "body"} <= data.keys(), path.name
        ids = [item["id"] for item in data["body"] if "id" in item]
        assert len(ids) == len(set(ids)), f"{path.name}: duplicate ids {ids}"
