"""Utilities to work with pygls

Helper functions that simplify working with pygls
"""


import functools
from typing import Callable, NamedTuple, Tuple
from uuid import uuid4

from pygls.types import Position
from pygls.workspace import Document

_SENTINEL = object()


class FeatureConfig(NamedTuple):
    """Configuration for a feature"""

    arg: str
    path: str
    default: object


class Feature(NamedTuple):
    """Organize information about LanguageServer features"""

    lsp_method: str
    function: Callable
    config: Tuple[FeatureConfig, ...] = tuple()


def rgetattr(obj: object, attr: str, default: object = None) -> object:
    """Get nested attributes, recursively"""
    result = _rgetattr(obj, attr)
    return default if result is _SENTINEL else result


def _rgetattr(obj: object, attr: str) -> object:
    """Get nested attributes, recursively"""

    def _getattr(obj, attr):
        return getattr(obj, attr, _SENTINEL)

    return functools.reduce(_getattr, [obj] + attr.split("."))  # type: ignore


def clean_completion_name(name: str, char: str) -> str:
    """Clean the completion name, stripping bad surroundings

    1. Remove all surrounding " and '. For
    """
    if char == "'":
        return name.lstrip("'")
    if char == '"':
        return name.lstrip('"')
    return name


def char_before_cursor(
    document: Document, position: Position, default=""
) -> str:
    """Get the character directly before the cursor"""
    try:
        return document.lines[position.line][position.character - 1]
    except IndexError:
        return default


def uuid() -> str:
    """Function to create a string uuid"""
    return str(uuid4())
