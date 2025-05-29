#!/usr/bin/env python3
"""
Configuration management for cursor rules scripts.
Provides centralized path resolution and configuration loading.
"""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class CursorRulesConfig:
    """Centralized configuration for cursor rules scripts."""

    def __init__(self, config_path: Path | None = None):
        """Initialize configuration.
        
        Args:
            config_path: Optional path to config file. If None, searches for it.
        """
        self._project_root = self._find_project_root()
        self._config_path = config_path or self._project_root / "cursor_rules_config.json"
        self._config = self._load_config()

    def _find_project_root(self) -> Path:
        """Find project root containing .cursor directory or cursor_rules_config.json."""
        current = Path(__file__).parent.parent.parent  # Start from project root

        # Look for markers of project root
        markers = [".cursor", "cursor_rules_config.json", "pyproject.toml"]

        while current != current.parent:
            if any((current / marker).exists() for marker in markers):
                logger.debug(f"Found project root: {current}")
                return current
            current = current.parent

        # Fallback to current working directory
        logger.warning("Cannot find project root, using current working directory")
        return Path.cwd()

    def _load_config(self) -> dict[str, Any]:
        """Load configuration from JSON file."""
        if not self._config_path.exists():
            logger.warning(f"Config file not found at {self._config_path}, using defaults")
            return self._get_default_config()

        try:
            with open(self._config_path, encoding="utf-8") as f:
                config = json.load(f)
                logger.debug(f"Loaded configuration from {self._config_path}")
                return config
        except (json.JSONDecodeError, OSError) as e:
            logger.error(f"Failed to load config from {self._config_path}: {e}")
            return self._get_default_config()

    def _get_default_config(self) -> dict[str, Any]:
        """Get default configuration if config file is missing."""
        return {
            "paths": {
                "cursor_rules": ".cursor/rules",
                "tool_registry": ".cursor/rules/tools/tool_registry.json",
                "role_library": ".cursor/rules/tools/role_library.json",
                "templates": "templates",
                "scripts": "scripts"
            },
            "validation": {
                "exclude_patterns": ["*.mdc", "*.md", "*.template"],
                "required_tools": ["uv", "ruff"],
                "mdc_linter": "scripts/validation/lint_mdc.py",
                "role_linter": "scripts/roles/lint_role_library.py"
            },
            "defaults": {
                "output_dir": ".cursor/rules/roles",
                "role_types": ["executive", "specialist"],
                "template_dir": "templates/roles"
            },
            "behavior": {
                "interactive_mode": True,
                "strict_validation": False,
                "auto_backup": True,
                "progress_indicators": True
            }
        }

    @property
    def project_root(self) -> Path:
        """Get project root directory."""
        return self._project_root

    def get_path(self, path_key: str) -> Path:
        """Get absolute path for a configured path key.
        
        Args:
            path_key: Key from paths configuration
            
        Returns:
            Absolute path
            
        Raises:
            KeyError: If path_key is not found in configuration
        """
        if path_key not in self._config["paths"]:
            raise KeyError(f"Path key '{path_key}' not found in configuration")

        relative_path = self._config["paths"][path_key]
        return self._project_root / relative_path

    def get_config(self, section: str, key: str | None = None) -> Any:
        """Get configuration value.
        
        Args:
            section: Configuration section
            key: Optional key within section
            
        Returns:
            Configuration value
        """
        if section not in self._config:
            raise KeyError(f"Configuration section '{section}' not found")

        if key is None:
            return self._config[section]

        if key not in self._config[section]:
            raise KeyError(f"Configuration key '{key}' not found in section '{section}'")

        return self._config[section][key]

    def validate_paths(self) -> bool:
        """Validate that required paths exist.
        
        Returns:
            True if all required paths exist, False otherwise
        """
        required_paths = ["cursor_rules", "tool_registry", "role_library"]
        missing_paths = []

        for path_key in required_paths:
            try:
                path = self.get_path(path_key)
                if not path.exists():
                    missing_paths.append(f"{path_key}: {path}")
            except KeyError:
                missing_paths.append(f"{path_key}: not configured")

        if missing_paths:
            logger.error(f"Missing required paths: {missing_paths}")
            return False

        return True

    def ensure_directories(self) -> None:
        """Ensure required directories exist."""
        directories = ["cursor_rules", "templates", "scripts"]

        for dir_key in directories:
            try:
                path = self.get_path(dir_key)
                path.mkdir(parents=True, exist_ok=True)
                logger.debug(f"Ensured directory exists: {path}")
            except KeyError:
                logger.warning(f"Directory key '{dir_key}' not found in configuration")


# Global configuration instance
_config_instance: CursorRulesConfig | None = None


def get_config() -> CursorRulesConfig:
    """Get global configuration instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = CursorRulesConfig()
    return _config_instance


def reset_config() -> None:
    """Reset global configuration instance (useful for testing)."""
    global _config_instance
    _config_instance = None
