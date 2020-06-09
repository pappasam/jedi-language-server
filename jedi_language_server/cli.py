"""Jedi Language Server command line interface."""

import click

from .server import SERVER


@click.command()
@click.version_option()
def cli() -> None:
    """Jedi language server.

    Examples:

        Run from stdio : jedi-language-server
    """
    SERVER.start_io()
