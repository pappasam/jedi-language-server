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
        ({"line": 2, "character": 3}, None),
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
    initialize_params["rootPath"]: str(REFERENCES_TEST_ROOT)
    initialize_params["rootUri"]: as_uri(REFERENCES_TEST_ROOT)

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
