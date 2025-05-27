#!/usr/bin/env python3
"""
Tests for role creation script.
Uses pytest with AAA pattern and fixtures for setup/teardown.
"""

import json
import tempfile
from pathlib import Path
from typing import Any, Dict, List
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
    get_role_data,
    load_role_library,
    load_tool_registry,
    resolve_tools_from_registry,
    validate_cli_input,
    validate_role_library,
    validate_role_name,
    write_role_file,
)


@pytest.fixture
def sample_tool_registry() -> Dict[str, Any]:
    """Create a sample tool registry for testing."""
    return {
        "tool_categories": {
            "linting": {
                "description": "Code linting tools",
                "tools": ["ruff", "black", "isort"]
            },
            "testing": {
                "description": "Testing frameworks",
                "tools": ["pytest", "coverage"]
            },
            "cloud": {
                "description": "Cloud infrastructure tools",
                "tools": ["terraform", "ansible"]
            }
        },
        "domain_mappings": {
            "backend": ["linting", "testing"],
            "aws": ["cloud"],
            "python": ["linting", "testing"]
        }
    }


@pytest.fixture
def sample_role_library() -> Dict[str, Any]:
    """Create a sample role library for testing."""
    return {
        "executive": {
            "cmo": {
                "identity": {
                    "scope": "Global",
                    "seniority": "C-level",
                    "span_of_control": "50"
                },
                "objectives": {
                    "top_objectives": ["Drive brand awareness", "Increase market share"],
                    "kpis": ["Brand recognition", "Lead generation", "Customer acquisition cost"]
                },
                "influence": {
                    "decision_rights": ["Marketing budget", "Brand strategy"],
                    "stakeholders": ["CEO", "Sales VP", "Product VP"]
                },
                "behaviors": {
                    "comms": ["Weekly reviews", "Monthly board updates"],
                    "trusted_tools": ["HubSpot", "Google Analytics"],
                    "tool_domains": ["martech"],
                    "risk_posture": "Moderate"
                },
                "motivations": {
                    "drivers": ["Growth", "Innovation"],
                    "pain_points": ["Budget constraints", "Attribution challenges"]
                }
            }
        },
        "specialist": {
            "qa_lead": {
                "identity": {
                    "scope": "Cross-functional",
                    "seniority": "Senior specialist",
                    "span_of_control": "5"
                },
                "objectives": {
                    "top_objectives": ["Ensure quality standards", "Reduce defect rate"],
                    "kpis": ["Test coverage", "Defect density"]
                },
                "standards": ["ISO 9001", "ISTQB"],
                "gates": ["Code review", "Integration testing"],
                "behaviors": {
                    "trusted_tools": ["Selenium", "Jest"],
                    "tool_domains": ["testing"],
                    "risk_posture": "Conservative"
                }
            }
        }
    }


@pytest.fixture
def temp_role_library_file(sample_role_library: Dict[str, Any]) -> Path:
    """Create a temporary role library file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_role_library, f, indent=2)
        return Path(f.name)


@pytest.fixture
def temp_tool_registry_file(sample_tool_registry: Dict[str, Any]) -> Path:
    """Create a temporary tool registry file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_tool_registry, f, indent=2)
        return Path(f.name)


@pytest.fixture
def temp_output_dir() -> Path:
    """Create a temporary output directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


class TestValidateCliInput:
    """Test cases for validate_cli_input function."""
    
    def test_validate_safe_input(self):
        """Test validation of safe input."""
        # Arrange
        safe_input = "backend_development"
        field_name = "test_field"
        
        # Act
        result = validate_cli_input(safe_input, field_name)
        
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
            result = validate_cli_input(dangerous_input, "test_field")
            
            # Assert
            assert result is False, f"Should reject dangerous input: {dangerous_input}"
    
    def test_validate_excessive_length(self):
        """Test validation rejects excessively long input."""
        # Arrange
        long_input = "a" * 501  # Exceeds MAX_INPUT_LENGTH of 500
        
        # Act
        result = validate_cli_input(long_input, "test_field")
        
        # Assert
        assert result is False


class TestValidateRoleName:
    """Test cases for validate_role_name function."""
    
    def test_validate_valid_name(self):
        """Test validation of valid role name."""
        # Arrange
        valid_name = "cmo"
        
        # Act
        result = validate_role_name(valid_name)
        
        # Assert
        assert result == "cmo"
    
    def test_validate_mixed_case(self):
        """Test validation converts to lowercase."""
        # Arrange
        mixed_case = "CMO"
        
        # Act
        result = validate_role_name(mixed_case)
        
        # Assert
        assert result == "cmo"
    
    def test_validate_special_characters(self):
        """Test validation removes special characters."""
        # Arrange
        special_chars = "qa@lead#test"
        
        # Act
        result = validate_role_name(special_chars)
        
        # Assert
        assert result == "qaleadtest"
    
    def test_validate_preserves_hyphens_underscores(self):
        """Test validation preserves hyphens and underscores."""
        # Arrange
        name_with_separators = "qa-lead_test"
        
        # Act
        result = validate_role_name(name_with_separators)
        
        # Assert
        assert result == "qa-lead_test"
    
    def test_validate_empty_result_exits(self):
        """Test validation exits on empty result."""
        # Arrange
        invalid_name = "@#$%"
        
        # Act & Assert
        with pytest.raises(SystemExit):
            validate_role_name(invalid_name)
    
    def test_validate_dangerous_input_exits(self):
        """Test validation exits on dangerous input."""
        # Arrange
        dangerous_name = "{{malicious}}"
        
        # Act & Assert
        with pytest.raises(SystemExit):
            validate_role_name(dangerous_name)


class TestCoerceCsv:
    """Test cases for coerce_csv function."""
    
    def test_coerce_valid_csv(self):
        """Test coercing valid CSV string."""
        # Arrange
        csv_string = "item1,item2,item3"
        
        # Act
        result = coerce_csv(csv_string)
        
        # Assert
        assert result == ["item1", "item2", "item3"]
    
    def test_coerce_csv_with_spaces(self):
        """Test coercing CSV string with spaces."""
        # Arrange
        csv_string = "item1, item2 , item3"
        
        # Act
        result = coerce_csv(csv_string)
        
        # Assert
        assert result == ["item1", "item2", "item3"]
    
    def test_coerce_none_input(self):
        """Test coercing None input."""
        # Arrange
        csv_string = None
        
        # Act
        result = coerce_csv(csv_string)
        
        # Assert
        assert result is None
    
    def test_coerce_empty_string(self):
        """Test coercing empty string."""
        # Arrange
        csv_string = ""
        
        # Act
        result = coerce_csv(csv_string)
        
        # Assert
        assert result is None


class TestDeepMerge:
    """Test cases for deep_merge function."""
    
    def test_deep_merge_simple(self):
        """Test deep merge with simple dictionaries."""
        # Arrange
        base = {"a": 1, "b": 2}
        override = {"b": 3, "c": 4}
        
        # Act
        result = deep_merge(base, override)
        
        # Assert
        assert result == {"a": 1, "b": 3, "c": 4}
    
    def test_deep_merge_nested(self):
        """Test deep merge with nested dictionaries."""
        # Arrange
        base = {"level1": {"a": 1, "b": 2}}
        override = {"level1": {"b": 3, "c": 4}}
        
        # Act
        result = deep_merge(base, override)
        
        # Assert
        assert result == {"level1": {"a": 1, "b": 3, "c": 4}}
    
    def test_deep_merge_override_non_dict(self):
        """Test deep merge when override replaces non-dict with dict."""
        # Arrange
        base = {"level1": "string_value"}
        override = {"level1": {"new": "dict"}}
        
        # Act
        result = deep_merge(base, override)
        
        # Assert
        assert result == {"level1": {"new": "dict"}}


class TestApplyOverrides:
    """Test cases for apply_overrides function."""
    
    def test_apply_cli_overrides(self, sample_role_library: Dict[str, Any]):
        """Test applying CLI overrides to role data."""
        # Arrange
        base_data = sample_role_library["executive"]["cmo"]
        mock_args = Mock()
        mock_args.trusted_tools = "tool1,tool2"
        mock_args.scope = "Regional"
        mock_args.kpis = "metric1,metric2"
        # Set all other attributes to None
        for attr in ["comms", "drivers", "pain_points", "top_objectives", 
                    "decision_rights", "stakeholders", "seniority", "span_of_control"]:
            setattr(mock_args, attr, None)
        
        # Act
        with patch('scripts.create_role.validate_cli_input', return_value=True):
            result = apply_overrides(base_data, mock_args)
        
        # Assert
        assert result["behaviors"]["trusted_tools"] == ["tool1", "tool2"]
        assert result["identity"]["scope"] == "Regional"
        assert result["objectives"]["kpis"] == ["metric1", "metric2"]
    
    def test_apply_json_overrides(self, sample_role_library: Dict[str, Any]):
        """Test applying JSON file overrides to role data."""
        # Arrange
        base_data = sample_role_library["executive"]["cmo"]
        mock_args = Mock()
        # Set all CLI attributes to None
        for attr in ["trusted_tools", "comms", "kpis", "drivers", "pain_points", 
                    "top_objectives", "decision_rights", "stakeholders", "scope", 
                    "seniority", "span_of_control"]:
            setattr(mock_args, attr, None)
        
        json_override = {
            "behaviors": {
                "trusted_tools": ["override_tool"]
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(json_override, f)
            json_path = f.name
        
        # Act
        result = apply_overrides(base_data, mock_args, json_path)
        
        # Assert
        assert "override_tool" in result["behaviors"]["trusted_tools"]
    
    def test_apply_overrides_precedence(self, sample_role_library: Dict[str, Any]):
        """Test that CLI overrides take precedence over JSON overrides."""
        # Arrange
        base_data = sample_role_library["executive"]["cmo"]
        mock_args = Mock()
        mock_args.scope = "CLI_Override"
        # Set all other CLI attributes to None
        for attr in ["trusted_tools", "comms", "kpis", "drivers", "pain_points", 
                    "top_objectives", "decision_rights", "stakeholders", 
                    "seniority", "span_of_control"]:
            setattr(mock_args, attr, None)
        
        json_override = {
            "identity": {
                "scope": "JSON_Override"
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(json_override, f)
            json_path = f.name
        
        # Act
        with patch('scripts.create_role.validate_cli_input', return_value=True):
            result = apply_overrides(base_data, mock_args, json_path)
        
        # Assert
        assert result["identity"]["scope"] == "CLI_Override"
    
    def test_apply_overrides_invalid_json_file(self, sample_role_library: Dict[str, Any]):
        """Test handling of invalid JSON override file."""
        # Arrange
        base_data = sample_role_library["executive"]["cmo"]
        mock_args = Mock()
        # Set all CLI attributes to None
        for attr in ["trusted_tools", "comms", "kpis", "drivers", "pain_points", 
                    "top_objectives", "decision_rights", "stakeholders", "scope", 
                    "seniority", "span_of_control"]:
            setattr(mock_args, attr, None)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json }")
            json_path = f.name
        
        # Act & Assert
        with pytest.raises(SystemExit):
            apply_overrides(base_data, mock_args, json_path)
    
    def test_apply_overrides_missing_json_file(self, sample_role_library: Dict[str, Any]):
        """Test handling of missing JSON override file."""
        # Arrange
        base_data = sample_role_library["executive"]["cmo"]
        mock_args = Mock()
        # Set all CLI attributes to None
        for attr in ["trusted_tools", "comms", "kpis", "drivers", "pain_points", 
                    "top_objectives", "decision_rights", "stakeholders", "scope", 
                    "seniority", "span_of_control"]:
            setattr(mock_args, attr, None)
        
        json_path = "/nonexistent/file.json"
        
        # Act & Assert
        with pytest.raises(SystemExit):
            apply_overrides(base_data, mock_args, json_path)


class TestLoadToolRegistry:
    """Test cases for load_tool_registry function."""
    
    def test_load_existing_registry(self, temp_tool_registry_file: Path):
        """Test loading existing tool registry."""
        # Arrange & Act
        with patch('builtins.open', mock_open_registry_file(temp_tool_registry_file)):
            with patch('pathlib.Path.exists', return_value=True):
                result = load_tool_registry()
        
        # Assert
        assert isinstance(result, dict)
        assert "tool_categories" in result
        assert "domain_mappings" in result
    
    def test_load_missing_registry(self):
        """Test loading missing tool registry."""
        # Arrange & Act
        with patch('pathlib.Path.exists', return_value=False):
            result = load_tool_registry()
        
        # Assert
        assert result == {}
    
    def test_load_invalid_json_registry(self):
        """Test loading invalid JSON registry."""
        # Arrange & Act
        with patch('builtins.open', mock_open_invalid_json()):
            with patch('pathlib.Path.exists', return_value=True):
                result = load_tool_registry()
        
        # Assert
        assert result == {}


class TestResolveToolsFromRegistry:
    """Test cases for resolve_tools_from_registry function."""
    
    def test_resolve_domain_mappings(self, sample_tool_registry: Dict[str, Any]):
        """Test resolving tools from domain mappings."""
        # Arrange
        domains = ["backend"]
        
        # Act
        result = resolve_tools_from_registry(domains, sample_tool_registry)
        
        # Assert
        assert "ruff" in result
        assert "pytest" in result
        assert len(result) == 5  # ruff, black, isort, pytest, coverage
    
    def test_resolve_direct_categories(self, sample_tool_registry: Dict[str, Any]):
        """Test resolving tools from direct categories."""
        # Arrange
        categories = ["linting"]
        
        # Act
        result = resolve_tools_from_registry(categories, sample_tool_registry)
        
        # Assert
        assert result == ["ruff", "black", "isort"]
    
    def test_resolve_unknown_domain(self, sample_tool_registry: Dict[str, Any]):
        """Test resolving tools from unknown domain."""
        # Arrange
        domains = ["unknown_domain"]
        
        # Act
        result = resolve_tools_from_registry(domains, sample_tool_registry)
        
        # Assert
        assert result == []
    
    def test_resolve_empty_registry(self):
        """Test resolving tools from empty registry."""
        # Arrange
        domains = ["backend"]
        empty_registry = {}
        
        # Act
        result = resolve_tools_from_registry(domains, empty_registry)
        
        # Assert
        assert result == []
    
    def test_resolve_removes_duplicates(self, sample_tool_registry: Dict[str, Any]):
        """Test that duplicate tools are removed."""
        # Arrange
        domains = ["backend", "python"]  # Both map to overlapping categories
        
        # Act
        result = resolve_tools_from_registry(domains, sample_tool_registry)
        
        # Assert
        # Should not have duplicates
        assert len(result) == len(set(result))


class TestValidateRoleLibrary:
    """Test cases for validate_role_library function."""
    
    def test_validate_valid_library(self, sample_role_library: Dict[str, Any]):
        """Test validation of valid role library."""
        # Arrange & Act & Assert (should not raise exceptions)
        validate_role_library(sample_role_library)
    
    def test_validate_missing_executive_buckets(self):
        """Test validation warns about missing executive buckets."""
        # Arrange
        invalid_library = {
            "executive": {
                "cmo": {
                    "identity": {"scope": "Global"},
                    # Missing other required buckets
                }
            }
        }
        
        # Act & Assert (should not raise exceptions, but log warnings)
        with patch('scripts.create_role.logger') as mock_logger:
            validate_role_library(invalid_library)
            mock_logger.warning.assert_called()
    
    def test_validate_missing_specialist_buckets(self):
        """Test validation warns about missing specialist buckets."""
        # Arrange
        invalid_library = {
            "specialist": {
                "qa_lead": {
                    # Missing required buckets
                }
            }
        }
        
        # Act & Assert (should not raise exceptions, but log warnings)
        with patch('scripts.create_role.logger') as mock_logger:
            validate_role_library(invalid_library)
            mock_logger.warning.assert_called()


class TestLoadRoleLibrary:
    """Test cases for load_role_library function."""
    
    def test_load_existing_library(self, temp_role_library_file: Path):
        """Test loading existing role library."""
        # Arrange & Act
        with patch('builtins.open', mock_open_registry_file(temp_role_library_file)):
            with patch('pathlib.Path.exists', return_value=True):
                result = load_role_library()
        
        # Assert
        assert isinstance(result, dict)
        assert "executive" in result
        assert "specialist" in result
    
    def test_load_missing_library(self):
        """Test loading missing role library."""
        # Arrange & Act & Assert
        with patch('pathlib.Path.exists', return_value=False):
            with pytest.raises(SystemExit):
                load_role_library()
    
    def test_load_invalid_json_library(self):
        """Test loading invalid JSON library."""
        # Arrange & Act & Assert
        with patch('builtins.open', mock_open_invalid_json()):
            with patch('pathlib.Path.exists', return_value=True):
                with pytest.raises(SystemExit):
                    load_role_library()


class TestGetRoleData:
    """Test cases for get_role_data function."""
    
    def test_get_existing_role(self, sample_role_library: Dict[str, Any]):
        """Test getting existing role data."""
        # Arrange
        role_type = "executive"
        role_name = "cmo"
        
        # Act
        result = get_role_data(role_type, role_name, sample_role_library)
        
        # Assert
        assert result is not None
        assert "identity" in result
        assert "objectives" in result
    
    def test_get_unknown_role_type(self, sample_role_library: Dict[str, Any]):
        """Test getting role data for unknown type."""
        # Arrange
        role_type = "unknown"
        role_name = "test"
        
        # Act
        result = get_role_data(role_type, role_name, sample_role_library)
        
        # Assert
        assert result is None
    
    def test_get_custom_role_confirmed(self, sample_role_library: Dict[str, Any]):
        """Test getting custom role when confirmed."""
        # Arrange
        role_type = "executive"
        role_name = "custom_role"
        
        # Act
        with patch('scripts.create_role.Confirm.ask', return_value=True):
            result = get_role_data(role_type, role_name, sample_role_library)
        
        # Assert
        assert result == {}
    
    def test_get_custom_role_denied(self, sample_role_library: Dict[str, Any]):
        """Test getting custom role when denied."""
        # Arrange
        role_type = "executive"
        role_name = "custom_role"
        
        # Act
        with patch('scripts.create_role.Confirm.ask', return_value=False):
            result = get_role_data(role_type, role_name, sample_role_library)
        
        # Assert
        assert result is None


class TestGenerateSynthesisInstructions:
    """Test cases for generate_synthesis_instructions function."""
    
    def test_generate_known_domains(self):
        """Test generating instructions for known domains."""
        # Arrange
        tool_domains = ["aws", "python"]
        
        # Act
        result = generate_synthesis_instructions(tool_domains)
        
        # Assert
        assert "@aws" in result
        assert "@python" in result
        assert "infrastructure standards" in result
        assert "coding standards" in result
    
    def test_generate_unknown_domains(self):
        """Test generating instructions for unknown domains."""
        # Arrange
        tool_domains = ["unknown_domain"]
        
        # Act
        result = generate_synthesis_instructions(tool_domains)
        
        # Assert
        assert "@unknown_domain" in result
        assert "domain-specific standards" in result
    
    def test_generate_empty_domains(self):
        """Test generating instructions for empty domains."""
        # Arrange
        tool_domains = []
        
        # Act
        result = generate_synthesis_instructions(tool_domains)
        
        # Assert
        assert "@aws" in result  # Default domains
        assert "@python" in result
        assert "@database" in result


class TestGenerateExecutiveRole:
    """Test cases for generate_executive_role function."""
    
    def test_generate_complete_executive_role(self, sample_role_library: Dict[str, Any]):
        """Test generating complete executive role."""
        # Arrange
        role_name = "cmo"
        role_data = sample_role_library["executive"]["cmo"]
        
        # Act
        result = generate_executive_role(role_name, role_data)
        
        # Assert
        assert "CMO" in result
        assert "Global" in result
        assert "C-level" in result
        assert "Drive brand awareness" in result
        assert "@martech" in result
    
    def test_generate_incomplete_executive_role_strict(self):
        """Test generating incomplete executive role in strict mode."""
        # Arrange
        role_name = "test_exec"
        incomplete_data = {"identity": {"scope": "Global"}}
        
        # Act & Assert
        with pytest.raises(SystemExit):
            generate_executive_role(role_name, incomplete_data, strict=True)
    
    def test_generate_incomplete_executive_role_non_strict(self):
        """Test generating incomplete executive role in non-strict mode."""
        # Arrange
        role_name = "test_exec"
        incomplete_data = {"identity": {"scope": "Global"}}
        
        # Act
        result = generate_executive_role(role_name, incomplete_data, strict=False)
        
        # Assert
        assert "Test Exec" in result
        assert "Global" in result


class TestGenerateSpecialistRole:
    """Test cases for generate_specialist_role function."""
    
    def test_generate_complete_specialist_role(self, sample_role_library: Dict[str, Any]):
        """Test generating complete specialist role."""
        # Arrange
        role_name = "qa_lead"
        role_data = sample_role_library["specialist"]["qa_lead"]
        
        # Act
        result = generate_specialist_role(role_name, role_data)
        
        # Assert
        assert "Qa Lead" in result
        assert "Cross-functional" in result
        assert "Senior specialist" in result
        assert "Ensure quality standards" in result
        assert "ISO 9001" in result
    
    def test_generate_incomplete_specialist_role_strict(self):
        """Test generating incomplete specialist role in strict mode."""
        # Arrange
        role_name = "test_spec"
        incomplete_data = {"identity": {"scope": "Cross-functional"}}
        
        # Act & Assert
        with pytest.raises(SystemExit):
            generate_specialist_role(role_name, incomplete_data, strict=True)
    
    def test_generate_incomplete_specialist_role_non_strict(self):
        """Test generating incomplete specialist role in non-strict mode."""
        # Arrange
        role_name = "test_spec"
        incomplete_data = {"identity": {"scope": "Cross-functional"}}
        
        # Act
        result = generate_specialist_role(role_name, incomplete_data, strict=False)
        
        # Assert
        assert "Test Spec" in result
        assert "Cross-functional" in result


class TestWriteRoleFile:
    """Test cases for write_role_file function."""
    
    def test_write_new_role_file(self, temp_output_dir: Path):
        """Test writing new role file."""
        # Arrange
        role_name = "test_role"
        content = "test content"
        
        # Act
        result_path = write_role_file(role_name, content, temp_output_dir)
        
        # Assert
        assert result_path.exists()
        assert result_path.name == "test_role.mdc"
        assert result_path.read_text(encoding="utf-8") == content
    
    def test_write_existing_file_overwrite_confirmed(self, temp_output_dir: Path):
        """Test writing existing file when overwrite is confirmed."""
        # Arrange
        role_name = "test_role"
        content = "new content"
        existing_file = temp_output_dir / "test_role.mdc"
        existing_file.write_text("old content")
        
        # Act
        with patch('scripts.create_role.Confirm.ask', return_value=True):
            result_path = write_role_file(role_name, content, temp_output_dir)
        
        # Assert
        assert result_path.exists()
        assert result_path.read_text(encoding="utf-8") == content
    
    def test_write_existing_file_overwrite_denied(self, temp_output_dir: Path):
        """Test writing existing file when overwrite is denied."""
        # Arrange
        role_name = "test_role"
        content = "new content"
        existing_file = temp_output_dir / "test_role.mdc"
        existing_file.write_text("old content")
        
        # Act & Assert
        with patch('scripts.create_role.Confirm.ask', return_value=False):
            with pytest.raises(SystemExit):
                write_role_file(role_name, content, temp_output_dir)


class TestConstants:
    """Test cases for module constants."""
    
    def test_valid_role_types(self):
        """Test that valid role types are defined."""
        # Arrange & Act & Assert
        assert "executive" in VALID_ROLE_TYPES
        assert "specialist" in VALID_ROLE_TYPES
    
    def test_required_executive_buckets(self):
        """Test that required executive buckets are defined."""
        # Arrange & Act & Assert
        expected_buckets = ["identity", "objectives", "influence", "behaviors", "motivations"]
        assert all(bucket in REQUIRED_EXECUTIVE_BUCKETS for bucket in expected_buckets)
    
    def test_required_specialist_buckets(self):
        """Test that required specialist buckets are defined."""
        # Arrange & Act & Assert
        expected_buckets = ["identity", "objectives"]
        assert all(bucket in REQUIRED_SPECIALIST_BUCKETS for bucket in expected_buckets)


def mock_open_invalid_json():
    """Mock open function that returns invalid JSON."""
    from unittest.mock import mock_open
    return mock_open(read_data="{ invalid json }")


def mock_open_registry_file(file_path: Path):
    """Mock open function that returns content from a file."""
    from unittest.mock import mock_open
    content = file_path.read_text(encoding="utf-8")
    return mock_open(read_data=content)


@pytest.fixture(autouse=True)
def cleanup_temp_files():
    """Cleanup temporary files after each test."""
    yield
    # Cleanup happens automatically with tempfile context managers 