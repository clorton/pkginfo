"""
Tests for the extract_docstrings function.

These tests verify that docstrings are correctly extracted from Python packages
and that the count of missing docstrings is accurate.
"""

import json
import sys
from pathlib import Path

import pytest

from pkginfo.impl import extract_docstrings


@pytest.fixture
def fixture_package_path():
    """
    Provide the path to the fixture package.

    Returns:
        Path: Path to the tests/fixtures directory.
    """
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def temp_output(tmp_path):
    """
    Provide a temporary output file path.

    Args:
        tmp_path: pytest fixture providing a temporary directory.

    Returns:
        Path: Path to a temporary JSON output file.
    """
    return tmp_path / "output.json"


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


def test_extract_all_docstrings(temp_output):
    """
    Test extracting all docstrings (modules, classes, functions).

    Given a package with various documented and undocumented items,
    when extract_docstrings is called with all flags enabled,
    then it should extract all docstrings and return the count of missing ones.

    Failure implications: The tool may not correctly identify or count missing docstrings.
    """
    # When
    missing_count = extract_docstrings(
        package="sample_package",
        output=temp_output,
        modules=True,
        classes=True,
        functions=True,
    )

    # Then
    assert temp_output.exists(), "Output file should be created"

    with temp_output.open("r") as f:
        docstrings = json.load(f)

    # Verify main package docstring exists
    assert "sample_package" in docstrings
    assert docstrings["sample_package"] is not None
    assert "testing pkginfo extraction tools" in docstrings["sample_package"].lower()

    # Verify documented function exists
    assert "sample_package.submodule.complex_function" in docstrings
    assert docstrings["sample_package.submodule.complex_function"] is not None

    # Verify submodule docstring
    assert "sample_package.submodule" in docstrings
    assert docstrings["sample_package.submodule"] is not None

    # Verify documented class
    assert "sample_package.submodule.DocumentedClass" in docstrings
    assert docstrings["sample_package.submodule.DocumentedClass"] is not None

    # Verify undocumented class
    assert "sample_package.submodule.UndocumentedClass" in docstrings
    assert docstrings["sample_package.submodule.UndocumentedClass"] is None

    # Verify missing count is correct (should have at least 2: UndocumentedClass, empty_module)
    assert missing_count >= 2, f"Expected at least 2 missing docstrings, got {missing_count}"


def test_extract_modules_only(temp_output):
    """
    Test extracting only module docstrings.

    Given a package with modules, classes, and functions,
    when extract_docstrings is called with only modules=True,
    then only module-level docstrings should be extracted.

    Failure implications: The filtering flags may not be working correctly.
    """
    # When
    extract_docstrings(
        package="sample_package",
        output=temp_output,
        modules=True,
        classes=False,
        functions=False,
    )

    # Then
    with temp_output.open("r") as f:
        docstrings = json.load(f)

    # Should have module docstrings
    assert "sample_package" in docstrings
    assert "sample_package.submodule" in docstrings

    # Should NOT have class or function docstrings
    assert "sample_package.submodule.complex_function" not in docstrings
    assert "sample_package.submodule.DocumentedClass" not in docstrings


def test_extract_classes_only(temp_output):
    """
    Test extracting only class docstrings.

    Given a package with modules, classes, and functions,
    when extract_docstrings is called with only classes=True,
    then only class docstrings should be extracted.

    Failure implications: The filtering flags may not be working correctly.
    """
    # When
    extract_docstrings(
        package="sample_package",
        output=temp_output,
        modules=False,
        classes=True,
        functions=False,
    )

    # Then
    with temp_output.open("r") as f:
        docstrings = json.load(f)

    # Should have class docstrings
    assert "sample_package.submodule.DocumentedClass" in docstrings
    assert "sample_package.submodule.UndocumentedClass" in docstrings

    # Should NOT have module or function docstrings
    assert "sample_package" not in docstrings
    assert "sample_package.top_level_function" not in docstrings


def test_extract_functions_only(temp_output):
    """
    Test extracting only function docstrings.

    Given a package with modules, classes, and functions,
    when extract_docstrings is called with only functions=True,
    then only function docstrings should be extracted.

    Failure implications: The filtering flags may not be working correctly.
    """
    # When
    extract_docstrings(
        package="sample_package",
        output=temp_output,
        modules=False,
        classes=False,
        functions=True,
    )

    # Then
    with temp_output.open("r") as f:
        docstrings = json.load(f)

    # Should have function docstrings
    assert "sample_package.submodule.complex_function" in docstrings
    assert "sample_package.submodule.no_type_annotations" in docstrings

    # Should NOT have module or class docstrings
    assert "sample_package" not in docstrings
    assert "sample_package.submodule.DocumentedClass" not in docstrings


def test_missing_docstrings_count(temp_output):
    """
    Test that the return value correctly counts missing docstrings.

    Given a package with some missing docstrings,
    when extract_docstrings is called,
    then the return value should equal the number of None values in the output.

    Failure implications: The exit code behavior may be incorrect.
    """
    # When
    missing_count = extract_docstrings(
        package="sample_package",
        output=temp_output,
        modules=True,
        classes=True,
        functions=True,
    )

    # Then
    with temp_output.open("r") as f:
        docstrings = json.load(f)

    # Count None values manually
    expected_missing = sum(1 for v in docstrings.values() if v is None)

    assert missing_count == expected_missing, (
        f"Missing count {missing_count} does not match "
        f"actual None values {expected_missing}"
    )


def test_output_json_format(temp_output):
    """
    Test that the output JSON is properly formatted.

    Given any package,
    when extract_docstrings writes output,
    then the JSON should be valid and properly indented.

    Failure implications: Output may not be human-readable or parseable.
    """
    # When
    extract_docstrings(
        package="sample_package",
        output=temp_output,
        modules=True,
        classes=True,
        functions=True,
    )

    # Then
    with temp_output.open("r") as f:
        content = f.read()
        docstrings = json.loads(content)

    # Verify it's a dictionary
    assert isinstance(docstrings, dict)

    # Verify keys are strings (fully qualified names)
    for key in docstrings.keys():
        assert isinstance(key, str)
        assert key.startswith("sample_package")

    # Verify values are either strings or None
    for value in docstrings.values():
        assert value is None or isinstance(value, str)
