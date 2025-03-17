"""Tests for initialize requests."""

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


def test_notebook_server_capabilities() -> None:
    """Test that the server's notebook capabilities are set correctly."""
    actual = []

    def _process_server_capabilities(capabilities):
        actual.append(capabilities)

    initialize_params = copy.deepcopy(defaults.VSCODE_DEFAULT_INITIALIZE)
    initialize_params["capabilities"]["notebookDocument"] = {
        "synchronization": {
            "dynamicRegistration": True,
            "executionSummarySupport": True,
        },
    }
    with session.LspSession() as ls_session:
        ls_session.initialize(initialize_params, _process_server_capabilities)

        assert_that(len(actual) == 1)
        for params in actual:
            assert_that(
                params["capabilities"]["notebookDocumentSync"],
                is_(
                    {"notebookSelector": [{"cells": [{"language": "python"}]}]}
                ),
            )
