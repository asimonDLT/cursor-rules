#!/usr/bin/env python3
"""
Tests for domain validation script.
Uses pytest with AAA pattern and fixtures for setup/teardown.
"""

import json
import tempfile
import uuid
from pathlib import Path
from typing import Dict, Set
from unittest.mock import patch

import pytest

from scripts.validate_domains import (
    get_filesystem_domains,
    get_registry_domains,
    load_tool_registry,
    validate_domain_consistency,
)


@pytest.fixture
def correlation_id() -> str:
    """Generate a unique correlation ID for test runs."""
    return str(uuid.uuid4())[:8]


@pytest.fixture
def sample_registry() -> Dict:
    """Create a sample tool registry for testing."""
    return {
        "domain_mappings": {
            "backend": ["backend/python", "backend/containers"],
            "frontend": ["frontend/typescript"],
            "cloud": ["cloud/aws"],
            "python": ["backend/python"],
        },
        "domain_metadata": {
            "backend": {"description": "Backend development"},
            "frontend": {"description": "Frontend development"},
            "cloud": {"description": "Cloud infrastructure"},
            "python": {"description": "Python expertise"},
        }
    }


@pytest.fixture
def temp_registry_file(sample_registry: Dict) -> Path:
    """Create a temporary registry file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_registry, f, indent=2)
        return Path(f.name)


@pytest.fixture
def temp_rules_dir() -> Path:
    """Create a temporary rules directory structure for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        rules_dir = Path(temp_dir) / "rules"
        rules_dir.mkdir()
        
        # Create domain directories
        (rules_dir / "backend").mkdir()
        (rules_dir / "frontend").mkdir()
        (rules_dir / "cloud").mkdir()
        (rules_dir / "roles").mkdir()  # Should be excluded
        
        yield rules_dir


class TestLoadToolRegistry:
    """Test cases for load_tool_registry function."""
    
    def test_load_valid_registry(self, temp_registry_file: Path, correlation_id: str):
        """Test loading a valid registry file."""
        # Arrange
        expected_keys = {"domain_mappings", "domain_metadata"}
        
        # Act
        result = load_tool_registry(temp_registry_file, correlation_id)
        
        # Assert
        assert isinstance(result, dict)
        assert expected_keys.issubset(result.keys())
        assert "backend" in result["domain_mappings"]
    
    def test_load_nonexistent_registry(self, correlation_id: str):
        """Test loading a non-existent registry file."""
        # Arrange
        nonexistent_path = Path("/nonexistent/registry.json")
        
        # Act
        result = load_tool_registry(nonexistent_path, correlation_id)
        
        # Assert
        assert result == {}
    
    def test_load_invalid_json_registry(self, correlation_id: str):
        """Test loading a registry file with invalid JSON."""
        # Arrange
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json }")
            invalid_path = Path(f.name)
        
        # Act
        result = load_tool_registry(invalid_path, correlation_id)
        
        # Assert
        assert result == {}


class TestGetFilesystemDomains:
    """Test cases for get_filesystem_domains function."""
    
    def test_get_existing_domains(self, temp_rules_dir: Path, correlation_id: str):
        """Test getting domains from existing directory structure."""
        # Arrange
        expected_domains = {"backend", "frontend", "cloud"}
        
        # Act
        result = get_filesystem_domains(temp_rules_dir, correlation_id)
        
        # Assert
        assert result == expected_domains
        assert "roles" not in result  # Should be excluded
    
    def test_get_domains_nonexistent_dir(self, correlation_id: str):
        """Test getting domains from non-existent directory."""
        # Arrange
        nonexistent_dir = Path("/nonexistent/rules")
        
        # Act
        result = get_filesystem_domains(nonexistent_dir, correlation_id)
        
        # Assert
        assert result == set()


class TestGetRegistryDomains:
    """Test cases for get_registry_domains function."""
    
    def test_get_registry_domains(self, sample_registry: Dict, correlation_id: str):
        """Test extracting domains from registry data."""
        # Arrange
        expected_mappings = {"backend", "frontend", "cloud", "python"}
        expected_metadata = {"backend", "frontend", "cloud", "python"}
        
        # Act
        mappings, metadata = get_registry_domains(sample_registry, correlation_id)
        
        # Assert
        assert mappings == expected_mappings
        assert metadata == expected_metadata
    
    def test_get_registry_domains_empty(self, correlation_id: str):
        """Test extracting domains from empty registry."""
        # Arrange
        empty_registry = {}
        
        # Act
        mappings, metadata = get_registry_domains(empty_registry, correlation_id)
        
        # Assert
        assert mappings == set()
        assert metadata == set()


class TestValidateDomainConsistency:
    """Test cases for validate_domain_consistency function."""
    
    def test_validate_consistent_domains(self, correlation_id: str):
        """Test validation with consistent domains."""
        # Arrange
        filesystem_domains = {"backend", "frontend", "cloud"}
        registry_mappings = {"backend", "frontend", "cloud", "python"}  # python is technical
        registry_metadata = {"backend", "frontend", "cloud", "python"}
        
        # Act
        is_valid, errors = validate_domain_consistency(
            filesystem_domains, registry_mappings, registry_metadata, correlation_id
        )
        
        # Assert
        assert is_valid is True
        assert errors == []
    
    def test_validate_missing_filesystem_domain(self, correlation_id: str):
        """Test validation with missing filesystem domain."""
        # Arrange
        filesystem_domains = {"backend", "frontend"}  # Missing cloud
        registry_mappings = {"backend", "frontend", "cloud"}
        registry_metadata = {"backend", "frontend", "cloud"}
        
        # Act
        is_valid, errors = validate_domain_consistency(
            filesystem_domains, registry_mappings, registry_metadata, correlation_id
        )
        
        # Assert
        assert is_valid is False
        assert any("cloud" in error and "filesystem directory" in error for error in errors)
    
    def test_validate_missing_registry_domain(self, correlation_id: str):
        """Test validation with missing registry domain."""
        # Arrange
        filesystem_domains = {"backend", "frontend", "cloud"}
        registry_mappings = {"backend", "frontend"}  # Missing cloud
        registry_metadata = {"backend", "frontend"}  # Missing cloud
        
        # Act
        is_valid, errors = validate_domain_consistency(
            filesystem_domains, registry_mappings, registry_metadata, correlation_id
        )
        
        # Assert
        assert is_valid is False
        assert any("cloud" in error and "missing from domain_mappings" in error for error in errors)
        assert any("cloud" in error and "missing from domain_metadata" in error for error in errors)
    
    def test_validate_inconsistent_mappings_metadata(self, correlation_id: str):
        """Test validation with inconsistent mappings and metadata."""
        # Arrange
        filesystem_domains = {"backend", "frontend"}
        registry_mappings = {"backend", "frontend", "cloud"}
        registry_metadata = {"backend", "frontend"}  # Missing cloud
        
        # Act
        is_valid, errors = validate_domain_consistency(
            filesystem_domains, registry_mappings, registry_metadata, correlation_id
        )
        
        # Assert
        assert is_valid is False
        assert any("cloud" in error and "domain_mappings but not in domain_metadata" in error for error in errors)
    
    def test_validate_technical_domains_allowed(self, correlation_id: str):
        """Test that technical domains don't require filesystem directories."""
        # Arrange
        filesystem_domains = {"backend", "frontend"}
        registry_mappings = {"backend", "frontend", "python", "aws", "database"}  # All technical
        registry_metadata = {"backend", "frontend", "python", "aws", "database"}
        
        # Act
        is_valid, errors = validate_domain_consistency(
            filesystem_domains, registry_mappings, registry_metadata, correlation_id
        )
        
        # Assert
        assert is_valid is True
        assert errors == []


@pytest.fixture(autouse=True)
def cleanup_temp_files():
    """Cleanup temporary files after each test."""
    yield
    # Cleanup happens automatically with tempfile context managers 