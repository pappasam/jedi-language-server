"""Tests for hover requests."""

from hamcrest import assert_that, is_

from tests import TEST_DATA
from tests.lsp_test_client import session
from tests.lsp_test_client.utils import as_uri

HOVER_TEST_ROOT = TEST_DATA / "hover"


def test_hover_on_module():
    """Tests hover on the name of a imported module.

    Test Data: tests/test_data/hover/hover_test1.py
    """
    with session.LspSession() as ls_session:
        ls_session.initialize()
        uri = as_uri(HOVER_TEST_ROOT / "hover_test1.py")
        actual = ls_session.text_document_hover(
            {
                "textDocument": {"uri": uri},
                "position": {"line": 2, "character": 12},
            }
        )

        expected = {
            "contents": {
                "kind": "markdown",
                "value": "```\nModule doc string for testing\n```\n",
            },
            "range": {
                "start": {"line": 2, "character": 7},
                "end": {"line": 2, "character": 17},
            },
        }
        assert_that(actual, is_(expected))


def test_hover_on_function():
    """Tests hover on the name of a function.

    Test Data: tests/test_data/hover/hover_test1.py
    """
    with session.LspSession() as ls_session:
        ls_session.initialize()
        uri = as_uri(HOVER_TEST_ROOT / "hover_test1.py")
        actual = ls_session.text_document_hover(
            {
                "textDocument": {"uri": uri},
                "position": {"line": 4, "character": 19},
            }
        )

        expected = {
            "contents": {
                "kind": "markdown",
                "value": "```\ndo_something()\n\nFunction doc string for testing\n```\n",
            },
            "range": {
                "start": {"line": 4, "character": 11},
                "end": {"line": 4, "character": 23},
            },
        }
        assert_that(actual, is_(expected))


def test_hover_on_class():
    """Tests hover on the name of a class.

    Test Data: tests/test_data/hover/hover_test1.py
    """
    with session.LspSession() as ls_session:
        ls_session.initialize()
        uri = as_uri(HOVER_TEST_ROOT / "hover_test1.py")
        actual = ls_session.text_document_hover(
            {
                "textDocument": {"uri": uri},
                "position": {"line": 6, "character": 21},
            }
        )

        expected = {
            "contents": {
                "kind": "markdown",
                "value": "```\nSomeClass()\n\nClass doc string for testing\n```\n",
            },
            "range": {
                "start": {"line": 6, "character": 15},
                "end": {"line": 6, "character": 24},
            },
        }
        assert_that(actual, is_(expected))


def test_hover_on_method():
    """Tests hover on the name of a class method.

    Test Data: tests/test_data/hover/hover_test1.py
    """
    with session.LspSession() as ls_session:
        ls_session.initialize()
        uri = as_uri(HOVER_TEST_ROOT / "hover_test1.py")
        actual = ls_session.text_document_hover(
            {
                "textDocument": {"uri": uri},
                "position": {"line": 8, "character": 6},
            }
        )

        expected = {
            "contents": {
                "kind": "markdown",
                "value": "```\nsome_method()\n\nMethod doc string for testing\n```\n",
            },
            "range": {
                "start": {"line": 8, "character": 2},
                "end": {"line": 8, "character": 13},
            },
        }
        assert_that(actual, is_(expected))


def test_hover_on_method_no_docstring():
    """Tests hover on the name of a class method without doc string.

    Test Data: tests/test_data/hover/hover_test1.py
    """
    with session.LspSession() as ls_session:
        ls_session.initialize()
        uri = as_uri(HOVER_TEST_ROOT / "hover_test1.py")
        actual = ls_session.text_document_hover(
            {
                "textDocument": {"uri": uri},
                "position": {"line": 10, "character": 6},
            }
        )

        expected = {
            "contents": {
                "kind": "markdown",
                "value": "```\nsome_method2()\n```\n",
            },
            "range": {
                "start": {"line": 10, "character": 2},
                "end": {"line": 10, "character": 14},
            },
        }
        assert_that(actual, is_(expected))
