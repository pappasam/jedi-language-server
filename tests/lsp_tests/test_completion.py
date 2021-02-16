"""Tests for document completion requests."""

from hamcrest import assert_that, is_

from tests import TEST_DATA
from tests.lsp_test_client import session
from tests.lsp_test_client.utils import as_uri

COMPLETION_TEST_ROOT = TEST_DATA / "completion"


def test_lsp_completion() -> None:
    """Test a simple completion request.

    Test Data: tests/test_data/completion/completion_test1.py
    """

    with session.LspSession() as ls_session:
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
                    "detail": None,
                    "documentation": None,
                    "deprecated": False,
                    "preselect": False,
                    "sortText": "z",
                    "filterText": "my_function",
                    "insertText": "my_function()$0",
                    "insertTextFormat": 2,
                    "textEdit": None,
                    "additionalTextEdits": None,
                    "commitCharacters": None,
                    "command": None,
                    "data": None,
                }
            ],
        }
        assert_that(actual, is_(expected))
