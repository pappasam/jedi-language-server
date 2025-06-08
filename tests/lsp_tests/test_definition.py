"""Tests for definition requests."""

from hamcrest import assert_that, is_

from tests import TEST_DATA
from tests.lsp_test_client import session
from tests.lsp_test_client.utils import as_uri

DEFINITION_TEST_ROOT = TEST_DATA / "definition"


def test_definition() -> None:
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


def test_definition_notebook() -> None:
    """Tests definition on a function imported from a module, in a notebook.

    Test Data: tests/test_data/definition/definition_test1.ipynb
    """
    with session.LspSession() as ls_session:
        ls_session.initialize()
        path = DEFINITION_TEST_ROOT / "definition_test1.ipynb"
        cell_uris = ls_session.open_notebook_document(path)
        actual = ls_session.text_document_definition(
            {
                "textDocument": {"uri": cell_uris[1]},
                "position": {"line": 1, "character": 20},
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


def test_declaration() -> None:
    """Tests declaration on an imported module.

    Test Data: tests/test_data/definition/definition_test1.py
    """
    with session.LspSession() as ls_session:
        ls_session.initialize()
        uri = as_uri(DEFINITION_TEST_ROOT / "definition_test1.py")
        actual = ls_session.text_document_declaration(
            {
                "textDocument": {"uri": uri},
                "position": {"line": 5, "character": 0},
            }
        )

        expected = [
            {
                "uri": uri,
                "range": {
                    "start": {"line": 2, "character": 26},
                    "end": {"line": 2, "character": 37},
                },
            }
        ]

        assert_that(actual, is_(expected))


def test_declaration_notebook() -> None:
    """Tests declaration on an imported module, in a notebook.

    Test Data: tests/test_data/definition/definition_test1.ipynb
    """
    with session.LspSession() as ls_session:
        ls_session.initialize()
        path = DEFINITION_TEST_ROOT / "definition_test1.ipynb"
        cell_uris = ls_session.open_notebook_document(path)
        actual = ls_session.text_document_declaration(
            {
                "textDocument": {"uri": cell_uris[1]},
                "position": {"line": 0, "character": 0},
            }
        )

        expected = [
            {
                "uri": cell_uris[0],
                "range": {
                    "start": {"line": 0, "character": 7},
                    "end": {"line": 0, "character": 17},
                },
            }
        ]

        assert_that(actual, is_(expected))
