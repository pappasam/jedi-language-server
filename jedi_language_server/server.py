"""Jedi Language Server

Creates the language server constant and wraps "features" with it.

Official language server spec:
    https://microsoft.github.io/language-server-protocol/specification
"""

import itertools
from collections import defaultdict
from typing import Dict, List, Optional

from pygls.exceptions import FeatureAlreadyRegisteredError
from pygls.features import (
    COMPLETION,
    DEFINITION,
    DOCUMENT_SYMBOL,
    HOVER,
    INITIALIZED,
    REFERENCES,
    RENAME,
    WORKSPACE_SYMBOL,
)
from pygls.server import LanguageServer
from pygls.types import (
    CompletionItem,
    CompletionList,
    CompletionParams,
    ConfigurationItem,
    ConfigurationParams,
    DocumentSymbolParams,
    Hover,
    Location,
    Registration,
    RegistrationParams,
    RenameParams,
    SymbolInformation,
    TextDocumentPositionParams,
    TextEdit,
    Unregistration,
    UnregistrationParams,
    WorkspaceEdit,
    WorkspaceSymbolParams,
)

from . import jedi_utils, pygls_utils
from .pygls_utils import Feature, FeatureConfig
from .type_map import get_lsp_completion_type


class JediLanguageServer(LanguageServer):
    """The Jedi Language Server"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lookup_feature_id: Dict[str, str] = defaultdict(pygls_utils.uuid)

    async def re_register_feature(
        self, feature: pygls_utils.Feature, config: object,
    ):
        """Unregister and register feature with new options"""
        if feature.lsp_method in self.lookup_feature_id:
            params = UnregistrationParams(
                [
                    Unregistration(
                        self.lookup_feature_id[feature.lsp_method],
                        feature.lsp_method,
                    )
                ]
            )
            await self.unregister_capability_async(params)
        registration_options = {
            cfg.arg: pygls_utils.rgetattr(config, cfg.path, cfg.default)
            for cfg in feature.config
        }
        register_params = RegistrationParams(
            [
                Registration(
                    self.lookup_feature_id[feature.lsp_method],
                    feature.lsp_method,
                    registration_options,
                )
            ]
        )
        response = await self.register_capability_async(register_params)
        if response is None:
            try:
                self.feature(feature.lsp_method)(feature.function)
            except FeatureAlreadyRegisteredError:
                pass


def completion(
    server: JediLanguageServer, params: CompletionParams
) -> CompletionList:
    """Returns completion items"""
    jedi_script = jedi_utils.script(server.workspace, params.textDocument)
    jedi_lines = jedi_utils.line_column(params.position)
    completions = jedi_script.complete(**jedi_lines)
    char = pygls_utils.char_before_cursor(
        document=server.workspace.get_document(params.textDocument.uri),
        position=params.position,
    )
    return CompletionList(
        is_incomplete=False,
        items=[
            CompletionItem(
                label=completion.name,
                kind=get_lsp_completion_type(completion.type),
                detail=completion.description,
                documentation=completion.docstring(),
                insert_text=pygls_utils.clean_completion_name(
                    completion.name, char
                ),
            )
            for completion in completions
        ],
    )


def definition(
    server: JediLanguageServer, params: TextDocumentPositionParams
) -> List[Location]:
    """Support Goto Definition"""
    jedi_script = jedi_utils.script(server.workspace, params.textDocument)
    jedi_lines = jedi_utils.line_column(params.position)
    names = jedi_script.goto(
        follow_imports=True, follow_builtin_imports=True, **jedi_lines,
    )
    return [jedi_utils.lsp_location(name) for name in names]


def hover(
    server: JediLanguageServer, params: TextDocumentPositionParams
) -> Hover:
    """Support Hover"""
    jedi_script = jedi_utils.script(server.workspace, params.textDocument)
    jedi_lines = jedi_utils.line_column(params.position)
    try:
        _names = jedi_script.help(**jedi_lines)
    except Exception:  # pylint: disable=broad-except
        names: List[str] = []
    else:
        names = [name for name in (n.docstring() for n in _names) if name]
    return Hover(contents=names if names else "jedi: no help docs found")


def references(
    server: JediLanguageServer, params: TextDocumentPositionParams
) -> List[Location]:
    """Obtain all references to document"""
    jedi_script = jedi_utils.script(server.workspace, params.textDocument)
    jedi_lines = jedi_utils.line_column(params.position)
    try:
        names = jedi_script.get_references(**jedi_lines)
    except Exception:  # pylint: disable=broad-except
        return []
    return [jedi_utils.lsp_location(name) for name in names]


def rename(
    server: JediLanguageServer, params: RenameParams
) -> Optional[WorkspaceEdit]:
    """Rename a symbol across a workspace"""
    jedi_script = jedi_utils.script(server.workspace, params.textDocument)
    jedi_lines = jedi_utils.line_column(params.position)
    try:
        names = jedi_script.get_references(**jedi_lines)
    except Exception:  # pylint: disable=broad-except
        return None
    locations = [jedi_utils.lsp_location(name) for name in names]
    if not locations:
        return None
    changes: Dict[str, List[TextEdit]] = {}
    for location in locations:
        text_edit = TextEdit(location.range, new_text=params.newName)
        if location.uri not in changes:
            changes[location.uri] = [text_edit]
        else:
            changes[location.uri].append(text_edit)
    return WorkspaceEdit(changes=changes)


def document_symbol(
    server: JediLanguageServer, params: DocumentSymbolParams
) -> List[SymbolInformation]:
    """Document Python document symbols"""
    jedi_script = jedi_utils.script(server.workspace, params.textDocument)
    try:
        names = jedi_script.get_names()
    except Exception:  # pylint: disable=broad-except
        return []
    return [jedi_utils.lsp_symbol_information(name) for name in names]


def workspace_symbol(
    server: JediLanguageServer, params: WorkspaceSymbolParams
) -> List[SymbolInformation]:
    """Document Python workspace symbols"""
    jedi_project = jedi_utils.project(server.workspace)
    if params.query.strip() == "":
        return []
    try:
        names = jedi_project.search(params.query)
    except Exception:  # pylint: disable=broad-except
        return []
    return [
        jedi_utils.lsp_symbol_information(name)
        for name in itertools.islice(names, 20)
    ]


_CONFIG_COMPLETION = (
    FeatureConfig(
        "triggerCharacters", "completion.triggerCharacters", [".", "'", '"'],
    ),
)

_FEATURES = (
    Feature(COMPLETION, completion, _CONFIG_COMPLETION),
    Feature(DEFINITION, definition),
    Feature(HOVER, hover),
    Feature(REFERENCES, references),
    Feature(RENAME, rename),
    Feature(DOCUMENT_SYMBOL, document_symbol),
    Feature(WORKSPACE_SYMBOL, workspace_symbol),
)

SERVER = JediLanguageServer()


@SERVER.feature(INITIALIZED)
async def initialized(
    server: JediLanguageServer,
    params: Dict[str, object],  # pylint: disable=unused-argument
):
    """Post-basic initialization actions

    1. If server is not enabled, do not register any features
    2. Otherwise, register all features
    """
    _config = await server.get_configuration_async(
        ConfigurationParams([ConfigurationItem(section="jedi")])
    )
    config = _config[0] if _config else object()
    if not getattr(config, "enabled", True):
        server.show_message(
            'jedi-language-server disabled {"jedi.enabled": false}'
        )
        return
    for feature in _FEATURES:
        await server.re_register_feature(feature, config)
    server.show_message("jedi-language-server initialized")
