"""Test file for highlighting."""

from enum import Enum

SOME_CONSTANT = "something"


def some_function(arg: str) -> str:
    """Test function for highlighting."""
    return arg


class SomeClass(Enum):
    """Test class for highlighting."""

    def __init__(self):
        self._field = 1

    def some_method1(self):
        """Test method for highlighting."""
        return SOME_CONSTANT + self._field

    def some_method2(self):
        """Test method for highlighting."""
        return some_function(SOME_CONSTANT)


instance = SomeClass()
instance.some_method1()
instance.some_method2()

# Jedi returns an implicit definition for these special variables,
# which has no line number.  Highlighting of usages with line numbers
# should still function.
print(__file__)
print(__package__)
print(__doc__)
print(__name__)
