"""Constants."""

from lsprotocol.types import SemanticTokenTypes

MAX_CONCURRENT_DEBOUNCE_CALLS = 10
"""The maximum number of concurrent calls allowed by the debounce decorator."""

_token_types = list(SemanticTokenTypes)

TYPE_TO_TOKEN_ID = {
    "module": _token_types.index(SemanticTokenTypes.Namespace),
    "class": _token_types.index(SemanticTokenTypes.Class),
    "function": _token_types.index(SemanticTokenTypes.Function),
    "param": _token_types.index(SemanticTokenTypes.Parameter),
    "statement": _token_types.index(SemanticTokenTypes.Variable),
    "property": _token_types.index(SemanticTokenTypes.Property),
}
