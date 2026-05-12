from __future__ import annotations

from collections.abc import Callable

from rfr_hjm_fmm.curve import DiscountCurve


def convexity_parallel(
    price_fn: Callable[[DiscountCurve], float],
    curve: DiscountCurve,
    bump_bp: float = 1.0,
) -> float:
    """
    Parallel convexity via central finite differences.

    Convexity ≈ [V(+h) - 2V(0) + V(-h)] / h^2
    where h is the parallel zero-rate shift in decimal form.
    """
    h = bump_bp / 10000.0

    up_curve = curve.bumped_parallel(bump_bp)
    down_curve = curve.bumped_parallel(-bump_bp)

    v0 = price_fn(curve)
    v_up = price_fn(up_curve)
    v_down = price_fn(down_curve)

    return (v_up - 2.0 * v0 + v_down) / (h ** 2)
