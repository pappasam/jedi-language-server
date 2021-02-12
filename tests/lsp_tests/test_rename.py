"""Tests for refactoring"""

import pathlib
from hamcrest import assert_that, is_
from tests.lsp_test_client.utils import normalizecase
from tests import TEST_DATA
from tests.lsp_test_client import session


REFACTOR_TEST_ROOT = pathlib.Path(TEST_DATA) / "refactoring"


def test_lsp_rename_function():
    """Tests single file function rename"""
    with session.LspSession() as ls_session:
        uri = normalizecase((REFACTOR_TEST_ROOT / "rename_test1.py").as_uri())
        actual = ls_session.text_document_rename(
            {
                "textDocument": {"uri": uri},
                "position": {"line": 12, "character": 4},
                "newName": "my_function_1",
            }
        )

        expected = {
            "changes": None,
            "documentChanges": [
                {
                    "textDocument": {
                        "uri": uri,
                        "version": 0,
                    },
                    "edits": [
                        {
                            "range": {
                                "start": {"line": 3, "character": 6},
                                "end": {"line": 3, "character": 6},
                            },
                            "newText": "_",
                        },
                        {
                            "range": {
                                "start": {"line": 3, "character": 10},
                                "end": {"line": 3, "character": 10},
                            },
                            "newText": "tion_",
                        },
                        {
                            "range": {
                                "start": {"line": 8, "character": 6},
                                "end": {"line": 8, "character": 6},
                            },
                            "newText": "_",
                        },
                        {
                            "range": {
                                "start": {"line": 8, "character": 10},
                                "end": {"line": 8, "character": 10},
                            },
                            "newText": "tion_",
                        },
                        {
                            "range": {
                                "start": {"line": 12, "character": 2},
                                "end": {"line": 12, "character": 2},
                            },
                            "newText": "_",
                        },
                        {
                            "range": {
                                "start": {"line": 12, "character": 6},
                                "end": {"line": 12, "character": 6},
                            },
                            "newText": "tion_",
                        },
                    ],
                }
            ],
        }
        assert_that(actual, is_(expected))
