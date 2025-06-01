import json
from pathlib import Path

import pytest

from library_explorer.data.loader import DataRepository
from library_explorer.data.validator import validate_data

# Sample valid tool_registry.json content (consistent with loader tests)
VALID_TOOL_REGISTRY_CONTENT = {
    "tool_categories": {
        "cat1": {"description": "Category 1 Description", "tools": ["ToolA", "ToolB"]},
        "cat2": {"description": "Category 2 Description", "tools": ["ToolC"]},
    },
    "domain_mappings": {"domain1": ["cat1"], "domain2": ["cat1", "cat2"]},
}

# Content with domain_mappings referencing a non-existent category
INVALID_DOMAIN_MAPPING_CONTENT = {
    "tool_categories": {
        "cat1": {"description": "Category 1 Description", "tools": ["ToolA"]}
    },
    "domain_mappings": {"domain1": ["cat1", "non_existent_cat"]},
}

# Content missing tool_categories key
MISSING_TOOL_CATEGORIES_CONTENT = {"domain_mappings": {"domain1": ["cat1"]}}

# Content missing domain_mappings key
MISSING_DOMAIN_MAPPINGS_CONTENT = {
    "tool_categories": {
        "cat1": {"description": "Category 1 Description", "tools": ["ToolA"]}
    }
}


@pytest.fixture
def temp_data_dir_for_validator(tmp_path: Path) -> Path:
    # Slightly different name to avoid conflict if tests are run in parallel or fixtures are shared unexpectedly
    data_dir = tmp_path / "validator_data"
    data_dir.mkdir(exist_ok=True)
    return data_dir


def test_validate_data_valid_tool_registry(
    temp_data_dir_for_validator: Path, capsys
) -> None:
    """Test validate_data with a perfectly valid tool_registry.json."""
    tool_registry_file = temp_data_dir_for_validator / "tool_registry.json"
    with open(tool_registry_file, "w") as f:
        json.dump(VALID_TOOL_REGISTRY_CONTENT, f)

    repo = DataRepository(data_path=temp_data_dir_for_validator)
    repo.load_data()
    is_valid = validate_data(repo)
    captured = capsys.readouterr()

    assert is_valid
    assert "All data validations passed successfully!" in captured.out
    assert "Tool domain mappings are consistent" in captured.out


def test_validate_data_invalid_domain_mapping(
    temp_data_dir_for_validator: Path, capsys
) -> None:
    """Test validate_data when domain_mappings references a non-existent category."""
    tool_registry_file = temp_data_dir_for_validator / "tool_registry.json"
    with open(tool_registry_file, "w") as f:
        json.dump(INVALID_DOMAIN_MAPPING_CONTENT, f)

    repo = DataRepository(data_path=temp_data_dir_for_validator)
    repo.load_data()
    is_valid = validate_data(repo)
    captured = capsys.readouterr()

    assert not is_valid
    assert "Data validation failed" in captured.out
    assert "references a non-existent tool category 'non_existent_cat'" in captured.out


def test_validate_data_missing_tool_categories(
    temp_data_dir_for_validator: Path, capsys
) -> None:
    """Test validate_data when tool_categories key is missing."""
    tool_registry_file = temp_data_dir_for_validator / "tool_registry.json"
    with open(tool_registry_file, "w") as f:
        json.dump(MISSING_TOOL_CATEGORIES_CONTENT, f)

    repo = DataRepository(data_path=temp_data_dir_for_validator)
    repo.load_data()  # Loader will print a warning about missing tool_categories
    is_valid = validate_data(repo)
    captured = capsys.readouterr()

    assert is_valid  # Should still be considered valid from validator's perspective, as loader handles this
    assert "'tool_categories' key missing in 'tool_registry.json'" in captured.out
    # It might also say "domain_mappings found, but no tool categories seem to be loaded" if domain_mappings exist
    assert (
        "All data validations passed successfully!" in captured.out
    )  # or specific message about this state


def test_validate_data_missing_domain_mappings(
    temp_data_dir_for_validator: Path, capsys
) -> None:
    """Test validate_data when domain_mappings key is missing but tool_categories exist."""
    tool_registry_file = temp_data_dir_for_validator / "tool_registry.json"
    with open(tool_registry_file, "w") as f:
        json.dump(MISSING_DOMAIN_MAPPINGS_CONTENT, f)

    repo = DataRepository(data_path=temp_data_dir_for_validator)
    repo.load_data()
    is_valid = validate_data(repo)
    captured = capsys.readouterr()

    assert is_valid
    assert "'tool_domain_mappings' key is missing or empty" in captured.out
    assert "All data validations passed successfully!" in captured.out


def test_validate_data_empty_tool_registry(
    temp_data_dir_for_validator: Path, capsys
) -> None:
    """Test validate_data with an entirely empty tool_registry.json ({})"""
    tool_registry_file = temp_data_dir_for_validator / "tool_registry.json"
    (tool_registry_file).write_text("{}")

    repo = DataRepository(data_path=temp_data_dir_for_validator)
    repo.load_data()  # Loader warns about missing tool_categories
    is_valid = validate_data(repo)
    captured = capsys.readouterr()

    assert is_valid
    assert "'tool_categories' key missing" in captured.out  # From validator itself
    assert "All data validations passed successfully!" in captured.out


# Placeholder for future tests when Role/Domain validations are active
# def test_validate_data_with_roles_and_domains():
#     pass
