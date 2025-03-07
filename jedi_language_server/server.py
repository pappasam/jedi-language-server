"""Jedi Language Server.

Creates the language server constant and wraps "features" with it.

Official language server spec:
    https://microsoft.github.io/language-server-protocol/specification
"""

import itertools
from typing import Any, Callable, List, Optional, TypeVar, Union

import cattrs
from jedi import Project, __version__
from lsprotocol.types import (
    COMPLETION_ITEM_RESOLVE,
    INITIALIZE,
    NOTEBOOK_DOCUMENT_DID_CHANGE,
    NOTEBOOK_DOCUMENT_DID_CLOSE,
    NOTEBOOK_DOCUMENT_DID_OPEN,
    NOTEBOOK_DOCUMENT_DID_SAVE,
    TEXT_DOCUMENT_CODE_ACTION,
    TEXT_DOCUMENT_COMPLETION,
    TEXT_DOCUMENT_DECLARATION,
    TEXT_DOCUMENT_DEFINITION,
    TEXT_DOCUMENT_DID_CHANGE,
    TEXT_DOCUMENT_DID_CLOSE,
    TEXT_DOCUMENT_DID_OPEN,
    TEXT_DOCUMENT_DID_SAVE,
    TEXT_DOCUMENT_DOCUMENT_HIGHLIGHT,
    TEXT_DOCUMENT_DOCUMENT_SYMBOL,
    TEXT_DOCUMENT_HOVER,
    TEXT_DOCUMENT_REFERENCES,
    TEXT_DOCUMENT_RENAME,
    TEXT_DOCUMENT_SIGNATURE_HELP,
    TEXT_DOCUMENT_TYPE_DEFINITION,
    WORKSPACE_DID_CHANGE_CONFIGURATION,
    WORKSPACE_SYMBOL,
    CodeAction,
    CodeActionKind,
    CodeActionOptions,
    CodeActionParams,
    CompletionItem,
    CompletionList,
    CompletionOptions,
    CompletionParams,
    DidChangeConfigurationParams,
    DidChangeTextDocumentParams,
    DidCloseTextDocumentParams,
    DidOpenTextDocumentParams,
    DidSaveTextDocumentParams,
    DocumentHighlight,
    DocumentSymbol,
    DocumentSymbolParams,
    Hover,
    InitializeParams,
    InitializeResult,
    Location,
    MessageType,
    NotebookDocumentSyncOptions,
    NotebookDocumentSyncOptionsNotebookSelectorType2,
    NotebookDocumentSyncOptionsNotebookSelectorType2CellsType,
    RenameParams,
    SignatureHelp,
    SignatureHelpOptions,
    SymbolInformation,
    TextDocumentPositionParams,
    WorkspaceEdit,
    WorkspaceSymbolParams,
)
from pygls.feature_manager import FeatureManager
from pygls.protocol import LanguageServerProtocol, lsp_method
from pygls.server import LanguageServer

from . import (
    jedi_utils,
    server_utils,
)
from .initialization_options import (
    InitializationOptions,
    initialization_options_converter,
)

F = TypeVar("F", bound=Callable)  # type: ignore[type-arg]


class JediLanguageServerProtocol(LanguageServerProtocol):
    """Override some built-in functions."""

    _server: "JediLanguageServer"

    def __init__(self, server: "JediLanguageServer", converter: Any):
        super().__init__(server, converter)  # type: ignore[no-untyped-call]

        self.notebook_fm = FeatureManager(server, converter)  # type: ignore[no-untyped-call]

    @lsp_method(INITIALIZE)
    def lsp_initialize(self, params: InitializeParams) -> InitializeResult:
        """Override built-in initialization.

        Here, we can conditionally register functions to features based
        on client capabilities and initializationOptions.
        """
        server = self._server
        try:
            server.initialization_options = (
                initialization_options_converter.structure(
                    {}
                    if params.initialization_options is None
                    else params.initialization_options,
                    InitializationOptions,
                )
            )
        except cattrs.BaseValidationError as error:
            msg = (
                "Invalid InitializationOptions, using defaults:"
                f" {cattrs.transform_error(error)}"
            )
            server.show_message(msg, msg_type=MessageType.Error)
            server.show_message_log(msg, msg_type=MessageType.Error)
            server.initialization_options = InitializationOptions()

        initialization_options = server.initialization_options
        jedi_utils.set_jedi_settings(initialization_options)

        from . import server_ipynb

        # Configure didOpen, didChange, and didSave
        # currently need to be configured manually
        diagnostics = initialization_options.diagnostics
        did_open_text_document = (
            did_open_text_document_diagnostics
            if diagnostics.enable and diagnostics.did_open
            else did_open_text_document_default
        )
        did_change_text_document = (
            did_change_text_document_diagnostics
            if diagnostics.enable and diagnostics.did_change
            else did_change_text_document_default
        )
        did_save_text_document = (
            did_save_text_document_diagnostics
            if diagnostics.enable and diagnostics.did_save
            else did_save_text_document_default
        )
        did_close_text_document = (
            did_close_text_document_diagnostics
            if diagnostics.enable
            else did_close_text_document_default
        )
        did_open_notebook_document = (
            server_ipynb.did_open_notebook_document_diagnostics
            if diagnostics.enable and diagnostics.did_open
            else server_ipynb.did_open_notebook_document_default
        )
        did_change_notebook_document = (
            server_ipynb.did_change_notebook_document_diagnostics
            if diagnostics.enable and diagnostics.did_change
            else server_ipynb.did_change_notebook_document_default
        )
        did_save_notebook_document = (
            server_ipynb.did_save_notebook_document_diagnostics
            if diagnostics.enable and diagnostics.did_save
            else server_ipynb.did_save_notebook_document_default
        )
        did_close_notebook_document = (
            server_ipynb.did_close_notebook_document_diagnostics
            if diagnostics.enable
            else server_ipynb.did_close_notebook_document_default
        )
        server.feature(TEXT_DOCUMENT_DID_OPEN)(did_open_text_document)
        server.feature(TEXT_DOCUMENT_DID_CHANGE)(did_change_text_document)
        server.feature(TEXT_DOCUMENT_DID_SAVE)(did_save_text_document)
        server.feature(TEXT_DOCUMENT_DID_CLOSE)(did_close_text_document)
        server.feature(NOTEBOOK_DOCUMENT_DID_OPEN)(did_open_notebook_document)
        server.feature(NOTEBOOK_DOCUMENT_DID_CHANGE)(
            did_change_notebook_document
        )
        server.feature(NOTEBOOK_DOCUMENT_DID_SAVE)(did_save_notebook_document)
        server.feature(NOTEBOOK_DOCUMENT_DID_CLOSE)(
            did_close_notebook_document
        )

        if server.initialization_options.hover.enable:
            server.feature(TEXT_DOCUMENT_HOVER)(hover)
            server.notebook_feature(TEXT_DOCUMENT_HOVER)(server_ipynb.hover)

        initialize_result: InitializeResult = super().lsp_initialize(params)
        workspace_options = initialization_options.workspace
        server.project = (
            Project(
                path=server.workspace.root_path,
                environment_path=workspace_options.environment_path,
                added_sys_path=workspace_options.extra_paths,
                smart_sys_path=True,
                load_unsafe_extensions=False,
            )
            if server.workspace.root_path
            else None
        )
        return initialize_result


class JediLanguageServer(LanguageServer):
    """Jedi language server.

    :attr initialization_options: initialized in lsp_initialize from the
        protocol_cls.
    :attr project: a Jedi project. This value is created in
        `JediLanguageServerProtocol.lsp_initialize`.
    """

    initialization_options: InitializationOptions
    lsp: JediLanguageServerProtocol
    project: Optional[Project]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def notebook_feature(
        self, feature_name: str, options: Any = None
    ) -> Callable[[F], F]:
        return self.lsp.notebook_fm.feature(feature_name, options)

    def feature(
        self, feature_name: str, options: Any = None
    ) -> Callable[[F], F]:
        base_decorator = super().feature(feature_name, options)

        def decorator(f):  # type: ignore[no-untyped-def]
            result = base_decorator(f)

            f = self.lsp.fm._features[feature_name]

            # TODO: handle coroutines?
            def wrapped(params):  # type: ignore[no-untyped-def]
                if (
                    hasattr(params, "text_document")
                    and hasattr(params.text_document, "uri")
                    and self.workspace.get_notebook_document(
                        cell_uri=params.text_document.uri
                    )
                    is not None
                    and feature_name in self.lsp.notebook_fm._features
                ):
                    return self.lsp.notebook_fm.features[feature_name](params)

                return f(params)

            self.lsp.fm._features[feature_name] = wrapped

            return result

        return decorator


SERVER = JediLanguageServer(
    name="jedi-language-server",
    version=__version__,
    protocol_cls=JediLanguageServerProtocol,
    # Advertise support for Python notebook cells.
    notebook_document_sync=NotebookDocumentSyncOptions(
        notebook_selector=[
            NotebookDocumentSyncOptionsNotebookSelectorType2(
                cells=[
                    NotebookDocumentSyncOptionsNotebookSelectorType2CellsType(
                        language="python"
                    )
                ]
            )
        ]
    ),
)


# Server capabilities


@SERVER.feature(COMPLETION_ITEM_RESOLVE)
def completion_item_resolve(
    server: JediLanguageServer, params: CompletionItem
) -> CompletionItem:
    """Resolves documentation and detail of given completion item."""
    markup_kind = server_utils._choose_markup(server)
    return jedi_utils.lsp_completion_item_resolve(
        params, markup_kind=markup_kind
    )


@SERVER.feature(
    TEXT_DOCUMENT_COMPLETION,
    CompletionOptions(
        trigger_characters=[".", "'", '"'], resolve_provider=True
    ),
)
def completion(
    server: JediLanguageServer, params: CompletionParams
) -> Optional[CompletionList]:
    """Returns completion items."""
    return server_utils.completion(server, params)


@SERVER.feature(
    TEXT_DOCUMENT_SIGNATURE_HELP,
    SignatureHelpOptions(trigger_characters=["(", ","]),
)
def signature_help(
    server: JediLanguageServer, params: TextDocumentPositionParams
) -> Optional[SignatureHelp]:
    """Returns signature help."""
    return server_utils.signature_help(server, params)


@SERVER.feature(TEXT_DOCUMENT_DECLARATION)
def declaration(
    server: JediLanguageServer, params: TextDocumentPositionParams
) -> Optional[List[Location]]:
    """Support Goto Declaration."""
    return server_utils.declaration(server, params)


@SERVER.feature(TEXT_DOCUMENT_DEFINITION)
def definition(
    server: JediLanguageServer, params: TextDocumentPositionParams
) -> Optional[List[Location]]:
    """Support Goto Definition."""
    return server_utils.definition(server, params)


@SERVER.feature(TEXT_DOCUMENT_TYPE_DEFINITION)
def type_definition(
    server: JediLanguageServer, params: TextDocumentPositionParams
) -> Optional[List[Location]]:
    """Support Goto Type Definition."""
    return server_utils.type_definition(server, params)


@SERVER.feature(TEXT_DOCUMENT_DOCUMENT_HIGHLIGHT)
def highlight(
    server: JediLanguageServer, params: TextDocumentPositionParams
) -> Optional[List[DocumentHighlight]]:
    """Support document highlight request.

    This function is called frequently, so we minimize the number of expensive
    calls. These calls are:

    1. Getting assignment of current symbol (script.goto)
    2. Getting all names in the current script (script.get_names)

    Finally, we only return names if there are more than 1. Otherwise, we don't
    want to highlight anything.
    """
    return server_utils.highlight(server, params)


# Registered with HOVER dynamically
def hover(
    server: JediLanguageServer, params: TextDocumentPositionParams
) -> Optional[Hover]:
    """Support Hover."""
    return server_utils.hover(server, params)


@SERVER.feature(TEXT_DOCUMENT_REFERENCES)
def references(
    server: JediLanguageServer, params: TextDocumentPositionParams
) -> Optional[List[Location]]:
    return server_utils.references(server, params)


@SERVER.feature(TEXT_DOCUMENT_DOCUMENT_SYMBOL)
def document_symbol(
    server: JediLanguageServer, params: DocumentSymbolParams
) -> Optional[Union[List[DocumentSymbol], List[SymbolInformation]]]:
    """Document Python document symbols, hierarchically if possible.

    In Jedi, valid values for `name.type` are:

    - `module`
    - `class`
    - `instance`
    - `function`
    - `param`
    - `path`
    - `keyword`
    - `statement`

    We do some cleaning here. For hierarchical symbols, names from scopes that
    aren't directly accessible with dot notation are removed from display. For
    non-hierarchical symbols, we simply remove `param` symbols. Others are
    included for completeness.
    """
    return server_utils.document_symbol(server, params)


def _ignore_folder(path_check: str, jedi_ignore_folders: List[str]) -> bool:
    """Determines whether there's an ignore folder in the path.

    Intended to be used with the `workspace_symbol` function
    """
    for ignore_folder in jedi_ignore_folders:
        if f"/{ignore_folder}/" in path_check:
            return True
    return False


@SERVER.feature(WORKSPACE_SYMBOL)
def workspace_symbol(
    server: JediLanguageServer, params: WorkspaceSymbolParams
) -> Optional[List[SymbolInformation]]:
    """Document Python workspace symbols.

    Returns up to maxSymbols, or all symbols if maxSymbols is <= 0, ignoring
    the following symbols:

    1. Those that don't have a module_path associated with them (built-ins)
    2. Those that are not rooted in the current workspace.
    3. Those whose folders contain a directory that is ignored (.venv, etc)
    """
    if not server.project:
        return None
    names = server.project.complete_search(params.query)
    workspace_root = server.workspace.root_path
    ignore_folders = (
        server.initialization_options.workspace.symbols.ignore_folders
    )
    unignored_names = (
        name
        for name in names
        if name.module_path is not None
        and str(name.module_path).startswith(workspace_root)
        and not _ignore_folder(str(name.module_path), ignore_folders)
    )
    _symbols = (
        symbol
        for symbol in (
            jedi_utils.lsp_symbol_information(name) for name in unignored_names
        )
        if symbol is not None
    )
    max_symbols = server.initialization_options.workspace.symbols.max_symbols
    symbols = (
        list(itertools.islice(_symbols, max_symbols))
        if max_symbols > 0
        else list(_symbols)
    )
    return symbols if symbols else None


@SERVER.feature(TEXT_DOCUMENT_RENAME)
def rename(
    server: JediLanguageServer, params: RenameParams
) -> Optional[WorkspaceEdit]:
    """Rename a symbol across a workspace."""
    return server_utils.rename(server, params)


@SERVER.feature(
    TEXT_DOCUMENT_CODE_ACTION,
    CodeActionOptions(
        code_action_kinds=[
            CodeActionKind.RefactorInline,
            CodeActionKind.RefactorExtract,
        ],
    ),
)
def code_action(
    server: JediLanguageServer, params: CodeActionParams
) -> Optional[List[CodeAction]]:
    """Get code actions.

    Currently supports:
        1. Inline variable
        2. Extract variable
        3. Extract function
    """
    return server_utils.code_action(server, params)


@SERVER.feature(WORKSPACE_DID_CHANGE_CONFIGURATION)
def did_change_configuration(
    server: JediLanguageServer,
    params: DidChangeConfigurationParams,
) -> None:
    """Implement event for workspace/didChangeConfiguration.

    Currently does nothing, but necessary for pygls. See::
        <https://github.com/pappasam/jedi-language-server/issues/58>
    """


# TEXT_DOCUMENT_DID_SAVE
def did_save_text_document_diagnostics(
    server: JediLanguageServer, params: DidSaveTextDocumentParams
) -> None:
    """Actions run on textDocument/didSave: diagnostics."""
    server_utils.publish_diagnostics(server, params.text_document.uri)


def did_save_text_document_default(
    server: JediLanguageServer,
    params: DidSaveTextDocumentParams,
) -> None:
    """Actions run on textDocument/didSave: default."""


# TEXT_DOCUMENT_DID_CHANGE
def did_change_text_document_diagnostics(
    server: JediLanguageServer, params: DidChangeTextDocumentParams
) -> None:
    """Actions run on textDocument/didChange: diagnostics."""
    server_utils.publish_diagnostics(server, params.text_document.uri)


def did_change_text_document_default(
    server: JediLanguageServer,
    params: DidChangeTextDocumentParams,
) -> None:
    """Actions run on textDocument/didChange: default."""


# TEXT_DOCUMENT_DID_OPEN
def did_open_text_document_diagnostics(
    server: JediLanguageServer, params: DidOpenTextDocumentParams
) -> None:
    """Actions run on textDocument/didOpen: diagnostics."""
    server_utils.publish_diagnostics(server, params.text_document.uri)


def did_open_text_document_default(
    server: JediLanguageServer,
    params: DidOpenTextDocumentParams,
) -> None:
    """Actions run on textDocument/didOpen: default."""


# TEXT_DOCUMENT_DID_CLOSE
def did_close_text_document_diagnostics(
    server: JediLanguageServer, params: DidCloseTextDocumentParams
) -> None:
    """Actions run on textDocument/didClose: diagnostics."""
    server_utils.clear_diagnostics(server, params.text_document.uri)


def did_close_text_document_default(
    server: JediLanguageServer,
    params: DidCloseTextDocumentParams,
) -> None:
    """Actions run on textDocument/didClose: default."""
