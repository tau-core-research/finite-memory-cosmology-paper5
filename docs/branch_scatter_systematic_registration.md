# Branch-Scatter Systematic Registration

Status: declared preflight bridge only. This is not measurement validation.

## Summary

- Preflight route registered: True
- Measurement validation allowed: False
- Current status: BRANCH_SCATTER_REGISTERED_AS_PREFLIGHT_SYSTEMATIC_BRIDGE
- Strongest allowed claim: branch scatter is registered as a declared A2 preflight bridge
- Residual risk: branch scatter is not independent public full covariance and not measurement validation

## Rules

- K2 remains locked.
- rho remains bounded at 4.
- K1 is not refit.
- The route cannot be selected as a measurement route without independent covariance/systematic calibration.

### BS_REG_1_ROUTE_DECLARED

- Status: PASS
- Evidence: branch-scatter promotion gate allows preflight benchmark
- Interpretation: route can be used as declared preflight benchmark

### BS_REG_2_NOT_FULL_PUBLIC_COVARIANCE

- Status: PASS
- Evidence: branch scatter is explicitly not public full covariance
- Interpretation: claim level is capped at preflight bridge

### BS_REG_3_TWO_BRANCH_COVERAGE

- Status: PASS
- Evidence: rows with at least two branches=8/8
- Interpretation: branch scatter is available across the current scoring grid

### BS_REG_4_K2_ROUTE_COMPETITIVE

- Status: PASS
- Evidence: K2 best branch-scatter routes=5; route summary competitive=5
- Interpretation: locked A2 remains competitive under branch-scatter route variants

### BS_REG_5_NO_POST_HOC_KERNEL_CHANGE

- Status: PASS
- Evidence: uses locked K2_A2 = 2*K1*(1+4*x^3); no rho>4; no K1 refit
- Interpretation: route does not change the finite-memory prediction

### BS_REG_6_INDEPENDENT_SYSTEMATIC_PENDING

- Status: WARNING
- Evidence: branch scatter is not yet independently calibrated as systematic floor
- Interpretation: stronger interpretation requires independent systematic or public full covariance
