import pytest

from src.server import analyze_project_risk, find_projects_needing_attention, load_projects


def test_invalid_minimum_rating_raises_value_error():
    with pytest.raises(ValueError, match="minimum_rating must be one of: Green, Amber, Red"):
        find_projects_needing_attention("critical")


def test_blank_project_id_raises_value_error():
    with pytest.raises(ValueError, match="project_id must be a non-empty string"):
        analyze_project_risk("   ")


def test_valid_project_id_returns_assessment():
    project_id = load_projects()[0]["project_id"]
    result = analyze_project_risk(project_id)

    assert result["project_id"] == project_id
    assert "rating" in result
