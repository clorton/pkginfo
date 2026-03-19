"""
A submodule with various classes and functions for testing.

This module demonstrates different patterns of docstrings and type annotations.
"""

from typing import Optional, Union


class DocumentedClass:
    """
    A class with proper documentation.

    This class demonstrates various method types and documentation patterns.
    """

    def __init__(self, value: int) -> None:
        """
        Initialize the documented class.

        Args:
            value (int): The initial value.
        """
        self.value = value

    def instance_method(self, increment: int = 1) -> int:
        """
        Increment the value by a given amount.

        Args:
            increment (int): Amount to increment. Defaults to 1.

        Returns:
            int: The new value after incrementing.
        """
        self.value += increment
        return self.value

    @staticmethod
    def static_method(x: float, y: float) -> float:
        """
        Add two numbers using a static method.

        Args:
            x (float): First number.
            y (float): Second number.

        Returns:
            float: Sum of x and y.
        """
        return x + y

    @classmethod
    def class_method(cls, name: str) -> "DocumentedClass":
        """
        Create an instance using a class method.

        Args:
            name (str): A name to use for initialization.

        Returns:
            DocumentedClass: A new instance.
        """
        return cls(len(name))


class UndocumentedClass:
    def __init__(self, data: str) -> None:
        self.data = data

    def method_without_docs(self, count: int) -> str:
        return self.data * count


def complex_function(
    required: str,
    optional: Optional[int] = None,
    union_type: Union[str, int] = "default",
    *args: str,
    **kwargs: int,
) -> dict:
    """
    Function with complex type annotations.

    Args:
        required (str): A required string parameter.
        optional (Optional[int]): An optional integer. Defaults to None.
        union_type (Union[str, int]): A parameter that accepts multiple types.
        *args (str): Variable positional arguments.
        **kwargs (int): Variable keyword arguments.

    Returns:
        dict: A dictionary with the processed arguments.
    """
    return {
        "required": required,
        "optional": optional,
        "union_type": union_type,
        "args": args,
        "kwargs": kwargs,
    }


def no_type_annotations(a, b, c=10):
    """
    Function without type annotations.

    Args:
        a: First parameter without type.
        b: Second parameter without type.
        c: Third parameter with default. Defaults to 10.

    Returns:
        The sum of all parameters.
    """
    return a + b + c


def function_without_docstring():
    return 42
