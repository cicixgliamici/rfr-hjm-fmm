from __future__ import annotations

import numpy as np
import pytest

from rfr_hjm_fmm.models.fmm import GeneralizedFMMModel


def make_model() -> GeneralizedFMMModel:
    return GeneralizedFMMModel(
        period_starts=[0.0, 0.5],
        period_ends=[0.5, 1.0],
        accruals=[0.5, 0.5],
        initial_rates=[0.01, 0.02],
        correlation=np.eye(2),
        a0=0.001,
        a1=0.10,
    )


def test_fmm_model_rejects_invalid_correlation_shape() -> None:
    with pytest.raises(ValueError, match="correlation must have shape"):
        GeneralizedFMMModel(
            period_starts=[0.0, 0.5],
            period_ends=[0.5, 1.0],
            accruals=[0.5, 0.5],
            initial_rates=[0.01, 0.02],
            correlation=np.eye(3),
        )


def test_fmm_model_rejects_non_positive_definite_correlation() -> None:
    with pytest.raises(ValueError, match="positive definite"):
        GeneralizedFMMModel(
            period_starts=[0.0, 0.5],
            period_ends=[0.5, 1.0],
            accruals=[0.5, 0.5],
            initial_rates=[0.01, 0.02],
            correlation=np.array([[1.0, 1.0], [1.0, 1.0]]),
        )


def test_effective_volatility_uses_initial_rates_and_decay() -> None:
    model = make_model()

    assert np.allclose(model.gamma_vector(0.0), np.array([1.0, 1.0]))
    assert np.allclose(model.effective_volatility(0.0), np.array([0.002, 0.003]))

    assert np.allclose(model.gamma_vector(0.75), np.array([0.0, 0.5]))
    assert np.allclose(model.effective_volatility(0.75), np.array([0.0, 0.0015]))


def test_drift_matches_identity_correlation_formula() -> None:
    model = make_model()

    drift = model.drift(0.0, np.array([0.01, 0.02]))

    expected_0 = 0.002 * (0.5 * 0.002 / (1.0 + 0.5 * 0.01))
    expected_1 = 0.003 * (0.5 * 0.003 / (1.0 + 0.5 * 0.02))
    assert np.allclose(drift, np.array([expected_0, expected_1]))


def test_step_freezes_rates_after_period_end() -> None:
    model = make_model()
    rng = np.random.default_rng(123)
    rates = np.array([0.01, 0.02])

    next_rates = model.step(0.75, rates, 0.25, rng)

    assert next_rates[0] == rates[0]
    assert next_rates[1] != rates[1]


def test_simulation_is_reproducible_with_seed() -> None:
    model = make_model()
    times = [0.0, 0.25, 0.5, 0.75, 1.0]

    path_1 = model.simulate(times, seed=42)
    path_2 = model.simulate(times, seed=42)
    path_3 = model.simulate(times, seed=43)

    assert np.array_equal(path_1.times, np.array(times))
    assert path_1.rates.shape == (5, 2)
    assert np.allclose(path_1.rates, path_2.rates)
    assert not np.allclose(path_1.rates, path_3.rates)


def test_fmm_simulation_rejects_non_increasing_times() -> None:
    model = make_model()

    with pytest.raises(ValueError, match="strictly increasing"):
        model.simulate([0.0, 0.5, 0.5], seed=42)


def test_fmm_step_rejects_non_positive_dt() -> None:
    model = make_model()

    with pytest.raises(ValueError, match="dt must be positive"):
        model.step(0.0, np.array([0.01, 0.02]), 0.0, np.random.default_rng(1))


def test_fmm_drift_rejects_invalid_rate_denominator() -> None:
    model = make_model()

    with pytest.raises(ValueError, match="must be positive"):
        model.drift(0.0, np.array([-3.0, 0.02]))
