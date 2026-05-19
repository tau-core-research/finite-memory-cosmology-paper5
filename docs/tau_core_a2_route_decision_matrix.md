# Tau Core A2 Route Decision Matrix

Status: route decision for locked A2 preflight only. Measurement validation remains closed.

## Decision

- Recommended next route: R3_BRANCH_SCATTER_SYSTEMATIC
- Current best supported route: BRANCH_SCATTER_DECLARED_PREFLIGHT
- Current preflight routes: 2
- Measurement-validation routes: 0
- Strongest allowed claim: locked A2 has independently calibrated preflight support through the branch-scatter/systematic bridge

## Routes

### R1_PUBLIC_FULL_COVARIANCE

- Status: BLOCKED
- Class: preferred_measurement_route
- Current preflight: False
- Measurement validation: False
- Primary blocker: full public likelihood-native covariance and cross-covariance route missing
- Next action: implement or import full likelihood-native public covariance transform before scorecard interpretation

### R2_REGISTERED_SHRINKAGE

- Status: FUTURE_PREFLIGHT_ONLY
- Class: future_preflight_public_proxy
- Current preflight: True
- Measurement validation: False
- Primary blocker: ACT_5_K2_VS_POLY_RESOLVED
- Next action: keep as registered sensitivity route; do not use as validation unless polynomial/public covariance blockers clear

### R3_BRANCH_SCATTER_SYSTEMATIC

- Status: INDEPENDENTLY_CALIBRATED_PREFLIGHT_SUPPORT
- Class: declared_preflight_bridge
- Current preflight: True
- Measurement validation: False
- Primary blocker: independent reconstruction-family calibration is preflight only; public full covariance still missing
- Next action: use this as calibrated preflight bridge; keep Phase II focused on full public covariance

### R4_FORBIDDEN_POST_HOC_ROUTE

- Status: FORBIDDEN
- Class: forbidden
- Current preflight: False
- Measurement validation: False
- Primary blocker: route selected or tuned after inspecting A2-vs-control score
- Next action: do not use
