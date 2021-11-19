"""Tests for signature help requests."""

import pytest
from hamcrest import assert_that, is_

from tests import TEST_DATA
from tests.lsp_test_client import session
from tests.lsp_test_client.utils import as_uri

SIGNATURE_TEST_ROOT = TEST_DATA / "signature"


@pytest.mark.parametrize(
    ["trigger_char", "column", "active_param"], [("(", 14, 0), (",", 18, 1)]
)
def test_signature_help(trigger_char, column, active_param):
    """Tests signature help response for a function.

    Test Data: tests/test_data/signature/signature_test1.py
    """
    with session.LspSession() as ls_session:
        ls_session.initialize()
        uri = as_uri(SIGNATURE_TEST_ROOT / "signature_test1.py")
        actual = ls_session.text_document_signature_help(
            {
                "textDocument": {"uri": uri},
                "position": {"line": 7, "character": column},
                "context": {
                    "isRetrigger": False,
                    "triggerCharacter": trigger_char,
                    "triggerKind": 2,
                },
            }
        )

        expected = {
            "signatures": [
                {
                    "label": (
                        "def some_function(arg1: str, arg2: int, arg3: list)"
                    ),
                    "documentation": {
                        "kind": "markdown",
                        "value": "```text\nThis is a test function.\n```",
                    },
                    "parameters": [
                        {"label": "arg1: str"},
                        {"label": "arg2: int"},
                        {"label": "arg3: list"},
                    ],
                }
            ],
            "activeSignature": 0,
            "activeParameter": active_param,
        }

        assert_that(actual, is_(expected))
