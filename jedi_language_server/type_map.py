"""Jedi types mapped to LSP types"""

from pygls.types import CompletionItemKind, SymbolKind

# Taken from: https://github.com/palantir/python-language-server
_JEDI_COMPLETION_TYPE_MAP = {
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

_JEDI_SYMBOL_TYPE_MAP = {
    "none": SymbolKind.Variable,
    "type": SymbolKind.Class,
    "tuple": SymbolKind.Class,
    "dict": SymbolKind.Class,
    "dictionary": SymbolKind.Class,
    "function": SymbolKind.Function,
    "lambda": SymbolKind.Function,
    "generator": SymbolKind.Function,
    "class": SymbolKind.Class,
    "instance": SymbolKind.Class,
    "method": SymbolKind.Method,
    "builtin": SymbolKind.Class,
    "builtinfunction": SymbolKind.Function,
    "module": SymbolKind.Module,
    "file": SymbolKind.File,
    "xrange": SymbolKind.Array,
    "slice": SymbolKind.Class,
    "traceback": SymbolKind.Class,
    "frame": SymbolKind.Class,
    "buffer": SymbolKind.Array,
    "dictproxy": SymbolKind.Class,
    "funcdef": SymbolKind.Function,
    "property": SymbolKind.Property,
    "import": SymbolKind.Module,
    "keyword": SymbolKind.Variable,
    "constant": SymbolKind.Constant,
    "variable": SymbolKind.Variable,
    "value": SymbolKind.Variable,
    "param": SymbolKind.Variable,
    "statement": SymbolKind.Variable,
    "boolean": SymbolKind.Boolean,
    "int": SymbolKind.Number,
    "longlean": SymbolKind.Number,
    "float": SymbolKind.Number,
    "complex": SymbolKind.Number,
    "string": SymbolKind.String,
    "unicode": SymbolKind.String,
    "list": SymbolKind.Array,
}


def get_lsp_completion_type(jedi_type: str) -> CompletionItemKind:
    """Get type map. Always return a value."""
    return _JEDI_COMPLETION_TYPE_MAP.get(jedi_type, CompletionItemKind.Text)


def get_lsp_symbol_type(jedi_type: str) -> SymbolKind:
    """Get type map. Always return a value."""
    return _JEDI_SYMBOL_TYPE_MAP.get(jedi_type, SymbolKind.Namespace)
