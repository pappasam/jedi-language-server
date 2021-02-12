"""Tests for document completion requests"""

import pathlib
import json
from hamcrest import assert_that, is_
from tests import TEST_DATA
from tests.lsp_test_client import session


COMPLETION_TEST_ROOT = pathlib.Path(TEST_DATA) / "completion"


def extract_completion_params(test_file):
    """Extract completions parameters form the test file. This should make
    reduce the fragility of the tests.
    """
    file_path = COMPLETION_TEST_ROOT / test_file
    position = None
    context = None
    with open(file_path.absolute(), "r") as data:
        lines = data.readlines()
        for line in lines:
            parts = line.split("@")
            try:
                if parts[1] == "completion-position":
                    position = json.loads(parts[2])
                elif parts[1] == "completion-context":
                    context = json.loads(parts[2])
            except IndexError:
                pass

    return {
        "textDocument": {"uri": file_path.as_uri()},
        "position": position,
        "context": context,
    }


def test_lsp_completion() -> None:
    """Test a simple completion request

    Test Data: tests/test_data/completion/completion_test1.py
    """

    with session.LspSession() as ls_session:
        uri = (COMPLETION_TEST_ROOT / "completion_test1.py").as_uri()
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
