from __future__ import annotations

import math

import icontract
import numpy as np
import pytest

from rfr_hjm_fmm.curve import DiscountCurve
from rfr_hjm_fmm.models.hjm import HJMState, MarkovianHJMModel
from rfr_hjm_fmm.volatility import gamma_linear


def test_gamma_contract_allows_valid_decay_values() -> None:
    assert gamma_linear(0.0, 1.0, 2.0) == 1.0
    assert gamma_linear(1.5, 1.0, 2.0) == 0.5
    assert gamma_linear(2.0, 1.0, 2.0) == 0.0


def test_forward_discount_contract_allows_positive_result() -> None:
    curve = DiscountCurve(times=[1.0, 2.0], discounts=[0.98, 0.95])

    assert curve.forward_discount(1.0, 2.0) > 0.0


def test_bond_price_contract_rejects_negative_state_result() -> None:
    curve = DiscountCurve(times=[0.5, 1.0], discounts=[math.exp(-0.02 * 0.5), math.exp(-0.02)])
    model = MarkovianHJMModel.constant_one_factor(curve)
    impossible_state = HJMState(
        time=1.0,
        x=np.array([0.0]),
        y=np.array([[0.0]]),
        bank_account=-1.0,
    )

    with pytest.raises(icontract.ViolationError, match="bond price must be positive"):
        model.bond_price(impossible_state, 0.5)
