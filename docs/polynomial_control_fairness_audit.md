# Polynomial Control Fairness Audit

Status: mandatory overfit-risk blocker; no measurement validation claim.

The registered-shrinkage future-preflight run leaves the main public benchmark
question unresolved: `K2_LOCKED_RHO4` improves over K1/no-memory, but
`POLY_DEG2` remains preferred under the registered shrinkage covariance.

This audit defines how polynomial controls should be interpreted.

Outputs:

- `evidence/polynomial_control_fairness_audit.csv`;
- `evidence/polynomial_control_fairness_summary.csv`.

## Decision

The polynomial controls are:

```text
PolynomialControlRole: mandatory_overfit_risk_control
PolynomialIsFairPhysicalNull: false
PolynomialCanBeDismissed: false
CurrentStatus: POLYNOMIAL_CONTROL_REMAINS_MEASUREMENT_BLOCKER
```

This means:

- they are not a standalone physical explanation;
- they are not enough to explain the result as a physical cosmology model;
- they cannot be dismissed, because they are preregistered controls and win
  some public-proxy tests;
- stronger public claims require K2 to be competitive against them under the
  same covariance and validation policy.

## Current Evidence

The audit records:

- registered-shrinkage in-sample: K2 does not beat the best polynomial;
- cross-validation: K2 beats the best polynomial in 5 of 6 comparison rows;
- support ladder: K2-vs-polynomial status is mixed conditional support.

## Interpretation

The polynomial objection is not a final falsification, because polynomial
dominance is not stable across all validation modes and routes. But it remains
a measurement blocker, because a public-benchmark route still exists where
polynomial controls outperform the locked K2 response.

The next stronger benchmark must either:

- show locked K2 competitiveness against polynomial controls under a public
  covariance route; or
- register a more specific physical null-comparator hierarchy before making
  stronger claims.

That hierarchy now exists. Its immediate result is that the physical null layer
is incomplete: backreaction-only and Dyer-Roeder/optical controls are still
missing.
