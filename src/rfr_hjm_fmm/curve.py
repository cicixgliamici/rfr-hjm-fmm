from __future__ import annotations

from dataclasses import dataclass
import bisect
import csv
import math

import icontract

from rfr_hjm_fmm.utils import assert_strictly_increasing


@dataclass
class DiscountCurve:
    """
    Simple discount curve with log-linear interpolation on discount factors.

    Attributes
    ----------
    times : list[float]
        Maturities in years.
    discounts : list[float]
        Discount factors P(0, T).
    """
    times: list[float]
    discounts: list[float]

    def __post_init__(self) -> None:
        if len(self.times) != len(self.discounts):
            raise ValueError("times and discounts must have the same length")
        if len(self.times) < 2:
            raise ValueError("curve must contain at least two points")

        assert_strictly_increasing(self.times, name="times")

        for p in self.discounts:
            if p <= 0.0:
                raise ValueError("all discount factors must be positive")

    @classmethod
    def from_csv(cls, path: str) -> "DiscountCurve":
        """
        Load a curve from a CSV file with columns:
        maturity_years, discount
        """
        times: list[float] = []
        discounts: list[float] = []

        with open(path, "r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                times.append(float(row["maturity_years"]))
                discounts.append(float(row["discount"]))

        return cls(times=times, discounts=discounts)

    def discount(self, t: float) -> float:
        """
        Return the discount factor P(0, t) using log-linear interpolation.
        """
        if t <= 0.0:
            return 1.0

        if t <= self.times[0]:
            return self._interp_log_discount(t, 0, 1)

        if t >= self.times[-1]:
            return self._interp_log_discount(t, len(self.times) - 2, len(self.times) - 1)

        idx = bisect.bisect_right(self.times, t) - 1
        return self._interp_log_discount(t, idx, idx + 1)

    def zero_rate(self, t: float) -> float:
        """
        Continuous-compounded zero rate:
        z(t) = -log(P(0,t)) / t
        """
        if t <= 0.0:
            return 0.0

        p = self.discount(t)
        return -math.log(p) / t

    @icontract.ensure(lambda result: result > 0.0, "forward discount must be positive")
    def forward_discount(self, t1: float, t2: float) -> float:
        """
        Forward discount factor P(t1, t2) under a deterministic curve:
        P(t1,t2) = P(0,t2) / P(0,t1)
        """
        if t2 < t1:
            raise ValueError("t2 must be >= t1")
        p1 = self.discount(t1)
        p2 = self.discount(t2)
        return p2 / p1

    def bumped_parallel(self, bump_bp: float) -> "DiscountCurve":
        """
        Build a new curve where all zero rates are shifted in parallel by bump_bp basis points.
        """
        bump = bump_bp / 10000.0
        bumped_discounts = [
            math.exp(-(self.zero_rate(t) + bump) * t)
            for t in self.times
        ]
        return DiscountCurve(times=self.times.copy(), discounts=bumped_discounts)

    def _interp_log_discount(self, t: float, i: int, j: int) -> float:
        t1, t2 = self.times[i], self.times[j]
        p1, p2 = self.discounts[i], self.discounts[j]

        if t2 == t1:
            return p1

        w = (t - t1) / (t2 - t1)
        lp = (1.0 - w) * math.log(p1) + w * math.log(p2)
        return math.exp(lp)
