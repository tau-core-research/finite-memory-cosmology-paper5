# BAO K1 Response Policy

Status: pre-K2 blocker policy.

The finite-memory operator cannot be fairly scored on public BAO residuals until
the no-memory response is defined in the same target space. The BAO residual
work so far has produced several baseline and null objects, but not yet a
locked K1 response for K2 scoring.

## Registry

Machine-readable registry:

```text
evidence/bao_k1_response_registry.csv
```

Readiness output:

```text
evidence/bao_k1_response_readiness.csv
```

## Current Interpretation

- `BAO_K1_ZERO_RESIDUAL` is a null comparator, not a finite-memory baseline.
- `BAO_K1_CONSTANT_OFFSET` is a same-data diagnostic control.
- `BAO_K1_PUBLIC_BESTFIT_RESIDUAL` is same-data and too permissive.
- `BAO_K1_CMB_ONLY_RESIDUAL` is more independent but carries BAO tension.
- `BAO_K1_LOCKED_RESPONSE_TARGET` is required before K2 scoring.

## Eligibility Rule

A BAO K1 response becomes eligible for K2 scoring only if:

- it is defined in the BAO log-residual target space;
- it is coordinate-native or likelihood-native;
- it is not fitted in this note;
- it is not only a same-data posterior maximum or scale offset;
- its amplitude normalization is frozen before K2 scoring;
- the same covariance is used by K2 and all null comparators.

## Next Step

Define the locked BAO K1 response target or explicitly decide that BAO cannot
yet host a K2 measurement gate. Until then, K2 scoring remains blocked.

The locked-response planning layer is:

```text
docs/bao_k1_locked_response_plan.md
evidence/bao_k1_amplitude_policy.csv
evidence/bao_k1_locked_response_registry.csv
evidence/bao_k1_locked_response_readiness.csv
```

The current candidate is `BAO_K1_CMB_ONLY_UNIT_COVNORM_CANDIDATE`, but it is
not selected and has no attached null scorecard. It is therefore not authorized
for K2 scoring.
