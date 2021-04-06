"""Test file for references."""

from enum import Enum

SOME_CONSTANT = "something"


def some_function(arg: str) -> str:
    """Test function for references."""
    return arg


class SomeClass(Enum):
    """Test class for references."""

    def __init__(self):
        self._field = 1

    def some_method1(self):
        """Test method for references."""
        return SOME_CONSTANT + self._field

    def some_method2(self):
        """Test method for references."""
        return some_function(SOME_CONSTANT)


instance = SomeClass()
instance.some_method1()
instance.some_method2()
