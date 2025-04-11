"""Provides LSP session helpers for testing."""

import json
import os
import subprocess
import sys
from concurrent.futures import Future, ThreadPoolExecutor
from threading import Event

from pylsp_jsonrpc.dispatchers import MethodDispatcher
from pylsp_jsonrpc.endpoint import Endpoint
from pylsp_jsonrpc.streams import JsonRpcStreamReader, JsonRpcStreamWriter

from tests.lsp_test_client import defaults
from tests.lsp_test_client.utils import as_uri

LSP_EXIT_TIMEOUT = 5000


PUBLISH_DIAGNOSTICS = "textDocument/publishDiagnostics"
WINDOW_LOG_MESSAGE = "window/logMessage"
WINDOW_SHOW_MESSAGE = "window/showMessage"


class LspSession(MethodDispatcher):
    """Send and Receive messages over LSP as a test LS Client."""

    def __init__(self, cwd=None):
        self.cwd = cwd if cwd else os.getcwd()
        self._thread_pool = ThreadPoolExecutor()
        self._sub = None
        self._writer = None
        self._reader = None
        self._endpoint = None
        self._notification_callbacks = {}

    def __enter__(self):
        """Context manager entrypoint.

        shell=True needed for pytest-cov to work in subprocess.
        """
        self._sub = subprocess.Popen(
            [
                sys.executable,
                os.path.join(os.path.dirname(__file__), "lsp_run.py"),
            ],
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            bufsize=0,
            cwd=self.cwd,
            env=os.environ,
            shell="WITH_COVERAGE" in os.environ,
        )

        self._writer = JsonRpcStreamWriter(
            os.fdopen(self._sub.stdin.fileno(), "wb")
        )
        self._reader = JsonRpcStreamReader(
            os.fdopen(self._sub.stdout.fileno(), "rb")
        )

        dispatcher = {
            PUBLISH_DIAGNOSTICS: self._publish_diagnostics,
            WINDOW_SHOW_MESSAGE: self._window_show_message,
            WINDOW_LOG_MESSAGE: self._window_log_message,
        }
        self._endpoint = Endpoint(dispatcher, self._writer.write)
        self._thread_pool.submit(self._reader.listen, self._endpoint.consume)

        self._last_cell_id = 0
        return self

    def __exit__(self, typ, value, _tb):
        self.shutdown(True)
        try:
            self._sub.terminate()
        except Exception:
            pass
        self._endpoint.shutdown()
        self._thread_pool.shutdown()

    def initialize(
        self,
        initialize_params=None,
        process_server_capabilities=None,
    ):
        """Sends the initialize request to LSP server."""
        server_initialized = Event()

        def _after_initialize(fut):
            if process_server_capabilities:
                process_server_capabilities(fut.result())
            self.initialized()
            server_initialized.set()

        self._send_request(
            "initialize",
            params=(
                initialize_params
                if initialize_params is not None
                else defaults.VSCODE_DEFAULT_INITIALIZE
            ),
            handle_response=_after_initialize,
        )

        server_initialized.wait()

    def initialized(self, initialized_params=None):
        """Sends the initialized notification to LSP server."""
        if initialized_params is None:
            initialized_params = {}
        self._endpoint.notify("initialized", initialized_params)

    def shutdown(self, should_exit, exit_timeout=LSP_EXIT_TIMEOUT):
        """Sends the shutdown request to LSP server."""

        def _after_shutdown(_):
            if should_exit:
                self.exit_lsp(exit_timeout)

        self._send_request("shutdown", handle_response=_after_shutdown)

    def exit_lsp(self, exit_timeout=LSP_EXIT_TIMEOUT):
        """Handles LSP server process exit."""
        self._endpoint.notify("exit")
        assert self._sub.wait(exit_timeout) == 0

    def text_document_completion(self, completion_params):
        """Sends text document completion request to LSP server."""
        fut = self._send_request(
            "textDocument/completion", params=completion_params
        )
        return fut.result()

    def text_document_rename(self, rename_params):
        """Sends text document rename request to LSP server."""
        fut = self._send_request("textDocument/rename", params=rename_params)
        return fut.result()

    def text_document_code_action(self, code_action_params):
        """Sends text document code action request to LSP server."""
        fut = self._send_request(
            "textDocument/codeAction", params=code_action_params
        )
        return fut.result()

    def text_document_hover(self, hover_params):
        """Sends text document hover request to LSP server."""
        fut = self._send_request("textDocument/hover", params=hover_params)
        return fut.result()

    def text_document_signature_help(self, signature_help_params):
        """Sends text document hover request to LSP server."""
        fut = self._send_request(
            "textDocument/signatureHelp", params=signature_help_params
        )
        return fut.result()

    def text_document_declaration(self, declaration_params):
        """Sends text document declaration request to LSP server."""
        fut = self._send_request(
            "textDocument/declaration", params=declaration_params
        )
        return fut.result()

    def text_document_definition(self, definition_params):
        """Sends text document definition request to LSP server."""
        fut = self._send_request(
            "textDocument/definition", params=definition_params
        )
        return fut.result()

    def text_document_symbol(self, document_symbol_params):
        """Sends text document symbol request to LSP server."""
        fut = self._send_request(
            "textDocument/documentSymbol", params=document_symbol_params
        )
        return fut.result()

    def text_document_highlight(self, document_highlight_params):
        """Sends text document highlight request to LSP server."""
        fut = self._send_request(
            "textDocument/documentHighlight", params=document_highlight_params
        )
        return fut.result()

    def text_document_references(self, references_params):
        """Sends text document references request to LSP server."""
        fut = self._send_request(
            "textDocument/references", params=references_params
        )
        return fut.result()

    def text_doc_semantic_tokens_full(self, semantic_tokens_params):
        """Sends text document semantic tokens full request to LSP server."""
        fut = self._send_request(
            "textDocument/semanticTokens/full", params=semantic_tokens_params
        )
        return fut.result()

    def text_doc_semantic_tokens_range(self, semantic_tokens_range_params):
        """Sends text document semantic tokens range request to LSP server."""
        fut = self._send_request(
            "textDocument/semanticTokens/range",
            params=semantic_tokens_range_params,
        )
        return fut.result()

    def workspace_symbol(self, workspace_symbol_params):
        """Sends workspace symbol request to LSP server."""
        fut = self._send_request(
            "workspace/symbol", params=workspace_symbol_params
        )
        return fut.result()

    def completion_item_resolve(self, resolve_params):
        """Sends completion item resolve request to LSP server."""
        fut = self._send_request(
            "completionItem/resolve", params=resolve_params
        )
        return fut.result()

    def notify_did_change_text_document(self, did_change_params):
        """Sends did change text document notification to LSP Server."""
        self._send_notification(
            "textDocument/didChange", params=did_change_params
        )

    def notify_did_save_text_document(self, did_save_params):
        """Sends did save text document notification to LSP Server."""
        self._send_notification("textDocument/didSave", params=did_save_params)

    def notify_did_open_text_document(self, did_open_params):
        """Sends did open text document notification to LSP Server."""
        self._send_notification("textDocument/didOpen", params=did_open_params)

    def notify_did_close_text_document(self, did_close_params):
        """Sends did close text document notification to LSP Server."""
        self._send_notification(
            "textDocument/didClose", params=did_close_params
        )

    def notify_did_change_notebook_document(self, did_change_params):
        """Sends did change notebook document notification to LSP Server."""
        self._send_notification(
            "notebookDocument/didChange", params=did_change_params
        )

    def notify_did_save_notebook_document(self, did_save_params):
        """Sends did save notebook document notification to LSP Server."""
        self._send_notification(
            "notebookDocument/didSave", params=did_save_params
        )

    def notify_did_open_notebook_document(self, did_open_params):
        """Sends did open notebook document notification to LSP Server."""
        self._send_notification(
            "notebookDocument/didOpen", params=did_open_params
        )

    def notify_did_close_notebook_document(self, did_close_params):
        """Sends did close notebook document notification to LSP Server."""
        self._send_notification(
            "notebookDocument/didClose", params=did_close_params
        )

    def open_notebook_document(self, path):
        """Opens a notebook document on the LSP Server."""
        # Construct did_open_notebook_document params from the notebook file.
        notebook = json.loads(path.read_text("utf-8"))
        uri = as_uri(path)
        lsp_cells = []
        lsp_cell_text_documents = []
        for cell in notebook["cells"]:
            self._last_cell_id += 1
            cell_uri = f"{uri}#{self._last_cell_id}"
            lsp_cells.append(
                {
                    "kind": 2 if cell["cell_type"] == "code" else 1,
                    "document": cell_uri,
                    "metadata": {"metadata": cell["metadata"]},
                }
            )
            lsp_cell_text_documents.append(
                {
                    "uri": cell_uri,
                    "languageId": "python",
                    "version": 1,
                    "text": "".join(cell["source"]),
                }
            )

        # Notify the server.
        self.notify_did_open_notebook_document(
            {
                "notebookDocument": {
                    "uri": uri,
                    "notebookType": "jupyter-notebook",
                    "languageId": "python",
                    "version": 1,
                    "cells": lsp_cells,
                },
                "cellTextDocuments": lsp_cell_text_documents,
            }
        )

        # Return the generated cell URIs.
        return [cell["document"] for cell in lsp_cells]

    def set_notification_callback(self, notification_name, callback):
        """Set custom LS notification handler."""
        self._notification_callbacks[notification_name] = callback

    def get_notification_callback(self, notification_name):
        """Gets callback if set or default callback for a given LS notification."""
        try:
            return self._notification_callbacks[notification_name]
        except KeyError:

            def _default_handler(_params):
                """Default notification handler."""

            return _default_handler

    def _publish_diagnostics(self, publish_diagnostics_params):
        """Internal handler for text document publish diagnostics."""
        return self._handle_notification(
            PUBLISH_DIAGNOSTICS, publish_diagnostics_params
        )

    def _window_log_message(self, window_log_message_params):
        """Internal handler for window log message."""
        return self._handle_notification(
            WINDOW_LOG_MESSAGE, window_log_message_params
        )

    def _window_show_message(self, window_show_message_params):
        """Internal handler for window show message."""
        return self._handle_notification(
            WINDOW_SHOW_MESSAGE, window_show_message_params
        )

    def _handle_notification(self, notification_name, params):
        """Internal handler for notifications."""
        fut = Future()

        def _handler():
            callback = self.get_notification_callback(notification_name)
            callback(params)
            fut.set_result(None)

        self._thread_pool.submit(_handler)
        return fut

    def _send_request(
        self, name, params=None, handle_response=lambda f: f.done()
    ):
        """Sends {name} request to the LSP server."""
        fut = self._endpoint.request(name, params)
        fut.add_done_callback(handle_response)
        return fut

    def _send_notification(self, name, params=None):
        """Sends {name} notification to the LSP server."""
        self._endpoint.notify(name, params)
