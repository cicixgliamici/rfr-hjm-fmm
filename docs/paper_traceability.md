# Paper Traceability

This file tracks how the repository maps to `Alternative Risk-Free Rates and
the New Indexation Framework: An Analysis of Compounded Overnight Rates with
Applications to FRNs and Swaps`.

Status values:

- `implemented`: covered by current code and at least basic tests or examples.
- `partial`: represented by current code, but only as a deterministic subset,
  helper, or approximation.
- `missing`: not yet implemented in code.

Related diagrams:

- `docs/model_flow.md`: end-to-end flow from OIS curve to paper numerical table.
- `docs/hjm_fmm_architecture.md`: mathematical layers and code boundaries.

| Paper section | Concept / equation | Status | Current modules | Tests required |
| --- | --- | --- | --- | --- |
| 3.1 Overnight rate compounded in arrears | Discrete overnight compounding and continuous approximation through the bank account `B(T_j) / B(T_{j-1})` | missing | None | Unit tests for compounded overnight fixings, day-count fractions, and continuous approximation against a controlled short-rate path |
| 3.2 Forward-looking and backward-looking rates | Relationship between the backward-looking realized RFR and forward-looking rate under the `T_j`-forward measure | missing | None | Tests showing period-start forward-looking values and period-end realized rates are represented by the same extended-rate process |
| 3.3 Extended forward rate | `R_j(t) = (P(t,T_{j-1}) / P(t,T_j) - 1) / tau_j` and freezing after `T_j` | partial | `models/extended_rate.py`, `curve.py` | Add expected-value tests at `t=0`, inside the accrual period, at `T_j`, and after `T_j`; clarify deterministic approximation |
| 3.4 Generalized FMM dynamics | Stochastic dynamics for `R_j(t)` with drift, Brownian drivers, correlation, volatility `sigma_j(t)`, and decay `gamma_j(t)` | partial | `models/fmm.py`, `volatility.py` | Extend seeded-path tests to multi-step paper grids and later reconcile with HJM-completed bond prices |
| 3.4 Volatility decay | `gamma_j(t)` equal to 1 before the period, decaying during the period, and 0 after `T_j` | implemented | `volatility.py`, `models/fmm.py` | Covered by boundary and inside-period tests; add regression checks once paper calibration is fixed |
| 3.4 Parametric volatility | `sigma_j(t) = (a0 + a1 R_j(0)) gamma_j(t)` | implemented | `volatility.py`, `models/fmm.py` | Covered by expected-value tests; add calibration tests later |
| 3.5 FMM-HJM completion | Recursive link from extended rates to bond prices and completion of the term structure | partial | `models/hjm.py` | Couple HJM-completed bond prices to simulated FMM extended rates and test no-arbitrage consistency on a toy grid |
| 3.5 Markovian HJM state | Separable volatility, state variables `X(t)` and `Y(t)`, and pathwise forward-rate/bond-price reconstruction | partial | `models/hjm.py` | Extend seeded tests to multi-factor functions and validate pathwise `P(t,T)`, `r(t)`, and `B(t)` inside pricing |
| 3.6 RFR-linked FRN valuation | Residual floating coupons plus notional redemption using `P(t,T_j)` and `R_j(t)` | partial | `pricing/frn_pricer.py`, `instruments/frn.py` | Expected-value tests for deterministic cases, spread sensitivity, maturity behavior, and later pathwise HJM-FMM pricing |
| 3.7 Fixed-floating payer swap valuation | Floating leg minus fixed leg and par swap rate | partial | `pricing/swap_pricer.py`, `instruments/swap.py` | Tests for par swap value near zero, fixed-rate sensitivity, residual schedule handling, and pathwise valuation |
| 3.8 DV01 / PV01 | Parallel bump-and-reprice sensitivity to the initial curve | partial | `risk/dv01.py`, `curve.py` | Expected sign and scale tests for FRN and swap; later rerun full simulation after each bumped curve |
| 3.8 Convexity | Central finite-difference second derivative with respect to parallel curve shifts | partial | `risk/convexity.py`, `curve.py` | Controlled toy-instrument tests and regression tests against paper-level qualitative behavior |
| 4 Numerical implementation | Initial OIS curve, zero rates, initial extended rates, monthly simulation grid, state updates, pricing, risk | missing | `examples/` only covers deterministic examples | End-to-end example and regression tests for the full paper workflow |
| 4 Monte Carlo simulation | Multi-path FRN/swap valuation, mean values, standard errors, DV01 and convexity table | missing | None | Seeded Monte Carlo smoke tests and tolerance-band regression tests for the paper's headline results |

## Current Implementation Summary

The current repository implements the deterministic pricing and risk scaffold:

- OIS-style discount curve and zero-rate extraction;
- deterministic forward discount factors;
- deterministic extended-rate formula;
- FRN and payer swap valuation using the current deterministic curve;
- par swap rate;
- parallel DV01 and convexity finite differences.

The implementation now has tested scaffolds for generalized FMM extended-rate
paths and Markovian HJM state evolution. It still lacks the coupling between
the two layers, paper-consistent pathwise pricing, the monthly paper simulation
workflow, and Monte Carlo aggregation.
