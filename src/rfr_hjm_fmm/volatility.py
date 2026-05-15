from __future__ import annotations

import icontract

@icontract.ensure(lambda result: 0.0 <= result <= 1.0, "gamma must stay in [0, 1]")
def gamma_linear(t: float, start: float, end: float) -> float:
    """
    Linear volatility decay function.

    It matches the paper's intuitive specification:
    - 1 before the accrual period starts
    - linearly decreasing during the accrual period
    - 0 after the accrual period ends
    """
    if end <= start:
        raise ValueError("end must be greater than start")

    if t <= start:
        return 1.0
    if t >= end:
        return 0.0
    return (end - t) / (end - start)


def sigma_parametric(
    t: float,
    start: float,
    end: float,
    r0: float,
    a0: float = 0.001,
    a1: float = 0.10,
) -> float:
    """
    Simple parametric volatility:
    sigma_j(t) = (a0 + a1 * R_j(0)) * gamma_j(t)

    This is included already in V1 because it will be useful in V2,
    where we add stochastic simulation.
    """
    return (a0 + a1 * r0) * gamma_linear(t, start, end)
