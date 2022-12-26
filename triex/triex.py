"""
A tool to generate semi-minimized regular expression alternations.
"""
from typing import Any


TrieNode = dict[str, "TrieNode"]
DataValue = int | float | str
DataInput = list[DataValue] | DataValue | None


class Trie:
    """Trie data structure.

    Create and manipulate a trie representation of one or more strings. Duplicates are pruned before insertion,
    and members are cached to allow insertion without re-generating the entire trie.

    Args:
        data: A value or `list` of values to be added to the trie. Values may be a `str`, `int` and/or `float`.

    Attributes:
        silent: Indicates whether invalid values should be skipped silently during insertion or raise an Exception.
    """

    def __init__(self, data: DataInput = None, silent: bool = True):
        self._structure: TrieNode = {}
        self._invalid: list[Any] = []
        self._members: list[str] = []
        self.silent = silent

        self.add(data)

    def add(self, data: DataInput) -> None:
        """
        Add values to the trie

        Args:
            data: A value or list of values to add to the trie.
        """
        if data is None:
            data = []
        elif not isinstance(data, list):
            data = [data]

        processed_data = self._prune(self._coerce(data))
        self._insert(processed_data)

    @property
    def invalid(self) -> list[Any]:
        """A sorted list of values that could not be added to the trie."""
        return sorted(self._invalid)

    @property
    def members(self) -> list[str]:
        """A sorted list of values added to the trie."""
        return sorted(self._members)

    @property
    def structure(self) -> TrieNode:
        """The trie data structure."""
        return self._structure

    def to_regex(self, boundary: bool = False, capturing: bool | None = None) -> str:
        """Convert the trie to a regular expression.

        Args:
            boundary: Indicates whether the regex should be surrounded by boundary ('\b') tokens.
            capturing: Indicates whether the pattern should be in a capturing (`True`) or non-capturing (`False`) group.
                       When value is `None` the pattern will not be grouped unless `boundary` is `True` in which case it
                       will be made a non-capturing group so the boundary tokens apply to all items in the pattern.
        """
        return Regex(self, boundary=boundary, capturing=capturing).pattern

    def _coerce(self, data: list[DataValue]) -> list[str]:
        """Coerce raw values to string objects.

        If `self.silent` is `True` processing will continue after encountering an invalid value, otherwise processing
        stops and raises an exception.

        Args:
            data: A list of values.

        Raises:
            TypeError: When a value could not be coerced to a string.
        """
        coerced = []

        for value in data:
            if not isinstance(value, (str, float, int)):
                self._invalid.append(value)
                if not self.silent:
                    raise TypeError(f'Cannot add value "{value}" with data type "{type(value)}" to trie')
            else:
                coerced.append(str(value))

        return coerced

    def _insert(self, data: list[str]) -> None:
        """Insert values in the trie.

        Args:
            data: A list of string objects.
        """
        for value in data:
            node = self._structure

            for char in value:
                if not char in node:
                    node[char] = {}

                node = node[char]

            node[""] = {}
            self._members.append(value)

    def _prune(self, data: list[str]) -> list[str]:
        """Prune duplicate values from the input data and values in `self.members`.

        Args:
            data: A list of values.
        """
        data = list(set(data))
        return [v for v in data if v not in self.members]


class Regex:  # pylint: disable=r0903
    """A regular expression generated from a trie data structure.

    Args:
        trie: A `Trie` data object.

    Attributes:
        boundary: Indicates whether the regex should be surrounded by boundary ('\b') tokens.
        capturing: Indicates whether the pattern should be in a capturing (`True`) or non-capturing (`False`) group.
                   When value is `None` the pattern will not be grouped unless `boundary` is `True` in which case it
                   will be made a non-capturing group so the boundary tokens apply to all items in the pattern.
        _pattern: The regex pattern built from the trie.
    """

    def __init__(self, trie: Trie, boundary: bool = False, capturing: bool | None = None):
        self.boundary = boundary

        if boundary and capturing is None:
            capturing = False

        self.capturing = capturing

        self._pattern = self._construct(trie.structure, is_outer=True)

    @property
    def pattern(self) -> str:
        """A regex pattern generated from the Trie."""
        formatted_pattern = self._pattern

        if self.capturing is not None:
            control_chars = "" if self.capturing else "?:"
            formatted_pattern = rf"({control_chars}{formatted_pattern})"

        if self.boundary:
            formatted_pattern = rf"\b{formatted_pattern}\b"

        return formatted_pattern

    def _construct(self, data: TrieNode, is_outer=False) -> str:
        """
        Construct a regular expression from a trie structure.

        Args:
            data: A trie data structure.
            is_outer: Whether the method call is the outermost in the recursive stack.
        """
        node = data

        alternates = []
        char_class = []
        optional = False

        if "" in node and len(node) == 1:
            return ""

        for child_node in sorted(node):
            if len(node[child_node]) > 0:
                children = self._construct(node[child_node])

                if children:
                    child_node = self._escape(child_node, False)
                    alternates.append(f"{child_node}{children}")
                else:
                    child_node = self._escape(child_node, True)
                    char_class.append(child_node)
            else:
                optional = True

        alternates_count = len(alternates)

        if char_class:
            char_class = self._make_char_class(char_class)
            alternates.append(char_class)

        alternates = self._make_alternates(alternates, is_outer)

        if optional:
            alternates = self._make_optional(alternates, alternates_count)

        return alternates

    def _escape(self, char: str, char_class: bool) -> str:
        """Escape regex control characters.

        Args:
            char: The character to escape.
            char_class: Whether `character` is part of a character class.
        """
        control_chars = r"^-]\\" if char_class else r".^$*+?()[{\|"

        if char in control_chars:
            return rf"\{char}".format(char)

        return char

    def _make_alternates(self, values: list[str], is_outer: bool = False) -> str:
        """Make regex alternation (e.g., foo|bar|baz).

        Args:
            values: A list of alternate values
            is_outer: Whether `values` are the outermost in the pattern. Inner alternations are placed in non-capturing
                      groups.
        """
        if len(values) == 1:
            return values[0]

        alternates = r"|".join(values)

        if not is_outer:
            alternates = rf"(?:{alternates})"

        return alternates

    def _make_char_class(self, values: list[str]) -> str:
        """Make regex character class (e.g., [AZ123]).

        Args:
            values: A list of characters
        """
        if len(values) == 1:
            return values[0]

        chars = "".join(values)
        return rf"[{chars}]"

    def _make_optional(self, value, count) -> str:
        """Make character class or alternation optional.

        Args:
            value: The partial regex pattern value
            count: The number of non-character class alternates.
        """
        return rf"{value}?" if count < 1 else rf"(?:{value})?"
