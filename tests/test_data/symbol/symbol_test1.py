"""Test file for symbol tests."""

from typing import Any

from . import somemodule, somemodule2

SOME_CONSTANT = 1


def do_work():
    """Function for symbols test."""
    somemodule.do_something()
    somemodule2.do_something_else()


class SomeClass:
    """Class for symbols test."""

    def __init__(self, arg1: Any):
        self.somedata = arg1

    def do_something(self):
        """Method for symbols test."""

    def so_something_else(self):
        """Method for symbols test."""
