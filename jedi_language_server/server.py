"""Jedi Language Server

Creates the language server constant and wraps "features" with it.

Official language server spec:
    https://microsoft.github.io/language-server-protocol/specification
"""

import itertools
from typing import Dict, List, Optional, Union

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
    MarkupContent,
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
from .initialize_params_parser import InitializeParamsParser
from .type_map import get_lsp_completion_type

# pylint: disable=line-too-long


class JediLanguageServerProtocol(LanguageServerProtocol):
    """Override some built-in functions"""

    def bf_initialize(self, params: InitializeParams) -> InitializeResult:
        """Override built-in initialization

        Here, we can conditionally register functions to features based on
        client capabilities and initializationOptions.
        """
        server: "JediLanguageServer" = self._server
        ip = server.initialize_params  # pylint: disable=invalid-name
        ip.set_initialize_params(params)
        if ip.initializationOptions_diagnostics_enable:
            if ip.initializationOptions_diagnostics_didOpen:
                SERVER.feature(TEXT_DOCUMENT_DID_OPEN)(did_open)
            if ip.initializationOptions_diagnostics_didChange:
                SERVER.feature(TEXT_DOCUMENT_DID_CHANGE)(did_change)
            if ip.initializationOptions_diagnostics_didSave:
                SERVER.feature(TEXT_DOCUMENT_DID_SAVE)(did_save)
        return super().bf_initialize(params)


class JediLanguageServer(LanguageServer):
    """Jedi language server

    :attr initialize_params: initialized in bf_initialize from the protocol_cls
    """

    def __init__(self, *args, **kwargs):
        self.initialize_params = InitializeParamsParser()
        super().__init__(*args, **kwargs)


SERVER = JediLanguageServer(protocol_cls=JediLanguageServerProtocol)


# Server capabilities


@SERVER.feature(COMPLETION, trigger_characters=[".", "'", '"'])
def completion(
    server: JediLanguageServer, params: CompletionParams
) -> CompletionList:
    """Returns completion items"""
    jedi_script = jedi_utils.script(server.workspace, params.textDocument.uri)
    jedi_lines = jedi_utils.line_column(params.position)
    completions = jedi_script.complete(**jedi_lines)
    char = pygls_utils.char_before_cursor(
        document=server.workspace.get_document(params.textDocument.uri),
        position=params.position,
    )
    markup_preferred = (
        server.initialize_params.initializationOptions_markupKindPreferred
    )
    markup_supported = (
        server.initialize_params.capabilities_textDocument_completion_completionItem_documentationFormat
    )
    markup_kind = (
        markup_preferred
        if markup_preferred in markup_supported
        else markup_supported[0]
    )
    return CompletionList(
        is_incomplete=False,
        items=[
            CompletionItem(
                label=completion.name,
                kind=get_lsp_completion_type(completion.type),
                detail=completion.description,
                documentation=MarkupContent(
                    kind=markup_kind, value=completion.docstring()
                ),
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
    server: JediLanguageServer, params: TextDocumentPositionParams
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
    server: JediLanguageServer, params: TextDocumentPositionParams
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
    server: JediLanguageServer, params: TextDocumentPositionParams
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
def hover(
    server: JediLanguageServer, params: TextDocumentPositionParams
) -> Optional[Hover]:
    """Support Hover"""
    jedi_script = jedi_utils.script(server.workspace, params.textDocument.uri)
    jedi_lines = jedi_utils.line_column(params.position)
    for name in jedi_script.help(**jedi_lines):
        docstring = name.docstring()
        if not docstring:
            continue
        markup_preferred = (
            server.initialize_params.initializationOptions_markupKindPreferred
        )
        markup_supported = (
            server.initialize_params.capabilities_textDocument_hover_contentFormat
        )
        markup_kind = (
            markup_preferred
            if markup_preferred in markup_supported
            else markup_supported[0]
        )
        contents = MarkupContent(kind=markup_kind, value=docstring)
        document = server.workspace.get_document(params.textDocument.uri)
        _range = pygls_utils.current_word_range(document, params.position)
        return Hover(contents=contents, range=_range)
    return None


@SERVER.feature(REFERENCES)
def references(
    server: JediLanguageServer, params: TextDocumentPositionParams
) -> List[Location]:
    """Obtain all references to text"""
    jedi_script = jedi_utils.script(server.workspace, params.textDocument.uri)
    jedi_lines = jedi_utils.line_column(params.position)
    names = jedi_script.get_references(**jedi_lines)
    return [jedi_utils.lsp_location(name) for name in names]


@SERVER.feature(RENAME)
def rename(
    server: JediLanguageServer, params: RenameParams
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


@SERVER.feature(DOCUMENT_SYMBOL)
def document_symbol(
    server: JediLanguageServer, params: DocumentSymbolParams
) -> Union[List[DocumentSymbol], List[SymbolInformation]]:
    """Document Python document symbols, hierarchically"""
    jedi_script = jedi_utils.script(server.workspace, params.textDocument.uri)
    names = jedi_script.get_names(all_scopes=True, definitions=True)
    if (
        server.initialize_params.capabilities_textDocument_documentSymbol_hierarchicalDocumentSymbolSupport
    ):
        return jedi_utils.lsp_document_symbols(names)
    return [jedi_utils.lsp_symbol_information(name) for name in names]


@SERVER.feature(WORKSPACE_SYMBOL)
def workspace_symbol(
    server: JediLanguageServer, params: WorkspaceSymbolParams
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
def _publish_diagnostics(server: JediLanguageServer, uri: str):
    """Helper function to publish diagnostics for a file"""
    jedi_script = jedi_utils.script(server.workspace, uri)
    errors = jedi_script.get_syntax_errors()
    diagnostics = [jedi_utils.lsp_diagnostic(error) for error in errors]
    server.publish_diagnostics(uri, diagnostics)


# TEXT_DOCUMENT_DID_SAVE
def did_save(server: JediLanguageServer, params: DidSaveTextDocumentParams):
    """Actions run on textDocument/didSave"""
    _publish_diagnostics(server, params.textDocument.uri)


# TEXT_DOCUMENT_DID_CHANGE
def did_change(
    server: JediLanguageServer, params: DidChangeTextDocumentParams
):
    """Actions run on textDocument/didChange"""
    _publish_diagnostics(server, params.textDocument.uri)


# TEXT_DOCUMENT_DID_OPEN
def did_open(server: JediLanguageServer, params: DidOpenTextDocumentParams):
    """Actions run on textDocument/didOpen"""
    _publish_diagnostics(server, params.textDocument.uri)
