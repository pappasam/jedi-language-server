"""Utility functions for converting to TextEdit.

This module is a bridge between `jedi.Refactoring` and
`pygls.types.TextEdit` types
"""


import difflib
from typing import Dict, Iterator, List, NamedTuple, Union

from jedi.api.refactoring import ChangedFile, Refactoring
from pygls.types import (
    Position,
    Range,
    RenameFileOptions,
    TextDocumentEdit,
    TextEdit,
    VersionedTextDocumentIdentifier,
)
from pygls.uris import from_fs_path


class RenameFile:  # pylint: disable=too-few-public-methods
    """Pygls has bug right now, this would be simple pull request."""

    def __init__(
        self, old_uri: str, new_uri: str, options: RenameFileOptions = None
    ):
        # pylint: disable=invalid-name
        self.kind = "rename"
        self.oldUri = old_uri
        self.newUri = new_uri
        self.options = options


def lsp_document_changes(
    refactoring: Refactoring,
) -> List[Union[TextDocumentEdit, RenameFile]]:
    """Get lsp text document edits from Jedi refactoring.

    This is the main public function that you probably want
    """
    converter = RefactoringConverter(refactoring)
    return [
        *converter.lsp_text_document_edits(),
        *converter.lsp_renames(),
    ]


class RefactoringConverter:
    """Convert jedi Refactoring objects into renaming machines."""

    def __init__(self, refactoring: Refactoring) -> None:
        self.refactoring = refactoring

    def lsp_renames(self) -> Iterator[RenameFile]:
        """Get all File rename operations."""
        for old_name, new_name in self.refactoring.get_renames():
            yield RenameFile(
                old_uri=from_fs_path(old_name),
                new_uri=from_fs_path(new_name),
                options=RenameFileOptions(
                    ignore_if_exists=True, overwrite=True
                ),
            )

    def lsp_text_document_edits(self) -> Iterator[TextDocumentEdit]:
        """Get all text document edits."""
        changed_files = self.refactoring.get_changed_files()
        for path, changed_file in changed_files.items():
            uri = from_fs_path(path)
            text_edits = lsp_text_edits(changed_file)
            yield TextDocumentEdit(
                text_document=VersionedTextDocumentIdentifier(
                    uri=uri,
                    version=None,  # type: ignore
                ),
                edits=text_edits,
            )


_OPCODES_CHANGE = {"replace", "delete", "insert"}


def lsp_text_edits(changed_file: ChangedFile) -> List[TextEdit]:
    """Take a jedi `ChangedFile` and convert to list of text edits.

    Handles inserts, replaces, and deletions within a text file
    """
    old_code = (
        changed_file._module_node.get_code()  # pylint: disable=protected-access
    )
    new_code = changed_file.get_new_code()
    opcode_position_lookup_old = get_opcode_position_lookup(old_code)
    text_edits = []
    for opcode in get_opcodes(old_code, new_code):
        if opcode.op in _OPCODES_CHANGE:
            start = opcode_position_lookup_old[opcode.old_start]
            end = opcode_position_lookup_old[opcode.old_end]
            start_char = opcode.old_start - start.range_start
            end_char = opcode.old_end - end.range_start
            new_text = new_code[opcode.new_start : opcode.new_end]
            text_edits.append(
                TextEdit(
                    range=Range(
                        start=Position(line=start.line, character=start_char),
                        end=Position(line=end.line, character=end_char),
                    ),
                    new_text=new_text,
                )
            )
    return text_edits


class Opcode(NamedTuple):
    """Typed opcode.

    Op can be one of the following values:
        'replace':  a[i1:i2] should be replaced by b[j1:j2]
        'delete':   a[i1:i2] should be deleted.
            Note that j1==j2 in this case.
        'insert':   b[j1:j2] should be inserted at a[i1:i1].
            Note that i1==i2 in this case.
        'equal':    a[i1:i2] == b[j1:j2]
    """

    op: str
    old_start: int
    old_end: int
    new_start: int
    new_end: int


def get_opcodes(old: str, new: str) -> List[Opcode]:
    """Obtain typed opcodes from two files (old and new)"""
    diff = difflib.SequenceMatcher(a=old, b=new)
    return [Opcode(*opcode) for opcode in diff.get_opcodes()]


class LinePosition(NamedTuple):
    """Container to map absolute text position to lines and columns."""

    range_start: int
    range_end: int
    line: int
    code: str


class RangeDict(dict):
    """Range dict.

    Copied from: https://stackoverflow.com/a/39358140
    """

    def __getitem__(self, item):
        if not isinstance(item, range):
            for key in self:
                if item in key:
                    return self[key]
            raise KeyError(item)
        return super().__getitem__(item)


def get_opcode_position_lookup(
    code: str,
) -> Dict[int, LinePosition]:
    """Obtain the opcode lookup position.

    This function is beautiful. It takes code and creates a data
    structure within which one can look up opcode-friendly values. It
    relies on the `RangeDict` above, which lets you look up a value
    within a range of linear values
    """
    original_lines = code.splitlines(keepends=True)
    line_lookup = RangeDict()
    start = 0
    for line, code_line in enumerate(original_lines):
        end = start + len(code_line)
        key = range(start, end + 1)  # must be 1 greater than last item
        line_lookup[key] = LinePosition(start, end, line, code_line)
        start = end
    return line_lookup
