# BAO K1 Locked Response Plan

Status: planning layer, not scoring authorization.

The missing object for BAO-side K2 scoring is:

```text
BAO_K1_LOCKED_RESPONSE_TARGET
```

This object is not yet available. The purpose of this plan is to define what it
would have to contain before K2 can be scored on public BAO residuals.

## Required Properties

The locked BAO K1 response target must:

- live in the BAO log-residual target space;
- declare its baseline bracket before scoring;
- use the same covariance metric as K2 and the null comparators;
- have an amplitude normalization fixed before looking at K2 scores;
- not be derived from same-data `rd` offset absorption;
- not be only the same-data DESI BAO posterior maximum;
- be reported together with zero residual, constant offset, polynomial, and
  independent-baseline null controls.

Machine-readable policy:

```text
evidence/bao_k1_amplitude_policy.csv
```

## Candidate Normalizations

These are candidate normalization policies, not selected rules:

- unit covariance norm: `K1^T C^-1 K1 = 1`;
- unit RMS residual over the BAO rows;
- unit high-depth residual budget;
- independent-baseline residual norm, using CMB-only baseline residuals.

The first selected policy must be frozen before any K2 score is evaluated.

## Current Decision

No BAO K1 response is currently eligible for K2 scoring. The safest next step
is to implement a readiness check that confirms this and lists the missing
normalization fields explicitly.

## Candidate Evaluation

The CMB-only unit-covariance-norm candidate is built by:

```text
scripts/build_bao_k1_candidate.py
```

and checked against simple nulls by:

```text
scripts/run_bao_k1_candidate_null_scorecard.py
```

Outputs:

```text
evidence/bao_k1_cmb_only_unit_covnorm_candidate.csv
evidence/bao_k1_cmb_only_unit_covnorm_summary.csv
evidence/bao_k1_candidate_null_scorecard.csv
```

Current result: the candidate can be normalized cleanly, but the zero-response
null is AIC-preferred after unit covariance normalization. This makes the
candidate too weak to select as the locked K1 response target at this stage.
