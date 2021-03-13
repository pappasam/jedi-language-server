"""Test the InitializeParamsParser class."""

import pytest
from pygls.lsp.types import ClientCapabilities, InitializeParams, MarkupKind

from jedi_language_server.initialize_options_parser import (
    InitializationOptionsParser,
)

_LIST_OF_SETTINGS_AND_DEFAULTS = [
    ("markupKindPreferred", None),
    ("completion_disableSnippets", False),
    ("completion_resolveEagerly", False),
    ("diagnostics_enable", True),
    ("diagnostics_didOpen", True),
    ("diagnostics_didSave", True),
    ("diagnostics_didChange", True),
    ("jediSettings_autoImportModules", []),
    ("jediSettings_caseInsensitiveCompletion", True),
    ("workspace_extraPaths", []),
]


@pytest.mark.parametrize("setting, expected", _LIST_OF_SETTINGS_AND_DEFAULTS)
def test_default(setting, expected) -> None:
    """This test ensures the defaults don't change by accident."""
    init_params = InitializationOptionsParser()
    actual = getattr(init_params, setting)
    assert actual == expected


def test_unknown_setting() -> None:
    """A new setting was addeded, and tests weren't updated with the defaults
    for that setting."""
    init_params = InitializationOptionsParser()
    actual = [
        attr
        for attr in dir(init_params)
        if attr.startswith(("capabilities", "initializationOptions"))
    ].sort()

    expected = [attr for attr, _ in _LIST_OF_SETTINGS_AND_DEFAULTS].sort()
    assert expected == actual
