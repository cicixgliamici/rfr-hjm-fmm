# Validation Stack

The project uses two complementary validation tools:

- Pydantic for boundary validation.
- icontract for internal mathematical contracts.

They solve different problems and should not be treated as substitutes.

## Why Pydantic

Pydantic validates external inputs before they enter the numerical core:

- experiment configuration;
- JSON/YAML-like payloads;
- notebook and CLI inputs;
- curve, instrument, schedule, and model specifications.

Benefits:

- structured error messages for invalid user input;
- strict schemas with forbidden extra fields;
- type coercion where useful, strict validation where required;
- conversion from validated specs into core objects such as `DiscountCurve`,
  `FloatingRateNote`, `PayerSwap`, and `GeneralizedFMMModel`;
- a clean place to add paper-experiment configuration later.

Current implementation:

```text
rfr_hjm_fmm.validation.DiscountCurveSpec
rfr_hjm_fmm.validation.RegularScheduleSpec
rfr_hjm_fmm.validation.FloatingRateNoteSpec
rfr_hjm_fmm.validation.PayerSwapSpec
rfr_hjm_fmm.validation.FMMModelSpec
```

Use Pydantic when data enters the library from the outside.

## Why icontract

icontract validates assumptions inside the numerical code:

- function postconditions;
- method preconditions where they do not conflict with existing `ValueError`
  validation;
- class invariants later, once model classes stabilize.

Benefits:

- contracts live next to the formula they protect;
- violations are explicit and reviewable;
- contracts document mathematical expectations in executable form;
- postconditions catch impossible numerical states even when inputs came from
  internal code rather than Pydantic specs;
- the style maps naturally to JML-like `requires`, `ensures`, and `invariant`.

Current contracts:

```text
DiscountCurve.forward_discount -> result > 0
gamma_linear -> 0 <= result <= 1
MarkovianHJMModel.bond_price -> result > 0
```

Use icontract when a mathematical property must hold for every implementation
path, not just for external inputs.

## Boundary Between The Two

Pydantic should validate shape and domain of input data:

```text
curve times are increasing
discount factors are positive
correlation matrix is positive definite
payment dates and accruals have matching lengths
```

icontract should validate mathematical consequences:

```text
forward discounts are positive
volatility decay stays in [0, 1]
bond prices are positive
P(t,t) equals 1
bank account stays positive
```

The numerical core should remain ordinary Python dataclasses and NumPy arrays.
That keeps simulation code fast, readable, and easy to test.

## Why Not Only One Library

Only Pydantic would validate inputs well, but it would not naturally express
postconditions on numerical methods.

Only icontract would express internal formulas well, but it would not provide
rich external schemas for experiment configuration and user-facing payloads.

Together, they give the project a practical contract system:

```text
external data -> Pydantic specs -> core numerical objects -> icontract checks
```

## Policy

- Add Pydantic models for any new external configuration or reproducible
  experiment payload.
- Add icontract only to high-value mathematical methods.
- Avoid decorating every small helper; contracts should increase clarity.
- Prefer existing `ValueError` validation for user-facing invalid input.
- Use icontract postconditions to catch internal model inconsistencies.
- Add tests for every new schema and every nontrivial contract.
