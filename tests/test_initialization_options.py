"""Test parsing of the initialization options."""

import re

from hamcrest import assert_that, is_

from jedi_language_server.initialization_options import InitializationOptions


def test_initialization_options() -> None:
    """Test our adjustments to parsing of the initialization options."""

    initialization_options = InitializationOptions.model_validate(
        {
            "completion": {
                "resolveEagerly": True,
                "ignorePatterns": [r"foo", r"bar/.*"],
            },
            "hover": {
                "disable": {
                    "keyword": {"all": False},
                    "class": {"all": True},
                    "function": {"all": True},
                },
            },
            "extra": "ignored",
        },
    )

    assert_that(initialization_options.completion.resolve_eagerly, is_(True))
    assert_that(
        initialization_options.completion.ignore_patterns,
        is_(
            [
                re.compile(r"foo"),
                re.compile(r"bar/.*"),
            ]
        ),
    )
    assert_that(initialization_options.hover.disable.keyword_.all, is_(False))
    assert_that(initialization_options.hover.disable.class_.all, is_(True))
    assert_that(initialization_options.hover.disable.function_.all, is_(True))
