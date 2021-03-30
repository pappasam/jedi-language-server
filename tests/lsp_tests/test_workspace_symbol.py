"""Tests for workspace symbols requests."""

from hamcrest import assert_that, is_

from tests import TEST_DATA
from tests.lsp_test_client import session
from tests.lsp_test_client.utils import as_uri

SYMBOL_TEST_ROOT = TEST_DATA / "symbol"


def test_workspace_symbol() -> None:
    """Test document symbol request.

    Test Data: tests/test_data/symbol/symbol_test1.py
    """

    with session.LspSession() as ls_session:
        ls_session.initialize()
        actual = ls_session.workspace_symbol({"query": "do_workspace_thing"})

        module_uri = as_uri(SYMBOL_TEST_ROOT / "somemodule2.py")
        expected = [
            {
                "name": "do_workspace_thing",
                "kind": 12,
                "location": {
                    "uri": module_uri,
                    "range": {
                        "start": {"line": 7, "character": 4},
                        "end": {"line": 7, "character": 22},
                    },
                },
                "containerName": (
                    "tests.test_data.symbol.somemodule2.do_workspace_thing"
                ),
            }
        ]
        assert_that(actual, is_(expected))
