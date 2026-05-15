from __future__ import annotations

import math

from rfr_hjm_fmm.curve import DiscountCurve
from rfr_hjm_fmm.risk.convexity import convexity_parallel
from rfr_hjm_fmm.risk.dv01 import dv01_parallel


def test_dv01_parallel_for_single_discount_cashflow() -> None:
    curve = DiscountCurve(times=[1.0, 2.0], discounts=[0.98, 0.95])

    def price(c: DiscountCurve) -> float:
        return 100.0 * c.discount(1.0)

    expected = 100.0 * curve.discount(1.0) * math.sinh(0.0001)
    assert math.isclose(dv01_parallel(price, curve), expected, rel_tol=1e-12)


def test_convexity_parallel_for_single_discount_cashflow() -> None:
    curve = DiscountCurve(times=[1.0, 2.0], discounts=[0.98, 0.95])

    def price(c: DiscountCurve) -> float:
        return 100.0 * c.discount(1.0)

    expected = 100.0 * curve.discount(1.0) * (
        math.exp(0.0001) - 2.0 + math.exp(-0.0001)
    ) / (0.0001**2)
    assert math.isclose(convexity_parallel(price, curve), expected, rel_tol=1e-8)
