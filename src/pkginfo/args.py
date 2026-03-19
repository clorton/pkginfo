from pathlib import Path

import click

from .impl import extract_args

help = """
A tool for extracting argument information from Python packages.
"""


@click.command(help=help)
@click.argument("package", required=True)
@click.option(
    "--output",
    "-o",
    default=None,
    type=Path,
    help="Output file for the extracted argument information.",
)
@click.option(
    "--classes/--no-classes",
    default=True,
    help="Extract argument information from classes.",
)
@click.option(
    "--functions/--no-functions",
    default=True,
    help="Extract argument information from functions.",
)
def cli(package: str, output: Path, classes: bool, functions: bool) -> int:

    output = output or (Path.cwd() / f"{package}.args.json")

    print(
        {
            "package": package,
            "output": str(output),
            "classes": classes,
            "functions": functions,
        }
    )

    extract_args(package, output, classes, functions)

    return


if __name__ == "__main__":
    cli()
