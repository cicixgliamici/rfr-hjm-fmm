from __future__ import annotations

from rfr_hjm_fmm.curve import DiscountCurve
from rfr_hjm_fmm.schedule import generate_regular_schedule
from rfr_hjm_fmm.instruments.swap import PayerSwap
from rfr_hjm_fmm.pricing.swap_pricer import par_swap_rate, price_payer_swap


def main() -> None:
    curve = DiscountCurve.from_csv("data/ois_curve_example.csv")

    float_starts, float_dates, float_accruals = generate_regular_schedule(
        maturity_years=5.0,
        payments_per_year=4,
    )
    _, fixed_dates, fixed_accruals = generate_regular_schedule(
        maturity_years=5.0,
        payments_per_year=1,
    )

    k_par = par_swap_rate(
        t=0.0,
        float_payment_dates=float_dates,
        float_accruals=float_accruals,
        fixed_payment_dates=fixed_dates,
        fixed_accruals=fixed_accruals,
        float_period_starts=float_starts,
        curve=curve,
    )

    swap = PayerSwap(
        fixed_rate=k_par,
        float_payment_dates=float_dates,
        float_accruals=float_accruals,
        fixed_payment_dates=fixed_dates,
        fixed_accruals=fixed_accruals,
        notional=100.0,
    )

    value = price_payer_swap(
        t=0.0,
        swap=swap,
        curve=curve,
        float_period_starts=float_starts,
    )

    print("=== Swap Example ===")
    print(f"Par swap rate: {k_par:.6f}")
    print(f"Payer swap value at inception: {value:.6f}")


if __name__ == "__main__":
    main()
