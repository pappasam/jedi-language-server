"""Tests for hover requests."""

from hamcrest import assert_that, is_

from tests import TEST_DATA
from tests.lsp_test_client import session
from tests.lsp_test_client.utils import as_uri

HOVER_TEST_ROOT = TEST_DATA / "hover"


def test_hover_on_module() -> None:
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
                "value": "```python\nmodule somemodule\n```\n---\nModule doc string for testing.",
            },
            "range": {
                "start": {"line": 2, "character": 7},
                "end": {"line": 2, "character": 17},
            },
        }
        assert_that(actual, is_(expected))


def test_hover_on_module_notebook() -> None:
    """Tests hover on the name of an imported module in a notebook.

    Test Data: tests/test_data/hover/hover_test1.ipynb
    """
    with session.LspSession() as ls_session:
        ls_session.initialize()
        path = HOVER_TEST_ROOT / "hover_test1.ipynb"
        cell_uris = ls_session.open_notebook_document(path)

        actual = ls_session.text_document_hover(
            {
                "textDocument": {"uri": cell_uris[0]},
                "position": {"line": 0, "character": 12},
            }
        )

        expected = {
            "contents": {
                "kind": "markdown",
                "value": "```python\nmodule somemodule\n```\n---\nModule doc string for testing.",
            },
            "range": {
                "start": {"line": 0, "character": 7},
                "end": {"line": 0, "character": 17},
            },
        }
        assert_that(actual, is_(expected))


def test_hover_on_function() -> None:
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
                "value": "```python\ndef do_something()\n```\n---\nFunction doc string for testing.\n**Full name:** `somemodule.do_something`",
            },
            "range": {
                "start": {"line": 4, "character": 11},
                "end": {"line": 4, "character": 23},
            },
        }
        assert_that(actual, is_(expected))


def test_hover_on_function_notebook() -> None:
    """Tests hover on the name of a function in a notebook.

    Test Data: tests/test_data/hover/hover_test1.ipynb
    """
    with session.LspSession() as ls_session:
        ls_session.initialize()
        path = HOVER_TEST_ROOT / "hover_test1.ipynb"
        cell_uris = ls_session.open_notebook_document(path)

        actual = ls_session.text_document_hover(
            {
                "textDocument": {"uri": cell_uris[1]},
                "position": {"line": 0, "character": 19},
            }
        )

        expected = {
            "contents": {
                "kind": "markdown",
                "value": "```python\ndef do_something()\n```\n---\nFunction doc string for testing.\n**Full name:** `somemodule.do_something`",
            },
            "range": {
                "start": {"line": 0, "character": 11},
                "end": {"line": 0, "character": 23},
            },
        }
        assert_that(actual, is_(expected))


def test_hover_on_class() -> None:
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
                "value": "```python\nclass SomeClass()\n```\n---\nClass doc string for testing.\n**Full name:** `somemodule.SomeClass`",
            },
            "range": {
                "start": {"line": 6, "character": 15},
                "end": {"line": 6, "character": 24},
            },
        }
        assert_that(actual, is_(expected))


def test_hover_on_class_notebook() -> None:
    """Tests hover on the name of a class in a notebook.

    Test Data: tests/test_data/hover/hover_test1.ipynb
    """
    with session.LspSession() as ls_session:
        ls_session.initialize()
        path = HOVER_TEST_ROOT / "hover_test1.ipynb"
        cell_uris = ls_session.open_notebook_document(path)

        actual = ls_session.text_document_hover(
            {
                "textDocument": {"uri": cell_uris[2]},
                "position": {"line": 0, "character": 21},
            }
        )

        expected = {
            "contents": {
                "kind": "markdown",
                "value": "```python\nclass SomeClass()\n```\n---\nClass doc string for testing.\n**Full name:** `somemodule.SomeClass`",
            },
            "range": {
                "start": {"line": 0, "character": 15},
                "end": {"line": 0, "character": 24},
            },
        }
        assert_that(actual, is_(expected))


def test_hover_on_method() -> None:
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
                "value": "```python\ndef some_method()\n```\n---\nMethod doc string for testing.\n**Full name:** `somemodule.SomeClass.some_method`",
            },
            "range": {
                "start": {"line": 8, "character": 2},
                "end": {"line": 8, "character": 13},
            },
        }
        assert_that(actual, is_(expected))


def test_hover_on_method_notebook() -> None:
    """Tests hover on the name of a class method in a notebook.

    Test Data: tests/test_data/hover/hover_test1.ipynb
    """
    with session.LspSession() as ls_session:
        ls_session.initialize()
        path = HOVER_TEST_ROOT / "hover_test1.ipynb"
        cell_uris = ls_session.open_notebook_document(path)

        actual = ls_session.text_document_hover(
            {
                "textDocument": {"uri": cell_uris[3]},
                "position": {"line": 0, "character": 6},
            }
        )

        expected = {
            "contents": {
                "kind": "markdown",
                "value": "```python\ndef some_method()\n```\n---\nMethod doc string for testing.\n**Full name:** `somemodule.SomeClass.some_method`",
            },
            "range": {
                "start": {"line": 0, "character": 2},
                "end": {"line": 0, "character": 13},
            },
        }
        assert_that(actual, is_(expected))


def test_hover_on_method_no_docstring() -> None:
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
                "value": "```python\ndef some_method2()\n```\n---\n**Full name:** `somemodule.SomeClass.some_method2`",
            },
            "range": {
                "start": {"line": 10, "character": 2},
                "end": {"line": 10, "character": 14},
            },
        }
        assert_that(actual, is_(expected))


def test_hover_on_method_no_docstring_notebook() -> None:
    """Tests hover on the name of a class method without doc string in a notebook.

    Test Data: tests/test_data/hover/hover_test1.ipynb
    """
    with session.LspSession() as ls_session:
        ls_session.initialize()
        path = HOVER_TEST_ROOT / "hover_test1.ipynb"
        cell_uris = ls_session.open_notebook_document(path)

        actual = ls_session.text_document_hover(
            {
                "textDocument": {"uri": cell_uris[4]},
                "position": {"line": 0, "character": 6},
            }
        )

        expected = {
            "contents": {
                "kind": "markdown",
                "value": "```python\ndef some_method2()\n```\n---\n**Full name:** `somemodule.SomeClass.some_method2`",
            },
            "range": {
                "start": {"line": 0, "character": 2},
                "end": {"line": 0, "character": 14},
            },
        }
        assert_that(actual, is_(expected))
