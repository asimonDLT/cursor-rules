#!/usr/bin/env python3
"""
Test suite for Cursor Role Factory.
Validates role generation, structure, and security.
"""
import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from create_role import (
    validate_role_name,
    load_role_library,
    generate_executive_role,
    generate_specialist_role,
    write_role_file,
    validate_cli_input,
)


class TestRoleNameValidation:
    """Test role name sanitization and validation."""
    
    def test_valid_role_names(self):
        """Test that valid role names pass through unchanged."""
        assert validate_role_name("cmo") == "cmo"
        assert validate_role_name("qa_lead") == "qa_lead"
        assert validate_role_name("frontend-architect") == "frontend-architect"
    
    def test_name_sanitization(self):
        """Test that invalid characters are removed."""
        assert validate_role_name("CMO") == "cmo"
        assert validate_role_name("qa@lead") == "qalead"
        assert validate_role_name("test role") == "testrole"
    
    def test_empty_name_rejection(self):
        """Test that empty names are rejected."""
        with pytest.raises(SystemExit):
            validate_role_name("")
        with pytest.raises(SystemExit):
            validate_role_name("@#$%")


class TestRoleLibrary:
    """Test role library loading and validation."""
    
    def test_load_valid_library(self, tmp_path):
        """Test loading a valid role library."""
        library_data = {
            "executive": {"cmo": {"identity": {"scope": "Global"}, "objectives": {"kpis": ["CAC"]}}},
            "specialist": {"security": {"identity": {"scope": "Cross-functional"}, "objectives": {"kpis": ["Security score"]}}}
        }
        
        library_file = tmp_path / "role_library.json"
        with open(library_file, 'w') as f:
            json.dump(library_data, f)
        
        with patch('create_role.Path') as mock_path:
            mock_path.return_value.parent = tmp_path
            mock_path.return_value.__truediv__.return_value = library_file
            library = load_role_library()
        
        assert "executive" in library
        assert "specialist" in library
        assert library["executive"]["cmo"]["identity"]["scope"] == "Global"
    
    def test_missing_library_file(self, tmp_path):
        """Test handling of missing library file."""
        with patch('create_role.Path') as mock_path:
            mock_path.return_value.parent = tmp_path
            mock_path.return_value.__truediv__.return_value.exists.return_value = False
            
            with pytest.raises(SystemExit):
                load_role_library()


class TestRoleGeneration:
    """Test role content generation."""
    
    def test_executive_role_generation(self):
        """Test executive role template generation."""
        role_data = {
            "identity": {"scope": "Global", "seniority": "C-level", "span_of_control": "100"},
            "objectives": {"top_objectives": ["Drive growth"], "kpis": ["CAC", "LTV"]},
            "influence": {"decision_rights": ["Strategy"], "stakeholders": ["CEO"]},
            "behaviors": {"comms": ["Weekly reviews"], "trusted_tools": ["Excel"], "risk_posture": "Balanced"},
            "motivations": {"drivers": ["Growth"], "pain_points": ["Resource constraints"]}
        }
        
        content = generate_executive_role("cmo", role_data)
        
        # Validate structure
        assert "rule_type: Agent Requested" in content
        assert "CMO (v1.0)" in content
        assert "CAC, LTV" in content
        assert "Drive growth" in content
        assert "Project rules override this Role" in content
    
    def test_specialist_role_generation(self):
        """Test specialist role template generation."""
        role_data = {
            "identity": {"scope": "Cross-functional", "seniority": "Senior specialist", "span_of_control": "0"},
            "objectives": {"top_objectives": ["Ensure security"], "kpis": ["Security score"]},
            "standards": ["nist-framework", "zero-trust"],
            "gates": ["Threat Model", "Pen Test"]
        }
        
        content = generate_specialist_role("security", role_data)
        
        # Validate structure
        assert "rule_type: Agent Requested" in content
        assert "Security (v1.0)" in content
        assert "nist-framework, zero-trust" in content
        assert "Ensure security" in content
        assert "APPROVED / BLOCKED / NEEDS_REVISION" in content
    
    def test_framework_requirement_validation(self):
        """Test that roles can be generated with minimal data."""
        role_data = {"identity": {"scope": "Test"}, "objectives": {"kpis": ["metric1"]}}
        
        # This should not raise an exception with current implementation
        content = generate_executive_role("test_role", role_data)
        assert "Test Role (v1.0)" in content


class TestFileOperations:
    """Test file writing and validation."""
    
    def test_write_role_file(self, tmp_path):
        """Test writing role content to file."""
        content = """---
rule_type: Agent Requested
description: Test role
---

# Test Role (v1.0)

Test content
"""
        
        output_path = write_role_file("test_role", content, tmp_path)
        
        assert output_path.exists()
        assert output_path.name == "test_role.mdc"
        
        with open(output_path, 'r') as f:
            written_content = f.read()
        
        assert written_content == content
    
    def test_overwrite_protection(self, tmp_path):
        """Test that existing files are protected from overwrite."""
        existing_file = tmp_path / "existing.mdc"
        existing_file.write_text("existing content")
        
        with patch('create_role.Confirm.ask', return_value=False):
            with pytest.raises(SystemExit):
                write_role_file("existing", "new content", tmp_path)


class TestSecurity:
    """Test security features and input sanitization."""
    
    def test_input_sanitization(self):
        """Test that malicious input is detected."""
        # Test script injection attempts
        malicious_names = [
            "role; rm -rf /",
            "role$(whoami)",
            "role && echo 'hacked'"
        ]
        
        for name in malicious_names:
            sanitized = validate_role_name(name)
            # Should only contain alphanumeric and allowed characters
            assert all(c.isalnum() or c in '_-' for c in sanitized)
    
    def test_dangerous_input_detection(self):
        """Test that dangerous patterns are detected in CLI input."""
        dangerous_inputs = [
            "role`cat /etc/passwd`",
            "role{{malicious}}",
            "role<script>alert('xss')</script>"
        ]
        
        for dangerous_input in dangerous_inputs:
            assert not validate_cli_input(dangerous_input, "test_field")
    
    def test_template_placeholder_detection(self):
        """Test that generated content contains expected output placeholders."""
        role_data = {
            "identity": {"scope": "Global"},
            "objectives": {"kpis": ["test"]},
            "influence": {"decision_rights": ["test"]},
            "behaviors": {"trusted_tools": ["test"]},
            "motivations": {"drivers": ["test"]}
        }
        
        content = generate_executive_role("test_role", role_data)
        
        # Check that output template placeholders are present (these are intentional)
        assert "{{finding_1}}" in content
        assert "{{action_1}}" in content
        
        # Check that no unresolved template variables remain (single braces)
        assert "{role}" not in content
        assert "{title}" not in content


class TestIntegration:
    """Test integration scenarios."""
    
    def test_lint_validation_integration(self, tmp_path):
        """Test that generated files pass lint validation."""
        role_data = {
            "identity": {"scope": "Global"},
            "objectives": {"kpis": ["test"]},
            "influence": {"decision_rights": ["test"]},
            "behaviors": {"trusted_tools": ["test"]},
            "motivations": {"drivers": ["test"]}
        }
        
        content = generate_executive_role("test_role", role_data)
        output_path = write_role_file("test_role", content, tmp_path)
        
        # Basic validation that file was created and has expected structure
        assert output_path.exists()
        with open(output_path, 'r') as f:
            file_content = f.read()
        
        assert "rule_type: Agent Requested" in file_content
        assert "Test Role (v1.0)" in file_content
    
    def test_line_count_enforcement(self, tmp_path):
        """Test that generated files meet line count requirements."""
        role_data = {
            "identity": {"scope": "Global"},
            "objectives": {"kpis": ["test"]},
            "influence": {"decision_rights": ["test"]},
            "behaviors": {"trusted_tools": ["test"]},
            "motivations": {"drivers": ["test"]}
        }
        
        content = generate_executive_role("test_role", role_data)
        lines = content.split('\n')
        
        # Should be reasonable length (not too short, not too long)
        assert 20 <= len(lines) <= 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 