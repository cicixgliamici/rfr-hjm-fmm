# Roadmap

This roadmap is organized around implementing the paper, not around a generic
pricing-library progression.

## Phase 1: Paper Traceability

- Maintain `docs/paper_traceability.md` as the source of truth for what is
  implemented, partial, or missing.
- Use `docs/model_flow.md` and `docs/hjm_fmm_architecture.md` as the visual
  map of the paper-to-code implementation path.
- Keep formulas split between paper target formulas and current deterministic
  approximations.
- Add tests that lock down the deterministic subset before introducing
  stochastic dynamics.

## Phase 2: Generalized FMM Dynamics

- Implemented baseline: extended-rate state vectors over the accrual schedule,
  volatility decay, parametric volatility, correlation validation, Brownian
  increments, drift, Euler stepping, and seeded single-path generation.
- Next: extend the seeded paths to the paper's monthly grid and prepare the
  interface that HJM completion will use for pathwise bond prices.

## Phase 3: HJM Completion

- Implemented baseline: Markovian HJM state variables `X(t)` and `Y(t)`,
  integrated `G(t,T)`, initial forward-rate reconstruction, pathwise bond
  prices `P(t,T)`, short-rate extraction, bank-account updates, and seeded HJM
  state paths.
- Next: couple HJM bond prices with FMM extended-rate paths and generalize the
  valuation layer to consume pathwise `R_j(t)` and `P(t,T)`.

## Phase 4: Numerical Simulation

- Build the monthly grid used by the paper's numerical section.
- Initialize the OIS curve, zero rates, and extended rates from the project
  data.
- Run single-path simulations for FRN and payer swap values.
- Reprice instruments pathwise using the HJM-FMM bond prices rather than the
  deterministic initial curve.

## Phase 5: Monte Carlo And Risk Table

- Add multi-path Monte Carlo valuation for FRN and payer swap.
- Compute mean values and standard errors.
- Rebuild the full simulation under parallel curve bumps for DV01 and
  convexity.
- Reproduce the qualitative behavior in the paper table: FRN close to par,
  par swap near zero at inception, swap risk larger than FRN risk, and
  declining risk as maturity shortens.

## Phase 6: Review Readiness

- Configure tests to run without manual `PYTHONPATH` setup.
- Introduce the validation discipline described in
  `docs/validation_language.md`.
- Maintain the Pydantic/icontract split described in
  `docs/validation_stack.md`.
- Expand Pydantic specs for experiment configuration, especially the
  paper-reproduction workflow.
- Add CI for tests, linting, type checks, and package build.
- Add regression tests around paper-traceability milestones.
- Document remaining gaps explicitly before any release tag.
