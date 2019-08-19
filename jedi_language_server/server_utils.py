"""Utility functions used by the language server"""

from typing import Union, List

from jedi import Script
from jedi.api.classes import Definition
from jedi.api.environment import get_cached_default_environment

from pygls.server import LanguageServer
from pygls.uris import from_fs_path
from pygls.types import (
    Location,
    Range,
    Position,
    RenameParams,
    TextDocumentPositionParams,
)


def get_jedi_script(
    server: LanguageServer,
    params: Union[TextDocumentPositionParams, RenameParams],
) -> Script:
    """Simplifies getting jedi Script

    NOTE:
        * jedi is 1-indexed for lines and 0-indexed for columns
        * LSP is 0-indexed for lines and 0-indexed for columns
        * Therefore, add 1 to LSP's request for the line
    """
    workspace = server.workspace
    text_doc = workspace.get_document(params.textDocument.uri)
    return Script(
        source=text_doc.source,
        path=text_doc.path,
        line=params.position.line + 1,
        column=params.position.character,
        environment=get_cached_default_environment(),
    )


def locations_from_definitions(
    definitions: List[Definition]
) -> List[Location]:
    """Get LSP locations from Jedi definitions

    NOTE:
        * jedi is 1-indexed for lines and 0-indexed for columns
        * LSP is 0-indexed for lines and 0-indexed for columns
        * Therefore, subtract 1 from Jedi's definition line
    """
    return [
        Location(
            uri=from_fs_path(definition.module_path),
            range=Range(
                start=Position(
                    line=definition.line - 1, character=definition.column
                ),
                end=Position(
                    line=definition.line - 1,
                    character=definition.column + len(definition.name),
                ),
            ),
        )
        for definition in definitions
    ]
