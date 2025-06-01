#!/usr/bin/env python3
"""
Tests for domain rule creation script.
Uses pytest with AAA pattern and fixtures for setup/teardown.
"""

import json
import tempfile
from collections.abc import Generator
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, mock_open, patch

import pytest
from typer.testing import CliRunner

from scripts.domains.create_domain_rule import (
    DANGEROUS_INPUT_PATTERNS,
    VALID_CATEGORIES,
    create_domain_rule_file,
    generate_domain_rule_content,
    load_domain_metadata,
    load_domain_rule_template,
    sanitize_name,
    validate_input,
)


@pytest.fixture
def runner() -> CliRunner:
    """Fixture for invoking command-line interfaces."""
    return CliRunner()


@pytest.fixture
def sample_tool_registry() -> dict[str, Any]:
    """Create a sample tool registry for testing."""
    return {
        "domain_metadata": {
            "backend": {"description": "Backend development standards"},
            "frontend": {"description": "Frontend development standards"},
            "martech": {"description": "Marketing technology standards"},
        }
    }


@pytest.fixture
def temp_registry_file(
    sample_tool_registry: dict[str, Any],
) -> Generator[Path, None, None]:
    """Create a temporary registry file for testing."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        file_path = Path(f.name)
        json.dump(sample_tool_registry, f, indent=2)
    yield file_path
    file_path.unlink()


@pytest.fixture
def temp_output_dir() -> Generator[Path, None, None]:
    """Create a temporary output directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


class TestValidateInput:
    """Test cases for validate_input function."""

    def test_validate_safe_input(self) -> None:
        """Test validation of safe input."""
        # Arrange
        safe_input = "backend_api"
        field_name = "test_field"

        # Act
        result: bool = validate_input(safe_input, field_name)

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
            result: bool = validate_input(dangerous_input, "test_field")

            # Assert
            assert result is False, f"Should reject: {dangerous_input}"

    def test_validate_excessive_length(self) -> None:
        """Test validation rejects excessively long input."""
        # Arrange
        long_input = "a" * 101  # Exceeds MAX_INPUT_LENGTH of 100

        # Act
        result: bool = validate_input(long_input, "test_field")

        # Assert
        assert result is False


class TestSanitizeName:
    """Test cases for sanitize_name function."""

    def test_sanitize_valid_name(self) -> None:
        """Test sanitization of valid name."""
        # Arrange
        valid_name = "backend_api"

        # Act
        result: str = sanitize_name(valid_name)

        # Assert
        assert result == "backend_api"

    def test_sanitize_mixed_case(self) -> None:
        """Test sanitization converts to lowercase."""
        # Arrange
        mixed_case = "BackEnd_API"

        # Act
        result: str = sanitize_name(mixed_case)

        # Assert
        assert result == "backend_api"

    def test_sanitize_special_characters(self) -> None:
        """Test sanitization removes special characters."""
        # Arrange
        special_chars = "backend@api#test"

        # Act
        result: str = sanitize_name(special_chars)

        # Assert
        assert result == "backendapitest"

    def test_sanitize_preserves_hyphens_underscores(self) -> None:
        """Test sanitization preserves hyphens and underscores."""
        # Arrange
        name_with_separators = "backend-api_test"

        # Act
        result: str = sanitize_name(name_with_separators)

        # Assert
        assert result == "backend-api_test"

    def test_sanitize_empty_result_exits(self) -> None:
        """Test sanitization exits on empty result."""
        # Arrange
        invalid_name = "@#$%"

        # Act & Assert
        with pytest.raises(SystemExit):
            sanitize_name(invalid_name)

    def test_sanitize_dangerous_input_exits(self) -> None:
        """Test sanitization exits on dangerous input."""
        # Arrange
        dangerous_name = "{{malicious}}"

        # Act & Assert
        with pytest.raises(SystemExit):
            sanitize_name(dangerous_name)


def mock_open_registry(registry_data: dict[str, Any]) -> MagicMock:
    """Mock open function that returns valid registry JSON."""
    return mock_open(read_data=json.dumps(registry_data))


def mock_open_invalid_json() -> MagicMock:
    """Mock open function that returns invalid JSON."""
    return mock_open(read_data="{ invalid json }")


class TestLoadDomainMetadata:
    """Test cases for load_domain_metadata function."""

    def test_load_existing_domain_metadata(
        self, sample_tool_registry: dict[str, Any], temp_registry_file: Path
    ) -> None:
        """Test loading metadata for existing domain."""
        # Arrange
        domain_name = "backend"

        # Act
        # Patch 'TOOL_REGISTRY_PATH' in the module where load_domain_metadata is defined
        with patch(
            "scripts.domains.create_domain_rule.TOOL_REGISTRY_PATH", temp_registry_file
        ):
            result: dict[str, Any] | None = load_domain_metadata(domain_name)

        # Assert
        assert result == {"description": "Backend development standards"}

    def test_load_nonexistent_domain_metadata(
        self, sample_tool_registry: dict[str, Any], temp_registry_file: Path
    ) -> None:
        """Test loading metadata for non-existent domain."""
        # Arrange
        domain_name = "nonexistent"

        # Act
        with patch(
            "scripts.domains.create_domain_rule.TOOL_REGISTRY_PATH", temp_registry_file
        ):
            result: dict[str, Any] | None = load_domain_metadata(domain_name)

        # Assert
        assert result is None

    def test_load_metadata_missing_registry(self) -> None:
        """Test loading metadata when registry file is missing."""
        # Arrange
        domain_name = "backend"
        non_existent_path = Path("non_existent_registry.json")

        # Act
        with patch(
            "scripts.domains.create_domain_rule.TOOL_REGISTRY_PATH", non_existent_path
        ):
            result: dict[str, Any] | None = load_domain_metadata(domain_name)

        # Assert
        assert result is None

    def test_load_metadata_invalid_json(self, temp_output_dir: Path) -> None:
        """Test loading metadata with invalid JSON."""
        # Arrange
        domain_name = "backend"
        invalid_json_path = temp_output_dir / "invalid.json"
        with open(invalid_json_path, "w", encoding="utf-8") as f:
            f.write("{ invalid json }")

        # Act
        with patch(
            "scripts.domains.create_domain_rule.TOOL_REGISTRY_PATH", invalid_json_path
        ):
            result: dict[str, Any] | None = load_domain_metadata(domain_name)

        # Assert
        assert result is None


class TestGenerateDomainRuleContent:
    """Test cases for generate_domain_rule_content function."""

    def test_generate_backend_content(self) -> None:
        """Test generating content for backend category."""
        # Arrange
        name = "api_design"
        category = "backend"
        description = "API design standards"

        # Act
        result: str = generate_domain_rule_content(name, category, description)

        # Assert
        assert "Api Design" in result  # Title case conversion
        assert "API design standards" in result
        assert "scalability and maintainability" in result
        assert "RESTful API design principles" in result

    def test_generate_frontend_content(self) -> None:
        """Test generating content for frontend category."""
        # Arrange
        name = "ui_components"
        category = "frontend"
        # Using default description
        # Act
        result: str = generate_domain_rule_content(name, category)

        # Assert
        assert "Ui Components" in result
        assert "user experience and performance" in result
        assert "WCAG 2.1 AA accessibility" in result

    def test_generate_martech_content(self) -> None:
        """Test generating content for martech category."""
        # Arrange
        name = "analytics"
        category = "martech"
        # Using default description
        # Act
        result: str = generate_domain_rule_content(name, category)

        # Assert
        assert "Analytics" in result
        assert "user privacy and consent" in result
        assert "GDPR and privacy compliance" in result
        assert "tag management" in result

    def test_generate_with_custom_description(self) -> None:
        """Test generating content with custom description."""
        # Arrange
        name = "test_domain"
        category = "backend"
        custom_description = "Custom test description for this specific domain rule."

        # Act
        result: str = generate_domain_rule_content(name, category, custom_description)

        # Assert
        assert custom_description in result

    def test_generate_unknown_category(self) -> None:
        """Test generating content for unknown category."""
        # Arrange
        name = "test_domain"
        category = "new_custom_category"
        # Using default description
        # Act
        result: str = generate_domain_rule_content(name, category)

        # Assert
        assert "Test Domain" in result
        assert (
            f"Standards and best practices for {name} in the {category} category."
            in result
        )


class TestCreateDomainRuleFile:
    """Test cases for create_domain_rule_file function."""

    def test_create_valid_domain_rule(self, temp_output_dir: Path) -> None:
        """Test creating a valid domain rule file."""
        # Arrange
        name = "test_domain"
        category = "backend"
        description = "Test description for a backend domain rule."

        # Act
        result_path: Path = create_domain_rule_file(
            name, category, description, str(temp_output_dir)
        )

        # Assert
        assert result_path.exists()
        assert result_path.name == "test_domain.mdc"
        assert result_path.parent.name == "backend"
        # Corrected assertion for the full path
        expected_base: Path = temp_output_dir / ".cursor" / "rules" / "domains"
        assert result_path.parent.parent == expected_base

        # Check file content
        content: str = result_path.read_text(encoding="utf-8")
        assert description in content
        assert "Test Domain" in content  # Check titleized name

    def test_create_with_invalid_category(self, temp_output_dir: Path) -> None:
        """Test creating domain rule with invalid category (user denies)."""
        # Arrange
        name = "test_domain"
        category = "category_not_in_list"

        # Act & Assert
        with patch(
            "scripts.domains.create_domain_rule.Confirm.ask", return_value=False
        ) as mock_confirm:
            with pytest.raises(SystemExit):
                create_domain_rule_file(
                    name,
                    category,
                    description="Test desc",
                    output_base_dir=str(temp_output_dir),
                )
            mock_confirm.assert_called_once()

    def test_create_with_invalid_category_confirmed(
        self, temp_output_dir: Path
    ) -> None:
        """Test creating domain rule with invalid category when confirmed by user."""
        # Arrange
        name = "test_domain"
        category = "new_confirmed_category"

        # Act
        with patch(
            "scripts.domains.create_domain_rule.Confirm.ask", return_value=True
        ) as mock_confirm:
            result_path: Path = create_domain_rule_file(
                name,
                category,
                description="A new category rule",
                output_base_dir=str(temp_output_dir),
            )
            mock_confirm.assert_called_once()

        # Assert
        assert result_path.exists()
        assert result_path.parent.name == category

    def test_create_existing_file_overwrite_denied(self, temp_output_dir: Path) -> None:
        """Test creating domain rule when file exists and overwrite is denied."""
        # Arrange
        name = "existing_domain"
        category = "backend"
        output_rules_dir: Path = temp_output_dir / ".cursor" / "rules" / "domains"
        existing_dir: Path = output_rules_dir / category
        existing_dir.mkdir(parents=True, exist_ok=True)
        existing_file: Path = existing_dir / f"{name}.mdc"
        original_content = "original pre-existing content"
        existing_file.write_text(original_content, encoding="utf-8")

        # Act & Assert
        with patch(
            "scripts.domains.create_domain_rule.Confirm.ask", return_value=False
        ) as mock_confirm:
            with pytest.raises(SystemExit):
                create_domain_rule_file(
                    name,
                    category,
                    description="Attempting to overwrite",
                    output_base_dir=str(temp_output_dir),
                )
            mock_confirm.assert_called_once()
        # Check that original content remains
        assert existing_file.read_text(encoding="utf-8") == original_content

    def test_create_existing_file_overwrite_confirmed(
        self, temp_output_dir: Path
    ) -> None:
        """Test creating domain rule when file exists and overwrite is confirmed."""
        # Arrange
        name = "overwrite_domain"
        category = "frontend"
        description = "This is the new overwritten content."
        output_rules_dir: Path = temp_output_dir / ".cursor" / "rules" / "domains"
        existing_dir: Path = output_rules_dir / category
        existing_dir.mkdir(parents=True, exist_ok=True)
        existing_file: Path = existing_dir / f"{name}.mdc"
        original_content_before_overwrite = "original content before overwrite"
        existing_file.write_text(original_content_before_overwrite, encoding="utf-8")

        # Act
        with patch(
            "scripts.domains.create_domain_rule.Confirm.ask", return_value=True
        ) as mock_confirm:
            result_path: Path = create_domain_rule_file(
                name, category, description, str(temp_output_dir)
            )
            mock_confirm.assert_called_once()

        # Assert
        assert result_path.exists()
        content: str = result_path.read_text(encoding="utf-8")
        assert original_content_before_overwrite not in content
        assert description in content
        assert "Overwrite Domain" in content  # Check titleized name

    def test_create_with_dangerous_name(self, temp_output_dir: Path) -> None:
        """Test creating domain rule with dangerous name pattern."""
        # Arrange
        dangerous_name = "{{payload}}"
        category = "backend"

        # Act & Assert
        with pytest.raises(SystemExit):
            create_domain_rule_file(
                dangerous_name,
                category,
                description="Dangerous name test",
                output_base_dir=str(temp_output_dir),
            )


class TestTemplateLoading:
    """Test cases for template loading functions."""

    def test_load_domain_rule_template(self) -> None:
        """Test loading domain rule template from file."""
        # Act
        template_content: str | None = load_domain_rule_template()

        # Assert
        assert template_content is not None
        assert "rule_type: Agent Requested" in template_content
        assert "{title}" in template_content
        assert "{description}" in template_content
        assert "Core Principles" in template_content
        assert "Best Practices" in template_content
        assert "Standards & Guidelines" in template_content
        assert "Common Patterns" in template_content
        assert "Anti-Patterns" in template_content
        assert "Security Considerations" in template_content
        assert "Performance Considerations" in template_content
        assert "Key Metrics & Observability" in template_content
        assert "{{example_metric}}" in template_content
        assert "Tooling & Ecosystem" in template_content
        assert "{{example_tool}}" in template_content
        assert "Further Reading" in template_content
        assert "[{{link_text}}]({{link_url}})" in template_content


class TestConstants:
    """Test cases for module constants."""

    def test_valid_categories_contains_expected(self) -> None:
        """Test that VALID_CATEGORIES contains expected categories."""
        # Arrange
        expected_categories: list[str] = [
            "frontend",
            "backend",
            "cloud",
            "data",
            "security",
            "docs",
            "martech",
            "tools",
        ]

        # Act & Assert
        for category_item in expected_categories:
            assert category_item in VALID_CATEGORIES

    def test_dangerous_patterns_imported(self) -> None:
        """Test that dangerous input patterns are defined and imported."""
        # Arrange & Act
        # DANGEROUS_INPUT_PATTERNS is imported at the module level

        # Assert
        assert isinstance(DANGEROUS_INPUT_PATTERNS, list)
        assert len(DANGEROUS_INPUT_PATTERNS) > 0
        # Check for presence of some known dangerous patterns
        assert "{{" in DANGEROUS_INPUT_PATTERNS
        assert "<script" in DANGEROUS_INPUT_PATTERNS
        assert "javascript:" in DANGEROUS_INPUT_PATTERNS
        assert "`" in DANGEROUS_INPUT_PATTERNS  # backticks


@pytest.fixture(autouse=True)
def cleanup_temp_files() -> Generator[None, None, None]:
    """Ensure temporary files created during tests are cleaned up."""
    # This fixture can be expanded if specific cleanup beyond
    # what tempfile.TemporaryDirectory handles is needed.
    yield
    # No specific cleanup action needed here if using tempfile context managers properly.
