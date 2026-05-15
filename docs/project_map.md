# Project Map

## Functional View

`rfr-hjm-fmm` is intended to be a Python implementation of the paper
`Alternative Risk-Free Rates and the New Indexation Framework: An Analysis of
Compounded Overnight Rates with Applications to FRNs and Swaps`.

The implementation target is to encode the mathematical framework and
numerical experiment described in the paper, including the RFR
compounded-in-arrears setup, the extended forward rates, the generalized FMM
dynamics, the HJM completion, and the FRN/swap simulation and risk analysis.

The current codebase implements the deterministic subset plus tested FMM and
HJM scaffolds:

- building and querying an OIS-style discount curve;
- computing zero rates and deterministic forward discount factors;
- computing extended forward rates for accrual periods;
- pricing RFR-linked floating rate notes (FRNs);
- pricing plain-vanilla payer swaps;
- computing par swap rates;
- computing parallel DV01 and convexity by bump-and-reprice.
- simulating generalized FMM extended-rate paths.
- simulating Markovian HJM states and reconstructing pathwise `P(t,T)`.

These pieces are not yet coupled into the full paper workflow.

## Current Model

The current implementation uses a deterministic single-curve subset:

- discount factors `P(0, T)` are read directly or provided as curve points;
- discount interpolation is log-linear on discount factors;
- deterministic forward discount factors use `P(t, T) = P(0, T) / P(0, t)`;
- extended rates use the accrual-period formula
  `R_j(t) = (P(t, T_{j-1}) / P(t, T_j) - 1) / tau_j`;
- schedules are regular year-fraction grids with no calendar adjustment;
- pricing discounts cash flows directly from the deterministic initial curve.

The code does not yet implement the full paper stochastic HJM-FMM simulation:

- generalized FMM drift/diffusion for `R_j(t)` is only a tested scaffold;
- HJM-completed term-structure state is only a tested scaffold;
- Markovian HJM state variables `X(t)` and `Y(t)` are implemented but not yet
  coupled to valuation;
- bank account `B(t)` and short-rate path updates are implemented in the HJM
  scaffold;
- pathwise reconstruction of `P(t, T)` is implemented in the HJM scaffold;
- no monthly simulation grid;
- no Monte Carlo valuation table matching the paper's numerical section.

## Software Flow

The main runtime flow is:

1. `DiscountCurve` stores and interpolates discount factors.
2. `generate_regular_schedule` creates period starts, payment dates, and
   accrual fractions.
3. Instrument dataclasses hold trade inputs for FRNs and payer swaps.
4. `ExtendedRate` computes each floating period rate from the curve.
5. Pricers aggregate discounted floating, fixed, spread, and notional cash
   flows.
6. Risk functions wrap a pricing function and reprice under parallel curve
   bumps.

In compact form:

```text
DiscountCurve -> schedule -> instrument -> ExtendedRate -> pricer -> risk
```

## Module Map

- `src/rfr_hjm_fmm/curve.py`: discount curve, zero rates, forward discounts,
  CSV loading, and parallel curve bumping.
- `src/rfr_hjm_fmm/schedule.py`: simple regular schedule generation.
- `src/rfr_hjm_fmm/models/extended_rate.py`: deterministic extended forward
  rate for one accrual period.
- `src/rfr_hjm_fmm/models/fmm.py`: generalized FMM extended-rate scaffold.
- `src/rfr_hjm_fmm/models/hjm.py`: Markovian HJM completion scaffold.
- `src/rfr_hjm_fmm/models/deterministic_model.py`: thin deterministic term
  structure wrapper.
- `src/rfr_hjm_fmm/instruments/`: FRN and payer swap dataclasses.
- `src/rfr_hjm_fmm/pricing/`: FRN price, payer swap price, and par swap rate.
- `src/rfr_hjm_fmm/risk/`: parallel DV01 and convexity finite differences.
- `src/rfr_hjm_fmm/volatility.py`: early V2 volatility helpers, including
  linear decay and a parametric sigma function.
- `examples/`: executable examples for FRN, swap, and risk calculations.
- `tests/`: current unit tests for curve behavior, extended rates, and FRN
  pricing.
- `docs/`: formulas, assumptions, roadmap, and project-level notes.

## Paper Coverage

Current coverage against the paper:

- Sections 3.1-3.3: partially covered through compounded-rate motivation and
  the extended-rate formula.
- Sections 3.6-3.8: partially covered through deterministic FRN/swap pricing,
  par swap rate, DV01, and convexity.
- Section 4: only superficially covered by examples; the actual hybrid
  HJM-FMM simulation and Monte Carlo layer are missing.
- Section 3.4: partially implemented through the generalized FMM scaffold.
- Section 3.5: partially implemented through the Markovian HJM scaffold.

## Current Test State

The local test suite currently contains 22 tests. In the current checkout:

- `python -m pytest -q` fails because the `src/` package is not installed or
  otherwise added to the import path;
- `$env:PYTHONPATH='src'; python -m pytest -q` passes with `22 passed`.

That means the implemented deterministic subset and the FMM/HJM scaffolds are
testable, but the developer/test setup is not yet review-ready out of the box.

## Known Boundaries

The current boundaries are important because they mark the gap between this
checkout and the paper:

- deterministic initial discount curve;
- single-curve pricing;
- vanilla FRNs and payer swaps only;
- simple regular schedules and year fractions;
- no market calibration;
- generalized FMM stochastic dynamics are partial and not yet coupled to HJM;
- HJM completion is a tested scaffold, not yet coupled to FMM or valuation;
- no stochastic state evolution or Monte Carlo pricing;
- no business-day calendar logic;
- no RFR lookback, lockout, observation shift, or payment-delay conventions.
