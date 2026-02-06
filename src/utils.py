"""
Utility Functions Module

Common utility functions used across the application.
"""

import os
import json
from pathlib import Path
from typing import Any, Dict
from datetime import datetime


def ensure_directory(path: str) -> None:
    """
    Ensure a directory exists, create if it doesn't.

    Args:
        path: Directory path to ensure exists
    """
    Path(path).mkdir(parents=True, exist_ok=True)


def save_json(data: Dict[str, Any], filepath: str) -> None:
    """
    Save dictionary to JSON file.

    Args:
        data: Dictionary to save
        filepath: Path to output JSON file
    """
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_json(filepath: str) -> Dict[str, Any]:
    """
    Load JSON file into dictionary.

    Args:
        filepath: Path to JSON file

    Returns:
        Dictionary from JSON file
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_file_size_mb(filepath: str) -> float:
    """
    Get file size in megabytes.

    Args:
        filepath: Path to file

    Returns:
        File size in MB
    """
    size_bytes = os.path.getsize(filepath)
    return size_bytes / (1024 * 1024)


def format_duration(seconds: int) -> str:
    """
    Format duration in seconds to readable string.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted duration (e.g., "3m 25s")
    """
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    return f"{minutes}m {remaining_seconds}s"


def timestamp_filename(prefix: str = "", extension: str = "") -> str:
    """
    Generate filename with timestamp.

    Args:
        prefix: Filename prefix
        extension: File extension (with or without dot)

    Returns:
        Filename with timestamp
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if extension and not extension.startswith('.'):
        extension = f".{extension}"

    return f"{prefix}_{timestamp}{extension}" if prefix else f"{timestamp}{extension}"


def clean_filename(text: str, max_length: int = 50) -> str:
    """
    Clean text to be safe for use as filename.

    Args:
        text: Text to clean
        max_length: Maximum length for filename

    Returns:
        Cleaned filename-safe text
    """
    # Remove or replace unsafe characters
    unsafe_chars = '<>:"/\\|?*'

    for char in unsafe_chars:
        text = text.replace(char, '_')

    # Remove leading/trailing spaces and dots
    text = text.strip('. ')

    # Limit length
    if len(text) > max_length:
        text = text[:max_length]

    return text
