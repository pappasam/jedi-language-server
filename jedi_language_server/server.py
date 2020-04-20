"""Jedi Language Server

Creates the language server constant and wraps "features" with it.

Official language server spec:
    https://microsoft.github.io/language-server-protocol/specification
"""

from typing import Dict  # pylint: disable=unused-import
from typing import List, Optional

from pygls.features import (
    COMPLETION,
    DEFINITION,
    DOCUMENT_SYMBOL,
    HOVER,
    REFERENCES,
    RENAME,
)
from pygls.server import LanguageServer
from pygls.types import (
    CompletionItem,
    CompletionList,
    CompletionParams,
    DocumentSymbolParams,
    Hover,
    Location,
    RenameParams,
    SymbolInformation,
    TextDocumentPositionParams,
    TextEdit,
    WorkspaceEdit,
)

from .server_utils import (
    get_jedi_line_column,
    get_jedi_types,
    get_location_from_name,
    get_symbol_information_from_name,
)
from .type_map import get_lsp_completion_type

SERVER = LanguageServer()


@SERVER.feature(COMPLETION, triggerCharacters=["."])
def lsp_completion(server: LanguageServer, params: CompletionParams):
    """Returns completion items"""
    jedi_types = get_jedi_types(server, params.textDocument)
    jedi_lines = get_jedi_line_column(params.position)
    completions = jedi_types.script.complete(**jedi_lines)
    return CompletionList(
        is_incomplete=False,
        items=[
            CompletionItem(
                label=completion.name,
                kind=get_lsp_completion_type(completion.type),
                detail=completion.description,
                documentation=completion.docstring(),
                insert_text=completion.name,
            )
            for completion in completions
        ],
    )


@SERVER.feature(DEFINITION)
def lsp_definition(
    server: LanguageServer, params: TextDocumentPositionParams
) -> List[Location]:
    """Support Goto Definition"""
    jedi_types = get_jedi_types(server, params.textDocument)
    jedi_lines = get_jedi_line_column(params.position)
    names = jedi_types.script.goto(
        follow_imports=True, follow_builtin_imports=True, **jedi_lines,
    )
    return [get_location_from_name(name) for name in names]


@SERVER.feature(HOVER)
def lsp_hover(
    server: LanguageServer, params: TextDocumentPositionParams
) -> Hover:
    """Support Hover"""
    jedi_types = get_jedi_types(server, params.textDocument)
    jedi_lines = get_jedi_line_column(params.position)
    try:
        _names = jedi_types.script.help(**jedi_lines)
    except Exception:  # pylint: disable=broad-except
        names = []  # type: List[str]
    else:
        names = [name for name in (n.docstring() for n in _names) if name]
    return Hover(contents=names if names else "jedi: no help docs found")


@SERVER.feature(REFERENCES)
def lsp_references(
    server: LanguageServer, params: TextDocumentPositionParams
) -> List[Location]:
    """Obtain all references to document"""
    jedi_types = get_jedi_types(server, params.textDocument)
    jedi_lines = get_jedi_line_column(params.position)
    try:
        names = jedi_types.script.get_references(**jedi_lines)
    except Exception:  # pylint: disable=broad-except
        return []
    return [get_location_from_name(name) for name in names]


@SERVER.feature(RENAME)
def lsp_rename(
    server: LanguageServer, params: RenameParams
) -> Optional[WorkspaceEdit]:
    """Rename a symbol across a workspace"""
    jedi_types = get_jedi_types(server, params.textDocument)
    jedi_lines = get_jedi_line_column(params.position)
    try:
        names = jedi_types.script.get_references(**jedi_lines)
    except Exception:  # pylint: disable=broad-except
        return None
    locations = [get_location_from_name(name) for name in names]
    if not locations:
        return None
    changes = {}  # type: Dict[str, List[TextEdit]]
    for location in locations:
        text_edit = TextEdit(location.range, new_text=params.newName)
        if location.uri not in changes:
            changes[location.uri] = [text_edit]
        else:
            changes[location.uri].append(text_edit)
    return WorkspaceEdit(changes=changes)


@SERVER.feature(DOCUMENT_SYMBOL)
def lsp_document_symbol(
    server: LanguageServer, params: DocumentSymbolParams
) -> List[SymbolInformation]:
    """Document Python document symbols"""
    jedi_types = get_jedi_types(server, params.textDocument)
    try:
        names = jedi_types.script.get_names()
    except Exception:  # pylint: disable=broad-except
        return []
    return [get_symbol_information_from_name(name) for name in names]
