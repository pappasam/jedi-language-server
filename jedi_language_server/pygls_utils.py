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
    """Configuration item for a feature with associated defaults

    :attr arg: the name of the option within the feature
    :attr path: the lookup path, rooted at `jedi`, to the user configuration.
        The last item in the path must be the option associated with a feature
    :attr default: the value used if no value is found in the path

    Example:

        settings.json:

        {
          "jedi.completion.triggerCharacters": [".", "'", "\""]
        }

        python code associated with this configuration:

        FeatureConfig("completion.triggerCharacters", [".", "'", '"'])

    NOTE: all paths are rooted at "jedi". Do not specify the top-level jedi in
    the path.
    """

    path: str
    default: object


class Feature(NamedTuple):
    """Organize information about LanguageServer features

    :attr lsp_method: exact name of the feature's LSP method
    :attr function: python function to be associated with the method
    :attr config: collection of FeatureConfig supported by this feature
    """

    lsp_method: str
    function: Callable
    config: Tuple[FeatureConfig, ...] = tuple()


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
