"""Tests for definition requests."""

from hamcrest import assert_that, is_

from tests import TEST_DATA
from tests.lsp_test_client import session
from tests.lsp_test_client.utils import as_uri

DEFINITION_TEST_ROOT = TEST_DATA / "definition"


def test_definition():
    """Tests definition on a function imported from module.

    Test Data: tests/test_data/definition/definition_test1.py
    """
    with session.LspSession() as ls_session:
        ls_session.initialize()
        uri = as_uri(DEFINITION_TEST_ROOT / "definition_test1.py")
        actual = ls_session.text_document_definition(
            {
                "textDocument": {"uri": uri},
                "position": {"line": 5, "character": 20},
            }
        )

        module_uri = as_uri(DEFINITION_TEST_ROOT / "somemodule2.py")
        expected = [
            {
                "uri": module_uri,
                "range": {
                    "start": {"line": 3, "character": 4},
                    "end": {"line": 3, "character": 17},
                },
            }
        ]

        assert_that(actual, is_(expected))
