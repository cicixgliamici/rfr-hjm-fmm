from __future__ import annotations

from collections.abc import Callable

from rfr_hjm_fmm.curve import DiscountCurve


def dv01_parallel(
    price_fn: Callable[[DiscountCurve], float],
    curve: DiscountCurve,
    bump_bp: float = 1.0,
) -> float:
    """
    Parallel DV01 via bump-and-reprice.

    Returns:
        (V_down - V_up) / 2

    This matches the usual central-difference approximation
    used in the paper's finite-difference discussion.
    """
    up_curve = curve.bumped_parallel(bump_bp)
    down_curve = curve.bumped_parallel(-bump_bp)

    v_up = price_fn(up_curve)
    v_down = price_fn(down_curve)

    return (v_down - v_up) / 2.0
