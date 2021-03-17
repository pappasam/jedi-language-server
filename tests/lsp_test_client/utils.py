"""Provides LSP client side utilities for easier testing."""
import pathlib
import platform
import re

import py


def normalizecase(path: str) -> str:
    """Fixes 'file' uri or path case for easier testing in windows."""
    if platform.system() == "Windows":
        return path.lower()
    return path


def as_uri(path: py.path.local) -> str:
    """Return 'file' uri as string."""
    return normalizecase(pathlib.Path(path).as_uri())


class StringPattern:
    """Matches string patterns."""

    def __init__(self, pattern):
        self.pattern = pattern

    def __eq__(self, o):
        """Compares against pattern when possible."""
        if isinstance(o, str):
            match = re.match(self.pattern, o)
            return match is not None

        if isinstance(o, StringPattern):
            return self.pattern == o.pattern

        return False

    def match(self, test_str):
        """Returns matches if pattern matches are found in the test string."""
        return re.match(self.pattern, test_str)
