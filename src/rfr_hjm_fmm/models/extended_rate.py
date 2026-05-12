from __future__ import annotations

from dataclasses import dataclass

from rfr_hjm_fmm.curve import DiscountCurve


@dataclass
class ExtendedRate:
    """
    Extended forward rate associated with an accrual period [start, end].

    Formula:
        R_j(t) = ( P(t, start) / P(t, end) - 1 ) / tau

    In this V1 implementation we use a deterministic term structure:
        P(t, T) = P(0,T) / P(0,t), for t <= T
    """
    start: float
    end: float
    tau: float

    def __post_init__(self) -> None:
        if self.end <= self.start:
            raise ValueError("end must be greater than start")
        if self.tau <= 0.0:
            raise ValueError("tau must be positive")

    def value(self, t: float, curve: DiscountCurve) -> float:
        """
        Evaluate the extended rate at time t.

        Notes
        -----
        For this deterministic V1:
        - if t <= start, the rate is fully forward-looking
        - if start < t <= end, we still use the same deterministic formula
        - if t > end, we return the realized fixing approximated as the value at end
        """
        if t <= self.end:
            p_t_start = self._bond_price(t, self.start, curve)
            p_t_end = self._bond_price(t, self.end, curve)
            return (p_t_start / p_t_end - 1.0) / self.tau

        # After the end of the accrual period, keep the fixing frozen.
        p_end_start = self._bond_price(self.end, self.start, curve)
        p_end_end = self._bond_price(self.end, self.end, curve)
        return (p_end_start / p_end_end - 1.0) / self.tau

    def _bond_price(self, t: float, T: float, curve: DiscountCurve) -> float:
        """
        Deterministic bond price P(t,T).

        If T < t, the payment date is already in the past.
        For V1, we collapse it to 1.0 in the frozen-fixing logic used above.
        """
        if T < t:
            return 1.0
        return curve.forward_discount(t, T)
