"""Module containing the InitializeParams parser

This parser handles the following tasks for the InitializeParams:

- storage / accessibility outside the initialize request
- configuring option defaults
- organizing initialization values in one place
"""

from typing import List, Optional

from pygls.types import InitializeParams, MarkupKind

from .pygls_utils import rgetattr

# pylint: disable=line-too-long
# pylint: disable=invalid-name
# pylint: disable=missing-function-docstring


class InitializeParamsParser:
    """Class to parse and manage InitializeParams"""

    def __init__(self) -> None:
        self._initialize_params_store: Optional[InitializeParams] = None

    @property
    def _initialize_params(self) -> InitializeParams:
        """Get the initialize params"""
        if self._initialize_params_store is None:
            raise ValueError("InitializeParams not set")
        return self._initialize_params_store

    def set_initialize_params(self, params: InitializeParams) -> None:
        """Set the initialize params"""
        self._initialize_params_store = params

    @property
    def capabilities_textDocument_completion_completionItem_documentationFormat(
        self,
    ) -> List[MarkupKind]:
        _path = (
            "capabilities",
            "textDocument",
            "completion",
            "completionItem",
            "documentationFormat",
        )
        path = ".".join(_path)
        default = [MarkupKind.PlainText]
        return rgetattr(self._initialize_params, path, default)  # type: ignore

    @property
    def capabilities_textDocument_documentSymbol_hierarchicalDocumentSymbolSupport(
        self,
    ) -> bool:
        _path = (
            "capabilities",
            "textDocument",
            "documentSymbol",
            "hierarchicalDocumentSymbolSupport",
        )
        path = ".".join(_path)
        default = False
        return bool(rgetattr(self._initialize_params, path, default))

    @property
    def capabilities_textDocument_hover_contentFormat(
        self,
    ) -> List[MarkupKind]:
        _path = (
            "capabilities",
            "textDocument",
            "hover",
            "contentFormat",
        )
        path = ".".join(_path)
        default = [MarkupKind.PlainText]
        return rgetattr(self._initialize_params, path, default)  # type: ignore

    @property
    def capabilities_textDocument_signatureHelp_contentFormat(
        self,
    ) -> List[str]:
        _path = (
            "capabilities",
            "textDocument",
            "hover",
            "contentFormat",
        )
        path = ".".join(_path)
        default = [MarkupKind.PlainText]
        return rgetattr(self._initialize_params, path, default)  # type: ignore

    @property
    def initializationOptions_markupKindPreferred(
        self,
    ) -> Optional[MarkupKind]:
        _path = (
            "initializationOptions",
            "markupKindPreferred",
        )
        path = ".".join(_path)
        result = rgetattr(self._initialize_params, path)
        return result if result is None else MarkupKind(result)

    @property
    def initializationOptions_diagnostics_enable(self) -> bool:
        _path = (
            "initializationOptions",
            "diagnostics",
            "enable",
        )
        path = ".".join(_path)
        default = True
        return bool(rgetattr(self._initialize_params, path, default))

    @property
    def initializationOptions_diagnostics_didOpen(self) -> bool:
        _path = (
            "initializationOptions",
            "diagnostics",
            "didOpen",
        )
        path = ".".join(_path)
        default = True
        return bool(rgetattr(self._initialize_params, path, default))

    @property
    def initializationOptions_diagnostics_didSave(self) -> bool:
        _path = (
            "initializationOptions",
            "diagnostics",
            "didSave",
        )
        path = ".".join(_path)
        default = True
        return bool(rgetattr(self._initialize_params, path, default))

    @property
    def initializationOptions_diagnostics_didChange(self) -> bool:
        _path = (
            "initializationOptions",
            "diagnostics",
            "didChange",
        )
        path = ".".join(_path)
        default = True
        return bool(rgetattr(self._initialize_params, path, default))
