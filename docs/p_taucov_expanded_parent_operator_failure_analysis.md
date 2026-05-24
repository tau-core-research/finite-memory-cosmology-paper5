# P-TauCov Expanded Parent-Operator Failure Analysis

Status: `P_TAUCOV_EXPANDED_PARENT_OPERATOR_FAILURE_LOCALIZED_NO_RESCUE`

This is a post-score failure analysis. It does not introduce a new
score, does not rescue the failed primary scorecard, and does not
authorize survival or Tau Core validation language.

## What Survived Locally

- primary OOS Delta NLL: `143.1393222976955`
- gates passed: `5/8`

The expanded object carries a real covariance-level improvement over
the diagonal baseline.

## What Failed

- strongest null: `GENERIC_RANDOM_SMOOTH_PSD`
- strongest null Delta NLL: `290.3908841108725`
- primary minus strongest null: `-147.251561813177`
- failed gates: `SURV-G5_BEATS_ALL_REQUIRED_NULLS;SURV-G6_NOT_SINGLE_FAMILY_OR_CONTEXT_DOMINATED;SURV-G7_ALPHA_STABLE`
- largest positive fold share: `0.7285013580725607`
- primary folds with alpha <= 0: `1`

The decisive failure is not a simple projection-null or morphology-null
duplication. The decisive failure is that a generic smooth PSD covariance
object is stronger than the declared expanded parent-operator object.

## Consequence

The next Tau-specific route should not be another covariance-shape
variant. It needs an additional parent-Hessian-specific restriction that
is not reproducible by generic smooth PSD covariance structure.

Recommended next gate:

`derive_non_smooth_parent_hessian_specific_constraint_before_any_new_scoring`
