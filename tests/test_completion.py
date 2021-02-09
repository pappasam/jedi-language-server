"""Tests for document completion requests"""

import pathlib
import json
from hamcrest import assert_that, is_
from tests import TEST_DATA
from tests.lsp import session


def extract_completion_params(test_file):
    """Extract completions parameters form the test file. This should make
    reduce the fragility of the tests.
    """
    file_path = pathlib.Path(TEST_DATA) / "completion" / test_file
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
    """Test a simple completion request"""

    with session.LspSession() as ls_session:

        actual = ls_session.text_document_completion(
            extract_completion_params("completion_test1.py")
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
