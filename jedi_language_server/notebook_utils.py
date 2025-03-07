"""Utility functions for handling notebook documents."""

from __future__ import annotations

from collections import defaultdict
from typing import (
    TYPE_CHECKING,
    Callable,
    Dict,
    Iterable,
    List,
    NamedTuple,
    Optional,
    Tuple,
    TypeVar,
    Union,
    cast,
)

import attrs
from lsprotocol.types import (
    AnnotatedTextEdit,
    CodeActionParams,
    CompletionParams,
    Hover,
    Location,
    NotebookDocument,
    OptionalVersionedTextDocumentIdentifier,
    Position,
    Range,
    RenameParams,
    TextDocumentEdit,
    TextDocumentPositionParams,
    TextEdit,
)
from pygls.uris import to_fs_path
from pygls.workspace import TextDocument, Workspace

if TYPE_CHECKING:
    from .server import JediLanguageServer


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
        # msg = "Notebook document not found for"
        # if notebook_uri is not None:
        #     msg += f" notebook_uri={notebook_uri}"
        # if cell_uri is not None:
        #     msg += f" cell_uri={cell_uri}"
        # raise ValueError(msg)
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
    def path(self) -> str:
        path = to_fs_path(self._document.uri)
        if path is None:
            raise ValueError("Could not convert notebook URI to path")
        return cast(str, path)

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


NotebookSupportedParams = Union[
    CodeActionParams,
    CompletionParams,
    RenameParams,
    TextDocumentPositionParams,
]
T_params = TypeVar(
    "T_params",
    bound=NotebookSupportedParams,
)


def notebook_text_document_and_params(
    workspace: Workspace,
    params: T_params,
) -> Tuple[TextDocument, T_params]:
    notebook = notebook_coordinate_mapper(
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


T = TypeVar("T")


def with_notebook_support(
    f: Callable[
        [JediLanguageServer, T_params, Optional[TextDocument]],
        T,
    ],
) -> Callable[[JediLanguageServer, T_params], T]:
    def wrapped(server: JediLanguageServer, params: T_params) -> T:
        document, params = notebook_text_document_and_params(
            server.workspace, params
        )
        result = f(server, params, document)

        if (
            isinstance(result, list)
            and result
            and isinstance(result[0], Location)
        ):
            return cast(
                T, text_document_or_cell_locations(server.workspace, result)
            )

        if isinstance(result, Hover) and result.range is not None:
            notebook_mapper = notebook_coordinate_mapper(
                server.workspace, cell_uri=params.text_document.uri
            )
            if notebook_mapper is None:
                return cast(T, result)
            location = notebook_mapper.cell_range(result.range)
            if location is None or location.uri != params.text_document.uri:
                return cast(T, result)
            return cast(T, attrs.evolve(result, range=location.range))

        return result

    return wrapped
