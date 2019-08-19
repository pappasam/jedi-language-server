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

## Motivation

My motivation goes here...

## Usage

It currently works only over IO.

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

## Written by

Samuel Roeca *samuel.roeca@gmail.com*
