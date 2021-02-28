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
        self._server_initialized = Event()
        self._sub = None
        self._writer = None
        self._reader = None
        self._endpoint = None

    def __enter__(self):
        self._sub = subprocess.Popen(
            [
                sys.executable,
                "-c",
                (
                    "import sys;"
                    + "from jedi_language_server.cli import cli;"
                    + "sys.exit(cli())"
                ),
            ],
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE,
            bufsize=0,
            cwd=self.cwd,
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
        self.initialize()
        self._server_initialized.wait()
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

        def _after_initialize(fut):
            if process_server_capabilities:
                process_server_capabilities(fut.result())
            self.initialized()
            self._server_initialized.set()

        self._send_request(
            "initialize",
            params=(
                initialize_params
                if initialize_params is not None
                else defaults.VSCODE_DEFAULT_INITIALIZE
            ),
            handle_response=_after_initialize,
        )

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
