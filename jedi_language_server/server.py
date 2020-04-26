"""Jedi Language Server

Creates the language server constant and wraps "features" with it.

Official language server spec:
    https://microsoft.github.io/language-server-protocol/specification
"""

import itertools
import uuid
from collections import defaultdict
from typing import Callable, Dict, List, NamedTuple, Optional

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
    InitializeParams,
    Location,
    MessageType,
    Position,
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
from pygls.workspace import Document

from . import jedi_utils, pygls_utils
# from .features import FEATURES, Feature
from .pygls_utils import rgetattr
from .type_map import get_lsp_completion_type


def _clean_completion_name(name: str, char: str) -> str:
    """Clean the completion name, stripping bad surroundings

    1. Remove all surrounding " and '. For
    """
    if char == "'":
        return name.lstrip("'")
    if char == '"':
        return name.lstrip('"')
    return name


def _char_before_cursor(
    document: Document, position: Position, default=""
) -> str:
    """Get the character directly before the cursor"""
    try:
        return document.lines[position.line][position.character - 1]
    except IndexError:
        return default


def _uuid() -> str:
    return str(uuid.uuid4())


class FeatureConfig(NamedTuple):
    """Configuration for a feature"""

    arg: str
    path: str
    default: object


class Feature(NamedTuple):
    """Organize information about LanguageServer features"""

    lsp_method: str
    function: Callable[[LanguageServer, object], object]
    config: List[FeatureConfig]


class JediLanguageServer(LanguageServer):
    """The Jedi Language Server"""

    lookup_feature_id = defaultdict(_uuid)  # type: Dict[str, str]

    async def re_register_feature(
        self, feature: Feature, config: object,
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
        # config = await self.get_configuration_async(
        #     ConfigurationParams([ConfigurationItem(section=config_section)])
        # )

        registration_options = {
            cfg.arg: rgetattr(config, cfg.path, cfg.default)
            for cfg in feature.config
        }

        self.show_message(str(registration_options))
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

    # @SERVER.feature(COMPLETION)

    # @SERVER.feature(HOVER)
    def feature_hover(self, params: TextDocumentPositionParams) -> Hover:
        """Support Hover"""
        jedi_script = jedi_utils.script(server.workspace, params.textDocument)
        jedi_lines = jedi_utils.line_column(params.position)
        try:
            _names = jedi_script.help(**jedi_lines)
        except Exception:  # pylint: disable=broad-except
            names = []  # type: List[str]
        else:
            names = [name for name in (n.docstring() for n in _names) if name]
        return Hover(contents=names if names else "jedi: no help docs found")

    # @SERVER.feature(REFERENCES)
    def feature_references(
        self, params: TextDocumentPositionParams
    ) -> List[Location]:
        """Obtain all references to document"""
        jedi_script = jedi_utils.script(server.workspace, params.textDocument)
        jedi_lines = jedi_utils.line_column(params.position)
        try:
            names = jedi_script.get_references(**jedi_lines)
        except Exception:  # pylint: disable=broad-except
            return []
        return [jedi_utils.lsp_location(name) for name in names]

    # @SERVER.feature(RENAME)
    def feature_rename(self, params: RenameParams) -> Optional[WorkspaceEdit]:
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
        changes = {}  # type: Dict[str, List[TextEdit]]
        for location in locations:
            text_edit = TextEdit(location.range, new_text=params.newName)
            if location.uri not in changes:
                changes[location.uri] = [text_edit]
            else:
                changes[location.uri].append(text_edit)
        return WorkspaceEdit(changes=changes)

    # @SERVER.feature(DOCUMENT_SYMBOL)
    def feature_document_symbol(
        self, params: DocumentSymbolParams
    ) -> List[SymbolInformation]:
        """Document Python document symbols"""
        jedi_script = jedi_utils.script(server.workspace, params.textDocument)
        try:
            names = jedi_script.get_names()
        except Exception:  # pylint: disable=broad-except
            return []
        return [jedi_utils.lsp_symbol_information(name) for name in names]

    # @SERVER.feature(WORKSPACE_SYMBOL)
    def feature_workspace_symbol(
        self, params: WorkspaceSymbolParams
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


SERVER = JediLanguageServer()


@SERVER.feature(INITIALIZED)
async def initialized(server: JediLanguageServer, params):
    """Register features that could be changed in the future"""
    _config = await server.get_configuration_async(
        ConfigurationParams([ConfigurationItem(section="jedi")])
    )
    config = _config[0] if _config else object()
    for feature in FEATURES:
        await server.re_register_feature(feature, config)


# @SERVER.feature(COMPLETION)


def completion(
    server: JediLanguageServer, params: CompletionParams
) -> CompletionList:
    """Returns completion items"""
    jedi_script = jedi_utils.script(server.workspace, params.textDocument)
    jedi_lines = jedi_utils.line_column(params.position)
    completions = jedi_script.complete(**jedi_lines)
    char = _char_before_cursor(
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
                insert_text=_clean_completion_name(completion.name, char),
            )
            for completion in completions
        ],
    )


# @SERVER.feature(DEFINITION)


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


_CONFIG_DEFINITION = []
_CONFIG_COMPLETION = [
    FeatureConfig(
        "triggerCharacters", "completion.triggerCharacters", [".", "'", '"'],
    ),
]

FEATURES = (
    Feature(DEFINITION, definition, _CONFIG_DEFINITION),
    Feature(COMPLETION, completion, _CONFIG_COMPLETION),
)


# SERVER = LanguageServer()


# class Option(NamedTuple):
#     name_user: str
#     name_system: str
#     default: object


# class ServerConfig:
#     async def re_register_completions(self):
#         """Unregister and register completions with new options."""
#         config = await self.get_configuration_async(
#             ConfigurationParams(
#                 [
#                     ConfigurationItem(
#                         "", JsonLanguageServer.CONFIGURATION_SECTION
#                     )
#                 ]
#             )
#         )

#         trigger_chars = config[0].triggerCharacters
#         # register completions
#         await self.re_register_feature(
#             self.COMPLETION_ID,
#             self.completions,
#             COMPLETION,
#             **dict(triggerCharacters=trigger_chars),
#         )
#         self.show_message(
#             "Completion trigger characters are: {}".format(
#                 " ".join(trigger_chars)
#             )
#         )

#     def __init__(
#         self, server: LanguageServer, initialization_options: object
#     ) -> None:
#         self.server = server
#         self.init_options = initialization_options

#     def get_options(self, options: List[Option]) -> Dict[str, object]:
#         """Obtain the object provided by the default"""
#         return {
#             option.name_system: getattr(
#                 self.init_options, option.name_user, option.default
#             )
#             for option in options
#         }

#     async def register(self, method: str, options: List[Option]) -> None:
#         response = await self.server.register_capability_async(
#             RegistrationParams(
#                 [
#                     Registration(
#                         str(uuid.uuid4()), method, self.get_options(options)
#                     )
#                 ]
#             )
#         )
#         if response is not None:
#             self.server.show_message(
#                 f"jedi-language-server: error during {method} registration",
#                 MessageType.Error,
#             )

# @SERVER.feature(INITIALIZED)
# async def lsp_initialize(server: LanguageServer, params: InitializeParams):
#     """Initialize language server"""
#     config = ServerConfig(server, params.initializationOptions)
#     await config.register(
#         COMPLETION,
#         [
#             Option(
#                 name_user="completion_triggerCharacters",
#                 name_system="triggerCharacters",
#                 default=[".", "'", '"'],
#             )
#         ],
#     )
#     server.show_message("jedi-language-server: registration complete")
