from __future__ import annotations

import math

import pytest

from rfr_hjm_fmm.curve import DiscountCurve
from rfr_hjm_fmm.instruments.swap import PayerSwap
from rfr_hjm_fmm.pricing.swap_pricer import par_swap_rate, price_payer_swap
from rfr_hjm_fmm.schedule import generate_regular_schedule


def make_curve() -> DiscountCurve:
    return DiscountCurve(
        times=[0.25, 0.5, 1.0, 2.0, 3.0],
        discounts=[0.999, 0.997, 0.992, 0.982, 0.968],
    )


def test_par_swap_prices_near_zero_at_inception() -> None:
    curve = make_curve()
    float_starts, float_dates, float_accruals = generate_regular_schedule(2.0, 4)
    _, fixed_dates, fixed_accruals = generate_regular_schedule(2.0, 1)

    par_rate = par_swap_rate(
        0.0,
        float_dates,
        float_accruals,
        fixed_dates,
        fixed_accruals,
        float_starts,
        curve,
    )
    swap = PayerSwap(
        fixed_rate=par_rate,
        float_payment_dates=float_dates,
        float_accruals=float_accruals,
        fixed_payment_dates=fixed_dates,
        fixed_accruals=fixed_accruals,
        notional=100.0,
    )

    assert math.isclose(
        price_payer_swap(0.0, swap, curve, float_starts),
        0.0,
        abs_tol=1e-12,
    )


def test_higher_fixed_rate_lowers_payer_swap_value() -> None:
    curve = make_curve()
    float_starts, float_dates, float_accruals = generate_regular_schedule(2.0, 4)
    _, fixed_dates, fixed_accruals = generate_regular_schedule(2.0, 1)

    low_fixed = PayerSwap(
        fixed_rate=0.01,
        float_payment_dates=float_dates,
        float_accruals=float_accruals,
        fixed_payment_dates=fixed_dates,
        fixed_accruals=fixed_accruals,
        notional=100.0,
    )
    high_fixed = PayerSwap(
        fixed_rate=0.03,
        float_payment_dates=float_dates,
        float_accruals=float_accruals,
        fixed_payment_dates=fixed_dates,
        fixed_accruals=fixed_accruals,
        notional=100.0,
    )

    assert price_payer_swap(0.0, high_fixed, curve, float_starts) < price_payer_swap(
        0.0,
        low_fixed,
        curve,
        float_starts,
    )


def test_par_swap_rate_rejects_zero_denominator() -> None:
    curve = make_curve()

    with pytest.raises(ValueError, match="denominator is zero"):
        par_swap_rate(
            t=3.0,
            float_payment_dates=[1.0],
            float_accruals=[1.0],
            fixed_payment_dates=[1.0],
            fixed_accruals=[1.0],
            float_period_starts=[0.0],
            curve=curve,
        )
