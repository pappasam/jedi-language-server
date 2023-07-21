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
        expected = [
            {
                "type": 1,
                "message": "Invalid InitializationOptions, using defaults: 1 validation error for InitializationOptions\ndiagnostics\n  Input should be a valid dictionary or instance of Diagnostics [type=model_type, input_value=1, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.0.3/v/model_type",
            },
            {
                "type": 1,
                "message": "Invalid InitializationOptions, using defaults: 1 validation error for InitializationOptions\ndiagnostics\n  Input should be a valid dictionary or instance of Diagnostics [type=model_type, input_value=1, input_type=int]\n    For further information visit https://errors.pydantic.dev/2.0.3/v/model_type",
            },
        ]

        assert_that(actual, is_(expected))
