# Formulas

This file separates formulas from the paper from formulas currently implemented
in the code. The current code is a deterministic subset of the target
HJM-FMM framework.

## Paper Formulas

### Overnight Rate Compounded In Arrears

Discrete overnight compounding over `[T_{j-1}, T_j]`:

```text
R(T_{j-1}, T_j) = (1 / tau_j) * (prod_i (1 + r_i delta_i) - 1)
```

Continuous-time approximation:

```text
R(T_{j-1}, T_j) = (1 / tau_j) * (exp(int_{T_{j-1}}^{T_j} r(u) du) - 1)
                = (1 / tau_j) * (B(T_j) / B(T_{j-1}) - 1)
```

Current status: missing. The code does not yet model overnight fixing paths or
the bank account `B(t)`.

### Extended Forward Rate

```text
R_j(t) = (1 / tau_j) * (P(t, T_{j-1}) / P(t, T_j) - 1)
```

Current status: partial. `ExtendedRate` implements this formula with
deterministic forward discount factors from the initial curve.

### Generalized FMM Dynamics

In the paper, the extended rates evolve stochastically with volatility decay:

```text
dR_j(t) =
    gamma_j(t) sigma_j(t)^T
    sum_{i=eta(t)}^j sigma_i(t) tau_i gamma_i(t) / (1 + tau_i R_i(t)) dt
    + gamma_j(t) sigma_j(t)^T dW(t)
```

The scalar/correlation notation in the paper is equivalent to specifying
correlated Brownian drivers for the extended rates.

Current status: partial. `GeneralizedFMMModel` implements the extended-rate
drift, correlated Brownian increments, Euler stepping, and seeded single-path
simulation. It does not yet connect the simulated rates to the HJM-completed
bond-price and bank-account processes.

### Volatility Decay And Parametric Volatility

Linear decay:

```text
gamma_j(t) = 1                         for t <= T_{j-1}
gamma_j(t) = (T_j - t) / (T_j-T_{j-1}) for T_{j-1} < t < T_j
gamma_j(t) = 0                         for t >= T_j
```

Parametric volatility:

```text
sigma_j(t) = (a0 + a1 R_j(0)) * gamma_j(t)
```

Current status: implemented for the current FMM scaffold. `volatility.py`
contains `gamma_linear` and `sigma_parametric`, and `models/fmm.py` uses them
for drift and diffusion.

### FMM-HJM Completion

Recursive bond-price relation from extended rates:

```text
P(t, T_j) = P(t, T_{j-1}) / (1 + tau_j R_j(t))
```

Markovian HJM state representation with separable volatility:

```text
f(t,T) = f(0,T) + g(T)^T X(t) + g(T)^T Y(t) G(t,T),  t < T

dX(t) = Y(t) g(t) dt + zeta(t) dW(t)
dY(t) = zeta(t) zeta(t)^T dt
```

Bond-price reconstruction:

```text
P(t,T) = P(0,t,T)
         * exp(-G(t,T)^T X(t) - 0.5 * G(t,T)^T Y(t) G(t,T))
```

Current status: partial. `MarkovianHJMModel` implements `X(t)`, `Y(t)`,
initial forward-rate reconstruction, pathwise `P(t,T)`, short-rate extraction,
bank-account stepping, and seeded HJM state simulation. It is not yet coupled
to the generalized FMM extended-rate paths or the pricing layer.

## Implemented Deterministic Subset

### Discount Factor

```text
P(0,T)
```

Implemented in `DiscountCurve` with log-linear interpolation on discount
factors.

### Continuous Zero Rate

```text
z(T) = -log(P(0,T)) / T
```

Implemented in `DiscountCurve.zero_rate`.

### Deterministic Forward Discount Factor

```text
P(t,T) = P(0,T) / P(0,t)
```

Implemented in `DiscountCurve.forward_discount`. This is a deterministic
approximation and not the full pathwise HJM-FMM bond-price process.

### FRN Price

Paper target:

```text
V_FRN(t) = N * sum_{j=eta(t)}^n tau_j P(t,T_j) (R_j(t) + s)
           + N P(t,T_n)
```

Current implementation:

```text
V_FRN(t) = N * sum_j tau_j P(0,T_j) (R_j(t) + s) + N P(0,T_n)
```

The current implementation discounts directly from the initial curve and skips
past payment dates. It does not yet use pathwise `P(t,T_j)`.

### Payer Swap Value

Paper target:

```text
V_swap(t) =
    sum_j tau_j P(t,T_j) R_j(t)
    - K sum_j tau'_j P(t,T'_j)
```

Current implementation:

```text
V_swap(t) =
    sum_j tau_j P(0,T_j) R_j(t)
    - K sum_j tau'_j P(0,T'_j)
```

The current implementation is the deterministic subset of the paper formula.

### Par Swap Rate

```text
S(t) =
    sum_j tau_j P(t,T_j) R_j(t)
    / sum_j tau'_j P(t,T'_j)
```

Current implementation uses the same ratio, but with deterministic initial
curve discounting.

### DV01 And Convexity

DV01:

```text
DV01(t) ~= (V(z - 1bp) - V(z + 1bp)) / 2
```

Convexity:

```text
Gamma(t) ~= (V(z + 1bp) - 2 V(z) + V(z - 1bp)) / (1bp)^2
```

Current status: implemented for deterministic bump-and-reprice. The full paper
workflow should rebuild the curve, initial extended rates, and simulated paths
under each bump.
