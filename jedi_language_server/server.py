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
    get_jedi_script,
    get_location_from_name,
    get_symbol_information_from_name,
)
from .type_map import get_lsp_completion_type

SERVER = LanguageServer()


@SERVER.feature(COMPLETION, triggerCharacters=["."])
def lsp_completion(server: LanguageServer, params: CompletionParams):
    """Returns completion items."""
    script = get_jedi_script(server, params.textDocument.uri)
    jedi_completions = script.complete(
        line=params.position.line + 1, column=params.position.character,
    )
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
            for completion in jedi_completions
        ],
    )


@SERVER.feature(DEFINITION)
def lsp_definition(
    server: LanguageServer, params: TextDocumentPositionParams
) -> List[Location]:
    """Support Goto Definition"""
    script = get_jedi_script(server, params.textDocument.uri)
    names = script.goto(
        line=params.position.line + 1,
        column=params.position.character,
        follow_imports=True,
        follow_builtin_imports=True,
    )
    return [get_location_from_name(name) for name in names]


@SERVER.feature(HOVER)
def lsp_hover(
    server: LanguageServer, params: TextDocumentPositionParams
) -> Hover:
    """Support the hover feature"""
    script = get_jedi_script(server, params.textDocument.uri)
    names = script.infer(
        line=params.position.line + 1, column=params.position.character,
    )
    return Hover(
        contents=(
            names[0].docstring() if names else "No docstring definition found."
        )
    )


@SERVER.feature(REFERENCES)
def lsp_references(
    server: LanguageServer, params: TextDocumentPositionParams
) -> List[Location]:
    """Obtain all references to document"""
    script = get_jedi_script(server, params.textDocument.uri)
    try:
        names = script.get_references(
            line=params.position.line + 1, column=params.position.character,
        )
    except Exception:  # pylint: disable=broad-except
        return []
    return [get_location_from_name(name) for name in names]


@SERVER.feature(RENAME)
def lsp_rename(
    server: LanguageServer, params: RenameParams
) -> Optional[WorkspaceEdit]:
    """Rename a symbol across a workspace"""
    script = get_jedi_script(server, params.textDocument.uri)
    try:
        names = script.get_references(
            line=params.position.line + 1, column=params.position.character,
        )
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
    script = get_jedi_script(server, params.textDocument.uri)
    try:
        names = script.get_names(
            line=params.position.line + 1, column=params.position.character,
        )
    except Exception:  # pylint: disable=broad-except
        return []
    return [get_symbol_information_from_name(name) for name in names]
