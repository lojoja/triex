# pylint: disable=missing-function-docstring,missing-module-docstring

import re
import typing as t

import pytest

from triex import Trie, Regex


@pytest.fixture(name="values")
def fixture_values() -> list[str]:
    return ["foo", "foobar", "foobaz", "bar", "bat"]


@pytest.fixture(name="pattern")
def fixture_pattern() -> str:
    return r"ba[rt]|foo(?:ba[rz])?"


@pytest.fixture(name="patterns")
def fixture_patterns(pattern) -> dict[str, str]:
    return {
        "default": pattern,
        "boundary": f"\\b(?:{pattern})\\b",
        "boundary (capturing)": f"\\b({pattern})\\b",
        "boundary (non-capturing)": f"\\b(?:{pattern})\\b",
        "capturing": f"({pattern})",
        "non-capturing": f"(?:{pattern})",
    }


@pytest.mark.parametrize(
    ["boundary", "capturing", "pattern_name"],
    [
        (False, None, "default"),
        (True, None, "boundary"),
        (True, True, "boundary (capturing)"),
        (True, False, "boundary (non-capturing)"),
        (False, True, "capturing"),
        (False, False, "non-capturing"),
    ],
    ids=["default", "boundary", "boundary (capturing)", "boundary (non-capturing)", "capturing", "non-capturing"],
)
def test_pattern(
    values: list[str], patterns: dict[str, str], boundary: bool, capturing: t.Optional[bool], pattern_name: str
):
    trie = Trie(values)
    regex = Regex(trie, boundary, capturing)

    assert regex.pattern == patterns[pattern_name]

    for value in trie.members:
        assert re.match(regex.pattern, value) is not None


def test_escape():
    trie = Trie(["f.123", "f.$56"])
    regex = Regex(trie)

    assert regex.pattern == r"f\.(?:\$56|123)"

    for value in trie.members:
        assert re.match(regex.pattern, value) is not None
