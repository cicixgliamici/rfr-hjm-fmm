from __future__ import annotations

from rfr_hjm_fmm.curve import DiscountCurve
from rfr_hjm_fmm.schedule import generate_regular_schedule
from rfr_hjm_fmm.instruments.frn import FloatingRateNote
from rfr_hjm_fmm.pricing.frn_pricer import price_frn


def main() -> None:
    curve = DiscountCurve.from_csv("data/ois_curve_example.csv")

    starts, payment_dates, accruals = generate_regular_schedule(
        maturity_years=5.0,
        payments_per_year=4,
    )

    frn = FloatingRateNote(
        notional=100.0,
        payment_dates=payment_dates,
        accrual_fractions=accruals,
        spread=0.0025,  # 25 bps
    )

    value = price_frn(
        t=0.0,
        frn=frn,
        curve=curve,
        period_starts=starts,
    )

    print("=== FRN Example ===")
    print(f"Price: {value:.6f}")


if __name__ == "__main__":
    main()
