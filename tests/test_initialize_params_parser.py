"""Test the InitializeParamsParser class"""

import pytest
from pygls.types import (
    InitializeParams,
    MarkupKind,
    ClientCapabilities,
    TextDocumentClientCapabilities,
)
from jedi_language_server.initialize_params_parser import (
    InitializeParamsParser,
)


def test_error_when_init_params_not_set() -> None:
    """Test to ensure that InitializeParamsParser class raises error
    when used without setting InitializeParams via `set_initialize_params`
    """
    init_params = InitializeParamsParser()

    with pytest.raises(ValueError):
        _ = init_params.initializationOptions_diagnostics_enable


@pytest.mark.parametrize(
    "setting, expected",
    [
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
    ],
)
def test_default(setting, expected) -> None:
    """This test ensures the defaults don't change by accident."""
    init_params = InitializeParamsParser()
    init_params.set_initialize_params({})

    actual = getattr(init_params, setting)
    assert actual == expected
