# rfr-hjm-fmm

A Python implementation of the post-IBOR pricing framework for compounded overnight risk-free rates (RFRs), following the HJM-FMM approach described in:

**Alternative Risk-Free Rates and the New Indexation Framework: An Analysis of Compounded Overnight Rates with Applications to FRNs and Swaps**

## Motivation

The transition from IBOR benchmarks to overnight risk-free rates is not just a benchmark replacement. It also changes the structure of floating cash flows and the way interest-rate instruments should be modeled, priced, and risk-managed.

This repository is being aligned with the paper's mathematical framework and numerical experiment.

## Current status

- deterministic OIS discount curve
- zero rates and deterministic forward discount factors
- deterministic extended forward rates
- deterministic pricing of:
  - RFR-linked floating rate notes
  - plain vanilla payer swaps
- par swap rate
- DV01
- convexity
- generalized FMM extended-rate scaffold
- Markovian HJM completion scaffold

The current implementation has deterministic pricing/risk plus tested FMM and HJM scaffolds. The remaining work is coupling those layers for pathwise pricing, then adding the monthly simulation grid, Monte Carlo experiment, and paper risk table.

## Planned extensions

- stochastic dynamics for extended rates
- Monte Carlo pricing
- hybrid HJM-FMM state evolution
- richer volatility structures
- calibration

## Repository structure

- `src/rfr_hjm_fmm/curve.py`: discount curve and zero rates
- `src/rfr_hjm_fmm/models/extended_rate.py`: extended rate process
- `src/rfr_hjm_fmm/models/fmm.py`: generalized FMM extended-rate scaffold
- `src/rfr_hjm_fmm/models/hjm.py`: Markovian HJM completion scaffold
- `src/rfr_hjm_fmm/instruments/`: FRN and swap instruments
- `src/rfr_hjm_fmm/pricing/`: pricing functions
- `src/rfr_hjm_fmm/risk/`: DV01 and convexity
- `examples/`: executable examples
- `tests/`: validation suite

## Quick start

```bash
pip install -r requirements.txt
pip install -e .
pytest
python examples/run_frn.py
python examples/run_swap.py
python examples/run_risk.py
