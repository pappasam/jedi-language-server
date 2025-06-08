"""Tests for semantic tokens requests."""

import copy

import pylsp_jsonrpc
from hamcrest import assert_that, calling, is_, raises

from tests import TEST_DATA
from tests.lsp_test_client import session
from tests.lsp_test_client.defaults import VSCODE_DEFAULT_INITIALIZE
from tests.lsp_test_client.utils import as_uri

SEMANTIC_TEST_ROOT = TEST_DATA / "semantic_tokens"


def initialize_session(ls_session: session.LspSession) -> None:
    initialize_params = copy.deepcopy(VSCODE_DEFAULT_INITIALIZE)
    initialize_params["initializationOptions"] = {
        "semanticTokens": {"enable": True}
    }
    ls_session.initialize(initialize_params)


def test_semantic_tokens_disabled() -> None:
    with session.LspSession() as ls_session:
        ls_session.initialize()

        assert_that(
            calling(ls_session.text_doc_semantic_tokens_full).with_args(
                {
                    "textDocument": {"uri": ""},
                }
            ),
            raises(pylsp_jsonrpc.exceptions.JsonRpcException),
        )


def test_semantic_tokens_full_import() -> None:
    """Tests tokens for 'import name1 as name2'.

    Test Data: tests/test_data/semantic_tokens/semantic_tokens_test1.py.
    """
    with session.LspSession() as ls_session:
        initialize_session(ls_session)
        uri = as_uri(SEMANTIC_TEST_ROOT / "semantic_tokens_test1.py")
        actual = ls_session.text_doc_semantic_tokens_full(
            {
                "textDocument": {"uri": uri},
            }
        )
        # fmt: off
        # [line, column, length, id, mod_id]
        expected = {
            "data": [
                5, 7, 2, 0, 0,  # "import re"
                1, 7, 3, 0, 0,  # "import sys, "
                0, 5, 2, 0, 0,  # "os."
                0, 3, 4, 0, 0,  # "path as "
                0, 8, 4, 0, 0,  # "path"
            ]
        }
        # fmt: on
        assert_that(actual, is_(expected))


def test_semantic_tokens_full_import_from() -> None:
    """Tests tokens for 'from name1 import name2 as name3'.

    Test Data: tests/test_data/semantic_tokens/semantic_tokens_test2.py.
    """
    with session.LspSession() as ls_session:
        initialize_session(ls_session)
        uri = as_uri(SEMANTIC_TEST_ROOT / "semantic_tokens_test2.py")
        actual = ls_session.text_doc_semantic_tokens_full(
            {
                "textDocument": {"uri": uri},
            }
        )
        # fmt: off
        # [line, column, length, id, mod_id]
        expected = {
            "data": [
                0, 5, 2, 0, 0,  # "from os."
                0, 3, 4, 0, 0,  # "path import "
                0, 12, 6, 2, 0,  # "exists"
                1, 5, 3, 0, 0,  # "from sys import"
                0, 11, 4, 4, 0,  # "argv as "
                0, 8, 9, 4, 0,  # "arguments"
            ]
        }
        # fmt: on
        assert_that(actual, is_(expected))


def test_semantic_tokens_range_import_from() -> None:
    """Tests tokens for 'from name1 import name2 as name3'.

    Test Data: tests/test_data/semantic_tokens/semantic_tokens_test2.py.
    """
    with session.LspSession() as ls_session:
        initialize_session(ls_session)
        uri = as_uri(SEMANTIC_TEST_ROOT / "semantic_tokens_test2.py")
        actual = ls_session.text_doc_semantic_tokens_range(
            {
                "textDocument": {"uri": uri},
                "range": {
                    "start": {"line": 1, "character": 1},
                    "end": {"line": 2, "character": 0},
                },
            }
        )
        # fmt: off
        # [line, column, length, id, mod_id]
        expected = {
            "data": [
                0, 4, 3, 0, 0,  # "from sys import"
                0, 11, 4, 4, 0,  # "argv as "
                0, 8, 9, 4, 0,  # "arguments"
            ]
        }
        # fmt: on
        assert_that(actual, is_(expected))
