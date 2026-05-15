# Model Flow

This diagram shows the intended end-to-end implementation flow from the paper
to the codebase.

```mermaid
flowchart LR
    Paper[Paper framework] --> OIS[Initial OIS curve]
    OIS --> Zero[Zero rates z(T)]
    OIS --> DF[Initial discount factors P(0,T)]
    DF --> R0[Initial extended rates R_j(0)]

    R0 --> FMM[Generalized FMM dynamics]
    FMM --> RPath[Pathwise extended rates R_j(t)]
    FMM --> Gamma[Volatility decay gamma_j(t)]
    FMM --> Sigma[Parametric volatility sigma_j(t)]
    FMM --> Corr[Brownian drivers and correlation]

    RPath --> HJM[HJM completion]
    HJM --> PPath[Pathwise bond prices P(t,T)]
    HJM --> Short[Short rate r(t)]
    HJM --> Bank[Bank account B(t)]

    RPath --> Pricing[FRN and swap pricing]
    PPath --> Pricing
    Bank --> Pricing

    Pricing --> SinglePath[Single-path values]
    Pricing --> MC[Monte Carlo means and errors]
    Pricing --> Risk[DV01 and convexity]

    Risk --> PaperTable[Paper numerical table]
    MC --> PaperTable
```

## Current Implementation Status

- Implemented deterministic scaffold: `DiscountCurve`, deterministic
  `ExtendedRate`, FRN/swap pricing, par swap rate, DV01, and convexity.
- Implemented stochastic scaffold: generalized FMM drift, volatility decay,
  parametric volatility, correlation validation, seeded single-path simulation.
- Implemented HJM scaffold: `X(t)`, `Y(t)`, `G(t,T)`, `P(t,T)`, short-rate
  path, bank-account path, and seeded HJM state simulation.
- Missing: coupling between FMM and HJM paths, monthly paper simulation,
  Monte Carlo aggregation, and simulation-based risk table.

## Next Coding Target

The next mathematical block should couple the FMM and HJM layers. Pricing
should then consume pathwise `R_j(t)` from FMM and pathwise `P(t,T)` from HJM.
