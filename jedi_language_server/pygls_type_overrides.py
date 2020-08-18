"""Type overrides where things don't work correctly.

Since some language clients care about missing values, we override some
types
"""

from typing import List

# pylint: disable=too-few-public-methods, invalid-name


class ParameterInformation:
    """Override because we don't want key "documentation" to exists."""

    def __init__(self, label: str):
        self.label = label


class SignatureInformation:
    """Override because we don't want key "documentation" to exists."""

    def __init__(self, label: str, parameters: List[ParameterInformation]):
        self.label = label
        self.parameters = parameters


class SignatureHelp:
    """Override because we want this module's SignatureInformation."""

    def __init__(
        self,
        signatures: List[SignatureInformation],
        active_signature: int = 0,
        active_parameter: int = 0,
    ):
        self.signatures = signatures
        self.activeSignature = active_signature
        self.activeParameter = active_parameter
