"""
Command-line interface for extracting docstrings from Python packages.

This module provides the docstrings CLI tool that extracts documentation strings
from modules, classes, and functions in a Python package. Results are saved to
a JSON file, and the tool returns the count of missing docstrings as its exit code.
"""

from pathlib import Path

import click

from .impl import extract_docstrings

help = """
A tool for extracting docstrings from Python packages.
"""


@click.command(help=help)
@click.argument("package", required=True)
@click.option(
    "--output",
    "-o",
    default=None,
    type=Path,
    help="Output file for the extracted docstrings.",
)
@click.option(
    "--modules/--no-modules",
    default=True,
    help="Extract docstrings from modules.",
)
@click.option(
    "--classes/--no-classes",
    default=True,
    help="Extract docstrings from classes.",
)
@click.option(
    "--functions/--no-functions",
    default=True,
    help="Extract docstrings from functions.",
)
def cli(
    package: str, output: Path, modules: bool, classes: bool, functions: bool
) -> int:

    output = output or (Path.cwd() / f"{package}.docs.json")

    print(
        {
            "package": package,
            "output": str(output),
            "modules": modules,
            "classes": classes,
            "functions": functions,
        }
    )
    num_none = extract_docstrings(package, output, modules, classes, functions)

    return num_none


if __name__ == "__main__":
    import sys

    sys.exit(cli())
