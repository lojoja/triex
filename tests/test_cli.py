# pylint: disable=missing-function-docstring,missing-module-docstring

import pathlib

from click.testing import CliRunner
import pytest

import triex.cli


@pytest.fixture(name="values")
def fixture_values() -> list[str]:
    return ["foo", "foobar", "foobaz", "bar", "bat\n"]


@pytest.fixture(name="pattern")
def fixture_pattern() -> str:
    return r"ba[rt]|foo(?:ba[rz])?"


@pytest.fixture(name="patterns")
def fixture_patterns(pattern: str) -> dict[str, str]:
    return {
        "default": f"{pattern}\n",
        "boundary": f"\\b(?:{pattern})\\b\n",
        "boundary (capturing)": f"\\b({pattern})\\b\n",
        "boundary (non-capturing)": f"\\b(?:{pattern})\\b\n",
        "capturing": f"({pattern})\n",
        "non-capturing": f"(?:{pattern})\n",
    }


@pytest.fixture(name="files")
def fixture_files(tmp_path: pathlib.Path) -> dict[str, pathlib.Path]:
    return {"in": tmp_path / "in.txt", "out": tmp_path / "out.txt"}


@pytest.mark.parametrize(
    ["args", "delimiter", "pattern_name"],
    [
        ([], "\n", ""),
        ([], "\n", "default"),
        (["-b"], "\n", "boundary"),
        (["-b", "-c"], "\n", "boundary (capturing)"),
        (["-b", "-n"], "\n", "boundary (non-capturing)"),
        (["-c"], "\n", "capturing"),
        (["-d", "::"], "::", "default"),
        (["-n"], "\n", "non-capturing"),
    ],
    ids=[
        "no input",
        "default",
        "boundary",
        "boundary (capturing)",
        "boundary (non-capturing)",
        "capturing",
        "delimiter",
        "non-capturing",
    ],
)
def test_convert_file(
    values: list[str],
    patterns: dict[str, str],
    files: dict[str, pathlib.Path],
    args: list[str],
    delimiter: str,
    pattern_name: str,
):  # pylint: disable=too-many-arguments
    convert_args = ["convert", *args]

    if pattern_name:
        convert_args.extend(["-i", str(files["in"]), "-o", str(files["out"])])
        files["in"].write_text(delimiter.join(values), encoding="utf8")

    runner = CliRunner()
    result = runner.invoke(triex.cli.cli, convert_args)

    if pattern_name:
        assert result.exit_code == 0
        assert files["out"].read_text(encoding="utf8") == patterns[pattern_name]
    else:
        assert result.exit_code > 0
        assert result.output.endswith("No input provided\n")


@pytest.fixture(name="batch_files")
def fixture_batch_files(tmp_path: pathlib.Path) -> dict[str, list[pathlib.Path]]:
    return {
        "in": [tmp_path / "foo.txt", tmp_path / "bar.txt"],
        "out": [tmp_path / "foo.triex.txt", tmp_path / "bar.triex.txt"],
    }


@pytest.mark.parametrize(
    ["args", "delimiter", "pattern_name"],
    [
        ([], "\n", ""),
        ([], "\n", "default"),
        (["-b"], "\n", "boundary"),
        (["-b", "-c"], "\n", "boundary (capturing)"),
        (["-b", "-n"], "\n", "boundary (non-capturing)"),
        (["-c"], "\n", "capturing"),
        (["-d", "::"], "::", "default"),
        (["-n"], "\n", "non-capturing"),
    ],
    ids=[
        "no input",
        "default",
        "boundary",
        "boundary (capturing)",
        "boundary (non-capturing)",
        "capturing",
        "delimiter",
        "non-capturing",
    ],
)
def test_batch(
    batch_files: dict[str, list[pathlib.Path]],
    values: list[str],
    patterns: dict[str, str],
    args: list[str],
    delimiter: str,
    pattern_name: str,
):  # pylint: disable=too-many-arguments
    for file in batch_files["in"]:
        content = delimiter.join(values) if pattern_name else ""
        file.write_text(content, encoding="utf8")

    runner = CliRunner()
    result = runner.invoke(triex.cli.cli, ["batch", *args, *[str(f) for f in batch_files["in"]]])

    assert result.exit_code == 0

    if pattern_name:
        for file in batch_files["out"]:
            assert file.read_text(encoding="utf8") == patterns[pattern_name]
    else:
        assert result.output.endswith("File is empty\n")
