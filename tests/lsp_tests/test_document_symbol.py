"""Tests for document symbols requests."""

import copy

from hamcrest import assert_that, is_

from tests import TEST_DATA
from tests.lsp_test_client import session
from tests.lsp_test_client.defaults import VSCODE_DEFAULT_INITIALIZE
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
                        "children": [],
                    },
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


def test_document_symbol_notebook() -> None:
    """Test document symbol request for notebooks.

    Test Data: tests/test_data/symbol/symbol_test1.ipynb
    """
    with session.LspSession() as ls_session:
        ls_session.initialize()
        path = SYMBOL_TEST_ROOT / "symbol_test1.ipynb"
        cell_uris = ls_session.open_notebook_document(path)

        actual = ls_session.text_document_symbol(
            {"textDocument": {"uri": cell_uris[0]}}
        )

        expected = [
            {
                "name": "Any",
                "kind": 5,
                "range": {
                    "start": {"line": 0, "character": 0},
                    "end": {"line": 0, "character": 22},
                },
                "selectionRange": {
                    "start": {"line": 0, "character": 19},
                    "end": {"line": 0, "character": 22},
                },
                "detail": "class Any",
                "children": [],
            },
            {
                "name": "somemodule",
                "kind": 2,
                "range": {
                    "start": {"line": 2, "character": 0},
                    "end": {"line": 2, "character": 37},
                },
                "selectionRange": {
                    "start": {"line": 2, "character": 14},
                    "end": {"line": 2, "character": 24},
                },
                "detail": "module somemodule",
                "children": [],
            },
            {
                "name": "somemodule2",
                "kind": 2,
                "range": {
                    "start": {"line": 2, "character": 0},
                    "end": {"line": 2, "character": 37},
                },
                "selectionRange": {
                    "start": {"line": 2, "character": 26},
                    "end": {"line": 2, "character": 37},
                },
                "detail": "module somemodule2",
                "children": [],
            },
        ]

        assert_that(actual, is_(expected))

        actual = ls_session.text_document_symbol(
            {"textDocument": {"uri": cell_uris[1]}}
        )

        expected = [
            {
                "name": "SOME_CONSTANT",
                "kind": 13,
                "range": {
                    "start": {"line": 0, "character": 0},
                    "end": {"line": 0, "character": 17},
                },
                "selectionRange": {
                    "start": {"line": 0, "character": 0},
                    "end": {"line": 0, "character": 13},
                },
                "detail": "SOME_CONSTANT = 1",
                "children": [],
            },
        ]

        assert_that(actual, is_(expected))

        actual = ls_session.text_document_symbol(
            {"textDocument": {"uri": cell_uris[2]}}
        )

        expected = [
            {
                "name": "do_work",
                "kind": 12,
                "range": {
                    "start": {"line": 0, "character": 0},
                    "end": {"line": 3, "character": 35},
                },
                "selectionRange": {
                    "start": {"line": 0, "character": 4},
                    "end": {"line": 0, "character": 11},
                },
                "detail": "def do_work",
                "children": [],
            },
        ]

        assert_that(actual, is_(expected))

        actual = ls_session.text_document_symbol(
            {"textDocument": {"uri": cell_uris[3]}}
        )

        expected = [
            {
                "name": "SomeClass",
                "kind": 5,
                "range": {
                    "start": {"line": 0, "character": 0},
                    "end": {"line": 10, "character": 38},
                },
                "selectionRange": {
                    "start": {"line": 0, "character": 6},
                    "end": {"line": 0, "character": 15},
                },
                "detail": "class SomeClass",
                "children": [
                    {
                        "name": "__init__",
                        "kind": 6,
                        "range": {
                            "start": {"line": 3, "character": 4},
                            "end": {"line": 4, "character": 28},
                        },
                        "selectionRange": {
                            "start": {"line": 3, "character": 8},
                            "end": {"line": 3, "character": 16},
                        },
                        "detail": "def __init__",
                        "children": [],
                    },
                    {
                        "name": "somedata",
                        "kind": 7,
                        "range": {
                            "start": {"line": 4, "character": 8},
                            "end": {"line": 4, "character": 28},
                        },
                        "selectionRange": {
                            "start": {"line": 4, "character": 13},
                            "end": {"line": 4, "character": 21},
                        },
                        "detail": "self.somedata = arg1",
                        "children": [],
                    },
                    {
                        "name": "do_something",
                        "kind": 6,
                        "range": {
                            "start": {"line": 6, "character": 4},
                            "end": {"line": 7, "character": 38},
                        },
                        "selectionRange": {
                            "start": {"line": 6, "character": 8},
                            "end": {"line": 6, "character": 20},
                        },
                        "detail": "def do_something",
                        "children": [],
                    },
                    {
                        "name": "so_something_else",
                        "kind": 6,
                        "range": {
                            "start": {"line": 9, "character": 4},
                            "end": {"line": 10, "character": 38},
                        },
                        "selectionRange": {
                            "start": {"line": 9, "character": 8},
                            "end": {"line": 9, "character": 25},
                        },
                        "detail": "def so_something_else",
                        "children": [],
                    },
                ],
            },
        ]

        assert_that(actual, is_(expected))


def test_document_symbol_no_hierarchy() -> None:
    """Test document symbol request with hierarchy turned off.

    Test Data: tests/test_data/symbol/symbol_test1.py
    """
    initialize_params = copy.deepcopy(VSCODE_DEFAULT_INITIALIZE)
    initialize_params["capabilities"]["textDocument"]["documentSymbol"][
        "hierarchicalDocumentSymbolSupport"
    ] = False
    with session.LspSession() as ls_session:
        ls_session.initialize(initialize_params)
        uri = as_uri(SYMBOL_TEST_ROOT / "symbol_test1.py")
        actual = ls_session.text_document_symbol(
            {"textDocument": {"uri": uri}}
        )

        expected = [
            {
                "name": "Any",
                "kind": 5,
                "location": {
                    "uri": uri,
                    "range": {
                        "start": {"line": 2, "character": 19},
                        "end": {"line": 2, "character": 22},
                    },
                },
                "containerName": "typing.Any",
            },
            {
                "name": "somemodule",
                "kind": 2,
                "location": {
                    "uri": uri,
                    "range": {
                        "start": {"line": 4, "character": 14},
                        "end": {"line": 4, "character": 24},
                    },
                },
                "containerName": "somemodule",
            },
            {
                "name": "somemodule2",
                "kind": 2,
                "location": {
                    "uri": uri,
                    "range": {
                        "start": {"line": 4, "character": 26},
                        "end": {"line": 4, "character": 37},
                    },
                },
                "containerName": "somemodule2",
            },
            {
                "name": "SOME_CONSTANT",
                "kind": 13,
                "location": {
                    "uri": uri,
                    "range": {
                        "start": {"line": 6, "character": 0},
                        "end": {"line": 6, "character": 13},
                    },
                },
                "containerName": "tests.test_data.symbol.symbol_test1.SOME_CONSTANT",
            },
            {
                "name": "do_work",
                "kind": 12,
                "location": {
                    "uri": uri,
                    "range": {
                        "start": {"line": 9, "character": 4},
                        "end": {"line": 9, "character": 11},
                    },
                },
                "containerName": "tests.test_data.symbol.symbol_test1.do_work",
            },
            {
                "name": "SomeClass",
                "kind": 5,
                "location": {
                    "uri": uri,
                    "range": {
                        "start": {"line": 15, "character": 6},
                        "end": {"line": 15, "character": 15},
                    },
                },
                "containerName": "tests.test_data.symbol.symbol_test1.SomeClass",
            },
            {
                "name": "__init__",
                "kind": 12,
                "location": {
                    "uri": uri,
                    "range": {
                        "start": {"line": 18, "character": 8},
                        "end": {"line": 18, "character": 16},
                    },
                },
                "containerName": "tests.test_data.symbol.symbol_test1.SomeClass.__init__",
            },
            {
                "name": "somedata",
                "kind": 13,
                "location": {
                    "uri": uri,
                    "range": {
                        "start": {"line": 19, "character": 13},
                        "end": {"line": 19, "character": 21},
                    },
                },
                "containerName": "tests.test_data.symbol.symbol_test1.SomeClass.__init__.somedata",
            },
            {
                "name": "do_something",
                "kind": 12,
                "location": {
                    "uri": uri,
                    "range": {
                        "start": {"line": 21, "character": 8},
                        "end": {"line": 21, "character": 20},
                    },
                },
                "containerName": "tests.test_data.symbol.symbol_test1.SomeClass.do_something",
            },
            {
                "name": "so_something_else",
                "kind": 12,
                "location": {
                    "uri": uri,
                    "range": {
                        "start": {"line": 24, "character": 8},
                        "end": {"line": 24, "character": 25},
                    },
                },
                "containerName": "tests.test_data.symbol.symbol_test1.SomeClass.so_something_else",
            },
        ]
        assert_that(actual, is_(expected))


def test_document_symbol_no_hierarchy_notebook() -> None:
    """Test document symbol request with hierarchy turned off for notebooks.

    Test Data: tests/test_data/symbol/symbol_test1.ipynb
    """
    initialize_params = copy.deepcopy(VSCODE_DEFAULT_INITIALIZE)
    initialize_params["capabilities"]["textDocument"]["documentSymbol"][
        "hierarchicalDocumentSymbolSupport"
    ] = False
    with session.LspSession() as ls_session:
        ls_session.initialize(initialize_params)
        path = SYMBOL_TEST_ROOT / "symbol_test1.ipynb"
        cell_uris = ls_session.open_notebook_document(path)

        actual = ls_session.text_document_symbol(
            {"textDocument": {"uri": cell_uris[0]}}
        )

        expected = [
            {
                "name": "Any",
                "kind": 5,
                "location": {
                    "uri": cell_uris[0],
                    "range": {
                        "start": {"line": 0, "character": 19},
                        "end": {"line": 0, "character": 22},
                    },
                },
                "containerName": "typing.Any",
            },
            {
                "name": "somemodule",
                "kind": 2,
                "location": {
                    "uri": cell_uris[0],
                    "range": {
                        "start": {"line": 2, "character": 14},
                        "end": {"line": 2, "character": 24},
                    },
                },
                "containerName": "somemodule",
            },
            {
                "name": "somemodule2",
                "kind": 2,
                "location": {
                    "uri": cell_uris[0],
                    "range": {
                        "start": {"line": 2, "character": 26},
                        "end": {"line": 2, "character": 37},
                    },
                },
                "containerName": "somemodule2",
            },
        ]

        assert_that(actual, is_(expected))

        actual = ls_session.text_document_symbol(
            {"textDocument": {"uri": cell_uris[1]}}
        )

        expected = [
            {
                "name": "SOME_CONSTANT",
                "kind": 13,
                "location": {
                    "uri": cell_uris[1],
                    "range": {
                        "start": {"line": 0, "character": 0},
                        "end": {"line": 0, "character": 13},
                    },
                },
                "containerName": "tests.test_data.symbol.symbol_test1.ipynb.SOME_CONSTANT",
            },
        ]

        assert_that(actual, is_(expected))

        actual = ls_session.text_document_symbol(
            {"textDocument": {"uri": cell_uris[2]}}
        )

        expected = [
            {
                "name": "do_work",
                "kind": 12,
                "location": {
                    "uri": cell_uris[2],
                    "range": {
                        "start": {"line": 0, "character": 4},
                        "end": {"line": 0, "character": 11},
                    },
                },
                "containerName": "tests.test_data.symbol.symbol_test1.ipynb.do_work",
            },
        ]

        assert_that(actual, is_(expected))

        actual = ls_session.text_document_symbol(
            {"textDocument": {"uri": cell_uris[3]}}
        )

        expected = [
            {
                "name": "SomeClass",
                "kind": 5,
                "location": {
                    "uri": cell_uris[3],
                    "range": {
                        "start": {"line": 0, "character": 6},
                        "end": {"line": 0, "character": 15},
                    },
                },
                "containerName": "tests.test_data.symbol.symbol_test1.ipynb.SomeClass",
            },
            {
                "name": "__init__",
                "kind": 12,
                "location": {
                    "uri": cell_uris[3],
                    "range": {
                        "start": {"line": 3, "character": 8},
                        "end": {"line": 3, "character": 16},
                    },
                },
                "containerName": "tests.test_data.symbol.symbol_test1.ipynb.SomeClass.__init__",
            },
            {
                "name": "somedata",
                "kind": 13,
                "location": {
                    "uri": cell_uris[3],
                    "range": {
                        "start": {"line": 4, "character": 13},
                        "end": {"line": 4, "character": 21},
                    },
                },
                "containerName": "tests.test_data.symbol.symbol_test1.ipynb.SomeClass.__init__.somedata",
            },
            {
                "name": "do_something",
                "kind": 12,
                "location": {
                    "uri": cell_uris[3],
                    "range": {
                        "start": {"line": 6, "character": 8},
                        "end": {"line": 6, "character": 20},
                    },
                },
                "containerName": "tests.test_data.symbol.symbol_test1.ipynb.SomeClass.do_something",
            },
            {
                "name": "so_something_else",
                "kind": 12,
                "location": {
                    "uri": cell_uris[3],
                    "range": {
                        "start": {"line": 9, "character": 8},
                        "end": {"line": 9, "character": 25},
                    },
                },
                "containerName": "tests.test_data.symbol.symbol_test1.ipynb.SomeClass.so_something_else",
            },
        ]
        assert_that(actual, is_(expected))
