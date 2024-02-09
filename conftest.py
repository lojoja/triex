# pylint: disable=missing-module-docstring,missing-function-docstring

import typing as t

import pytest


@pytest.fixture(name="build_pattern", scope="session")
def build_pattern_fixture() -> t.Callable[[bool, t.Optional[bool]], str]:
    """Builds a regex pattern with the given options using the `raw_values` fixture data."""

    def build_pattern(boundary: bool, capturing: t.Optional[bool]) -> str:
        pattern = r"ba[rt]|foo(?:ba[rz])?"

        if capturing is False or (boundary and capturing is None):
            pattern = rf"(?:{pattern})"
        elif capturing:
            pattern = rf"({pattern})"

        if boundary:
            pattern = rf"\b{pattern}\b"

        return pattern

    return build_pattern


@pytest.fixture(name="raw_values", scope="session")
def raw_values_fixture() -> list[str]:
    """Common values to use for verifying regex patterns."""
    return ["foo", "foobar", "foobaz", "bar", "bat"]
