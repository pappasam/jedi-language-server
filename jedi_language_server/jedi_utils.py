"""Utilities to work with Jedi

Translates pygls types back and forth with Jedi
"""

from typing import Dict, Optional

from jedi import Project, Script
from jedi.api.classes import Name
from jedi.api.environment import get_cached_default_environment
from pygls.types import (
    Location,
    Position,
    Range,
    SymbolInformation,
    TextDocumentIdentifier,
)
from pygls.uris import from_fs_path
from pygls.workspace import Workspace

from .type_map import get_lsp_symbol_type


def get_script(
    workspace: Workspace, text_document_identifier: TextDocumentIdentifier
) -> Script:
    """Simplifies getting jedi Script"""
    project = get_project(workspace)
    document = workspace.get_document(text_document_identifier.uri)
    return Script(
        code=document.source,
        path=document.path,
        project=project,
        environment=get_cached_default_environment(),
    )


def get_project(workspace: Workspace) -> Project:
    """Simplifies getting jedi project"""
    return Project(
        path=workspace.root_path,
        smart_sys_path=True,
        load_unsafe_extensions=False,
    )


def get_lsp_location(name: Name) -> Location:
    """Get LSP location from Jedi definition

    NOTE:
        * jedi is 1-indexed for lines and 0-indexed for columns
        * LSP is 0-indexed for lines and 0-indexed for columns
        * Therefore, subtract 1 from Jedi's definition line
    """
    return Location(
        uri=from_fs_path(name.module_path),
        range=Range(
            start=Position(line=name.line - 1, character=name.column),
            end=Position(
                line=name.line - 1, character=name.column + len(name.name),
            ),
        ),
    )


def get_lsp_symbol_information(name: Name) -> SymbolInformation:
    """Get LSP SymbolInformation from Jedi definition"""
    return SymbolInformation(
        name=name.name,
        kind=get_lsp_symbol_type(name.type),
        location=get_lsp_location(name),
        container_name=get_parent_name(name),
    )


def get_parent_name(name: Name) -> Optional[str]:
    """Retrieve the parent name from Jedi

    Error prone Jedi calls are wrapped in try/except to avoid
    """
    try:
        parent = name.parent()
    except Exception:  # pylint: disable=broad-except
        return None
    return parent.name if parent and parent.parent() else None


def get_line_column(position: Position) -> Dict[str, int]:
    """Translate pygls Position to Jedi's line / column

    Returns a dictionary because this return result should be unpacked as a
    function argument to Jedi's functions.

    Jedi is 1-indexed for lines and 0-indexed for columns. LSP is 0-indexed for
    lines and 0-indexed for columns. Therefore, add 1 to LSP's request for the
    line.
    """
    return dict(line=position.line + 1, column=position.character)
