# jedi-language-server

[![image-version](https://img.shields.io/pypi/v/jedi-language-server.svg)](https://python.org/pypi/jedi-language-server)
[![image-license](https://img.shields.io/pypi/l/jedi-language-server.svg)](https://python.org/pypi/jedi-language-server)
[![image-python-versions](https://img.shields.io/pypi/pyversions/jedi-language-server.svg)](https://python.org/pypi/jedi-language-server)

A [Language Server](https://microsoft.github.io/language-server-protocol/) for the latest version(s) of [Jedi](https://jedi.readthedocs.io/en/latest/).

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

Configure jedi-language-server with [coc.nvim](https://github.com/neoclide/coc.nvim/wiki/Language-servers#register-custom-language-servers). For diagnostics, we recommend installing and using the latest version of [coc-diagnostic](https://github.com/iamcco/coc-diagnostic) with [pylint](https://github.com/PyCQA/pylint).

~/.config/nvim/coc-settings.json:

```json
"languageserver": {
  "jls": {
    "command": "jedi-language-server",
    "args": [],
    "filetypes": ["python"]
  }
},
"diagnostic-languageserver.filetypes": {
  "python": "pylint"
},
"diagnostic-languageserver.linters": {
  "pylint": {
    "sourceName": "pylint",
    "command": "pylint",
    "args": [
      "--output-format",
      "text",
      "--score",
      "no",
      "--msg-template",
      "'{line}:{column}:{category}:{msg} ({msg_id}:{symbol})'",
      "%file"
    ],
    "formatPattern": [
      "^(\\d+?):(\\d+?):([a-z]+?):(.*)$",
      {
        "line": 1,
        "column": 2,
        "security": 3,
        "message": 4
      }
    ],
    "securities": {
      "informational": "hint",
      "refactor": "info",
      "convention": "info",
      "warning": "warning",
      "error": "error",
      "fatal": "error"
    },
    "offsetColumn": 1,
    "formatLines": 1
  }
}
```

## Local Development

To build and run this project from source:

### Dependencies

Install the following tools manually:

* [Poetry](https://github.com/sdispater/poetry#installation)
* [GNU Make](https://www.gnu.org/software/make/)

#### Recommended

* [asdf](https://github.com/asdf-vm/asdf)

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

* Uses `pygls` instead of creating its own low-level Language Server Protocol bindings
* Supports one powerful 3rd party library: Jedi. By only supporting Jedi, we can focus on supporting all Jedi features without exposing ourselves to too many broken 3rd party dependencies (I'm looking at you, [rope](https://github.com/python-rope/rope)).
* Is supremely simple because of its scope constraints. Leave complexity to the Jedi [master](https://github.com/davidhalter). If the force is strong with you, please submit a PR!

## Written by

Samuel Roeca *samuel.roeca@gmail.com*
