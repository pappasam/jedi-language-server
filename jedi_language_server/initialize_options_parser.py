"""Module containing the InitializationOptions parser.

This parser handles the following tasks for the InitializationOptions:

- storage / accessibility outside the initialize request
- configuring option defaults
- organizing initialization values in one place
"""

from typing import Any, Dict, List, Optional

from pygls.lsp.types import MarkupKind

from .pygls_utils import rget

try:
    from functools import cached_property  # type: ignore
except ImportError:
    from cached_property import cached_property  # type: ignore


# pylint: disable=invalid-name
# pylint: disable=missing-function-docstring


class InitializationOptionsParser:
    """Class to parse and manage InitializationOptions."""

    def __init__(self) -> None:
        self.initialization_options: Optional[Dict[str, Any]] = None

    @cached_property
    def markupKindPreferred(
        self,
    ) -> Optional[MarkupKind]:
        path = ["markupKindPreferred"]
        result = rget(self.initialization_options, path)
        return result if result is None else MarkupKind(result)

    @cached_property
    def completion_disableSnippets(self) -> bool:
        path = [
            "completion",
            "disableSnippets",
        ]
        result = rget(self.initialization_options, path)
        return False if result is None else result

    @cached_property
    def completion_resolveEagerly(self) -> bool:
        path = [
            "completion",
            "resolveEagerly",
        ]
        result = rget(self.initialization_options, path)
        return False if result is None else result

    @cached_property
    def diagnostics_enable(self) -> bool:
        path = [
            "diagnostics",
            "enable",
        ]
        result = rget(self.initialization_options, path)
        return True if result is None else result

    @cached_property
    def diagnostics_didOpen(self) -> bool:
        path = [
            "diagnostics",
            "didOpen",
        ]
        result = rget(self.initialization_options, path)
        return True if result is None else result

    @cached_property
    def diagnostics_didSave(self) -> bool:
        path = [
            "diagnostics",
            "didSave",
        ]
        result = rget(self.initialization_options, path)
        return True if result is None else result

    @cached_property
    def diagnostics_didChange(self) -> bool:
        path = [
            "diagnostics",
            "didChange",
        ]
        result = rget(self.initialization_options, path)
        return True if result is None else result

    @cached_property
    def jediSettings_autoImportModules(
        self,
    ) -> List[str]:
        path = [
            "jediSettings",
            "autoImportModules",
        ]
        result = rget(self.initialization_options, path)
        return [] if result is None else result

    @cached_property
    def jediSettings_caseInsensitiveCompletion(
        self,
    ) -> bool:
        path = [
            "jediSettings",
            "caseInsensitiveCompletion",
        ]
        result = rget(self.initialization_options, path)
        return True if result is None else result

    @cached_property
    def workspace_extraPaths(
        self,
    ) -> List[str]:
        path = [
            "workspace",
            "extraPaths",
        ]
        result = rget(self.initialization_options, path)
        return [] if result is None else result

    @cached_property
    def workspace_symbols_ignoreFolders(
        self,
    ) -> List[str]:
        path = [
            "workspace",
            "symbols",
            "ignoreFolders",
        ]
        default = [
            ".nox",
            ".tox",
            ".venv",
            "__pycache__",
            "venv",
        ]
        result = rget(self.initialization_options, path)
        return default if result is None else result

    @cached_property
    def workspace_symbols_maxSymbols(
        self,
    ) -> int:
        path = [
            "workspace",
            "symbols",
            "maxSymbols",
        ]
        result = rget(self.initialization_options, path)
        return 20 if result is None else result
