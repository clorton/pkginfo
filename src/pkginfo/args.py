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
    default="arginfo.json",
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
def cli(package, output, classes, functions):
    print(
        {
            "package": package,
            "output": output,
            "classes": classes,
            "functions": functions,
        }
    )

    extract_args(package, output, classes, functions)

    return


if __name__ == "__main__":
    cli()
