"""Tests for problem diagnostics notification."""

import copy
import json
import platform
import tempfile
from threading import Event

from hamcrest import assert_that, is_

from tests import TEST_DATA
from tests.lsp_test_client import session
from tests.lsp_test_client.defaults import VSCODE_DEFAULT_INITIALIZE
from tests.lsp_test_client.utils import PythonFile, as_uri

DIAGNOSTICS_TEST_ROOT = TEST_DATA / "diagnostics"
TEMP_DIR = tempfile.gettempdir()


def get_changes(changes_file):
    """Obtain changes from a changes file."""
    with open(changes_file, "r") as ch_file:
        return json.load(ch_file)


def test_publish_diagnostics_on_open():
    """Tests publish diagnostics on open."""
    content_path = DIAGNOSTICS_TEST_ROOT / "diagnostics_test1_contents.txt"
    with open(content_path, "r") as text_file:
        contents = text_file.read()

    # Introduce a syntax error before opening the file
    contents = contents.replace("1 == 1", "1 === 1")

    actual = []
    with PythonFile(contents, TEMP_DIR) as py_file:
        uri = as_uri(py_file.fullpath)

        initialize_params = copy.deepcopy(VSCODE_DEFAULT_INITIALIZE)
        initialize_params["workspaceFolders"] = [
            {"uri": as_uri(TEMP_DIR), "name": "jedi_lsp_test"}
        ]
        with session.LspSession() as ls_session:
            ls_session.initialize(initialize_params)
            done = Event()

            def _handler(params):
                actual.append(params)
                done.set()

            ls_session.set_notification_callback(
                session.PUBLISH_DIAGNOSTICS, _handler
            )

            ls_session.notify_did_open(
                {
                    "textDocument": {
                        "uri": uri,
                        "languageId": "python",
                        "version": 1,
                        "text": contents,
                    }
                }
            )

            # ensure the document is loaded
            symbols = ls_session.text_document_symbol(
                {"textDocument": {"uri": uri}}
            )

            assert len(symbols) > 0

            # wait for a second to receive all notifications
            done.wait(1.1)

        # Diagnostics look a little different on Windows.
        filename = (
            as_uri(py_file.fullpath)
            if platform.system() == "Windows"
            else py_file.basename
        )

        expected = [
            {
                "uri": uri,
                "diagnostics": [
                    {
                        "range": {
                            "start": {"line": 5, "character": 15},
                            "end": {"line": 5, "character": 16},
                        },
                        "message": f"SyntaxError: invalid syntax ({filename}, line 6)",
                        "severity": 1,
                        "source": "compile",
                    }
                ],
            }
        ]
    assert_that(actual, is_(expected))


def test_publish_diagnostics_on_change():
    """Tests publish diagnostics on change."""
    with open(
        DIAGNOSTICS_TEST_ROOT / "diagnostics_test1_contents.txt", "r"
    ) as text_file:
        contents = text_file.read()

    changes = get_changes(
        DIAGNOSTICS_TEST_ROOT / "diagnostics_test1_content_changes.json"
    )

    actual = []
    with PythonFile(contents, TEMP_DIR) as py_file:
        uri = as_uri(py_file.fullpath)

        initialize_params = copy.deepcopy(VSCODE_DEFAULT_INITIALIZE)
        initialize_params["workspaceFolders"] = [
            {"uri": as_uri(TEMP_DIR), "name": "jedi_lsp_test"}
        ]
        initialize_params["initializationOptions"]["diagnostics"] = {
            "enable": True,
            "didOpen": False,
            "didSave": False,
            "didChange": True,
        }

        with session.LspSession() as ls_session:
            ls_session.initialize(initialize_params)
            done = Event()

            def _handler(params):
                actual.append(params)
                done.set()

            ls_session.set_notification_callback(
                session.PUBLISH_DIAGNOSTICS, _handler
            )

            ls_session.notify_did_open(
                {
                    "textDocument": {
                        "uri": uri,
                        "languageId": "python",
                        "version": 1,
                        "text": contents,
                    }
                }
            )

            # ensure the document is loaded
            symbols = ls_session.text_document_symbol(
                {"textDocument": {"uri": uri}}
            )
            assert len(symbols) > 0

            # At this point there should be no published diagnostics
            assert_that(actual, is_([]))

            # Introduce a syntax error and save the file
            contents = contents.replace("1 == 1", "1 === 1")
            with open(py_file.fullpath, "w") as pyf:
                pyf.write(contents)

            # Reset waiting event just in case a diagnostic was received
            done.clear()

            # Send changes to LS
            version = 2
            for change in changes:
                change["textDocument"] = {"uri": uri, "version": version}
                version = version + 1
                ls_session.notify_did_change(change)

            # ensure the document is loaded
            symbols = ls_session.text_document_symbol(
                {"textDocument": {"uri": uri}}
            )
            assert len(symbols) > 0

            # wait for a second to receive all notifications
            done.wait(1.1)

        # Diagnostics look a little different on Windows.
        filename = (
            as_uri(py_file.fullpath)
            if platform.system() == "Windows"
            else py_file.basename
        )

        expected = [
            {
                "uri": uri,
                "diagnostics": [
                    {
                        "range": {
                            "start": {"line": 5, "character": 15},
                            "end": {"line": 5, "character": 16},
                        },
                        "message": f"SyntaxError: invalid syntax ({filename}, line 6)",
                        "severity": 1,
                        "source": "compile",
                    }
                ],
            }
        ]
    assert_that(actual, is_(expected))


def test_publish_diagnostics_on_save():
    """Tests publish diagnostics on save."""
    with open(
        DIAGNOSTICS_TEST_ROOT / "diagnostics_test1_contents.txt", "r"
    ) as text_file:
        contents = text_file.read()

    changes = get_changes(
        DIAGNOSTICS_TEST_ROOT / "diagnostics_test1_content_changes.json"
    )

    actual = []
    with PythonFile(contents, TEMP_DIR) as py_file:
        uri = as_uri(py_file.fullpath)

        initialize_params = copy.deepcopy(VSCODE_DEFAULT_INITIALIZE)
        initialize_params["workspaceFolders"] = [
            {"uri": as_uri(TEMP_DIR), "name": "jedi_lsp_test"}
        ]
        initialize_params["initializationOptions"]["diagnostics"] = {
            "enable": True,
            "didOpen": False,
            "didSave": True,
            "didChange": False,
        }

        with session.LspSession() as ls_session:
            ls_session.initialize(initialize_params)
            done = Event()

            def _handler(params):
                actual.append(params)
                done.set()

            ls_session.set_notification_callback(
                session.PUBLISH_DIAGNOSTICS, _handler
            )

            ls_session.notify_did_open(
                {
                    "textDocument": {
                        "uri": uri,
                        "languageId": "python",
                        "version": 1,
                        "text": contents,
                    }
                }
            )

            # ensure the document is loaded
            symbols = ls_session.text_document_symbol(
                {"textDocument": {"uri": uri}}
            )
            assert len(symbols) > 0

            # At this point there should be no published diagnostics
            assert_that(actual, is_([]))

            # Introduce a syntax error and save the file
            contents = contents.replace("1 == 1", "1 === 1")
            with open(py_file.fullpath, "w") as pyf:
                pyf.write(contents)

            # Reset waiting event just in case a diagnostic was received
            done.clear()

            # Send changes to LS
            version = 2
            for change in changes:
                change["textDocument"] = {"uri": uri, "version": version}
                version = version + 1
                ls_session.notify_did_change(change)

            # ensure the document is loaded
            symbols = ls_session.text_document_symbol(
                {"textDocument": {"uri": uri}}
            )
            assert len(symbols) > 0

            # At this point there should be no published diagnostics
            assert_that(actual, is_([]))

            # Reset waiting event just in case a diagnostic was received
            done.clear()

            ls_session.notify_did_save(
                {
                    "textDocument": {
                        "uri": uri,
                        "version": version,
                    }
                }
            )

            # wait for a second to receive all notifications
            done.wait(1.1)

        # Diagnostics look a little different on Windows.
        filename = (
            as_uri(py_file.fullpath)
            if platform.system() == "Windows"
            else py_file.basename
        )

        expected = [
            {
                "uri": uri,
                "diagnostics": [
                    {
                        "range": {
                            "start": {"line": 5, "character": 15},
                            "end": {"line": 5, "character": 16},
                        },
                        "message": f"SyntaxError: invalid syntax ({filename}, line 6)",
                        "severity": 1,
                        "source": "compile",
                    }
                ],
            }
        ]
    assert_that(actual, is_(expected))
