# HJM-FMM Architecture

This diagram separates the mathematical components of the paper and shows how
they should become code modules.

```mermaid
flowchart TB
    subgraph MarketInputs[Market Inputs]
        Curve[OIS curve P(0,T)]
        Schedule[Accrual schedule T_j and tau_j]
        Params[Volatility and correlation parameters]
    end

    subgraph ExtendedRates[Extended Rate Layer]
        RDef[R_j(t) = P(t,T_j-1)/P(t,T_j) - 1 over tau_j]
        Gamma[gamma_j(t)]
        Sigma[sigma_j(t)]
        Drift[FMM drift]
        Brownian[Correlated Brownian shocks]
        RSim[Simulated R_j(t)]
    end

    subgraph HJMCompletion[HJM Completion Layer]
        SepVol[Separable volatility zeta_k(t) g_k(T)]
        X[X(t)]
        Y[Y(t)]
        Forward[f(t,T)]
        Bond[P(t,T)]
        Short[r(t)]
        Bank[B(t)]
    end

    subgraph Valuation[Valuation Layer]
        FRN[FRN value]
        Swap[Payer swap value]
        Par[Par swap rate]
        DV01[DV01]
        Convexity[Convexity]
        MC[Monte Carlo aggregation]
    end

    Curve --> RDef
    Schedule --> RDef
    Params --> Gamma
    Params --> Sigma
    Params --> Brownian

    RDef --> Drift
    Gamma --> Drift
    Sigma --> Drift
    Brownian --> RSim
    Drift --> RSim

    Curve --> SepVol
    SepVol --> X
    SepVol --> Y
    X --> Forward
    Y --> Forward
    Forward --> Bond
    Forward --> Short
    Short --> Bank

    RSim --> FRN
    Bond --> FRN
    Bank --> FRN
    RSim --> Swap
    Bond --> Swap
    Swap --> Par
    FRN --> DV01
    Swap --> DV01
    FRN --> Convexity
    Swap --> Convexity
    FRN --> MC
    Swap --> MC
```

## Layer Responsibilities

- Extended Rate Layer: implements Section 3.4 of the paper. The current
  `GeneralizedFMMModel` starts this layer with stochastic extended-rate paths.
- HJM Completion Layer: implements the Section 3.5 scaffold. It now provides
  state evolution and pathwise `P(t,T)`, `r(t)`, and `B(t)`, but still needs to
  be coupled to FMM paths and valuation.
- Valuation Layer: uses `R_j(t)` and `P(t,T)` together. The current pricers use
  deterministic discounting and must later be generalized to pathwise inputs.

## Implementation Boundary

The FMM layer should not price instruments by itself. It produces extended-rate
paths. Pricing becomes paper-consistent when the valuation layer consumes both
FMM extended rates and HJM pathwise discount factors.
