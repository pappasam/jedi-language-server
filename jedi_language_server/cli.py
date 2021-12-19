"""Jedi Language Server command line interface."""

import argparse
import logging
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

    Run over stdio     : jedi-language-server
    Run over tcp       : jedi-language-server --tcp
    Run over websockets:
        # only need to pip install once per env
        pip install pygls[ws]
        jedi-language-server --ws

Notes:

    For use with web sockets, user must first run
    'pip install pygls[ws]' to install the correct
    version of the websockets library.
""",
    )
    parser.add_argument(
        "--version",
        help="display version information and exit",
        action="store_true",
    )
    parser.add_argument(
        "--tcp",
        help="use TCP web server instead of stdio",
        action="store_true",
    )
    parser.add_argument(
        "--ws",
        help="use web socket server instead of stdio",
        action="store_true",
    )
    parser.add_argument(
        "--host",
        help="host for web server (default 127.0.0.1)",
        type=str,
        default="127.0.0.1",
    )
    parser.add_argument(
        "--port",
        help="port for web server (default 2087)",
        type=int,
        default=2087,
    )
    parser.add_argument(
        "--log-file",
        help="redirect logs to file specified",
        type=str,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="increase verbosity of log output",
        action="count",
        default=0,
    )
    args = parser.parse_args()
    if args.version:
        print(get_version())
        sys.exit(0)
    if args.tcp and args.ws:
        print(
            "Error: --tcp and --ws cannot both be specified",
            file=sys.stderr,
        )
        sys.exit(1)
    log_level = {0: logging.WARN, 1: logging.INFO, 2: logging.DEBUG}.get(
        args.verbose,
        logging.DEBUG,
    )

    if args.log_file:
        logging.basicConfig(
            filename=args.log_file,
            filemode="w",
            level=log_level,
        )
    else:
        logging.basicConfig(stream=sys.stderr, level=log_level)

    if args.tcp:
        SERVER.start_tcp(host=args.host, port=args.port)
    elif args.ws:
        SERVER.start_ws(host=args.host, port=args.port)
    else:
        SERVER.start_io()
