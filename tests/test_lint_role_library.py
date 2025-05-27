#!/usr/bin/env python3
"""
Tests for Role Library Linter - Validates role_library.json structure and integrity.
"""

import json
import tempfile
import uuid
from pathlib import Path
from typing import Dict, Any

import pytest

import sys
from pathlib import Path

# Add the scripts directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lint_role_library import (
    sanitize_file_path,
    load_tool_registry,
    validate_json_structure,
    validate_field_structure,
    validate_tool_registry_references,
    validate_role_consistency,
    validate_role_library,
    VALID_ROLE_TYPES,
    REQUIRED_EXECUTIVE_BUCKETS,
    REQUIRED_SPECIALIST_BUCKETS,
    REQUIRED_IDENTITY_FIELDS,
    REQUIRED_OBJECTIVES_FIELDS,
)


@pytest.fixture
def correlation_id() -> str:
    """Generate a correlation ID for test runs."""
    return str(uuid.uuid4())[:8]


@pytest.fixture
def valid_executive_role() -> Dict[str, Any]:
    """Factory for valid executive role data."""
    return {
        "identity": {
            "scope": "Enterprise-wide strategic oversight",
            "seniority": "C-level executive",
            "span_of_control": "All business units and functions"
        },
        "objectives": {
            "top_objectives": [
                "Drive overall business strategy and growth",
                "Ensure operational excellence across all functions"
            ],
            "kpis": [
                "Revenue growth rate",
                "Market share expansion"
            ]
        },
        "influence": {
            "decision_authority": "Final authority on strategic decisions",
            "stakeholder_management": "Board, investors, key customers"
        },
        "behaviors": {
            "leadership_style": "Visionary and decisive",
            "communication_approach": "High-level strategic messaging"
        },
        "motivations": {
            "primary_drivers": ["Business growth", "Stakeholder value"],
            "success_metrics": ["Company valuation", "Market position"]
        }
    }


@pytest.fixture
def valid_specialist_role() -> Dict[str, Any]:
    """Factory for valid specialist role data."""
    return {
        "identity": {
            "scope": "Backend development and architecture",
            "seniority": "Senior level",
            "span_of_control": "Development team and technical decisions"
        },
        "objectives": {
            "top_objectives": [
                "Build scalable backend systems",
                "Ensure code quality and performance"
            ],
            "kpis": [
                "System uptime",
                "Code coverage percentage"
            ]
        },
        "standards": [
            "Follow REST API design principles",
            "Implement comprehensive error handling"
        ],
        "behaviors": {
            "tool_domains": ["backend", "database"],
            "trusted_tools": ["python", "postgresql"]
        }
    }


@pytest.fixture
def valid_role_library(
    valid_executive_role: Dict[str, Any],
    valid_specialist_role: Dict[str, Any]
) -> Dict[str, Any]:
    """Factory for valid role library data."""
    return {
        "executive": {
            "ceo": valid_executive_role
        },
        "specialist": {
            "backend_engineer": valid_specialist_role
        }
    }


@pytest.fixture
def sample_tool_registry() -> Dict[str, Any]:
    """Factory for sample tool registry data."""
    return {
        "domain_mappings": {
            "backend": ["python", "nodejs", "java"],
            "database": ["postgresql", "mysql", "mongodb"],
            "frontend": ["react", "vue", "angular"]
        }
    }


@pytest.fixture
def temp_json_file():
    """Create a temporary JSON file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = Path(f.name)
        yield temp_path
        # Cleanup
        if temp_path.exists():
            temp_path.unlink()


class TestSanitizeFilePath:
    """Test file path sanitization functionality."""

    def test_sanitize_valid_file_path(self, temp_json_file: Path):
        """Test sanitization of valid file path."""
        # Arrange
        temp_json_file.write_text('{}')
        
        # Act
        result = sanitize_file_path(str(temp_json_file))
        
        # Assert
        assert result == temp_json_file.resolve()

    def test_sanitize_dangerous_patterns(self):
        """Test rejection of dangerous file path patterns."""
        # Arrange
        dangerous_paths = [
            "../etc/passwd",
            "~/secret.txt",
            "file$with$vars",
            "command`injection`",
            "file;rm -rf /",
            "file|cat",
            "file&background"
        ]
        
        # Act & Assert
        for dangerous_path in dangerous_paths:
            with pytest.raises(ValueError, match="Potentially dangerous file path"):
                sanitize_file_path(dangerous_path)

    def test_sanitize_nonexistent_file(self):
        """Test handling of nonexistent file paths."""
        # Arrange
        nonexistent_path = "/nonexistent/file.json"
        
        # Act & Assert
        with pytest.raises(ValueError, match="File does not exist"):
            sanitize_file_path(nonexistent_path)


class TestLoadToolRegistry:
    """Test tool registry loading functionality."""

    def test_load_existing_tool_registry(
        self, 
        sample_tool_registry: Dict[str, Any],
        correlation_id: str,
        monkeypatch
    ):
        """Test loading existing tool registry."""
        # Arrange
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_tool_registry, f)
            registry_path = Path(f.name)
        
        # Mock the registry path
        monkeypatch.setattr(
            'lint_role_library.Path.__truediv__',
            lambda self, other: registry_path if other == "tool_registry.json" else self / other
        )
        
        try:
            # Act
            result = load_tool_registry(correlation_id)
            
            # Assert
            assert result == sample_tool_registry
        finally:
            registry_path.unlink()

    def test_load_missing_tool_registry(self, correlation_id: str, monkeypatch):
        """Test handling of missing tool registry."""
        # Arrange
        nonexistent_path = Path("/nonexistent/tool_registry.json")
        monkeypatch.setattr(
            'lint_role_library.Path.__truediv__',
            lambda self, other: nonexistent_path if other == "tool_registry.json" else self / other
        )
        
        # Act
        result = load_tool_registry(correlation_id)
        
        # Assert
        assert result == {}

    def test_load_invalid_json_tool_registry(self, correlation_id: str, monkeypatch):
        """Test handling of invalid JSON in tool registry."""
        # Arrange
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content")
            registry_path = Path(f.name)
        
        monkeypatch.setattr(
            'lint_role_library.Path.__truediv__',
            lambda self, other: registry_path if other == "tool_registry.json" else self / other
        )
        
        try:
            # Act
            result = load_tool_registry(correlation_id)
            
            # Assert
            assert result == {}
        finally:
            registry_path.unlink()


class TestValidateJsonStructure:
    """Test JSON structure validation functionality."""

    def test_validate_valid_structure(
        self, 
        valid_role_library: Dict[str, Any],
        correlation_id: str
    ):
        """Test validation of valid JSON structure."""
        # Act
        is_valid, errors = validate_json_structure(valid_role_library, correlation_id)
        
        # Assert
        assert is_valid is True
        assert errors == []

    def test_validate_non_dict_root(self, correlation_id: str):
        """Test validation of non-dictionary root."""
        # Arrange
        invalid_data = ["not", "a", "dictionary"]
        
        # Act
        is_valid, errors = validate_json_structure(invalid_data, correlation_id)
        
        # Assert
        assert is_valid is False
        assert "Role library must be a dictionary" in errors

    def test_validate_missing_role_types(self, correlation_id: str):
        """Test validation with missing valid role types."""
        # Arrange
        invalid_data = {"invalid_type": {}}
        
        # Act
        is_valid, errors = validate_json_structure(invalid_data, correlation_id)
        
        # Assert
        assert is_valid is False
        assert any("No valid role types found" in error for error in errors)

    def test_validate_unknown_role_types(self, correlation_id: str):
        """Test validation with unknown role types."""
        # Arrange
        invalid_data = {
            "executive": {},
            "unknown_type": {}
        }
        
        # Act
        is_valid, errors = validate_json_structure(invalid_data, correlation_id)
        
        # Assert
        assert is_valid is False
        assert any("Unknown role types found" in error for error in errors)

    def test_validate_missing_executive_buckets(
        self, 
        valid_executive_role: Dict[str, Any],
        correlation_id: str
    ):
        """Test validation of executive role missing required buckets."""
        # Arrange
        incomplete_role = {key: value for key, value in valid_executive_role.items() 
                          if key != "motivations"}
        invalid_data = {"executive": {"ceo": incomplete_role}}
        
        # Act
        is_valid, errors = validate_json_structure(invalid_data, correlation_id)
        
        # Assert
        assert is_valid is False
        assert any("missing required buckets" in error and "motivations" in error 
                  for error in errors)

    def test_validate_missing_specialist_buckets(
        self, 
        valid_specialist_role: Dict[str, Any],
        correlation_id: str
    ):
        """Test validation of specialist role missing required buckets."""
        # Arrange
        incomplete_role = {key: value for key, value in valid_specialist_role.items() 
                          if key not in ["standards", "behaviors"]}
        invalid_data = {"specialist": {"engineer": incomplete_role}}
        
        # Act
        is_valid, errors = validate_json_structure(invalid_data, correlation_id)
        
        # Assert
        assert is_valid is False
        assert any("missing both 'standards' and 'behaviors' buckets" in error 
                  for error in errors)


class TestValidateFieldStructure:
    """Test field structure validation functionality."""

    def test_validate_valid_fields(
        self, 
        valid_role_library: Dict[str, Any],
        correlation_id: str
    ):
        """Test validation of valid field structures."""
        # Act
        is_valid, errors = validate_field_structure(valid_role_library, correlation_id)
        
        # Assert
        assert is_valid is True
        assert errors == []

    def test_validate_missing_identity_fields(self, correlation_id: str):
        """Test validation of missing identity fields."""
        # Arrange
        invalid_data = {
            "executive": {
                "ceo": {
                    "identity": {"scope": "test"},  # Missing seniority, span_of_control
                    "objectives": {
                        "top_objectives": ["test"],
                        "kpis": ["test"]
                    },
                    "influence": {},
                    "behaviors": {},
                    "motivations": {}
                }
            }
        }
        
        # Act
        is_valid, errors = validate_field_structure(invalid_data, correlation_id)
        
        # Assert
        assert is_valid is False
        assert any("identity missing fields" in error for error in errors)

    def test_validate_invalid_objectives_structure(self, correlation_id: str):
        """Test validation of invalid objectives structure."""
        # Arrange
        invalid_data = {
            "specialist": {
                "engineer": {
                    "identity": {
                        "scope": "test",
                        "seniority": "test",
                        "span_of_control": "test"
                    },
                    "objectives": {
                        "top_objectives": "not_an_array",  # Should be array
                        "kpis": ["test"]
                    },
                    "standards": ["test"]
                }
            }
        }
        
        # Act
        is_valid, errors = validate_field_structure(invalid_data, correlation_id)
        
        # Assert
        assert is_valid is False
        assert any("must be an array" in error for error in errors)


class TestValidateToolRegistryReferences:
    """Test tool registry reference validation functionality."""

    def test_validate_valid_tool_domains(
        self,
        valid_role_library: Dict[str, Any],
        sample_tool_registry: Dict[str, Any],
        correlation_id: str
    ):
        """Test validation of valid tool domain references."""
        # Act
        is_valid, errors = validate_tool_registry_references(
            valid_role_library, sample_tool_registry, correlation_id
        )
        
        # Assert
        assert is_valid is True
        assert errors == []

    def test_validate_invalid_tool_domains(
        self,
        sample_tool_registry: Dict[str, Any],
        correlation_id: str
    ):
        """Test validation of invalid tool domain references."""
        # Arrange
        invalid_data = {
            "specialist": {
                "engineer": {
                    "identity": {"scope": "test", "seniority": "test", "span_of_control": "test"},
                    "objectives": {"top_objectives": ["test"], "kpis": ["test"]},
                    "behaviors": {
                        "tool_domains": ["nonexistent_domain"]
                    }
                }
            }
        }
        
        # Act
        is_valid, errors = validate_tool_registry_references(
            invalid_data, sample_tool_registry, correlation_id
        )
        
        # Assert
        assert is_valid is False
        assert any("unknown tool domain" in error for error in errors)

    def test_validate_empty_tool_registry(
        self,
        valid_role_library: Dict[str, Any],
        correlation_id: str
    ):
        """Test validation with empty tool registry."""
        # Act
        is_valid, errors = validate_tool_registry_references(
            valid_role_library, {}, correlation_id
        )
        
        # Assert
        assert is_valid is True  # Should pass when registry is empty
        assert errors == []


class TestValidateRoleConsistency:
    """Test role consistency validation functionality."""

    def test_validate_consistent_roles(
        self,
        valid_role_library: Dict[str, Any],
        correlation_id: str
    ):
        """Test validation of consistent role names."""
        # Act
        is_valid, errors = validate_role_consistency(valid_role_library, correlation_id)
        
        # Assert
        assert is_valid is True
        assert errors == []

    def test_validate_duplicate_role_names(self, correlation_id: str):
        """Test validation of duplicate role names across types."""
        # Arrange
        invalid_data = {
            "executive": {
                "manager": {"identity": {}, "objectives": {}, "influence": {}, "behaviors": {}, "motivations": {}}
            },
            "specialist": {
                "manager": {"identity": {}, "objectives": {}, "standards": []}
            }
        }
        
        # Act
        is_valid, errors = validate_role_consistency(invalid_data, correlation_id)
        
        # Assert
        assert is_valid is False
        assert any("Duplicate role names found" in error for error in errors)


class TestValidateRoleLibrary:
    """Test complete role library validation functionality."""

    def test_validate_complete_valid_library(
        self,
        valid_role_library: Dict[str, Any],
        temp_json_file: Path,
        correlation_id: str
    ):
        """Test validation of complete valid role library."""
        # Arrange
        temp_json_file.write_text(json.dumps(valid_role_library, indent=2))
        
        # Act
        is_valid, library_data = validate_role_library(temp_json_file, correlation_id)
        
        # Assert
        assert is_valid is True
        assert library_data == valid_role_library

    def test_validate_invalid_json_file(
        self,
        temp_json_file: Path,
        correlation_id: str
    ):
        """Test validation of invalid JSON file."""
        # Arrange
        temp_json_file.write_text("invalid json content")
        
        # Act
        is_valid, library_data = validate_role_library(temp_json_file, correlation_id)
        
        # Assert
        assert is_valid is False
        assert library_data == {}

    def test_validate_nonexistent_file(self, correlation_id: str):
        """Test validation of nonexistent file."""
        # Arrange
        nonexistent_path = Path("/nonexistent/file.json")
        
        # Act
        is_valid, library_data = validate_role_library(nonexistent_path, correlation_id)
        
        # Assert
        assert is_valid is False
        assert library_data == {}


class TestConstants:
    """Test validation constants."""

    def test_valid_role_types_constant(self):
        """Test that valid role types constant is properly defined."""
        # Assert
        assert VALID_ROLE_TYPES == {"executive", "specialist"}

    def test_required_buckets_constants(self):
        """Test that required bucket constants are properly defined."""
        # Assert
        assert "identity" in REQUIRED_EXECUTIVE_BUCKETS
        assert "objectives" in REQUIRED_EXECUTIVE_BUCKETS
        assert "identity" in REQUIRED_SPECIALIST_BUCKETS
        assert "objectives" in REQUIRED_SPECIALIST_BUCKETS

    def test_required_field_constants(self):
        """Test that required field constants are properly defined."""
        # Assert
        assert "scope" in REQUIRED_IDENTITY_FIELDS
        assert "seniority" in REQUIRED_IDENTITY_FIELDS
        assert "span_of_control" in REQUIRED_IDENTITY_FIELDS
        assert "top_objectives" in REQUIRED_OBJECTIVES_FIELDS
        assert "kpis" in REQUIRED_OBJECTIVES_FIELDS 