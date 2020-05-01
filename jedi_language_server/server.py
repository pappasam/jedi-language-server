"""Jedi Language Server

Creates the language server constant and wraps "features" with it.

Official language server spec:
    https://microsoft.github.io/language-server-protocol/specification
"""

import itertools
from collections import defaultdict
from typing import DefaultDict, Dict, List, Optional

from pygls.exceptions import FeatureAlreadyRegisteredError
from pygls.features import (
    COMPLETION,
    DEFINITION,
    DOCUMENT_HIGHLIGHT,
    DOCUMENT_SYMBOL,
    HOVER,
    INITIALIZED,
    REFERENCES,
    RENAME,
    SIGNATURE_HELP,
    TEXT_DOCUMENT_DID_CHANGE,
    TEXT_DOCUMENT_DID_OPEN,
    TEXT_DOCUMENT_DID_SAVE,
    WORKSPACE_SYMBOL,
)
from pygls.server import LanguageServer
from pygls.types import (
    CompletionItem,
    CompletionList,
    CompletionParams,
    ConfigurationItem,
    ConfigurationParams,
    DidChangeTextDocumentParams,
    DidOpenTextDocumentParams,
    DidSaveTextDocumentParams,
    DocumentHighlight,
    DocumentSymbolParams,
    Hover,
    Location,
    ParameterInformation,
    Registration,
    RegistrationParams,
    RenameParams,
    SignatureHelp,
    SignatureInformation,
    SymbolInformation,
    TextDocumentPositionParams,
    TextEdit,
    Unregistration,
    UnregistrationParams,
    WorkspaceEdit,
    WorkspaceSymbolParams,
)

from . import jedi_utils, pygls_utils
from .pygls_utils import Feature, FeatureConfig, rgetattr
from .type_map import get_lsp_completion_type


class JediLanguageServer(LanguageServer):
    """The Jedi Language Server

    :attr lookup_feature_id: map feature name to feature id.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.lookup_feature_id: DefaultDict[str, str] = defaultdict(
            pygls_utils.uuid
        )

    def jls_message(self, message: str) -> None:
        """Standardize `JediLanguageServer.show_message`"""
        self.show_message(f"jedi-language-server {message}")

    async def unregister_feature(self, feature: Feature) -> None:
        """Unregister an LSP method if it has already been registered"""
        lsp_method = feature.lsp_method
        if lsp_method not in self.lookup_feature_id:
            return
        await self.unregister_capability_async(
            UnregistrationParams(
                [
                    Unregistration(
                        self.lookup_feature_id[lsp_method], lsp_method
                    )
                ]
            )
        )
        del self.lookup_feature_id[lsp_method]

    async def register_feature(
        self, feature: Feature, config: object,
    ) -> None:
        """(unregister and) register feature with new options

        :param config: full configuration object, used to lookup relevant
            feature configurations sent by the client
        """
        await self.unregister_feature(feature)
        registration_options = {
            cfg.path.split(".")[-1]: rgetattr(config, cfg.path, cfg.default)
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
    jedi_script = jedi_utils.script(server.workspace, params.textDocument.uri)
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


def signature_help(
    server: JediLanguageServer, params: TextDocumentPositionParams
) -> SignatureHelp:
    """Returns signature help"""
    jedi_script = jedi_utils.script(server.workspace, params.textDocument.uri)
    jedi_lines = jedi_utils.line_column(params.position)
    signatures = jedi_script.get_signatures(**jedi_lines)
    return SignatureHelp(
        signatures=[
            SignatureInformation(
                label=signature.to_string(),
                documentation=None,
                parameters=[
                    ParameterInformation(
                        label=info.to_string(), documentation=None
                    )
                    for info in signature.params
                ],
            )
            for signature in signatures
        ],
        active_signature=0,
        active_parameter=signatures[0].index if signatures else 0,
    )


def definition(
    server: JediLanguageServer, params: TextDocumentPositionParams
) -> List[Location]:
    """Support Goto Definition"""
    jedi_script = jedi_utils.script(server.workspace, params.textDocument.uri)
    jedi_lines = jedi_utils.line_column(params.position)
    names = jedi_script.goto(
        follow_imports=True, follow_builtin_imports=True, **jedi_lines,
    )
    return [jedi_utils.lsp_location(name) for name in names]


def highlight(
    server: JediLanguageServer, params: TextDocumentPositionParams
) -> List[DocumentHighlight]:
    """Support document highlight request

    This function is called frequently, so we minimize the number of expensive
    calls. These calls are:

    1. Getting assignment of current symbol (script.goto)
    2. Getting all names in the current script (script.get_names)

    Finally, we only return names if there are more than 1. Otherwise, we don't
    want to highlight anything.
    """
    document = server.workspace.get_document(params.textDocument.uri)
    word = document.word_at_position(params.position)
    jedi_script = jedi_utils.script(server.workspace, params.textDocument.uri)
    jedi_lines = jedi_utils.line_column(params.position)
    jedi_definition_names = jedi_script.goto(
        follow_imports=False, follow_builtin_imports=False, **jedi_lines,
    )
    if not jedi_definition_names:
        return []
    current_definition_name = jedi_definition_names[0]
    jedi_context = jedi_script.get_context(**jedi_lines)
    current_full_name = (
        jedi_context.full_name
        if jedi_context.name == word
        else f"{jedi_context.full_name}.{word}"
    )
    highlight_names = [
        DocumentHighlight(jedi_utils.lsp_range(name))
        for name in jedi_script.get_names(
            all_scopes=True, definitions=True, references=True
        )
        if name.full_name == current_full_name
        or jedi_utils.compare_names(name, current_definition_name)
    ]
    return highlight_names if len(highlight_names) > 1 else []


def hover(
    server: JediLanguageServer, params: TextDocumentPositionParams
) -> Hover:
    """Support Hover"""
    jedi_script = jedi_utils.script(server.workspace, params.textDocument.uri)
    jedi_lines = jedi_utils.line_column(params.position)
    jedi_docstrings = (n.docstring() for n in jedi_script.help(**jedi_lines))
    names = [name for name in jedi_docstrings if name]
    return Hover(contents=names if names else "jedi: no help docs found")


def references(
    server: JediLanguageServer, params: TextDocumentPositionParams
) -> List[Location]:
    """Obtain all references to text"""
    jedi_script = jedi_utils.script(server.workspace, params.textDocument.uri)
    jedi_lines = jedi_utils.line_column(params.position)
    names = jedi_script.get_references(**jedi_lines)
    return [jedi_utils.lsp_location(name) for name in names]


def rename(
    server: JediLanguageServer, params: RenameParams
) -> Optional[WorkspaceEdit]:
    """Rename a symbol across a workspace"""
    jedi_script = jedi_utils.script(server.workspace, params.textDocument.uri)
    jedi_lines = jedi_utils.line_column(params.position)
    names = jedi_script.get_references(**jedi_lines)
    if not names:
        return None
    locations = [jedi_utils.lsp_location(name) for name in names]
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
    jedi_script = jedi_utils.script(server.workspace, params.textDocument.uri)
    names = jedi_script.get_names()
    return [jedi_utils.lsp_symbol_information(name) for name in names]


def workspace_symbol(
    server: JediLanguageServer, params: WorkspaceSymbolParams
) -> List[SymbolInformation]:
    """Document Python workspace symbols"""
    jedi_project = jedi_utils.project(server.workspace)
    if params.query.strip() == "":
        return []
    names = jedi_project.search(params.query)
    return [
        jedi_utils.lsp_symbol_information(name)
        for name in itertools.islice(names, 20)
    ]


def _publish_diagnostics(server: JediLanguageServer, uri: str):
    """Helper function to publish diagnostics for a file"""
    jedi_script = jedi_utils.script(server.workspace, uri)
    errors = jedi_script.get_syntax_errors()
    diagnostics = [jedi_utils.lsp_diagnostic(error) for error in errors]
    server.publish_diagnostics(uri, diagnostics)


def did_save(server: JediLanguageServer, params: DidSaveTextDocumentParams):
    """Actions run on textDocument/didSave"""
    _publish_diagnostics(server, params.textDocument.uri)


def did_change(
    server: JediLanguageServer, params: DidChangeTextDocumentParams
):
    """Actions run on textDocument/didChange"""
    _publish_diagnostics(server, params.textDocument.uri)


def did_open(server: JediLanguageServer, params: DidOpenTextDocumentParams):
    """Actions run on textDocument/didOpen"""
    _publish_diagnostics(server, params.textDocument.uri)


# Feature constants


_CONFIG_COMPLETION = (
    FeatureConfig("completion.triggerCharacters", [".", "'", '"']),
)

_CONFIG_SIGNATURE = (
    FeatureConfig("signatureHelp.triggerCharacters", ["(", ",", ")"]),
)

_FEATURES_STANDARD = (
    Feature(COMPLETION, completion, _CONFIG_COMPLETION),
    Feature(DEFINITION, definition),
    Feature(DOCUMENT_HIGHLIGHT, highlight),
    Feature(DOCUMENT_SYMBOL, document_symbol),
    Feature(HOVER, hover),
    Feature(REFERENCES, references),
    Feature(RENAME, rename),
    Feature(SIGNATURE_HELP, signature_help, _CONFIG_SIGNATURE),
    Feature(WORKSPACE_SYMBOL, workspace_symbol),
)
_FEATURE_DID_CHANGE = Feature(TEXT_DOCUMENT_DID_CHANGE, did_change)
_FEATURE_DID_OPEN = Feature(TEXT_DOCUMENT_DID_OPEN, did_open)
_FEATURE_DID_SAVE = Feature(TEXT_DOCUMENT_DID_SAVE, did_save)


# Instantiate server singleton


SERVER = JediLanguageServer()


# Define post-initialization function to customize configuration


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
        server.jls_message("disabled; `jedi.enabled` set to `false`}")
        return
    for feature in _FEATURES_STANDARD:
        await server.register_feature(feature, config)

    if rgetattr(config, "diagnostics.enabled", True):
        if rgetattr(config, "diagnostics.didOpen", True):
            await server.register_feature(_FEATURE_DID_OPEN, config)
        else:
            await server.unregister_feature(_FEATURE_DID_OPEN)

        if rgetattr(config, "diagnostics.didChange", True):
            await server.register_feature(_FEATURE_DID_CHANGE, config)
        else:
            await server.unregister_feature(_FEATURE_DID_CHANGE)

        if rgetattr(config, "diagnostics.didSave", True):
            await server.register_feature(_FEATURE_DID_SAVE, config)
        else:
            await server.unregister_feature(_FEATURE_DID_SAVE)
    else:
        await server.unregister_feature(_FEATURE_DID_OPEN)
        await server.unregister_feature(_FEATURE_DID_CHANGE)
        await server.unregister_feature(_FEATURE_DID_SAVE)

    server.jls_message("initialized")
