# rfr-hjm-fmm

A Python implementation of a post-IBOR pricing framework for compounded overnight risk-free rates (RFRs), inspired by the HJM-FMM approach described in:

**Alternative Risk-Free Rates and the New Indexation Framework: An Analysis of Compounded Overnight Rates with Applications to FRNs and Swaps**

## Motivation

The transition from IBOR benchmarks to overnight risk-free rates is not just a benchmark replacement. It also changes the structure of floating cash flows and the way interest-rate instruments should be modeled, priced, and risk-managed.

This repository implements a clean and educational version of that framework.

## Current features

- OIS discount curve
- zero rates and forward discount factors
- extended forward rates
- pricing of:
  - RFR-linked floating rate notes
  - plain vanilla payer swaps
- par swap rate
- DV01
- convexity

## Planned extensions

- stochastic dynamics for extended rates
- Monte Carlo pricing
- hybrid HJM-FMM state evolution
- richer volatility structures
- calibration

## Repository structure

- `src/rfr_hjm_fmm/curve.py`: discount curve and zero rates
- `src/rfr_hjm_fmm/models/extended_rate.py`: extended rate process
- `src/rfr_hjm_fmm/instruments/`: FRN and swap instruments
- `src/rfr_hjm_fmm/pricing/`: pricing functions
- `src/rfr_hjm_fmm/risk/`: DV01 and convexity
- `examples/`: executable demos
- `tests/`: validation suite

## Quick start

```bash
pip install -r requirements.txt
pip install -e .
pytest
python examples/run_frn.py
python examples/run_swap.py
python examples/run_risk.py
