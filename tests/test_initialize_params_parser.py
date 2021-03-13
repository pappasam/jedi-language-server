"""Test the InitializeParamsParser class."""

import pytest
from pygls.lsp.types import ClientCapabilities, InitializeParams, MarkupKind

from jedi_language_server.initialize_params_parser import (
    InitializeParamsParser,
)

_LIST_OF_SETTINGS_AND_DEFAULTS = [
    # pylint: disable=line-too-long
    (
        "capabilities_textDocument_completion_completionItem_documentationFormat",
        [MarkupKind.PlainText],
    ),
    (
        "capabilities_textDocument_completion_completionItem_snippetSupport",
        False,
    ),
    (
        "capabilities_textDocument_documentSymbol_hierarchicalDocumentSymbolSupport",
        False,
    ),
    (
        "capabilities_textDocument_hover_contentFormat",
        [MarkupKind.PlainText],
    ),
    (
        "capabilities_textDocument_signatureHelp_contentFormat",
        [MarkupKind.PlainText],
    ),
    ("initializationOptions_markupKindPreferred", None),
    ("initializationOptions_completion_disableSnippets", False),
    ("initializationOptions_completion_resolveEagerly", False),
    ("initializationOptions_diagnostics_enable", True),
    ("initializationOptions_diagnostics_didOpen", True),
    ("initializationOptions_diagnostics_didSave", True),
    ("initializationOptions_diagnostics_didChange", True),
    ("initializationOptions_jediSettings_autoImportModules", []),
    ("initializationOptions_jediSettings_caseInsensitiveCompletion", True),
    ("initializationOptions_workspace_extraPaths", []),
]


@pytest.mark.parametrize(
    "setting, _",
    _LIST_OF_SETTINGS_AND_DEFAULTS,
)
def test_error_when_init_params_not_set(setting, _) -> None:
    """Test to ensure that InitializeParamsParser class raises error when used
    without setting InitializeParams via `set_initialize_params`"""
    init_params = InitializeParamsParser()

    with pytest.raises(ValueError):
        _ = getattr(init_params, setting)


@pytest.mark.parametrize("setting, expected", _LIST_OF_SETTINGS_AND_DEFAULTS)
def test_default(setting, expected) -> None:
    """This test ensures the defaults don't change by accident."""
    init_params = InitializeParamsParser()
    default_capabilities = ClientCapabilities()
    default_params = InitializeParams(capabilities=default_capabilities)
    init_params.set_initialize_params(default_params)

    actual = getattr(init_params, setting)
    assert actual == expected


def test_unknown_setting() -> None:
    """A new setting was addeded, and tests weren't updated with the defaults
    for that setting."""
    init_params = InitializeParamsParser()
    actual = [
        attr
        for attr in dir(init_params)
        if attr.startswith(("capabilities", "initializationOptions"))
    ].sort()

    expected = [attr for attr, _ in _LIST_OF_SETTINGS_AND_DEFAULTS].sort()
    assert expected == actual
