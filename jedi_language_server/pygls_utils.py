"""Utilities to work with pygls

Helper functions that simplify working with pygls
"""


import functools
from typing import Callable, NamedTuple
from uuid import uuid4

from pygls.types import Position
from pygls.workspace import Document

_SENTINEL = object()


class Feature(NamedTuple):
    """Organize information about LanguageServer features

    :attr lsp_method: exact name of the feature's LSP method
    :attr function: python function to be associated with the method
    """

    lsp_method: str
    function: Callable


def rgetattr(obj: object, attr: str, default: object = None) -> object:
    """Get nested attributes, recursively

    Usage:
        >> repr(my_object)
            Object(hello=Object(world=2))
        >> rgetattr(my_object, "hello.world")
            2
        >> rgetattr(my_object, "hello.world.space")
            None
        >> rgetattr(my_object, "hello.world.space", 20)
            20
    """
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
