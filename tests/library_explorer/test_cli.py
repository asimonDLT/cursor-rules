from typer.testing import CliRunner

from library_explorer.cli import app

runner = CliRunner()


def test_library_explorer_main_help() -> None:
    """Test the main --help output."""
    result = runner.invoke(app, ["main", "--help"])
    assert result.exit_code == 0
    assert "Usage: main [OPTIONS]" in result.stdout
    assert "A CLI tool to explore Role Library and Tool Registry." in result.stdout


def test_library_explorer_load_help() -> None:
    """Test the load --help output."""
    result = runner.invoke(app, ["load", "--help"])
    assert result.exit_code == 0
    assert "Usage: load [OPTIONS]" in result.stdout
    assert "Load and print tool names from the data repository." in result.stdout


def test_library_explorer_validate_help() -> None:
    """Test the validate --help output."""
    result = runner.invoke(app, ["validate", "--help"])
    assert result.exit_code == 0
    assert "Usage: validate [OPTIONS]" in result.stdout
    assert "Load and validate data from the repository." in result.stdout


def test_library_explorer_browse_help() -> None:
    """Test the browse --help output."""
    result = runner.invoke(app, ["browse", "--help"])
    assert result.exit_code == 0
    assert "Usage: library-explorer browse [OPTIONS] COMMAND [ARGS]..." in result.stdout
    assert "Browse Roles, Tools, or Domains." in result.stdout
    assert "tools" in result.stdout  # Check for the tools subcommand


def test_library_explorer_browse_tools_help() -> None:
    """Test the browse tools --help output."""
    result = runner.invoke(app, ["browse", "tools", "--help"])
    assert result.exit_code == 0
    assert "Usage: library-explorer browse tools [OPTIONS]" in result.stdout
    assert "Browse available tools from the Tool Registry." in result.stdout


# Add a simple smoke test for the browse tools command with a non-existent file
def test_browse_tools_command_non_existent_file(tmp_path) -> None:
    """Test browse tools command with a non-existent tool_registry.json shows correct message and exits."""
    result = runner.invoke(app, ["browse", "tools", "--data-path", str(tmp_path)])
    assert result.exit_code == 1
    assert "Running Data Validations..." in result.stdout  # Validation runs
    assert (
        f"Warning: {tmp_path / 'tool_registry.json'!s} not found." in result.stdout
    )  # Loader warning
    # Validator should indicate tool_categories missing
    assert "'tool_categories' key missing in 'tool_registry.json'" in result.stdout
    assert (
        "All data validations passed successfully!" in result.stdout
    )  # Because missing categories isn't a hard fail for validator
    assert "No tools found or loaded even after validation." in result.stdout


# Test for browse tools with formats
def test_browse_tools_format_table_empty(tmp_path) -> None:
    """Test browse tools --format table with no tools (empty file or parsing issue)."""
    (tmp_path / "tool_registry.json").write_text("{}")
    result = runner.invoke(
        app, ["browse", "tools", "--data-path", str(tmp_path), "--format", "table"]
    )
    assert result.exit_code == 1
    assert "Running Data Validations..." in result.stdout
    assert "Warning: 'tool_categories' key not found" in result.stdout  # Loader warning
    assert (
        "'tool_categories' key missing in 'tool_registry.json'" in result.stdout
    )  # Validator info
    assert "No tools found or loaded even after validation" in result.stdout


def test_browse_tools_format_list_empty(tmp_path) -> None:
    """Test browse tools --format list with no tools."""
    (tmp_path / "tool_registry.json").write_text("{}")
    result = runner.invoke(
        app, ["browse", "tools", "--data-path", str(tmp_path), "--format", "list"]
    )
    assert result.exit_code == 1
    assert "Running Data Validations..." in result.stdout
    assert "Warning: 'tool_categories' key not found" in result.stdout  # Loader warning
    assert (
        "'tool_categories' key missing in 'tool_registry.json'" in result.stdout
    )  # Validator info
    assert "No tools found or loaded even after validation" in result.stdout


# Mocked Data for successful browse commands
SAMPLE_TOOL_REGISTRY_CONTENT = """
{
  "tool_categories": {
    "category1": {
      "description": "Desc for Cat1",
      "tools": ["ToolA", "ToolB"]
    },
    "category2": {
      "description": "Desc for Cat2",
      "tools": ["ToolC"]
    }
  },
  "domain_mappings": {}
}
"""


def test_browse_tools_format_table_with_data(tmp_path) -> None:
    """Test browse tools --format table with sample data."""
    (tmp_path / "tool_registry.json").write_text(SAMPLE_TOOL_REGISTRY_CONTENT)
    result = runner.invoke(
        app, ["browse", "tools", "--data-path", str(tmp_path), "--format", "table"]
    )
    assert result.exit_code == 0
    assert "Available Tools" in result.stdout
    assert "ToolA" in result.stdout
    assert "category1" in result.stdout
    assert "ToolC" in result.stdout
    assert "Desc for Cat2" in result.stdout


def test_browse_tools_format_list_with_data(tmp_path) -> None:
    """Test browse tools --format list with sample data."""
    (tmp_path / "tool_registry.json").write_text(SAMPLE_TOOL_REGISTRY_CONTENT)
    result = runner.invoke(
        app, ["browse", "tools", "--data-path", str(tmp_path), "--format", "list"]
    )
    assert result.exit_code == 0
    assert "ToolA" in result.stdout
    assert "Category: category1" in result.stdout
    assert "Description: Desc for Cat1" in result.stdout
    assert "ToolC" in result.stdout


def test_browse_tools_invalid_format(tmp_path) -> None:
    """Test browse tools with an invalid format option."""
    (tmp_path / "tool_registry.json").write_text(SAMPLE_TOOL_REGISTRY_CONTENT)
    result = runner.invoke(
        app, ["browse", "tools", "--data-path", str(tmp_path), "--format", "invalid"]
    )
    assert result.exit_code == 1
    assert "Error: Invalid format 'invalid'" in result.stdout


# Add a simple smoke test for the load command with a non-existent file
# to ensure basic error handling/output without actual data an dependencies.
# More comprehensive tests will need mocked data.
def test_load_command_non_existent_file(tmp_path) -> None:
    """Test load command with a non-existent tool_registry.json."""
    result = runner.invoke(app, ["load", "--data-path", str(tmp_path)])
    assert result.exit_code == 0  # Load command itself doesn't exit with error for this
    assert f"Loading data from: {tmp_path!s}" in result.stdout
    assert (
        f"Warning: {tmp_path / 'tool_registry.json'!s} not found." in result.stdout
    )  # Loader warning
    assert "Running Data Validations..." in result.stdout  # Validation runs
    assert (
        "'tool_categories' key missing in 'tool_registry.json'" in result.stdout
    )  # Validator info
    assert "No tools found or loaded." in result.stdout
