# P-TauCov Parent-Hessian Residue Gate

Status: `P_TAUCOV_PARENT_HESSIAN_RESIDUE_GATE_DEFINED_NO_OBJECT_NO_SCORING`

This is a no-score gate packet. It does not define a new empirical
scorecard and does not rescue any failed candidate.

## Inputs From Previous Failures

- expanded parent-operator failure: `P_TAUCOV_EXPANDED_PARENT_OPERATOR_FAILURE_LOCALIZED_NO_RESCUE`
- parent-Hessian commutator status: `P_TAUCOV_PARENT_HESSIAN_COMMUTATOR_OBJECT_PREFLIGHT_FAIL_NO_SCORING`
- smooth PSD failure observed: `True`
- projection-null failure observed: `True`

The two failure modes are different and both matter:

1. the expanded parent-operator object was too reproducible by a generic
   smooth PSD covariance null;
2. the previous parent-Hessian commutator object was close enough to the
   projection-null direction to fail specificity.

## Gate Definition

A future candidate may approach empirical scoring only if it first declares
a target-blind parent-Hessian residue satisfying all gate rows in
`evidence/p_taucov_parent_hessian_residue_gate.csv`.

The intended object class is not another smooth covariance shape. It is a
parent-Hessian residue with non-smooth or spectrally localized structure,
projection-null exclusion, smooth-PSD exclusion, and balanced support
retention.

## Forbidden Claim

> The expanded P-TauCov object found a Tau Core signal.

## Allowed Claim

> The failed scorecards identify the next required Tau-specific gate: a
> parent-Hessian residue that is not representable as generic smooth PSD
> covariance and does not leak into projection-null structure.

## Next Allowed Artifact

`p_taucov_parent_hessian_residue_candidate_v1_no_score_preflight`
