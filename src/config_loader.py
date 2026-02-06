"""
Configuration Loader Module

Loads and validates configuration from YAML files and environment variables.
Provides a centralized config object for the entire application.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any


def load_config(config_path: str = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file and environment variables.

    Args:
        config_path: Path to config YAML file. If None, uses default location.

    Returns:
        Dictionary containing all configuration settings

    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If config file is invalid
    """

    # Determine config file path
    if config_path is None:
        project_root = Path(__file__).parent.parent
        config_path = project_root / "config" / "config.yaml"
    else:
        config_path = Path(config_path)

    if not config_path.exists():
        raise FileNotFoundError(
            f"Configuration file not found: {config_path}\n"
            "Please copy config.example.yaml to config.yaml and fill in your settings."
        )

    # Load YAML configuration
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # Override with environment variables if present
    if 'OPENAI_API_KEY' in os.environ:
        config['api_keys']['openai_api_key'] = os.environ['OPENAI_API_KEY']

    if 'PEXELS_API_KEY' in os.environ:
        config['api_keys']['pexels_api_key'] = os.environ['PEXELS_API_KEY']

    if 'ELEVENLABS_API_KEY' in os.environ:
        config['api_keys']['elevenlabs_api_key'] = os.environ['ELEVENLABS_API_KEY']

    # Validate required settings
    _validate_config(config)

    # Convert relative paths to absolute
    _resolve_paths(config)

    return config


def _validate_config(config: Dict[str, Any]) -> None:
    """
    Validate that required configuration values are present.

    Args:
        config: Configuration dictionary to validate

    Raises:
        ValueError: If required configuration is missing
    """

    required_keys = [
        ('api_keys', 'openai_api_key'),
        ('paths', 'ffmpeg_path'),
    ]

    for section, key in required_keys:
        if section not in config or key not in config[section]:
            raise ValueError(f"Missing required configuration: {section}.{key}")

        value = config[section][key]
        if not value or value.startswith("YOUR_") or value.startswith("your_"):
            raise ValueError(
                f"Configuration {section}.{key} not set. "
                "Please update config/config.yaml with your actual values."
            )


def _resolve_paths(config: Dict[str, Any]) -> None:
    """
    Convert relative paths in config to absolute paths.

    Args:
        config: Configuration dictionary (modified in place)
    """

    project_root = Path(__file__).parent.parent

    # Paths that need to be resolved
    path_keys = ['output_dir', 'thumbnail_dir', 'assets_dir', 'prompts_dir', 'logs_dir']

    for key in path_keys:
        if key in config['paths']:
            path = Path(config['paths'][key])
            if not path.is_absolute():
                config['paths'][key] = str(project_root / path)
