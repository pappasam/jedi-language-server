"""Tests for initialization options over language server protocol."""

import copy
from threading import Event

from hamcrest import assert_that

from tests.lsp_test_client import defaults, session


def test_invalid_initialization_options() -> None:
    """Test what happens when invalid initialization is sent."""
    initialize_params = copy.deepcopy(defaults.VSCODE_DEFAULT_INITIALIZE)
    initialize_params["initializationOptions"]["diagnostics"] = 1

    with session.LspSession() as ls_session:
        window_show_message_done = Event()
        window_log_message_done = Event()

        actual = []

        def _window_show_message_handler(params):
            actual.append(params)
            window_show_message_done.set()

        ls_session.set_notification_callback(
            session.WINDOW_SHOW_MESSAGE, _window_show_message_handler
        )

        def _window_log_message_handler(params):
            actual.append(params)
            window_log_message_done.set()

        ls_session.set_notification_callback(
            session.WINDOW_LOG_MESSAGE, _window_log_message_handler
        )

        ls_session.initialize(initialize_params)

        window_show_message_done.wait(5)
        window_log_message_done.wait(5)

        assert_that(len(actual) == 2)
        for params in actual:
            assert_that(params["type"] == 1)
            assert_that(
                params["message"]
                == (
                    "Invalid InitializationOptions, using defaults: "
                    "['invalid value for type, expected Diagnostics @ "
                    "$.diagnostics']"
                )
            )
