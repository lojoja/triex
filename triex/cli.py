from codecs import open
import logging
import platform

import click

from .triex import Trie

__all__ = ['cli']


PROGRAM_NAME = 'triex'
MIN_MACOS_VERSION = 10.11
LOG_VERBOSITY_MAP = {True: logging.DEBUG, False: logging.WARNING}


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class ClickFormatter(logging.Formatter):
    colors = {
        'critical': 'red',
        'debug': 'blue',
        'error': 'red',
        'exception': 'red',
        'warning': 'yellow',
    }

    def format(self, record):
        if not record.exc_info:
            level = record.levelname.lower()
            msg = record.msg
            if level in self.colors:
                prefix = click.style(
                    '{0}: '.format(level.title()), fg=self.colors[level]
                )
                if not isinstance(msg, (str, bytes)):
                    msg = str(msg)
                msg = '\n'.join(prefix + l for l in msg.splitlines())
            return msg
        return logging.Formatter.format(self, record)


class ClickHandler(logging.Handler):
    error_levels = ['critical', 'error', 'exception', 'warning']

    def emit(self, record):
        try:
            msg = self.format(record)
            err = record.levelname.lower() in self.error_levels
            click.echo(msg, err=err)
        except Exception:
            self.handleError(record)


click_handler = ClickHandler()
click_formatter = ClickFormatter()
click_handler.setFormatter(click_formatter)
logger.addHandler(click_handler)


class Context(object):
    def __init__(self, boundary, group, capturing, verbose, file):
        logger.debug('Gathering system and environment details')

        self.verbose = verbose
        self.boundary = boundary
        self.group = group
        self.capturing = capturing
        self.file = file
        self.data = None
        self.macos_version = self._get_mac_version()

    def load(self):
        """ Load source data. """
        try:
            with open(self.file, mode='rb', encoding='utf-8') as f:
                self.data = f.read().splitlines()
        except ValueError:
            raise click.ClickException('Failed to read source data file')

    def _get_mac_version(self):
        version = platform.mac_ver()[0]
        version = float('.'.join(version.split('.')[:2]))  # format as e.g., '10.10'
        return version


@click.command()
@click.option(
    '--boundary/--no-boundary',
    is_flag=True,
    default=False,
    help='Whether to surround regex with boundary token (\\b)',
)
@click.option(
    '--group/--no-group',
    is_flag=True,
    default=False,
    help='Whether to surround regex with parenthesis.',
)
@click.option(
    '--capturing/--non-capturing',
    is_flag=True,
    default=False,
    help=(
        'Whether outer parenthesis should be capturing or not. '
        'Forces surrounding parenthesis when --capturing is set even if --no-group is specified.'
    ),
)
@click.option(
    '--verbose/--quiet',
    '-v/-q',
    is_flag=True,
    default=None,
    help='Specify verbosity level.',
)
@click.version_option()
@click.argument('file', nargs=1, required=True, type=click.Path(exists=True))
@click.pass_context
def cli(ctx, boundary, group, capturing, verbose, file):
    logger.setLevel(LOG_VERBOSITY_MAP.get(verbose, logging.INFO))
    logger.debug('{0} started'.format(PROGRAM_NAME))

    ctx.obj = Context(boundary, group, capturing, verbose, file)

    logger.debug('Checking macOS version')
    if ctx.obj.macos_version < MIN_MACOS_VERSION:
        raise click.ClickException(
            '{0} requires macOS {1} or higher'.format(PROGRAM_NAME, MIN_MACOS_VERSION)
        )

    logger.info('Loading data')
    ctx.obj.load()

    logger.info('Generating trie')
    trie = Trie(ctx.obj.data)

    logger.info('Generating regular expression')
    regex = trie.to_regex(ctx.obj.boundary, ctx.obj.group, ctx.obj.capturing)

    print(regex)


def show_exception(self, file=None):
    logger.error(self.message)


click.ClickException.show = show_exception
click.UsageError.show = show_exception
