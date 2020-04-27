"""Utilities to work with Jedi

Translates pygls types back and forth with Jedi
"""

from typing import Dict, Optional

import jedi.api.errors
from jedi import Project, Script
from jedi.api.classes import Name
from jedi.api.environment import get_cached_default_environment
from pygls.types import (
    Diagnostic,
    DiagnosticSeverity,
    Location,
    Position,
    Range,
    SymbolInformation,
)
from pygls.uris import from_fs_path
from pygls.workspace import Workspace

from .type_map import get_lsp_symbol_type


def script(workspace: Workspace, uri: str) -> Script:
    """Simplifies getting jedi Script"""
    project_ = project(workspace)
    document = workspace.get_document(uri)
    return Script(
        code=document.source,
        path=document.path,
        project=project_,
        environment=get_cached_default_environment(),
    )


def project(workspace: Workspace) -> Project:
    """Simplifies getting jedi project"""
    return Project(
        path=workspace.root_path,
        smart_sys_path=True,
        load_unsafe_extensions=False,
    )


def lsp_location(name: Name) -> Location:
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


def lsp_symbol_information(name: Name) -> SymbolInformation:
    """Get LSP SymbolInformation from Jedi definition"""
    return SymbolInformation(
        name=name.name,
        kind=get_lsp_symbol_type(name.type),
        location=lsp_location(name),
        container_name=parent_name(name),
    )


def lsp_diagnostic(error: jedi.api.errors.SyntaxError) -> Diagnostic:
    """Get LSP Diagnostic from Jedi SyntaxError"""
    return Diagnostic(
        range=Range(
            start=Position(line=error.line - 1, character=error.column),
            end=Position(line=error.line - 1, character=error.column),
        ),
        message=str(error).strip("<>"),
        severity=DiagnosticSeverity.Error,
        source="jedi",
    )


def parent_name(name: Name) -> Optional[str]:
    """Retrieve the parent name from Jedi

    Error prone Jedi calls are wrapped in try/except to avoid
    """
    try:
        parent = name.parent()
    except Exception:  # pylint: disable=broad-except
        return None
    return parent.name if parent and parent.parent() else None


def line_column(position: Position) -> Dict[str, int]:
    """Translate pygls Position to Jedi's line / column

    Returns a dictionary because this return result should be unpacked as a
    function argument to Jedi's functions.

    Jedi is 1-indexed for lines and 0-indexed for columns. LSP is 0-indexed for
    lines and 0-indexed for columns. Therefore, add 1 to LSP's request for the
    line.
    """
    return dict(line=position.line + 1, column=position.character)
