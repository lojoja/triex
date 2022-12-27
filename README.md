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
Usage: triex [OPTIONS] COMMAND [ARGS]...

  Command line interface entry point.

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  convert  Convert input to a regex pattern.
  batch    Batch convert file contents to patterns.
```

#### Examples

Convert:

```
> printf "foo\nfoobar\nfoobaz\nbar\nbat" > words.txt
> triex convert -i words.txt
ba[rt]|foo(?:ba[rz])?
> printf "foo\nfoobar\nfoobaz\nbar\nbat" | triex convert
ba[rt]|foo(?:ba[rz])?
```

Batch:
```
> printf "foo\nbar" > words1.txt
> printf "foo\nbaz" > words2.txt
> triex batch *.txt
Converting words1.txt
Converting words2.txt
```
