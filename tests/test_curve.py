from __future__ import annotations

from rfr_hjm_fmm.curve import DiscountCurve


def test_discount_at_zero_is_one() -> None:
    curve = DiscountCurve(
        times=[0.5, 1.0, 2.0],
        discounts=[0.99, 0.97, 0.94],
    )
    assert curve.discount(0.0) == 1.0


def test_discount_is_positive() -> None:
    curve = DiscountCurve(
        times=[0.5, 1.0, 2.0],
        discounts=[0.99, 0.97, 0.94],
    )
    assert curve.discount(1.5) > 0.0


def test_zero_rate_is_non_negative_for_decreasing_curve() -> None:
    curve = DiscountCurve(
        times=[0.5, 1.0, 2.0],
        discounts=[0.99, 0.97, 0.94],
    )
    assert curve.zero_rate(1.0) >= 0.0
