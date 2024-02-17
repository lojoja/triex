# Triex

A tool to generate semi-minimized regular expression alternations.

Given a list of `str`, `int`, and `float` values, triex constructs a trie data structure and generates a minimized regular expression that matches all members in the trie. The regex is created walking the values left-to-right, so the best results are achieved with values that share a common prefix.

## Requirements

- Python 3.10.x, 3.11.x

## Installation

```
pip install py-triex
```

## Usage

### As a Library

```
>>> from triex import Trie
>>> t = Trie(['foo', 'foobar', 'foobaz', 'bar', 'bat'])
>>> t.to_regex()
ba[rt]|foo(?:ba[rz])?
```

### Command Line

```
Usage: triex [OPTIONS] COMMAND [ARGS]...

  A tool to generate semi-minimized regular expression alternations.

Options:
  --help         Show this message and exit.
  -v, --verbose  Increase verbosity.
  --version      Show the version and exit.

Commands:
  batch    Batch convert file contents to patterns.
  convert  Convert input to a regex pattern.
```

#### Examples

Convert:

```
$ echo "foo\nfoobar\nfoobaz\nbar\nbat" > words.txt
$ triex convert -i words.txt
ba[rt]|foo(?:ba[rz])?
$ echo -e "foo\nfoobar\nfoobaz\nbar\nbat" | triex convert
ba[rt]|foo(?:ba[rz])?
```

Batch:

```
$ printf "foo\nbar" > words1.txt
$ printf "foo\nbaz" > words2.txt
$ triex batch *.txt
Converting words1.txt
Converting words2.txt
$ less -FX words1.txt
bar|foo
$ less -FX words2.txt
baz|foo
```

## License

triex is released under the [MIT License](./LICENSE)
