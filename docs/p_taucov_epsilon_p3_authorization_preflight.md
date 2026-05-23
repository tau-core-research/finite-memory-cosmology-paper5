# P-TauCov Epsilon-P3 Authorization Preflight

Status: `BLOCKED_NO_SCORING_AUTHORIZATION`.

This artifact checks whether epsilon-P3 P-TauCov empirical scoring can be
authorized.

## Result

```text
ChecksPassed: 3/6
OpenRequiredChecks: 3
PTauCovScoringAuthorized: false
```

Blocking items:

```text
scorecard_script_frozen
observed_residual_input_contract_frozen
final_authorization_manifest_ready
```

## Interpretation

The theoretical/protocol side is now much cleaner than before:

- epsilon-P3 specificity candidate is frozen;
- branch support is frozen from `delta_C_tau` only;
- fold/null/covariance/df/survival policies are frozen.

However, empirical scoring remains blocked until the scorecard script and the
observed residual/covariance input contract are frozen by hash.

Allowed statement:

```text
P-TauCov epsilon-P3 has passed pre-scoring protocol readiness up to the
scorecard/input-contract gate.
```

Forbidden statement:

```text
P-TauCov epsilon-P3 has produced an empirical Tau signal.
```
