"""Tests for initialization options over language server protocol."""

import copy
from threading import Event

from hamcrest import assert_that, is_

from tests.lsp_test_client import defaults, session


def test_invalid_initialization_options() -> None:
    """Test what happens when invalid initialization is sent."""
    initialize_params = copy.deepcopy(defaults.VSCODE_DEFAULT_INITIALIZE)
    initialize_params["initializationOptions"]["diagnostics"] = 1

    with session.LspSession() as ls_session:
        done = Event()
        actual = []

        def _handler(params):
            actual.append(params)
            done.set()

        ls_session.set_notification_callback(
            session.WINDOW_SHOW_MESSAGE, _handler
        )

        ls_session.initialize(initialize_params)
        expected = [
            {
                "type": 1,
                "message": "Invalid InitializationOptions, using defaults: 1 validation error for InitializationOptions\ndiagnostics\n  value is not a valid dict (type=type_error.dict)",
            }
        ]

        assert_that(actual, is_(expected))