"""Jedi types mapped to LSP types"""

from typing import Optional
from pygls.types import CompletionItemKind

# Taken from: https://github.com/palantir/python-language-server
_JEDI_LSP_TYPE_MAP = {
    "buffer": CompletionItemKind.Class,
    "builtin": CompletionItemKind.Class,
    "builtinfunction": CompletionItemKind.Function,
    "class": CompletionItemKind.Class,
    "constant": CompletionItemKind.Variable,
    "dict": CompletionItemKind.Class,
    "dictionary": CompletionItemKind.Class,
    "dictproxy": CompletionItemKind.Class,
    "file": CompletionItemKind.File,
    "frame": CompletionItemKind.Class,
    "funcdef": CompletionItemKind.Function,
    "function": CompletionItemKind.Function,
    "generator": CompletionItemKind.Function,
    "import": CompletionItemKind.Module,
    "instance": CompletionItemKind.Reference,
    "keyword": CompletionItemKind.Keyword,
    "lambda": CompletionItemKind.Function,
    "method": CompletionItemKind.Method,
    "module": CompletionItemKind.Module,
    "none": CompletionItemKind.Value,
    "param": CompletionItemKind.Variable,
    "property": CompletionItemKind.Property,
    "slice": CompletionItemKind.Class,
    "statement": CompletionItemKind.Keyword,
    "traceback": CompletionItemKind.Class,
    "tuple": CompletionItemKind.Class,
    "type": CompletionItemKind.Class,
    "value": CompletionItemKind.Value,
    "variable": CompletionItemKind.Variable,
    "xrange": CompletionItemKind.Class,
}


def get_lsp_type(jedi_type: str) -> Optional[int]:
    """Get type map"""
    return _JEDI_LSP_TYPE_MAP.get(jedi_type)
