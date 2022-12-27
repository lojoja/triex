from pathlib import Path

from click.testing import CliRunner
import pytest

from triex.cli import cli


@pytest.fixture
def files(tmp_path: Path) -> dict[str, Path]:
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
def test_convert(files, args: list[str], content: str, output: str, error_message: str):
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
