"""Utility functions used by the language server"""

import itertools
import os
from glob import glob
from typing import List, Optional, Union

import jedi.api
from jedi import Script
from jedi.api.classes import Definition
from jedi.api.environment import get_cached_default_environment
from pygls.server import LanguageServer
from pygls.types import (
    DocumentSymbolParams,
    Location,
    Position,
    Range,
    RenameParams,
    SymbolInformation,
    TextDocumentPositionParams,
)
from pygls.uris import from_fs_path

from .type_map import get_lsp_type


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


def get_jedi_document_names(
    server: LanguageServer, params: DocumentSymbolParams,
) -> List[Definition]:
    """Get a list of document names from Jedi"""
    workspace = server.workspace
    text_doc = workspace.get_document(params.textDocument.uri)
    return jedi.api.names(
        source=text_doc.source,
        path=text_doc.path,
        all_scopes=True,
        definitions=True,
        references=False,
        environment=get_cached_default_environment(),
    )


def get_jedi_workspace_names(server: LanguageServer) -> List[Definition]:
    """Get a list of workspace names from Jedi"""
    workspace = server.workspace
    python_paths = (
        os.path.abspath(path)
        for path in itertools.chain.from_iterable(
            glob(os.path.join(x[0], "*.py"))
            for x in os.walk(workspace.root_path)
        )
    )
    documents = (
        workspace.get_document(from_fs_path(python_path))
        for python_path in python_paths
        if os.getenv("VIRTUAL_ENV")
        and not python_path.startswith(os.getenv("VIRTUAL_ENV"))
    )
    definitions_by_document = (
        jedi.api.names(
            source=text_doc.source,
            path=text_doc.path,
            all_scopes=True,
            definitions=True,
            references=False,
            environment=get_cached_default_environment(),
        )
        for text_doc in documents
        if text_doc and os.path.splitext(text_doc.path)[1] == ".py"
    )
    return list(
        itertools.chain.from_iterable(
            definitions if definitions else []
            for definitions in definitions_by_document
        )
    )


def get_location_from_definition(definition: Definition) -> Location:
    """Get LSP location from Jedi definition

    NOTE:
        * jedi is 1-indexed for lines and 0-indexed for columns
        * LSP is 0-indexed for lines and 0-indexed for columns
        * Therefore, subtract 1 from Jedi's definition line
    """
    return Location(
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


def get_symbol_information_from_definition(
    definition: Definition,
) -> SymbolInformation:
    """Get LSP SymbolInformation from Jedi definition"""
    return SymbolInformation(
        name=definition.name,
        kind=get_lsp_type(definition.type),
        location=get_location_from_definition(definition),
        container_name=get_jedi_parent_name(definition),
    )


def get_jedi_parent_name(definition: Definition) -> Optional[str]:
    """Retrieve the parent name from Jedi

    Error prone Jedi calls are wrapped in try/except to avoid
    """
    try:
        parent = definition.parent()
    except Exception:  # pylint: disable=broad-except
        return None
    return parent.name if parent and parent.parent() else None
