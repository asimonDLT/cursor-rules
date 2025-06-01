#!/usr/bin/env python3
"""
Test suite for Cursor Role Factory.

Validates role generation, structure, and security.
"""

import json
import sys
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest
from pytest import MonkeyPatch

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from create_role import (
    generate_executive_role,
    generate_specialist_role,
    load_role_library,
    validate_cli_input,
    validate_role_name,
    write_role_file,
)


class TestRoleNameValidation:
    """Test role name sanitization and validation."""

    def test_valid_role_names(self) -> None:
        """Test that valid role names pass through unchanged."""
        assert validate_role_name("cmo") == "cmo"
        assert validate_role_name("qa_lead") == "qa_lead"
        assert validate_role_name("frontend-architect") == "frontend-architect"

    def test_name_sanitization(self) -> None:
        """Test that invalid characters are removed and name lowercased."""
        assert validate_role_name("CMO") == "cmo"
        assert validate_role_name("qa@lead! complexe") == "qaleadcomplexe"
        assert validate_role_name("Test Role With Spaces") == "testrolewithspaces"

    def test_empty_name_rejection(self) -> None:
        """Test that empty or fully invalid names are rejected."""
        with pytest.raises(SystemExit):
            validate_role_name("")
        with pytest.raises(SystemExit):
            validate_role_name("@#$%^&")


class TestRoleLibrary:
    """Test role library loading and validation."""

    @pytest.fixture
    def mock_library_path(self, monkeypatch: MonkeyPatch, tmp_path: Path) -> Path:
        """Mocks the path to role_library.json within the templates directory."""
        # Construct what Path("../templates") would resolve to in the test environment
        # Assuming script is in scripts/ and templates/ is a sibling of scripts/
        # This needs to correctly mock the path formation in `load_role_library`
        mock_templates_dir = tmp_path / "templates"
        mock_templates_dir.mkdir(exist_ok=True)
        mock_lib_file = mock_templates_dir / "role_library.json"

        # Patch create_role.ROLE_LIBRARY_PATH to use this mock path
        monkeypatch.setattr("create_role.ROLE_LIBRARY_PATH", mock_lib_file)
        return mock_lib_file

    def test_load_valid_library(self, mock_library_path: Path) -> None:
        """Test loading a valid role library from the mocked path."""
        library_data: dict[str, Any] = {
            "executive": {
                "cmo": {
                    "identity": {"scope": "Global Marketing"},
                    "objectives": {"kpis": ["Customer Acquisition Cost"]},
                }
            },
            "specialist": {
                "security_analyst": {
                    "identity": {"scope": "Security Operations"},
                    "objectives": {"kpis": ["Mean Time to Detect"]},
                }
            },
        }
        with open(mock_library_path, "w", encoding="utf-8") as f:
            json.dump(library_data, f)

        library = load_role_library()
        assert "executive" in library
        assert "specialist" in library
        assert library["executive"]["cmo"]["identity"]["scope"] == "Global Marketing"

    def test_missing_library_file(self, mock_library_path: Path) -> None:
        """Test handling of missing library file (path itself exists, file doesn't)."""
        # mock_library_path is set up, but we don't write a file to it.
        if mock_library_path.exists():  # Ensure it does not exist for this test
            mock_library_path.unlink()

        with pytest.raises(SystemExit):
            load_role_library()


class TestRoleGeneration:
    """Test role content generation for different role types."""

    def test_executive_role_generation(self) -> None:
        """Test executive role template generation with various fields."""
        role_data: dict[str, Any] = {
            "identity": {
                "scope": "Global Operations",
                "seniority": "EVP",
                "span_of_control": "Multiple business units",
            },
            "objectives": {
                "top_objectives": ["Improve operational efficiency by 15%"],
                "kpis": ["Opex Ratio", "Process Cycle Time"],
            },
            "influence": {
                "decision_rights": ["Budget allocation for operations"],
                "stakeholders": ["CEO", "CFO", "Business Unit Heads"],
            },
            "behaviors": {
                "comms": ["Monthly operational reviews", "Quarterly strategic updates"],
                "trusted_tools": ["Salesforce", "SAP", "Tableau"],
                "risk_posture": "Risk-averse in core operations, moderate in new initiatives",
            },
            "motivations": {
                "drivers": ["Operational excellence", "Cost optimization"],
                "pain_points": ["Siloed data", "Legacy systems integration"],
            },
        }
        content: str = generate_executive_role("coo", role_data)
        assert "rule_type: Agent Requested" in content
        assert "COO (v1.0)" in content
        assert "Opex Ratio, Process Cycle Time" in content
        assert "Improve operational efficiency by 15%" in content
        assert "Project rules override this Role" in content
        assert "{{finding_1}}" in content

    def test_specialist_role_generation(self) -> None:
        """Test specialist role template generation with specific fields."""
        role_data: dict[str, Any] = {
            "identity": {
                "scope": "Frontend Web Development",
                "seniority": "Lead Developer",
                "span_of_control": "Frontend development team (5 engineers)",
            },
            "objectives": {
                "top_objectives": ["Deliver high-quality user interfaces"],
                "kpis": ["Page Load Time", "Lighthouse Performance Score"],
            },
            "standards": [
                "W3C Accessibility Guidelines (WCAG) 2.1 AA",
                "Responsive Design",
            ],
            "gates": ["Code Review by 2 peers", "Automated E2E tests pass"],
            "behaviors": {
                "tool_domains": ["frontend"],
                "trusted_tools": ["React", "TypeScript", "Jest"],
            },
        }
        content: str = generate_specialist_role("frontend_lead", role_data)
        assert "rule_type: Agent Requested" in content
        assert "Frontend Lead (v1.0)" in content
        assert (
            "W3C Accessibility Guidelines (WCAG) 2.1 AA, Responsive Design" in content
        )
        assert "Deliver high-quality user interfaces" in content
        assert "APPROVED / BLOCKED / NEEDS_REVISION" in content
        assert "{{technical_finding}}" in content

    def test_minimal_data_role_generation(self) -> None:
        """Test roles can be generated with only minimal required data."""
        # Executive minimal
        exec_min_data: dict[str, Any] = {
            "identity": {"scope": "Minimal Executive"},
            "objectives": {"kpis": ["MinKPI"]},
        }
        exec_content: str = generate_executive_role("min_exec", exec_min_data)
        assert "Min Exec (v1.0)" in exec_content
        assert "MinKPI" in exec_content

        # Specialist minimal
        spec_min_data: dict[str, Any] = {
            "identity": {"scope": "Minimal Specialist"},
            "objectives": {"kpis": ["MinMetric"]},
            "standards": ["Minimal Standard"],
        }
        spec_content: str = generate_specialist_role("min_spec", spec_min_data)
        assert "Min Spec (v1.0)" in spec_content
        assert "MinMetric" in spec_content


class TestFileOperations:
    """Test file writing operations including overwrite protection."""

    def test_write_role_file(self, tmp_path: Path) -> None:
        """Test writing role content to a new file."""
        content = """---
rule_type: Agent Requested
description: Test Role File Output
---
# Test Role Output (v1.0)
Content for file write test.
"""
        output_path: Path = write_role_file("file_op_test", content, tmp_path)
        assert output_path.exists()
        assert output_path.name == "file_op_test.mdc"
        with open(output_path, encoding="utf-8") as f:
            written_content = f.read()
        assert written_content == content

    def test_overwrite_protection_denied(self, tmp_path: Path) -> None:
        """Test that existing files are protected if user denies overwrite."""
        existing_file: Path = tmp_path / "overwrite_test.mdc"
        original_content = "Original Content - Do Not Overwrite"
        existing_file.write_text(original_content, encoding="utf-8")

        with patch("create_role.Confirm.ask", return_value=False):
            with pytest.raises(SystemExit):
                write_role_file("overwrite_test", "New Content", tmp_path)
        # Verify file was not overwritten
        assert existing_file.read_text(encoding="utf-8") == original_content

    def test_overwrite_protection_confirmed(self, tmp_path: Path) -> None:
        """Test that existing files can be overwritten if user confirms."""
        existing_file: Path = tmp_path / "overwrite_confirmed.mdc"
        existing_file.write_text("Old Content", encoding="utf-8")
        new_content = "New Content After Overwrite Confirmation"

        with patch("create_role.Confirm.ask", return_value=True):
            write_role_file("overwrite_confirmed", new_content, tmp_path)
        assert existing_file.read_text(encoding="utf-8") == new_content


class TestSecurityAndInputValidation:
    """Test security features, input sanitization, and validation logic."""

    def test_role_name_input_sanitization_detailed(self) -> None:
        """Test detailed role name sanitization for various malicious inputs."""
        malicious_examples: list[tuple[str, str]] = [
            ("role; rm -rf /", "rolermrf"),
            ("role$(whoami)", "rolewhoami"),
            ("role && echo 'hacked'", "roleechohacked"),
            ("role`cat /etc/passwd`", "rolecatetcpasswd"),
            ("role<script>alert()</script>", "rolescriptalertscript"),
            ("role with spaces and !@#$", "rolewithspacesand"),
        ]
        for malicious_input, expected_sanitized in malicious_examples:
            assert validate_role_name(malicious_input) == expected_sanitized

    def test_cli_input_validation_dangerous_patterns(self) -> None:
        """Test CLI input validation rejects dangerous patterns."""
        dangerous_cli_inputs: list[str] = [
            "{{ some_injection }}",
            "<img src=x onerror=alert(1)>",
            "javascript:doEvil()",
            "`rm -rf *`",
            "$(touch hacked.txt)",
        ]
        for dangerous_input in dangerous_cli_inputs:
            assert not validate_cli_input(dangerous_input, "test_field_name")

    def test_cli_input_validation_safe_patterns(self) -> None:
        """Test CLI input validation accepts safe, common inputs."""
        safe_cli_inputs: list[str] = [
            "My Role Name",
            "A description with spaces, commas, and periods.",
            "alpha-numeric_with-hyphens_and_underscores",
            "email@example.com",
            "https://example.com/path?query=value#fragment",
        ]
        for safe_input in safe_cli_inputs:
            assert validate_cli_input(safe_input, "test_field_name")

    def test_template_output_placeholders_are_correct(self) -> None:
        """Verify that generated content uses double-brace placeholders correctly."""
        exec_role_data: dict[str, Any] = {
            "identity": {"scope": "Global"},
            "objectives": {"kpis": ["KPI"]},
            "influence": {},
            "behaviors": {},
            "motivations": {},
        }
        exec_content: str = generate_executive_role("placeholder_exec", exec_role_data)
        assert "{{finding_1}}" in exec_content
        assert "{{action_1}}" in exec_content
        assert "{single_brace_problem}" not in exec_content

        spec_role_data: dict[str, Any] = {
            "identity": {"scope": "Technical"},
            "objectives": {"kpis": ["Metric"]},
            "standards": ["StandardX"],
            "behaviors": {},
        }
        spec_content: str = generate_specialist_role("placeholder_spec", spec_role_data)
        assert "{{technical_finding}}" in spec_content
        assert "{{recommendation}}" in spec_content
        assert "{another_single_brace}}" not in spec_content


class TestIntegrationScenarios:
    """Test integration of various components like file creation and linting."""

    def test_generated_file_properties_for_linting(self, tmp_path: Path) -> None:
        """Test that generated files have properties that would pass basic linting."""
        # Executive Role
        exec_role_data: dict[str, Any] = {
            "identity": {"scope": "Global Exec"},
            "objectives": {"kpis": ["Growth"]},
            "influence": {},
            "behaviors": {},
            "motivations": {},
        }
        exec_content: str = generate_executive_role("lint_exec", exec_role_data)
        exec_output_path: Path = write_role_file("lint_exec", exec_content, tmp_path)

        assert exec_output_path.exists()
        with open(exec_output_path, encoding="utf-8") as f:
            exec_file_content = f.read()
        assert "rule_type: Agent Requested" in exec_file_content
        assert "Lint Exec (v1.0)" in exec_file_content
        assert len(exec_file_content.splitlines()) < 150

        # Specialist Role
        spec_role_data: dict[str, Any] = {
            "identity": {"scope": "Tech Specialist"},
            "objectives": {"kpis": ["Uptime"]},
            "standards": ["High Availability"],
            "behaviors": {},
        }
        spec_content: str = generate_specialist_role("lint_spec", spec_role_data)
        spec_output_path: Path = write_role_file("lint_spec", spec_content, tmp_path)

        assert spec_output_path.exists()
        with open(spec_output_path, encoding="utf-8") as f:
            spec_file_content = f.read()
        assert "rule_type: Agent Requested" in spec_file_content
        assert "Lint Spec (v1.0)" in spec_file_content
        assert len(spec_file_content.splitlines()) < 150

    def test_line_count_of_generated_roles(self) -> None:
        """Ensure generated roles have a reasonable line count (not too long/short)."""
        exec_role_data: dict[str, Any] = {
            "identity": {
                "scope": "TestScope",
                "seniority": "TestSeniority",
                "span_of_control": "TestSpan",
            },
            "objectives": {"top_objectives": ["Obj1"], "kpis": ["KPI1"]},
            "influence": {"decision_rights": ["DR1"], "stakeholders": ["SH1"]},
            "behaviors": {
                "comms": ["C1"],
                "trusted_tools": ["T1"],
                "risk_posture": "RP1",
            },
            "motivations": {"drivers": ["D1"], "pain_points": ["PP1"]},
        }
        exec_content: str = generate_executive_role("line_count_exec", exec_role_data)
        assert 30 <= len(exec_content.splitlines()) <= 100

        spec_role_data: dict[str, Any] = {
            "identity": {
                "scope": "TestScope",
                "seniority": "TestSeniority",
                "span_of_control": "TestSpan",
            },
            "objectives": {"top_objectives": ["Obj1"], "kpis": ["KPI1"]},
            "standards": ["Std1", "Std2"],
            "gates": ["Gate1"],
            "behaviors": {"tool_domains": ["dom1"], "trusted_tools": ["toolA"]},
        }
        spec_content: str = generate_specialist_role("line_count_spec", spec_role_data)
        assert 30 <= len(spec_content.splitlines()) <= 100


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
