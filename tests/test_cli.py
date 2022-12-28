# pylint: disable=c0114,c0116

import pathlib

from click.testing import CliRunner
import pytest

from triex.cli import cli


@pytest.fixture
def files(tmp_path: pathlib.Path) -> dict[str, pathlib.Path]:
    return {"in": tmp_path / "in.txt", "out": tmp_path / "out.txt"}


@pytest.mark.parametrize(
    ["args", "content", "output", "error_message"],
    [
        ([], "", "", "No input"),
        ([], "foo\nbar\n", "bar|foo\n", ""),
        (["-b"], "foo\nbar\n", "\\b(?:bar|foo)\\b\n", ""),
        (["-b", "-c"], "foo\nbar\n", "\\b(bar|foo)\\b\n", ""),
        (["-b", "-n"], "foo\nbar\n", "\\b(?:bar|foo)\\b\n", ""),
        (["-c"], "foo\nbar\n", "(bar|foo)\n", ""),
        (["-d", "::"], "foo::bar\n", "bar|foo\n", ""),
        (["-n"], "foo\nbar\n", "(?:bar|foo)\n", ""),
    ],
)
def test_convert(
    files: dict[str, pathlib.Path],  # pylint: disable=w0621
    args: list[str],
    content: str,
    output: str,
    error_message: str,
):
    convert_args = ["convert", "-i", str(files["in"]), "-o", str(files["out"])]
    convert_args.extend(args)

    files["in"].write_text(content)

    runner = CliRunner()
    result = runner.invoke(cli, convert_args)

    if error_message:
        assert result.exit_code > 0
        assert error_message in result.output
    else:
        assert result.exit_code == 0
        assert files["out"].read_text() == output


@pytest.fixture
def batch_files(tmp_path: pathlib.Path) -> dict[str, list[pathlib.Path]]:
    return {
        "in": [tmp_path / "foo.txt", tmp_path / "bar.txt"],
        "out": [tmp_path / "foo.triex.txt", tmp_path / "bar.triex.txt"],
    }


@pytest.mark.parametrize(
    ["args", "content", "output", "warning_message"],
    [
        ([], ["", ""], ["", ""], ""),
        ([], ["foo\nbar\n", "foo\nbar\n"], ["bar|foo\n", "bar|foo\n"], ""),
        (["-b"], ["foo\nbar\n", "foo\nbar\n"], ["\\b(?:bar|foo)\\b\n", "\\b(?:bar|foo)\\b\n"], ""),
        (["-b", "-c"], ["foo\nbar\n", "foo\nbar\n"], ["\\b(bar|foo)\\b\n", "\\b(bar|foo)\\b\n"], ""),
        (["-b", "-n"], ["foo\nbar\n", "foo\nbar\n"], ["\\b(?:bar|foo)\\b\n", "\\b(?:bar|foo)\\b\n"], ""),
        (["-c"], ["foo\nbar\n", "foo\nbar\n"], ["(bar|foo)\n", "(bar|foo)\n"], ""),
        (["-d", "::"], ["foo::bar\n", "foo::bar\n"], ["bar|foo\n", "bar|foo\n"], ""),
        (["-n"], ["foo\nbar\n", "foo\nbar\n"], ["(?:bar|foo)\n", "(?:bar|foo)\n"], ""),
    ],
)
def test_batch(
    batch_files: dict[str, list[pathlib.Path]],  # pylint: disable=w0621
    args: list[str],
    content: list[str],
    output: list[str],
    warning_message: str,
):
    batch_args = ["batch"]
    batch_args.extend(args)

    for idx, file in enumerate(batch_files["in"]):
        file.write_text(content[idx])
        batch_args.append(str(file))

    runner = CliRunner()
    result = runner.invoke(cli, batch_args)

    assert result.exit_code == 0
    if warning_message:
        assert warning_message in result.output

    for idx, file in enumerate(batch_files["out"]):
        if not output[idx]:
            assert not file.exists()
        else:
            assert file.read_text() == output[idx]
