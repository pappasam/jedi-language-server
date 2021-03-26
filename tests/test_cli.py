"""Test the CLI."""

from jedi_language_server.cli import cli, get_version


def test_get_version() -> None:
    """Test that the get_version function returns a string."""
    assert isinstance(get_version(), str)


def test_cli() -> None:
    """Test the basic cli behavior."""
    assert cli
