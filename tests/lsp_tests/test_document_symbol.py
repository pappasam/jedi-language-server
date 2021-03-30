"""Tests for document symbols requests."""

from hamcrest import assert_that, is_

from tests import TEST_DATA
from tests.lsp_test_client import session
from tests.lsp_test_client.utils import as_uri

SYMBOL_TEST_ROOT = TEST_DATA / "symbol"


def test_document_symbol() -> None:
    """Test document symbol request.

    Test Data: tests/test_data/symbol/symbol_test1.py
    """

    with session.LspSession() as ls_session:
        ls_session.initialize()
        uri = as_uri(SYMBOL_TEST_ROOT / "symbol_test1.py")
        actual = ls_session.text_document_symbol(
            {"textDocument": {"uri": uri}}
        )

        expected = [
            {
                "name": "Any",
                "kind": 5,
                "range": {
                    "start": {"line": 2, "character": 0},
                    "end": {"line": 2, "character": 22},
                },
                "selectionRange": {
                    "start": {"line": 2, "character": 19},
                    "end": {"line": 2, "character": 22},
                },
                "detail": "class Any",
                "children": [],
            },
            {
                "name": "somemodule",
                "kind": 2,
                "range": {
                    "start": {"line": 4, "character": 0},
                    "end": {"line": 4, "character": 37},
                },
                "selectionRange": {
                    "start": {"line": 4, "character": 14},
                    "end": {"line": 4, "character": 24},
                },
                "detail": "module somemodule",
                "children": [],
            },
            {
                "name": "somemodule2",
                "kind": 2,
                "range": {
                    "start": {"line": 4, "character": 0},
                    "end": {"line": 4, "character": 37},
                },
                "selectionRange": {
                    "start": {"line": 4, "character": 26},
                    "end": {"line": 4, "character": 37},
                },
                "detail": "module somemodule2",
                "children": [],
            },
            {
                "name": "SOME_CONSTANT",
                "kind": 13,
                "range": {
                    "start": {"line": 6, "character": 0},
                    "end": {"line": 6, "character": 17},
                },
                "selectionRange": {
                    "start": {"line": 6, "character": 0},
                    "end": {"line": 6, "character": 13},
                },
                "detail": "SOME_CONSTANT = 1",
                "children": [],
            },
            {
                "name": "do_work",
                "kind": 12,
                "range": {
                    "start": {"line": 9, "character": 0},
                    "end": {"line": 12, "character": 35},
                },
                "selectionRange": {
                    "start": {"line": 9, "character": 4},
                    "end": {"line": 9, "character": 11},
                },
                "detail": "def do_work",
                "children": [],
            },
            {
                "name": "SomeClass",
                "kind": 5,
                "range": {
                    "start": {"line": 15, "character": 0},
                    "end": {"line": 25, "character": 38},
                },
                "selectionRange": {
                    "start": {"line": 15, "character": 6},
                    "end": {"line": 15, "character": 15},
                },
                "detail": "class SomeClass",
                "children": [
                    {
                        "name": "__init__",
                        "kind": 6,
                        "range": {
                            "start": {"line": 18, "character": 4},
                            "end": {"line": 19, "character": 28},
                        },
                        "selectionRange": {
                            "start": {"line": 18, "character": 8},
                            "end": {"line": 18, "character": 16},
                        },
                        "detail": "def __init__",
                        "children": [
                            {
                                "name": "somedata",
                                "kind": 7,
                                "range": {
                                    "start": {"line": 19, "character": 8},
                                    "end": {"line": 19, "character": 28},
                                },
                                "selectionRange": {
                                    "start": {"line": 19, "character": 13},
                                    "end": {"line": 19, "character": 21},
                                },
                                "detail": "self.somedata = arg1",
                                "children": [],
                            }
                        ],
                    },
                    {
                        "name": "do_something",
                        "kind": 6,
                        "range": {
                            "start": {"line": 21, "character": 4},
                            "end": {"line": 22, "character": 38},
                        },
                        "selectionRange": {
                            "start": {"line": 21, "character": 8},
                            "end": {"line": 21, "character": 20},
                        },
                        "detail": "def do_something",
                        "children": [],
                    },
                    {
                        "name": "so_something_else",
                        "kind": 6,
                        "range": {
                            "start": {"line": 24, "character": 4},
                            "end": {"line": 25, "character": 38},
                        },
                        "selectionRange": {
                            "start": {"line": 24, "character": 8},
                            "end": {"line": 24, "character": 25},
                        },
                        "detail": "def so_something_else",
                        "children": [],
                    },
                ],
            },
        ]

    assert_that(actual, is_(expected))
