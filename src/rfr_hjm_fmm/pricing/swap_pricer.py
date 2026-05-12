from __future__ import annotations

from rfr_hjm_fmm.curve import DiscountCurve
from rfr_hjm_fmm.instruments.swap import PayerSwap
from rfr_hjm_fmm.models.extended_rate import ExtendedRate


def price_payer_swap(
    t: float,
    swap: PayerSwap,
    curve: DiscountCurve,
    float_period_starts: list[float],
) -> float:
    """
    Price a payer swap:
    receive floating, pay fixed
    """
    if len(float_period_starts) != len(swap.float_payment_dates):
        raise ValueError("float_period_starts must match the number of floating payment dates")

    float_leg = 0.0
    fixed_leg = 0.0

    for j, Tj in enumerate(swap.float_payment_dates):
        if Tj < t:
            continue

        tau = swap.float_accruals[j]
        Tjm1 = float_period_starts[j]
        rj = ExtendedRate(start=Tjm1, end=Tj, tau=tau).value(t, curve)
        float_leg += swap.notional * tau * curve.discount(Tj) * rj

    for j, Tj in enumerate(swap.fixed_payment_dates):
        if Tj < t:
            continue

        tau = swap.fixed_accruals[j]
        fixed_leg += swap.notional * tau * curve.discount(Tj) * swap.fixed_rate

    return float_leg - fixed_leg


def par_swap_rate(
    t: float,
    float_payment_dates: list[float],
    float_accruals: list[float],
    fixed_payment_dates: list[float],
    fixed_accruals: list[float],
    float_period_starts: list[float],
    curve: DiscountCurve,
) -> float:
    """
    Compute the par fixed rate K such that the initial payer swap value is zero.
    """
    if len(float_payment_dates) != len(float_accruals):
        raise ValueError("floating dates and accruals must match")
    if len(fixed_payment_dates) != len(fixed_accruals):
        raise ValueError("fixed dates and accruals must match")
    if len(float_period_starts) != len(float_payment_dates):
        raise ValueError("float_period_starts must match floating dates")

    numerator = 0.0
    denominator = 0.0

    for j, Tj in enumerate(float_payment_dates):
        if Tj < t:
            continue

        tau = float_accruals[j]
        Tjm1 = float_period_starts[j]
        rj = ExtendedRate(start=Tjm1, end=Tj, tau=tau).value(t, curve)
        numerator += tau * curve.discount(Tj) * rj

    for j, Tj in enumerate(fixed_payment_dates):
        if Tj < t:
            continue

        denominator += fixed_accruals[j] * curve.discount(Tj)

    if denominator == 0.0:
        raise ValueError("denominator is zero; check fixed leg schedule")

    return numerator / denominator
