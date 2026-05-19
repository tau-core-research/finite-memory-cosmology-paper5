# Joint Covariance Adjudication Audit

Status: FG_4 is executable at preflight level. Measurement validation remains closed.

## Summary

- Public routes where A2 improves over K1: 2/2
- Public routes where A2 beats polynomial controls: 0/2
- Branch bridge supportive against polynomial controls: True
- Measurement-grade routes: 0
- Primary blocker: public covariance routes remain polynomial-dominated; branch bridge is not measurement-grade.

## Route Decisions

### JCOV_PUBLIC_ZERO_CROSS_V1

- Class: public_proxy_preflight
- Adjudication: PUBLIC_ROUTE_SUPPORTIVE_VS_K1_POLY_BLOCKED
- Delta AIC A2-K1: -2.214884814818623
- Delta AIC A2-best polynomial: 5.032909767652857
- Finding: A2 improves over K1 under this public covariance proxy, but polynomial controls remain stronger.
- Next action: treat as K1-supportive but measurement-blocked; require likelihood-native transform and final null policy

### JCOV_PUBLIC_REGISTERED_SHRINKAGE_V1

- Class: registered_public_proxy_preflight
- Adjudication: PUBLIC_ROUTE_SUPPORTIVE_VS_K1_POLY_BLOCKED
- Delta AIC A2-K1: -2.2442322084424244
- Delta AIC A2-best polynomial: 5.053109286316316
- Finding: A2 improves over K1 under this public covariance proxy, but polynomial controls remain stronger.
- Next action: treat as K1-supportive but measurement-blocked; require likelihood-native transform and final null policy

### JCOV_PUBLIC_ROW_CROSS_RHO0_V1

- Class: cross_covariance_sensitivity_only
- Adjudication: SENSITIVITY_ONLY_NOT_MEASUREMENT
- Delta AIC A2-K1: -2.214884814818623
- Delta AIC A2-best polynomial: 5.032909767652857
- Finding: This route is a sensitivity/control route and cannot support measurement validation.
- Next action: use only to localize covariance sensitivity

### JCOV_BRANCH_SCATTER_BRIDGE_V1

- Class: calibrated_preflight_bridge
- Adjudication: PREFLIGHT_SUPPORTIVE_NOT_MEASUREMENT
- Delta AIC A2-K1: -3.7693086335735906
- Delta AIC A2-best polynomial: -206.30899405703624
- Finding: A2 is stronger than K1 and polynomial controls on this calibrated bridge, but the route is not a full public covariance route.
- Next action: use as calibrated preflight support only; replace or validate with full public covariance before any stronger interpretation

## Claim Boundary

This audit does not alter the locked A2 prediction, does not fit K1, does not allow rho > 4, and does not authorize measurement validation.
