"""Utility functions used by the language server"""

from typing import Optional

from jedi import Project, Script
from jedi.api.classes import Name
from jedi.api.environment import get_cached_default_environment
from pygls.server import LanguageServer
from pygls.types import Location, Position, Range, SymbolInformation
from pygls.uris import from_fs_path

from .type_map import get_lsp_symbol_type


def get_jedi_script(server: LanguageServer, doc_uri: str) -> Script:
    """Simplifies getting jedi Script

    :param doc_uri: the uri for the LSP text document. Obtained through
    params.textDocument.uri

    NOTE:
        * jedi is 1-indexed for lines and 0-indexed for columns
        * LSP is 0-indexed for lines and 0-indexed for columns
        * Therefore, add 1 to LSP's request for the line
    """
    workspace = server.workspace
    text_doc = workspace.get_document(doc_uri)
    project = Project(
        path=workspace.root_path,
        smart_sys_path=True,
        load_unsafe_extensions=False,
    )
    return Script(
        code=text_doc.source,
        path=text_doc.path,
        project=project,
        environment=get_cached_default_environment(),
    )


def get_location_from_name(name: Name) -> Location:
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


def get_symbol_information_from_name(name: Name,) -> SymbolInformation:
    """Get LSP SymbolInformation from Jedi definition"""
    return SymbolInformation(
        name=name.name,
        kind=get_lsp_symbol_type(name.type),
        location=get_location_from_name(name),
        container_name=get_jedi_parent_name(name),
    )


def get_jedi_parent_name(name: Name) -> Optional[str]:
    """Retrieve the parent name from Jedi

    Error prone Jedi calls are wrapped in try/except to avoid
    """
    try:
        parent = name.parent()
    except Exception:  # pylint: disable=broad-except
        return None
    return parent.name if parent and parent.parent() else None
