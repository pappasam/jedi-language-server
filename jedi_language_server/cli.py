"""Jedi Language Server command line interface."""


import argparse
import sys

from .server import SERVER


def get_version() -> str:
    """Get the program version."""
    # pylint: disable=import-outside-toplevel
    try:
        # Type checker for Python < 3.8 fails.
        # Since this ony happens here, we just ignore.
        from importlib.metadata import version  # type: ignore
    except ImportError:
        try:
            # Below ignored both because this a redefinition from above, and
            # because importlib_metadata isn't known by mypy. Ignored because
            # this is intentional.
            from importlib_metadata import version  # type: ignore
        except ImportError:
            print(
                "Error: unable to get version. "
                "If using Python < 3.8, you must install "
                "`importlib_metadata` to get the version.",
                file=sys.stderr,
            )
            sys.exit(1)
    return version("jedi-language-server")


def cli() -> None:
    """Jedi language server cli entrypoint."""
    parser = argparse.ArgumentParser(
        prog="jedi-language-server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Jedi language server: an LSP wrapper for jedi.",
        epilog="""\
Examples:

    Run from stdio: jedi-language-server
""",
    )
    parser.add_argument("--version", action="store_true")
    args = parser.parse_args()
    if args.version:
        print(get_version())
        sys.exit(0)
    SERVER.start_io()
