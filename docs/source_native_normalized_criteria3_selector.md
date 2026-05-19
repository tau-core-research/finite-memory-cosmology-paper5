# Source-Native Normalized Criteria-Set-3 Selector

Status: SOURCE_NATIVE_NORMALIZED_CRITERIA3_PRE_REGISTERED_NOT_MEASUREMENT_ACTIVE.

This document freezes a scale-aware selector for future source-native PySR bootstrap reruns. It is not retroactive measurement scoring.

## Formula

`score = loss / loss_constant + lambda_complexity * (complexity - 1) / n_eff`

where `loss_constant` is the best finite constant expression loss in the same hall of fame, `n_eff` is the route training row count, and `lambda_complexity = 1.0`.

## Smoke Audit

- Raw penalty-one selected constant: True
- Normalized selector selected constant: False
- Selected equation: `(x0 * 1.4965818) + -1.7322209`
- Selected score: 0.20638884814589986
- Selected original weighted MSE: 4.864081623592746

## Boundary

The selector does not change K2, does not refit K1, does not allow rho > 4, and does not authorize measurement validation. It may only be used after a frozen bootstrap rerun.
