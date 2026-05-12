from __future__ import annotations

from rfr_hjm_fmm.curve import DiscountCurve
from rfr_hjm_fmm.schedule import generate_regular_schedule
from rfr_hjm_fmm.instruments.frn import FloatingRateNote
from rfr_hjm_fmm.instruments.swap import PayerSwap
from rfr_hjm_fmm.pricing.frn_pricer import price_frn
from rfr_hjm_fmm.pricing.swap_pricer import par_swap_rate, price_payer_swap
from rfr_hjm_fmm.risk.dv01 import dv01_parallel
from rfr_hjm_fmm.risk.convexity import convexity_parallel


def main() -> None:
    curve = DiscountCurve.from_csv("data/ois_curve_example.csv")

    starts, float_dates, float_accruals = generate_regular_schedule(
        maturity_years=5.0,
        payments_per_year=4,
    )
    _, fixed_dates, fixed_accruals = generate_regular_schedule(
        maturity_years=5.0,
        payments_per_year=1,
    )

    frn = FloatingRateNote(
        notional=100.0,
        payment_dates=float_dates,
        accrual_fractions=float_accruals,
        spread=0.0025,
    )

    k_par = par_swap_rate(
        t=0.0,
        float_payment_dates=float_dates,
        float_accruals=float_accruals,
        fixed_payment_dates=fixed_dates,
        fixed_accruals=fixed_accruals,
        float_period_starts=starts,
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

    def frn_price_fn(c):
        return price_frn(0.0, frn, c, starts)

    def swap_price_fn(c):
        return price_payer_swap(0.0, swap, c, starts)

    frn_value = frn_price_fn(curve)
    swap_value = swap_price_fn(curve)

    frn_dv01 = dv01_parallel(frn_price_fn, curve)
    swap_dv01 = dv01_parallel(swap_price_fn, curve)

    frn_conv = convexity_parallel(frn_price_fn, curve)
    swap_conv = convexity_parallel(swap_price_fn, curve)

    print("=== Risk Example ===")
    print(f"FRN price:      {frn_value:.6f}")
    print(f"Swap price:     {swap_value:.6f}")
    print(f"FRN DV01:       {frn_dv01:.6f}")
    print(f"Swap DV01:      {swap_dv01:.6f}")
    print(f"FRN Convexity:  {frn_conv:.6f}")
    print(f"Swap Convexity: {swap_conv:.6f}")


if __name__ == "__main__":
    main()
