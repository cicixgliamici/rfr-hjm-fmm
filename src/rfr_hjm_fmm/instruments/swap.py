from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PayerSwap:
    """
    Plain vanilla fixed-floating payer swap.

    The holder pays the fixed leg and receives the floating leg.
    """
    fixed_rate: float
    float_payment_dates: list[float]
    float_accruals: list[float]
    fixed_payment_dates: list[float]
    fixed_accruals: list[float]
    notional: float = 1.0

    def __post_init__(self) -> None:
        if self.notional <= 0.0:
            raise ValueError("notional must be positive")
        if len(self.float_payment_dates) != len(self.float_accruals):
            raise ValueError("float payment dates and accruals must have the same length")
        if len(self.fixed_payment_dates) != len(self.fixed_accruals):
            raise ValueError("fixed payment dates and accruals must have the same length")
