from __future__ import annotations

import math

import numpy as np
import pytest

from rfr_hjm_fmm.curve import DiscountCurve
from rfr_hjm_fmm.models.hjm import MarkovianHJMModel


def flat_curve(rate: float = 0.03) -> DiscountCurve:
    times = [0.5, 1.0, 2.0, 3.0]
    discounts = [math.exp(-rate * t) for t in times]
    return DiscountCurve(times=times, discounts=discounts)


def test_hjm_rejects_invalid_factor_shape() -> None:
    curve = flat_curve()

    with pytest.raises(ValueError, match="g must return shape"):
        MarkovianHJMModel(
            curve=curve,
            g=lambda _: np.array([1.0, 2.0]),
            zeta=lambda _: np.array([0.0]),
            n_factors=1,
        )


def test_integrated_g_for_constant_one_factor() -> None:
    model = MarkovianHJMModel.constant_one_factor(flat_curve(), g_level=2.0)

    assert np.allclose(model.integrated_g(0.5, 1.5), np.array([2.0]))
    assert np.allclose(model.integrated_g(1.0, 1.0), np.array([0.0]))


def test_zero_vol_bond_price_matches_deterministic_forward_discount() -> None:
    curve = flat_curve()
    model = MarkovianHJMModel.constant_one_factor(curve, zeta_level=0.0)
    state = model.initial_state()

    state = model.step(state, 0.5, np.random.default_rng(123))

    assert np.allclose(state.x, np.array([0.0]))
    assert np.allclose(state.y, np.array([[0.0]]))
    assert math.isclose(
        model.bond_price(state, 2.0),
        curve.forward_discount(0.5, 2.0),
        rel_tol=1e-12,
    )


def test_bank_account_updates_from_short_rate() -> None:
    rate = 0.03
    model = MarkovianHJMModel.constant_one_factor(flat_curve(rate), zeta_level=0.0)
    state = model.step(model.initial_state(), 0.5, np.random.default_rng(123))

    assert math.isclose(state.bank_account, math.exp(rate * 0.5), rel_tol=1e-12)


def test_positive_vol_updates_y_and_seeded_path_is_reproducible() -> None:
    model = MarkovianHJMModel.constant_one_factor(
        flat_curve(),
        g_level=1.0,
        zeta_level=0.02,
    )
    times = [0.0, 0.25, 0.5, 0.75]

    path_1 = model.simulate(times, seed=42)
    path_2 = model.simulate(times, seed=42)
    path_3 = model.simulate(times, seed=43)

    assert path_1.x.shape == (4, 1)
    assert path_1.y.shape == (4, 1, 1)
    assert np.allclose(path_1.y[-1], np.array([[0.02**2 * 0.75]]))
    assert np.allclose(path_1.x, path_2.x)
    assert not np.allclose(path_1.x, path_3.x)


def test_bond_price_at_state_time_is_one() -> None:
    model = MarkovianHJMModel.constant_one_factor(flat_curve())
    state = model.step(model.initial_state(), 0.5, np.random.default_rng(123))

    assert model.bond_price(state, state.time) == 1.0


def test_hjm_simulation_rejects_times_not_starting_at_zero() -> None:
    model = MarkovianHJMModel.constant_one_factor(flat_curve())

    with pytest.raises(ValueError, match="start at 0.0"):
        model.simulate([0.25, 0.5], seed=1)


def test_hjm_step_rejects_non_positive_dt() -> None:
    model = MarkovianHJMModel.constant_one_factor(flat_curve())

    with pytest.raises(ValueError, match="dt must be positive"):
        model.step(model.initial_state(), 0.0, np.random.default_rng(1))


def test_hjm_bond_price_rejects_negative_maturity() -> None:
    model = MarkovianHJMModel.constant_one_factor(flat_curve())

    with pytest.raises(ValueError, match="maturity must be non-negative"):
        model.bond_price(model.initial_state(), -0.1)
