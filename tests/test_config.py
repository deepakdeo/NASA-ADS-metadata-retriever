"""
Tests for configuration loader.

Tests for loading configuration from various sources.
"""

import pytest
import tempfile
from pathlib import Path
import os

from nasa_ads.config.config_loader import ConfigLoader, get_default_config


class TestConfigLoader:
    """Tests for configuration loader."""

    def test_create_config_loader(self):
        """Test creating config loader."""
        loader = ConfigLoader()
        assert loader is not None

    def test_get_default_config(self):
        """Test getting default configuration."""
        config = get_default_config()

        assert "api_key" in config
        assert "api_base_url" in config
        assert "timeout" in config

    def test_config_get(self):
        """Test getting config values."""
        loader = ConfigLoader()
        loader.set("test_key", "test_value")

        assert loader.get("test_key") == "test_value"

    def test_config_get_default(self):
        """Test getting config with default."""
        loader = ConfigLoader()

        value = loader.get("nonexistent_key", "default_value")
        assert value == "default_value"

    def test_config_to_dict(self):
        """Test converting config to dict."""
        loader = ConfigLoader()
        loader.set("key1", "value1")
        loader.set("key2", "value2")

        config_dict = loader.to_dict()
        assert isinstance(config_dict, dict)

    def test_load_env_file(self):
        """Test loading from .env file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            env_file = Path(tmpdir) / ".env"
            env_file.write_text("NASA_ADS_API_KEY=test_key_123456\n")

            loader = ConfigLoader(env_file=env_file)
            # Should load from environment if set
            # (actual env var loading depends on dotenv)

    def test_yaml_loading_missing(self):
        """Test loading with missing YAML file."""
        loader = ConfigLoader(config_file=Path("/nonexistent/file.yaml"))
        # Should not raise, just skip YAML loading
        assert loader is not None

    def test_config_from_default_locations(self):
        """Test loading from default locations."""
        loader = ConfigLoader.from_default_locations()
        assert loader is not None

    def test_config_validate_missing_api_key(self):
        """Test validation with missing API key."""
        loader = ConfigLoader()
        loader._config.pop("api_key", None)

        with pytest.raises(ValueError, match="API key not found"):
            loader.validate()

    def test_config_validate_with_api_key(self):
        """Test validation with API key."""
        loader = ConfigLoader()
        loader.set("api_key", "test_key_1234567890")

        assert loader.validate() is True
