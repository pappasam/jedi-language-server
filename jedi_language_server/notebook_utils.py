"""Utility functions for handling notebook documents."""

from collections import defaultdict
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    NamedTuple,
    Optional,
    Protocol,
    TypeVar,
    Union,
    cast,
)

import attrs
from lsprotocol.types import (
    AnnotatedTextEdit,
    CallHierarchyPrepareParams,
    CodeActionParams,
    ColorPresentationParams,
    CompletionParams,
    DefinitionParams,
    DocumentHighlightParams,
    DocumentOnTypeFormattingParams,
    Hover,
    HoverParams,
    InlayHintParams,
    InlineValueParams,
    Location,
    NotebookDocument,
    OptionalVersionedTextDocumentIdentifier,
    Position,
    PrepareRenameParams,
    Range,
    ReferenceParams,
    RenameParams,
    SemanticTokensRangeParams,
    SignatureHelpParams,
    TextDocumentEdit,
    TextDocumentIdentifier,
    TextDocumentPositionParams,
    TextEdit,
)
from pygls.server import LanguageServer
from pygls.workspace import TextDocument, Workspace


def notebook_coordinate_mapper(
    workspace: Workspace,
    *,
    notebook_uri: Optional[str] = None,
    cell_uri: Optional[str] = None,
) -> Optional["NotebookCoordinateMapper"]:
    notebook_document = workspace.get_notebook_document(
        notebook_uri=notebook_uri, cell_uri=cell_uri
    )
    if notebook_document is None:
        return None
    cells = [
        workspace.text_documents[cell.document]
        for cell in notebook_document.cells
    ]
    return NotebookCoordinateMapper(notebook_document, cells)


class DocumentPosition(NamedTuple):
    """A position in a document."""

    uri: str
    position: Position


class DocumentTextEdit(NamedTuple):
    """A text edit in a document."""

    uri: str
    text_edit: Union[TextEdit, AnnotatedTextEdit]


class NotebookCoordinateMapper:
    """Maps positions between individual notebook cells and the concatenated notebook document."""

    def __init__(
        self,
        notebook_document: NotebookDocument,
        cells: List[TextDocument],
    ):
        self._document = notebook_document
        self._cells = cells

        # Construct helper data structures.
        self._cell_by_uri: Dict[str, TextDocument] = {}
        self._cell_line_range_by_uri: Dict[str, range] = {}
        start_line = 0
        for index, cell in enumerate(self._cells):
            end_line = start_line + len(cell.lines)

            self._cell_by_uri[cell.uri] = cell
            self._cell_line_range_by_uri[cell.uri] = range(
                start_line, end_line
            )

            start_line = end_line

    @property
    def source(self) -> str:
        """Concatenated notebook source."""
        return "\n".join(cell.source for cell in self._cells)

    def notebook_position(
        self, cell_uri: str, cell_position: Position
    ) -> Position:
        """Convert a cell position to a concatenated notebook position."""
        line = (
            self._cell_line_range_by_uri[cell_uri].start + cell_position.line
        )
        return Position(line=line, character=cell_position.character)

    def notebook_range(self, cell_uri: str, cell_range: Range) -> Range:
        """Convert a cell range to a concatenated notebook range."""
        start = self.notebook_position(cell_uri, cell_range.start)
        end = self.notebook_position(cell_uri, cell_range.end)
        return Range(start=start, end=end)

    def cell_position(
        self, notebook_position: Position
    ) -> Optional[DocumentPosition]:
        """Convert a concatenated notebook position to a cell position."""
        for cell in self._cells:
            line_range = self._cell_line_range_by_uri[cell.uri]
            if notebook_position.line in line_range:
                line = notebook_position.line - line_range.start
                return DocumentPosition(
                    uri=cell.uri,
                    position=Position(
                        line=line, character=notebook_position.character
                    ),
                )
        return None

    def cell_range(self, notebook_range: Range) -> Optional[Location]:
        """Convert a concatenated notebook range to a cell range.

        Returns a `Location` to identify the cell that the range is in.
        """
        start = self.cell_position(notebook_range.start)
        if start is None:
            return None

        end = self.cell_position(notebook_range.end)
        if end is None:
            return None

        if start.uri != end.uri:
            return None

        return Location(
            uri=start.uri, range=Range(start=start.position, end=end.position)
        )

    def cell_location(self, notebook_location: Location) -> Optional[Location]:
        """Convert a concatenated notebook location to a cell location."""
        if notebook_location.uri != self._document.uri:
            return None
        return self.cell_range(notebook_location.range)

    def cell_index(self, cell_uri: str) -> Optional[int]:
        """Get the index of a cell by its URI."""
        for index, cell in enumerate(self._cells):
            if cell.uri == cell_uri:
                return index
        return None

    def cell_text_edit(
        self, text_edit: Union[TextEdit, AnnotatedTextEdit]
    ) -> Optional[DocumentTextEdit]:
        """Convert a concatenated notebook text edit to a cell text edit."""
        location = self.cell_range(text_edit.range)
        if location is None:
            return None

        return DocumentTextEdit(
            uri=location.uri,
            text_edit=attrs.evolve(text_edit, range=location.range),
        )

    def cell_text_document_edits(
        self, text_document_edit: TextDocumentEdit
    ) -> Iterable[TextDocumentEdit]:
        """Convert a concatenated notebook text document edit to cell text document edits."""
        if text_document_edit.text_document.uri != self._document.uri:
            return

        # Convert edits in the concatenated notebook to per-cell edits, grouped by cell URI.
        edits_by_uri: Dict[str, List[Union[TextEdit, AnnotatedTextEdit]]] = (
            defaultdict(list)
        )
        for text_edit in text_document_edit.edits:
            cell_text_edit = self.cell_text_edit(text_edit)
            if cell_text_edit is not None:
                edits_by_uri[cell_text_edit.uri].append(
                    cell_text_edit.text_edit
                )

        # Yield per-cell text document edits.
        for uri, edits in edits_by_uri.items():
            cell = self._cell_by_uri[uri]
            version = 0 if cell.version is None else cell.version
            yield TextDocumentEdit(
                text_document=OptionalVersionedTextDocumentIdentifier(
                    uri=cell.uri, version=version
                ),
                edits=edits,
            )


def text_document_or_cell_locations(
    workspace: Workspace, locations: Optional[List[Location]]
) -> Optional[List[Location]]:
    """Convert concatenated notebook locations to cell locations, leaving text document locations as-is."""
    if locations is None:
        return None

    results = []
    for location in locations:
        mapper = notebook_coordinate_mapper(
            workspace, notebook_uri=location.uri
        )
        if mapper is not None:
            cell_location = mapper.cell_location(location)
            if cell_location is not None:
                location = cell_location

        results.append(location)

    return results if results else None


def cell_index(workspace: Workspace, cell_uri: str) -> int:
    notebook = notebook_coordinate_mapper(workspace, cell_uri=cell_uri)
    if notebook is None:
        raise ValueError(
            f"Notebook document not found for cell URI: {cell_uri}"
        )
    index = notebook.cell_index(cell_uri)
    assert index is not None
    return index


TextDocumentPositionParamsTypes = (
    CompletionParams,
    RenameParams,
    TextDocumentPositionParams,
)
T_ls = TypeVar("T_ls", bound=LanguageServer)


class _TextDocumentPositionParams(Protocol):
    text_document: TextDocumentIdentifier
    position: Position


class _TextDocumentRangeParams(Protocol):
    text_document: TextDocumentIdentifier
    range: Range


_TextDocumentPositionOrRangeParams = Union[
    _TextDocumentPositionParams, _TextDocumentRangeParams
]

T_params = TypeVar(
    "T_params",
    # # Position
    # CallHierarchyPrepareParams,
    # CompletionParams,
    # DefinitionParams,
    # DocumentHighlightParams,
    # DocumentOnTypeFormattingParams,
    # HoverParams,
    # PrepareRenameParams,
    # ReferenceParams,
    # RenameParams,
    # SignatureHelpParams,
    # TextDocumentPositionParams,
    # # Range
    # CodeActionParams,
    # ColorPresentationParams,
    # InlayHintParams,
    # InlineValueParams,
    # SemanticTokensRangeParams,
    bound=_TextDocumentPositionOrRangeParams,
)


T = TypeVar("T")


class ServerWrapper:
    def __init__(self, server: LanguageServer):
        self._wrapped = server
        self.workspace = WorkspaceWrapper(server.workspace)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._wrapped, name)


class WorkspaceWrapper:
    def __init__(self, workspace: Workspace):
        self._wrapped = workspace

    def __getattr__(self, name: str) -> Any:
        return getattr(self._wrapped, name)

    def get_text_document(self, doc_uri: str) -> TextDocument:
        notebook = notebook_coordinate_mapper(self._wrapped, cell_uri=doc_uri)
        if notebook is None:
            return self._wrapped.get_text_document(doc_uri)
        return TextDocument(uri=notebook._document.uri, source=notebook.source)


def _pre(notebook: NotebookCoordinateMapper, params: T_params) -> T_params:
    if isinstance(
        params,
        (
            CallHierarchyPrepareParams,
            CompletionParams,
            DefinitionParams,
            DocumentHighlightParams,
            DocumentOnTypeFormattingParams,
            HoverParams,
            PrepareRenameParams,
            ReferenceParams,
            RenameParams,
            SignatureHelpParams,
            TextDocumentPositionParams,
        ),
    ):
        notebook_position = notebook.notebook_position(
            params.text_document.uri, params.position
        )
        return cast(T_params, attrs.evolve(params, position=notebook_position))

    if isinstance(
        params,
        (
            CodeActionParams,
            ColorPresentationParams,
            InlayHintParams,
            InlineValueParams,
            SemanticTokensRangeParams,
        ),
    ):
        notebook_range = notebook.notebook_range(
            params.text_document.uri, params.range
        )
        return cast(T_params, attrs.evolve(params, range=notebook_range))

    return params


def _post(
    workspace: Workspace,
    notebook: Optional[NotebookCoordinateMapper],
    params: _TextDocumentPositionOrRangeParams,
    result: T,
) -> T:
    if isinstance(result, list) and result and isinstance(result[0], Location):
        return cast(T, text_document_or_cell_locations(workspace, result))

    if (
        notebook is not None
        and isinstance(result, Hover)
        and result.range is not None
    ):
        location = notebook.cell_range(result.range)
        if location is not None and location.uri == params.text_document.uri:
            return cast(T, attrs.evolve(result, range=location.range))

    return result


def supports_notebooks(
    f: Callable[[T_ls, T_params], T],
) -> Callable[[T_ls, T_params], T]:
    def wrapped(ls: T_ls, params: T_params) -> T:
        notebook = notebook_coordinate_mapper(
            ls.workspace, cell_uri=params.text_document.uri
        )
        params = _pre(notebook, params) if notebook else params
        result = f(ls, params)
        return _post(ls.workspace, notebook, params, result)

    return wrapped


def cell_filename(
    workspace: Workspace,
    cell_uri: str,
) -> str:
    notebook = notebook_coordinate_mapper(workspace, cell_uri=cell_uri)
    if notebook is None:
        raise ValueError(
            f"Notebook document not found for cell URI: {cell_uri}"
        )
    index = notebook.cell_index(cell_uri)
    assert index is not None
    return f"cell {index + 1}"
