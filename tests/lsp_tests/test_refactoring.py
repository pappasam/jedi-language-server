"""Tests for refactoring requests."""

from hamcrest import assert_that, is_

from tests import TEST_DATA
from tests.lsp_test_client import session
from tests.lsp_test_client.utils import StringPattern, as_uri

REFACTOR_TEST_ROOT = TEST_DATA / "refactoring"


def test_lsp_rename_function():
    """Tests single file function rename."""
    with session.LspSession() as ls_session:
        ls_session.initialize()
        uri = as_uri((REFACTOR_TEST_ROOT / "rename_test1.py"))
        actual = ls_session.text_document_rename(
            {
                "textDocument": {"uri": uri},
                "position": {"line": 12, "character": 4},
                "newName": "my_function_1",
            }
        )

        expected = {
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


def test_lsp_rename_variable_at_line_start():
    """Tests renaming a variable that appears at the start of a line."""
    with session.LspSession() as ls_session:
        ls_session.initialize()
        uri = as_uri((REFACTOR_TEST_ROOT / "rename_test2.py"))
        actual = ls_session.text_document_rename(
            {
                "textDocument": {"uri": uri},
                "position": {"line": 1, "character": 0},
                "newName": "y",
            }
        )

        expected = {
            "documentChanges": [
                {
                    "textDocument": {
                        "uri": uri,
                        "version": 0,
                    },
                    "edits": [
                        {
                            "range": {
                                "start": {"line": 1, "character": 0},
                                "end": {"line": 1, "character": 1},
                            },
                            "newText": "y",
                        },
                    ],
                }
            ],
        }
        assert_that(actual, is_(expected))


def test_lsp_rename_last_line():
    """Tests whether rename works for end of file edge case.

    This example was receiving a KeyError, but now we check for end-1 to
    fit within correct range.
    """
    with session.LspSession() as ls_session:
        ls_session.initialize()
        uri = as_uri((REFACTOR_TEST_ROOT / "rename_test3.py"))
        actual = ls_session.text_document_rename(
            {
                "textDocument": {"uri": uri},
                "position": {"line": 14, "character": 7},
                "newName": "args2",
            }
        )

        expected = {
            "documentChanges": [
                {
                    "textDocument": {
                        "uri": uri,
                        "version": 0,
                    },
                    "edits": [
                        {
                            "range": {
                                "start": {"line": 11, "character": 4},
                                "end": {"line": 11, "character": 4},
                            },
                            "newText": "2",
                        },
                        {
                            "range": {
                                "start": {"line": 12, "character": 7},
                                "end": {"line": 12, "character": 7},
                            },
                            "newText": "2",
                        },
                        {
                            "range": {
                                "start": {"line": 12, "character": 15},
                                "end": {"line": 12, "character": 15},
                            },
                            "newText": "2",
                        },
                        {
                            "range": {
                                "start": {"line": 14, "character": 10},
                                "end": {"line": 14, "character": 12},
                            },
                            "newText": "2)\n",
                        },
                    ],
                }
            ],
        }
        assert_that(actual, is_(expected))


def test_lsp_code_action() -> None:
    """Tests code actions like extract variable and extract function."""

    with session.LspSession() as ls_session:
        ls_session.initialize()
        uri = as_uri((REFACTOR_TEST_ROOT / "code_action_test1.py"))
        actual = ls_session.text_document_code_action(
            {
                "textDocument": {"uri": uri},
                "range": {
                    "start": {"line": 4, "character": 10},
                    "end": {"line": 4, "character": 10},
                },
                "context": {"diagnostics": []},
            }
        )

        expected = [
            {
                "title": StringPattern(
                    r"Extract expression into variable 'var_\w+'"
                ),
                "kind": "refactor.extract",
                "edit": {
                    "documentChanges": [
                        {
                            "textDocument": {
                                "uri": uri,
                                "version": 0,
                            },
                            "edits": [],
                        }
                    ]
                },
            },
            {
                "title": StringPattern(
                    r"Extract expression into function 'func_\w+'"
                ),
                "kind": "refactor.extract",
                "edit": {
                    "documentChanges": [
                        {
                            "textDocument": {
                                "uri": uri,
                                "version": 0,
                            },
                            "edits": [],
                        }
                    ]
                },
            },
        ]

        # Cannot use hamcrest directly for this due to unpredictable
        # variations in how the text edits are generated.

        assert_that(len(actual), is_(len(expected)))

        # Remove the edits
        actual[0]["edit"]["documentChanges"][0]["edits"] = []
        actual[1]["edit"]["documentChanges"][0]["edits"] = []

        assert_that(actual, is_(expected))
