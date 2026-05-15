from __future__ import annotations

from typing import Self

import numpy as np
from pydantic import BaseModel, ConfigDict, Field, model_validator

from rfr_hjm_fmm.curve import DiscountCurve
from rfr_hjm_fmm.instruments.frn import FloatingRateNote
from rfr_hjm_fmm.instruments.swap import PayerSwap
from rfr_hjm_fmm.models.fmm import GeneralizedFMMModel
from rfr_hjm_fmm.schedule import generate_regular_schedule


class StrictSpec(BaseModel):
    """
    Base class for Pydantic input specifications.
    """

    model_config = ConfigDict(extra="forbid")


class DiscountCurveSpec(StrictSpec):
    """
    Validated input payload for a discount curve.
    """

    times: list[float] = Field(min_length=2)
    discounts: list[float] = Field(min_length=2)

    @model_validator(mode="after")
    def validate_curve(self) -> Self:
        if len(self.times) != len(self.discounts):
            raise ValueError("times and discounts must have the same length")
        if any(t2 <= t1 for t1, t2 in zip(self.times, self.times[1:])):
            raise ValueError("times must be strictly increasing")
        if any(p <= 0.0 for p in self.discounts):
            raise ValueError("all discount factors must be positive")
        return self

    def to_curve(self) -> DiscountCurve:
        return DiscountCurve(times=self.times.copy(), discounts=self.discounts.copy())


class RegularScheduleSpec(StrictSpec):
    """
    Validated input payload for a regular numerical schedule.
    """

    maturity_years: float = Field(gt=0.0)
    payments_per_year: int = Field(gt=0)

    def build(self) -> tuple[list[float], list[float], list[float]]:
        return generate_regular_schedule(self.maturity_years, self.payments_per_year)


class FloatingRateNoteSpec(StrictSpec):
    """
    Validated input payload for an RFR-linked floating rate note.
    """

    notional: float = Field(gt=0.0)
    payment_dates: list[float] = Field(min_length=1)
    accrual_fractions: list[float] = Field(min_length=1)
    spread: float = 0.0

    @model_validator(mode="after")
    def validate_frn(self) -> Self:
        if len(self.payment_dates) != len(self.accrual_fractions):
            raise ValueError("payment_dates and accrual_fractions must have the same length")
        if any(t2 <= t1 for t1, t2 in zip(self.payment_dates, self.payment_dates[1:])):
            raise ValueError("payment_dates must be strictly increasing")
        if any(tau <= 0.0 for tau in self.accrual_fractions):
            raise ValueError("all accrual_fractions must be positive")
        return self

    def to_instrument(self) -> FloatingRateNote:
        return FloatingRateNote(
            notional=self.notional,
            payment_dates=self.payment_dates.copy(),
            accrual_fractions=self.accrual_fractions.copy(),
            spread=self.spread,
        )


class PayerSwapSpec(StrictSpec):
    """
    Validated input payload for a fixed-rate payer swap.
    """

    fixed_rate: float
    float_payment_dates: list[float] = Field(min_length=1)
    float_accruals: list[float] = Field(min_length=1)
    fixed_payment_dates: list[float] = Field(min_length=1)
    fixed_accruals: list[float] = Field(min_length=1)
    notional: float = Field(default=1.0, gt=0.0)

    @model_validator(mode="after")
    def validate_swap(self) -> Self:
        _validate_dates_and_accruals(
            self.float_payment_dates,
            self.float_accruals,
            "float",
        )
        _validate_dates_and_accruals(
            self.fixed_payment_dates,
            self.fixed_accruals,
            "fixed",
        )
        return self

    def to_instrument(self) -> PayerSwap:
        return PayerSwap(
            fixed_rate=self.fixed_rate,
            float_payment_dates=self.float_payment_dates.copy(),
            float_accruals=self.float_accruals.copy(),
            fixed_payment_dates=self.fixed_payment_dates.copy(),
            fixed_accruals=self.fixed_accruals.copy(),
            notional=self.notional,
        )


class FMMModelSpec(StrictSpec):
    """
    Validated input payload for the generalized FMM extended-rate scaffold.
    """

    period_starts: list[float] = Field(min_length=1)
    period_ends: list[float] = Field(min_length=1)
    accruals: list[float] = Field(min_length=1)
    initial_rates: list[float] = Field(min_length=1)
    correlation: list[list[float]] | None = None
    a0: float = Field(default=0.001, ge=0.0)
    a1: float = Field(default=0.10, ge=0.0)

    @model_validator(mode="after")
    def validate_fmm(self) -> Self:
        n_periods = len(self.period_ends)
        if len(self.period_starts) != n_periods:
            raise ValueError("period_starts must match period_ends")
        if len(self.accruals) != n_periods:
            raise ValueError("accruals must match period_ends")
        if len(self.initial_rates) != n_periods:
            raise ValueError("initial_rates must match period_ends")
        if any(t2 <= t1 for t1, t2 in zip(self.period_ends, self.period_ends[1:])):
            raise ValueError("period_ends must be strictly increasing")
        for start, end in zip(self.period_starts, self.period_ends):
            if end <= start:
                raise ValueError("each period end must be greater than its start")
        if any(tau <= 0.0 for tau in self.accruals):
            raise ValueError("all accruals must be positive")
        if any(rate <= -1.0 for rate in self.initial_rates):
            raise ValueError("initial rates must be greater than -100%")
        if self.correlation is not None:
            _validate_correlation_matrix(self.correlation, n_periods)
        return self

    def to_model(self) -> GeneralizedFMMModel:
        correlation = None
        if self.correlation is not None:
            correlation = np.array(self.correlation, dtype=float)
        return GeneralizedFMMModel(
            period_starts=self.period_starts.copy(),
            period_ends=self.period_ends.copy(),
            accruals=self.accruals.copy(),
            initial_rates=self.initial_rates.copy(),
            correlation=correlation,
            a0=self.a0,
            a1=self.a1,
        )


def _validate_dates_and_accruals(
    dates: list[float],
    accruals: list[float],
    leg_name: str,
) -> None:
    if len(dates) != len(accruals):
        raise ValueError(f"{leg_name} payment dates and accruals must have the same length")
    if any(t2 <= t1 for t1, t2 in zip(dates, dates[1:])):
        raise ValueError(f"{leg_name} payment dates must be strictly increasing")
    if any(tau <= 0.0 for tau in accruals):
        raise ValueError(f"all {leg_name} accruals must be positive")


def _validate_correlation_matrix(values: list[list[float]], n_periods: int) -> None:
    matrix = np.array(values, dtype=float)
    if matrix.shape != (n_periods, n_periods):
        raise ValueError("correlation must have shape (n_periods, n_periods)")
    if not np.allclose(matrix, matrix.T):
        raise ValueError("correlation must be symmetric")
    if not np.allclose(np.diag(matrix), np.ones(n_periods)):
        raise ValueError("correlation diagonal must be one")
    try:
        np.linalg.cholesky(matrix)
    except np.linalg.LinAlgError as exc:
        raise ValueError("correlation must be positive definite") from exc
