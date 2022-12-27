import logging
import pathlib
from sys import stdin, stdout
from typing import IO

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
                'Enclose pattern in boundary tokens ("\\b"). A non-capturing group is added when neither -c or -n is passed.'
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
    """Command line interface entry point."""
    logger.debug("%s started" % __package__)


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
def convert(
    in_: IO,
    out: IO,
    boundary: bool,
    delimiter: str,
    capture: bool | None,
    debug: bool,  # pyright: ignore reportUnusedVariable
) -> str | None:  # pylint: disable=r0913
    """Convert input to a regex pattern."""

    logger.debug("Preparing input data")
    if not in_.isatty():
        raw_data = in_.read().rstrip()
    else:
        raw_data = None

    if not raw_data:
        raise click.ClickException("No input provided")

    data = raw_data.split(delimiter) if delimiter else raw_data.splitlines()

    logger.debug("Generating trie")
    trie = Trie(data)  # type: ignore

    logger.debug("Trie created with %s value(s) and %s invalid value(s)" % (len(trie.members), len(trie.invalid)))

    if trie.invalid:
        logger.warning("%s invalid values skipped (%s)" % (len(trie.invalid), ",".join(trie.invalid)))

    logger.debug("Generating regex")
    regex = trie.to_regex(boundary, capture)

    logger.debug("Writing regex to %s" % out.name)
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
def batch(
    suffix: str,
    boundary: bool,
    delimiter: str,
    capture: bool | None,
    debug: bool,  # pyright: ignore reportUnusedVariable
    files: tuple[pathlib.Path],
) -> str | None:  # pylint: disable=r0913
    """Batch convert file contents to patterns.

    Patterns will be written to a separate files with the --prefix value inserted before the extension:

    source.txt > source.<suffix>.txt
    """

    logger.debug("Converting %s files" % len(files))

    for file in files:
        logger.info("Converting %s" % file.name)

        raw_data = file.read_text().rstrip()

        if not raw_data:
            logger.warning("File is empty")
            continue

        data = raw_data.split(delimiter) if delimiter else raw_data.splitlines()

        logger.debug("Generating trie")
        trie = Trie(data)  # type: ignore

        logger.debug("Trie created with %s value(s) and %s invalid value(s)" % (len(trie.members), len(trie.invalid)))

        if trie.invalid:
            logger.warning("%s invalid values skipped (%s)" % (len(trie.invalid), ",".join(trie.invalid)))

        logger.debug("Generating regex")
        regex = trie.to_regex(boundary, capture)

        out = file.with_name(f"{file.stem}.{suffix}{file.suffix}")

        logger.debug("Writing regex to %s" % out.name)
        out.write_text(f"{regex}\n")
