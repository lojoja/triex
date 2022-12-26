# Triex

A tool to generate semi-minimized regular expression alternations.

Given a list of `str`, `int`, and `float` values, triex constructs a trie data structure and generates a minimized regular expression that matches all members in the trie. The regex is created walking the values left-to-right, so the best results are achieved with values that share a common prefix.


## Requirements

* Python 3.10.x


## Usage

### As a Library

```
>>> from triex import Trie
>>> t = Trie(['foo', 'foobar', 'foobaz', 'bar', 'bat'])
>>> t.to_regex()
>>> ba[rt]|foo(?:ba[rz])?
```

### Command Line

```
```

#### Examples

```
> printf "foo\nfoobar\nfoobaz\nbar\nbat" > words.txt
> triex words.txt
ba[rt]|foo(?:ba[rz])?
```
