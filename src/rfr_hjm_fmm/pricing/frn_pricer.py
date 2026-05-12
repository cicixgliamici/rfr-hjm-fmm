from __future__ import annotations

from rfr_hjm_fmm.curve import DiscountCurve
from rfr_hjm_fmm.instruments.frn import FloatingRateNote
from rfr_hjm_fmm.models.extended_rate import ExtendedRate


def price_frn(
    t: float,
    frn: FloatingRateNote,
    curve: DiscountCurve,
    period_starts: list[float],
) -> float:
    """
    Price an RFR-linked floating rate note.

    Formula:
        V_FRN(t) = N * sum_j tau_j * P(0, T_j) * (R_j(t) + s)
                   + N * P(0, T_n)

    In V1 we discount from time 0 directly and keep the implementation simple.
    """
    if len(period_starts) != len(frn.payment_dates):
        raise ValueError("period_starts must match the number of payment dates")

    value = 0.0
    n = len(frn.payment_dates)

    for j in range(n):
        Tj = frn.payment_dates[j]
        if Tj < t:
            continue

        Tjm1 = period_starts[j]
        tau = frn.accrual_fractions[j]

        rj = ExtendedRate(start=Tjm1, end=Tj, tau=tau).value(t, curve)
        value += frn.notional * tau * curve.discount(Tj) * (rj + frn.spread)

    value += frn.notional * curve.discount(frn.payment_dates[-1])
    return value
