# Assumptions And Current Gaps

The repository is intended to implement the paper `Alternative Risk-Free Rates
and the New Indexation Framework: An Analysis of Compounded Overnight Rates
with Applications to FRNs and Swaps`.

The simplifications below are current implementation gaps, not the final design
goal.

## Current Simplifications

- deterministic initial discount curve;
- deterministic forward discount factors from the initial curve;
- single-curve setup;
- vanilla FRN and payer swap only;
- simple year-fraction schedules;
- no overnight fixing path;
- no bank account `B(t)`;
- generalized FMM stochastic dynamics only as a tested scaffold;
- HJM completion only as a tested scaffold;
- pathwise bond-price reconstruction only inside the HJM scaffold;
- no monthly simulation grid;
- no Monte Carlo aggregation;
- no market calibration;
- no business-day calendar logic;
- no lookback, lockout, observation-shift, or payment-delay conventions.

## Working Defaults

- Use the existing deterministic implementation as a baseline and regression
  scaffold while the paper model is implemented.
- Treat the numerical table in the paper as a qualitative regression target
  until every required input parameter is explicitly represented in code.
- Add market conventions and calibration only after the core HJM-FMM simulation
  reproduces the paper workflow.
