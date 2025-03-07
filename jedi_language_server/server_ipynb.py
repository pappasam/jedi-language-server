from typing import List, Optional, Tuple, TypeVar, Union

import attrs
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
from pygls.workspace.text_document import TextDocument

from . import notebook_utils, server_utils
from .server import SERVER, JediLanguageServer

T_params = TypeVar(
    "T_params",
    bound=Union[
        CodeActionParams,
        CompletionParams,
        RenameParams,
        TextDocumentPositionParams,
    ],
)


@SERVER.notebook_feature(TEXT_DOCUMENT_COMPLETION)
def completion(
    server: JediLanguageServer, params: CompletionParams
) -> Optional[CompletionList]:
    document, params = _notebook_text_document_and_params(
        server.workspace, params
    )
    return server_utils.completion(server, params, document)


@SERVER.notebook_feature(TEXT_DOCUMENT_SIGNATURE_HELP)
def signature_help(
    server: JediLanguageServer, params: TextDocumentPositionParams
) -> Optional[SignatureHelp]:
    document, params = _notebook_text_document_and_params(
        server.workspace, params
    )
    return server_utils.signature_help(server, params, document)


@SERVER.notebook_feature(TEXT_DOCUMENT_DECLARATION)
def declaration(
    server: JediLanguageServer, params: TextDocumentPositionParams
) -> Optional[List[Location]]:
    document, params = _notebook_text_document_and_params(
        server.workspace, params
    )
    locations = server_utils.declaration(server, params, document)
    return notebook_utils.text_document_or_cell_locations(
        server.workspace, locations
    )


@SERVER.notebook_feature(TEXT_DOCUMENT_DEFINITION)
def definition(
    server: JediLanguageServer, params: TextDocumentPositionParams
) -> Optional[List[Location]]:
    document, params = _notebook_text_document_and_params(
        server.workspace, params
    )
    locations = server_utils.definition(server, params, document)
    return notebook_utils.text_document_or_cell_locations(
        server.workspace, locations
    )


@SERVER.notebook_feature(TEXT_DOCUMENT_TYPE_DEFINITION)
def type_definition(
    server: JediLanguageServer, params: TextDocumentPositionParams
) -> Optional[List[Location]]:
    document, params = _notebook_text_document_and_params(
        server.workspace, params
    )
    locations = server_utils.type_definition(server, params, document)
    return notebook_utils.text_document_or_cell_locations(
        server.workspace, locations
    )


def hover(
    server: JediLanguageServer, params: TextDocumentPositionParams
) -> Optional[Hover]:
    document, params = _notebook_text_document_and_params(
        server.workspace, params
    )
    # TODO: Can we clean this up?
    #       Maybe have a single notebook_to_cell and vice versa function that
    #       can handle most needed lsprotocol types?
    hover = server_utils.hover(server, params, document)
    if hover is None or hover.range is None:
        return hover
    notebook_mapper = notebook_utils.notebook_coordinate_mapper(
        server.workspace, cell_uri=params.text_document.uri
    )
    if notebook_mapper is None:
        return hover
    location = notebook_mapper.cell_range(hover.range)
    if location is None or location.uri != params.text_document.uri:
        return hover
    return attrs.evolve(hover, range=location.range)


@SERVER.notebook_feature(TEXT_DOCUMENT_REFERENCES)
def references(
    server: JediLanguageServer, params: TextDocumentPositionParams
) -> Optional[List[Location]]:
    document, params = _notebook_text_document_and_params(
        server.workspace, params
    )
    locations = server_utils.references(server, params, document)
    return notebook_utils.text_document_or_cell_locations(
        server.workspace, locations
    )


@SERVER.notebook_feature(TEXT_DOCUMENT_RENAME)
def rename(
    server: JediLanguageServer, params: RenameParams
) -> Optional[WorkspaceEdit]:
    document, params = _notebook_text_document_and_params(
        server.workspace, params
    )
    return server_utils.rename(server, params, document)


@SERVER.notebook_feature(TEXT_DOCUMENT_CODE_ACTION)
def code_action(
    server: JediLanguageServer,
    params: CodeActionParams,
) -> Optional[List[CodeAction]]:
    document, params = _notebook_text_document_and_params(
        server.workspace, params
    )
    return server_utils.code_action(server, params, document)


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


def _notebook_text_document_and_params(
    workspace: Workspace,
    params: T_params,
) -> Tuple[TextDocument, T_params]:
    notebook = notebook_utils.notebook_coordinate_mapper(
        workspace, cell_uri=params.text_document.uri
    )
    if notebook is None:
        raise ValueError(
            f"Notebook not found with cell URI: {params.text_document.uri}"
        )
    document = TextDocument(uri=notebook._document.uri, source=notebook.source)

    position = getattr(params, "position", None)
    if position is not None:
        notebook_position = notebook.notebook_position(
            params.text_document.uri, position
        )
        params = attrs.evolve(params, position=notebook_position)  # type: ignore[arg-type]

    range = getattr(params, "range", None)
    if range is not None:
        notebook_range = notebook.notebook_range(
            params.text_document.uri, range
        )
        params = attrs.evolve(params, range=notebook_range)  # type: ignore[arg-type]

    return document, params


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
