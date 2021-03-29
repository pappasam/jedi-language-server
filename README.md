# jedi-language-server

[![image-version](https://img.shields.io/pypi/v/jedi-language-server.svg)](https://python.org/pypi/jedi-language-server)
[![image-license](https://img.shields.io/pypi/l/jedi-language-server.svg)](https://python.org/pypi/jedi-language-server)
[![image-python-versions](https://img.shields.io/badge/python->=3.6.1-blue)](https://python.org/pypi/jedi-language-server)
[![image-pypi-downloads](https://pepy.tech/badge/jedi-language-server)](https://pepy.tech/project/jedi-language-server)
[![github-action-testing](https://github.com/pappasam/jedi-language-server/actions/workflows/testing.yaml/badge.svg)](https://github.com/pappasam/jedi-language-server/actions/workflows/testing.yaml)

A [Language Server](https://microsoft.github.io/language-server-protocol/) for the latest version(s) of [Jedi](https://jedi.readthedocs.io/en/latest/). If using Neovim/Vim, we recommend using with [coc-jedi](https://github.com/pappasam/coc-jedi). Supports Python versions 3.6.1 and newer.

**Note:** this tool is actively used by its primary author. He's happy to review pull requests / respond to issues you may discover.

## Installation

Some frameworks, like coc-jedi and vscode-python, will install and manage jedi-language-server for you. If you're setting up manually, you can run the following from your command line (bash / zsh):

```bash
pip install -U jedi-language-server
```

Alternatively (and preferably), use [pipx](https://github.com/pipxproject/pipx) to keep jedi-language-server and its dependencies isolated from your other Python dependencies. Don't worry, jedi is smart enough to figure out which Virtual environment you're currently using!

## Capabilities

jedi-language-server aims to support Jedi's capabilities and expose them through the Language Server Protocol. It supports the following Language Server capabilities:

### Language Features

- [completionItem/resolve](https://microsoft.github.io/language-server-protocol/specification#completionItem_resolve)
- [textDocument/codeAction](https://microsoft.github.io/language-server-protocol/specification#textDocument_codeAction) (refactor.inline, refactor.extract)
- [textDocument/completion](https://microsoft.github.io/language-server-protocol/specifications/specification-current/#textDocument_completion)
- [textDocument/definition](https://microsoft.github.io/language-server-protocol/specifications/specification-current/#textDocument_definition)
- [textDocument/documentHighlight](https://microsoft.github.io/language-server-protocol/specification#textDocument_documentHighlight)
- [textDocument/documentSymbol](https://microsoft.github.io/language-server-protocol/specifications/specification-current/#textDocument_documentSymbol)
- [textDocument/hover](https://microsoft.github.io/language-server-protocol/specifications/specification-current/#textDocument_hover)
- [textDocument/publishDiagnostics](https://microsoft.github.io/language-server-protocol/specification#textDocument_publishDiagnostics)
- [textDocument/references](https://microsoft.github.io/language-server-protocol/specifications/specification-current/#textDocument_references)
- [textDocument/rename](https://microsoft.github.io/language-server-protocol/specifications/specification-current/#textDocument_rename)
- [textDocument/signatureHelp](https://microsoft.github.io/language-server-protocol/specification#textDocument_signatureHelp)
- [workspace/symbol](https://microsoft.github.io/language-server-protocol/specifications/specification-current/#workspace_symbol)

### Text Synchronization (for diagnostics)

- [textDocument/didChange](https://microsoft.github.io/language-server-protocol/specification#textDocument_didChange)
- [textDocument/didOpen](https://microsoft.github.io/language-server-protocol/specification#textDocument_didOpen)
- [textDocument/didSave](https://microsoft.github.io/language-server-protocol/specification#textDocument_didSave)

## Editor Setup

The following instructions show how to use jedi-language-server with your development tooling. The instructions assume you have already installed jedi-language-server.

### Vim / Neovim

Users may choose 1 of the following options:

- [coc.nvim](https://github.com/neoclide/coc.nvim) with [coc-jedi](https://github.com/pappasam/coc-jedi).
- [ALE](https://github.com/dense-analysis/ale).
- [Neovim's native LSP client](https://neovim.io/doc/user/lsp.html). See [here](https://github.com/neovim/nvim-lspconfig#jedi_language_server) for an example configuration.
- [vim-lsp](https://github.com/prabirshrestha/vim-lsp).

Note: this list is non-exhaustive. If you know of a great choice not included in this list, please submit a PR!

### Emacs

Users may choose 1 of the following options:

- [lsp-jedi](https://github.com/fredcamps/lsp-jedi).

Note: this list is non-exhaustive. If you know of a great choice not included in this list, please submit a PR!

### Visual Studio Code (vscode)

With [this release](https://github.com/microsoft/vscode-python/releases/tag/2021.2.576481509) there is a new setting for `python.languageServer` to use jedi-language-server: set `python.languageServer` to `JediLSP`.

Note: this is experimental and uses an older version (for now) to support python 2.7.

See: <https://github.com/pappasam/jedi-language-server/issues/50#issuecomment-781101169>

## Command line

jedi-language-server can be run directly from the command line.

```console
$ jedi-language-server --help
usage: jedi-language-server [-h] [--version] [--tcp] [--host HOST]
                            [--port PORT] [--log-file LOG_FILE] [-v]

Jedi language server: an LSP wrapper for jedi.

optional arguments:
  -h, --help           show this help message and exit
  --version            display version information and exit
  --tcp                use TCP server instead of stdio
  --host HOST          host for TCP server (default 127.0.0.1)
  --port PORT          port for TCP server (default 2087)
  --log-file LOG_FILE  redirect logs to the given file instead of writing to
                       stderr
  -v, --verbose        increase verbosity of log output

Examples:

    Run from stdio: jedi-language-server
```

## Configuration

We recommend using [coc-jedi](https://github.com/pappasam/coc-jedi) and following its [configuration instructions](https://github.com/pappasam/coc-jedi#configuration).

If you are configuring manually, jedi-language-server supports the following [initializationOptions](https://microsoft.github.io/language-server-protocol/specification#initialize):

```json
{
  "initializationOptions": {
    "codeAction": {
      "nameExtractVariable": "jls_extract_var",
      "nameExtractFunction": "jls_extract_def"
    },
    "completion": {
      "disableSnippets": false,
      "resolveEagerly": false
    },
    "diagnostics": {
      "enable": true,
      "didOpen": true,
      "didChange": true,
      "didSave": true
    },
    "jediSettings": {
      "autoImportModules": [],
      "caseInsensitiveCompletion": true
    },
    "markupKindPreferred": "markdown",
    "workspace": {
      "extraPaths": [],
      "symbols": {
        "ignoreFolders": [".nox", ".tox", ".venv", "__pycache__", "venv"],
        "maxSymbols": 20
      }
    }
  }
}
```

See coc-jedi's [configuration instructions](https://github.com/pappasam/coc-jedi#configuration) for an explanation of the above configurations.

## Additional Diagnostics

jedi-langugage-server provides diagnostics about syntax errors, powered by Jedi. If you would like additional diagnostics, we suggest using the powerful [diagnostic-language-server](https://github.com/iamcco/diagnostic-languageserver).

## Code Formatting

Again, we recommend that you use [diagnostic-language-server](https://github.com/iamcco/diagnostic-languageserver). It also supports code formatting.

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

### Run tests

```bash
make test
```

## Inspiration

Palantir's [python-language-server](https://github.com/palantir/python-language-server) inspired this project. In fact, for consistency's sake, many of python-language-server's CLI options are used as-is in jedi-language-server.

Unlike python-language-server, jedi-language-server:

- Uses [pygls](https://github.com/openlawlibrary/pygls) instead of creating its own low-level Language Server Protocol bindings
- Supports one powerful 3rd party static analysis / completion / refactoring library: Jedi. By only supporting Jedi, we can focus on supporting all Jedi features without exposing ourselves to too many broken 3rd party dependencies (I'm looking at you, [rope](https://github.com/python-rope/rope)).
- Is supremely simple because of its scope constraints. Leave complexity to the Jedi [master](https://github.com/davidhalter). If the force is strong with you, please submit a PR!

## Articles

- [Python in VS Code Improves Jedi Language Server Support](https://visualstudiomagazine.com/articles/2021/03/17/vscode-jedi.aspx)

## Written by

Samuel Roeca _samuel.roeca@gmail.com_
