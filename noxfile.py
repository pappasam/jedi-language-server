"""Configure nox."""

import nox

NOX_SESSION = nox.session(python=False)


@NOX_SESSION
def fix(session: nox.Session) -> None:
    """Fix files inplace."""
    session.run("ruff", "format", "-s", ".")
    session.run("ruff", "check", "-se", "--fix", ".")


@NOX_SESSION
def lint(session: nox.Session) -> None:
    """Check file formatting that only have to do with formatting."""
    session.run("ruff", "format", "--check", ".")
    session.run("ruff", "check", ".")


@NOX_SESSION
def typecheck(session: nox.Session) -> None:
    session.run("mypy", "jedi_language_server")


@NOX_SESSION
def tests(session: nox.Session) -> None:
    session.run(
        "slipcover", "--source", "jedi_language_server", "-m", "pytest"
    )
