"""Utilities to work with Jedi.

Translates pygls types back and forth with Jedi
"""

import random
import string  # pylint: disable=deprecated-module
from inspect import Parameter
from typing import Dict, List, Optional, Tuple

import jedi.api.errors
import jedi.inference.references
import jedi.settings
from jedi import Project, Script
from jedi.api.classes import Completion, Name, ParamName, Signature
from pygls.types import (
    CompletionItem,
    CompletionItemKind,
    Diagnostic,
    DiagnosticSeverity,
    DocumentSymbol,
    InsertTextFormat,
    Location,
    MarkupContent,
    MarkupKind,
    Position,
    Range,
    SymbolInformation,
)
from pygls.uris import from_fs_path
from pygls.workspace import Workspace

from .initialize_params_parser import InitializeParamsParser
from .type_map import get_lsp_completion_type, get_lsp_symbol_type


def set_jedi_settings(  # pylint: disable=invalid-name
    ip: InitializeParamsParser,
) -> None:
    """Sets jedi settings."""
    jedi.settings.auto_import_modules = list(
        set(
            jedi.settings.auto_import_modules
            + ip.initializationOptions_jediSettings_autoImportModules
        )
    )


def script(workspace: Workspace, uri: str) -> Script:
    """Simplifies getting jedi Script."""
    project_ = project(workspace)
    document = workspace.get_document(uri)
    return Script(code=document.source, path=document.path, project=project_)


def project(workspace: Workspace) -> Project:
    """Simplifies getting jedi project."""
    return Project(
        path=workspace.root_path,
        smart_sys_path=True,
        load_unsafe_extensions=False,
    )


def lsp_range(name: Name) -> Range:
    """Get LSP range from Jedi definition.

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
    """Get LSP location from Jedi definition."""
    return Location(uri=from_fs_path(name.module_path), range=lsp_range(name))


def lsp_symbol_information(name: Name) -> SymbolInformation:
    """Get LSP SymbolInformation from Jedi definition."""
    return SymbolInformation(
        name=name.name,
        kind=get_lsp_symbol_type(name.type),
        location=lsp_location(name),
        container_name=name.parent(),
    )


def _get_definition_start_position(name: Name) -> Optional[Tuple[int, int]]:
    """Start of the definition range. Rows start with 1, columns with 0.

    NOTE: replace with public method when Jedi 0.17.1 released
    """
    # pylint: disable=protected-access
    if name._name.tree_name is None:
        return None
    definition = name._name.tree_name.get_definition()
    if definition is None:
        return name._name.start_pos
    return definition.start_pos


def _get_definition_end_position(name: Name) -> Optional[Tuple[int, int]]:
    """End of the definition range. Rows start with 1, columns with 0.

    NOTE: replace with public method when Jedi 0.17.1 released
    """
    # pylint: disable=protected-access
    if name._name.tree_name is None:
        return None
    definition = name._name.tree_name.get_definition()
    if definition is None:
        return name._name.tree_name.end_pos
    if name.type in ("function", "class"):
        last_leaf = definition.get_last_leaf()
        if last_leaf.type == "newline":
            return last_leaf.get_previous_leaf().end_pos
        return last_leaf.end_pos
    return definition.end_pos


def _document_symbol_range(name: Name) -> Range:
    """Get accurate full range of function.

    Thanks https://github.com/CXuesong from
    https://github.com/palantir/python-language-server/pull/537/files for the
    inspiration!

    Note: I add tons of extra space to make dictionary completions work. Jedi
    cuts off the end sometimes before the final function statement. This may be
    the cause of bugs at some point.
    """
    start = _get_definition_start_position(name)
    end = _get_definition_end_position(name)
    if start is None or end is None:
        return lsp_range(name)
    (start_line, start_column) = start
    (end_line, end_column) = end
    return Range(
        start=Position(start_line - 1, start_column),
        end=Position(end_line - 1, end_column),
    )


def lsp_document_symbols(names: List[Name]) -> List[DocumentSymbol]:
    """Get hierarchical symbols."""
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
    """Get LSP Diagnostic from Jedi SyntaxError."""
    return Diagnostic(
        range=Range(
            start=Position(line=error.line - 1, character=error.column),
            end=Position(
                line=error.until_line - 1, character=error.until_column
            ),
        ),
        message=error.get_message(),
        severity=DiagnosticSeverity.Error,
        source="jedi",
    )


def line_column(position: Position) -> Dict[str, int]:
    """Translate pygls Position to Jedi's line/column.

    Returns a dictionary because this return result should be unpacked as a
    function argument to Jedi's functions.

    Jedi is 1-indexed for lines and 0-indexed for columns. LSP is 0-indexed for
    lines and 0-indexed for columns. Therefore, add 1 to LSP's request for the
    line.
    """
    return dict(line=position.line + 1, column=position.character)


def line_column_range(pygls_range: Range) -> Dict[str, int]:
    """Translate pygls range to Jedi's line/column/until_line/until_column.

    Returns a dictionary because this return result should be unpacked as a
    function argument to Jedi's functions.

    Jedi is 1-indexed for lines and 0-indexed for columns. LSP is 0-indexed for
    lines and 0-indexed for columns. Therefore, add 1 to LSP's request for the
    line.
    """
    return dict(
        line=pygls_range.start.line + 1,
        column=pygls_range.start.character,
        until_line=pygls_range.end.line + 1,
        until_column=pygls_range.end.character,
    )


def compare_names(name1: Name, name2: Name) -> bool:
    """Check if one Name is equal to another.

    This function, while trivial, is useful for documenting types
    without needing to directly import anything from jedi into
    `server.py`
    """
    return name1 == name2


def complete_sort_name(name: Completion) -> str:
    """Return sort name for a jedi completion.

    Should be passed to the sortText field in CompletionItem. Strings sort a-z,
    a comes first and z comes last.

    Additionally, we'd like to keep the sort order to what Jedi has provided.
    For this reason, we make sure the sort-text is just a letter and not the
    name itself.
    """
    if name.type == "param" and name.name.endswith("="):
        return "a"
    return "z"


def clean_completion_name(name: str, char_before_cursor: str) -> str:
    """Clean the completion name, stripping bad surroundings.

    1. Remove all surrounding " and '. For
    """
    if char_before_cursor in {"'", '"'}:
        return name.lstrip(char_before_cursor)
    return name


_POSITION_PARAMETERS = {
    Parameter.POSITIONAL_ONLY,
    Parameter.POSITIONAL_OR_KEYWORD,
}

_PARAM_NAME_IGNORE = {"/", "*"}


def get_snippet_signature(signature: Signature) -> str:
    """Return the snippet signature."""
    params: List[ParamName] = signature.params
    if not params:
        return "()$0"
    signature_list = []
    count = 1
    for param in params:
        param_name = param.name
        if param_name in _PARAM_NAME_IGNORE:
            continue
        if param.kind in _POSITION_PARAMETERS:
            param_str = param.to_string()
            if "=" in param_str:  # hacky default argument check
                break
            result = "${" + f"{count}:{param_name}" + "}"
            signature_list.append(result)
            count += 1
            continue
        if param.kind == Parameter.KEYWORD_ONLY:
            result = param_name + "=${" + f"{count}:..." + "}"
            signature_list.append(result)
            count += 1
            continue
    if not signature_list:
        return "($0)"
    return "(" + ", ".join(signature_list) + ")$0"


def is_import(script_: Script, line: int, column: int) -> bool:
    """Check whether a position is a Jedi import.

    line and column are Jedi lines and columns

    NOTE: this function is a bit of a hack and should be revisited with each
    Jedi release. Additionally, it doesn't really work for manually-triggered
    completions, without any text, which will may cause issues for users with
    manually triggered completions.
    """
    # pylint: disable=protected-access
    tree_name = script_._module_node.get_name_of_position((line, column))
    if tree_name is None:
        return False
    name = script_._get_module_context().create_name(tree_name)
    if name is None:
        return False
    return name.is_import()


_LSP_TYPE_FOR_SNIPPET = {
    CompletionItemKind.Class,
    CompletionItemKind.Function,
}


def lsp_completion_item(
    name: Completion,
    char_before_cursor: str,
    enable_snippets: bool,
    markup_kind: MarkupKind,
) -> CompletionItem:
    """Using a Jedi completion, obtain a jedi completion item."""
    name_name = name.name
    name_clean = clean_completion_name(name_name, char_before_cursor)
    lsp_type = get_lsp_completion_type(name.type)
    completion_item = CompletionItem(
        label=name_name,
        filter_text=name_name,
        kind=lsp_type,
        detail=name.description,
        documentation=MarkupContent(kind=markup_kind, value=name.docstring()),
        sort_text=complete_sort_name(name),
        insert_text=name_clean,
        insert_text_format=InsertTextFormat.PlainText,
    )
    if not enable_snippets:
        return completion_item
    if lsp_type not in _LSP_TYPE_FOR_SNIPPET:
        return completion_item

    signatures = name.get_signatures()
    if not signatures:
        return completion_item

    try:
        snippet_signature = get_snippet_signature(signatures[0])
    except Exception:  # pylint: disable=broad-except
        return completion_item
    new_text = name_name + snippet_signature
    completion_item.insertText = new_text
    completion_item.insertTextFormat = InsertTextFormat.Snippet
    return completion_item


def random_var(
    beginning: str,
    random_length: int = 8,
    letters: str = string.ascii_lowercase,
) -> str:
    """Generate a random variable name.

    Useful for refactoring functions
    """
    ending = "".join(random.choice(letters) for _ in range(random_length))
    return beginning + ending
