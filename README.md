# jedi-language-server

[![image-version](https://img.shields.io/pypi/v/jedi-language-server.svg)](https://python.org/pypi/jedi-language-server)
[![image-license](https://img.shields.io/pypi/l/jedi-language-server.svg)](https://python.org/pypi/jedi-language-server)
[![image-python-versions](https://img.shields.io/pypi/pyversions/jedi-language-server.svg)](https://python.org/pypi/jedi-language-server)

A [Language Server](https://microsoft.github.io/language-server-protocol/) for the latest version(s) [Jedi](https://jedi.readthedocs.io/en/latest/).

**Note:** this tool is actively used by its primary author. He's happy to review pull requests / respond to issues you may discover.

## Installation

From your command line (bash / zsh), run:

```bash
pip install -U jedi jedi-language-server
```

`-U` ensures that you're pulling the latest version from pypi.

## Overview

jedi-language-server aims to support all of Jedi's capabilities and expose them through the Language Server Protocol. It currently supports the following Language Server requests:

* [textDocument/completion](https://microsoft.github.io/language-server-protocol/specifications/specification-current/#textDocument_completion)
* [textDocument/definition](https://microsoft.github.io/language-server-protocol/specifications/specification-current/#textDocument_definition)
* [textDocument/documentSymbol](https://microsoft.github.io/language-server-protocol/specifications/specification-current/#textDocument_documentSymbol)
* [textDocument/hover](https://microsoft.github.io/language-server-protocol/specifications/specification-current/#textDocument_hover)
* [textDocument/references](https://microsoft.github.io/language-server-protocol/specifications/specification-current/#textDocument_references)
* [textDocument/rename](https://microsoft.github.io/language-server-protocol/specifications/specification-current/#textDocument_rename)
* [workspace/symbol](https://microsoft.github.io/language-server-protocol/specifications/specification-current/#workspace_symbol)

These language server requests are not currently configurable by the user, but we expect to relax this constraint in a future release.

## Usage

The following instructions show how to use jedi-language-server with your development tooling. The instructions assume you have already installed jedi-language-server.

### Command line (bash / zsh)

At your terminal prompt:

```bash
jedi-language-server
```

jedi-language-server currently works only over IO. This may change in the future.

### Neovim

Configure jedi-language-server with [coc.nvim](https://github.com/neoclide/coc.nvim/wiki/Language-servers#register-custom-language-servers). For diagnostics, we recommend installing and using the latest version of [efm-langserver](git@github.com:mattn/efm-langserver.git) + [pylint](https://github.com/PyCQA/pylint).

~/.config/nvim/coc-settings.json:

```json
"languageserver": {
  "efm": {
    "command": "efm-langserver",
    "args": [],
    "filetypes": ["python"]
  },
  "jls": {
    "command": "jedi-language-server",
    "args": [],
    "filetypes": ["python"]
  }
}
```

~/.config/efm-langserver/config.yaml:

```yaml
version: 2
tools:
  python-pylint: &python-pylint
    lint-command: 'pylint'
    lint-formats:
      - '%f:%l:%c: %t%m'
languages:
  python:
    - <<: *python-pylint
```

## Local Development

Like everything else in this project, local development is quite simple.

### Dependencies

Install the following tools manually.

* [Poetry](https://github.com/sdispater/poetry#installation)
* [GNU Make](https://www.gnu.org/software/make/)

#### Recommended

* [asdf](https://github.com/asdf-vm/asdf)

### Set up development environment

```bash
make setup
```

### Run tests

```bash
make test
```

## Inspiration

Palantir's [python-language-server](https://github.com/palantir/python-language-server) inspired this project. jedi-language-server differs from python-language-server. jedi-language-server:

* Uses `pygls` instead of creating its own low-level Language Server Protocol bindings
* Supports one powerful 3rd party library: Jedi. By only supporting Jedi, we can focus on supporting all Jedi features without exposing ourselves to too many broken 3rd party dependencies (I'm looking at you, [rope](https://github.com/python-rope/rope)).
* Is supremely simple. Given its scope constraints, it will continue to be super simple and leave complexity to the Jedi [master](https://github.com/davidhalter). Feel free to submit a PR!

## Written by

Samuel Roeca *samuel.roeca@gmail.com*
