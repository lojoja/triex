"""
triex

The command-line interface for triex
"""

import logging
import pathlib
import sys
import typing as t

import click
from clickext import ClickextCommand, ClickextGroup, init_logging, verbose_option

from .triex import Trie


__all__ = ["cli"]


logger = logging.getLogger(__package__)
init_logging(logger)


@click.group(cls=ClickextGroup, global_opts=["verbose"], shared_params=["boundary", "capture", "delimiter"])
@click.version_option()
@click.option(
    "--boundary",
    "-b",
    is_flag=True,
    flag_value=True,
    default=False,
    help=(
        'Enclose pattern in boundary tokens ("\\b").'
        " The pattern is placed in a non-capturing group if neither --capture or --non-capture is passed."
    ),
)
@click.option(
    "--capture/--non-capture",
    "-c/-n",
    flag_value=True,
    default=None,
    help="Enclose pattern in a capturing/non-capturing group.",
)
@click.option(
    "--delimiter",
    "-d",
    default=None,
    help='The character(s) that separate values in the input. [default: "\\n"]',
    type=click.STRING,
)
@verbose_option(logger)
def cli() -> None:
    """A tool to generate semi-minimized regular expression alternations."""
    logger.debug("%s started", __package__)


@cli.command(cls=ClickextCommand)
@click.option("--in", "-i", "in_", default=sys.stdin, help="The input file. [default: stdin]", type=click.File())
@click.option("--out", "-o", default=sys.stdout, help="The output file. [default: stdout]", type=click.File(mode="w"))
def convert(in_: t.IO, out: t.IO, boundary: bool, capture: t.Optional[bool], delimiter: str) -> None:
    """Convert input to a regex pattern."""

    logger.debug("Preparing input data")

    raw_data: t.Optional[str]

    if not in_.isatty():
        raw_data = in_.read().rstrip()
    else:
        raw_data = None

    if not raw_data:
        raise click.ClickException("No input provided")

    data = raw_data.split(delimiter) if delimiter else raw_data.splitlines()

    logger.debug("Generating trie")
    trie = Trie(data)
    logger.debug("Trie created with %s value(s)", len(trie.members))

    logger.debug("Generating regex")
    regex = trie.to_regex(boundary, capture)

    logger.debug("Writing regex to %s", out.name)
    click.echo(regex, file=out, color=False)


@cli.command(cls=ClickextCommand)
@click.option(
    "--suffix",
    "-s",
    default="triex",
    show_default=True,
    help="The suffix to add to the output file names.",
    type=click.STRING,
)
@click.argument("files", nargs=-1, type=click.Path(exists=True, dir_okay=False, path_type=pathlib.Path))
def batch(suffix: str, files: tuple[pathlib.Path], capture: t.Optional[bool], boundary: bool, delimiter: str) -> None:
    """Batch convert file contents to patterns.

    Patterns will be written to a separate files with the --suffix value inserted before the extension:

    source.txt > source.<suffix>.txt
    """

    logger.debug("Converting %s files", len(files))

    for file in files:
        logger.info("Converting %s", file.name)

        raw_data = file.read_text(encoding="utf8").rstrip()

        if not raw_data:
            logger.warning("File is empty")
            continue

        data = raw_data.split(delimiter) if delimiter else raw_data.splitlines()

        logger.debug("Generating trie")
        trie = Trie(data)
        logger.debug("Trie created with %s value(s)", len(trie.members))

        logger.debug("Generating regex")
        regex = trie.to_regex(boundary, capture)

        out = file.with_name(f"{file.stem}.{suffix}{file.suffix}")

        logger.debug("Writing regex to %s", out.name)
        out.write_text(f"{regex}\n", encoding="utf8")
