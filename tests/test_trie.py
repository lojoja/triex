# pylint: disable=c0114,c0116

import pytest

from triex import Trie


@pytest.mark.parametrize(
    ["data", "expected_members", "expected_structure"],
    [
        (None, [], {}),
        ([], [], {}),
        ("foo", ["foo"], {"f": {"o": {"o": {"": {}}}}}),
        (["foo", 1, 1.0], ["1", "1.0", "foo"], {"f": {"o": {"o": {"": {}}}}, "1": {".": {"0": {"": {}}}, "": {}}}),
    ],
)
def test_create_with_valid_data(data, expected_members, expected_structure):
    trie = Trie(data)

    assert trie.members == expected_members
    assert trie.structure == expected_structure


def test_add_invalid_data():
    trie = Trie(silent=False)

    with pytest.raises(TypeError):
        trie.add([None])  # type: ignore

    assert trie.members == []
    assert trie.invalid == [None]


def test_add_duplicate_data():
    trie = Trie("foo")
    trie.add(["bar", "foo"])

    assert trie.members == ["bar", "foo"]
    assert trie.structure == {"f": {"o": {"o": {"": {}}}}, "b": {"a": {"r": {"": {}}}}}


def test_to_regex():
    trie = Trie(["foo", "bar"])
    pattern = trie.to_regex()

    assert pattern == "bar|foo"
