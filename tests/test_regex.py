import re

import pytest

from triex.triex import Trie, Regex


@pytest.mark.parametrize(
    ["boundary", "capturing", "expected"],
    [
        (True, None, rf"\b(?:ba[rt]|foo(?:ba[rz])?)\b"),
        (True, True, rf"\b(ba[rt]|foo(?:ba[rz])?)\b"),
        (True, False, rf"\b(?:ba[rt]|foo(?:ba[rz])?)\b"),
        (False, None, rf"ba[rt]|foo(?:ba[rz])?"),
        (False, True, rf"(ba[rt]|foo(?:ba[rz])?)"),
        (False, False, rf"(?:ba[rt]|foo(?:ba[rz])?)"),
    ],
)
def test_pattern(boundary, capturing, expected):
    trie = Trie(["foo", "foobar", "foobaz", "bar", "bat"])
    regex = Regex(trie, boundary, capturing)

    assert regex.pattern == expected

    for value in trie.members:
        assert re.match(regex.pattern, value) is not None


def test_escape():
    trie = Trie(["f.123", "f.$56"])
    regex = Regex(trie)

    assert regex.pattern == rf"f\.(?:\$56|123)"

    for value in trie.members:
        assert re.match(regex.pattern, value) is not None
