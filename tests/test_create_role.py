#!/usr/bin/env python3
"""
Tests for role creation script.
Uses pytest with AAA pattern and fixtures for setup/teardown.
"""

import json
import tempfile
from collections.abc import Generator
from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch

import pytest

from scripts.create_role import (
    REQUIRED_EXECUTIVE_BUCKETS,
    REQUIRED_SPECIALIST_BUCKETS,
    VALID_ROLE_TYPES,
    apply_overrides,
    coerce_csv,
    deep_merge,
    generate_executive_role,
    generate_specialist_role,
    generate_synthesis_instructions,
    get_executive_template,
    get_role_data,
    get_specialist_template,
    load_role_library,
    load_template,
    load_tool_registry,
    resolve_tools_from_registry,
    validate_cli_input,
    validate_role_library,
    validate_role_name,
    write_role_file,
)


@pytest.fixture
def sample_tool_registry() -> dict[str, Any]:
    """Create a sample tool registry for testing."""
    return {
        "tool_categories": {
            "linting": {
                "description": "Code linting tools",
                "tools": ["ruff", "black", "isort"],
            },
            "testing": {
                "description": "Testing frameworks",
                "tools": ["pytest", "coverage"],
            },
            "cloud": {
                "description": "Cloud infrastructure tools",
                "tools": ["terraform", "ansible"],
            },
        },
        "domain_mappings": {
            "backend": ["linting", "testing"],
            "aws": ["cloud"],
            "python": ["linting", "testing"],
        },
    }


@pytest.fixture
def sample_role_library() -> dict[str, Any]:
    """Create a sample role library for testing."""
    return {
        "executive": {
            "cmo": {
                "identity": {
                    "scope": "Global",
                    "seniority": "C-level",
                    "span_of_control": "50",
                },
                "objectives": {
                    "top_objectives": [
                        "Drive brand awareness",
                        "Increase market share",
                    ],
                    "kpis": [
                        "Brand recognition",
                        "Lead generation",
                        "Customer acquisition cost",
                    ],
                },
                "influence": {
                    "decision_rights": ["Marketing budget", "Brand strategy"],
                    "stakeholders": ["CEO", "Sales VP", "Product VP"],
                },
                "behaviors": {
                    "comms": ["Weekly reviews", "Monthly board updates"],
                    "trusted_tools": ["HubSpot", "Google Analytics"],
                    "tool_domains": ["martech"],
                    "risk_posture": "Moderate",
                },
                "motivations": {
                    "drivers": ["Growth", "Innovation"],
                    "pain_points": ["Budget constraints", "Attribution challenges"],
                },
            }
        },
        "specialist": {
            "qa_lead": {
                "identity": {
                    "scope": "Cross-functional",
                    "seniority": "Senior specialist",
                    "span_of_control": "5",
                },
                "objectives": {
                    "top_objectives": [
                        "Ensure quality standards",
                        "Reduce defect rate",
                    ],
                    "kpis": ["Test coverage", "Defect density"],
                },
                "standards": ["ISO 9001", "ISTQB"],
                "gates": ["Code review", "Integration testing"],
                "behaviors": {
                    "trusted_tools": ["Selenium", "Jest"],
                    "tool_domains": ["testing"],
                    "risk_posture": "Conservative",
                },
            }
        },
    }


@pytest.fixture
def temp_role_library_file(sample_role_library: dict[str, Any]) -> Path:
    """Create a temporary role library file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(sample_role_library, f, indent=2)
        return Path(f.name)


@pytest.fixture
def temp_tool_registry_file(sample_tool_registry: dict[str, Any]) -> Path:
    """Create a temporary tool registry file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(sample_tool_registry, f, indent=2)
        return Path(f.name)


@pytest.fixture
def temp_output_dir() -> Generator[Path, None, None]:
    """Create a temporary output directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


class TestValidateCliInput:
    """Test cases for validate_cli_input function."""

    def test_validate_safe_input(self) -> None:
        """Test validation of safe input."""
        # Arrange
        safe_input = "backend_development"
        field_name = "test_field"

        # Act
        result = validate_cli_input(safe_input, field_name)

        # Assert
        assert result is True

    def test_validate_dangerous_patterns(self) -> None:
        """Test validation rejects dangerous patterns."""
        # Arrange
        dangerous_inputs: list[str] = [
            "{{malicious}}",
            "<script>alert('xss')</script>",
            "javascript:void(0)",
            "data:text/html,<script>",
            "${injection}",
            "`command`",
        ]

        for dangerous_input in dangerous_inputs:
            # Act
            result = validate_cli_input(dangerous_input, "test_field")

            # Assert
            assert result is False, f"Should reject: {dangerous_input}"

    def test_validate_excessive_length(self) -> None:
        """Test validation rejects excessively long input."""
        # Arrange
        long_input = "a" * 501  # Exceeds MAX_INPUT_LENGTH of 500

        # Act
        result = validate_cli_input(long_input, "test_field")

        # Assert
        assert result is False


class TestValidateRoleName:
    """Test cases for validate_role_name function."""

    def test_validate_valid_name(self) -> None:
        """Test validation of valid role name."""
        # Arrange
        valid_name = "cmo"

        # Act
        result = validate_role_name(valid_name)

        # Assert
        assert result == "cmo"

    def test_validate_mixed_case(self) -> None:
        """Test validation converts to lowercase."""
        # Arrange
        mixed_case = "CMO"

        # Act
        result = validate_role_name(mixed_case)

        # Assert
        assert result == "cmo"

    def test_validate_special_characters(self) -> None:
        """Test validation removes special characters."""
        # Arrange
        special_chars = "qa@lead#test"

        # Act
        result = validate_role_name(special_chars)

        # Assert
        assert result == "qaleadtest"

    def test_validate_preserves_hyphens_underscores(self) -> None:
        """Test validation preserves hyphens and underscores."""
        # Arrange
        name_with_separators = "qa-lead_test"

        # Act
        result = validate_role_name(name_with_separators)

        # Assert
        assert result == "qa-lead_test"

    def test_validate_empty_result_exits(self) -> None:
        """Test validation exits on empty result."""
        # Arrange
        invalid_name = "@#$%"

        # Act & Assert
        with pytest.raises(SystemExit):
            validate_role_name(invalid_name)

    def test_validate_dangerous_input_exits(self) -> None:
        """Test validation exits on dangerous input."""
        # Arrange
        dangerous_name = "{{malicious}}"

        # Act & Assert
        with pytest.raises(SystemExit):
            validate_role_name(dangerous_name)


class TestCoerceCsv:
    """Test cases for coerce_csv function."""

    def test_coerce_valid_csv(self) -> None:
        """Test coercing valid CSV string."""
        # Arrange
        csv_string: str = "item1,item2,item3"

        # Act
        result: list[str] | None = coerce_csv(csv_string)

        # Assert
        assert result == ["item1", "item2", "item3"]

    def test_coerce_csv_with_spaces(self) -> None:
        """Test coercing CSV string with spaces."""
        # Arrange
        csv_string: str = "item1, item2 , item3"

        # Act
        result: list[str] | None = coerce_csv(csv_string)

        # Assert
        assert result == ["item1", "item2", "item3"]

    def test_coerce_none_input(self) -> None:
        """Test coercing None input."""
        # Arrange
        csv_string: str | None = None

        # Act
        result: list[str] | None = coerce_csv(csv_string)

        # Assert
        assert result is None

    def test_coerce_empty_string(self) -> None:
        """Test coercing empty string."""
        # Arrange
        csv_string: str = ""

        # Act
        result: list[str] | None = coerce_csv(csv_string)

        # Assert
        assert result is None  # Empty string should result in None or empty list


class TestDeepMerge:
    """Test cases for deep_merge function."""

    def test_deep_merge_simple(self) -> None:
        """Test deep merge with simple dictionaries."""
        # Arrange
        base: dict[str, Any] = {"a": 1, "b": 2}
        override: dict[str, Any] = {"b": 3, "c": 4}

        # Act
        result: dict[str, Any] = deep_merge(base, override)

        # Assert
        assert result == {"a": 1, "b": 3, "c": 4}

    def test_deep_merge_nested(self) -> None:
        """Test deep merge with nested dictionaries."""
        # Arrange
        base: dict[str, Any] = {"level1": {"a": 1, "b": 2}}
        override: dict[str, Any] = {"level1": {"b": 3, "c": 4}}

        # Act
        result: dict[str, Any] = deep_merge(base, override)

        # Assert
        assert result == {"level1": {"a": 1, "b": 3, "c": 4}}

    def test_deep_merge_override_non_dict(self) -> None:
        """Test deep merge when override replaces non-dict with dict."""
        # Arrange
        base: dict[str, Any] = {"level1": "string_value"}
        override: dict[str, Any] = {"level1": {"new": "dict"}}

        # Act
        result: dict[str, Any] = deep_merge(base, override)

        # Assert
        assert result == {"level1": {"new": "dict"}}


class TestApplyOverrides:
    """Test cases for apply_overrides function."""

    def test_apply_cli_overrides(self, sample_role_library: dict[str, Any]) -> None:
        """Test applying CLI overrides to role data."""
        # Arrange
        base_data: dict[str, Any] = sample_role_library["executive"]["cmo"]
        mock_args = Mock()  # Using unittest.mock.Mock
        mock_args.trusted_tools = "tool1,tool2"
        mock_args.scope = "Regional"
        mock_args.kpis = "metric1,metric2"
        mock_args.json_override = None  # Ensure json_override is None for this test

        # Set all other CLI-overridable attributes to None to isolate test
        cli_override_fields: list[str] = [
            "comms",
            "drivers",
            "pain_points",
            "top_objectives",
            "decision_rights",
            "stakeholders",
            "seniority",
            "span_of_control",
        ]
        for attr in cli_override_fields:
            setattr(mock_args, attr, None)

        # Act
        with patch("scripts.create_role.validate_cli_input", return_value=True):
            result: dict[str, Any] = apply_overrides(base_data, mock_args)

        # Assert
        assert result["behaviors"]["trusted_tools"] == ["tool1", "tool2"]
        assert result["identity"]["scope"] == "Regional"
        assert result["objectives"]["kpis"] == ["metric1", "metric2"]

    def test_apply_json_overrides(self, sample_role_library: dict[str, Any]) -> None:
        """Test applying JSON file overrides to role data."""
        # Arrange
        base_data: dict[str, Any] = sample_role_library["executive"]["cmo"]
        mock_args = Mock()
        # Set all CLI attributes to None to ensure JSON override is tested in isolation
        cli_fields: list[str] = [
            "trusted_tools",
            "comms",
            "kpis",
            "drivers",
            "pain_points",
            "top_objectives",
            "decision_rights",
            "stakeholders",
            "scope",
            "seniority",
            "span_of_control",
        ]
        for attr in cli_fields:
            setattr(mock_args, attr, None)

        json_override_content: dict[str, Any] = {
            "behaviors": {"trusted_tools": ["override_tool_from_json"]}
        }
        # pylint: disable=W1514
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as tmp_json_file:
            json.dump(json_override_content, tmp_json_file)
            json_override_path_str = tmp_json_file.name
        mock_args.json_override = json_override_path_str

        try:
            # Act
            result: dict[str, Any] = apply_overrides(base_data, mock_args)

            # Assert
            assert "override_tool_from_json" in result["behaviors"]["trusted_tools"]
        finally:
            Path(json_override_path_str).unlink(missing_ok=True)

    def test_apply_overrides_precedence(
        self, sample_role_library: dict[str, Any]
    ) -> None:
        """Test that CLI overrides take precedence over JSON overrides."""
        # Arrange
        base_data: dict[str, Any] = sample_role_library["executive"]["cmo"]
        mock_args = Mock()
        mock_args.scope = "CLI_Scope_Override"
        # Other CLI args to None
        cli_fields_to_nullify: list[str] = [
            "trusted_tools",
            "comms",
            "kpis",
            "drivers",
            "pain_points",
            "top_objectives",
            "decision_rights",
            "stakeholders",
            "seniority",
            "span_of_control",
        ]
        for attr in cli_fields_to_nullify:
            setattr(mock_args, attr, None)

        json_override_content: dict[str, Any] = {
            "identity": {"scope": "JSON_Scope_Override"}
        }
        # pylint: disable=W1514
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as tmp_json_file:
            json.dump(json_override_content, tmp_json_file)
            json_override_path_str = tmp_json_file.name
        mock_args.json_override = json_override_path_str

        try:
            # Act
            with patch("scripts.create_role.validate_cli_input", return_value=True):
                result: dict[str, Any] = apply_overrides(base_data, mock_args)

            # Assert
            assert result["identity"]["scope"] == "CLI_Scope_Override"
        finally:
            Path(json_override_path_str).unlink(missing_ok=True)

    def test_apply_overrides_invalid_json_file(
        self, sample_role_library: dict[str, Any]
    ) -> None:
        """Test handling of invalid JSON override file."""
        # Arrange
        base_data: dict[str, Any] = sample_role_library["executive"]["cmo"]
        mock_args = Mock()
        # Set all CLI attributes to None
        cli_fields: list[str] = [
            "trusted_tools",
            "comms",
            "kpis",
            "drivers",
            "pain_points",
            "top_objectives",
            "decision_rights",
            "stakeholders",
            "scope",
            "seniority",
            "span_of_control",
        ]
        for attr in cli_fields:
            setattr(mock_args, attr, None)

        json_override_path_str = "/nonexistent/override.json"
        mock_args.json_override = json_override_path_str

        # Act & Assert
        with pytest.raises(SystemExit) as excinfo:
            apply_overrides(base_data, mock_args)
        assert "JSON override file not found" in str(excinfo.value)

    def test_apply_overrides_missing_json_file(
        self, sample_role_library: dict[str, Any]
    ) -> None:
        """Test handling of missing JSON override file."""
        # Arrange
        base_data: dict[str, Any] = sample_role_library["executive"]["cmo"]
        mock_args = Mock()
        # Set all CLI attributes to None
        cli_fields: list[str] = [
            "trusted_tools",
            "comms",
            "kpis",
            "drivers",
            "pain_points",
            "top_objectives",
            "decision_rights",
            "stakeholders",
            "scope",
            "seniority",
            "span_of_control",
        ]
        for attr in cli_fields:
            setattr(mock_args, attr, None)

        json_path = "/nonexistent/file.json"

        # Act & Assert
        with pytest.raises(SystemExit):
            apply_overrides(base_data, mock_args, json_path)


class TestLoadToolRegistry:
    """Test cases for load_tool_registry function."""

    def test_load_existing_registry(self, temp_tool_registry_file: Path) -> None:
        """Test loading existing tool registry."""
        # Arrange
        # The temp_tool_registry_file fixture creates the file.
        # We need to mock Path().parent.parent... to point to its location.
        mock_path_instance = Mock()
        # Simulate .cursor/rules/tools/tool_registry.json structure relative to a base
        # For the purpose of this test, assume SCRIPT_DIR is the parent of temp_tool_registry_file's parent
        # This is a bit indirect; ideally, the function would take the path as an argument.
        base_dir_containing_cursor = temp_tool_registry_file.parent.parent.parent
        mock_path_instance.parent.parent.parent.__truediv__.return_value = (
            base_dir_containing_cursor
            / ".cursor"
            / "rules"
            / "tools"
            / "tool_registry.json"
        )
        mock_path_instance.parent.parent.parent.__truediv__.return_value.exists.return_value = True

        # Act
        # Mock SCRIPT_DIR to be the effective base for Path resolution within the function
        with patch("scripts.create_role.SCRIPT_DIR", base_dir_containing_cursor):
            # Mock open to read from the temp file path
            with patch(
                "builtins.open",
                mock_open(
                    read_data=temp_tool_registry_file.read_text(encoding="utf-8")
                ),
            ):
                result: dict[str, Any] = load_tool_registry()

        # Assert
        assert isinstance(result, dict)
        assert "tool_categories" in result
        assert "domain_mappings" in result

    def test_load_missing_registry(self) -> None:
        """Test loading missing tool registry (file does not exist)."""
        # Arrange
        # Mock the path to tool_registry.json to report it doesn't exist.
        mock_path_instance = Mock()
        mock_path_instance.exists.return_value = False
        with patch("scripts.create_role.Path") as mock_path_constructor:
            mock_path_constructor.return_value = mock_path_instance
            # Act
            result: dict[str, Any] = load_tool_registry()

        # Assert
        assert result == {}

    def test_load_invalid_json_registry(self, temp_tool_registry_file: Path) -> None:
        """Test loading invalid JSON registry."""
        # Arrange
        # Overwrite the valid fixture file with invalid JSON
        temp_tool_registry_file.write_text("{ not_valid_json: True ", encoding="utf-8")

        mock_path_instance = Mock()
        base_dir_containing_cursor = temp_tool_registry_file.parent.parent.parent
        registry_path_mock = (
            base_dir_containing_cursor
            / ".cursor"
            / "rules"
            / "tools"
            / "tool_registry.json"
        )
        registry_path_mock.exists.return_value = True  # File exists

        # Act
        with patch("scripts.create_role.SCRIPT_DIR", base_dir_containing_cursor):
            # Mock open to read the corrupted content from the temp file
            with patch(
                "builtins.open",
                mock_open(
                    read_data=temp_tool_registry_file.read_text(encoding="utf-8")
                ),
            ):
                with patch("scripts.create_role.Path") as mock_path_constructor:
                    # Ensure the Path() call inside load_tool_registry resolves to something
                    # whose .exists() is True, but whose content (via mocked open) is bad.
                    mock_constructed_path = Mock()
                    mock_constructed_path.exists.return_value = True
                    mock_path_constructor.return_value = mock_constructed_path
                    result: dict[str, Any] = load_tool_registry()
        # Assert
        assert result == {}


class TestResolveToolsFromRegistry:
    """Test cases for resolve_tools_from_registry function."""

    def test_resolve_domain_mappings(
        self, sample_tool_registry: dict[str, Any]
    ) -> None:
        """Test resolving tools from domain mappings."""
        # Arrange
        domains: list[str] = ["backend"]

        # Act
        result: list[str] = resolve_tools_from_registry(domains, sample_tool_registry)

        # Assert
        assert "ruff" in result
        assert "pytest" in result
        assert len(result) == 5  # ruff, black, isort, pytest, coverage

    def test_resolve_direct_categories(
        self, sample_tool_registry: dict[str, Any]
    ) -> None:
        """Test resolving tools from direct categories."""
        # Arrange
        categories: list[str] = ["linting"]

        # Act
        result: list[str] = resolve_tools_from_registry(
            categories, sample_tool_registry
        )

        # Assert
        assert result == ["ruff", "black", "isort"]

    def test_resolve_unknown_domain(self, sample_tool_registry: dict[str, Any]) -> None:
        """Test resolving tools from unknown domain."""
        # Arrange
        domains: list[str] = ["unknown_domain"]

        # Act
        result: list[str] = resolve_tools_from_registry(domains, sample_tool_registry)

        # Assert
        assert not result  # Expect empty list

    def test_resolve_empty_registry(self) -> None:
        """Test resolving tools from empty registry."""
        # Arrange
        domains: list[str] = ["backend"]
        empty_registry: dict[str, Any] = {}

        # Act
        result: list[str] = resolve_tools_from_registry(domains, empty_registry)

        # Assert
        assert not result  # Expect empty list

    def test_resolve_removes_duplicates(
        self, sample_tool_registry: dict[str, Any]
    ) -> None:
        """Test that duplicate tools are removed."""
        # Arrange
        # 'backend' maps to linting, testing. 'python' maps to linting, testing.
        domains: list[str] = ["backend", "python"]

        # Act
        result: list[str] = resolve_tools_from_registry(domains, sample_tool_registry)

        # Assert
        # Expected tools: ruff, black, isort (from linting), pytest, coverage (from testing)
        expected_tools_set = {"ruff", "black", "isort", "pytest", "coverage"}
        assert set(result) == expected_tools_set
        assert len(result) == len(
            expected_tools_set
        )  # Ensure no duplicates in list form either


class TestValidateRoleLibrary:
    """Test cases for validate_role_library function."""

    def test_validate_valid_library(self, sample_role_library: dict[str, Any]) -> None:
        """Test validation of valid role library (should not raise/warn)."""
        # Arrange & Act & Assert
        try:
            validate_role_library(sample_role_library)
        except Exception as e:  # pylint: disable=broad-except
            pytest.fail(
                f"validate_role_library raised an exception for valid library: {e}"
            )

    def test_validate_missing_executive_buckets(self) -> None:
        """Test validation warns about missing executive buckets."""
        # Arrange
        invalid_library: dict[str, Any] = {
            "executive": {
                "cmo_incomplete": {
                    "identity": {"scope": "Global"},  # Missing other required buckets
                    "objectives": {},
                    "influence": {},
                    # "behaviors" is missing
                    "motivations": {},
                }
            }
        }

        # Act & Assert
        with patch("scripts.create_role.logger") as mock_logger:
            validate_role_library(invalid_library)
            # Check if warning was called, be more specific if possible about the message
            mock_logger.warning.assert_called()
            # Example of checking call args if a specific message is expected:
            # found_expected_warning = False
            # for call_args in mock_logger.warning.call_args_list:
            #     if "Missing required executive bucket(s)" in call_args[0][0]:
            #         found_expected_warning = True
            #         break
            # assert found_expected_warning, "Expected warning for missing exec buckets not logged"

    def test_validate_missing_specialist_buckets(self) -> None:
        """Test validation warns about missing specialist buckets."""
        # Arrange
        invalid_library: dict[str, Any] = {
            "specialist": {
                "qa_lead_incomplete": {
                    "identity": {
                        "scope": "Product"
                    },  # Missing objectives and one of (standards/behaviors)
                    "objectives": {},  # Add objectives to only test standards/behaviors
                }
            }
        }

        # Act & Assert
        with patch("scripts.create_role.logger") as mock_logger:
            validate_role_library(invalid_library)
            mock_logger.warning.assert_called()
            # Similar to above, could check for specific warning messages.


class TestLoadRoleLibrary:
    """Test cases for load_role_library function."""

    def test_load_existing_library(self, temp_role_library_file: Path) -> None:
        """Test loading existing role library."""
        # Arrange
        # temp_role_library_file fixture creates the file.
        # Mock the path resolution within load_role_library.
        # The function constructs path like: SCRIPT_DIR.parent / "templates" / "role_library.json"
        mock_path_instance = Mock()
        # Simulate the path structure the function expects to find role_library.json
        # Assume SCRIPT_DIR is parent of temp_role_library_file's parent's parent for this test.
        base_dir_for_templates = temp_role_library_file.parent.parent.parent
        expected_library_path = (
            base_dir_for_templates / "templates" / "role_library.json"
        )
        expected_library_path.parent.mkdir(
            parents=True, exist_ok=True
        )  # Ensure templates dir exists
        # Copy content from temp_role_library_file to where the func expects it
        expected_library_path.write_text(
            temp_role_library_file.read_text(encoding="utf-8"), encoding="utf-8"
        )

        # Act
        with patch("scripts.create_role.SCRIPT_DIR", base_dir_for_templates):
            result: dict[str, Any] = load_role_library()

        # Assert
        assert isinstance(result, dict)
        assert "executive" in result
        assert "specialist" in result

        # Cleanup the mock-created file
        expected_library_path.unlink(missing_ok=True)

    def test_load_missing_library(self) -> None:
        """Test loading missing role library (file does not exist)."""
        # Arrange
        # Mock Path resolution to make .exists() return False
        mock_path_instance = Mock()
        mock_path_instance.exists.return_value = False
        with patch("scripts.create_role.Path") as mock_path_constructor:
            mock_path_constructor.return_value = mock_path_instance
            # Act & Assert
            with pytest.raises(SystemExit) as excinfo:
                load_role_library()
            assert "Role library file not found" in str(excinfo.value)

    def test_load_invalid_json_library(self, temp_role_library_file: Path) -> None:
        """Test loading invalid JSON library."""
        # Arrange
        # Corrupt the content of the temp file
        temp_role_library_file.write_text("this is not valid json", encoding="utf-8")

        base_dir_for_templates = temp_role_library_file.parent.parent.parent
        expected_library_path = (
            base_dir_for_templates / "templates" / "role_library.json"
        )
        expected_library_path.parent.mkdir(parents=True, exist_ok=True)
        expected_library_path.write_text(
            temp_role_library_file.read_text(encoding="utf-8"), encoding="utf-8"
        )

        # Act & Assert
        with patch("scripts.create_role.SCRIPT_DIR", base_dir_for_templates):
            with pytest.raises(SystemExit) as excinfo:
                load_role_library()
            assert "Error decoding JSON from role library" in str(excinfo.value)

        expected_library_path.unlink(missing_ok=True)


class TestGetRoleData:
    """Test cases for get_role_data function."""

    def test_get_existing_role(self, sample_role_library: dict[str, Any]) -> None:
        """Test getting existing role data."""
        # Arrange
        role_type: str = "executive"
        role_name: str = "cmo"

        # Act
        result: dict[str, Any] | None = get_role_data(
            role_type, role_name, sample_role_library
        )

        # Assert
        assert result is not None
        assert "identity" in result
        assert result["identity"]["scope"] == "Global"

    def test_get_unknown_role_type(self, sample_role_library: dict[str, Any]) -> None:
        """Test getting role data for unknown type."""
        # Arrange
        role_type: str = "non_existent_type"
        role_name: str = "any_name"

        # Act
        result: dict[str, Any] | None = get_role_data(
            role_type, role_name, sample_role_library
        )

        # Assert
        assert result is None  # Should return None for unknown type, not ask

    def test_get_custom_role_confirmed(
        self, sample_role_library: dict[str, Any]
    ) -> None:
        """Test getting custom role when user confirms creation."""
        # Arrange
        role_type: str = "executive"
        role_name: str = "new_custom_executive"

        # Act
        with patch(
            "scripts.create_role.Confirm.ask", return_value=True
        ) as mock_confirm:
            result: dict[str, Any] | None = get_role_data(
                role_type, role_name, sample_role_library
            )
            mock_confirm.assert_called_once()

        # Assert
        assert result == {}  # Returns empty dict for confirmed new role

    def test_get_custom_role_denied(self, sample_role_library: dict[str, Any]) -> None:
        """Test getting custom role when user denies creation."""
        # Arrange
        role_type: str = "specialist"
        role_name: str = "new_custom_specialist"

        # Act
        with patch(
            "scripts.create_role.Confirm.ask", return_value=False
        ) as mock_confirm:
            result: dict[str, Any] | None = get_role_data(
                role_type, role_name, sample_role_library
            )
            mock_confirm.assert_called_once()

        # Assert
        assert result is None  # Returns None if user denies new role creation


class TestGenerateSynthesisInstructions:
    """Test cases for generate_synthesis_instructions function."""

    def test_generate_known_domains(self) -> None:
        """Test generating instructions for known tool domains."""
        # Arrange
        tool_domains: list[str] = ["aws", "python", "database"]

        # Act
        result: str = generate_synthesis_instructions(tool_domains)

        # Assert
        assert "@aws for infrastructure standards" in result
        assert "@python for coding standards" in result
        assert "@database for data management best practices" in result

    def test_generate_unknown_domains(self) -> None:
        """Test generating instructions for unknown tool domains."""
        # Arrange
        tool_domains: list[str] = ["unknown_domain"]

        # Act
        result: str = generate_synthesis_instructions(tool_domains)

        # Assert
        assert "@unknown_domain" in result
        assert "domain-specific standards" in result

    def test_generate_empty_domains(self) -> None:
        """Test generating instructions for empty domains (should use defaults)."""
        # Arrange
        tool_domains: list[str] = []

        # Act
        result: str = generate_synthesis_instructions(tool_domains)

        # Assert
        assert "@aws for infrastructure standards" in result
        assert "@python for coding standards" in result
        assert "@database for data management best practices" in result


class TestGenerateExecutiveRole:
    """Test cases for generate_executive_role function."""

    def test_generate_complete_executive_role(
        self, sample_role_library: dict[str, Any]
    ) -> None:
        """Test generating complete executive role from sample library data."""
        # Arrange
        role_name: str = "cmo"
        role_data: dict[str, Any] = sample_role_library["executive"][role_name]

        # Act
        result: str = generate_executive_role(role_name, role_data)

        # Assert
        assert "CMO" in result  # Title cased name
        assert role_data["identity"]["scope"] in result
        assert role_data["identity"]["seniority"] in result
        assert "Drive brand awareness" in result  # From objectives
        assert "@martech" in result  # From behaviors.tool_domains

    def test_generate_incomplete_executive_role_strict(self) -> None:
        """Test generating incomplete executive role in strict mode (should exit)."""
        # Arrange
        role_name: str = "test_incomplete_exec"
        # Missing several required buckets for strict mode
        incomplete_data: dict[str, Any] = {"identity": {"scope": "Global"}}

        # Act & Assert
        with pytest.raises(SystemExit) as excinfo:
            generate_executive_role(role_name, incomplete_data, strict=True)
        assert "Missing required executive bucket(s)" in str(excinfo.value)

    def test_generate_incomplete_executive_role_non_strict(self) -> None:
        """Test generating incomplete executive role in non-strict mode."""
        # Arrange
        role_name: str = "test_nonstrict_exec"
        incomplete_data: dict[str, Any] = {
            "identity": {"scope": "Regional Chapter"},
            "objectives": {"top_objectives": ["Grow membership"]},
            # Other buckets like influence, behaviors, motivations are missing
        }

        # Act
        result: str = generate_executive_role(role_name, incomplete_data, strict=False)

        # Assert
        assert "Test Nonstrict Exec" in result  # Title cased
        assert "Regional Chapter" in result
        assert "Grow membership" in result
        # Check for placeholder/default text for missing sections
        assert "{{comms_style_specifics}}" in result  # Placeholder from template


class TestGenerateSpecialistRole:
    """Test cases for generate_specialist_role function."""

    def test_generate_complete_specialist_role(
        self, sample_role_library: dict[str, Any]
    ) -> None:
        """Test generating complete specialist role from sample library data."""
        # Arrange
        role_name: str = "qa_lead"
        role_data: dict[str, Any] = sample_role_library["specialist"][role_name]

        # Act
        result: str = generate_specialist_role(role_name, role_data)

        # Assert
        assert "Qa Lead" in result  # Title cased name
        assert role_data["identity"]["seniority"] in result
        assert "Ensure quality standards" in result  # From objectives
        assert "ISO 9001" in result  # From standards
        assert "@testing" in result  # From behaviors.tool_domains

    def test_generate_incomplete_specialist_role_strict(self) -> None:
        """Test generating incomplete specialist role in strict mode (should exit)."""
        # Arrange
        role_name: str = "test_incomplete_spec"
        # Missing objectives and standards/behaviors for strict mode
        incomplete_data: dict[str, Any] = {"identity": {"scope": "API Security"}}

        # Act & Assert
        with pytest.raises(SystemExit) as excinfo:
            generate_specialist_role(role_name, incomplete_data, strict=True)
        assert "Missing required specialist bucket(s)" in str(excinfo.value)

    def test_generate_incomplete_specialist_role_non_strict(self) -> None:
        """Test generating incomplete specialist role in non-strict mode."""
        # Arrange
        role_name: str = "test_nonstrict_spec"
        incomplete_data: dict[str, Any] = {
            "identity": {"scope": "Component Testing"},
            # Missing objectives, standards, behaviors
        }

        # Act
        result: str = generate_specialist_role(role_name, incomplete_data, strict=False)

        # Assert
        assert "Test Nonstrict Spec" in result
        assert "Component Testing" in result
        # Check for placeholder/default text for missing sections
        assert "{{specific_quality_standard}}" in result  # Placeholder from template


class TestWriteRoleFile:
    """Test cases for write_role_file function."""

    def test_write_new_role_file(self, temp_output_dir: Path) -> None:
        """Test writing new role file to the correct directory structure."""
        # Arrange
        role_name: str = "brand_new_role"
        content: str = "# Content for brand_new_role\n---\nDetails here."
        expected_dir = temp_output_dir / ".cursor" / "rules" / "roles" / "custom"

        # Act
        result_path: Path = write_role_file(role_name, content, temp_output_dir)

        # Assert
        assert result_path.exists()
        assert result_path.name == f"{role_name}.mdc"
        assert result_path.parent == expected_dir
        assert result_path.read_text(encoding="utf-8") == content

    def test_write_existing_file_overwrite_confirmed(
        self, temp_output_dir: Path
    ) -> None:
        """Test writing existing file when overwrite is confirmed by user."""
        # Arrange
        role_name: str = "existing_role_to_overwrite"
        new_content: str = "## New Overwritten Content\nThis is it."
        role_dir = temp_output_dir / ".cursor" / "rules" / "roles" / "custom"
        role_dir.mkdir(parents=True, exist_ok=True)
        existing_file_path: Path = role_dir / f"{role_name}.mdc"
        existing_file_path.write_text("Original content here.", encoding="utf-8")

        # Act
        with patch(
            "scripts.create_role.Confirm.ask", return_value=True
        ) as mock_confirm:
            result_path: Path = write_role_file(role_name, new_content, temp_output_dir)
            mock_confirm.assert_called_once()

        # Assert
        assert result_path.exists()
        assert result_path.read_text(encoding="utf-8") == new_content

    def test_write_existing_file_overwrite_denied(self, temp_output_dir: Path) -> None:
        """Test writing existing file when overwrite is denied by user (should exit)."""
        # Arrange
        role_name: str = "existing_role_no_overwrite"
        new_content: str = "This content should not be written."
        role_dir = temp_output_dir / ".cursor" / "rules" / "roles" / "custom"
        role_dir.mkdir(parents=True, exist_ok=True)
        existing_file_path: Path = role_dir / f"{role_name}.mdc"
        original_content = "This is the original, sacred content."
        existing_file_path.write_text(original_content, encoding="utf-8")

        # Act & Assert
        with patch(
            "scripts.create_role.Confirm.ask", return_value=False
        ) as mock_confirm:
            with pytest.raises(SystemExit) as excinfo:
                write_role_file(role_name, new_content, temp_output_dir)
            mock_confirm.assert_called_once()
            assert "File already exists and overwrite not confirmed" in str(
                excinfo.value
            )

        # Verify original file is untouched
        assert existing_file_path.read_text(encoding="utf-8") == original_content


class TestTemplateLoading:
    """Test cases for template loading functions."""

    def test_load_executive_template(self) -> None:
        """Test loading executive role template content."""
        # Act
        template_content: str = get_executive_template()

        # Assert
        assert isinstance(template_content, str)
        assert "rule_type: Agent Requested" in template_content
        assert "{title}" in template_content
        assert "Identity & Context" in template_content
        assert "Objectives, KPIs & Mandate" in template_content
        assert "Output Template" in template_content

    def test_load_specialist_template(self) -> None:
        """Test loading specialist role template content."""
        # Act
        template_content: str = get_specialist_template()

        # Assert
        assert isinstance(template_content, str)
        assert "rule_type: Agent Requested" in template_content
        assert "{title}" in template_content
        assert "Identity & Context" in template_content
        assert "Objectives & Quality Standards" in template_content
        assert "Output Template" in template_content

    def test_load_template_direct_valid(self) -> None:
        """Test loading template directly by valid name."""
        # Act
        template_content: str = load_template(
            "executive_role"
        )  # Assuming this is a valid key

        # Assert
        assert isinstance(template_content, str)
        assert "rule_type: Agent Requested" in template_content

    def test_load_nonexistent_template(self) -> None:
        """Test loading nonexistent template raises SystemExit."""
        # Act & Assert
        with pytest.raises(SystemExit) as excinfo:
            load_template("this_template_does_not_exist_hopefully")
        assert "Template 'this_template_does_not_exist_hopefully' not found." in str(
            excinfo.value
        )


class TestConstants:
    """Test cases for module constants."""

    def test_valid_role_types(self) -> None:
        """Test that valid role types (VALID_ROLE_TYPES) are defined correctly."""
        # Assert
        assert "executive" in VALID_ROLE_TYPES
        assert "specialist" in VALID_ROLE_TYPES
        assert len(VALID_ROLE_TYPES) == 2

    def test_required_executive_buckets(self) -> None:
        """Test REQUIRED_EXECUTIVE_BUCKETS constant."""
        # Assert
        expected_buckets: list[str] = [
            "identity",
            "objectives",
            "influence",
            "behaviors",
            "motivations",
        ]
        assert all(bucket in REQUIRED_EXECUTIVE_BUCKETS for bucket in expected_buckets)
        assert len(REQUIRED_EXECUTIVE_BUCKETS) == len(expected_buckets)

    def test_required_specialist_buckets(self) -> None:
        """Test REQUIRED_SPECIALIST_BUCKETS constant."""
        # Assert
        # Note: Validation logic checks for identity, objectives, AND (standards OR behaviors)
        # The constant itself might just list all possible top-level fields for specialists.
        expected_top_level_keys = [
            "identity",
            "objectives",
            "standards",
            "behaviors",
            "gates",
        ]
        assert all(
            bucket in REQUIRED_SPECIALIST_BUCKETS for bucket in expected_top_level_keys
        )
        # The actual requirement check is more nuanced (e.g. standards OR behaviors)
        # This test just checks the content of the constant.


# Helper function for mocking open, if needed by other tests not using temp files directly
def mock_open_invalid_json_global() -> (
    Mock
):  # Renamed to avoid conflict if used elsewhere
    """Mock open function that returns invalid JSON data."""
    return mock_open(read_data="{ this is not valid json: oops }")


def mock_open_valid_registry_file_global(file_path: Path) -> Mock:  # Renamed
    """Mock open to return content from a specific file (e.g., a temp file)."""
    content = file_path.read_text(encoding="utf-8")
    return mock_open(read_data=content)


@pytest.fixture(autouse=True)
def cleanup_temp_files_global() -> Generator[None, None, None]:  # Renamed
    """Ensure temporary files are cleaned up after tests if any were manually managed."""
    # Primarily for tests that might use tempfile.NamedTemporaryFile with delete=False
    # and don't clean up within the test itself.
    # For most tests using tmp_path fixture or with-statements, this is not strictly needed.
    created_files: list[Path] = []  # If tests add to this list, they will be cleaned.

    original_named_temp_file = tempfile.NamedTemporaryFile

    def new_named_temp_file(*args: Any, **kwargs: Any) -> Any:
        fp = original_named_temp_file(*args, **kwargs)
        if kwargs.get("delete") is False:
            created_files.append(Path(fp.name))
        return fp

    # Monkeypatch tempfile.NamedTemporaryFile if you want to track files this way
    # For this example, assuming direct cleanup or tmp_path is used more often.
    # tempfile.NamedTemporaryFile = new_named_temp_file

    yield

    # tempfile.NamedTemporaryFile = original_named_temp_file # Restore

    for file_path in created_files:
        if file_path.exists():
            try:
                file_path.unlink()
            except OSError:
                pass  # Log error if necessary
