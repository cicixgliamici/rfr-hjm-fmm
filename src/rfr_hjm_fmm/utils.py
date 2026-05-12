from __future__ import annotations

import math


def assert_strictly_increasing(values: list[float], name: str = "values") -> None:
    """
    Ensure that a list is strictly increasing.

    Parameters
    ----------
    values : list[float]
        Sequence of values to validate.
    name : str
        Name used in the error message.

    Raises
    ------
    ValueError
        If the list is empty or not strictly increasing.
    """
    if not values:
        raise ValueError(f"{name} must not be empty")

    for i in range(1, len(values)):
        if values[i] <= values[i - 1]:
            raise ValueError(f"{name} must be strictly increasing")


def is_close(a: float, b: float, tol: float = 1e-10) -> bool:
    """
    Compare two floating-point numbers with a small absolute tolerance.
    """
    return math.isclose(a, b, abs_tol=tol, rel_tol=tol)
