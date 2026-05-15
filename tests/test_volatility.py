from __future__ import annotations

import pytest

from rfr_hjm_fmm.volatility import gamma_linear, sigma_parametric


def test_gamma_linear_boundaries() -> None:
    assert gamma_linear(0.0, 1.0, 2.0) == 1.0
    assert gamma_linear(1.0, 1.0, 2.0) == 1.0
    assert gamma_linear(2.0, 1.0, 2.0) == 0.0
    assert gamma_linear(3.0, 1.0, 2.0) == 0.0


def test_gamma_linear_decays_inside_period() -> None:
    assert gamma_linear(1.25, 1.0, 2.0) == 0.75
    assert gamma_linear(1.50, 1.0, 2.0) == 0.50
    assert gamma_linear(1.75, 1.0, 2.0) == 0.25


def test_gamma_linear_rejects_invalid_period() -> None:
    with pytest.raises(ValueError, match="end must be greater than start"):
        gamma_linear(1.0, 2.0, 2.0)


def test_sigma_parametric_includes_linear_decay() -> None:
    assert sigma_parametric(0.0, 1.0, 2.0, r0=0.02, a0=0.001, a1=0.10) == 0.003
    assert sigma_parametric(1.5, 1.0, 2.0, r0=0.02, a0=0.001, a1=0.10) == 0.0015
    assert sigma_parametric(2.0, 1.0, 2.0, r0=0.02, a0=0.001, a1=0.10) == 0.0
