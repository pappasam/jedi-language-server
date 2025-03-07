from typing import List, Optional

from lsprotocol.types import (
    TEXT_DOCUMENT_CODE_ACTION,
    TEXT_DOCUMENT_COMPLETION,
    TEXT_DOCUMENT_DECLARATION,
    TEXT_DOCUMENT_DEFINITION,
    TEXT_DOCUMENT_REFERENCES,
    TEXT_DOCUMENT_RENAME,
    TEXT_DOCUMENT_SIGNATURE_HELP,
    TEXT_DOCUMENT_TYPE_DEFINITION,
    CodeAction,
    CodeActionParams,
    CompletionList,
    CompletionParams,
    DidChangeNotebookDocumentParams,
    DidCloseNotebookDocumentParams,
    DidOpenNotebookDocumentParams,
    DidSaveNotebookDocumentParams,
    Hover,
    Location,
    RenameParams,
    SignatureHelp,
    TextDocumentPositionParams,
    WorkspaceEdit,
)
from pygls.workspace import Workspace

from . import notebook_utils, server_utils
from .server import SERVER, JediLanguageServer


@SERVER.notebook_feature(TEXT_DOCUMENT_COMPLETION)
def completion(
    server: JediLanguageServer, params: CompletionParams
) -> Optional[CompletionList]:
    return notebook_utils.with_notebook_support(server_utils.completion)(
        server, params
    )


@SERVER.notebook_feature(TEXT_DOCUMENT_SIGNATURE_HELP)
def signature_help(
    server: JediLanguageServer, params: TextDocumentPositionParams
) -> Optional[SignatureHelp]:
    return notebook_utils.with_notebook_support(server_utils.signature_help)(
        server, params
    )


@SERVER.notebook_feature(TEXT_DOCUMENT_DECLARATION)
def declaration(
    server: JediLanguageServer, params: TextDocumentPositionParams
) -> Optional[List[Location]]:
    return notebook_utils.with_notebook_support(server_utils.declaration)(
        server, params
    )


@SERVER.notebook_feature(TEXT_DOCUMENT_DEFINITION)
def definition(
    server: JediLanguageServer, params: TextDocumentPositionParams
) -> Optional[List[Location]]:
    return notebook_utils.with_notebook_support(server_utils.definition)(
        server, params
    )


@SERVER.notebook_feature(TEXT_DOCUMENT_TYPE_DEFINITION)
def type_definition(
    server: JediLanguageServer, params: TextDocumentPositionParams
) -> Optional[List[Location]]:
    return notebook_utils.with_notebook_support(server_utils.type_definition)(
        server, params
    )


def hover(
    server: JediLanguageServer, params: TextDocumentPositionParams
) -> Optional[Hover]:
    return notebook_utils.with_notebook_support(server_utils.hover)(
        server, params
    )


@SERVER.notebook_feature(TEXT_DOCUMENT_REFERENCES)
def references(
    server: JediLanguageServer, params: TextDocumentPositionParams
) -> Optional[List[Location]]:
    return notebook_utils.with_notebook_support(server_utils.references)(
        server, params
    )


@SERVER.notebook_feature(TEXT_DOCUMENT_RENAME)
def rename(
    server: JediLanguageServer, params: RenameParams
) -> Optional[WorkspaceEdit]:
    return notebook_utils.with_notebook_support(server_utils.rename)(
        server, params
    )


@SERVER.notebook_feature(TEXT_DOCUMENT_CODE_ACTION)
def code_action(
    server: JediLanguageServer,
    params: CodeActionParams,
) -> Optional[List[CodeAction]]:
    return notebook_utils.with_notebook_support(server_utils.code_action)(
        server, params
    )


# NOTEBOOK_DOCUMENT_DID_SAVE
def did_save_notebook_document_diagnostics(
    server: JediLanguageServer, params: DidSaveNotebookDocumentParams
) -> None:
    """Actions run on notebookDocument/didSave: diagnostics."""
    notebook_document = server.workspace.get_notebook_document(
        notebook_uri=params.notebook_document.uri
    )
    if notebook_document:
        for cell in notebook_document.cells:
            text_document = server.workspace.text_documents[cell.document]
            _publish_diagnostics(server, text_document.uri)


def did_save_notebook_document_default(
    server: JediLanguageServer,
    params: DidSaveNotebookDocumentParams,
) -> None:
    """Actions run on notebookDocument/didSave: default."""


# NOTEBOOK_DOCUMENT_DID_CHANGE
def did_change_notebook_document_diagnostics(
    server: JediLanguageServer, params: DidChangeNotebookDocumentParams
) -> None:
    """Actions run on notebookDocument/didChange: diagnostics."""
    cells = params.change.cells
    if cells:
        structure = cells.structure
        if structure:
            did_open = structure.did_open
            if did_open:
                for text_document_item in did_open:
                    _publish_diagnostics(
                        server,
                        text_document_item.uri,
                    )
            did_close = structure.did_close
            if did_close:
                for text_document in did_close:
                    server_utils.clear_diagnostics(server, text_document.uri)
        text_content = cells.text_content
        if text_content:
            for change in text_content:
                _publish_diagnostics(server, change.document.uri)


def did_change_notebook_document_default(
    server: JediLanguageServer,
    params: DidChangeNotebookDocumentParams,
) -> None:
    """Actions run on notebookDocument/didChange: default."""


# NOTEBOOK_DOCUMENT_DID_OPEN
def did_open_notebook_document_diagnostics(
    server: JediLanguageServer, params: DidOpenNotebookDocumentParams
) -> None:
    """Actions run on notebookDocument/didOpen: diagnostics."""
    for text_document in params.cell_text_documents:
        _publish_diagnostics(server, text_document.uri)


def did_open_notebook_document_default(
    server: JediLanguageServer,
    params: DidOpenNotebookDocumentParams,
) -> None:
    """Actions run on notebookDocument/didOpen: default."""


# NOTEBOOK_DOCUMENT_DID_CLOSE
def did_close_notebook_document_diagnostics(
    server: JediLanguageServer, params: DidCloseNotebookDocumentParams
) -> None:
    """Actions run on notebookDocument/didClose: diagnostics."""
    for text_document in params.cell_text_documents:
        server_utils.clear_diagnostics(server, text_document.uri)


def did_close_notebook_document_default(
    server: JediLanguageServer,
    params: DidCloseNotebookDocumentParams,
) -> None:
    """Actions run on notebookDocument/didClose: default."""


def _cell_filename(
    workspace: Workspace,
    cell_uri: str,
) -> str:
    notebook = notebook_utils.notebook_coordinate_mapper(
        workspace, cell_uri=cell_uri
    )
    if notebook is None:
        raise ValueError(
            f"Notebook document not found for cell URI: {cell_uri}"
        )
    index = notebook.cell_index(cell_uri)
    assert index is not None
    return f"cell {index + 1}"


def _publish_diagnostics(server: JediLanguageServer, uri: str) -> None:
    filename = _cell_filename(server.workspace, uri)
    return server_utils.publish_diagnostics(server, uri, filename)
