from __future__ import annotations

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
