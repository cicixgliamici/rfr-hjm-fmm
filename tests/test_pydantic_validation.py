from __future__ import annotations

import numpy as np
import pytest
from pydantic import ValidationError

from rfr_hjm_fmm.curve import DiscountCurve
from rfr_hjm_fmm.instruments.frn import FloatingRateNote
from rfr_hjm_fmm.instruments.swap import PayerSwap
from rfr_hjm_fmm.models.fmm import GeneralizedFMMModel
from rfr_hjm_fmm.validation import (
    DiscountCurveSpec,
    FMMModelSpec,
    FloatingRateNoteSpec,
    PayerSwapSpec,
    RegularScheduleSpec,
)


def test_discount_curve_spec_builds_curve() -> None:
    spec = DiscountCurveSpec(times=[1.0, 2.0], discounts=[0.99, 0.97])

    curve = spec.to_curve()

    assert isinstance(curve, DiscountCurve)
    assert curve.times == [1.0, 2.0]
    assert curve.discounts == [0.99, 0.97]


def test_discount_curve_spec_rejects_invalid_curve() -> None:
    with pytest.raises(ValidationError, match="strictly increasing"):
        DiscountCurveSpec(times=[1.0, 1.0], discounts=[0.99, 0.97])


def test_specs_forbid_extra_fields() -> None:
    with pytest.raises(ValidationError, match="Extra inputs"):
        RegularScheduleSpec(
            maturity_years=1.0,
            payments_per_year=4,
            unexpected=True,
        )


def test_regular_schedule_spec_builds_schedule() -> None:
    assert RegularScheduleSpec(maturity_years=1.0, payments_per_year=2).build() == (
        [0.0, 0.5],
        [0.5, 1.0],
        [0.5, 0.5],
    )


def test_frn_spec_builds_instrument_and_rejects_invalid_accruals() -> None:
    spec = FloatingRateNoteSpec(
        notional=100.0,
        payment_dates=[0.5, 1.0],
        accrual_fractions=[0.5, 0.5],
        spread=0.0025,
    )

    assert isinstance(spec.to_instrument(), FloatingRateNote)

    with pytest.raises(ValidationError, match="positive"):
        FloatingRateNoteSpec(
            notional=100.0,
            payment_dates=[0.5, 1.0],
            accrual_fractions=[0.5, 0.0],
            spread=0.0025,
        )


def test_swap_spec_builds_instrument_and_rejects_unordered_dates() -> None:
    spec = PayerSwapSpec(
        fixed_rate=0.02,
        float_payment_dates=[0.5, 1.0],
        float_accruals=[0.5, 0.5],
        fixed_payment_dates=[1.0, 2.0],
        fixed_accruals=[1.0, 1.0],
        notional=100.0,
    )

    assert isinstance(spec.to_instrument(), PayerSwap)

    with pytest.raises(ValidationError, match="strictly increasing"):
        PayerSwapSpec(
            fixed_rate=0.02,
            float_payment_dates=[1.0, 0.5],
            float_accruals=[0.5, 0.5],
            fixed_payment_dates=[1.0, 2.0],
            fixed_accruals=[1.0, 1.0],
        )


def test_fmm_model_spec_builds_model() -> None:
    spec = FMMModelSpec(
        period_starts=[0.0, 0.5],
        period_ends=[0.5, 1.0],
        accruals=[0.5, 0.5],
        initial_rates=[0.01, 0.02],
        correlation=[[1.0, 0.25], [0.25, 1.0]],
    )

    model = spec.to_model()

    assert isinstance(model, GeneralizedFMMModel)
    assert np.allclose(model.correlation, np.array([[1.0, 0.25], [0.25, 1.0]]))


def test_fmm_model_spec_rejects_bad_correlation() -> None:
    with pytest.raises(ValidationError, match="positive definite"):
        FMMModelSpec(
            period_starts=[0.0, 0.5],
            period_ends=[0.5, 1.0],
            accruals=[0.5, 0.5],
            initial_rates=[0.01, 0.02],
            correlation=[[1.0, 1.0], [1.0, 1.0]],
        )
