"""
Tests for the arginfo CLI command.

These tests verify the command-line interface for extracting function and method
signatures, including argument parsing and default values.
"""

import json
import sys
from pathlib import Path

import pytest
from click.testing import CliRunner

from pkginfo.args import cli


@pytest.fixture
def runner():
    """
    Provide a Click CLI test runner.

    Returns:
        CliRunner: A Click test runner instance.
    """
    return CliRunner()


@pytest.fixture
def fixture_package_path():
    """
    Provide the path to the fixture package.

    Returns:
        Path: Path to the tests/fixtures directory.
    """
    return Path(__file__).parent / "fixtures"


@pytest.fixture(autouse=True)
def setup_fixture_package(fixture_package_path):
    """
    Ensure the fixture package is in sys.path for import.

    Args:
        fixture_package_path: Path to the fixtures directory.
    """
    sys.path.insert(0, str(fixture_package_path))
    yield
    sys.path.remove(str(fixture_package_path))


def test_cli_with_default_output(runner):
    """
    Test CLI with default output location.

    Given the arginfo command with only a package name,
    when the command is executed,
    then it should create an output file named <package>.args.json in the current directory.

    Failure implications: Default output path generation may be incorrect.
    """
    with runner.isolated_filesystem():
        # When
        result = runner.invoke(cli, ["sample_package"])

        # Then
        assert Path("sample_package.args.json").exists()

        # Verify output shows correct config
        assert "sample_package" in result.output
        assert "sample_package.args.json" in result.output


def test_cli_with_custom_output(runner):
    """
    Test CLI with custom output path.

    Given the arginfo command with --output flag,
    when the command is executed,
    then it should create the output file at the specified path.

    Failure implications: Custom output path may not be respected.
    """
    with runner.isolated_filesystem():
        custom_path = Path("custom/location/output.json")
        custom_path.parent.mkdir(parents=True, exist_ok=True)

        # When
        result = runner.invoke(cli, ["sample_package", "--output", str(custom_path)])

        # Then
        assert custom_path.exists()
        assert str(custom_path) in result.output


def test_cli_exit_code(runner):
    """
    Test that CLI returns exit code 0 on success.

    Given a valid package,
    when the arginfo command is executed,
    then the exit code should be 0.

    Failure implications: The CLI may not be indicating success correctly.
    """
    with runner.isolated_filesystem():
        # When
        result = runner.invoke(cli, ["sample_package"])

        # Then
        assert result.exit_code == 0


def test_cli_no_classes_flag(runner):
    """
    Test CLI with --no-classes flag.

    Given the arginfo command with --no-classes,
    when the command is executed,
    then class information should not be extracted.

    Failure implications: Command-line flags may not be properly passed to the function.
    """
    with runner.isolated_filesystem():
        # When
        result = runner.invoke(cli, ["sample_package", "--no-classes"])

        # Then
        with Path("sample_package.args.json").open("r") as f:
            args_info = json.load(f)

        # Should not have class entries
        assert "sample_package.submodule.DocumentedClass" not in args_info
        assert "sample_package.submodule.UndocumentedClass" not in args_info

        # Should still have functions
        assert "sample_package.submodule.complex_function" in args_info


def test_cli_no_functions_flag(runner):
    """
    Test CLI with --no-functions flag.

    Given the arginfo command with --no-functions,
    when the command is executed,
    then function information should not be extracted.

    Failure implications: Command-line flags may not be properly passed to the function.
    """
    with runner.isolated_filesystem():
        # When
        result = runner.invoke(cli, ["sample_package", "--no-functions"])

        # Then
        with Path("sample_package.args.json").open("r") as f:
            args_info = json.load(f)

        # Should not have function entries
        assert "sample_package.top_level_function" not in args_info
        assert "sample_package.submodule.complex_function" not in args_info

        # Should still have classes
        assert "sample_package.submodule.DocumentedClass" in args_info


def test_cli_combined_flags(runner):
    """
    Test CLI with both --no-classes and --no-functions.

    Given the arginfo command with both flags disabled,
    when the command is executed,
    then the output should be empty or minimal.

    Failure implications: Multiple flags may not work together correctly.
    """
    with runner.isolated_filesystem():
        # When
        result = runner.invoke(
            cli, ["sample_package", "--no-classes", "--no-functions"]
        )

        # Then
        with Path("sample_package.args.json").open("r") as f:
            args_info = json.load(f)

        # Should have no entries
        assert len(args_info) == 0


def test_cli_output_format(runner):
    """
    Test that CLI output to stdout shows configuration.

    Given the arginfo command,
    when executed,
    then it should print the configuration dictionary to stdout.

    Failure implications: Users may not see what options are being used.
    """
    with runner.isolated_filesystem():
        # When
        result = runner.invoke(cli, ["sample_package"])

        # Then
        assert "package" in result.output
        assert "output" in result.output
        assert "classes" in result.output
        assert "functions" in result.output


def test_cli_help(runner):
    """
    Test CLI help message.

    Given the arginfo command with --help,
    when executed,
    then it should display help information.

    Failure implications: Users may not be able to discover command usage.
    """
    # When
    result = runner.invoke(cli, ["--help"])

    # Then
    assert result.exit_code == 0
    assert "extracting argument information from python packages" in result.output.lower()
    assert "--output" in result.output
    assert "--classes" in result.output
    assert "--functions" in result.output


def test_cli_extracts_type_information(runner):
    """
    Test that CLI correctly extracts type information.

    Given a package with type-annotated functions,
    when arginfo is executed,
    then the output should contain type information.

    Failure implications: Type extraction in CLI flow may be broken.
    """
    with runner.isolated_filesystem():
        # When
        result = runner.invoke(cli, ["sample_package"])

        # Then
        with Path("sample_package.args.json").open("r") as f:
            args_info = json.load(f)

        # Verify type information exists
        func = args_info["sample_package.submodule.complex_function"]
        assert func["type"] == "function"
        assert len(func["arguments"]) >= 3  # At least required, optional, union_type
        assert "type" in func["arguments"][0]
        assert "str" in func["arguments"][0]["type"]


def test_cli_extracts_class_methods(runner):
    """
    Test that CLI correctly extracts class method information.

    Given a package with classes,
    when arginfo is executed with classes enabled,
    then the output should contain method information.

    Failure implications: Class method extraction in CLI flow may be broken.
    """
    with runner.isolated_filesystem():
        # When
        result = runner.invoke(cli, ["sample_package"])

        # Then
        with Path("sample_package.args.json").open("r") as f:
            args_info = json.load(f)

        # Verify class method information
        class_info = args_info["sample_package.submodule.DocumentedClass"]
        assert class_info["type"] == "class"
        assert "methods" in class_info
        assert "instance_method" in class_info["methods"]
        assert "static_method" in class_info["methods"]


def test_cli_short_output_flag(runner):
    """
    Test CLI with short -o flag for output.

    Given the arginfo command with -o flag,
    when the command is executed,
    then it should work the same as --output.

    Failure implications: Short flag alias may not be working.
    """
    with runner.isolated_filesystem():
        custom_path = Path("test_output.json")

        # When
        result = runner.invoke(cli, ["sample_package", "-o", str(custom_path)])

        # Then
        assert result.exit_code == 0
        assert custom_path.exists()


def test_cli_default_flags_are_true(runner):
    """
    Test that default values for classes and functions are True.

    Given the arginfo command with no flags,
    when executed,
    then both classes and functions should be extracted by default.

    Failure implications: Default behavior may not match documentation.
    """
    with runner.isolated_filesystem():
        # When
        result = runner.invoke(cli, ["sample_package"])

        # Then
        with Path("sample_package.args.json").open("r") as f:
            args_info = json.load(f)

        # Both classes and functions should be present
        has_functions = any(
            v.get("type") == "function" for v in args_info.values()
        )
        has_classes = any(
            v.get("type") == "class" for v in args_info.values()
        )

        assert has_functions, "Functions should be extracted by default"
        assert has_classes, "Classes should be extracted by default"
