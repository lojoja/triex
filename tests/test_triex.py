# pylint: disable=missing-module-docstring,missing-function-docstring,protected-access

from contextlib import nullcontext as does_not_raise
import re
import typing as t

import pytest

from triex.triex import Regex, Trie


@pytest.mark.parametrize("values", [None, "foo", [], ["foo", "bar", "foo"]])
def test_trie_add(values: t.Optional[str | list[str]]):
    if values is None:
        expected = []
    elif isinstance(values, str):
        expected = [values]
    else:
        expected = [str(i) for i in set(values)]

    trie = Trie()
    trie.add(values)

    assert trie.members == sorted(expected)


def test_trie_invalid():
    assert Trie([None]).invalid == [None]  # type:ignore


def test_trie_members():
    assert Trie(["foo", "bar"]).members == ["bar", "foo"]


def test_trie_structure():
    assert Trie(["foo"]).structure == {"f": {"o": {"o": {"": {}}}}}


def test_to_regex():
    pattern = Trie(["foo", "bar"]).to_regex(True, True)
    assert pattern == r"\b(bar|foo)\b"


@pytest.mark.parametrize("silent", [True, False])
def test_trie__coerce(silent: bool):
    values = ["foo", 1, 1.0, None]
    context = does_not_raise() if silent else pytest.raises(TypeError, match=r"Cannot add value .*")

    trie = Trie(silent=silent)

    with context:
        result = trie._coerce(values)

    if silent:
        assert result == [str(i) for i in values[0:-1]]
        assert trie.invalid == sorted([values[-1]])


def test_trie__insert():
    values = ["foo", "bar", "baz"]
    trie = Trie()
    trie._insert(values)

    assert trie.members == sorted(values)
    assert trie.structure == {"b": {"a": {"r": {"": {}}, "z": {"": {}}}}, "f": {"o": {"o": {"": {}}}}}


def test_trie__prune():
    trie = Trie(["foo"])
    new_values = ["bar", "baz"]
    result = trie._prune(new_values + trie.members)

    assert sorted(result) == sorted(new_values)


@pytest.mark.parametrize("boundary", [True, False])
def test_regex_boundary(boundary: bool):
    regex = Regex(Trie(), boundary=boundary)
    assert regex.boundary == boundary


@pytest.mark.parametrize("capturing", [None, True, False])
@pytest.mark.parametrize("boundary", [True, False])
def test_regex_capturing(boundary: bool, capturing: t.Optional[bool]):
    regex = Regex(Trie(), boundary=boundary, capturing=capturing)
    assert regex.capturing == (False if boundary and capturing is None else capturing)


@pytest.mark.parametrize("capturing", [None, True, False])
@pytest.mark.parametrize("boundary", [True, False])
def test_regex_pattern(
    raw_values: list[str],
    build_pattern: t.Callable[[bool, t.Optional[bool]], str],
    boundary: bool,
    capturing: t.Optional[bool],
):
    trie = Trie(raw_values)
    regex = Regex(trie, boundary, capturing)

    assert regex.pattern == build_pattern(boundary, capturing)
    assert all(re.match(regex.pattern, v) is not None for v in trie.members)


def test_regex__construct():
    trie = Trie(["foo", "bar", "ba$", "ba-", "foos", "x.y"])
    regex = Regex(trie)
    assert regex._construct(trie.structure, is_outer=True) == r"ba[$\-r]|foos?|x\.y"


def test_regex_escape():
    trie = Trie(["f.123", "f.$56"])
    regex = Regex(trie)

    assert regex.pattern == r"f\.(?:\$56|123)"
    assert all(re.match(regex.pattern, v) is not None for v in trie.members)


@pytest.mark.parametrize("char_class", [True, False])
@pytest.mark.parametrize("char", ["^", "$", "-", "\\", "|", ".", "*", "+", "(", ")", "[", "]", "{"])
def test_regex__escape(char: str, char_class: bool):
    expected = rf"\{char}" if char in (r"^-]\\" if char_class else r".^$*+?()[{\|") else char
    regex = Regex(Trie())
    assert regex._escape(char, char_class) == expected


@pytest.mark.parametrize("outer", [True, False])
@pytest.mark.parametrize("values", [["foo"], ["foo", "bar"]])
def test_regex__make_alternates(values: list[str], outer: bool):
    expected = values[0] if len(values) == 1 else "|".join(values) if outer else rf"(?:{'|'.join(values)})"
    regex = Regex(Trie())
    assert regex._make_alternates(values, outer) == expected


@pytest.mark.parametrize("values", [["A"], ["A", "B"]])
def test_regex__make_char_class(values: list[str]):
    regex = Regex(Trie())
    assert regex._make_char_class(values) == (values[0] if len(values) == 1 else rf"[{''.join(values)}]")


@pytest.mark.parametrize("count", [0, 1])
def test_regex__make_optional(count: int):
    regex = Regex(Trie())
    assert regex._make_optional("foo|bar", count) == (r"foo|bar?" if count < 1 else r"(?:foo|bar)?")
