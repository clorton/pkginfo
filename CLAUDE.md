## General
- Always use python3 rather than python to run Python scripts.
- Always use the local .venv virtual environment unless explicitly told otherwise.
- Always note accepted edits in CHANGELOG.md
- Always use double quotes unless already inside a quoted string
- Always use pathlib rather than os.path as long as possible
## Documentation - docstrings
- Always use Google style docstrings formatted for markdown (not restructuredtext)
- Always include information on exceptions explicitly raised in the code
- Consider executable code examples in docstrings when appropriate and concise
## Testing
- Always write tests in a "given-when-then" style: given this scenario, when I call this function, then I expect (`assert`) this result
- Ensure that the test actually constructs the given scenario.
- Ensure that the test actually calls or executes the when aspect of the test.
- Ensure that the test actually checks the then expected outcome of calling the "when" code, method, function, or class.
- Always add a docstring to tests explaining the purpose of the test and the implications of failure(s)
- Always comment on inconsistencies or ambiguities in functions being tested
- Always run new tests to verify implementation before considering implementation as complete
