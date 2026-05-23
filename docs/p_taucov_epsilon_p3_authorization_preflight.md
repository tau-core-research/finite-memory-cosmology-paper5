# P-TauCov Epsilon-P3 Authorization Preflight

Status: `BLOCKED_NO_SCORING_AUTHORIZATION`.

This artifact checks whether epsilon-P3 P-TauCov empirical scoring can be
authorized.

## Result

```text
ChecksPassed: 5/7
OpenRequiredChecks: 2
PTauCovScoringAuthorized: false
```

Blocking items:

```text
coordinate_bridge_frozen
final_authorization_manifest_ready
```

## Interpretation

The theoretical/protocol side is now much cleaner than before:

- epsilon-P3 specificity candidate is frozen;
- branch support is frozen from `delta_C_tau` only;
- fold/null/covariance/df/survival policies are frozen.

However, empirical scoring remains blocked until a target-blind coordinate
bridge maps the frozen Tau-coordinate support into the empirical family-clock
space without using target residuals or P5C gain patterns.

Allowed statement:

```text
P-TauCov epsilon-P3 has passed pre-scoring protocol readiness up to the
coordinate-bridge/final-authorization gate.
```

Forbidden statement:

```text
P-TauCov epsilon-P3 has produced an empirical Tau signal.
```
