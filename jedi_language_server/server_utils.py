"""Utility functions used by the language server"""

import itertools
import os
import subprocess
from typing import List, Optional, Union

import jedi.api
from jedi import Script
from jedi.api.classes import Definition
from jedi.api.environment import get_cached_default_environment
from pygls.server import LanguageServer, Workspace
from pygls.types import (
    DocumentSymbolParams,
    Location,
    Position,
    Range,
    RenameParams,
    SymbolInformation,
    TextDocumentItem,
    TextDocumentPositionParams,
)
from pygls.uris import from_fs_path

from .type_map import get_lsp_symbol_type


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


class WorkspaceDocuments:
    """A class to manage one-time gathering of workspace documents"""

    # pylint: disable=too-few-public-methods

    def __init__(self) -> None:
        self.gathered_names = False

    def gather_workspace_names(self, workspace: Workspace) -> None:
        """Collect the workspace names"""
        if not self.gathered_names:
            git_path = os.path.join(workspace.root_path, ".git")
            git_command = "git --git-dir=" + git_path + " ls-files --full-name"
            try:
                git_output = subprocess.check_output(git_command, shell=True)
            except subprocess.CalledProcessError:
                self.gathered_names = True
                return
            project_paths = git_output.decode("utf-8").splitlines()
            for doc_path in project_paths:
                if os.path.splitext(doc_path)[1] == ".py":
                    full_doc_path = os.path.join(workspace.root_path, doc_path)
                    doc_uri = from_fs_path(full_doc_path)
                    with open(full_doc_path) as infile:
                        text = infile.read()
                    workspace.put_document(
                        TextDocumentItem(
                            uri=doc_uri,
                            language_id="python",
                            version=0,
                            text=text,
                        )
                    )
        self.gathered_names = True


_WORKSPACE_DOCUMENTS = WorkspaceDocuments()


def get_jedi_workspace_names(server: LanguageServer) -> List[Definition]:
    """Get a list of workspace names from Jedi"""
    workspace = server.workspace
    _WORKSPACE_DOCUMENTS.gather_workspace_names(workspace)
    definitions_by_document = (
        jedi.api.names(
            source=text_doc.source,
            path=text_doc.path,
            all_scopes=True,
            definitions=True,
            references=False,
            environment=get_cached_default_environment(),
        )
        for text_doc in workspace.documents.values()
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
        kind=get_lsp_symbol_type(definition.type),
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
