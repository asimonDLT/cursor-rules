import json
from pathlib import Path

import pytest

from library_explorer.data.loader import DataRepository
from library_explorer.data.models import Tool

# Sample valid tool_registry.json content
VALID_TOOL_REGISTRY_CONTENT = {
    "tool_categories": {
        "cat1": {"description": "Category 1 Description", "tools": ["ToolA", "ToolB"]},
        "cat2": {"description": "Category 2 Description", "tools": ["ToolC"]},
    },
    "domain_mappings": {"domain1": ["cat1"], "domain2": ["cat1", "cat2"]},
}

# Sample tool_registry.json with missing 'tools' list in a category
MALFORMED_CATEGORY_CONTENT = {
    "tool_categories": {
        "cat1": {
            "description": "Category 1 Description"  # Missing "tools"
        }
    },
    "domain_mappings": {},
}

# Sample tool_registry.json with non-string tool name
NON_STRING_TOOL_NAME_CONTENT = {
    "tool_categories": {
        "cat1": {
            "description": "Category 1 Description",
            "tools": ["ToolA", 123],  # 123 is not a string
        }
    },
    "domain_mappings": {},
}


@pytest.fixture
def temp_data_dir(tmp_path: Path) -> Path:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    return data_dir


def test_datarepository_init(temp_data_dir: Path) -> None:
    """Test DataRepository initialization."""
    repo = DataRepository(data_path=temp_data_dir)
    assert repo.data_path == temp_data_dir
    assert not repo.roles
    assert not repo.tools
    assert not repo.domains
    assert not repo.tool_domain_mappings
    assert not repo.tool_categories_present


def test_load_data_tool_registry_valid(temp_data_dir: Path) -> None:
    """Test loading a valid tool_registry.json."""
    tool_registry_file = temp_data_dir / "tool_registry.json"
    with open(tool_registry_file, "w") as f:
        json.dump(VALID_TOOL_REGISTRY_CONTENT, f)

    repo = DataRepository(data_path=temp_data_dir)
    repo.load_data()

    assert repo.tool_categories_present
    assert len(repo.tools) == 3
    assert "ToolA" in repo.tools
    assert repo.tools["ToolA"].name == "ToolA"
    assert repo.tools["ToolA"].category == "cat1"
    assert repo.tools["ToolA"].description == "Category 1 Description"
    assert "ToolC" in repo.tools
    assert repo.tools["ToolC"].category == "cat2"
    assert repo.tool_domain_mappings == VALID_TOOL_REGISTRY_CONTENT["domain_mappings"]


def test_load_data_tool_registry_non_existent(temp_data_dir: Path, capsys) -> None:
    """Test loading when tool_registry.json does not exist."""
    repo = DataRepository(data_path=temp_data_dir)
    repo.load_data()
    captured = capsys.readouterr()

    assert not repo.tool_categories_present
    assert not repo.tools
    assert not repo.tool_domain_mappings
    assert f"Warning: {temp_data_dir / 'tool_registry.json'} not found." in captured.out


def test_load_data_tool_registry_empty_json(temp_data_dir: Path, capsys) -> None:
    """Test loading an empty JSON ({}) as tool_registry.json."""
    tool_registry_file = temp_data_dir / "tool_registry.json"
    with open(tool_registry_file, "w") as f:
        json.dump({}, f)

    repo = DataRepository(data_path=temp_data_dir)
    repo.load_data()
    captured = capsys.readouterr()

    assert not repo.tool_categories_present
    assert not repo.tools
    assert not repo.tool_domain_mappings
    assert "Warning: 'tool_categories' key not found" in captured.out


def test_load_data_tool_registry_malformed_category(temp_data_dir: Path) -> None:
    """Test loading tool_registry.json where a category misses the 'tools' list."""
    tool_registry_file = temp_data_dir / "tool_registry.json"
    with open(tool_registry_file, "w") as f:
        json.dump(MALFORMED_CATEGORY_CONTENT, f)

    repo = DataRepository(data_path=temp_data_dir)
    repo.load_data()

    assert repo.tool_categories_present
    assert not repo.tools  # No tools should be loaded if the 'tools' list is missing
    assert repo.tool_domain_mappings == {}


def test_load_data_tool_registry_non_string_tool_name(
    temp_data_dir: Path, capsys
) -> None:
    """Test loading tool_registry.json with a non-string tool name, expecting Pydantic error."""
    tool_registry_file = temp_data_dir / "tool_registry.json"
    with open(tool_registry_file, "w") as f:
        json.dump(NON_STRING_TOOL_NAME_CONTENT, f)

    repo = DataRepository(data_path=temp_data_dir)
    # Pydantic validation happens during model instantiation.
    # The loader currently prints validation errors but doesn't raise them to stop loading.
    # So, we check that ToolA is loaded, but the invalid one (123) is skipped and an error is printed.
    repo.load_data()
    captured = capsys.readouterr()

    assert repo.tool_categories_present
    assert "ToolA" in repo.tools
    assert len(repo.tools) == 1  # Only ToolA should be loaded
    assert "Error validating tool '123'" in captured.out
    assert (
        "Input should be a valid string" in captured.out
    )  # Pydantic error message for name field


def test_get_tool_methods(temp_data_dir: Path) -> None:
    """Test get_tool and list_tools methods."""
    tool_registry_file = temp_data_dir / "tool_registry.json"
    with open(tool_registry_file, "w") as f:
        json.dump(VALID_TOOL_REGISTRY_CONTENT, f)

    repo = DataRepository(data_path=temp_data_dir)
    repo.load_data()

    tool_a = repo.get_tool("ToolA")
    assert tool_a is not None
    assert tool_a.name == "ToolA"

    non_existent_tool = repo.get_tool("NonExistent")
    assert non_existent_tool is None

    all_tools = repo.list_tools()
    assert len(all_tools) == 3
    assert isinstance(all_tools[0], Tool)


# Placeholder for future tests when Role/Domain YAML loading is implemented
# def test_load_yaml_roles_not_implemented_yet():
#     pass

# def test_load_yaml_domains_not_implemented_yet():
#     pass
