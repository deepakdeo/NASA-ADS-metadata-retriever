"""
Configuration management for NASA ADS metadata retriever.

This module handles loading and managing configuration from multiple sources:
- Environment variables (.env files)
- YAML configuration files
- Programmatic defaults
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv


class ConfigLoader:
    """
    Load and manage configuration from multiple sources.

    Priority order:
    1. Environment variables
    2. .env file in current/specified directory
    3. YAML config file
    4. Built-in defaults
    """

    def __init__(
        self,
        env_file: Optional[Path] = None,
        config_file: Optional[Path] = None,
    ):
        """
        Initialize configuration loader.

        Args:
            env_file: Path to .env file (default: .env in current dir)
            config_file: Path to YAML config file
        """
        self.env_file = env_file or Path(".env")
        self.config_file = config_file
        self._config: Dict[str, Any] = {}
        self._load_configuration()

    def _load_configuration(self) -> None:
        """Load configuration from all sources."""
        # Load from .env file if exists
        if self.env_file.exists():
            load_dotenv(self.env_file)

        # Load from YAML if specified
        if self.config_file and self.config_file.exists():
            with open(self.config_file) as f:
                yaml_config = yaml.safe_load(f)
                if yaml_config:
                    self._config.update(yaml_config)

        # Environment variables override everything
        self._config.update(self._load_env_vars())

    @staticmethod
    def _load_env_vars() -> Dict[str, Any]:
        """Extract NASA_ADS_* environment variables."""
        env_vars = {}
        for key, value in os.environ.items():
            if key.startswith("NASA_ADS_"):
                # Convert NASA_ADS_API_KEY to api_key
                config_key = key.replace("NASA_ADS_", "").lower()
                env_vars[config_key] = value
        return env_vars

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.

        Args:
            key: Configuration key (supports dot notation for nested values)
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        if "." in key:
            keys = key.split(".")
            value = self._config
            for k in keys:
                if isinstance(value, dict):
                    value = value.get(k)
                    if value is None:
                        return default
                else:
                    return default
            return value
        return self._config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self._config[key] = value

    def to_dict(self) -> Dict[str, Any]:
        """Get entire configuration as dictionary."""
        return self._config.copy()

    @classmethod
    def from_default_locations(cls) -> "ConfigLoader":
        """
        Create ConfigLoader using default locations.

        Searches for:
        - .env file in current directory
        - nasa_ads.yaml config file in current directory
        """
        env_file = Path.cwd() / ".env"
        config_file = Path.cwd() / "nasa_ads.yaml"

        if not config_file.exists():
            config_file = None

        return cls(env_file=env_file, config_file=config_file)

    def validate(self) -> bool:
        """Validate required configuration."""
        api_key = self.get("api_key")
        if not api_key:
            raise ValueError(
                "API key not found. Set NASA_ADS_API_KEY env var or in config file"
            )
        return True


def get_default_config() -> Dict[str, Any]:
    """Get default configuration values."""
    return {
        "api_key": "",
        "api_base_url": "https://api.adsabs.harvard.edu/v1",
        "timeout": 30,
        "max_retries": 3,
        "retry_backoff_factor": 0.5,
        "rows_per_request": 100,
        "output_format": "csv",
        "log_level": "INFO",
    }
