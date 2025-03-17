"""Tests for refactoring requests."""

import sys

import pytest
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


def test_lsp_rename_function_notebook():
    """Tests single notebook function rename."""
    with session.LspSession() as ls_session:
        ls_session.initialize()
        path = REFACTOR_TEST_ROOT / "rename_test1.ipynb"
        cell_uris = ls_session.open_notebook_document(path)
        actual = ls_session.text_document_rename(
            {
                "textDocument": {"uri": cell_uris[2]},
                "position": {"line": 0, "character": 4},
                "newName": "my_function_1",
            }
        )

        expected = {
            "documentChanges": [
                {
                    "textDocument": {
                        "uri": cell_uris[0],
                        "version": 1,
                    },
                    "edits": [
                        {
                            "range": {
                                "start": {"line": 0, "character": 6},
                                "end": {"line": 0, "character": 6},
                            },
                            "newText": "_",
                        },
                        {
                            "range": {
                                "start": {"line": 0, "character": 10},
                                "end": {"line": 0, "character": 10},
                            },
                            "newText": "tion_",
                        },
                    ],
                },
                {
                    "textDocument": {
                        "uri": cell_uris[1],
                        "version": 1,
                    },
                    "edits": [
                        {
                            "range": {
                                "start": {"line": 1, "character": 6},
                                "end": {"line": 1, "character": 6},
                            },
                            "newText": "_",
                        },
                        {
                            "range": {
                                "start": {"line": 1, "character": 10},
                                "end": {"line": 1, "character": 10},
                            },
                            "newText": "tion_",
                        },
                    ],
                },
                {
                    "textDocument": {
                        "uri": cell_uris[2],
                        "version": 1,
                    },
                    "edits": [
                        {
                            "range": {
                                "start": {"line": 0, "character": 2},
                                "end": {"line": 0, "character": 2},
                            },
                            "newText": "_",
                        },
                        {
                            "range": {
                                "start": {"line": 0, "character": 6},
                                "end": {"line": 0, "character": 6},
                            },
                            "newText": "tion_",
                        },
                    ],
                },
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


def test_lsp_rename_inserts_at_line_start():
    """Tests renaming a variable by inserting text at the start of a line."""
    with session.LspSession() as ls_session:
        ls_session.initialize()
        uri = as_uri((REFACTOR_TEST_ROOT / "rename_test2.py"))
        actual = ls_session.text_document_rename(
            {
                "textDocument": {"uri": uri},
                "position": {"line": 1, "character": 0},
                # old name is "x", so we will insert "a"
                "newName": "ax",
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
                                "end": {"line": 1, "character": 0},
                            },
                            "newText": "a",
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


def test_rename_package() -> None:
    """Tests renaming of an imported package."""
    test_root = REFACTOR_TEST_ROOT / "rename_package_test1"
    with session.LspSession() as ls_session:
        ls_session.initialize()
        uri = as_uri(test_root / "rename_test_main.py")
        actual = ls_session.text_document_rename(
            {
                "textDocument": {"uri": uri},
                "position": {"line": 2, "character": 12},
                "newName": "new_name",
            }
        )
        old_name_uri = as_uri(test_root / "old_name")
        new_name_uri = as_uri(test_root / "new_name")

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
                                "start": {"line": 2, "character": 5},
                                "end": {"line": 2, "character": 8},
                            },
                            "newText": "new",
                        }
                    ],
                },
                {
                    "kind": "rename",
                    "oldUri": old_name_uri,
                    "newUri": new_name_uri,
                    "options": {"overwrite": True, "ignoreIfExists": True},
                },
            ]
        }
        assert_that(actual, is_(expected))


@pytest.mark.skipif(
    sys.platform == "win32",
    reason="Fails on Windows due to how pygls handles line endings "
    "(https://github.com/pappasam/jedi-language-server/issues/159)",
)
def test_rename_package_notebook() -> None:
    """Tests renaming of an imported package in a notebook."""
    test_root = REFACTOR_TEST_ROOT / "rename_package_test1"
    with session.LspSession() as ls_session:
        ls_session.initialize()
        path = test_root / "rename_test_main.ipynb"
        cell_uris = ls_session.open_notebook_document(path)
        actual = ls_session.text_document_rename(
            {
                "textDocument": {"uri": cell_uris[0]},
                "position": {"line": 0, "character": 12},
                "newName": "new_name",
            }
        )
        old_name_uri = as_uri(test_root / "old_name")
        new_name_uri = as_uri(test_root / "new_name")

        expected = {
            "documentChanges": [
                {
                    "textDocument": {
                        "uri": cell_uris[0],
                        "version": 1,
                    },
                    "edits": [
                        {
                            "range": {
                                "start": {"line": 0, "character": 5},
                                "end": {"line": 0, "character": 8},
                            },
                            "newText": "new",
                        }
                    ],
                },
                {
                    "textDocument": {
                        "uri": as_uri(test_root / "rename_test_main.py"),
                        "version": 0,
                    },
                    "edits": [
                        {
                            "range": {
                                "start": {"line": 2, "character": 5},
                                "end": {"line": 2, "character": 8},
                            },
                            "newText": "new",
                        },
                    ],
                },
                {
                    "kind": "rename",
                    "oldUri": old_name_uri,
                    "newUri": new_name_uri,
                    "options": {"overwrite": True, "ignoreIfExists": True},
                },
            ]
        }
        assert_that(actual, is_(expected))


def test_rename_module() -> None:
    """Tests example from the following example.

    https://github.com/pappasam/jedi-language-server/issues/159
    """
    test_root = REFACTOR_TEST_ROOT
    with session.LspSession() as ls_session:
        ls_session.initialize()
        uri = as_uri(test_root / "rename_module.py")
        actual = ls_session.text_document_rename(
            {
                "textDocument": {"uri": uri},
                "position": {"line": 0, "character": 24},
                "newName": "new_somemodule",
            }
        )
        old_name_uri = as_uri(test_root / "somepackage" / "somemodule.py")
        new_name_uri = as_uri(test_root / "somepackage" / "new_somemodule.py")

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
                                "start": {"line": 0, "character": 24},
                                "end": {"line": 0, "character": 24},
                            },
                            "newText": "new_",
                        },
                        {
                            "range": {
                                "start": {"line": 4, "character": 4},
                                "end": {"line": 4, "character": 4},
                            },
                            "newText": "new_",
                        },
                    ],
                },
                {
                    "kind": "rename",
                    "oldUri": old_name_uri,
                    "newUri": new_name_uri,
                    "options": {"overwrite": True, "ignoreIfExists": True},
                },
            ]
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
                    r"Extract expression into variable 'jls_extract_var'"
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
                    r"Extract expression into function 'jls_extract_def'"
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


def test_lsp_code_action_notebook() -> None:
    """Tests code actions like extract variable and extract function in notebooks."""
    with session.LspSession() as ls_session:
        ls_session.initialize()
        path = REFACTOR_TEST_ROOT / "code_action_test1.ipynb"
        cell_uris = ls_session.open_notebook_document(path)
        uri = cell_uris[0]
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

        # Code actions are not yet supported in notebooks.
        assert_that(actual, is_(None))


def test_lsp_code_action2() -> None:
    """Tests edge case for code actions.

    Identified in: https://github.com/pappasam/jedi-language-server/issues/96
    """
    with session.LspSession() as ls_session:
        ls_session.initialize()
        uri = as_uri((REFACTOR_TEST_ROOT / "code_action_test2.py"))
        actual = ls_session.text_document_code_action(
            {
                "textDocument": {"uri": uri},
                "range": {
                    "start": {"line": 2, "character": 6},
                    "end": {"line": 2, "character": 6},
                },
                "context": {"diagnostics": []},
            }
        )
        assert_that(actual, is_(None))
