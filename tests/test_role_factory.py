#!/usr/bin/env python3
"""
Test suite for Cursor Role Factory.
Validates role generation, structure, and security.
"""
import json
import subprocess
import sys
import tempfile
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
    write_role_file
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
            "executive": {"cmo": {"frameworks": ["growth"], "metrics": ["CAC"]}},
            "specialist": {"security": {"standards": ["nist"], "gates": ["audit"]}}
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
        assert library["executive"]["cmo"]["frameworks"] == ["growth"]
    
    def test_missing_library_file(self, tmp_path):
        """Test handling of missing library file."""
        with patch('create_role.Path') as mock_path:
            mock_path.return_value.parent = tmp_path
            mock_path.return_value.__truediv__.return_value.exists.return_value = False
            
            with pytest.raises(SystemExit):
                load_role_library()


class TestRoleGeneration:
    """Test role content generation."""
    
    @patch('create_role.Prompt.ask')
    def test_executive_role_generation(self, mock_prompt):
        """Test executive role template generation."""
        mock_prompt.side_effect = [
            "growth strategy",  # domain
            "Speak as a growth CMO: data-driven, customer-obsessed",  # voice_style
            "Build sustainable growth engine",  # primary_goal
            "Drive marketing growth",  # mandate
            "Data-driven decisions",  # principle 1
            "Customer-centric approach"  # principle 2
        ]
        
        role_data = {
            "frameworks": ["growth-marketing", "aarrr-metrics"],
            "metrics": ["CAC", "LTV"]
        }
        
        content = generate_executive_role("cmo", role_data)
        
        # Validate structure
        assert "rule_type: Agent Requested" in content
        assert "CMO (v1.0)" in content
        assert "growth-marketing, aarrr-metrics" in content
        assert "CAC, LTV" in content
        assert "Data-driven decisions" in content
        assert "Project Rules override this Role" in content
    
    @patch('create_role.Prompt.ask')
    def test_specialist_role_generation(self, mock_prompt):
        """Test specialist role template generation."""
        mock_prompt.side_effect = [
            "security review",  # domain
            "Speak as security expert: technical, risk-focused",  # voice_style
            "Ensure security and compliance",  # primary_goal
            "Security best practices",  # focus area
            "Threat assessment",  # gate 1
            "Compliance check"  # gate 2
        ]
        
        role_data = {
            "standards": ["nist-framework", "zero-trust"],
            "gates": ["Threat Model", "Pen Test"]
        }
        
        content = generate_specialist_role("security", role_data)
        
        # Validate structure
        assert "rule_type: Agent Requested" in content
        assert "Security (v1.0)" in content
        assert "nist-framework, zero-trust" in content
        assert "Threat assessment" in content
        assert "APPROVED / BLOCKED / NEEDS_REVISION" in content
    
    def test_framework_requirement_validation(self):
        """Test that executive roles validate framework requirements."""
        role_data = {"frameworks": ["single-framework"], "metrics": ["metric1"]}
        
        with patch('create_role.Confirm.ask', return_value=False):
            with pytest.raises(SystemExit):
                generate_executive_role("cmo", role_data)


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
        """Test that malicious input is sanitized."""
        # Test script injection attempts
        malicious_names = [
            "role; rm -rf /",
            "role$(whoami)",
            "role`cat /etc/passwd`",
            "role && echo 'hacked'"
        ]
        
        for name in malicious_names:
            sanitized = validate_role_name(name)
            # Should only contain alphanumeric and allowed characters
            assert all(c.isalnum() or c in '_-' for c in sanitized)
    
    def test_template_placeholder_detection(self):
        """Test that generated content doesn't contain unresolved placeholders."""
        role_data = {"frameworks": ["test-framework", "another-framework"], "metrics": ["test"]}
        
        with patch('create_role.Prompt.ask', return_value="test"):
            content = generate_executive_role("test", role_data)
        
        # Should not contain template placeholders (single braces)
        assert "{role}" not in content
        assert "{title}" not in content
        assert "{frameworks}" not in content
        
        # Should contain output placeholders (double braces) for user customization
        assert "{{finding_1}}" in content
        assert "{{action_1}}" in content


class TestIntegration:
    """Integration tests for the complete workflow."""
    
    def test_lint_validation_integration(self, tmp_path):
        """Test that generated files pass lint validation."""
        # Create a minimal valid role file
        content = """---
rule_type: Agent Requested
description: Test role for validation
---

# Test Role (v1.0)

**Mandate:** Test mandate
**Frameworks:** test-framework
**Success Metrics:** test-metric

**Decision Logic:**
- Test principle 1
- Test principle 2

> Project Rules override this Role if they conflict.

## Output Template

**Test Role Assessment:**
- {{finding_1}}
- {{finding_2}}

**Decision:** <GO / NO-GO / REVISE>
**Next steps:**
- {{action_1}}
- {{action_2}}
"""
        
        test_file = tmp_path / "test_role.mdc"
        test_file.write_text(content)
        
        # Run lint validation
        try:
            result = subprocess.run([
                "uv", "run", "python", "scripts/lint_mdc.py", str(test_file)
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
            
            # Should pass validation (line count under 150)
            assert result.returncode == 0
            assert "within limit" in result.stdout or "PASS" in result.stdout
        except FileNotFoundError:
            pytest.skip("lint_mdc.py not found - integration test skipped")
    
    def test_line_count_enforcement(self, tmp_path):
        """Test that files exceeding 150 lines are rejected."""
        # Create a file with too many lines
        long_content = "---\nrule_type: Agent Requested\n---\n\n" + "\n".join([f"Line {i}" for i in range(150)])
        
        test_file = tmp_path / "long_role.mdc"
        test_file.write_text(long_content)
        
        try:
            result = subprocess.run([
                "uv", "run", "python", "scripts/lint_mdc.py", str(test_file)
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
            
            # Should fail validation
            assert result.returncode == 1
            assert "exceeds" in result.stdout or "FAIL" in result.stdout
        except FileNotFoundError:
            pytest.skip("lint_mdc.py not found - integration test skipped")


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 