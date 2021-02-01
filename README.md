# jedi-language-server

[![image-version](https://img.shields.io/pypi/v/jedi-language-server.svg)](https://python.org/pypi/jedi-language-server)
[![image-license](https://img.shields.io/pypi/l/jedi-language-server.svg)](https://python.org/pypi/jedi-language-server)
[![image-python-versions](https://img.shields.io/pypi/pyversions/jedi-language-server.svg)](https://python.org/pypi/jedi-language-server)

A [Language Server](https://microsoft.github.io/language-server-protocol/) for the latest version(s) of [Jedi](https://jedi.readthedocs.io/en/latest/). If using Neovim/Vim, we recommend using with [coc-jedi](https://github.com/pappasam/coc-jedi).

**Note:** this tool is actively used by its primary author. He's happy to review pull requests / respond to issues you may discover.

## Installation

From your command line (bash / zsh), run:

```bash
pip install -U jedi-language-server
```

`-U` ensures that you're pulling the latest version from pypi.

Alternatively, consider using [pipx](https://github.com/pipxproject/pipx) to keep jedi-language-server isolated from your other Python dependencies. Don't worry, jedi is smart enough to figure out which Virtual environment you're currently using!

## Capabilities

jedi-language-server aims to support all of Jedi's capabilities and expose them through the Language Server Protocol. It currently supports the following Language Server capabilities:

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

### Command line (bash / zsh)

At your terminal prompt:

```bash
jedi-language-server
```

jedi-language-server currently works only over IO. This may change in the future.

## Configuration

We recommend using [coc-jedi](https://github.com/pappasam/coc-jedi) and following its [configuration instructions](https://github.com/pappasam/coc-jedi#configuration).

If you are configuring manually, jedi-language-server supports the following [initializationOptions](https://microsoft.github.io/language-server-protocol/specification#initialize):

```json
...
  "initializationOptions": {
    "markupKindPreferred": null,
    "jediSettings": {
      "autoImportModules": []
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
    "workspace": {
      "extraPaths": []
    }
  }
...
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

Palantir's [python-language-server](https://github.com/palantir/python-language-server) inspired this project. Unlike python-language-server, jedi-language-server:

- Uses [pygls](https://github.com/openlawlibrary/pygls) instead of creating its own low-level Language Server Protocol bindings
- Supports one powerful 3rd party library: Jedi. By only supporting Jedi, we can focus on supporting all Jedi features without exposing ourselves to too many broken 3rd party dependencies (I'm looking at you, [rope](https://github.com/python-rope/rope)).
- Is supremely simple because of its scope constraints. Leave complexity to the Jedi [master](https://github.com/davidhalter). If the force is strong with you, please submit a PR!

## Written by

Samuel Roeca _samuel.roeca@gmail.com_
