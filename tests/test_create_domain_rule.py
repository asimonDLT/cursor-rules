#!/usr/bin/env python3
"""
Tests for domain rule creation script.
Uses pytest with AAA pattern and fixtures for setup/teardown.
"""

import json
import tempfile
from pathlib import Path
from typing import Dict
from unittest.mock import patch

import pytest

from scripts.domains.create_domain_rule import (
    VALID_CATEGORIES,
    create_domain_rule_file,
    generate_domain_rule_content,
    load_domain_metadata,
    load_domain_rule_template,
    sanitize_name,
    validate_input,
)


@pytest.fixture
def sample_tool_registry() -> Dict:
    """Create a sample tool registry for testing."""
    return {
        "domain_metadata": {
            "backend": {"description": "Backend development standards"},
            "frontend": {"description": "Frontend development standards"},
            "martech": {"description": "Marketing technology standards"},
        }
    }


@pytest.fixture
def temp_registry_file(sample_tool_registry: Dict) -> Path:
    """Create a temporary registry file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_tool_registry, f, indent=2)
        return Path(f.name)


@pytest.fixture
def temp_output_dir() -> Path:
    """Create a temporary output directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


class TestValidateInput:
    """Test cases for validate_input function."""
    
    def test_validate_safe_input(self):
        """Test validation of safe input."""
        # Arrange
        safe_input = "backend_api"
        field_name = "test_field"
        
        # Act
        result = validate_input(safe_input, field_name)
        
        # Assert
        assert result is True
    
    def test_validate_dangerous_patterns(self):
        """Test validation rejects dangerous patterns."""
        # Arrange
        dangerous_inputs = [
            "{{malicious}}",
            "<script>alert('xss')</script>",
            "javascript:void(0)",
            "data:text/html,<script>",
            "${injection}",
            "`command`"
        ]
        
        for dangerous_input in dangerous_inputs:
            # Act
            result = validate_input(dangerous_input, "test_field")
            
            # Assert
            assert result is False, f"Should reject dangerous input: {dangerous_input}"
    
    def test_validate_excessive_length(self):
        """Test validation rejects excessively long input."""
        # Arrange
        long_input = "a" * 101  # Exceeds MAX_INPUT_LENGTH of 100
        
        # Act
        result = validate_input(long_input, "test_field")
        
        # Assert
        assert result is False


class TestSanitizeName:
    """Test cases for sanitize_name function."""
    
    def test_sanitize_valid_name(self):
        """Test sanitization of valid name."""
        # Arrange
        valid_name = "backend_api"
        
        # Act
        result = sanitize_name(valid_name)
        
        # Assert
        assert result == "backend_api"
    
    def test_sanitize_mixed_case(self):
        """Test sanitization converts to lowercase."""
        # Arrange
        mixed_case = "BackEnd_API"
        
        # Act
        result = sanitize_name(mixed_case)
        
        # Assert
        assert result == "backend_api"
    
    def test_sanitize_special_characters(self):
        """Test sanitization removes special characters."""
        # Arrange
        special_chars = "backend@api#test"
        
        # Act
        result = sanitize_name(special_chars)
        
        # Assert
        assert result == "backendapitest"
    
    def test_sanitize_preserves_hyphens_underscores(self):
        """Test sanitization preserves hyphens and underscores."""
        # Arrange
        name_with_separators = "backend-api_test"
        
        # Act
        result = sanitize_name(name_with_separators)
        
        # Assert
        assert result == "backend-api_test"
    
    def test_sanitize_empty_result_exits(self):
        """Test sanitization exits on empty result."""
        # Arrange
        invalid_name = "@#$%"
        
        # Act & Assert
        with pytest.raises(SystemExit):
            sanitize_name(invalid_name)
    
    def test_sanitize_dangerous_input_exits(self):
        """Test sanitization exits on dangerous input."""
        # Arrange
        dangerous_name = "{{malicious}}"
        
        # Act & Assert
        with pytest.raises(SystemExit):
            sanitize_name(dangerous_name)


class TestLoadDomainMetadata:
    """Test cases for load_domain_metadata function."""
    
    def test_load_existing_domain_metadata(self, sample_tool_registry: Dict):
        """Test loading metadata for existing domain."""
        # Arrange
        domain_name = "backend"
        
        # Act
        with patch('builtins.open', mock_open_registry(sample_tool_registry)):
            with patch('pathlib.Path.exists', return_value=True):
                result = load_domain_metadata(domain_name)
        
        # Assert
        assert result == {"description": "Backend development standards"}
    
    def test_load_nonexistent_domain_metadata(self, sample_tool_registry: Dict):
        """Test loading metadata for non-existent domain."""
        # Arrange
        domain_name = "nonexistent"
        
        # Act
        with patch('builtins.open', mock_open_registry(sample_tool_registry)):
            with patch('pathlib.Path.exists', return_value=True):
                result = load_domain_metadata(domain_name)
        
        # Assert
        assert result is None
    
    def test_load_metadata_missing_registry(self):
        """Test loading metadata when registry file is missing."""
        # Arrange
        domain_name = "backend"
        
        # Act
        with patch('pathlib.Path.exists', return_value=False):
            result = load_domain_metadata(domain_name)
        
        # Assert
        assert result is None
    
    def test_load_metadata_invalid_json(self):
        """Test loading metadata with invalid JSON."""
        # Arrange
        domain_name = "backend"
        
        # Act
        with patch('builtins.open', mock_open_invalid_json()):
            with patch('pathlib.Path.exists', return_value=True):
                result = load_domain_metadata(domain_name)
        
        # Assert
        assert result is None


def mock_open_invalid_json():
    """Mock open function that returns invalid JSON."""
    from unittest.mock import mock_open
    return mock_open(read_data="{ invalid json }")


def mock_open_registry(registry_data: Dict):
    """Mock open function that returns valid registry JSON."""
    from unittest.mock import mock_open
    return mock_open(read_data=json.dumps(registry_data))


class TestGenerateDomainRuleContent:
    """Test cases for generate_domain_rule_content function."""
    
    def test_generate_backend_content(self):
        """Test generating content for backend category."""
        # Arrange
        name = "api_design"
        category = "backend"
        description = "API design standards"
        
        # Act
        result = generate_domain_rule_content(name, category, description)
        
        # Assert
        assert "Api Design" in result  # Title case conversion changes "API" to "Api"
        assert "API design standards" in result
        assert "scalability and maintainability" in result
        assert "RESTful API design principles" in result
    
    def test_generate_frontend_content(self):
        """Test generating content for frontend category."""
        # Arrange
        name = "ui_components"
        category = "frontend"
        
        # Act
        result = generate_domain_rule_content(name, category)
        
        # Assert
        assert "Ui Components" in result
        assert "user experience and performance" in result
        assert "WCAG 2.1 AA accessibility" in result
    
    def test_generate_martech_content(self):
        """Test generating content for martech category."""
        # Arrange
        name = "analytics"
        category = "martech"
        
        # Act
        result = generate_domain_rule_content(name, category)
        
        # Assert
        assert "Analytics" in result
        assert "user privacy and consent" in result
        assert "GDPR and privacy compliance" in result
        assert "tag management" in result
    
    def test_generate_with_custom_description(self):
        """Test generating content with custom description."""
        # Arrange
        name = "test_domain"
        category = "backend"
        custom_description = "Custom test description"
        
        # Act
        result = generate_domain_rule_content(name, category, custom_description)
        
        # Assert
        assert custom_description in result
    
    def test_generate_unknown_category(self):
        """Test generating content for unknown category."""
        # Arrange
        name = "test_domain"
        category = "unknown"
        
        # Act
        result = generate_domain_rule_content(name, category)
        
        # Assert
        assert "Test Domain" in result
        assert "Standards and best practices for test domain" in result


class TestCreateDomainRuleFile:
    """Test cases for create_domain_rule_file function."""
    
    def test_create_valid_domain_rule(self, temp_output_dir: Path):
        """Test creating a valid domain rule file."""
        # Arrange
        name = "test_domain"
        category = "backend"
        description = "Test description"
        
        # Act
        result_path = create_domain_rule_file(
            name, category, description, str(temp_output_dir)
        )
        
        # Assert
        assert result_path.exists()
        assert result_path.name == "test_domain.mdc"
        assert result_path.parent.name == "backend"
        
        # Check file content
        content = result_path.read_text(encoding="utf-8")
        assert "Test description" in content
        assert "Test Domain" in content
    
    def test_create_with_invalid_category(self, temp_output_dir: Path):
        """Test creating domain rule with invalid category."""
        # Arrange
        name = "test_domain"
        category = "invalid_category"
        
        # Act & Assert
        with patch('scripts.domains.create_domain_rule.Confirm.ask', return_value=False):
            with pytest.raises(SystemExit):
                create_domain_rule_file(name, category, output_base_dir=str(temp_output_dir))
    
    def test_create_with_invalid_category_confirmed(self, temp_output_dir: Path):
        """Test creating domain rule with invalid category when confirmed."""
        # Arrange
        name = "test_domain"
        category = "invalid_category"
        
        # Act
        with patch('scripts.domains.create_domain_rule.Confirm.ask', return_value=True):
            result_path = create_domain_rule_file(
                name, category, output_base_dir=str(temp_output_dir)
            )
        
        # Assert
        assert result_path.exists()
        assert result_path.parent.name == "invalid_category"
    
    def test_create_existing_file_overwrite_denied(self, temp_output_dir: Path):
        """Test creating domain rule when file exists and overwrite is denied."""
        # Arrange
        name = "test_domain"
        category = "backend"
        
        # Create existing file
        existing_dir = temp_output_dir / "backend"
        existing_dir.mkdir()
        existing_file = existing_dir / "test_domain.mdc"
        existing_file.write_text("existing content")
        
        # Act & Assert
        with patch('scripts.domains.create_domain_rule.Confirm.ask', return_value=False):
            with pytest.raises(SystemExit):
                create_domain_rule_file(name, category, output_base_dir=str(temp_output_dir))
    
    def test_create_existing_file_overwrite_confirmed(self, temp_output_dir: Path):
        """Test creating domain rule when file exists and overwrite is confirmed."""
        # Arrange
        name = "test_domain"
        category = "backend"
        
        # Create existing file
        existing_dir = temp_output_dir / "backend"
        existing_dir.mkdir()
        existing_file = existing_dir / "test_domain.mdc"
        existing_file.write_text("existing content")
        
        # Act
        with patch('scripts.domains.create_domain_rule.Confirm.ask', return_value=True):
            result_path = create_domain_rule_file(
                name, category, output_base_dir=str(temp_output_dir)
            )
        
        # Assert
        assert result_path.exists()
        content = result_path.read_text(encoding="utf-8")
        assert "existing content" not in content
        assert "Test Domain" in content
    
    def test_create_with_dangerous_name(self, temp_output_dir: Path):
        """Test creating domain rule with dangerous name."""
        # Arrange
        dangerous_name = "{{malicious}}"
        category = "backend"
        
        # Act & Assert
        with pytest.raises(SystemExit):
            create_domain_rule_file(dangerous_name, category, output_base_dir=str(temp_output_dir))


class TestTemplateLoading:
    """Test cases for template loading functions."""
    
    def test_load_domain_rule_template(self):
        """Test loading domain rule template."""
        # Act
        template = load_domain_rule_template()
        
        # Assert
        assert template is not None
        assert "rule_type: Agent Requested" in template
        assert "{title}" in template
        assert "Core Principles" in template
        assert "Best Practices" in template
        assert "Standards & Guidelines" in template
        assert "Common Patterns" in template


class TestConstants:
    """Test cases for module constants."""
    
    def test_valid_categories_contains_expected(self):
        """Test that VALID_CATEGORIES contains expected categories."""
        # Arrange
        expected_categories = [
            "frontend", "backend", "cloud", "data", 
            "security", "docs", "martech"
        ]
        
        # Act & Assert
        for category in expected_categories:
            assert category in VALID_CATEGORIES
    
    def test_dangerous_patterns_imported(self):
        """Test that dangerous input patterns are defined."""
        # Arrange & Act
        from scripts.domains.create_domain_rule import DANGEROUS_INPUT_PATTERNS
        
        # Assert
        assert len(DANGEROUS_INPUT_PATTERNS) > 0
        assert "{{" in DANGEROUS_INPUT_PATTERNS
        assert "<script" in DANGEROUS_INPUT_PATTERNS


@pytest.fixture(autouse=True)
def cleanup_temp_files():
    """Cleanup temporary files after each test."""
    yield
    # Cleanup happens automatically with tempfile context managers 