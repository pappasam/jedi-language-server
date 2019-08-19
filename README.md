# jedi-language-server

[![image-version](https://img.shields.io/pypi/v/jedi-language-server.svg)](https://python.org/pypi/jedi-language-server)
[![image-license](https://img.shields.io/pypi/l/jedi-language-server.svg)](https://python.org/pypi/jedi-language-server)
[![image-python-versions](https://img.shields.io/pypi/pyversions/jedi-language-server.svg)](https://python.org/pypi/jedi-language-server)

A [Language Server](https://microsoft.github.io/language-server-protocol/) for [Jedi](https://jedi.readthedocs.io/en/latest/).

## Installation

```bash
# With pip
pip install jedi-language-server

# With poetry
poetry add jedi-language-server
```

## Usage

It currently works only over IO. This may change in the future.

```bash
jedi-language-server
```

## Local Development

Local development for this project is quite simple.

**Dependencies**

Install the following tools manually.

* [Poetry](https://github.com/sdispater/poetry#installation)
* [GNU Make](https://www.gnu.org/software/make/)

*Recommended*

* [pyenv](https://github.com/pyenv/pyenv)

**Set up development environment**

```bash
make setup
```

**Run Tests**

```bash
make test
```

## Inspiration

[Palantir's python-language-server](https://github.com/palantir/python-language-server) inspired this project. Jedi Language Server differs from Palantir's language server; JLS:

* Uses [pygls](https://github.com/openlawlibrary/pygls) instead of creating its own low-level LSP bindings
* Supports one powerful 3rd party library, [Jedi](https://github.com/davidhalter/jedi). By only supporting Jedi, I can focus on ironing out any issues I find with Jedi.
* Is super simple. Given the above scope, I hope you're convinced that it will continue to be super simple. Leave the complexity to the [Jedi master](https://github.com/davidhalter).

## Written by

Samuel Roeca *samuel.roeca@gmail.com*
