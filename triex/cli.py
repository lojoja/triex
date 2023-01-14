"""
triex

The command-line interface for triex
"""

import logging
import pathlib
from sys import stdin, stdout
import typing as t

import click
from clickext import DebugCommonOptionGroup

from .triex import Trie


__all__ = ["cli"]


logger = logging.getLogger(__name__)


@click.group(
    cls=DebugCommonOptionGroup,
    common_options=[
        click.Option(
            ["--boundary", "-b"],
            is_flag=True,
            flag_value=True,
            default=False,
            help=(
                'Enclose pattern in boundary tokens ("\\b"). '
                "A non-capturing group is added when neither -c or -n is passed."
            ),
        ),
        click.Option(
            ["--capture/--non-capture", "-c/-n"],
            flag_value=True,
            default=None,
            help=("Enclose pattern in a capturing/non-capturing group."),
        ),
        click.Option(
            ["--delimiter", "-d"],
            default=None,
            help='The character(s) that separate values in the input. [default: "\\n"]',
            type=str,
        ),
    ],
)
@click.version_option()
def cli() -> None:
    """A tool to generate semi-minimized regular expression alternations."""
    logger.debug("%s started", __package__)


@cli.command
@click.option(
    "--in",
    "-i",
    "in_",
    default=stdin,
    help="The input file. [default: stdin]",
    type=click.File(),
)
@click.option(
    "--out",
    "-o",
    default=stdout,
    help="The output file. [default: stdout]",
    type=click.File(mode="w"),
)
def convert(  # pylint: disable=r0913
    in_: t.IO,
    out: t.IO,
    boundary: bool,
    delimiter: str,
    capture: t.Optional[bool],
    debug: bool,  # pyright: ignore reportUnusedVariable pylint: disable=w0613
) -> None:
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


@cli.command
@click.option(
    "--suffix",
    "-s",
    default="triex",
    show_default=True,
    help="The suffix to add to the output file names.",
    type=str,
)
@click.argument(
    "files",
    nargs=-1,
    type=click.Path(exists=True, dir_okay=False, path_type=pathlib.Path),
)
def batch(  # pylint: disable=r0913
    suffix: str,
    boundary: bool,
    delimiter: str,
    capture: t.Optional[bool],
    debug: bool,  # pyright: ignore reportUnusedVariable pylint: disable=w0613
    files: tuple[pathlib.Path],
) -> None:
    """Batch convert file contents to patterns.

    Patterns will be written to a separate files with the --prefix value inserted before the extension:

    source.txt > source.<suffix>.txt
    """

    logger.debug("Converting %s files", len(files))

    for file in files:
        logger.info("Converting %s", file.name)

        raw_data = file.read_text().rstrip()

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
        out.write_text(f"{regex}\n")
