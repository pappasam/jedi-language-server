"""Provides LSP session helpers for testing."""

import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from threading import Event

from pyls_jsonrpc.dispatchers import MethodDispatcher
from pyls_jsonrpc.endpoint import Endpoint
from pyls_jsonrpc.streams import JsonRpcStreamReader, JsonRpcStreamWriter

from tests.lsp_test_client import defaults

LSP_EXIT_TIMEOUT = 5000


class LspSession(MethodDispatcher):
    """Send and Receive messages over LSP as a test LS Client."""

    def __init__(self, cwd=None):
        self.cwd = cwd if cwd else os.getcwd()
        self._thread_executor = ThreadPoolExecutor()
        self._sub = None
        self._writer = None
        self._reader = None
        self._endpoint = None

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
        self._endpoint = Endpoint(self, self._writer.write)
        self._thread_executor.submit(
            self._reader.listen, self._endpoint.consume
        )
        return self

    def __exit__(self, typ, value, _tb):
        self.shutdown(True)
        try:
            self._sub.terminate()
        except Exception:  # pylint:disable=broad-except
            pass
        self._endpoint.shutdown()
        self._thread_executor.shutdown()

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

    def text_document_definition(self, definition_params):
        """Sends text document defintion request to LSP server."""
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

    def _send_request(
        self, name, params=None, handle_response=lambda f: f.done()
    ):
        """Sends {name} request to the LSP server."""
        fut = self._endpoint.request(name, params)
        fut.add_done_callback(handle_response)
        return fut
