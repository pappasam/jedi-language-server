"""Jedi Language Server

Creates the language server constant and wraps "features" with it.

Official language server spec:
    https://microsoft.github.io/language-server-protocol/specification
"""

import itertools
from typing import Dict, List, Optional

from pygls.features import (
    COMPLETION,
    DEFINITION,
    DOCUMENT_HIGHLIGHT,
    DOCUMENT_SYMBOL,
    HOVER,
    REFERENCES,
    RENAME,
    SIGNATURE_HELP,
    TEXT_DOCUMENT_DID_CHANGE,
    TEXT_DOCUMENT_DID_OPEN,
    TEXT_DOCUMENT_DID_SAVE,
    WORKSPACE_SYMBOL,
)
from pygls.protocol import LanguageServerProtocol
from pygls.server import LanguageServer
from pygls.types import (
    CompletionItem,
    CompletionList,
    CompletionParams,
    DidChangeTextDocumentParams,
    DidOpenTextDocumentParams,
    DidSaveTextDocumentParams,
    DocumentHighlight,
    DocumentSymbol,
    DocumentSymbolParams,
    Hover,
    InitializeParams,
    InitializeResult,
    Location,
    ParameterInformation,
    RenameParams,
    SignatureHelp,
    SignatureInformation,
    SymbolInformation,
    TextDocumentPositionParams,
    TextEdit,
    WorkspaceEdit,
    WorkspaceSymbolParams,
)

from . import jedi_utils, pygls_utils
from .pygls_utils import rgetattr
from .type_map import get_lsp_completion_type


class JediLanguageServerProtocol(LanguageServerProtocol):
    """Override some built-in functions"""

    def bf_initialize(self, params: InitializeParams) -> InitializeResult:
        """Override built-in initialization

        Here, we can conditionally register functions to features based on
        client capabilities and initializationOptions.
        """
        server: "LanguageServer" = self._server
        text_document_capabilities = params.capabilities.textDocument
        if rgetattr(
            text_document_capabilities,
            "documentSymbol.hierarchicalDocumentSymbolSupport",
        ):
            server.feature(DOCUMENT_SYMBOL)(document_symbol)
        else:
            server.feature(DOCUMENT_SYMBOL)(document_symbol_legacy)
        init = params.initializationOptions
        if rgetattr(init, "diagnostics.enable", True):
            if rgetattr(init, "diagnostics.didOpen", True):
                SERVER.feature(TEXT_DOCUMENT_DID_OPEN)(did_open)
            if rgetattr(init, "diagnostics.didChange", True):
                SERVER.feature(TEXT_DOCUMENT_DID_CHANGE)(did_change)
            if rgetattr(init, "diagnostics.didSave", True):
                SERVER.feature(TEXT_DOCUMENT_DID_SAVE)(did_save)
        return super().bf_initialize(params)


SERVER = LanguageServer(protocol_cls=JediLanguageServerProtocol)


# Static capabilities, no configuration


@SERVER.feature(COMPLETION, trigger_characters=[".", "'", '"'])
def completion(
    server: LanguageServer, params: CompletionParams
) -> CompletionList:
    """Returns completion items"""
    jedi_script = jedi_utils.script(server.workspace, params.textDocument.uri)
    jedi_lines = jedi_utils.line_column(params.position)
    completions = jedi_script.complete(**jedi_lines)
    char = pygls_utils.char_before_cursor(
        document=server.workspace.get_document(params.textDocument.uri),
        position=params.position,
    )
    return CompletionList(
        is_incomplete=False,
        items=[
            CompletionItem(
                label=completion.name,
                kind=get_lsp_completion_type(completion.type),
                detail=completion.description,
                documentation=completion.docstring(),
                sort_text=jedi_utils.complete_sort_name(completion),
                insert_text=pygls_utils.clean_completion_name(
                    completion.name, char
                ),
            )
            for completion in completions
        ],
    )


@SERVER.feature(SIGNATURE_HELP, trigger_characters=["(", ","])
def signature_help(
    server: LanguageServer, params: TextDocumentPositionParams
) -> SignatureHelp:
    """Returns signature help"""
    jedi_script = jedi_utils.script(server.workspace, params.textDocument.uri)
    jedi_lines = jedi_utils.line_column(params.position)
    signatures = jedi_script.get_signatures(**jedi_lines)
    return SignatureHelp(
        signatures=[
            SignatureInformation(
                label=signature.to_string(),
                documentation=None,
                parameters=[
                    ParameterInformation(
                        label=info.to_string(), documentation=None
                    )
                    for info in signature.params
                ],
            )
            for signature in signatures
        ],
        active_signature=0,
        active_parameter=signatures[0].index if signatures else 0,
    )


@SERVER.feature(DEFINITION)
def definition(
    server: LanguageServer, params: TextDocumentPositionParams
) -> List[Location]:
    """Support Goto Definition"""
    jedi_script = jedi_utils.script(server.workspace, params.textDocument.uri)
    jedi_lines = jedi_utils.line_column(params.position)
    names = jedi_script.goto(
        follow_imports=True, follow_builtin_imports=True, **jedi_lines,
    )
    return [jedi_utils.lsp_location(name) for name in names]


@SERVER.feature(DOCUMENT_HIGHLIGHT)
def highlight(
    server: LanguageServer, params: TextDocumentPositionParams
) -> List[DocumentHighlight]:
    """Support document highlight request

    This function is called frequently, so we minimize the number of expensive
    calls. These calls are:

    1. Getting assignment of current symbol (script.goto)
    2. Getting all names in the current script (script.get_names)

    Finally, we only return names if there are more than 1. Otherwise, we don't
    want to highlight anything.
    """
    document = server.workspace.get_document(params.textDocument.uri)
    word = document.word_at_position(params.position)
    jedi_script = jedi_utils.script(server.workspace, params.textDocument.uri)
    jedi_lines = jedi_utils.line_column(params.position)
    jedi_definition_names = jedi_script.goto(
        follow_imports=False, follow_builtin_imports=False, **jedi_lines,
    )
    if not jedi_definition_names:
        return []
    current_definition_name = jedi_definition_names[0]
    jedi_context = jedi_script.get_context(**jedi_lines)
    current_full_name = (
        jedi_context.full_name
        if jedi_context.name == word
        else f"{jedi_context.full_name}.{word}"
    )
    highlight_names = [
        DocumentHighlight(jedi_utils.lsp_range(name))
        for name in jedi_script.get_names(
            all_scopes=True, definitions=True, references=True
        )
        if name.full_name == current_full_name
        or jedi_utils.compare_names(name, current_definition_name)
    ]
    return highlight_names if len(highlight_names) > 1 else []


@SERVER.feature(HOVER)
def hover(server: LanguageServer, params: TextDocumentPositionParams) -> Hover:
    """Support Hover"""
    jedi_script = jedi_utils.script(server.workspace, params.textDocument.uri)
    jedi_lines = jedi_utils.line_column(params.position)
    jedi_docstrings = (n.docstring() for n in jedi_script.help(**jedi_lines))
    names = [name for name in jedi_docstrings if name]
    return Hover(contents=names if names else "jedi: no help docs found")


@SERVER.feature(REFERENCES)
def references(
    server: LanguageServer, params: TextDocumentPositionParams
) -> List[Location]:
    """Obtain all references to text"""
    jedi_script = jedi_utils.script(server.workspace, params.textDocument.uri)
    jedi_lines = jedi_utils.line_column(params.position)
    names = jedi_script.get_references(**jedi_lines)
    return [jedi_utils.lsp_location(name) for name in names]


@SERVER.feature(RENAME)
def rename(
    server: LanguageServer, params: RenameParams
) -> Optional[WorkspaceEdit]:
    """Rename a symbol across a workspace"""
    jedi_script = jedi_utils.script(server.workspace, params.textDocument.uri)
    jedi_lines = jedi_utils.line_column(params.position)
    names = jedi_script.get_references(**jedi_lines)
    if not names:
        return None
    locations = [jedi_utils.lsp_location(name) for name in names]
    changes: Dict[str, List[TextEdit]] = {}
    for location in locations:
        text_edit = TextEdit(location.range, new_text=params.newName)
        if location.uri not in changes:
            changes[location.uri] = [text_edit]
        else:
            changes[location.uri].append(text_edit)
    return WorkspaceEdit(changes=changes)


@SERVER.feature(WORKSPACE_SYMBOL)
def workspace_symbol(
    server: LanguageServer, params: WorkspaceSymbolParams
) -> List[SymbolInformation]:
    """Document Python workspace symbols"""
    jedi_project = jedi_utils.project(server.workspace)
    if params.query.strip() == "":
        return []
    names = jedi_project.search(params.query)
    return [
        jedi_utils.lsp_symbol_information(name)
        for name in itertools.islice(names, 20)
    ]


# Static capability or initializeOptions functions that rely on a specific
# client capability or user configuration. These are associated with
# JediLanguageServer within JediLanguageServerProtocol.bf_initialize

# DOCUMENT_SYMBOL: legacy
def document_symbol_legacy(
    server: LanguageServer, params: DocumentSymbolParams
) -> List[SymbolInformation]:
    """Document Python document symbols"""
    jedi_script = jedi_utils.script(server.workspace, params.textDocument.uri)
    names = jedi_script.get_names()
    return [jedi_utils.lsp_symbol_information(name) for name in names]


# DOCUMENT_SYMBOL: new
def document_symbol(
    server: LanguageServer, params: DocumentSymbolParams
) -> List[DocumentSymbol]:
    """Document Python document symbols, hierarchically"""
    jedi_script = jedi_utils.script(server.workspace, params.textDocument.uri)
    names = jedi_script.get_names(all_scopes=True, definitions=True)
    return jedi_utils.lsp_document_symbols(names)


def _publish_diagnostics(server: LanguageServer, uri: str):
    """Helper function to publish diagnostics for a file"""
    jedi_script = jedi_utils.script(server.workspace, uri)
    errors = jedi_script.get_syntax_errors()
    diagnostics = [jedi_utils.lsp_diagnostic(error) for error in errors]
    server.publish_diagnostics(uri, diagnostics)


# TEXT_DOCUMENT_DID_SAVE
def did_save(server: LanguageServer, params: DidSaveTextDocumentParams):
    """Actions run on textDocument/didSave"""
    _publish_diagnostics(server, params.textDocument.uri)


# TEXT_DOCUMENT_DID_CHANGE
def did_change(server: LanguageServer, params: DidChangeTextDocumentParams):
    """Actions run on textDocument/didChange"""
    _publish_diagnostics(server, params.textDocument.uri)


# TEXT_DOCUMENT_DID_OPEN
def did_open(server: LanguageServer, params: DidOpenTextDocumentParams):
    """Actions run on textDocument/didOpen"""
    _publish_diagnostics(server, params.textDocument.uri)
