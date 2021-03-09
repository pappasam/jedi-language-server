"""Jedi Language Server.

Code in this module is a temporary workaround to address the following issues:
- <https://github.com/microsoft/vscode-languageserver-node/issues/
740#issuecomment-773967897>
- <https://github.com/pappasam/jedi-language-server/issues/60>
- <https://github.com/openlawlibrary/pygls/issues/145>
- <https://github.com/microsoft/vscode-languageserver-node/issues/740>

It's temporary, and taken almost in its entirety from:

<https://github.com/karthiknadig/vscode-python/blob/main/pythonFiles/
runJediLanguageServer.py>

Remove when either version 0.10 or 1.0 is released for pygls.
"""

import os
import sys
from typing import Any, Optional

import pygls.protocol

# pylint: disable=invalid-name

try:
    unicode  # pylint: disable=used-before-assignment
except Exception:  # pylint: disable=broad-except
    unicode = str


def is_json_basic_type(obj: Any) -> bool:
    """Checks if the object is an int, float, bool, or str."""
    if isinstance(obj, (int, float, bool, str)):
        return True
    return sys.version_info < (3,) and isinstance(obj, unicode)


def handle_null_fields(obj: Any, obj_field_name: Optional[str] = None) -> None:
    """Removes fields with a 'None' value.

    The LS Client in VS Code expects optional fields that are not needed
    to be omitted. Unfortunately, pygls uses 'null' in these instances.
    """
    if is_json_basic_type(obj):
        return
    if isinstance(obj, list):
        for o in obj:
            handle_null_fields(o, obj_field_name)
        return
    if isinstance(obj, dict):
        for k, v in obj.items():
            handle_null_fields(v, k)

    important_attribute = lambda x: not x.startswith("_") and not callable(
        getattr(obj, x)
    )

    for attr in filter(important_attribute, dir(obj)):
        member = getattr(obj, attr)
        if member is None:
            # This is a special condition to handle
            # VersionedTextDocumentIdentifier object.
            # See issues:
            # https://github.com/pappasam/jedi-language-server/issues/61
            # https://github.com/openlawlibrary/pygls/issues/146
            #
            # The version field should either use `0` or the value received
            # from `client`. Seems like using `null` or removing this causes VS
            # Code to ignore code actions.
            if (
                attr == "version"
                and obj_field_name == "textDocument"
                and "uri" in dir(obj)
            ):
                setattr(obj, "version", 0)
            else:
                delattr(obj, attr)

        elif is_json_basic_type(member):
            continue

        else:
            handle_null_fields(member, attr)


def patched_without_none_fields(
    resp: pygls.protocol.JsonRPCResponseMessage,
) -> pygls.protocol.JsonRPCResponseMessage:
    """Monkeypatch for `JsonRPCResponseMessage.without_none_fields` to remove
    `None` results."""
    if resp.error is None:
        del resp.error
        if hasattr(resp, "result"):
            handle_null_fields(resp.result)
    else:
        del resp.result
    return resp


pygls.protocol.JsonRPCResponseMessage.without_none_fields = (  # type: ignore
    patched_without_none_fields
)
