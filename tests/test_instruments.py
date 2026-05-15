from __future__ import annotations

import pytest

from rfr_hjm_fmm.instruments.frn import FloatingRateNote
from rfr_hjm_fmm.instruments.swap import PayerSwap


def test_frn_rejects_non_positive_notional() -> None:
    with pytest.raises(ValueError, match="notional must be positive"):
        FloatingRateNote(
            notional=0.0,
            payment_dates=[1.0],
            accrual_fractions=[1.0],
            spread=0.0,
        )


def test_frn_rejects_empty_payment_dates() -> None:
    with pytest.raises(ValueError, match="payment_dates must not be empty"):
        FloatingRateNote(
            notional=100.0,
            payment_dates=[],
            accrual_fractions=[],
            spread=0.0,
        )


def test_frn_rejects_mismatched_dates_and_accruals() -> None:
    with pytest.raises(ValueError, match="same length"):
        FloatingRateNote(
            notional=100.0,
            payment_dates=[1.0, 2.0],
            accrual_fractions=[1.0],
            spread=0.0,
        )


def test_swap_rejects_non_positive_notional() -> None:
    with pytest.raises(ValueError, match="notional must be positive"):
        PayerSwap(
            fixed_rate=0.02,
            float_payment_dates=[1.0],
            float_accruals=[1.0],
            fixed_payment_dates=[1.0],
            fixed_accruals=[1.0],
            notional=0.0,
        )


def test_swap_rejects_mismatched_float_leg() -> None:
    with pytest.raises(ValueError, match="float payment dates"):
        PayerSwap(
            fixed_rate=0.02,
            float_payment_dates=[1.0, 2.0],
            float_accruals=[1.0],
            fixed_payment_dates=[1.0],
            fixed_accruals=[1.0],
        )


def test_swap_rejects_mismatched_fixed_leg() -> None:
    with pytest.raises(ValueError, match="fixed payment dates"):
        PayerSwap(
            fixed_rate=0.02,
            float_payment_dates=[1.0],
            float_accruals=[1.0],
            fixed_payment_dates=[1.0, 2.0],
            fixed_accruals=[1.0],
        )
