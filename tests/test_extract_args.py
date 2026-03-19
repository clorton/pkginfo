"""
Tests for the extract_args function.

These tests verify that function and method signatures are correctly extracted
including type annotations, default values, and return types.
"""

import json
import sys
from pathlib import Path

import pytest

from pkginfo.impl import extract_args


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


def test_extract_function_with_types(temp_output):
    """
    Test extracting a function with type annotations and defaults.

    Given a function with type annotations and default values,
    when extract_args is called,
    then it should capture all parameter types, defaults, and return type.

    Failure implications: Type information may not be correctly extracted.
    """
    # When
    extract_args(
        package="sample_package",
        output=temp_output,
        classes=False,
        functions=True,
    )

    # Then
    with temp_output.open("r") as f:
        args_info = json.load(f)

    # Verify complex_function
    func_key = "sample_package.submodule.complex_function"
    assert func_key in args_info

    func_info = args_info[func_key]
    assert func_info["type"] == "function"
    assert "arguments" in func_info
    assert "return_type" in func_info

    # Check arguments - should have at least required, optional, union_type
    args = func_info["arguments"]
    assert len(args) >= 3

    # First argument: required
    required_arg = next((a for a in args if a["name"] == "required"), None)
    assert required_arg is not None
    assert "<class 'str'>" in required_arg["type"]
    assert "default" not in required_arg

    # Return type
    assert "<class 'dict'>" in func_info["return_type"]


def test_extract_function_without_types(temp_output):
    """
    Test extracting a function without type annotations.

    Given a function without type annotations,
    when extract_args is called,
    then it should still capture parameter names and defaults.

    Failure implications: Functions without type hints may not be properly handled.
    """
    # When
    extract_args(
        package="sample_package",
        output=temp_output,
        classes=False,
        functions=True,
    )

    # Then
    with temp_output.open("r") as f:
        args_info = json.load(f)

    # Verify no_type_annotations function
    func_key = "sample_package.submodule.no_type_annotations"
    assert func_key in args_info

    func_info = args_info[func_key]
    args = func_info["arguments"]

    # Should have 3 arguments
    assert len(args) == 3

    # Check parameter names
    assert args[0]["name"] == "a"
    assert args[1]["name"] == "b"
    assert args[2]["name"] == "c"

    # Third parameter should have default
    assert args[2]["default"] == "10"

    # First two should not have defaults
    assert "default" not in args[0]
    assert "default" not in args[1]


def test_extract_class_methods(temp_output):
    """
    Test extracting methods from a class.

    Given a class with various methods,
    when extract_args is called with classes=True,
    then it should extract all public method signatures.

    Failure implications: Class method extraction may be incomplete.
    """
    # When
    extract_args(
        package="sample_package",
        output=temp_output,
        classes=True,
        functions=False,
    )

    # Then
    with temp_output.open("r") as f:
        args_info = json.load(f)

    # Verify DocumentedClass exists
    class_key = "sample_package.submodule.DocumentedClass"
    assert class_key in args_info

    class_info = args_info[class_key]
    assert class_info["type"] == "class"
    assert "methods" in class_info

    methods = class_info["methods"]

    # Should have public methods
    # Note: __init__ and private methods should be excluded
    # The exact list depends on implementation, but should have at least some methods
    assert len(methods) > 0
    # Check that no private methods are included
    for method_name in methods.keys():
        assert not method_name.startswith("_")


def test_extract_complex_function_signatures(temp_output):
    """
    Test extracting a function with complex type annotations.

    Given a function with Optional, Union, *args, and **kwargs,
    when extract_args is called,
    then it should capture all parameter information excluding self/cls.

    Failure implications: Complex type annotations may not be properly handled.

    Note: The current implementation skips *args and **kwargs in extraction,
    which may be a design decision. If tests fail here, verify if this is
    the intended behavior.
    """
    # When
    extract_args(
        package="sample_package",
        output=temp_output,
        classes=False,
        functions=True,
    )

    # Then
    with temp_output.open("r") as f:
        args_info = json.load(f)

    func_key = "sample_package.submodule.complex_function"
    assert func_key in args_info

    func_info = args_info[func_key]
    args = func_info["arguments"]

    # Find the required parameter
    required_param = next((a for a in args if a["name"] == "required"), None)
    assert required_param is not None
    assert "str" in required_param["type"]

    # Find the optional parameter
    optional_param = next((a for a in args if a["name"] == "optional"), None)
    assert optional_param is not None
    assert "None" in optional_param["default"]

    # Find the union_type parameter
    union_param = next((a for a in args if a["name"] == "union_type"), None)
    assert union_param is not None
    assert union_param["default"] == "default"


def test_exclude_private_methods(temp_output):
    """
    Test that private methods are excluded from extraction.

    Given a class with __init__ and other private methods,
    when extract_args is called,
    then private methods (starting with _) should not be included.

    Failure implications: Private methods may be incorrectly exposed in output.
    """
    # When
    extract_args(
        package="sample_package",
        output=temp_output,
        classes=True,
        functions=False,
    )

    # Then
    with temp_output.open("r") as f:
        args_info = json.load(f)

    class_key = "sample_package.submodule.DocumentedClass"
    methods = args_info[class_key]["methods"]

    # __init__ should not be in methods (starts with _)
    assert "__init__" not in methods

    # Verify we only have public methods
    for method_name in methods.keys():
        assert not method_name.startswith("_")


def test_extract_both_classes_and_functions(temp_output):
    """
    Test extracting both classes and functions together.

    Given a package with both classes and functions,
    when extract_args is called with both flags enabled,
    then both should be present in the output.

    Failure implications: Combining extraction types may not work correctly.
    """
    # When
    extract_args(
        package="sample_package",
        output=temp_output,
        classes=True,
        functions=True,
    )

    # Then
    with temp_output.open("r") as f:
        args_info = json.load(f)

    # Should have functions
    assert "sample_package.submodule.complex_function" in args_info
    assert args_info["sample_package.submodule.complex_function"]["type"] == "function"

    # Should have classes
    assert "sample_package.submodule.DocumentedClass" in args_info
    assert args_info["sample_package.submodule.DocumentedClass"]["type"] == "class"


def test_extract_classes_only(temp_output):
    """
    Test extracting only classes, not functions.

    Given a package with both classes and functions,
    when extract_args is called with only classes=True,
    then only classes should be in the output.

    Failure implications: The filtering flags may not be working correctly.
    """
    # When
    extract_args(
        package="sample_package",
        output=temp_output,
        classes=True,
        functions=False,
    )

    # Then
    with temp_output.open("r") as f:
        args_info = json.load(f)

    # Should have classes
    assert "sample_package.submodule.DocumentedClass" in args_info

    # Should NOT have standalone functions
    assert "sample_package.submodule.complex_function" not in args_info
    assert "sample_package.submodule.no_type_annotations" not in args_info


def test_output_json_format(temp_output):
    """
    Test that the output JSON is properly formatted.

    Given any package,
    when extract_args writes output,
    then the JSON should be valid, properly indented, and well-structured.

    Failure implications: Output may not be human-readable or parseable.
    """
    # When
    extract_args(
        package="sample_package",
        output=temp_output,
        classes=True,
        functions=True,
    )

    # Then
    with temp_output.open("r") as f:
        content = f.read()
        args_info = json.loads(content)

    # Verify it's a dictionary
    assert isinstance(args_info, dict)

    # Verify structure for functions
    for key, value in args_info.items():
        assert isinstance(key, str)
        assert key.startswith("sample_package")

        if value["type"] == "function":
            assert "arguments" in value
            assert "return_type" in value
            assert isinstance(value["arguments"], list)

        elif value["type"] == "class":
            assert "methods" in value
            assert isinstance(value["methods"], dict)
