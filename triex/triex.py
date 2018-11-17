__version__ = '1.0.0'


class DataError(TypeError):
    """
    DataError Exception.

    Raised when data cannot be inserted in the trie.

    Args:
        data: The data that caused the error.
    """

    def __init__(self, data):
        self.message = 'Cannot add data type {}'.format(type(data))
        super(DataError, self).__init__(self.message)


class Trie(object):
    """
    Trie data structure.

    Create and manipulate a trie representation of one or more strings. Duplicates are pruned before insertion,
    and members are cached to allow insertion without re-generating the entire trie.
    """

    def __init__(self, data=None, silent=True):
        """
        Initialize trie structure.

        Args:
            data: An optional value or list of values to be added to the trie. Values may be a string, int and/or float.
            silent: An optional boolean indicating whether invalid data should be skipped silently during insertion
                or raise an Exception.
        """
        self._trie = {}
        self._invalid = []
        self._members = []
        self.silent = silent

        self.add(data)

    def add(self, data):
        """
        Add data to the trie.

        Args:
            data: An optional value or list of values to be added to the trie. Values may be a string, int and/or float.
        """
        if not isinstance(data, list):
            data = [data]

        data = self._prune(self._coerce(data))
        self._insert(data)

    @property
    def invalid(self):
        """
        A list of values that could not be added to the trie. This list will be empty if `self.silent` is `False`.
        """
        return self._invalid

    @property
    def members(self):
        """
        A list of all values in the trie.
        """
        return self._members

    def to_regex(self, boundary=False, parenthesis=False, capturing=False):
        """
        Convert the trie to a regular expression.

        Args:
            boundary: An optional boolean indicating whether to include surrounding boundary '\b' tokens.
            parenthesis: An optional boolean indicating whether to surround the entire pattern in parenthesis.
            capturing: An optional boolean indicating whether the surrounding parenthesis represent a capturing or
                non-capturing group. This value is ignored if `parenthesis` is `False`.
        """
        return Regex(self._trie).pattern(
            boundary=boundary, parenthesis=parenthesis, capturing=capturing
        )

    def _coerce(self, data):
        """
        Coerce raw values to string objects.

        If a value cannot be coerced and `self.silent` is `True`, the value will be added to `self._invalid` and
        processing will continue. If `self.silent` is `False`, processing stops and raises an exception.

        Args:
            data: A list of values.

        Raises:
            DataError: When a value is not a string, int, or float.
        """
        coerced = []

        for value in data:
            if not isinstance(value, (str, float, int)):
                if not self.silent:
                    raise DataError(value)
                self._invalid.append(value)
            else:
                coerced.append(str(value))

        return coerced

    def _insert(self, data):
        """
        Insert values in the trie and add to `self._members`.

        Args:
            data: A list of string objects.
        """
        for string in data:
            node = self._trie

            for char in string:
                try:
                    node[char]
                except KeyError:
                    node[char] = {}

                node = node[char]

            node[''] = None
            self._members.append(string)

    def _prune(self, data):
        """
        Reduce data to unique values.

        Args:
            data: A list of values.
        """
        data = set(data)
        return [v for v in data if v not in self.members]


class Regex(object):
    """
    Regular Expression.

    A regular expression generated from a trie data structure.
    """

    def __init__(self, trie):
        """
        Initialize regular expression.

        Args:
            trie: A `Trie` object.
        """
        self._pattern = self._construct(trie, is_outer=True)

    def pattern(self, boundary=False, parenthesis=False, capturing=False):
        """
        A regex pattern generated from the Trie.

        Args:
            boundary: An optional boolean indicating whether to include surrounding boundary '\b' tokens.
            parenthesis: An optional boolean indicating whether to surround the entire pattern in parenthesis.
            capturing: An optional boolean indicating whether the surrounding parenthesis represent a capturing or
                non-capturing group. If this value is `True`, `parenthesis` will be set to `True` automatically.
        """
        pattern = self._pattern
        parenthesis = True if capturing else parenthesis

        if parenthesis:
            pattern = r'({0}{1})'.format('?:' if capturing else '', pattern)

        if boundary:
            pattern = r'\b{}\b'.format(pattern)

        return pattern

    def _construct(self, data, is_outer=False):
        """
        Construct a regular expression from a trie.

        Recursively build a regular expression by walking a trie data structure, grouping alternates and character
        classes.

        Args:
            data: A `Trie` object to construct the regex from.
            is_outer: Whether the method call is the outermost in the recursive stack.
        """
        node = data

        alternates = []
        char_class = []
        optional = False

        if '' in node and len(node) == 1:
            return None

        for child_node in sorted(node):
            if isinstance(node[child_node], dict):
                children = self._construct(node[child_node])
                try:
                    child_node = self._escape(child_node, False)
                    alternates.append(child_node + children)
                except TypeError:
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

    def _escape(self, char, char_class):
        """
        Escape special characters.

        Args:
            char: The character to escape.
            char_class: A boolean flag indicating whether `character` is part of a character class.
        """
        special_chars = r'^-]\\' if char_class else r'.^$*+?()[{\|'

        if char in special_chars:
            return r'\\{}'.format(char)

        return char

    def _make_alternates(self, strings, is_outer=False):
        """
        Make regex alternations (e.g., foo|bar|baz)

        Args:
            strings: A list of alternate string objects.
            is_outer: Whether `strings` are the outermost in the pattern. Determine whether the alternates are
                surrounded by parenthesis (when `False`) or not (when `True`).
        """
        if len(strings) == 1:
            return strings[0]

        if is_outer:
            return r'{}'.format(r'|'.join(strings))
        else:
            return r'(?:{})'.format(r'|'.join(strings))

    def _make_char_class(self, string):
        """
        Make regex character class (e.g., [AZ123])

        Args:
            string: A string object with 1 or more characters.
        """
        if len(string) == 1:
            return string[0]

        return r'[{}]'.format(r''.join(string))

    def _make_optional(self, string, count):
        """
        Make character class or alternation optional.

        Args:
            string: A complete alternation pattern.
            count: The number of non-character class alternates.
        """
        if count < 1:
            return r'{}?'.format(string)
        else:
            return r'(?:{})?'.format(string)
