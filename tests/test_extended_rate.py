from __future__ import annotations

from rfr_hjm_fmm.curve import DiscountCurve
from rfr_hjm_fmm.models.extended_rate import ExtendedRate


def test_extended_rate_is_positive_for_decreasing_discount_curve() -> None:
    curve = DiscountCurve(
        times=[0.25, 0.5, 1.0, 2.0],
        discounts=[0.999, 0.997, 0.993, 0.985],
    )
    rate = ExtendedRate(start=0.5, end=1.0, tau=0.5)
    value = rate.value(0.0, curve)
    assert value > 0.0


def test_extended_rate_frozen_after_end() -> None:
    curve = DiscountCurve(
        times=[0.25, 0.5, 1.0, 2.0],
        discounts=[0.999, 0.997, 0.993, 0.985],
    )
    rate = ExtendedRate(start=0.5, end=1.0, tau=0.5)

    v1 = rate.value(1.2, curve)
    v2 = rate.value(1.5, curve)

    assert abs(v1 - v2) < 1e-12
