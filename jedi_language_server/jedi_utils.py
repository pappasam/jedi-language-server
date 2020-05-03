"""Utilities to work with Jedi

Translates pygls types back and forth with Jedi
"""

from typing import Dict, List

import jedi.api.errors
import jedi.inference.references
from jedi import Project, Script
from jedi.api.classes import Name
from jedi.api.environment import get_cached_default_environment
from pygls.types import (
    Diagnostic,
    DiagnosticSeverity,
    DocumentSymbol,
    Location,
    Position,
    Range,
    SymbolInformation,
)
from pygls.uris import from_fs_path
from pygls.workspace import Workspace

from .type_map import get_lsp_symbol_type

# NOTE: remove this once Jedi ignores '.venv' folders by default
# without this line, Jedi will search in '.venv' folders
jedi.inference.references._IGNORE_FOLDERS = (  # pylint: disable=protected-access
    *jedi.inference.references._IGNORE_FOLDERS,  # pylint: disable=protected-access
    ".venv",
)


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


def lsp_range(name: Name) -> Range:
    """Get LSP range from Jedi definition

    NOTE:
        * jedi is 1-indexed for lines and 0-indexed for columns
        * LSP is 0-indexed for lines and 0-indexed for columns
        * Therefore, subtract 1 from Jedi's definition line
    """
    return Range(
        start=Position(line=name.line - 1, character=name.column),
        end=Position(
            line=name.line - 1, character=name.column + len(name.name),
        ),
    )


def lsp_location(name: Name) -> Location:
    """Get LSP location from Jedi definition"""
    return Location(uri=from_fs_path(name.module_path), range=lsp_range(name))


def lsp_symbol_information(name: Name) -> SymbolInformation:
    """Get LSP SymbolInformation from Jedi definition"""
    return SymbolInformation(
        name=name.name,
        kind=get_lsp_symbol_type(name.type),
        location=lsp_location(name),
        container_name=name.parent(),
    )


def _document_symbol_range(name: Name) -> Range:
    """Get accurate full range of function

    Thanks https://github.com/CXuesong from
    https://github.com/palantir/python-language-server/pull/537/files for the
    inspiration!

    Note: I add tons of extra space to make dictionary completions work. Jedi
    cuts off the end sometimes before the final function statement. This may be
    the cause of bugs at some point.
    """
    _name = (
        name._name.tree_name.get_definition()  # pylint: disable=protected-access
    )
    (start_line, start_column) = _name.start_pos
    (end_line, end_column) = _name.end_pos
    return Range(
        start=Position(start_line - 1, start_column),
        end=Position(end_line - 1, end_column + 20000),
    )


def lsp_document_symbols(names: List[Name]) -> List[DocumentSymbol]:
    """Get hierarchical symbols"""
    _name_lookup: Dict[Name, DocumentSymbol] = {}
    results: List[DocumentSymbol] = []
    for name in names:
        symbol = DocumentSymbol(
            name=name.name,
            kind=get_lsp_symbol_type(name.type),
            range=_document_symbol_range(name),
            selection_range=lsp_range(name),
            children=[],
        )
        parent = name.parent()
        if parent is None or not parent in _name_lookup:
            results.append(symbol)
        else:
            _name_lookup[parent].children.append(symbol)  # type: ignore
        _name_lookup[name] = symbol
    return results


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


def line_column(position: Position) -> Dict[str, int]:
    """Translate pygls Position to Jedi's line / column

    Returns a dictionary because this return result should be unpacked as a
    function argument to Jedi's functions.

    Jedi is 1-indexed for lines and 0-indexed for columns. LSP is 0-indexed for
    lines and 0-indexed for columns. Therefore, add 1 to LSP's request for the
    line.
    """
    return dict(line=position.line + 1, column=position.character)


def compare_names(name1: Name, name2: Name) -> bool:
    """Check if one Name is equal to another

    This function, while trivial, is useful for documenting types without
    needing to directly import anything from jedi into `server.py`
    """
    return name1 == name2
