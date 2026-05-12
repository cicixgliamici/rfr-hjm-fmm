from __future__ import annotations

from dataclasses import dataclass

from rfr_hjm_fmm.curve import DiscountCurve


@dataclass
class DeterministicTermStructureModel:
    """
    Very simple deterministic model wrapper.

    In V1, the entire term structure is represented by the initial discount curve.
    In V2, this can be replaced or extended by a stochastic state model.
    """
    curve: DiscountCurve

    def discount(self, t: float, T: float) -> float:
        """
        Deterministic forward discount factor P(t, T) inferred from the initial curve.
        """
        if T < t:
            raise ValueError("T must be >= t")
        return self.curve.forward_discount(t, T)
