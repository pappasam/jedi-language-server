"""Module containing the InitializeParams parser.

This parser handles the following tasks for the InitializeParams:

- storage / accessibility outside the initialize request
- configuring option defaults
- organizing initialization values in one place
"""

from typing import Any, Dict, List, Optional

from pygls.lsp.types import InitializeParams, MarkupKind

from .pygls_utils import rget

try:
    from functools import cached_property  # type: ignore
except ImportError:
    from cached_property import cached_property  # type: ignore


# pylint: disable=line-too-long
# pylint: disable=invalid-name
# pylint: disable=missing-function-docstring


class InitializeParamsParser:
    """Class to parse and manage InitializeParams."""

    def __init__(self) -> None:
        self._initialize_params_store: Optional[InitializeParams] = None

    @cached_property
    def _initialize_params(self) -> InitializeParams:
        """Get the initialize params."""
        if self._initialize_params_store is None:
            raise ValueError("InitializeParams not set")
        return self._initialize_params_store

    @property
    def _initialization_options(self) -> Optional[Dict[str, Any]]:
        """Get the initialization options."""
        return self._initialize_params.initialization_options

    def set_initialize_params(self, params: InitializeParams) -> None:
        """Set the initialize params."""
        self._initialize_params_store = params

    @cached_property
    def capabilities_textDocument_completion_completionItem_documentationFormat(
        self,
    ) -> List[MarkupKind]:
        result = self._initialize_params.capabilities.get_capability(
            "text_document.completion.completion_item.documentation_format",
            [MarkupKind.PlainText]
        )
        return result

    @cached_property
    def capabilities_textDocument_completion_completionItem_snippetSupport(
        self,
    ) -> bool:
        result = self._initialize_params.capabilities.get_capability(
            "text_document.completion.completion_item.snippet_support",
            False
        )
        return result

    @cached_property
    def capabilities_textDocument_documentSymbol_hierarchicalDocumentSymbolSupport(
        self,
    ) -> bool:
        result = self._initialize_params.capabilities.get_capability(
            "text_document.document_symbol.hierarchical_document_symbol_support",
            False
        )
        return result

    @cached_property
    def capabilities_textDocument_hover_contentFormat(
        self,
    ) -> List[MarkupKind]:
        result = self._initialize_params.capabilities.get_capability(
            "text_document.hover.content_format",
            [MarkupKind.PlainText]
        )
        return result

    @cached_property
    def capabilities_textDocument_signatureHelp_contentFormat(
        self,
    ) -> List[str]:
        result = self._initialize_params.capabilities.get_capability(
            "text_document.signature_help.content_format",
            [MarkupKind.PlainText]
        )
        return result

    @cached_property
    def initializationOptions_markupKindPreferred(
        self,
    ) -> Optional[MarkupKind]:
        path = ["markupKindPreferred"]
        result = rget(self._initialization_options, path)
        return result if result is None else MarkupKind(result)

    @cached_property
    def initializationOptions_completion_disableSnippets(self) -> bool:
        path = [
            "completion",
            "disableSnippets",
        ]
        result = rget(self._initialization_options, path)
        return False if result is None else result

    @cached_property
    def initializationOptions_completion_resolveEagerly(self) -> bool:
        path = [
            "completion",
            "resolveEagerly",
        ]
        result = rget(self._initialization_options, path)
        return False if result is None else result

    @cached_property
    def initializationOptions_diagnostics_enable(self) -> bool:
        path = [
            "diagnostics",
            "enable",
        ]
        result = rget(self._initialization_options, path)
        return True if result is None else result

    @cached_property
    def initializationOptions_diagnostics_didOpen(self) -> bool:
        path = [
            "diagnostics",
            "didOpen",
        ]
        result = rget(self._initialization_options, path)
        return True if result is None else result

    @cached_property
    def initializationOptions_diagnostics_didSave(self) -> bool:
        path = [
            "diagnostics",
            "didSave",
        ]
        result = rget(self._initialization_options, path)
        return True if result is None else result

    @cached_property
    def initializationOptions_diagnostics_didChange(self) -> bool:
        path = [
            "diagnostics",
            "didChange",
        ]
        result = rget(self._initialization_options, path)
        return True if result is None else result

    @cached_property
    def initializationOptions_jediSettings_autoImportModules(
        self,
    ) -> List[str]:
        path = [
            "jediSettings",
            "autoImportModules",
        ]
        result = rget(self._initialization_options, path)
        return [] if result is None else result

    @cached_property
    def initializationOptions_jediSettings_caseInsensitiveCompletion(
        self,
    ) -> bool:
        path = [
            "jediSettings",
            "caseInsensitiveCompletion",
        ]
        result = rget(self._initialization_options, path)
        return True if result is None else result

    @cached_property
    def initializationOptions_workspace_extraPaths(
        self,
    ) -> List[str]:
        path = [
            "workspace",
            "extraPaths",
        ]
        result = rget(self._initialization_options, path)
        return [] if result is None else result

    @cached_property
    def initializationOptions_workspace_symbols_ignoreFolders(
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
        result = rget(self._initialization_options, path)
        return default if result is None else result

    @cached_property
    def initializationOptions_workspace_symbols_maxSymbols(
        self,
    ) -> int:
        path = [
            "workspace",
            "symbols",
            "maxSymbols",
        ]
        result = rget(self._initialization_options, path)
        return 20 if result is None else result
