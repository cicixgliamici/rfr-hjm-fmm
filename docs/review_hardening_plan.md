# Review Hardening Plan

## Goal

Make `rfr-hjm-fmm` ready for a serious technical and quantitative review as an
implementation of the paper `Alternative Risk-Free Rates and the New
Indexation Framework: An Analysis of Compounded Overnight Rates with
Applications to FRNs and Swaps`.

The target state is a traceable implementation of the paper. The code should
make clear which equations and numerical results are implemented, which are
approximated, and which remain future work.

## Milestone 1: Technical Stabilization

- Make the test command work out of the box from a fresh checkout, either by
  documenting and validating `pip install -e .` or by configuring pytest for
  the `src/` layout.
- Add CI with a minimal matrix for supported Python versions and run tests on
  every pull request.
- Decide the real Python support policy. The current `pyproject.toml` declares
  `>=3.10`, while the local environment uses Python 3.14.
- Add basic linting and formatting checks, such as Ruff, and keep the rules
  small enough for the project size.
- Add type checking with mypy or pyright once public APIs and dataclass fields
  are stable.
- Complete package metadata: author, license, classifiers, test extras, and
  optional dev dependencies.

## Milestone 2: Paper Traceability

- Create a traceability matrix from paper section/equation to code module,
  test, and implementation status.
- Maintain the visual diagrams in `docs/model_flow.md` and
  `docs/hjm_fmm_architecture.md` as the model grows.
- Mark the current deterministic curve, extended-rate, FRN, swap, DV01, and
  convexity code as the deterministic subset of Sections 3.3 and 3.6-3.8.
- Mark Sections 3.4 and 3.5 as missing core work: generalized FMM dynamics and
  Markovian HJM completion.
- Mark Section 4 as missing except for basic examples: monthly simulation,
  stochastic paths, Monte Carlo means, and pathwise risk analysis are not yet
  implemented.
- Update formulas documentation so it distinguishes paper formulas from current
  code approximations.

## Milestone 3: Quantitative Correctness

- Add numerical tests with explicit expected values for discount interpolation,
  zero rates, forward discounts, extended rates, FRN price, swap price, and par
  swap rate.
- Use the JML-like validation discipline in `docs/validation_language.md` to
  express preconditions, postconditions, invariants, and model properties.
- Use Pydantic specs for external configuration and input validation, keeping
  NumPy/dataclass objects as the numerical core.
- Use icontract for focused internal postconditions and invariants, as
  described in `docs/validation_stack.md`.
- Add invariant tests:
  - par swap value is approximately zero at inception when priced at its par
    rate;
  - positive spreads increase FRN value;
  - parallel upward rate bumps reduce the value of standard positive-duration
    cash flows;
  - frozen extended rates remain stable after the accrual period ends.
- Add edge-case tests for curve validation, non-increasing times, non-positive
  discount factors, empty schedules, inconsistent list lengths, zero accruals,
  past payment dates, and zero fixed-leg denominator.
- Validate DV01 and convexity against controlled toy instruments where the
  expected direction and scale are known.
- Document which formulas are exact in V1 and which are approximations of the
  target HJM-FMM framework.

## Milestone 4: HJM-FMM Model Implementation

- Implement the generalized FMM dynamics for extended rates `R_j(t)` with
  volatility decay `gamma_j(t)`, rate volatility `sigma_j(t)`, and correlation
  between Brownian drivers.
- Add the paper's linear decay and parametric volatility form
  `sigma_j(t) = (a0 + a1 R_j(0)) gamma_j(t)` as first-class model components.
- Implement a simulation grid, initially monthly as in the numerical section.
- Add Markovian HJM state variables `X(t)` and `Y(t)` for separable volatility,
  including deterministic initialization and reproducible Brownian increments.
- Reconstruct pathwise bond prices `P(t, T)`, short rate `r(t)`, and bank
  account `B(t)` consistently with the HJM completion.
- Preserve the existing deterministic implementation as a baseline and smoke
  test, not as the final model.

## Milestone 5: API and Domain Robustness

- Strengthen dataclass validation for instruments:
  payment dates should be non-empty and ordered, accruals should be positive,
  and instrument schedules should be internally consistent.
- Make schedule generation reject maturities that do not align cleanly with the
  requested payment frequency, or document the rounding behavior explicitly.
- Introduce clearer domain errors where user input is invalid, while keeping
  ordinary `ValueError` acceptable for simple validation.
- Expose a small, intentional public API from `rfr_hjm_fmm.__init__` after the
  core objects stabilize.
- Keep examples aligned with the public API so they act as executable
  documentation.

## Milestone 6: Numerical Experiment from the Paper

- Reproduce the paper's Section 4 workflow: initial OIS curve, zero rates,
  initial extended rates, monthly path simulation, FRN valuation, payer swap
  valuation, DV01, and convexity.
- Add Monte Carlo aggregation with means and standard errors for FRN and swap
  values.
- Add regression tests around the paper's headline numerical behavior:
  FRN close to par and converging toward notional, par swap near zero at
  inception, swap risk larger than FRN risk, and declining risk with maturity.
- Store simulation parameters explicitly: maturity, notional, spread, par fixed
  rate, grid frequency, volatility parameters, number of paths, and random seed.
- Decide whether to target exact reproduction of the paper table or stable
  tolerance bands, depending on whether all paper inputs are fully specified.

## Milestone 7: Market Conventions and Extensions

- Add richer RFR conventions only after the paper baseline works: compounding
  in arrears, lookback, observation shift, lockout if needed, and payment delay.
- Add business-day calendars and date-based schedules once numerical-year
  schedules are stable.
- Improve curve handling with market quote bootstrapping or at least a clearer
  abstraction for OIS curve construction.
- Extend volatility support from simple parametric sigma to calibratable
  structures.

## Milestone 8: Deployability and Review Readiness

- Add GitHub Actions for test, lint, type check, and package build.
- Add a build verification step using `python -m build` and install the wheel
  in a clean environment before running smoke tests.
- Run all examples in CI so README commands stay truthful.
- Add `CHANGELOG.md` and keep semantic versioning discipline from the first
  reviewed release.
- Add a short reviewer guide explaining the intended scope, current
  simplifications, and how to reproduce the test results.
- Add release artifacts only after the deterministic V1 has stronger numerical
  coverage and a passing clean-install workflow.

## Acceptance Criteria

The project can be considered review-ready for V1 when:

- a fresh checkout can install the package and run tests with documented
  commands;
- CI passes for the declared Python versions;
- pricing and risk functions have deterministic expected-value tests;
- invalid inputs fail with clear errors;
- examples run without manual path setup;
- documentation states exactly which parts of the paper are implemented,
  approximated, or missing.
