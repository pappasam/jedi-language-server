"""Provides LSP client side utilities for easier testing"""
import platform


def normalizecase(path: str) -> str:
    """Fixes uri or path case for easier testing in windows"""
    if platform.system() == "Windows":
        return path.lower()
    return path
