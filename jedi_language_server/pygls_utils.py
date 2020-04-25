"""Utilities to work with pygls

Helper functions that simplify working with pygls
"""


import functools

_SENTINEL = object()


def rgetattr(obj: object, attr: str, default: object = None) -> object:
    """Get nested attributes, recursively"""
    result = _rgetattr(obj, attr)
    return default if result is _SENTINEL else result


def _rgetattr(obj: object, attr: str):
    """Get nested attributes, recursively"""

    def _getattr(obj, attr):
        return getattr(obj, attr, _SENTINEL)

    return functools.reduce(_getattr, [obj] + attr.split("."))
