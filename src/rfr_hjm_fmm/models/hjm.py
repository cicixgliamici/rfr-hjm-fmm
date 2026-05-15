from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
import math

import icontract
import numpy as np

from rfr_hjm_fmm.curve import DiscountCurve
from rfr_hjm_fmm.utils import assert_strictly_increasing


FactorFunction = Callable[[float], np.ndarray]


@dataclass
class HJMState:
    """
    Markovian HJM state at a simulation time.
    """

    time: float
    x: np.ndarray
    y: np.ndarray
    bank_account: float


@dataclass
class HJMPath:
    """
    Simulated Markovian HJM state path.
    """

    times: np.ndarray
    x: np.ndarray
    y: np.ndarray
    bank_account: np.ndarray

    def state_at(self, index: int) -> HJMState:
        return HJMState(
            time=float(self.times[index]),
            x=self.x[index].copy(),
            y=self.y[index].copy(),
            bank_account=float(self.bank_account[index]),
        )


@dataclass
class MarkovianHJMModel:
    """
    Markovian HJM completion scaffold with separable volatility.

    The model follows the paper's state representation:

        dX(t) = Y(t) g(t) dt + zeta(t) dW(t)
        dY(t) = zeta(t) zeta(t)^T dt

    and reconstructs, for t < T:

        P(t,T) = P(0,t,T)
                 exp(-G(t,T)^T X(t) - 0.5 G(t,T)^T Y(t) G(t,T)).

    This is the HJM completion layer only. Coupling to the FMM extended-rate
    path and full paper Monte Carlo workflow comes next.
    """

    curve: DiscountCurve
    g: FactorFunction
    zeta: FactorFunction
    n_factors: int
    integration_steps: int = 32

    def __post_init__(self) -> None:
        if self.n_factors <= 0:
            raise ValueError("n_factors must be positive")
        if self.integration_steps <= 0:
            raise ValueError("integration_steps must be positive")

        g0 = np.asarray(self.g(0.0), dtype=float)
        zeta0 = np.asarray(self.zeta(0.0), dtype=float)
        if g0.shape != (self.n_factors,):
            raise ValueError("g must return shape (n_factors,)")
        if zeta0.shape != (self.n_factors,):
            raise ValueError("zeta must return shape (n_factors,)")

    @classmethod
    def constant_one_factor(
        cls,
        curve: DiscountCurve,
        g_level: float = 1.0,
        zeta_level: float = 0.0,
        integration_steps: int = 32,
    ) -> "MarkovianHJMModel":
        """
        Build a one-factor model with constant g and zeta.
        """

        def g(_: float) -> np.ndarray:
            return np.array([g_level], dtype=float)

        def zeta(_: float) -> np.ndarray:
            return np.array([zeta_level], dtype=float)

        return cls(
            curve=curve,
            g=g,
            zeta=zeta,
            n_factors=1,
            integration_steps=integration_steps,
        )

    def initial_state(self) -> HJMState:
        return HJMState(
            time=0.0,
            x=np.zeros(self.n_factors, dtype=float),
            y=np.zeros((self.n_factors, self.n_factors), dtype=float),
            bank_account=1.0,
        )

    def integrated_g(self, t: float, maturity: float) -> np.ndarray:
        """
        Compute G(t,T) = integral_t^T g(u) du with trapezoidal integration.
        """
        if maturity < t:
            raise ValueError("maturity must be >= t")
        if maturity == t:
            return np.zeros(self.n_factors, dtype=float)

        grid = np.linspace(t, maturity, self.integration_steps + 1)
        values = np.array([self._factor_vector(self.g, u, "g") for u in grid])
        return np.trapezoid(values, grid, axis=0)

    def forward_rate(self, state: HJMState, maturity: float) -> float:
        """
        Reconstruct f(t,T) from the Markovian HJM state for t <= T.
        """
        if maturity < state.time:
            return self.initial_forward_rate(maturity)

        base = self.initial_forward_rate(maturity)
        g_t = self._factor_vector(self.g, maturity, "g")
        g_int = self.integrated_g(state.time, maturity)
        linear = float(g_t @ state.x)
        quadratic = float(g_t @ state.y @ g_int)
        return base + linear + quadratic

    def initial_forward_rate(self, maturity: float) -> float:
        """
        Estimate the initial instantaneous forward rate f(0,T).
        """
        if maturity < 0.0:
            raise ValueError("maturity must be non-negative")

        eps = 1e-5
        if maturity <= eps:
            return -math.log(self.curve.discount(eps)) / eps

        left = max(0.0, maturity - eps)
        right = maturity + eps
        log_left = math.log(self.curve.discount(left))
        log_right = math.log(self.curve.discount(right))
        return -(log_right - log_left) / (right - left)

    def short_rate(self, state: HJMState) -> float:
        """
        Return r(t) = f(t,t) from the current HJM state.
        """
        return self.forward_rate(state, state.time)

    @icontract.ensure(lambda result: result > 0.0, "bond price must be positive")
    def bond_price(self, state: HJMState, maturity: float) -> float:
        """
        Reconstruct P(t,T). For T <= t, use the bank-account interpretation.
        """
        if maturity < 0.0:
            raise ValueError("maturity must be non-negative")

        if maturity < state.time:
            return state.bank_account / self._bank_account_at_maturity(
                state,
                maturity,
            )

        if maturity == state.time:
            return 1.0

        forward_discount = self.curve.forward_discount(state.time, maturity)
        g_int = self.integrated_g(state.time, maturity)
        exponent = -float(g_int @ state.x) - 0.5 * float(g_int @ state.y @ g_int)
        return forward_discount * math.exp(exponent)

    def step(
        self,
        state: HJMState,
        dt: float,
        rng: np.random.Generator,
    ) -> HJMState:
        """
        Advance X, Y, and B one Euler step.
        """
        if dt <= 0.0:
            raise ValueError("dt must be positive")

        zeta_t = self._factor_vector(self.zeta, state.time, "zeta")
        g_t = self._factor_vector(self.g, state.time, "g")
        d_w = rng.standard_normal(self.n_factors) * math.sqrt(dt)

        x_next = state.x + (state.y @ g_t) * dt + zeta_t * d_w
        y_next = state.y + np.outer(zeta_t, zeta_t) * dt
        r_t = self.short_rate(state)
        bank_next = state.bank_account * math.exp(r_t * dt)

        return HJMState(
            time=state.time + dt,
            x=x_next,
            y=y_next,
            bank_account=bank_next,
        )

    def simulate(self, times: list[float] | np.ndarray, seed: int | None = None) -> HJMPath:
        """
        Simulate one seeded HJM state path over the supplied grid.
        """
        times_array = np.asarray(times, dtype=float)
        if times_array.ndim != 1:
            raise ValueError("times must be one-dimensional")
        if len(times_array) < 2:
            raise ValueError("times must contain at least two points")
        if times_array[0] != 0.0:
            raise ValueError("times must start at 0.0")
        assert_strictly_increasing(times_array.tolist(), name="times")

        rng = np.random.default_rng(seed)
        x = np.zeros((len(times_array), self.n_factors), dtype=float)
        y = np.zeros((len(times_array), self.n_factors, self.n_factors), dtype=float)
        bank_account = np.ones(len(times_array), dtype=float)

        state = self.initial_state()
        for k in range(1, len(times_array)):
            dt = times_array[k] - times_array[k - 1]
            state = self.step(state, dt, rng)
            x[k] = state.x
            y[k] = state.y
            bank_account[k] = state.bank_account

        return HJMPath(
            times=times_array,
            x=x,
            y=y,
            bank_account=bank_account,
        )

    def _factor_vector(
        self,
        fn: FactorFunction,
        t: float,
        name: str,
    ) -> np.ndarray:
        values = np.asarray(fn(t), dtype=float)
        if values.shape != (self.n_factors,):
            raise ValueError(f"{name} must return shape (n_factors,)")
        return values

    def _bank_account_at_maturity(self, state: HJMState, maturity: float) -> float:
        if maturity == state.time:
            return state.bank_account
        return 1.0 / self.curve.discount(maturity)
