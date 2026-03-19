"""
Implementation module for extracting docstrings and function signatures from Python packages.

This module provides the core functionality for introspecting Python packages
and extracting documentation and signature information. It uses the inspect
module to walk through package modules and extract relevant metadata.
"""

from pathlib import Path


def extract_docstrings(
    package: str, output: Path, modules: bool, classes: bool, functions: bool
) -> int:
    """
    Extract docstrings from a Python package and save them to a JSON file.

    Args:
        package (str): The name of the package to extract docstrings from.
        output (Path): The path to the output JSON file.
        modules (bool): Whether to extract docstrings from modules.
        classes (bool): Whether to extract docstrings from classes.
        functions (bool): Whether to extract docstrings from functions.
    """
    import inspect
    import json
    import pkgutil
    import sys

    # Import the package
    __import__(package)
    pkg = sys.modules[package]

    docstrings = {}

    # Extract docstring from the main package if modules is True
    if modules:
        docstrings[package] = inspect.getdoc(pkg)

    # Walk through the package and extract docstrings
    for importer, modname, ispkg in pkgutil.walk_packages(
        pkg.__path__, pkg.__name__ + "."
    ):
        try:
            module = __import__(modname, fromlist=["*"])
        except ImportError:
            continue

        if modules:
            docstrings[modname] = inspect.getdoc(module)

        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and classes:
                # Check if class is defined in this module, not imported
                if obj.__module__ == modname:
                    docstrings[f"{modname}.{name}"] = inspect.getdoc(obj)
            elif inspect.isfunction(obj) and functions:
                # Check if function is defined in this module, not imported
                if obj.__module__ == modname:
                    docstrings[f"{modname}.{name}"] = inspect.getdoc(obj)

    # Save the extracted docstrings to a JSON file
    with output.open("w") as f:
        json.dump(docstrings, f, indent=4)

    return len([k for k, v in docstrings.items() if v is None])


def extract_args(package: str, output: Path, classes: bool, functions: bool) -> None:
    """
    Extract function and method signatures from a Python package and save them to a JSON file.

    Args:
        package (str): The name of the package to extract signatures from.
        output (Path): The path to the output JSON file.
        classes (bool): Whether to extract class method signatures.
        functions (bool): Whether to extract function signatures.
    """
    import inspect
    import json
    import pkgutil
    import sys

    # Import the package
    __import__(package)
    pkg = sys.modules[package]

    args_info = {}

    def get_function_info(func, full_name):
        """Extract function/method signature information."""
        info = {
            "arguments": [],
            "return_type": None,
        }

        try:
            sig = inspect.signature(func)

            # Extract argument information
            for param_name, param in sig.parameters.items():
                if param_name == "self" or param_name == "cls":
                    continue

                arg_info = {"name": param_name}

                # Add type annotation if available
                if param.annotation != inspect.Parameter.empty:
                    arg_info["type"] = str(param.annotation)

                # Add default value if available
                if param.default != inspect.Parameter.empty:
                    arg_info["default"] = str(param.default)

                info["arguments"].append(arg_info)

            # Extract return type if available
            if sig.return_annotation != inspect.Signature.empty:
                info["return_type"] = str(sig.return_annotation)

        except (ValueError, TypeError):
            # Some built-in objects don't have inspectable signatures
            pass

        return info

    # Walk through the package and extract signatures
    for importer, modname, ispkg in pkgutil.walk_packages(
        pkg.__path__, pkg.__name__ + "."
    ):
        try:
            module = __import__(modname, fromlist=["*"])
        except ImportError:
            continue

        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and classes:
                # Check if class is defined in this module, not imported
                if obj.__module__ == modname:
                    class_full_name = f"{modname}.{name}"
                    args_info[class_full_name] = {
                        "type": "class",
                        "methods": {},
                    }

                    # Extract class methods
                    for method_name, method in inspect.getmembers(
                        obj, predicate=inspect.isfunction
                    ):
                        if not method_name.startswith("_"):
                            args_info[class_full_name]["methods"][method_name] = (
                                get_function_info(
                                    method, f"{class_full_name}.{method_name}"
                                )
                            )

            elif inspect.isfunction(obj) and functions:
                # Check if function is defined in this module, not imported
                if obj.__module__ == modname:
                    func_full_name = f"{modname}.{name}"
                    args_info[func_full_name] = {
                        "type": "function",
                        **get_function_info(obj, func_full_name),
                    }

    # Save the extracted signatures to a JSON file
    with output.open("w") as f:
        json.dump(args_info, f, indent=4)

    return
