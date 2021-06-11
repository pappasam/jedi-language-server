"""Module containing the InitializationOptions parser.

Provides a fully defaulted pydantic model for this language server's
initialization options.
"""

from typing import List, Optional, Set, Union

from pydantic import BaseModel, Field
from pygls.lsp.types import MarkupKind

# pylint: disable=missing-class-docstring
# pylint: disable=too-few-public-methods


def snake_to_camel(string: str) -> str:
    """Convert from snake_case to camelCase."""
    return "".join(
        word.capitalize() if idx > 0 else word
        for idx, word in enumerate(string.split("_"))
    )


class Model(BaseModel):
    class Config:
        alias_generator = snake_to_camel


class CodeAction(Model):
    name_extract_variable: str = "jls_extract_var"
    name_extract_function: str = "jls_extract_def"


class Completion(Model):
    disable_snippets: bool = False
    resolve_eagerly: bool = False


class Diagnostics(Model):
    enable: bool = True
    did_open: bool = True
    did_save: bool = True
    did_change: bool = True


class HoverIgnoreChooseOptions(Model):
    names: Set[str] = set()
    full_names: Set[str] = set()


HoverIgnoreChoose = Union[HoverIgnoreChooseOptions, bool]


class HoverIgnore(Model):
    """All Attributes have _ appended to avoid syntax conflicts.

    For example, the keyword class would have required a special case.
    To get around this, I decided it's simpler to always assume an
    underscore at the end.
    """

    keyword_: HoverIgnoreChoose = Field(default=False, alias="keyword")
    module_: HoverIgnoreChoose = Field(default=False, alias="module")
    class_: HoverIgnoreChoose = Field(default=False, alias="class")
    instance_: HoverIgnoreChoose = Field(default=False, alias="instance")
    function_: HoverIgnoreChoose = Field(default=False, alias="function")
    param_: HoverIgnoreChoose = Field(default=False, alias="param")
    path_: HoverIgnoreChoose = Field(default=False, alias="path")
    keyword_: HoverIgnoreChoose = Field(default=False, alias="keyword")
    property_: HoverIgnoreChoose = Field(default=False, alias="property")
    statement_: HoverIgnoreChoose = Field(default=False, alias="statement")


class Hover(Model):
    ignore: HoverIgnore = HoverIgnore()


class JediSettings(Model):
    auto_import_modules: List[str] = []
    case_insensitive_completion: bool = True


class Symbols(Model):
    ignore_folders: List[str] = [".nox", ".tox", ".venv", "__pycache__"]
    max_symbols: int = 20


class Workspace(Model):
    extra_paths: List[str] = []
    symbols: Symbols = Symbols()


class InitializationOptions(Model):
    code_action: CodeAction = CodeAction()
    completion: Completion = Completion()
    diagnostics: Diagnostics = Diagnostics()
    hover: Hover = Hover()
    jedi_settings: JediSettings = JediSettings()
    markup_kind_preferred: Optional[MarkupKind]
    workspace: Workspace = Workspace()
