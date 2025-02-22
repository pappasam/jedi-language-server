"""Tests for references requests."""

import copy

import pytest
from hamcrest import assert_that, is_

from tests import TEST_DATA
from tests.lsp_test_client import session
from tests.lsp_test_client.defaults import VSCODE_DEFAULT_INITIALIZE
from tests.lsp_test_client.utils import as_uri

REFERENCES_TEST_ROOT = TEST_DATA / "references"


references1 = as_uri(REFERENCES_TEST_ROOT / "references_test1.py")


@pytest.mark.parametrize(
    ["position", "expected"],
    [
        # from
        ({"line": 2, "character": 3}, None),
        # SOME_CONSTANT
        (
            {"line": 4, "character": 8},
            [
                {
                    "uri": references1,
                    "range": {
                        "start": {"line": 4, "character": 0},
                        "end": {"line": 4, "character": 13},
                    },
                },
                {
                    "uri": references1,
                    "range": {
                        "start": {"line": 20, "character": 15},
                        "end": {"line": 20, "character": 28},
                    },
                },
                {
                    "uri": references1,
                    "range": {
                        "start": {"line": 24, "character": 29},
                        "end": {"line": 24, "character": 42},
                    },
                },
            ],
        ),
        # some_function
        (
            {"line": 7, "character": 9},
            [
                {
                    "uri": references1,
                    "range": {
                        "start": {"line": 7, "character": 4},
                        "end": {"line": 7, "character": 17},
                    },
                },
                {
                    "uri": references1,
                    "range": {
                        "start": {"line": 24, "character": 15},
                        "end": {"line": 24, "character": 28},
                    },
                },
            ],
        ),
        # arg of some_function
        (
            {"line": 7, "character": 20},
            [
                {
                    "uri": references1,
                    "range": {
                        "start": {"line": 7, "character": 18},
                        "end": {"line": 7, "character": 21},
                    },
                },
                {
                    "uri": references1,
                    "range": {
                        "start": {"line": 9, "character": 11},
                        "end": {"line": 9, "character": 14},
                    },
                },
            ],
        ),
        # SomeClass
        (
            {"line": 12, "character": 14},
            [
                {
                    "uri": references1,
                    "range": {
                        "start": {"line": 12, "character": 6},
                        "end": {"line": 12, "character": 15},
                    },
                },
                {
                    "uri": references1,
                    "range": {
                        "start": {"line": 27, "character": 11},
                        "end": {"line": 27, "character": 20},
                    },
                },
            ],
        ),
        # self arg of SomeClass.__init__
        (
            {"line": 15, "character": 20},
            [
                {
                    "uri": references1,
                    "range": {
                        "start": {"line": 15, "character": 17},
                        "end": {"line": 15, "character": 21},
                    },
                },
                {
                    "uri": references1,
                    "range": {
                        "start": {"line": 16, "character": 8},
                        "end": {"line": 16, "character": 12},
                    },
                },
            ],
        ),
        # SomeClass._field
        (
            {"line": 16, "character": 17},
            [
                {
                    "uri": references1,
                    "range": {
                        "start": {"line": 16, "character": 13},
                        "end": {"line": 16, "character": 19},
                    },
                },
                {
                    "uri": references1,
                    "range": {
                        "start": {"line": 20, "character": 36},
                        "end": {"line": 20, "character": 42},
                    },
                },
            ],
        ),
        # SomeClass.some_method1
        (
            {"line": 18, "character": 15},
            [
                {
                    "uri": references1,
                    "range": {
                        "start": {"line": 18, "character": 8},
                        "end": {"line": 18, "character": 20},
                    },
                },
                {
                    "uri": references1,
                    "range": {
                        "start": {"line": 28, "character": 9},
                        "end": {"line": 28, "character": 21},
                    },
                },
            ],
        ),
    ],
)
def test_references(position, expected):
    """Tests references on import statement.

    Test Data: tests/test_data/references/references_test1.py
    """
    initialize_params = copy.deepcopy(VSCODE_DEFAULT_INITIALIZE)
    initialize_params["workspaceFolders"] = [
        {"uri": as_uri(REFERENCES_TEST_ROOT), "name": "jedi_lsp"}
    ]
    initialize_params["rootPath"] = str(REFERENCES_TEST_ROOT)
    initialize_params["rootUri"] = as_uri(REFERENCES_TEST_ROOT)

    with session.LspSession() as ls_session:
        ls_session.initialize(initialize_params)
        uri = references1
        actual = ls_session.text_document_references(
            {
                "textDocument": {"uri": uri},
                "position": position,
                "context": {
                    "includeDeclaration": True,
                },
            }
        )

        assert_that(actual, is_(expected))


@pytest.mark.parametrize(
    ["cell", "position", "expected"],
    [
        # from
        (0, {"line": 0, "character": 3}, None),
        # SOME_CONSTANT
        (
            1,
            {"line": 0, "character": 8},
            [
                {
                    "cell": 1,
                    "range": {
                        "start": {"line": 0, "character": 0},
                        "end": {"line": 0, "character": 13},
                    },
                },
                {
                    "cell": 3,
                    "range": {
                        "start": {"line": 8, "character": 15},
                        "end": {"line": 8, "character": 28},
                    },
                },
                {
                    "cell": 3,
                    "range": {
                        "start": {"line": 12, "character": 29},
                        "end": {"line": 12, "character": 42},
                    },
                },
            ],
        ),
        # some_function
        (
            2,
            {"line": 0, "character": 9},
            [
                {
                    "cell": 2,
                    "range": {
                        "start": {"line": 0, "character": 4},
                        "end": {"line": 0, "character": 17},
                    },
                },
                {
                    "cell": 3,
                    "range": {
                        "start": {"line": 12, "character": 15},
                        "end": {"line": 12, "character": 28},
                    },
                },
            ],
        ),
        # arg of some_function
        (
            2,
            {"line": 0, "character": 20},
            [
                {
                    "cell": 2,
                    "range": {
                        "start": {"line": 0, "character": 18},
                        "end": {"line": 0, "character": 21},
                    },
                },
                {
                    "cell": 2,
                    "range": {
                        "start": {"line": 2, "character": 11},
                        "end": {"line": 2, "character": 14},
                    },
                },
            ],
        ),
        # SomeClass
        (
            3,
            {"line": 0, "character": 14},
            [
                {
                    "cell": 3,
                    "range": {
                        "start": {"line": 0, "character": 6},
                        "end": {"line": 0, "character": 15},
                    },
                },
                {
                    "cell": 4,
                    "range": {
                        "start": {"line": 0, "character": 11},
                        "end": {"line": 0, "character": 20},
                    },
                },
            ],
        ),
        # self arg of SomeClass.__init__
        (
            3,
            {"line": 3, "character": 20},
            [
                {
                    "cell": 3,
                    "range": {
                        "start": {"line": 3, "character": 17},
                        "end": {"line": 3, "character": 21},
                    },
                },
                {
                    "cell": 3,
                    "range": {
                        "start": {"line": 4, "character": 8},
                        "end": {"line": 4, "character": 12},
                    },
                },
            ],
        ),
        # SomeClass._field
        (
            3,
            {"line": 4, "character": 17},
            [
                {
                    "cell": 3,
                    "range": {
                        "start": {"line": 4, "character": 13},
                        "end": {"line": 4, "character": 19},
                    },
                },
                {
                    "cell": 3,
                    "range": {
                        "start": {"line": 8, "character": 36},
                        "end": {"line": 8, "character": 42},
                    },
                },
            ],
        ),
        # SomeClass.some_method1
        (
            3,
            {"line": 6, "character": 15},
            [
                {
                    "cell": 3,
                    "range": {
                        "start": {"line": 6, "character": 8},
                        "end": {"line": 6, "character": 20},
                    },
                },
                {
                    "cell": 4,
                    "range": {
                        "start": {"line": 1, "character": 9},
                        "end": {"line": 1, "character": 21},
                    },
                },
            ],
        ),
    ],
)
def test_references_notebook(cell, position, expected):
    """Tests references in a notebook.

    Test Data: tests/test_data/references/references_test1.ipynb
    """
    with session.LspSession() as ls_session:
        ls_session.initialize()
        path = REFERENCES_TEST_ROOT / "references_test1.ipynb"
        cell_uris = ls_session.open_notebook_document(path)
        actual = ls_session.text_document_references(
            {
                "textDocument": {"uri": cell_uris[cell]},
                "position": position,
                "context": {
                    "includeDeclaration": True,
                },
            }
        )

        if expected:
            for item in expected:
                item["uri"] = cell_uris[item.pop("cell")]
        assert_that(actual, is_(expected))
