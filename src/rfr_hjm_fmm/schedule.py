from __future__ import annotations


def generate_regular_schedule(
    maturity_years: float,
    payments_per_year: int,
) -> tuple[list[float], list[float], list[float]]:
    """
    Build a regular payment schedule.

    Parameters
    ----------
    maturity_years : float
        Final maturity in years.
    payments_per_year : int
        Number of payments per year. Example:
        - 4 for quarterly
        - 2 for semiannual
        - 1 for annual

    Returns
    -------
    tuple[list[float], list[float], list[float]]
        A tuple containing:
        - period starts
        - period ends / payment dates
        - accrual fractions

    Notes
    -----
    This uses a simple year-fraction convention:
    tau = 1 / payments_per_year
    """
    if maturity_years <= 0.0:
        raise ValueError("maturity_years must be positive")
    if payments_per_year <= 0:
        raise ValueError("payments_per_year must be positive")

    tau = 1.0 / payments_per_year
    n_periods = int(round(maturity_years * payments_per_year))

    starts = [i * tau for i in range(n_periods)]
    ends = [(i + 1) * tau for i in range(n_periods)]
    accruals = [tau] * n_periods

    return starts, ends, accruals
