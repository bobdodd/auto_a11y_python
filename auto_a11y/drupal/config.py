"""
Drupal Configuration Management

Handles loading and validation of Drupal connection settings.
"""

import os
import logging
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DrupalConfig:
    """Configuration for Drupal JSON:API connection"""

    base_url: str
    username: str
    password: str
    enabled: bool = True

    @classmethod
    def from_env(cls) -> 'DrupalConfig':
        """
        Load configuration from environment variables.

        Environment variables:
            DRUPAL_BASE_URL: Base URL of Drupal site
            DRUPAL_USERNAME: Username for authentication
            DRUPAL_PASSWORD: Password for authentication
            DRUPAL_EXPORT_ENABLED: Whether export is enabled (default: true)

        Returns:
            DrupalConfig instance

        Raises:
            ValueError: If required variables are missing
        """
        base_url = os.getenv('DRUPAL_BASE_URL')
        username = os.getenv('DRUPAL_USERNAME')
        password = os.getenv('DRUPAL_PASSWORD')
        enabled = os.getenv('DRUPAL_EXPORT_ENABLED', 'true').lower() == 'true'

        if not all([base_url, username, password]):
            raise ValueError(
                "Missing required Drupal configuration. "
                "Set DRUPAL_BASE_URL, DRUPAL_USERNAME, and DRUPAL_PASSWORD"
            )

        return cls(
            base_url=base_url,
            username=username,
            password=password,
            enabled=enabled
        )

    @classmethod
    def from_config_file(cls, config_path: Optional[str] = None) -> 'DrupalConfig':
        """
        Load configuration from a config file.

        Args:
            config_path: Path to config file. If None, uses default location.

        Returns:
            DrupalConfig instance

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If required settings are missing
        """
        if config_path is None:
            # Default to config/drupal.conf in project root
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'config',
                'drupal.conf'
            )

        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Drupal config file not found: {config_path}")

        # Simple key=value parser
        config = {}
        with open(config_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue

                if '=' in line:
                    key, value = line.split('=', 1)
                    config[key.strip()] = value.strip()

        base_url = config.get('base_url')
        username = config.get('username')
        password = config.get('password')
        enabled = config.get('enabled', 'true').lower() == 'true'

        if not all([base_url, username, password]):
            raise ValueError(
                f"Missing required Drupal configuration in {config_path}. "
                "Need: base_url, username, password"
            )

        logger.info(f"Loaded Drupal config from {config_path}")

        return cls(
            base_url=base_url,
            username=username,
            password=password,
            enabled=enabled
        )

    @classmethod
    def default(cls) -> 'DrupalConfig':
        """
        Get default configuration (for development/testing).

        Returns:
            DrupalConfig with default values

        Note:
            This uses the values from the documentation for testing.
            In production, use from_env() or from_config_file() instead.
        """
        return cls(
            base_url='https://audits.frontier-cnib.ca',
            username='restuser',
            password='venez1a?',
            enabled=True
        )

    def validate(self) -> bool:
        """
        Validate the configuration.

        Returns:
            True if valid

        Raises:
            ValueError: If configuration is invalid
        """
        if not self.base_url:
            raise ValueError("base_url is required")

        if not self.base_url.startswith(('http://', 'https://')):
            raise ValueError("base_url must start with http:// or https://")

        if not self.username:
            raise ValueError("username is required")

        if not self.password:
            raise ValueError("password is required")

        return True


def get_drupal_config(config_path: Optional[str] = None) -> DrupalConfig:
    """
    Get Drupal configuration, trying multiple sources.

    Tries in order:
    1. Config file (if path provided)
    2. Environment variables
    3. Default config file location

    Args:
        config_path: Optional path to config file

    Returns:
        DrupalConfig instance

    Raises:
        ValueError: If configuration cannot be loaded
    """
    # Try config file if specified
    if config_path:
        try:
            config = DrupalConfig.from_config_file(config_path)
            config.validate()
            return config
        except Exception as e:
            logger.warning(f"Could not load config from {config_path}: {e}")

    # Try environment variables
    try:
        config = DrupalConfig.from_env()
        config.validate()
        logger.info("Loaded Drupal config from environment variables")
        return config
    except Exception as e:
        logger.debug(f"Could not load config from environment: {e}")

    # Try default config file location
    try:
        config = DrupalConfig.from_config_file()
        config.validate()
        return config
    except Exception as e:
        logger.debug(f"Could not load config from default location: {e}")

    # All methods failed
    raise ValueError(
        "Could not load Drupal configuration. "
        "Please set environment variables (DRUPAL_BASE_URL, DRUPAL_USERNAME, DRUPAL_PASSWORD) "
        "or create a config file at config/drupal.conf"
    )
