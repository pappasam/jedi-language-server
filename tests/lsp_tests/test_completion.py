"""Tests for document completion requests."""

import copy

from hamcrest import assert_that, is_

from tests import TEST_DATA
from tests.lsp_test_client import session
from tests.lsp_test_client.defaults import VSCODE_DEFAULT_INITIALIZE
from tests.lsp_test_client.utils import as_uri

COMPLETION_TEST_ROOT = TEST_DATA / "completion"

# pylint: disable=line-too-long


def test_lsp_completion() -> None:
    """Test a simple completion request.

    Test Data: tests/test_data/completion/completion_test1.py
    """

    with session.LspSession() as ls_session:
        ls_session.initialize()
        uri = as_uri(COMPLETION_TEST_ROOT / "completion_test1.py")
        actual = ls_session.text_document_completion(
            {
                "textDocument": {"uri": uri},
                "position": {"line": 8, "character": 2},
                "context": {"triggerKind": 1},
            }
        )

        expected = {
            "isIncomplete": False,
            "items": [
                {
                    "label": "my_function",
                    "kind": 3,
                    "sortText": "v0",
                    "filterText": "my_function",
                    "insertText": "my_function()$0",
                    "insertTextFormat": 2,
                }
            ],
        }
        assert_that(actual, is_(expected))

        actual = ls_session.completion_item_resolve(
            {
                "label": "my_function",
                "kind": 3,
                "sortText": "v0",
                "filterText": "my_function",
                "insertText": "my_function()$0",
                "insertTextFormat": 2,
            }
        )
        expected = {
            "label": "my_function",
            "kind": 3,
            "detail": "def my_function()",
            "documentation": {
                "kind": "markdown",
                "value": "```text\nSimple test function.\n```",
            },
            "sortText": "v0",
            "filterText": "my_function",
            "insertText": "my_function()$0",
            "insertTextFormat": 2,
        }
        assert_that(actual, is_(expected))


def test_eager_lsp_completion() -> None:
    """Test a simple completion request, with eager resolution.

    Test Data: tests/test_data/completion/completion_test1.py
    """

    with session.LspSession() as ls_session:
        # Initialize, asking for eager resolution.
        initialize_params = copy.deepcopy(VSCODE_DEFAULT_INITIALIZE)
        initialize_params["initializationOptions"] = {
            "completion": {"resolveEagerly": True}
        }
        ls_session.initialize(initialize_params)

        uri = as_uri(COMPLETION_TEST_ROOT / "completion_test1.py")
        actual = ls_session.text_document_completion(
            {
                "textDocument": {"uri": uri},
                "position": {"line": 8, "character": 2},
                "context": {"triggerKind": 1},
            }
        )

        # pylint: disable=line-too-long
        expected = {
            "isIncomplete": False,
            "items": [
                {
                    "label": "my_function",
                    "kind": 3,
                    "detail": "def my_function()",
                    "documentation": {
                        "kind": "markdown",
                        "value": "```text\nSimple test function.\n```",
                    },
                    "sortText": "v0",
                    "filterText": "my_function",
                    "insertText": "my_function()$0",
                    "insertTextFormat": 2,
                }
            ],
        }
        assert_that(actual, is_(expected))


def test_lsp_completion_class_method() -> None:
    """Checks whether completion returns self unnecessarily.

    References: https://github.com/pappasam/jedi-language-server/issues/121

    Note: I resolve eagerly to make test simpler
    """
    with session.LspSession() as ls_session:
        # Initialize, asking for eager resolution.
        initialize_params = copy.deepcopy(VSCODE_DEFAULT_INITIALIZE)
        initialize_params["initializationOptions"] = {
            "completion": {"resolveEagerly": True}
        }
        ls_session.initialize(initialize_params)

        uri = as_uri(COMPLETION_TEST_ROOT / "completion_test_class_self.py")
        actual = ls_session.text_document_completion(
            {
                "textDocument": {"uri": uri},
                "position": {"line": 7, "character": 13},
                "context": {"triggerKind": 1},
            }
        )

        # pylint: disable=line-too-long
        expected = {
            "isIncomplete": False,
            "items": [
                {
                    "label": "some_method",
                    "kind": 3,
                    "detail": "def some_method(x)",
                    "documentation": {
                        "kind": "markdown",
                        "value": "```text\nGreat method.\n```",
                    },
                    "sortText": "v0",
                    "filterText": "some_method",
                    "insertText": "some_method(${1:x})$0",
                    "insertTextFormat": 2,
                }
            ],
        }
        assert_that(actual, is_(expected))


def test_lsp_completion_class_noargs() -> None:
    """Checks if classes without arguments include parenthesis in signature."""
    with session.LspSession() as ls_session:
        # Initialize, asking for eager resolution.
        initialize_params = copy.deepcopy(VSCODE_DEFAULT_INITIALIZE)
        initialize_params["initializationOptions"] = {
            "completion": {"resolveEagerly": True}
        }
        ls_session.initialize(initialize_params)

        uri = as_uri(COMPLETION_TEST_ROOT / "completion_test2.py")
        actual = ls_session.text_document_completion(
            {
                "textDocument": {"uri": uri},
                "position": {"line": 7, "character": 3},
                "context": {"triggerKind": 1},
            }
        )

        expected = {
            "isIncomplete": False,
            "items": [
                {
                    "label": "MyClass",
                    "kind": 7,
                    "detail": "class MyClass()",
                    "documentation": {
                        "kind": "markdown",
                        "value": "```text\nSimple class.\n```",
                    },
                    "sortText": "v0",
                    "filterText": "MyClass",
                    "insertText": "MyClass()$0",
                    "insertTextFormat": 2,
                }
            ],
        }
        assert_that(actual, is_(expected))
