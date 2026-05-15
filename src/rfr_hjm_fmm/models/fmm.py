from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from rfr_hjm_fmm.utils import assert_strictly_increasing
from rfr_hjm_fmm.volatility import gamma_linear, sigma_parametric


@dataclass
class FMMPath:
    """
    Simulated generalized FMM extended-rate path.

    Attributes
    ----------
    times : np.ndarray
        Simulation times.
    rates : np.ndarray
        Matrix with shape (n_times, n_periods). Row k contains R_j(times[k]).
    """

    times: np.ndarray
    rates: np.ndarray


@dataclass
class GeneralizedFMMModel:
    """
    Generalized Forward Market Model scaffold for extended rates.

    This implements the Section 3.4 rate dynamics from the paper at the
    extended-rate level. It does not yet include the HJM completion, pathwise
    bond-price reconstruction, bank account, or Monte Carlo aggregation.

    The effective volatility used in drift and diffusion is
    sigma_parametric(t, start, end, R_j(0)), which already includes the
    paper's linear decay gamma_j(t).
    """

    period_starts: list[float]
    period_ends: list[float]
    accruals: list[float]
    initial_rates: list[float]
    correlation: np.ndarray | None = None
    a0: float = 0.001
    a1: float = 0.10

    def __post_init__(self) -> None:
        n_periods = len(self.period_ends)
        if n_periods == 0:
            raise ValueError("period_ends must not be empty")
        if len(self.period_starts) != n_periods:
            raise ValueError("period_starts must match period_ends")
        if len(self.accruals) != n_periods:
            raise ValueError("accruals must match period_ends")
        if len(self.initial_rates) != n_periods:
            raise ValueError("initial_rates must match period_ends")

        assert_strictly_increasing(self.period_ends, name="period_ends")

        for start, end in zip(self.period_starts, self.period_ends):
            if end <= start:
                raise ValueError("each period end must be greater than its start")
        for tau in self.accruals:
            if tau <= 0.0:
                raise ValueError("all accruals must be positive")
        for rate in self.initial_rates:
            if rate <= -1.0:
                raise ValueError("initial rates must be greater than -100%")

        if self.a0 < 0.0:
            raise ValueError("a0 must be non-negative")
        if self.a1 < 0.0:
            raise ValueError("a1 must be non-negative")

        if self.correlation is None:
            self.correlation = np.eye(n_periods)
        else:
            self.correlation = np.asarray(self.correlation, dtype=float)

        if self.correlation.shape != (n_periods, n_periods):
            raise ValueError("correlation must have shape (n_periods, n_periods)")
        if not np.allclose(self.correlation, self.correlation.T):
            raise ValueError("correlation must be symmetric")
        if not np.allclose(np.diag(self.correlation), np.ones(n_periods)):
            raise ValueError("correlation diagonal must be one")

        try:
            np.linalg.cholesky(self.correlation)
        except np.linalg.LinAlgError as exc:
            raise ValueError("correlation must be positive definite") from exc

    @property
    def n_periods(self) -> int:
        return len(self.period_ends)

    def gamma_vector(self, t: float) -> np.ndarray:
        """
        Return the linear volatility decay for every accrual period.
        """
        return np.array(
            [
                gamma_linear(t, start, end)
                for start, end in zip(self.period_starts, self.period_ends)
            ],
            dtype=float,
        )

    def effective_volatility(self, t: float) -> np.ndarray:
        """
        Return sigma_j(t) including the linear decay gamma_j(t).
        """
        return np.array(
            [
                sigma_parametric(t, start, end, r0, self.a0, self.a1)
                for start, end, r0 in zip(
                    self.period_starts,
                    self.period_ends,
                    self.initial_rates,
                )
            ],
            dtype=float,
        )

    def eta_index(self, t: float) -> int:
        """
        Return the first non-matured period index at time t.
        """
        for idx, end in enumerate(self.period_ends):
            if end >= t:
                return idx
        return self.n_periods

    def drift(self, t: float, rates: np.ndarray) -> np.ndarray:
        """
        Risk-neutral generalized FMM drift for all extended rates.
        """
        rates = self._as_rate_vector(rates)
        vols = self.effective_volatility(t)
        eta = self.eta_index(t)
        drift = np.zeros(self.n_periods, dtype=float)

        for j in range(eta, self.n_periods):
            if vols[j] == 0.0:
                continue

            acc = 0.0
            for i in range(eta, j + 1):
                denominator = 1.0 + self.accruals[i] * rates[i]
                if denominator <= 0.0:
                    raise ValueError("1 + tau_i * R_i(t) must be positive")
                acc += (
                    self.correlation[i, j]
                    * self.accruals[i]
                    * vols[i]
                    / denominator
                )

            drift[j] = vols[j] * acc

        return drift

    def step(
        self,
        t: float,
        rates: np.ndarray,
        dt: float,
        rng: np.random.Generator,
    ) -> np.ndarray:
        """
        Advance the extended-rate vector one Euler step.
        """
        if dt <= 0.0:
            raise ValueError("dt must be positive")

        rates = self._as_rate_vector(rates)
        cholesky = np.linalg.cholesky(self.correlation)
        z = rng.standard_normal(self.n_periods)
        brownian_increment = cholesky @ z * np.sqrt(dt)
        vols = self.effective_volatility(t)

        next_rates = rates + self.drift(t, rates) * dt + vols * brownian_increment

        matured = np.array([t >= end for end in self.period_ends], dtype=bool)
        next_rates[matured] = rates[matured]
        return next_rates

    def simulate(self, times: list[float] | np.ndarray, seed: int | None = None) -> FMMPath:
        """
        Simulate one seeded generalized FMM path over the supplied time grid.
        """
        times_array = np.asarray(times, dtype=float)
        if times_array.ndim != 1:
            raise ValueError("times must be one-dimensional")
        if len(times_array) < 2:
            raise ValueError("times must contain at least two points")
        assert_strictly_increasing(times_array.tolist(), name="times")

        rng = np.random.default_rng(seed)
        rates = np.zeros((len(times_array), self.n_periods), dtype=float)
        rates[0, :] = np.asarray(self.initial_rates, dtype=float)

        for k in range(1, len(times_array)):
            dt = times_array[k] - times_array[k - 1]
            rates[k, :] = self.step(times_array[k - 1], rates[k - 1, :], dt, rng)

        return FMMPath(times=times_array, rates=rates)

    def _as_rate_vector(self, rates: np.ndarray) -> np.ndarray:
        rates = np.asarray(rates, dtype=float)
        if rates.shape != (self.n_periods,):
            raise ValueError("rates must have shape (n_periods,)")
        return rates
