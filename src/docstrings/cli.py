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
    default="docstrings.json",
    help="Output file for the extracted docstrings.",
)
@click.option(
    "-m",
    "--modules",
    is_flag=True,
    flag_value=False,
    default=True,
    help="Do _not_ extract docstrings from modules.",
)
@click.option(
    "-c",
    "--classes",
    is_flag=True,
    flag_value=False,
    default=True,
    help="Do _not_ extract docstrings from classes.",
)
@click.option(
    "-f",
    "--functions",
    is_flag=True,
    flag_value=False,
    default=True,
    help="Do _not_ extract docstrings from functions.",
)
def cli(package, output, modules, classes, functions):

    extract_docstrings(package, output, modules, classes, functions)

    return


if __name__ == "__main__":
    cli()
