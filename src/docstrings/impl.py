def extract_docstrings(package, output, modules, classes, functions):
    """
    Extract docstrings from a Python package and save them to a JSON file.

    Args:
        package (str): The name of the package to extract docstrings from.
        output (str): The path to the output JSON file.
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
                docstrings[f"{modname}.{name}"] = inspect.getdoc(obj)
            elif inspect.isfunction(obj) and functions:
                docstrings[f"{modname}.{name}"] = inspect.getdoc(obj)

    # Save the extracted docstrings to a JSON file
    with open(output, "w") as f:
        json.dump(docstrings, f, indent=4)

    return
