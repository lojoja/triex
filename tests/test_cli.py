# pylint: disable=missing-function-docstring,missing-module-docstring,too-many-arguments,too-many-locals

from io import BytesIO
from pathlib import Path
import typing as t

from click.testing import CliRunner
import pytest

from triex.cli import cli


def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(cli, "--version")
    assert result.output.startswith("cli, version")


@pytest.mark.parametrize("short_opts", [True, False])
@pytest.mark.parametrize("verbose", [True, False])
def test_cli_verbosity(caplog: pytest.LogCaptureFixture, verbose: bool, short_opts: bool):
    runner = CliRunner()
    runner.invoke(cli, ["convert", ("-v" if short_opts else "--verbose") if verbose else ""], "foo")
    assert ("DEBUG" in caplog.text) is verbose


@pytest.mark.parametrize("short_opts", [True, False])
@pytest.mark.parametrize("stdout", [True, False])
@pytest.mark.parametrize("stdin", [True, False])
@pytest.mark.parametrize("delimiter", [None, "::"])
@pytest.mark.parametrize("capturing", [True, False, None])
@pytest.mark.parametrize("boundary", [True, False])
def test_convert(
    tmp_path: Path,
    build_pattern: t.Callable[[bool, t.Optional[bool]], str],
    raw_values: list[str],
    boundary: bool,
    capturing: t.Optional[bool],
    delimiter: t.Optional[str],
    stdin: bool,
    stdout: bool,
    short_opts: bool,
):
    input_file = None
    output_file = None

    args = ["convert"]

    if boundary:
        args.append("-b" if short_opts else "--boundary")

    if capturing is not None:
        args.append(("-c" if short_opts else "--capture") if capturing else ("-n" if short_opts else "--non-capture"))

    if delimiter is not None:
        input_data = delimiter.join(raw_values)
        args.extend(["-d" if short_opts else "--delimiter", delimiter])
    else:
        input_data = "\n".join(raw_values)

    if not stdin:
        input_file = tmp_path / "in.txt"
        input_file.write_text(input_data, encoding="utf8")
        args.extend(["-i" if short_opts else "--in", str(input_file)])

    if not stdout:
        output_file = tmp_path / "sub/out.txt"  # Use subdirectory to test if parents are created
        args.extend(["-o" if short_opts else "--out", str(output_file)])

    runner = CliRunner()
    result = runner.invoke(cli, args, input_data if stdin else None)

    assert result.exit_code == 0

    if output_file:
        assert output_file.exists()
        pattern = output_file.read_text(encoding="utf8")
    else:
        pattern = result.output

    assert pattern == f"{build_pattern(boundary, capturing)}\n"


@pytest.mark.parametrize("isatty", [True, False])
def test_convert_detects_tty(monkeypatch: pytest.MonkeyPatch, isatty: bool):
    text = "foo\nbar"
    stream = BytesIO(text.encode())
    monkeypatch.setattr(stream, "isatty", lambda: isatty)

    runner = CliRunner()
    result = runner.invoke(cli, "convert", stream)

    assert result.output == "Error: No input provided\n" if isatty else "bar|foo\n"


@pytest.mark.parametrize("short_opts", [True, False])
@pytest.mark.parametrize("suffix", [None, "foo"])
@pytest.mark.parametrize("delimiter", [None, "::"])
@pytest.mark.parametrize("capturing", [True, False, None])
@pytest.mark.parametrize("boundary", [True, False])
def test_batch(
    tmp_path: Path,
    build_pattern: t.Callable[[bool, t.Optional[bool]], str],
    raw_values: list[str],
    boundary: bool,
    capturing: t.Optional[bool],
    delimiter: t.Optional[str],
    suffix: t.Optional[str],
    short_opts: bool,
):
    input_files = []
    output_files = []

    args = ["batch"]

    if boundary:
        args.append("-b" if short_opts else "--boundary")

    if capturing is not None:
        args.append(("-c" if short_opts else "--capture") if capturing else ("-n" if short_opts else "--non-capture"))

    if delimiter is not None:
        input_data = delimiter.join(raw_values)
        args.extend(["-d" if short_opts else "--delimiter", delimiter])
    else:
        input_data = "\n".join(raw_values)

    if suffix is not None:
        args.extend(["-s" if short_opts else "--suffix", suffix])

    for i in range(0, 2):
        input_file = tmp_path / f"{i}.txt"
        input_file.write_text(input_data, encoding="utf8")
        input_files.append(input_file)
        args.append(str(input_file))

        output_file = tmp_path / f"{input_file.stem}.{suffix if suffix else 'triex'}{input_file.suffix}"
        output_files.append(output_file)

    runner = CliRunner()
    result = runner.invoke(cli, args)

    assert result.exit_code == 0

    for file in output_files:
        assert file.exists()
        assert file.read_text(encoding="utf8") == f"{build_pattern(boundary, capturing)}\n"


def test_batch_with_empty_file(tmp_path: Path):
    input_file = tmp_path / "in.txt"
    input_file.touch()

    runner = CliRunner()
    result = runner.invoke(cli, ["batch", str(input_file)])

    assert result.exit_code == 0
    assert result.output == f"Converting {input_file.name}\nWarning: File is empty\n"
