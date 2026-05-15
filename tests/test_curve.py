from __future__ import annotations

import math

import pytest

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


def test_discount_log_linear_interpolation_has_expected_value() -> None:
    curve = DiscountCurve(
        times=[1.0, 3.0],
        discounts=[math.exp(-0.02), math.exp(-0.06)],
    )

    assert math.isclose(curve.discount(2.0), math.exp(-0.04), rel_tol=1e-12)


def test_forward_discount_matches_discount_ratio() -> None:
    curve = DiscountCurve(
        times=[0.5, 1.0, 2.0],
        discounts=[0.99, 0.97, 0.94],
    )

    assert math.isclose(
        curve.forward_discount(0.5, 2.0),
        curve.discount(2.0) / curve.discount(0.5),
        rel_tol=1e-12,
    )


def test_curve_rejects_mismatched_lengths() -> None:
    with pytest.raises(ValueError, match="same length"):
        DiscountCurve(times=[1.0, 2.0], discounts=[0.99])


def test_curve_rejects_non_increasing_times() -> None:
    with pytest.raises(ValueError, match="strictly increasing"):
        DiscountCurve(times=[1.0, 1.0], discounts=[0.99, 0.98])


def test_curve_rejects_non_positive_discount() -> None:
    with pytest.raises(ValueError, match="positive"):
        DiscountCurve(times=[1.0, 2.0], discounts=[0.99, 0.0])


def test_forward_discount_rejects_backwards_interval() -> None:
    curve = DiscountCurve(times=[1.0, 2.0], discounts=[0.99, 0.98])

    with pytest.raises(ValueError, match="t2 must be >= t1"):
        curve.forward_discount(2.0, 1.0)
