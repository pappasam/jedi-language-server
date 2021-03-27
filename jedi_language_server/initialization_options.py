"""Module containing the InitializationOptions parser.

Provides a fully defaulted pydantic model for this language server's
initialization options.
"""

from typing import List, Optional

from pydantic import BaseModel
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
    jedi_settings: JediSettings = JediSettings()
    markup_kind_preferred: Optional[MarkupKind]
    workspace: Workspace = Workspace()
