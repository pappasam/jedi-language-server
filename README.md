# Jedi Language Server

[![image-version](https://img.shields.io/pypi/v/jedi-language-server.svg)](https://python.org/pypi/jedi-language-server)
[![image-license](https://img.shields.io/pypi/l/jedi-language-server.svg)](https://python.org/pypi/jedi-language-server)
[![image-python-versions](https://img.shields.io/badge/python->=3.9-blue)](https://python.org/pypi/jedi-language-server)
[![image-pypi-downloads](https://static.pepy.tech/badge/jedi-language-server)](https://pepy.tech/projects/jedi-language-server)
[![github-action-testing](https://github.com/pappasam/jedi-language-server/actions/workflows/testing.yaml/badge.svg)](https://github.com/pappasam/jedi-language-server/actions/workflows/testing.yaml)
[![poetry](https://img.shields.io/endpoint?url=https://python-poetry.org/badge/v0.json)](https://python-poetry.org/)

A [Python](https://www.python.org/) [Language Server](https://microsoft.github.io/language-server-protocol/), with additional support for [computational notebooks](https://docs.jupyter.org/en/latest/#what-is-a-notebook), powered by the latest version of [Jedi](https://jedi.readthedocs.io/en/latest/).

## Installation

Some frameworks, like coc-jedi and vscode-python, will install and manage `jedi-language-server` for you. If you're setting up manually, you can run the following from your command line (bash / zsh):

```bash
pip install -U jedi-language-server
```

Alternatively (and preferably), use [pipx](https://github.com/pipxproject/pipx) to keep `jedi-language-server` and its dependencies isolated from your other Python dependencies. Don't worry, jedi is smart enough to figure out which Virtual environment you're currently using!

## Editor Setup

The following instructions show how to use `jedi-language-server` with your development tooling. The instructions assume you have already installed `jedi-language-server`.

### Vim and Neovim

For Neovim, this project is supported out-of-the-box by [Neovim's native LSP client](https://neovim.io/doc/user/lsp.html) through [nvim-lspconfig](https://github.com/neovim/nvim-lspconfig). See [here](https://github.com/neovim/nvim-lspconfig/blob/master/doc/configs.md#jedi_language_server) for an example configuration.

For Vim, here are some additional, actively maintained options:

- [ALE](https://github.com/dense-analysis/ale).
- [vim-lsp](https://github.com/prabirshrestha/vim-lsp).

Note: this list is non-exhaustive. If you know of a great choice not included in this list, please submit a PR!

### Emacs

Users may choose one of the following options:

- [lsp-jedi](https://github.com/fredcamps/lsp-jedi).
- [eglot](https://github.com/joaotavora/eglot).
- [lsp-bridge](https://github.com/manateelazycat/lsp-bridge).
- [lspce](https://github.com/zbelial/lspce).
  
Note: this list is non-exhaustive. If you know of a great choice not included in this list, please submit a PR!

### Visual Studio Code (vscode)

Starting from the [October 2021 release](https://github.com/microsoft/vscode-python/releases/tag/2021.10.1317843341), set the `python.languageServer` setting to `Jedi` to use `jedi-language-server`.

See: <https://github.com/pappasam/jedi-language-server/issues/50#issuecomment-781101169>

## Configuration

`jedi-language-server` supports the following [initializationOptions](https://microsoft.github.io/language-server-protocol/specification#initialize):

```json
{
  "initializationOptions": {
    "codeAction": {
      "nameExtractVariable": "jls_extract_var",
      "nameExtractFunction": "jls_extract_def"
    },
    "completion": {
      "disableSnippets": false,
      "resolveEagerly": false,
      "ignorePatterns": []
    },
    "diagnostics": {
      "enable": false,
      "didOpen": true,
      "didChange": true,
      "didSave": true
    },
    "hover": {
      "enable": true,
      "disable": {
        "class": { "all": false, "names": [], "fullNames": [] },
        "function": { "all": false, "names": [], "fullNames": [] },
        "instance": { "all": false, "names": [], "fullNames": [] },
        "keyword": { "all": false, "names": [], "fullNames": [] },
        "module": { "all": false, "names": [], "fullNames": [] },
        "param": { "all": false, "names": [], "fullNames": [] },
        "path": { "all": false, "names": [], "fullNames": [] },
        "property": { "all": false, "names": [], "fullNames": [] },
        "statement": { "all": false, "names": [], "fullNames": [] }
      }
    },
    "jediSettings": {
      "autoImportModules": [],
      "caseInsensitiveCompletion": true,
      "debug": false
    },
    "markupKindPreferred": "markdown",
    "workspace": {
      "extraPaths": [],
      "environmentPath": "/path/to/venv/bin/python",
      "symbols": {
        "ignoreFolders": [".nox", ".tox", ".venv", "__pycache__", "venv"],
        "maxSymbols": 20
      }
    },
    "semanticTokens": {
      "enable": false
    }
  }
}
```

The different sections of the InitializationOptions are explained below, in detail. Section headers use a `.` to separate nested JSON-object keys.

### markupKindPreferred

The preferred MarkupKind for all `jedi-language-server` messages that take [MarkupContent](https://microsoft.github.io/language-server-protocol/specification#markupContent).

- type: `string`
- accepted values: `"markdown"`, `"plaintext"`

If omitted, `jedi-language-server` defaults to the client-preferred configuration. If there is no client-preferred configuration, jedi language server users `"plaintext"`.

### jediSettings.autoImportModules

Modules that jedi will directly import without analyzing. Improves autocompletion but loses goto definition.

- type: `string[]`
- default: `[]`

If you're noticing that modules like `numpy` and `pandas` are taking a super long time to load, and you value completions / signatures over goto definition, I recommend using this option like this:

```json
{
  "jediSettings": {
    "autoImportModules": ["numpy", "pandas"]
  }
}
```

### jediSettings.caseInsensitiveCompletion

Completions are by default case-insensitive. Set to `false` to make completions case-sensitive.

- type: `boolean`
- default: `true`

```json
{
  "jediSettings": {
    "caseInsensitiveCompletion": false
  }
}
```

### jediSettings.debug

Print jedi debugging messages to stderr.

- type: `boolean`
- default: `false`

```json
{
  "jediSettings": {
    "debug": false
  }
}
```

### codeAction.nameExtractFunction

Function name generated by the 'extract_function' codeAction.

- type: `string`
- default: `"jls_extract_def"`

### codeAction.nameExtractVariable

Variable name generated by the 'extract_variable' codeAction.

- type: `string`
- default: `"jls_extract_var"`

### completion.disableSnippets

If your language client supports `CompletionItem` snippets but you don't like them, disable them by setting this option to `true`.

- type: `boolean`
- default: `false`

### completion.resolveEagerly

Return all completion results in initial completion request. Set to `true` if your language client does not support `completionItem/resolve`.

- type: `boolean`
- default: `false`

### completion.ignorePatterns

A list of regular expressions. If any regular expression in ignorePatterns matches a completion's name, that completion item is not returned to the client.

- type: `string[]`
- default: `[]`

In general, you should prefer the default value for this option. Jedi is good at filtering values for end users. That said, there are situations where IDE developers, or some programmers in some codebases, may want to filter some completions by name. This flexible interface is provided to accommodate these advanced use cases. If you have one of these advanced use cases, see below for some example patterns (and their corresponding regular expression).

#### All Private Names

| Matches             | Non-Matches  |
| ------------------- | ------------ |
| `_hello`, `__world` | `__dunder__` |

Regular Expression:

```re
^_{1,3}$|^_[^_].*$|^__.*(?<!__)$
```

#### Only private mangled names

| Matches   | Non-Matches            |
| --------- | ---------------------- |
| `__world` | `_hello`, `__dunder__` |

Regular Expression:

```re
^_{2,3}$|^__.*(?<!__)$
```

#### Only dunder names

| Matches      | Non-Matches         |
| ------------ | ------------------- |
| `__dunder__` | `_hello`, `__world` |

Regular Expression:

```re
^__.*?__$
```

#### All names beginning with underscore

| Matches                           | Non-Matches |
| --------------------------------- | ----------- |
| `_hello`, `__world`, `__dunder__` | `regular`   |

Regular Expression:

```re
^_.*$
```

### diagnostics.enable

Enables (or disables) diagnostics provided by Jedi.

- type: `boolean`
- default: `true`

### diagnostics.didOpen

When diagnostics are enabled, run on document open

- type: `boolean`
- default: `true`

### diagnostics.didChange

When diagnostics are enabled, run on in-memory document change (e.g., while you're editing, without needing to save to disk)

- type: `boolean`
- default: `true`

### diagnostics.didSave

When diagnostics are enabled, run on document save (to disk)

- type: `boolean`
- default: `true`

### hover.enable

Enable (or disable) all hover text. If set to `false`, will cause the hover method not to be registered to the language server.

- type: `boolean`
- default: `true`

### hover.disable.\*

The following options are available under this prefix:

- hover.disable.class.all
- hover.disable.class.names
- hover.disable.class.fullNames
- hover.disable.function.all
- hover.disable.function.names
- hover.disable.function.fullNames
- hover.disable.instance.all
- hover.disable.instance.names
- hover.disable.instance.fullNames
- hover.disable.keyword.all
- hover.disable.keyword.names
- hover.disable.keyword.fullNames
- hover.disable.module.all
- hover.disable.module.names
- hover.disable.module.fullNames
- hover.disable.param.all
- hover.disable.param.names
- hover.disable.param.fullNames
- hover.disable.path.all
- hover.disable.path.names
- hover.disable.path.fullNames
- hover.disable.property.all
- hover.disable.property.names
- hover.disable.property.fullNames
- hover.disable.statement.all
- hover.disable.statement.names
- hover.disable.statement.fullNames

#### hover.disable.\[jedi-type\].all

Disable all hover text of jedi-type specified.

- type: `bool`
- default: `false`

#### hover.disable.\[jedi-type\].names

Disable hover text identified by name in list of jedi-type specified.

- type: `string[]`
- default: `[]`

#### hover.disable.\[jedi-type\].fullNames

Disable hover text identified by the fully qualified name in list of jedi-type specified. If no fully qualified name can be found, `jedi-language-server` will default to the name to prevent any unexpected behavior for users (relevant for jedi types like keywords that don't have full names).

- type: `string[]`
- default: `[]`

### workspace.extraPaths

Add additional paths for Jedi's analysis. Useful with vendor directories, packages in a non-standard location, etc. You probably won't need to use this, but you'll be happy it's here when you need it!

- type: `string[]`
- default: `[]`

Non-absolute paths are relative to your project root. For example, let's say your Python project is structured like this:

```
├── funky
│   └── haha.py
├── poetry.lock
├── pyproject.toml
├── test.py
```

Assume that `funky/haha.py` contains 1 line, `x = 12`, and your build system does some wizardry that makes `haha` importable just like `os` or `pathlib`. In this example, if you want to have this same non-standard behavior with `jedi-language-server`, put the following in your `coc-settings.json`:

```json
{
  "workspace": {
    "extraPaths": ["funky"]
  }
}
```

When editing `test.py`, you'll get completions, goto definition, and all other lsp features for the line `from haha import ...`.

Again, you probably don't need this.

### workspace.environmentPath

The Python executable path, typically the path of a virtual environment.

- type: `string`

If omitted, defaults to the active Python environment.

### workspace.symbols.maxSymbols

Maximum number of symbols returned by a call to `workspace/symbols`.

- type: `number`
- default: 20

```json
{
  "workspace": {
    "symbols": {
      "maxSymbols": 20
    }
  }
}
```

A value less than or equal to zero removes the maximum and allows `jedi-language-server` to return all workplace symbols found by jedi.

### workspace.symbols.ignoreFolders

Performance optimization that sets names of folders that are ignored for `workspace/symbols`.

- type: `string[]`
- default: `[".nox", ".tox", ".venv", "__pycache__", "venv"]`

```json
{
  "workspace": {
    "symbols": {
      "ignoreFolders": ["hello", "world"]
    }
  }
}
```

If you manually set this option, it overrides the default. Setting it to an empty array will result in no ignored folders.

### semanticTokens.enable

Improves highlighting by providing semantic token information. Disabled by default, because feature is broken and currently under development.

- type: `boolean`
- default: `false`

## Diagnostics

Diagnostics are provided by Python's built-in `compile` function.

If you would like additional diagnostics, we recommend using other tools (like [diagnostic-language-server](https://github.com/iamcco/diagnostic-languageserver)) to complement `jedi-language-server`.

## Code Formatting

Again, we recommend that you use [diagnostic-language-server](https://github.com/iamcco/diagnostic-languageserver). It also supports code formatting.

## Command line usage

`jedi-language-server` can be run directly from the command line.

```console
$ jedi-language-server --help
usage: jedi-language-server [-h] [--version] [--tcp] [--ws] [--host HOST] [--port PORT] [--log-file LOG_FILE] [-v]
```

If testing sending requests over stdio manually from the command line, you must include Windows-style line endings: `\r\n`. For an example, from within this project, run the following:

```console
$ jedi-language-server -v < ./example-initialization-request.txt
INFO:pygls.server:Starting IO server
...
```

If testing interactively, be sure to manually insert carriage returns. Although this may differ between shell environments, within most bash terminals, you can explicitly insert the required line endings by typing `<C-v><C-m>`, which will insert a `^M`. See:

```console
$ jedi-language-server 2>logs
Content-Length: 1062^M
^M
...
```

## Technical capabilities

jedi-language-server aims to support Jedi's capabilities and expose them through the Language Server Protocol. It supports the following Language Server capabilities:

### Language Features

- [completionItem/resolve](https://microsoft.github.io/language-server-protocol/specification#completionItem_resolve)
- [textDocument/codeAction](https://microsoft.github.io/language-server-protocol/specification#textDocument_codeAction) (refactor.inline, refactor.extract)
- [textDocument/completion](https://microsoft.github.io/language-server-protocol/specifications/specification-current/#textDocument_completion)
- [textDocument/declaration](https://microsoft.github.io/language-server-protocol/specifications/specification-current/#textDocument_declaration)
- [textDocument/definition](https://microsoft.github.io/language-server-protocol/specifications/specification-current/#textDocument_definition)
- [textDocument/documentHighlight](https://microsoft.github.io/language-server-protocol/specification#textDocument_documentHighlight)
- [textDocument/documentSymbol](https://microsoft.github.io/language-server-protocol/specifications/specification-current/#textDocument_documentSymbol)
- [textDocument/typeDefinition](https://microsoft.github.io/language-server-protocol/specifications/specification-current/#textDocument_typeDefinition)
- [textDocument/hover](https://microsoft.github.io/language-server-protocol/specifications/specification-current/#textDocument_hover)
- [textDocument/publishDiagnostics](https://microsoft.github.io/language-server-protocol/specification#textDocument_publishDiagnostics)
- [textDocument/references](https://microsoft.github.io/language-server-protocol/specifications/specification-current/#textDocument_references)
- [textDocument/rename](https://microsoft.github.io/language-server-protocol/specifications/specification-current/#textDocument_rename)
- [textDocument/semanticTokens](https://microsoft.github.io/language-server-protocol/specifications/specification-current/#textDocument_semanticTokens) _(under development)_
- [textDocument/signatureHelp](https://microsoft.github.io/language-server-protocol/specification#textDocument_signatureHelp)
- [workspace/symbol](https://microsoft.github.io/language-server-protocol/specifications/specification-current/#workspace_symbol)

### Text Synchronization (for diagnostics)

- [textDocument/didChange](https://microsoft.github.io/language-server-protocol/specification#textDocument_didChange)
- [textDocument/didOpen](https://microsoft.github.io/language-server-protocol/specification#textDocument_didOpen)
- [textDocument/didSave](https://microsoft.github.io/language-server-protocol/specification#textDocument_didSave)

### Notebook document support

- [NotebookDocumentSyncClientCapabilities](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#notebookDocumentSyncClientCapabilities)

## Local Development

To build and run this project from source:

### Dependencies

Install the following tools manually:

- [Poetry](https://github.com/sdispater/poetry#installation)
- [GNU Make](https://www.gnu.org/software/make/)

#### Recommended

- [asdf](https://github.com/asdf-vm/asdf)

### Get source code

[Fork](https://help.github.com/en/github/getting-started-with-github/fork-a-repo) this repository and clone the fork to your development machine:

```bash
git clone https://github.com/<YOUR-USERNAME>/jedi-language-server
cd jedi-language-server
```

### Set up development environment

```bash
make setup
```

### Automatically format files

```bash
make fix
```

### Run tests

```bash
make lint
make typecheck
make tests
```

## Inspiration

Palantir's [python-language-server](https://github.com/palantir/python-language-server) inspired this project. In fact, for consistency's sake, many of python-language-server's CLI options are used as-is in `jedi-language-server`.

Unlike python-language-server, `jedi-language-server`:

- Uses [pygls](https://github.com/openlawlibrary/pygls) instead of creating its own low-level Language Server Protocol bindings
- Supports one powerful 3rd party static analysis / completion / refactoring library: Jedi. By only supporting Jedi, we can focus on supporting all Jedi features without exposing ourselves to too many broken 3rd party dependencies.
- Is supremely simple because of its scope constraints. Leave complexity to the Jedi [master](https://github.com/davidhalter). If the force is strong with you, please submit a PR!

## Articles

- [Python in VS Code Improves Jedi Language Server Support](https://visualstudiomagazine.com/articles/2021/03/17/vscode-jedi.aspx)

## Written by

[Samuel Roeca](https://samroeca.com/)
