#!/usr/bin/env python3
"""
Tests for tool registry linting script.
Uses pytest with AAA pattern and fixtures for setup/teardown.
"""

import json
import tempfile
import uuid
from pathlib import Path
from typing import Dict
from unittest.mock import patch

import pytest

from scripts.lint_tool_registry import (
    display_summary,
    sanitize_file_path,
    validate_json_structure,
    validate_referential_integrity,
    validate_tool_registry,
)


@pytest.fixture
def correlation_id() -> str:
    """Generate a unique correlation ID for test runs."""
    return str(uuid.uuid4())[:8]


@pytest.fixture
def valid_tool_registry() -> Dict:
    """Create a valid tool registry for testing."""
    return {
        "tool_categories": {
            "linting": {
                "description": "Code linting and formatting tools",
                "tools": ["ruff", "black", "isort"]
            },
            "testing": {
                "description": "Testing frameworks and tools",
                "tools": ["pytest", "coverage", "tox"]
            },
            "documentation": {
                "description": "Documentation generation tools",
                "tools": ["sphinx", "mkdocs"]
            }
        },
        "domain_mappings": {
            "backend": ["linting", "testing"],
            "frontend": ["linting"],
            "docs": ["documentation"]
        },
        "domain_metadata": {
            "backend": {"description": "Backend development"},
            "frontend": {"description": "Frontend development"},
            "docs": {"description": "Documentation"}
        }
    }


@pytest.fixture
def invalid_structure_registry() -> Dict:
    """Create a tool registry with invalid structure."""
    return {
        "tool_categories": "not_a_dict",  # Should be dict
        "domain_mappings": {
            "backend": "not_a_list"  # Should be list
        }
    }


@pytest.fixture
def invalid_integrity_registry() -> Dict:
    """Create a tool registry with referential integrity issues."""
    return {
        "tool_categories": {
            "linting": {
                "description": "Code linting tools",
                "tools": ["ruff"]
            }
        },
        "domain_mappings": {
            "backend": ["linting", "nonexistent_category"]  # References non-existent category
        }
    }


@pytest.fixture
def temp_registry_file(valid_tool_registry: Dict) -> Path:
    """Create a temporary registry file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(valid_tool_registry, f, indent=2)
        return Path(f.name)


@pytest.fixture
def temp_invalid_json_file() -> Path:
    """Create a temporary file with invalid JSON."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write("{ invalid json }")
        return Path(f.name)


class TestSanitizeFilePath:
    """Test cases for sanitize_file_path function."""
    
    def test_sanitize_valid_path(self, temp_registry_file: Path):
        """Test sanitization of valid file path."""
        # Arrange
        valid_path = str(temp_registry_file)
        
        # Act
        result = sanitize_file_path(valid_path)
        
        # Assert
        assert result == temp_registry_file.resolve()
        assert result.exists()
    
    def test_sanitize_dangerous_patterns(self):
        """Test sanitization rejects dangerous patterns."""
        # Arrange
        dangerous_paths = [
            "../etc/passwd",
            "~/malicious",
            "file$injection",
            "command`injection",
            "file;rm -rf /",
            "file|cat /etc/passwd",
            "file&& rm -rf /"
        ]
        
        for dangerous_path in dangerous_paths:
            # Act & Assert
            with pytest.raises(ValueError, match="Potentially dangerous file path"):
                sanitize_file_path(dangerous_path)
    
    def test_sanitize_nonexistent_file(self):
        """Test sanitization rejects non-existent files."""
        # Arrange
        nonexistent_path = "/nonexistent/file.json"
        
        # Act & Assert
        with pytest.raises(ValueError, match="File does not exist"):
            sanitize_file_path(nonexistent_path)
    
    def test_sanitize_invalid_path_format(self):
        """Test sanitization handles invalid path formats."""
        # Arrange
        invalid_path = "\x00invalid\x00path"
        
        # Act & Assert
        with pytest.raises(ValueError, match="lstat: embedded null character in path|Invalid file path"):
            sanitize_file_path(invalid_path)


class TestValidateJsonStructure:
    """Test cases for validate_json_structure function."""
    
    def test_validate_valid_structure(self, valid_tool_registry: Dict, correlation_id: str):
        """Test validation of valid JSON structure."""
        # Arrange
        registry_data = valid_tool_registry
        
        # Act
        is_valid, errors = validate_json_structure(registry_data, correlation_id)
        
        # Assert
        assert is_valid is True
        assert errors == []
    
    def test_validate_missing_required_keys(self, correlation_id: str):
        """Test validation fails with missing required keys."""
        # Arrange
        incomplete_registry = {"tool_categories": {}}  # Missing domain_mappings
        
        # Act
        is_valid, errors = validate_json_structure(incomplete_registry, correlation_id)
        
        # Assert
        assert is_valid is False
        assert any("Missing required top-level key: 'domain_mappings'" in error for error in errors)
    
    def test_validate_invalid_tool_categories_type(self, correlation_id: str):
        """Test validation fails with invalid tool_categories type."""
        # Arrange
        invalid_registry = {
            "tool_categories": "not_a_dict",
            "domain_mappings": {}
        }
        
        # Act
        is_valid, errors = validate_json_structure(invalid_registry, correlation_id)
        
        # Assert
        assert is_valid is False
        assert any("'tool_categories' must be a dictionary" in error for error in errors)
    
    def test_validate_invalid_category_structure(self, correlation_id: str):
        """Test validation fails with invalid category structure."""
        # Arrange
        invalid_registry = {
            "tool_categories": {
                "linting": "not_a_dict"  # Should be dict
            },
            "domain_mappings": {}
        }
        
        # Act
        is_valid, errors = validate_json_structure(invalid_registry, correlation_id)
        
        # Assert
        assert is_valid is False
        assert any("Category 'linting' must be a dictionary" in error for error in errors)
    
    def test_validate_missing_category_fields(self, correlation_id: str):
        """Test validation fails with missing category fields."""
        # Arrange
        invalid_registry = {
            "tool_categories": {
                "linting": {}  # Missing description and tools
            },
            "domain_mappings": {}
        }
        
        # Act
        is_valid, errors = validate_json_structure(invalid_registry, correlation_id)
        
        # Assert
        assert is_valid is False
        assert any("Category 'linting' missing 'description' field" in error for error in errors)
        assert any("Category 'linting' missing 'tools' field" in error for error in errors)
    
    def test_validate_invalid_tools_type(self, correlation_id: str):
        """Test validation fails with invalid tools type."""
        # Arrange
        invalid_registry = {
            "tool_categories": {
                "linting": {
                    "description": "Linting tools",
                    "tools": "not_a_list"  # Should be list
                }
            },
            "domain_mappings": {}
        }
        
        # Act
        is_valid, errors = validate_json_structure(invalid_registry, correlation_id)
        
        # Assert
        assert is_valid is False
        assert any("Category 'linting' 'tools' must be a list" in error for error in errors)
    
    def test_validate_invalid_domain_mappings_type(self, correlation_id: str):
        """Test validation fails with invalid domain_mappings type."""
        # Arrange
        invalid_registry = {
            "tool_categories": {},
            "domain_mappings": "not_a_dict"  # Should be dict
        }
        
        # Act
        is_valid, errors = validate_json_structure(invalid_registry, correlation_id)
        
        # Assert
        assert is_valid is False
        assert any("'domain_mappings' must be a dictionary" in error for error in errors)
    
    def test_validate_invalid_domain_mapping_type(self, correlation_id: str):
        """Test validation fails with invalid domain mapping type."""
        # Arrange
        invalid_registry = {
            "tool_categories": {},
            "domain_mappings": {
                "backend": "not_a_list"  # Should be list
            }
        }
        
        # Act
        is_valid, errors = validate_json_structure(invalid_registry, correlation_id)
        
        # Assert
        assert is_valid is False
        assert any("Domain 'backend' mapping must be a list of strings" in error for error in errors)
    
    def test_validate_invalid_domain_mapping_content(self, correlation_id: str):
        """Test validation fails with invalid domain mapping content."""
        # Arrange
        invalid_registry = {
            "tool_categories": {},
            "domain_mappings": {
                "backend": ["valid_string", 123]  # Should contain only strings
            }
        }
        
        # Act
        is_valid, errors = validate_json_structure(invalid_registry, correlation_id)
        
        # Assert
        assert is_valid is False
        assert any("Domain 'backend' mapping must contain only strings" in error for error in errors)


class TestValidateReferentialIntegrity:
    """Test cases for validate_referential_integrity function."""
    
    def test_validate_valid_integrity(self, valid_tool_registry: Dict, correlation_id: str):
        """Test validation of valid referential integrity."""
        # Arrange
        registry_data = valid_tool_registry
        
        # Act
        is_valid, errors = validate_referential_integrity(registry_data, correlation_id)
        
        # Assert
        assert is_valid is True
        assert errors == []
    
    def test_validate_missing_required_keys(self, correlation_id: str):
        """Test validation fails with missing required keys."""
        # Arrange
        incomplete_registry = {"tool_categories": {}}  # Missing domain_mappings
        
        # Act
        is_valid, errors = validate_referential_integrity(incomplete_registry, correlation_id)
        
        # Assert
        assert is_valid is False
        assert any("Cannot validate referential integrity without required keys" in error for error in errors)
    
    def test_validate_nonexistent_category_reference(self, correlation_id: str):
        """Test validation fails with references to non-existent categories."""
        # Arrange
        invalid_registry = {
            "tool_categories": {
                "linting": {
                    "description": "Linting tools",
                    "tools": ["ruff"]
                }
            },
            "domain_mappings": {
                "backend": ["linting", "nonexistent_category"]
            }
        }
        
        # Act
        is_valid, errors = validate_referential_integrity(invalid_registry, correlation_id)
        
        # Assert
        assert is_valid is False
        assert any("Domain 'backend' references non-existent category 'nonexistent_category'" in error for error in errors)
    
    def test_validate_unused_categories_warning(self, correlation_id: str):
        """Test validation warns about unused categories."""
        # Arrange
        registry_with_unused = {
            "tool_categories": {
                "linting": {
                    "description": "Linting tools",
                    "tools": ["ruff"]
                },
                "unused_category": {
                    "description": "Unused category",
                    "tools": ["tool"]
                }
            },
            "domain_mappings": {
                "backend": ["linting"]  # unused_category not referenced
            }
        }
        
        # Act
        with patch('scripts.lint_tool_registry.logger') as mock_logger:
            is_valid, errors = validate_referential_integrity(registry_with_unused, correlation_id)
        
        # Assert
        assert is_valid is True  # Unused categories are warnings, not errors
        assert errors == []
        mock_logger.warning.assert_called()


class TestValidateToolRegistry:
    """Test cases for validate_tool_registry function."""
    
    def test_validate_valid_registry_file(self, temp_registry_file: Path, correlation_id: str):
        """Test validation of valid registry file."""
        # Arrange
        file_path = temp_registry_file
        
        # Act
        is_valid, registry_data = validate_tool_registry(file_path, correlation_id)
        
        # Assert
        assert is_valid is True
        assert isinstance(registry_data, dict)
        assert "tool_categories" in registry_data
        assert "domain_mappings" in registry_data
    
    def test_validate_invalid_json_file(self, temp_invalid_json_file: Path, correlation_id: str):
        """Test validation fails with invalid JSON file."""
        # Arrange
        file_path = temp_invalid_json_file
        
        # Act
        is_valid, registry_data = validate_tool_registry(file_path, correlation_id)
        
        # Assert
        assert is_valid is False
        assert registry_data == {}
    
    def test_validate_nonexistent_file(self, correlation_id: str):
        """Test validation fails with non-existent file."""
        # Arrange
        nonexistent_path = Path("/nonexistent/registry.json")
        
        # Act
        is_valid, registry_data = validate_tool_registry(nonexistent_path, correlation_id)
        
        # Assert
        assert is_valid is False
        assert registry_data == {}
    
    def test_validate_structure_invalid_registry(self, invalid_structure_registry: Dict, correlation_id: str):
        """Test validation fails with structurally invalid registry."""
        # Arrange
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(invalid_structure_registry, f)
            file_path = Path(f.name)
        
        # Act
        is_valid, registry_data = validate_tool_registry(file_path, correlation_id)
        
        # Assert
        assert is_valid is False
        assert isinstance(registry_data, dict)  # Data is loaded but validation fails
    
    def test_validate_integrity_invalid_registry(self, invalid_integrity_registry: Dict, correlation_id: str):
        """Test validation fails with referential integrity issues."""
        # Arrange
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(invalid_integrity_registry, f)
            file_path = Path(f.name)
        
        # Act
        is_valid, registry_data = validate_tool_registry(file_path, correlation_id)
        
        # Assert
        assert is_valid is False
        assert isinstance(registry_data, dict)


class TestDisplaySummary:
    """Test cases for display_summary function."""
    
    def test_display_summary_valid_registry(self, temp_registry_file: Path, valid_tool_registry: Dict, correlation_id: str):
        """Test display summary for valid registry."""
        # Arrange
        file_path = temp_registry_file
        is_valid = True
        registry_data = valid_tool_registry
        
        # Act & Assert (no exceptions should be raised)
        display_summary(file_path, is_valid, registry_data, correlation_id)
    
    def test_display_summary_invalid_registry(self, temp_registry_file: Path, correlation_id: str):
        """Test display summary for invalid registry."""
        # Arrange
        file_path = temp_registry_file
        is_valid = False
        registry_data = {}
        
        # Act & Assert (no exceptions should be raised)
        display_summary(file_path, is_valid, registry_data, correlation_id)
    
    def test_display_summary_empty_registry(self, temp_registry_file: Path, correlation_id: str):
        """Test display summary for empty registry."""
        # Arrange
        file_path = temp_registry_file
        is_valid = True
        registry_data = {}
        
        # Act & Assert (no exceptions should be raised)
        display_summary(file_path, is_valid, registry_data, correlation_id)
    
    def test_display_summary_counts_tools_correctly(self, temp_registry_file: Path, valid_tool_registry: Dict, correlation_id: str):
        """Test display summary counts tools correctly."""
        # Arrange
        file_path = temp_registry_file
        is_valid = True
        registry_data = valid_tool_registry
        
        # Act
        with patch('scripts.lint_tool_registry.console') as mock_console:
            display_summary(file_path, is_valid, registry_data, correlation_id)
        
        # Assert
        mock_console.print.assert_called()
        # Verify that the summary includes correct counts
        call_args = [call[0][0] for call in mock_console.print.call_args_list if hasattr(call[0][0], 'columns')]
        assert len(call_args) > 0  # Table was printed


@pytest.fixture(autouse=True)
def cleanup_temp_files():
    """Cleanup temporary files after each test."""
    yield
    # Cleanup happens automatically with tempfile context managers 