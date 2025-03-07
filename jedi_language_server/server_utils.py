from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Union

from jedi.api.refactoring import RefactoringError
from lsprotocol.types import (
    CodeAction,
    CodeActionKind,
    CodeActionParams,
    CompletionList,
    CompletionParams,
    DocumentHighlight,
    DocumentSymbol,
    DocumentSymbolParams,
    Hover,
    Location,
    MarkupContent,
    MarkupKind,
    ParameterInformation,
    RenameParams,
    SignatureHelp,
    SignatureInformation,
    SymbolInformation,
    TextDocumentPositionParams,
    WorkspaceEdit,
)
from pygls.capabilities import get_capability
from pygls.workspace.text_document import TextDocument

from . import jedi_utils, pygls_utils, text_edit_utils

if TYPE_CHECKING:
    from .server import JediLanguageServer


def completion(
    server: JediLanguageServer,
    params: CompletionParams,
    document: Optional[TextDocument] = None,
) -> Optional[CompletionList]:
    if document is None:
        document = server.workspace.get_text_document(params.text_document.uri)
    snippet_disable = server.initialization_options.completion.disable_snippets
    resolve_eagerly = server.initialization_options.completion.resolve_eagerly
    ignore_patterns = server.initialization_options.completion.ignore_patterns
    jedi_script = jedi_utils.script(server.project, document)
    jedi_lines = jedi_utils.line_column(params.position)
    completions_jedi_raw = jedi_script.complete(*jedi_lines)
    if not ignore_patterns:
        # A performance optimization. ignore_patterns should usually be empty;
        # this special case avoid repeated filter checks for the usual case.
        completions_jedi = (comp for comp in completions_jedi_raw)
    else:
        completions_jedi = (
            comp
            for comp in completions_jedi_raw
            if not any(i.match(comp.name) for i in ignore_patterns)
        )
    snippet_support = get_capability(
        server.client_capabilities,
        "text_document.completion.completion_item.snippet_support",
        False,
    )
    markup_kind = _choose_markup(server)
    is_import_context = jedi_utils.is_import(
        script_=jedi_script,
        line=jedi_lines[0],
        column=jedi_lines[1],
    )
    enable_snippets = (
        snippet_support and not snippet_disable and not is_import_context
    )
    char_before_cursor = pygls_utils.char_before_cursor(
        document, params.position
    )
    char_after_cursor = pygls_utils.char_after_cursor(
        document, params.position
    )
    jedi_utils.clear_completions_cache()
    # number of characters in the string representation of the total number of
    # completions returned by jedi.
    total_completion_chars = len(str(len(completions_jedi_raw)))
    completion_items = [
        jedi_utils.lsp_completion_item(
            completion=completion,
            char_before_cursor=char_before_cursor,
            char_after_cursor=char_after_cursor,
            enable_snippets=enable_snippets,
            resolve_eagerly=resolve_eagerly,
            markup_kind=markup_kind,
            sort_append_text=str(count).zfill(total_completion_chars),
        )
        for count, completion in enumerate(completions_jedi)
        if completion.type != "path"
    ]
    return (
        CompletionList(is_incomplete=False, items=completion_items)
        if completion_items
        else None
    )


def signature_help(
    server: JediLanguageServer,
    params: TextDocumentPositionParams,
    document: Optional[TextDocument] = None,
) -> Optional[SignatureHelp]:
    """Returns signature help.

    Note: for docstring, we currently choose plaintext because coc doesn't
    handle markdown well in the signature. Will update if this changes in the
    future.
    """
    if document is None:
        document = server.workspace.get_text_document(params.text_document.uri)
    jedi_script = jedi_utils.script(server.project, document)
    jedi_lines = jedi_utils.line_column(params.position)
    signatures_jedi = jedi_script.get_signatures(*jedi_lines)
    markup_kind = _choose_markup(server)
    signatures = [
        SignatureInformation(
            label=jedi_utils.signature_string(signature),
            documentation=MarkupContent(
                kind=markup_kind,
                value=jedi_utils.convert_docstring(
                    signature.docstring(raw=True),
                    markup_kind,
                ),
            ),
            parameters=[
                ParameterInformation(label=info.to_string())
                for info in signature.params
            ],
        )
        for signature in signatures_jedi
    ]
    return (
        SignatureHelp(
            signatures=signatures,
            active_signature=0,
            active_parameter=(
                signatures_jedi[0].index if signatures_jedi else 0
            ),
        )
        if signatures
        else None
    )


def declaration(
    server: JediLanguageServer,
    params: TextDocumentPositionParams,
    document: Optional[TextDocument] = None,
) -> Optional[List[Location]]:
    """Support Goto Declaration."""
    if document is None:
        document = server.workspace.get_text_document(params.text_document.uri)
    jedi_script = jedi_utils.script(server.project, document)
    jedi_lines = jedi_utils.line_column(params.position)
    names = jedi_script.goto(*jedi_lines)
    definitions = [
        definition
        for definition in (jedi_utils.lsp_location(name) for name in names)
        if definition is not None
    ]
    return definitions if definitions else None


def definition(
    server: JediLanguageServer,
    params: TextDocumentPositionParams,
    document: Optional[TextDocument] = None,
) -> Optional[List[Location]]:
    """Support Goto Definition."""
    if document is None:
        document = server.workspace.get_text_document(params.text_document.uri)
    jedi_script = jedi_utils.script(server.project, document)
    jedi_lines = jedi_utils.line_column(params.position)
    names = jedi_script.goto(
        *jedi_lines,
        follow_imports=True,
        follow_builtin_imports=True,
    )
    definitions = [
        definition
        for definition in (jedi_utils.lsp_location(name) for name in names)
        if definition is not None
    ]
    return definitions if definitions else None


def type_definition(
    server: JediLanguageServer,
    params: TextDocumentPositionParams,
    document: Optional[TextDocument] = None,
) -> Optional[List[Location]]:
    """Support Goto Type Definition."""
    if document is None:
        document = server.workspace.get_text_document(params.text_document.uri)
    jedi_script = jedi_utils.script(server.project, document)
    jedi_lines = jedi_utils.line_column(params.position)
    names = jedi_script.infer(*jedi_lines)
    definitions = [
        definition
        for definition in (jedi_utils.lsp_location(name) for name in names)
        if definition is not None
    ]
    return definitions if definitions else None


def highlight(
    server: JediLanguageServer,
    params: TextDocumentPositionParams,
    document: Optional[TextDocument] = None,
) -> Optional[List[DocumentHighlight]]:
    """Support document highlight request.

    This function is called frequently, so we minimize the number of expensive
    calls. These calls are:

    1. Getting assignment of current symbol (script.goto)
    2. Getting all names in the current script (script.get_names)

    Finally, we only return names if there are more than 1. Otherwise, we don't
    want to highlight anything.
    """
    if document is None:
        document = server.workspace.get_text_document(params.text_document.uri)
    jedi_script = jedi_utils.script(server.project, document)
    jedi_lines = jedi_utils.line_column(params.position)
    names = jedi_script.get_references(*jedi_lines, scope="file")
    lsp_ranges = [jedi_utils.lsp_range(name) for name in names]
    highlight_names = [
        DocumentHighlight(range=lsp_range)
        for lsp_range in lsp_ranges
        if lsp_range
    ]
    return highlight_names if highlight_names else None


def hover(
    server: JediLanguageServer,
    params: TextDocumentPositionParams,
    document: Optional[TextDocument] = None,
) -> Optional[Hover]:
    """Support Hover."""
    if document is None:
        document = server.workspace.get_text_document(params.text_document.uri)
    jedi_script = jedi_utils.script(server.project, document)
    jedi_lines = jedi_utils.line_column(params.position)
    markup_kind = _choose_markup(server)
    hover_text = jedi_utils.hover_text(
        jedi_script.help(*jedi_lines),
        markup_kind,
        server.initialization_options,
    )
    if not hover_text:
        return None
    contents = MarkupContent(kind=markup_kind, value=hover_text)
    _range = pygls_utils.current_word_range(document, params.position)
    return Hover(contents=contents, range=_range)


def references(
    server: JediLanguageServer,
    params: TextDocumentPositionParams,
    document: Optional[TextDocument] = None,
) -> Optional[List[Location]]:
    """Obtain all references to text."""
    if document is None:
        document = server.workspace.get_text_document(params.text_document.uri)
    jedi_script = jedi_utils.script(server.project, document)
    jedi_lines = jedi_utils.line_column(params.position)
    names = jedi_script.get_references(*jedi_lines)
    locations = [
        location
        for location in (jedi_utils.lsp_location(name) for name in names)
        if location is not None
    ]
    return locations if locations else None


def document_symbol(
    server: JediLanguageServer,
    params: DocumentSymbolParams,
    document: Optional[TextDocument] = None,
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
    document = server.workspace.get_text_document(params.text_document.uri)
    jedi_script = jedi_utils.script(server.project, document)
    names = jedi_script.get_names(all_scopes=True, definitions=True)
    if get_capability(
        server.client_capabilities,
        "text_document.document_symbol.hierarchical_document_symbol_support",
        False,
    ):
        document_symbols = jedi_utils.lsp_document_symbols(names)
        return document_symbols if document_symbols else None
    symbol_information = [
        symbol_info
        for symbol_info in (
            jedi_utils.lsp_symbol_information(name, document.uri)
            for name in names
            if name.type != "param"
        )
        if symbol_info is not None
    ]
    return symbol_information if symbol_information else None


def rename(
    server: JediLanguageServer,
    params: RenameParams,
    document: Optional[TextDocument] = None,
) -> Optional[WorkspaceEdit]:
    """Rename a symbol across a workspace."""
    if document is None:
        document = server.workspace.get_text_document(params.text_document.uri)
    jedi_script = jedi_utils.script(server.project, document)
    jedi_lines = jedi_utils.line_column(params.position)
    try:
        refactoring = jedi_script.rename(*jedi_lines, new_name=params.new_name)
    except RefactoringError:
        return None
    changes = text_edit_utils.lsp_document_changes(
        server.workspace, refactoring
    )
    return WorkspaceEdit(document_changes=changes) if changes else None


def code_action(
    server: JediLanguageServer,
    params: CodeActionParams,
    document: Optional[TextDocument] = None,
) -> Optional[List[CodeAction]]:
    """Get code actions.

    Currently supports:
        1. Inline variable
        2. Extract variable
        3. Extract function
    """
    if document is None:
        document = server.workspace.get_text_document(params.text_document.uri)
    jedi_script = jedi_utils.script(server.project, document)
    code_actions = []
    jedi_lines = jedi_utils.line_column(params.range.start)
    jedi_lines_extract = jedi_utils.line_column_range(params.range)

    try:
        if params.range.start.line != params.range.end.line:
            # refactor this at some point; control flow with exception == bad
            raise RefactoringError("inline only viable for single-line range")
        inline_refactoring = jedi_script.inline(*jedi_lines)
    except (RefactoringError, AttributeError, IndexError):
        inline_changes = []
    else:
        inline_changes = text_edit_utils.lsp_document_changes(
            server.workspace, inline_refactoring
        )
    if inline_changes:
        code_actions.append(
            CodeAction(
                title="Inline variable",
                kind=CodeActionKind.RefactorInline,
                edit=WorkspaceEdit(
                    document_changes=inline_changes,
                ),
            )
        )

    extract_var = (
        server.initialization_options.code_action.name_extract_variable
    )
    try:
        extract_variable_refactoring = jedi_script.extract_variable(
            new_name=extract_var, **jedi_lines_extract
        )
    except (RefactoringError, AttributeError, IndexError):
        extract_variable_changes = []
    else:
        extract_variable_changes = text_edit_utils.lsp_document_changes(
            server.workspace, extract_variable_refactoring
        )
    if extract_variable_changes:
        code_actions.append(
            CodeAction(
                title=f"Extract expression into variable '{extract_var}'",
                kind=CodeActionKind.RefactorExtract,
                edit=WorkspaceEdit(
                    document_changes=extract_variable_changes,
                ),
            )
        )

    extract_func = (
        server.initialization_options.code_action.name_extract_function
    )
    try:
        extract_function_refactoring = jedi_script.extract_function(
            new_name=extract_func, **jedi_lines_extract
        )
    except (RefactoringError, AttributeError, IndexError):
        extract_function_changes = []
    else:
        extract_function_changes = text_edit_utils.lsp_document_changes(
            server.workspace, extract_function_refactoring
        )
    if extract_function_changes:
        code_actions.append(
            CodeAction(
                title=f"Extract expression into function '{extract_func}'",
                kind=CodeActionKind.RefactorExtract,
                edit=WorkspaceEdit(
                    document_changes=extract_function_changes,
                ),
            )
        )

    return code_actions if code_actions else None


def clear_diagnostics(server: JediLanguageServer, uri: str) -> None:
    """Helper function to clear diagnostics for a file."""
    server.publish_diagnostics(uri, [])


# Static capability or initializeOptions functions that rely on a specific
# client capability or user configuration. These are associated with
# JediLanguageServer within JediLanguageServerProtocol.lsp_initialize
@jedi_utils.debounce(1, keyed_by="uri")
def publish_diagnostics(
    server: JediLanguageServer, uri: str, filename: Optional[str] = None
) -> None:
    """Helper function to publish diagnostics for a file."""
    # The debounce decorator delays the execution by 1 second
    # canceling notifications that happen in that interval.
    # Since this function is executed after a delay, we need to check
    # whether the document still exists
    if uri not in server.workspace.documents:
        return
    if filename is None:
        filename = uri
    document = server.workspace.get_text_document(uri)
    diagnostic = jedi_utils.lsp_python_diagnostic(filename, document.source)
    diagnostics = [diagnostic] if diagnostic else []
    server.publish_diagnostics(uri, diagnostics)


def _choose_markup(server: JediLanguageServer) -> MarkupKind:
    """Returns the preferred or first of supported markup kinds."""
    markup_preferred = server.initialization_options.markup_kind_preferred
    markup_supported = get_capability(
        server.client_capabilities,
        "text_document.completion.completion_item.documentation_format",
        [MarkupKind.PlainText],
    )

    return MarkupKind(
        markup_preferred
        if markup_preferred in markup_supported
        else markup_supported[0]
    )
