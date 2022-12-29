# pylint: disable=c0114,c0116

import pytest

from triex import Trie


@pytest.mark.parametrize(
    ["init_data", "extra_data", "valid", "members", "structure"],
    [
        (None, [], True, [], {}),
        ([], [], True, [], {}),
        ("foo", [], True, ["foo"], {"f": {"o": {"o": {"": {}}}}}),
        (
            ["foo", 1, 1.0],
            [],
            True,
            ["1", "1.0", "foo"],
            {"f": {"o": {"o": {"": {}}}}, "1": {".": {"0": {"": {}}}, "": {}}},
        ),
        ("foo", ["foo", "bar"], True, ["bar", "foo"], {"f": {"o": {"o": {"": {}}}}, "b": {"a": {"r": {"": {}}}}}),
        ([], [None], False, [], {}),
    ],
    ids=["no value (None)", "no value (list)", "single value", "multiple values", "duplicate values", "invalid values"],
)
def test_trie_data(init_data, extra_data, valid, members, structure):
    trie = Trie(init_data, silent=valid)

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
