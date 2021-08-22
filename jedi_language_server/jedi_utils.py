"""Utilities to work with Jedi.

Translates pygls types back and forth with Jedi
"""

from inspect import Parameter
from typing import Dict, List, Optional

import docstring_to_markdown
import jedi.api.errors
import jedi.inference.references
import jedi.settings
from jedi import Project, Script
from jedi.api.classes import Completion, Name, ParamName, Signature
from pygls.lsp.types import (
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
    SymbolKind,
)
from pygls.workspace import Document

from .initialization_options import HoverDisableOptions, InitializationOptions
from .type_map import get_lsp_completion_type, get_lsp_symbol_type


def set_jedi_settings(  # pylint: disable=invalid-name
    initialization_options: InitializationOptions,
) -> None:
    """Sets jedi settings."""
    jedi.settings.auto_import_modules = list(
        set(
            jedi.settings.auto_import_modules
            + initialization_options.jedi_settings.auto_import_modules
        )
    )

    jedi.settings.case_insensitive_completion = (
        initialization_options.jedi_settings.case_insensitive_completion
    )


def script(project: Optional[Project], document: Document) -> Script:
    """Simplifies getting jedi Script."""
    return Script(code=document.source, path=document.path, project=project)


def lsp_range(name: Name) -> Range:
    """Get LSP range from Jedi definition.

    - jedi is 1-indexed for lines and 0-indexed for columns
    - LSP is 0-indexed for lines and 0-indexed for columns
    - Therefore, subtract 1 from Jedi's definition line
    """
    return Range(
        start=Position(line=name.line - 1, character=name.column),
        end=Position(
            line=name.line - 1,
            character=name.column + len(name.name),
        ),
    )


def lsp_location(name: Name) -> Location:
    """Get LSP location from Jedi definition."""
    return Location(uri=name.module_path.as_uri(), range=lsp_range(name))


def lsp_symbol_information(name: Name) -> SymbolInformation:
    """Get LSP SymbolInformation from Jedi definition."""
    return SymbolInformation(
        name=name.name,
        kind=get_lsp_symbol_type(name.type),
        location=lsp_location(name),
        container_name=(
            "None" if name is None else (name.full_name or name.name or "None")
        ),
    )


def _document_symbol_range(name: Name) -> Range:
    """Get accurate full range of function.

    Thanks <https://github.com/CXuesong> from
    <https://github.com/palantir/python-language-server/pull/537/files> for the
    inspiration!

    Note: I add tons of extra space to make dictionary completions work. Jedi
    cuts off the end sometimes before the final function statement. This may be
    the cause of bugs at some point.
    """
    start = name.get_definition_start_position()
    end = name.get_definition_end_position()
    if start is None or end is None:
        return lsp_range(name)
    (start_line, start_column) = start
    (end_line, end_column) = end
    return Range(
        start=Position(line=start_line - 1, character=start_column),
        end=Position(line=end_line - 1, character=end_column),
    )


def lsp_document_symbols(names: List[Name]) -> List[DocumentSymbol]:
    """Get hierarchical symbols.

    We do some cleaning here. Names from scopes that aren't directly
    accessible with dot notation are removed from display. See comments
    inline for cleaning steps.
    """
    _name_lookup: Dict[Name, DocumentSymbol] = {}
    results: List[DocumentSymbol] = []
    for name in names:
        symbol = DocumentSymbol(
            name=name.name,
            kind=get_lsp_symbol_type(name.type),
            range=_document_symbol_range(name),
            selection_range=lsp_range(name),
            detail=name.description,
            children=[],
        )
        parent = name.parent()
        if parent.type == "module":
            # add module-level variables to list
            results.append(symbol)
            if name.type == "class":
                # if they're a class, they can also be a namespace
                _name_lookup[name] = symbol
        elif (
            parent.type == "class"
            and name.type == "function"
            and name.name in {"__init__"}
        ):
            # special case for __init__ method in class; names defined here
            symbol.kind = SymbolKind.Method
            parent_symbol = _name_lookup[parent]
            assert parent_symbol.children is not None
            parent_symbol.children.append(symbol)
            _name_lookup[name] = symbol
        elif parent not in _name_lookup:
            # unqualified names are not included in the tree
            continue
        elif name.is_side_effect() and name.get_line_code().strip().startswith(
            "self."
        ):
            # handle attribute creation on __init__ method
            symbol.kind = SymbolKind.Property
            parent_symbol = _name_lookup[parent]
            assert parent_symbol.children is not None
            parent_symbol.children.append(symbol)
        elif parent.type == "class":
            # children are added for class scopes
            if name.type == "function":
                # No way to identify @property decorated items. That said, as
                # far as code is concerned, @property-decorated items should be
                # considered "methods" since do more than just assign a value.
                symbol.kind = SymbolKind.Method
            else:
                symbol.kind = SymbolKind.Property
            parent_symbol = _name_lookup[parent]
            assert parent_symbol.children is not None
            parent_symbol.children.append(symbol)
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


def line_column(jedi_script: Script, position: Position) -> Dict[str, int]:
    """Translate pygls Position to Jedi's line/column.

    Returns a dictionary because this return result should be unpacked as a
    function argument to Jedi's functions.

    Jedi is 1-indexed for lines and 0-indexed for columns. LSP is 0-indexed for
    lines and 0-indexed for columns. Therefore, add 1 to LSP's request for the
    line.

    Note: as of version 3.15, LSP's treatment of "position" conflicts with
    Jedi in some cases. According to the LSP docs:

        Character offset on a line in a document (zero-based). Assuming that
        the line is represented as a string, the `character` value represents
        the gap between the `character` and `character + 1`.

        If the character value is greater than the line length it defaults back
        to the line length.

    Sources:
    https://microsoft.github.io/language-server-protocol/specification#position
    https://github.com/palantir/python-language-server/pull/201/files
    """
    lines = jedi_script._code_lines  # pylint: disable=protected-access
    line_length = len(lines[position.line])
    character = 1 if position.character == 0 else position.character
    return dict(
        line=position.line + 1,
        column=min(character, line_length - 1 if line_length else 0),
    )


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
    equal: bool = name1 == name2
    return equal


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

    Currently, removes surrounding " and '.
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
    if not signature_list:
        return "($0)"
    return "(" + ", ".join(signature_list) + ")$0"


def is_import(script_: Script, line: int, column: int) -> bool:
    """Check whether a position is a Jedi import.

    `line` and `column` are Jedi lines and columns

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
    name_is_import: bool = name.is_import()
    return name_is_import


_LSP_TYPE_FOR_SNIPPET = {
    CompletionItemKind.Class,
    CompletionItemKind.Function,
}

_MOST_RECENT_COMPLETIONS: Dict[str, Completion] = {}


def clear_completions_cache() -> None:
    """Clears the cache of completions used for completionItem/resolve."""
    _MOST_RECENT_COMPLETIONS.clear()


def lsp_completion_item(
    completion: Completion,
    char_before_cursor: str,
    enable_snippets: bool,
    resolve_eagerly: bool,
    markup_kind: MarkupKind,
) -> CompletionItem:
    """Using a Jedi completion, obtain a jedi completion item."""
    completion_name = completion.name
    name_clean = clean_completion_name(completion_name, char_before_cursor)
    lsp_type = get_lsp_completion_type(completion.type)
    completion_item = CompletionItem(
        label=completion_name,
        filter_text=completion_name,
        kind=lsp_type,
        sort_text=complete_sort_name(completion),
        insert_text=name_clean,
        insert_text_format=InsertTextFormat.PlainText,
    )

    _MOST_RECENT_COMPLETIONS[completion_name] = completion
    if resolve_eagerly:
        completion_item = lsp_completion_item_resolve(
            completion_item, markup_kind=markup_kind
        )

    if not enable_snippets:
        return completion_item
    if lsp_type not in _LSP_TYPE_FOR_SNIPPET:
        return completion_item

    signatures = completion.get_signatures()
    if not signatures:
        return completion_item

    try:
        snippet_signature = get_snippet_signature(signatures[0])
    except Exception:  # pylint: disable=broad-except
        return completion_item
    new_text = completion_name + snippet_signature
    completion_item.insert_text = new_text
    completion_item.insert_text_format = InsertTextFormat.Snippet
    return completion_item


def _md_bold(value: str, markup_kind: MarkupKind) -> str:
    """Add bold surrounding when markup_kind is markdown."""
    return f"**{value}**" if markup_kind == MarkupKind.Markdown else value


def _md_italic(value: str, markup_kind: MarkupKind) -> str:
    """Add italic surrounding when markup_kind is markdown."""
    return f"*{value}*" if markup_kind == MarkupKind.Markdown else value


def _md_text(value: str, markup_kind: MarkupKind) -> str:
    """Surround a markdown string with a Python fence."""
    return (
        f"```text\n{value}\n```"
        if markup_kind == MarkupKind.Markdown
        else value
    )


def _md_python(value: str, markup_kind: MarkupKind) -> str:
    """Surround a markdown string with a Python fence."""
    return (
        f"```python\n{value}\n```"
        if markup_kind == MarkupKind.Markdown
        else value
    )


def _md_text_sl(value: str, markup_kind: MarkupKind) -> str:
    """Surround markdown text with single line backtick."""
    return f"`{value}`" if markup_kind == MarkupKind.Markdown else value


def convert_docstring(docstring: str, markup_kind: MarkupKind) -> str:
    """Take a docstring and convert it to markup kind if possible.

    Currently only supports markdown conversion; MarkupKind can only be
    plaintext or markdown as of LSP 3.16.

    NOTE: Since docstring_to_markdown is a new library, I add broad exception
    handling in case docstring_to_markdown.convert produces unexpected
    behavior.
    """
    docstring_stripped = docstring.strip()
    if docstring_stripped == "":
        return docstring_stripped
    if markup_kind == MarkupKind.Markdown:
        try:
            return docstring_to_markdown.convert(docstring_stripped).strip()
        except docstring_to_markdown.UnknownFormatError:
            return _md_text(docstring_stripped, markup_kind)
        except Exception as error:  # pylint: disable=broad-except
            result = (
                docstring_stripped
                + "\n"
                + "jedi-language-server error: "
                + "Uncaught exception while converting docstring to markdown. "
                + "Please open issue at "
                + "https://github.com/pappasam/jedi-language-server/issues. "
                + f"Traceback:\n{error}"
            ).strip()
            return _md_text(result, markup_kind)
    return docstring_stripped


_HOVER_SIGNATURE_TYPES = {"class", "instance", "function"}

_HOVER_TYPE_TRANSLATION = {
    "module": "module",
    "class": "class",
    "instance": "instance",
    "function": "def",
    "param": "param",
    "path": "path",
    "keyword": "keyword",
    "property": "property",
    "statement": "statement",
}


def _hover_ignore(name: Name, init: InitializationOptions) -> bool:
    """True if hover should be ignored, false otherwise.

    Split into separate function for readability.

    Note: appends underscore to lookup because pydantic model requires it.
    """
    name_str = name.name
    if not name_str:
        return True
    ignore_type: HoverDisableOptions = getattr(
        init.hover.disable, name.type + "_"
    )
    return (
        ignore_type.all is True
        or name_str in ignore_type.names
        or (name.full_name or name_str) in ignore_type.full_names
    )


def hover_text(
    names: List[Name],
    markup_kind: MarkupKind,
    initialization_options: InitializationOptions,
) -> Optional[str]:
    """Get a hover string from a list of names."""
    # pylint: disable=too-many-branches
    if not names:
        return None
    name = names[0]
    if _hover_ignore(name, initialization_options):
        return None
    name_str = name.name
    name_type = name.type
    full_name = name.full_name
    hover_type = _HOVER_TYPE_TRANSLATION[name_type]
    signatures = (
        [f"{hover_type} {s.to_string()}" for s in name.get_signatures()]
        if name_type in _HOVER_SIGNATURE_TYPES
        else []
    )
    description = name.description
    docstring = name.docstring(raw=True)
    if not signatures and name_type != "class":
        try:
            type_hint = name.get_type_hint()
        except Exception:  # pylint: disable=broad-except
            # jedi randomly raises NotImplemented, TypeError, and possibly more
            # errors here. One example from jls -
            # test_hover.test_hover_on_method
            type_hint = ""
    else:
        type_hint = ""

    if signatures:
        header_plain = "\n".join(signatures)
    elif name_type == "class":
        header_plain = f"{hover_type} {name_str}"
    elif type_hint:
        header_plain = f"{name_str}: {type_hint}"
    else:
        header_plain = f"{hover_type} {name_str}"
    header = _md_python(header_plain, markup_kind)

    result: List[str] = []
    result.append(header)
    if docstring:
        result.append("---")
        result.append(convert_docstring(docstring, markup_kind))
    elif header_plain.startswith(description):
        pass
    else:
        result.append("---")
        result.append(_md_python(description, markup_kind))

    if full_name:
        if len(result) == 1:
            result.append("---")
        result.append(
            _md_bold("Full name:", markup_kind)
            + " "
            + _md_text_sl(full_name, markup_kind)
        )
    return "\n".join(result).strip()


def lsp_completion_item_resolve(
    item: CompletionItem,
    markup_kind: MarkupKind,
) -> CompletionItem:
    """Resolve completion item using cached jedi completion data."""
    completion = _MOST_RECENT_COMPLETIONS[item.label]
    item.detail = completion.description
    docstring = convert_docstring(completion.docstring(), markup_kind)
    item.documentation = MarkupContent(kind=markup_kind, value=docstring)
    return item
