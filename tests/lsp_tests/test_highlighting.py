"""Tests for highlighting requests."""

import pytest
from hamcrest import assert_that, is_

from tests import TEST_DATA
from tests.lsp_test_client import session
from tests.lsp_test_client.utils import as_uri

HIGHLIGHTING_TEST_ROOT = TEST_DATA / "highlighting"


@pytest.mark.parametrize(
    ["position", "expected"],
    [
        ({"line": 2, "character": 3}, None),
        (
            {"line": 2, "character": 8},
            [
                {
                    "range": {
                        "start": {"line": 2, "character": 5},
                        "end": {"line": 2, "character": 9},
                    }
                }
            ],
        ),
        (
            {"line": 2, "character": 20},
            [
                {
                    "range": {
                        "start": {"line": 2, "character": 17},
                        "end": {"line": 2, "character": 21},
                    }
                },
                {
                    "range": {
                        "start": {"line": 12, "character": 16},
                        "end": {"line": 12, "character": 20},
                    }
                },
            ],
        ),
        (
            {"line": 4, "character": 8},
            [
                {
                    "range": {
                        "start": {"line": 4, "character": 0},
                        "end": {"line": 4, "character": 13},
                    }
                },
                {
                    "range": {
                        "start": {"line": 20, "character": 15},
                        "end": {"line": 20, "character": 28},
                    }
                },
                {
                    "range": {
                        "start": {"line": 24, "character": 29},
                        "end": {"line": 24, "character": 42},
                    }
                },
            ],
        ),
        (
            {"line": 7, "character": 9},
            [
                {
                    "range": {
                        "start": {"line": 7, "character": 4},
                        "end": {"line": 7, "character": 17},
                    }
                },
                {
                    "range": {
                        "start": {"line": 24, "character": 15},
                        "end": {"line": 24, "character": 28},
                    }
                },
            ],
        ),
        (
            {"line": 7, "character": 20},
            [
                {
                    "range": {
                        "start": {"line": 7, "character": 18},
                        "end": {"line": 7, "character": 21},
                    }
                },
                {
                    "range": {
                        "start": {"line": 9, "character": 11},
                        "end": {"line": 9, "character": 14},
                    }
                },
            ],
        ),
        (
            {"line": 12, "character": 14},
            [
                {
                    "range": {
                        "start": {"line": 12, "character": 6},
                        "end": {"line": 12, "character": 15},
                    }
                },
                {
                    "range": {
                        "start": {"line": 27, "character": 11},
                        "end": {"line": 27, "character": 20},
                    }
                },
            ],
        ),
        (
            {"line": 15, "character": 20},
            [
                {
                    "range": {
                        "start": {"line": 15, "character": 17},
                        "end": {"line": 15, "character": 21},
                    }
                },
                {
                    "range": {
                        "start": {"line": 16, "character": 8},
                        "end": {"line": 16, "character": 12},
                    }
                },
            ],
        ),
        (
            {"line": 16, "character": 17},
            [
                {
                    "range": {
                        "start": {"line": 16, "character": 13},
                        "end": {"line": 16, "character": 19},
                    }
                },
                {
                    "range": {
                        "start": {"line": 20, "character": 36},
                        "end": {"line": 20, "character": 42},
                    }
                },
            ],
        ),
        (
            {"line": 18, "character": 15},
            [
                {
                    "range": {
                        "start": {"line": 18, "character": 8},
                        "end": {"line": 18, "character": 20},
                    }
                },
                {
                    "range": {
                        "start": {"line": 28, "character": 9},
                        "end": {"line": 28, "character": 21},
                    }
                },
            ],
        ),
    ],
)
def test_highlighting(position, expected):
    """Tests highliting on import statement.

    Test Data: tests/test_data/highlighting/highlighting_test1.py
    """
    with session.LspSession() as ls_session:
        ls_session.initialize()
        uri = as_uri(HIGHLIGHTING_TEST_ROOT / "highlighting_test1.py")
        actual = ls_session.text_document_highlight(
            {
                "textDocument": {"uri": uri},
                "position": position,
            }
        )

        assert_that(actual, is_(expected))
