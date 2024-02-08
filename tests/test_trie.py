# pylint: disable=missing-function-docstring,missing-module-docstring

import pytest

from triex import Trie
from triex.triex import _TrieNode, _DataInput


@pytest.mark.parametrize(
    ["init_data", "extra_data", "valid", "members", "structure", "silent"],
    [
        (None, [], True, [], {}, True),
        ([], [], True, [], {}, True),
        ("foo", [], True, ["foo"], {"f": {"o": {"o": {"": {}}}}}, True),
        (
            ["foo", 1, 1.0],
            [],
            True,
            ["1", "1.0", "foo"],
            {"f": {"o": {"o": {"": {}}}}, "1": {".": {"0": {"": {}}}, "": {}}},
            True,
        ),
        ("foo", ["foo", "bar"], True, ["bar", "foo"], {"f": {"o": {"o": {"": {}}}}, "b": {"a": {"r": {"": {}}}}}, True),
        ([], [None], False, [], {}, False),
        ([], ["foo", None], True, ["foo"], {"f": {"o": {"o": {"": {}}}}}, True),
    ],
    ids=[
        "no value (None)",
        "no value (list)",
        "single value",
        "multiple values",
        "duplicate values",
        "invalid values",
        "valid+invalid values (silent)",
    ],
)
def test_trie_data(
    init_data: _DataInput, extra_data: _DataInput, valid: bool, members: list[str], structure: _TrieNode, silent: bool
):
    trie = Trie(init_data, silent=silent)

    if extra_data:
        if valid:
            trie.add(extra_data)
        else:
            with pytest.raises(TypeError):
                trie.add(extra_data)
            assert trie.invalid == extra_data

    assert trie.members == members
    assert trie.structure == structure


def test_to_regex():
    trie = Trie(["foo", "bar"])
    pattern = trie.to_regex()

    assert pattern == "bar|foo"
