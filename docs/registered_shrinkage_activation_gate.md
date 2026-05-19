# Registered Shrinkage Activation Gate

Status: future-preflight activation allowed; measurement validation blocked.

The registered-shrinkage parameter policy completed the template-level missing
pieces. This gate checks whether that route may now be activated for a future
preflight rerun.

Outputs:

- `evidence/registered_shrinkage_activation_gate.csv`;
- `evidence/registered_shrinkage_activation_summary.csv`.

## Gate Result

The gate reports:

```text
Checks: 8
PassedChecks: 6
PreflightBlockingChecks: 0
MeasurementBlockingChecks: 2
RegisteredShrinkagePreflightActivationAllowed: true
RegisteredShrinkageMeasurementValidationAllowed: false
AllowedRerunType: future_preflight_only
CurrentScorecardShouldRunNow: false
```

The route is therefore structurally ready for a future preflight rerun, but it
does not authorize a current scorecard and does not support measurement
validation.

## Remaining Measurement Blockers

The two measurement blockers are:

- `ACT_5_K2_VS_POLY_RESOLVED`: the K2-vs-polynomial issue is not fully resolved
  at the public-covariance level;
- `ACT_6_PUBLIC_MEASUREMENT_ROUTE_AVAILABLE`: no full public measurement route
  is available.

## Interpretation

This is progress, but a narrow kind of progress. The registered-shrinkage route
can now be used to design a future preflight scorecard without changing K2 or
K1. It cannot be used to claim measurement validation, and the current paper
should continue to describe it as a future measurement-gate route.

The future-preflight scorecard has now been run under this boundary. It should
be read as weakening evidence for the registered-shrinkage route: K2 improves
over K1/no-memory but does not beat `POLY_DEG2`.

The polynomial-control fairness audit records why this matters: the polynomial
control is not a physical explanation, but it is still a mandatory overfit-risk
blocker.
