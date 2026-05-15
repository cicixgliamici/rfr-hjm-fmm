from __future__ import annotations

import math

import pytest

from rfr_hjm_fmm.curve import DiscountCurve
from rfr_hjm_fmm.schedule import generate_regular_schedule
from rfr_hjm_fmm.instruments.frn import FloatingRateNote
from rfr_hjm_fmm.pricing.frn_pricer import price_frn


def test_frn_price_is_positive() -> None:
    curve = DiscountCurve(
        times=[0.25, 0.5, 1.0, 2.0, 3.0, 5.0],
        discounts=[0.999, 0.998, 0.995, 0.988, 0.978, 0.952],
    )
    starts, dates, accruals = generate_regular_schedule(5.0, 4)

    frn = FloatingRateNote(
        notional=100.0,
        payment_dates=dates,
        accrual_fractions=accruals,
        spread=0.0025,
    )

    value = price_frn(0.0, frn, curve, starts)
    assert value > 0.0


def test_frn_positive_spread_increases_price() -> None:
    curve = DiscountCurve(
        times=[0.5, 1.0, 2.0],
        discounts=[0.99, 0.97, 0.94],
    )
    starts, dates, accruals = generate_regular_schedule(2.0, 2)
    flat = FloatingRateNote(100.0, dates, accruals, 0.0)
    spread = FloatingRateNote(100.0, dates, accruals, 0.0025)

    assert price_frn(0.0, spread, curve, starts) > price_frn(0.0, flat, curve, starts)


def test_frn_price_after_maturity_is_redemption_discount_only() -> None:
    curve = DiscountCurve(
        times=[0.5, 1.0, 2.0],
        discounts=[0.99, 0.97, 0.94],
    )
    starts, dates, accruals = generate_regular_schedule(1.0, 2)
    frn = FloatingRateNote(100.0, dates, accruals, 0.0)

    assert math.isclose(
        price_frn(2.0, frn, curve, starts),
        100.0 * curve.discount(dates[-1]),
        rel_tol=1e-12,
    )


def test_frn_price_rejects_mismatched_period_starts() -> None:
    curve = DiscountCurve(times=[0.5, 1.0], discounts=[0.99, 0.97])
    frn = FloatingRateNote(100.0, [0.5, 1.0], [0.5, 0.5], 0.0)

    with pytest.raises(ValueError, match="period_starts must match"):
        price_frn(0.0, frn, curve, [0.0])
