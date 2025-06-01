#!/usr/bin/env python3
"""
Test suite for MDC file linter.
Validates line count checking, structure validation, and security features.
"""

import os
import sys
from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from lint_mdc import (
    DEFAULT_LINE_LIMIT,
    SINGLE_BRACE_PATTERN,
    YAML_FRONTMATTER_PATTERN,
    check_file,
    display_summary,
    main,
    sanitize_file_path,
)


class TestPathSanitization:
    """Test file path sanitization and security."""

    def test_valid_paths(self, tmp_path: Path) -> None:
        """Test that valid relative and absolute paths are accepted."""
        test_file = tmp_path / "test.mdc"
        test_file.write_text("content")

        # Test relative path
        sanitized = sanitize_file_path(str(test_file))
        assert sanitized.exists()

        # Test absolute path within project
        sanitized = sanitize_file_path(str(test_file.absolute()))
        assert sanitized.exists()

    def test_dangerous_paths_rejected(self) -> None:
        """Test that dangerous path patterns are rejected."""
        dangerous_paths: list[str] = [
            "../../../etc/passwd",
            "~/malicious",
            "file$with$vars",
            "file`with`backticks",
            "file;with;semicolons",
            "file|with|pipes",
            "file&with&ampersands",
        ]

        for dangerous_path in dangerous_paths:
            with pytest.raises(ValueError, match="Potentially dangerous file path"):
                sanitize_file_path(dangerous_path)

    def test_nonexistent_path_handling(self) -> None:
        """Test handling of nonexistent paths."""
        with pytest.raises(ValueError, match="File does not exist"):
            sanitize_file_path("/nonexistent/path/that/should/not/exist")


class TestFileValidation:
    """Test file content validation logic."""

    def test_valid_executive_role(self, tmp_path: Path) -> None:
        """Test validation of a properly formatted executive role."""
        content = """---
rule_type: Agent Requested
description: Test executive role
---

# Test Executive (v1.0)

## Identity & Context
* Scope / region: Global
* Seniority: C-level

## Objectives, KPIs & Mandate
* Top objectives: Test objectives
* Success metrics: Test metrics

## Influence & Decision Power
* Decision rights: Test decisions
* Key stakeholders: Test stakeholders

## Behaviors, Tools & Preferences
* Comms style: Test comms
* Trusted tools: Test tools

## Motivations, Pain Points & Constraints
* Drivers: Test drivers
* Pain points: Test pain points

## Output Template
**Test Assessment:**
- {{finding_1}}
- {{finding_2}}
"""

        test_file = tmp_path / "test_executive.mdc"
        test_file.write_text(content)

        is_valid, line_count, _ = check_file(test_file, "test-001")

        assert is_valid is True
        assert line_count == len(content.split("\n"))

    def test_valid_specialist_role(self, tmp_path: Path) -> None:
        """Test validation of a properly formatted specialist role."""
        content = """---
rule_type: Agent Requested
description: Test specialist role
---

# Test Specialist (v1.0)

## Identity & Context
* Scope / focus: Test scope
* Seniority: Senior specialist

## Objectives & Quality Standards
* Top objectives: Test objectives
* Success metrics: Test metrics

## Quality Gates & Behaviors
* Quality gates: Test gates
* Trusted tools: Test tools

## Output Template
**Test Review:**
- {{technical_finding}}
- {{recommendation}}
"""

        test_file = tmp_path / "test_specialist.mdc"
        test_file.write_text(content)

        is_valid, line_count, _ = check_file(test_file, "test-002")

        assert is_valid is True
        assert line_count == len(content.split("\n"))

    def test_line_limit_exceeded(self, tmp_path: Path) -> None:
        """Test that files exceeding line limits are flagged."""
        # Create content that exceeds default limit
        long_content = "---\nrule_type: Agent Requested\n---\n\n"
        long_content += "\n".join([f"Line {i}" for i in range(200)])

        test_file = tmp_path / "long_file.mdc"
        test_file.write_text(long_content)

        is_valid, line_count, _ = check_file(test_file, "test-003")

        assert is_valid is False
        assert line_count > DEFAULT_LINE_LIMIT

    def test_missing_yaml_frontmatter(self, tmp_path: Path) -> None:
        """Test detection of missing YAML front-matter."""
        content = """# Test Role (v1.0)

## Identity & Context
* Test content
"""

        test_file = tmp_path / "no_yaml.mdc"
        test_file.write_text(content)

        # check_file returns a tuple of (is_valid, line_count, warnings)
        # We capture warnings to check for specific messages
        is_valid, _, warnings = check_file(test_file, "test-004")

        # Should pass line count but have warnings
        assert is_valid is True  # Line count is fine
        assert any("Missing YAML frontmatter" in warning for warning in warnings)

    def test_missing_rule_type(self, tmp_path: Path) -> None:
        """Test detection of missing rule_type."""
        content = """---
description: Test role without rule_type
---

# Test Role (v1.0)

## Identity & Context
* Test content
"""

        test_file = tmp_path / "no_rule_type.mdc"
        test_file.write_text(content)

        is_valid, _, warnings = check_file(test_file, "test-005")

        # Should pass line count but have warnings
        assert is_valid is True
        assert any(
            "'rule_type' not found in YAML frontmatter" in warning
            for warning in warnings
        )

    def test_unresolved_placeholders(self, tmp_path: Path) -> None:
        """Test detection of unresolved template placeholders."""
        content = """---
rule_type: Agent Requested
---

# Test Role (v1.0)

## Identity & Context
* Unresolved placeholder: {placeholder_name}
* Valid template: {{template_var}}
"""

        test_file = tmp_path / "unresolved.mdc"
        test_file.write_text(content)

        is_valid, _, warnings = check_file(test_file, "test-006")

        # Should pass line count but have warnings about placeholders
        assert is_valid is True
        assert any(
            "Potential unresolved placeholder: {placeholder_name}" in warning
            for warning in warnings
        )

    def test_missing_executive_sections(self, tmp_path: Path) -> None:
        """Test detection of missing required executive sections."""
        content = """---
rule_type: Agent Requested
file_name: test_executive.mdc # Added to allow role type detection
---

# Test Executive (v1.0)

## Identity & Context
* Scope / region: Global

## Objectives, KPIs & Mandate
* Top objectives: Test objectives
"""

        test_file = tmp_path / "incomplete_executive.mdc"
        test_file.write_text(content)

        is_valid, _, warnings = check_file(test_file, "test-007")

        # Should pass line count but have warnings about missing sections
        assert is_valid is True
        assert any(
            "Missing required executive section: 'Influence & Decision Power'"
            in warning
            for warning in warnings
        )

    def test_missing_specialist_sections(self, tmp_path: Path) -> None:
        """Test detection of missing required specialist sections."""
        content = """---
rule_type: Agent Requested
file_name: test_specialist.mdc # Added to allow role type detection
---

# Test Specialist (v1.0)

## Identity & Context
* Scope / focus: Test scope
"""

        test_file = tmp_path / "incomplete_specialist.mdc"
        test_file.write_text(content)

        is_valid, _, warnings = check_file(test_file, "test-008")

        # Should pass line count but have warnings about missing sections
        assert is_valid is True
        assert any(
            "Missing required specialist section: 'Quality Gates & Behaviors'"
            in warning
            for warning in warnings
        )

    def test_file_not_found(self, tmp_path: Path) -> None:
        """Test handling of non-existent files."""
        non_existent_file = tmp_path / "does_not_exist.mdc"

        is_valid, line_count_val, warnings = check_file(non_existent_file, "test-009")

        assert is_valid is False
        assert line_count_val == 0  # Corrected variable name
        assert any("File does not exist" in warning for warning in warnings)

    def test_file_read_error(self, tmp_path: Path) -> None:
        """Test handling of file read errors."""
        test_file = tmp_path / "test.mdc"
        test_file.write_text("content")

        # Mock a read error by making the file unreadable
        with patch("builtins.open", side_effect=PermissionError("Access denied")):
            is_valid, line_count_val, warnings = check_file(test_file, "test-010")

            assert is_valid is False
            assert line_count_val == 0  # Corrected variable name
            assert any("Access denied" in warning for warning in warnings)


class TestRegexPatterns:
    """Test regex pattern matching."""

    def test_single_brace_pattern(self) -> None:
        """Test single brace pattern detection."""
        # Should match single braces
        assert SINGLE_BRACE_PATTERN.search("{placeholder}")
        assert SINGLE_BRACE_PATTERN.search("text {var} more")
        assert SINGLE_BRACE_PATTERN.search("{multi_word_var}")

        # Should NOT match double braces (template variables)
        assert not SINGLE_BRACE_PATTERN.search("{{template_var}}")
        assert not SINGLE_BRACE_PATTERN.search("text {{valid}} more")

        # Should NOT match empty braces
        assert not SINGLE_BRACE_PATTERN.search("{}")

        # Edge case: nested braces - the inner single brace should be detected
        # This is expected behavior as the regex finds single braces
        match = SINGLE_BRACE_PATTERN.search("{{nested {inner} braces}}")
        assert match is not None
        assert match.group(1) == "inner"  # Check the captured group

    def test_yaml_frontmatter_pattern(self) -> None:
        """Test YAML frontmatter pattern detection."""
        # Should match valid frontmatter start
        assert YAML_FRONTMATTER_PATTERN.search("---\nrule_type: Agent Requested")

        # Should match at start of string
        valid_yaml = """---
rule_type: Agent Requested
description: Test
---"""
        assert YAML_FRONTMATTER_PATTERN.search(valid_yaml)

        # Should NOT match when not at start
        assert not YAML_FRONTMATTER_PATTERN.search("text before\n---\nrule_type: Test")


class TestDisplaySummary:
    """Test summary display functionality."""

    def test_all_files_pass(self, tmp_path: Path, capsys: Any) -> None:
        """Test summary when all files pass validation."""
        results: list[tuple[str, bool, int]] = [
            ("file1.mdc", True, 50),
            ("file2.mdc", True, 75),
        ]

        display_summary(results, "test-001")

        captured = capsys.readouterr()
        assert "All 2 files passed validation!" in captured.out
        assert "PASSED FILES:" in captured.out  # Removed styling for robustness
        assert "NO FILES FAILED" in captured.out  # Removed styling

    def test_some_files_fail(self, tmp_path: Path, capsys: Any) -> None:
        """Test summary when some files fail validation."""
        results: list[tuple[str, bool, int]] = [
            ("file1.mdc", True, 50),
            ("file2.mdc", False, 200),
        ]

        display_summary(results, "test-002")

        captured = capsys.readouterr()
        assert "1 of 2 files failed validation" in captured.out
        assert "PASSED FILES:" in captured.out
        assert "FAILED FILES:" in captured.out

    def test_no_files_pass(self, tmp_path: Path, capsys: Any) -> None:
        """Test summary when no files pass validation."""
        results: list[tuple[str, bool, int]] = [
            ("file1.mdc", False, 200),
            ("file2.mdc", False, 180),
        ]

        display_summary(results, "test-003")

        captured = capsys.readouterr()
        assert "2 of 2 files failed validation" in captured.out
        assert "NO FILES PASSED" in captured.out
        assert "FAILED FILES:" in captured.out


class TestMainFunction:
    """Test main function behavior."""

    def test_no_arguments(self, capsys: Any) -> None:
        """Test main function with no arguments."""
        with patch("sys.argv", ["lint_mdc.py"]):
            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 1
            captured = capsys.readouterr()
            assert "Usage:" in captured.out

    def test_successful_validation(self, tmp_path: Path) -> None:
        """Test main function with valid files."""
        # Create valid test files
        valid_content = """---
rule_type: Agent Requested
description: Test role
file_name: test_role.mdc
---

# Test Role (v1.0)

## Identity & Context
* Scope: Test
* Seniority: Test

## Objectives & Quality Standards
* Top objectives: Test objectives

## Quality Gates & Behaviors
* Quality gates: Test gates
"""

        test_file1 = tmp_path / "test1.mdc"
        test_file1.write_text(valid_content, encoding="utf-8")

        test_file2 = tmp_path / "test2.mdc"
        test_file2.write_text(valid_content, encoding="utf-8")

        argv = ["lint_mdc.py", str(test_file1), str(test_file2)]
        with patch("sys.argv", argv):
            try:
                main()
                assert True  # If no SystemExit, it passed
            except SystemExit as e:
                assert e.code == 0, f"main() exited with {e.code} for valid files"

    def test_failed_validation(self, tmp_path: Path) -> None:
        """Test main function with invalid files."""
        # Create file that exceeds line limit
        long_content = "---\nrule_type: Agent Requested\n---\n\n"
        long_content += "\n".join([f"Line {i}" for i in range(DEFAULT_LINE_LIMIT + 50)])

        test_file = tmp_path / "long_file.mdc"
        test_file.write_text(long_content, encoding="utf-8")

        argv = ["lint_mdc.py", str(test_file)]
        with patch("sys.argv", argv):
            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 1

    def test_dangerous_path_handling(self) -> None:
        """Test main function with dangerous paths."""
        argv = ["lint_mdc.py", "../../../etc/passwd"]
        with patch("sys.argv", argv):
            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 1


class TestEnvironmentConfiguration:
    """Test environment variable configuration."""

    def test_custom_line_limit_via_env(self, tmp_path: Path) -> None:
        """Test that MDC_LINE_LIMIT environment variable overrides default."""
        content_over_default_under_custom = (
            "---\nrule_type: Agent Requested\nfile_name: custom_limit_test.mdc\n---\n"
            + "\n".join(
                [f"Line {i}" for i in range(DEFAULT_LINE_LIMIT + 10)]  # e.g. 160 lines
            )
        )
        test_file = tmp_path / "custom_limit.mdc"
        test_file.write_text(content_over_default_under_custom, encoding="utf-8")

        # Test with default limit (should fail)
        # Ensure we are using the `check_file` from the initially imported `lint_mdc`
        initial_lint_mdc_module = sys.modules["lint_mdc"]
        is_valid_default, _, _ = initial_lint_mdc_module.check_file(
            test_file, "env-default"
        )
        assert not is_valid_default, "Should fail with default line limit"

        # Test with custom limit via environment variable (should pass)
        with patch.dict(os.environ, {"MDC_LINE_LIMIT": "200"}):
            reloaded_lint_mdc_module = importlib.reload(
                sys.modules["lint_mdc"]
            )  # Reload to pick up env var
            is_valid_custom, _, _ = reloaded_lint_mdc_module.check_file(
                test_file, "env-custom"
            )
            assert is_valid_custom, "Should pass with custom line limit 200"

        # Cleanup: Reload module again to reset to default for subsequent tests
        # Ensure the key is removed if it was added, then reload
        if (
            "MDC_LINE_LIMIT" in os.environ
        ):  # Should be false here if patch.dict worked as expected
            del os.environ["MDC_LINE_LIMIT"]
        final_reloaded_lint_mdc_module = importlib.reload(sys.modules["lint_mdc"])
        # Optionally, assert that the DEFAULT_LINE_LIMIT is back to original if needed for other tests
        assert final_reloaded_lint_mdc_module.DEFAULT_LINE_LIMIT == DEFAULT_LINE_LIMIT


class TestIntegration:
    """Integration tests for complete workflows."""

    def test_mixed_file_validation(self, tmp_path: Path) -> None:
        """Test validation of mixed valid and invalid files."""
        # Create valid file
        valid_content = """---
rule_type: Agent Requested
description: Valid test role
file_name: valid.mdc
---

# Valid Role (v1.0)

## Identity & Context
* Scope: Test scope
* Seniority: Test level

## Objectives & Quality Standards
* Top objectives: Test objectives

## Quality Gates & Behaviors
* Quality gates: Test gates
"""

        valid_file = tmp_path / "valid.mdc"
        valid_file.write_text(valid_content, encoding="utf-8")

        # Create invalid file (too long)
        invalid_content = "---\nrule_type: Agent Requested\n---\n\n"
        invalid_content += "\n".join(
            [f"Line {i}" for i in range(DEFAULT_LINE_LIMIT + 1)]
        )

        invalid_file = tmp_path / "invalid.mdc"
        invalid_file.write_text(invalid_content, encoding="utf-8")

        # Test both files
        is_valid_valid, line_count_valid, _ = check_file(valid_file, "test-001")
        is_valid_invalid, line_count_invalid, _ = check_file(invalid_file, "test-002")

        assert is_valid_valid is True
        assert is_valid_invalid is False
        assert line_count_valid < DEFAULT_LINE_LIMIT
        assert line_count_invalid > DEFAULT_LINE_LIMIT

    def test_correlation_id_usage_in_check_file(
        self, tmp_path: Path, caplog: LogCaptureFixture
    ) -> None:
        """Test that correlation ID is present in log messages from check_file."""
        test_file = tmp_path / "correlation_test.mdc"
        test_file.write_text(
            "---\nrule_type: Agent Requested\nfile_name: correlation.mdc\n---\n# Test",
            encoding="utf-8",
        )
        correlation_id = "cid-log-test-123"

        with caplog.at_level("INFO"):
            # Use the initially imported check_file or ensure context for reloaded module
            lint_mdc_module_to_use = sys.modules.get(
                "lint_mdc", initial_lint_mdc_module
            )
            lint_mdc_module_to_use.check_file(test_file, correlation_id)

        assert any(
            correlation_id in record.message for record in caplog.records
        ), f"Correlation ID '{correlation_id}' not found in logs: {caplog.text}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
