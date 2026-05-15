# Validation Language

This project should grow with explicit mathematical contracts, similar in
spirit to JML: preconditions, postconditions, invariants, and model-level
properties that can be checked in tests and optionally at runtime.

The goal is not to recreate Java/JML in Python. The goal is to make financial
and numerical assumptions executable and reviewable.

## Contract Levels

### Level 1: Dataclass Invariants

Use `__post_init__` for local object invariants:

```text
requires:
  notional > 0
  payment_dates and accrual_fractions have the same length
  accrual_fractions are positive
  payment_dates are strictly increasing
```

Current status: partially implemented. Basic length and positivity checks
exist, but schedule ordering and positive accrual checks should be completed.

### Level 2: Function Preconditions

Use explicit validation at function boundaries:

```text
requires:
  t >= 0
  maturity >= t
  len(period_starts) == len(payment_dates)
  curve discount factors are positive
```

These should fail fast with clear `ValueError` messages.

### Level 3: Function Postconditions

For numerical finance functions, add checkable postconditions:

```text
ensures:
  discount(t) > 0
  forward_discount(t, t) == 1
  bond_price(state, state.time) == 1
  gamma_j(t) in [0, 1]
  Y(t) is symmetric positive semidefinite
```

Postconditions should first be enforced through tests. Runtime enforcement can
be enabled later for debug builds.

### Level 4: Model Properties

Use property-style tests for mathematical behavior:

```text
invariant:
  par swap value is approximately zero at its par rate
  positive FRN spread increases value
  matured FMM rates stay frozen
  zero-vol HJM bond price equals deterministic forward discount
  bank account stays positive
```

These are the closest analogue to JML behavioral specifications.

## Pydantic Boundary Layer

Pydantic is used for boundary validation: configuration files, API payloads,
notebook inputs, CLI inputs, and reproducible experiment specifications.

Current Pydantic models live under `rfr_hjm_fmm.validation`:

- `DiscountCurveSpec`
- `RegularScheduleSpec`
- `FloatingRateNoteSpec`
- `PayerSwapSpec`
- `FMMModelSpec`

These models validate external inputs and then build the existing core objects.
The numerical core can remain dataclass-based and NumPy-based, while Pydantic
guards the inputs before they enter the model.

Example:

```python
from rfr_hjm_fmm.validation import DiscountCurveSpec

spec = DiscountCurveSpec(
    times=[0.5, 1.0, 2.0],
    discounts=[0.99, 0.97, 0.94],
)
curve = spec.to_curve()
```

This gives us JML-like `requires` checks at the project boundary without
forcing every internal object to become a Pydantic model.

For the broader rationale, see `docs/validation_stack.md`.

## Proposed Contract Shape

For internal mathematical invariants, use a small contract layer only where it
adds clarity. The eventual API can look like this:

```python
from rfr_hjm_fmm.contracts import require, ensure

@require(lambda t, T: T >= t, "T must be >= t")
@ensure(lambda result: result > 0.0, "discount factor must be positive")
def discount_between(t: float, T: float) -> float:
    ...
```

For dataclasses and numerical objects, prefer named validation helpers:

```python
def validate_positive_accruals(accruals: list[float]) -> None:
    ...
```

This keeps production code readable while making the specification reusable in
tests. Pydantic handles input schemas; helpers/contracts handle internal model
invariants and postconditions.

The current runtime contract library is `icontract`. It is used for focused
postconditions such as positive forward discounts, bounded volatility decay,
and positive HJM bond prices.

## Near-Term Plan

1. Strengthen existing `__post_init__` checks for instruments and schedules.
2. Use Pydantic specs for boundary/config validation.
3. Add reusable internal validators for:
   - strictly increasing times;
   - positive numeric vectors;
   - matching vector lengths;
   - positive-definite correlation matrices;
   - symmetric positive-semidefinite HJM `Y` matrices.
4. Add a lightweight `contracts.py` only after the validation helpers settle.
5. Add property tests around financial invariants before adding Monte Carlo.
6. Keep runtime contracts cheap by default and move expensive checks to tests.

## Review Rule

Every new mathematical module should include:

- a docstring stating the paper equation or section it implements;
- explicit input validation;
- at least one numerical expected-value test;
- at least one invariant/property test;
- clear documentation of whether the implementation is exact, approximate, or
  a scaffold.
