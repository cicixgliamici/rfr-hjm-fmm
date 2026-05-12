from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FloatingRateNote:
    """
    Floating Rate Note indexed to an RFR-based rate.

    Attributes
    ----------
    notional : float
        Principal amount.
    payment_dates : list[float]
        Coupon payment dates.
    accrual_fractions : list[float]
        Year fractions associated with each coupon period.
    spread : float
        Constant spread added to the floating coupon.
    """
    notional: float
    payment_dates: list[float]
    accrual_fractions: list[float]
    spread: float

    def __post_init__(self) -> None:
        if self.notional <= 0.0:
            raise ValueError("notional must be positive")
        if len(self.payment_dates) != len(self.accrual_fractions):
            raise ValueError("payment_dates and accrual_fractions must have the same length")
        if not self.payment_dates:
            raise ValueError("payment_dates must not be empty")
