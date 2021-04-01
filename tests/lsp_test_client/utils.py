"""Provides LSP client side utilities for easier testing."""

import os
import pathlib
import platform
import re
from random import choice

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


class PythonFile:
    """Create python file on demand for testing."""

    def __init__(self, contents, root):
        self.contents = contents
        self.basename = "".join(
            choice("abcdefghijklmnopqrstuvwxyz") if i < 8 else ".py"
            for i in range(9)
        )
        self.fullpath = py.path.local(root) / self.basename

    def __enter__(self):
        """Creates a python file for  testing."""
        with open(self.fullpath, "w") as py_file:
            py_file.write(self.contents)
        return self

    def __exit__(self, typ, value, _tb):
        """Cleans up and deletes the python file."""
        os.unlink(self.fullpath)
