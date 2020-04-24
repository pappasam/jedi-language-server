"""Jedi Language Server

Creates the language server constant and wraps "features" with it.

Official language server spec:
    https://microsoft.github.io/language-server-protocol/specification
"""

import itertools
import uuid
from typing import Dict  # pylint: disable=unused-import
from typing import List, NamedTuple, Optional

from pygls.features import (
    COMPLETION,
    DEFINITION,
    DOCUMENT_SYMBOL,
    HOVER,
    INITIALIZED,
    REFERENCES,
    RENAME,
    WORKSPACE_SYMBOL,
)
from pygls.server import LanguageServer
from pygls.types import (
    CompletionItem,
    CompletionList,
    CompletionParams,
    DocumentSymbolParams,
    Hover,
    InitializeParams,
    Location,
    MessageType,
    Position,
    Registration,
    RegistrationParams,
    RenameParams,
    SymbolInformation,
    TextDocumentPositionParams,
    TextEdit,
    WorkspaceEdit,
    WorkspaceSymbolParams,
)
from pygls.workspace import Document

from .jedi_utils import (
    get_jedi_line_column,
    get_jedi_project,
    get_jedi_script,
    get_location_from_name,
    get_symbol_information_from_name,
)
from .type_map import get_lsp_completion_type

SERVER = LanguageServer()


class Option(NamedTuple):
    name_user: str
    name_system: str
    default: object


class ServerConfig:
    def __init__(
        self, server: LanguageServer, initialization_options: object
    ) -> None:
        self.server = server
        self.init_options = initialization_options

    def get_options(self, options: List[Option]) -> Dict[str, object]:
        """Obtain the object provided by the default"""
        return {
            option.name_system: getattr(
                self.init_options, option.name_user, option.default
            )
            for option in options
        }

    async def register(self, method: str, options: List[Option]) -> None:
        response = await self.server.register_capability_async(
            RegistrationParams(
                [
                    Registration(
                        str(uuid.uuid4()), method, self.get_options(options)
                    )
                ]
            )
        )
        if response is not None:
            self.server.show_message(
                f"jedi-language-server: error during {method} registration",
                MessageType.Error,
            )


@SERVER.feature(INITIALIZED)
async def lsp_initialize(server: LanguageServer, params: InitializeParams):
    """Initialize language server"""
    config = ServerConfig(server, params.initializationOptions)
    await config.register(
        COMPLETION,
        [
            Option(
                name_user="completion_triggerCharacters",
                name_system="triggerCharacters",
                default=[".", "'", '"'],
            )
        ],
    )
    server.show_message("jedi-language-server: registration complete")


def _clean_completion_name(name: str, char: str) -> str:
    """Clean the completion name, stripping bad surroundings

    1. Remove all surrounding " and '. For
    """
    if char == "'":
        return name.lstrip("'")
    if char == '"':
        return name.lstrip('"')
    return name


def _char_before_cursor(
    document: Document, position: Position, default=""
) -> str:
    """Get the character directly before the cursor"""
    try:
        return document.lines[position.line][position.character - 1]
    except IndexError:
        return default


@SERVER.feature(COMPLETION)
def lsp_completion(server: LanguageServer, params: CompletionParams):
    """Returns completion items"""
    jedi_script = get_jedi_script(server.workspace, params.textDocument)
    jedi_lines = get_jedi_line_column(params.position)
    completions = jedi_script.complete(**jedi_lines)
    char = _char_before_cursor(
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
                insert_text=_clean_completion_name(completion.name, char),
            )
            for completion in completions
        ],
    )


@SERVER.feature(DEFINITION)
def lsp_definition(
    server: LanguageServer, params: TextDocumentPositionParams
) -> List[Location]:
    """Support Goto Definition"""
    jedi_script = get_jedi_script(server.workspace, params.textDocument)
    jedi_lines = get_jedi_line_column(params.position)
    names = jedi_script.goto(
        follow_imports=True, follow_builtin_imports=True, **jedi_lines,
    )
    return [get_location_from_name(name) for name in names]


@SERVER.feature(HOVER)
def lsp_hover(
    server: LanguageServer, params: TextDocumentPositionParams
) -> Hover:
    """Support Hover"""
    jedi_script = get_jedi_script(server.workspace, params.textDocument)
    jedi_lines = get_jedi_line_column(params.position)
    try:
        _names = jedi_script.help(**jedi_lines)
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
    jedi_script = get_jedi_script(server.workspace, params.textDocument)
    jedi_lines = get_jedi_line_column(params.position)
    try:
        names = jedi_script.get_references(**jedi_lines)
    except Exception:  # pylint: disable=broad-except
        return []
    return [get_location_from_name(name) for name in names]


@SERVER.feature(RENAME)
def lsp_rename(
    server: LanguageServer, params: RenameParams
) -> Optional[WorkspaceEdit]:
    """Rename a symbol across a workspace"""
    jedi_script = get_jedi_script(server.workspace, params.textDocument)
    jedi_lines = get_jedi_line_column(params.position)
    try:
        names = jedi_script.get_references(**jedi_lines)
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
    jedi_script = get_jedi_script(server.workspace, params.textDocument)
    try:
        names = jedi_script.get_names()
    except Exception:  # pylint: disable=broad-except
        return []
    return [get_symbol_information_from_name(name) for name in names]


@SERVER.feature(WORKSPACE_SYMBOL)
def lsp_workspace_symbol(
    server: LanguageServer, params: WorkspaceSymbolParams
) -> List[SymbolInformation]:
    """Document Python workspace symbols"""
    jedi_project = get_jedi_project(server.workspace)
    if params.query.strip() == "":
        return []
    try:
        names = jedi_project.search(params.query)
    except Exception:  # pylint: disable=broad-except
        return []
    return [
        get_symbol_information_from_name(name)
        for name in itertools.islice(names, 20)
    ]
