"""
Helper utilities
"""
import sys
import importlib
from datetime import datetime
from typing import Any, Optional


def safe_import(module_name: str, fallback: Any = None) -> Any:
    """
    Safely import a module with fallback
    
    Args:
        module_name: Name of module to import
        fallback: Value to return if import fails
    
    Returns:
        Imported module or fallback
    """
    try:
        return importlib.import_module(module_name)
    except ImportError:
        return fallback


def format_number(value: float, decimals: int = 2) -> str:
    """Format a number with commas and decimals"""
    return f"{value:,.{decimals}f}"


def get_timestamp(format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Get current timestamp as string"""
    return datetime.now().strftime(format_str)


def get_file_size(file_path: str) -> str:
    """Get human-readable file size"""
    import os
    size = os.path.getsize(file_path)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"


def ensure_dir(path: str) -> bool:
    """Ensure directory exists"""
    import os
    os.makedirs(path, exist_ok=True)
    return os.path.exists(path)