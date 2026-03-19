# pkginfo
Tools for extracting docstrings and argument information from a Python package's modules, classes, and methods.

## Installation

1. clone the repository<br>```git clone https://github.com/clorton/pkginfo.git```
2. install the package<br>`uv pip intall -e .`

## Sample Usage

### docstrings

Here's the pkginfo `docstrings` tool running against the pkginfo package itself. Note that ouput, by default, goes into `<package>.docs.json`.

```shell
docstrings pkginfo
```

```text
{'package': 'pkginfo', 'output': '<cwd>/pkginfo.docs.json', 'modules': True, 'classes': True, 'functions': True}
```

`pkginfo.docs.json`

```json
{
    "pkginfo": null,
    "pkginfo.args": null,
    "pkginfo.impl": null,
    "pkginfo.impl.extract_args": "Extract function and method signatures from a Python package and save them to a JSON file.\n\nArgs:\n    package (str): The name of the package to extract signatures from.\n    output (Path): The path to the output JSON file.\n    classes (bool): Whether to extract class method signatures.\n    functions (bool): Whether to extract function signatures.",
    "pkginfo.impl.extract_docstrings": "Extract docstrings from a Python package and save them to a JSON file.\n\nArgs:\n    package (str): The name of the package to extract docstrings from.\n    output (Path): The path to the output JSON file.\n    modules (bool): Whether to extract docstrings from modules.\n    classes (bool): Whether to extract docstrings from classes.\n    functions (bool): Whether to extract docstrings from functions.",
    "pkginfo.strings": null
}
```

**_Note:_** the `docstrings` tool/command returns the number of modules+classes+methods which do not have a docstring so, from the Unix/Linux/MacOS perspective, the tool only "succeeds" when the number of missing docstrings is zero. Otherwise the tool returns a number > 0 which, technically, is an error exit code.

### arginfo

Here's the pkginfo `arginfo` tool running against the pkginfo package itself. Note that output, by default, goes into `<package>.args.json`.

```shell
arginfo pkginfo
```

```text
{'package': 'pkginfo', 'output': '<cwd>/pkginfo.args.json', 'classes': True, 'functions': True}
```

`pkginfo.args.json`

```json
{
    "pkginfo.impl.extract_args": {
        "type": "function",
        "arguments": [
            { "name": "package", "type": "<class 'str'>" },
            { "name": "output", "type": "<class 'pathlib._local.Path'>" },
            { "name": "classes", "type": "<class 'bool'>" },
            { "name": "functions", "type": "<class 'bool'>" }
        ],
        "return_type": "None"
    },
    "pkginfo.impl.extract_docstrings": {
        "type": "function",
        "arguments": [
            { "name": "package", "type": "<class 'str'>" },
            { "name": "output", "type": "<class 'pathlib._local.Path'>" },
            { "name": "modules", "type": "<class 'bool'>" },
            { "name": "classes", "type": "<class 'bool'>" },
            { "name": "functions", "type": "<class 'bool'>" }
        ],
        "return_type": "<class 'int'>"
    }
}
```

## Options

- `--help`
- `-o|--output` write output to the given file
- `docstrings --no-modules` : don't check for module level docstrings
- `docstrings --no-classes` : don't check for class docstrings
- `docstrings --no-functions` : don't check for function docstrings
- `arginfo --no-classes` : don't report on class method arguments
- `arginfo --no-functions` : don't report on regular function arguments
