# P-TauCov Clock/Family-Balanced Next Gate

Audit ID: `P_TAUCOV_CLOCK_FAMILY_BALANCED_NEXT_GATE_v1`

Status:

`P_TAUCOV_NEXT_GATE_DEFINED_NO_CANDIDATE_NO_SCORING`

## Purpose

The diagonal-orthogonal scorecard produced a positive raw alignment, but failed through clock inconsistency and family dominance. This document defines the next admissibility gate before any new candidate is built or scored.

The goal is not to rescue the failed candidate. The goal is to prevent the next route from inheriting the same hidden failure mode.

## Required Gates

| Gate | Requirement | Criterion |
|---|---|---|
| `G1` | parent_derived_support | support_or_weights_must_be_derived_from_delta_c_tau_or_parent_response_before_score_access |
| `G2` | clock_consistency | candidate_must_declare_clock_block_response_expectation_before_scoring |
| `G3` | family_balance | candidate_must_not_concentrate_positive_support_in_a_single_registered_family |
| `G4` | diagonal_orthogonality | diagonal_energy_must_be_zero_or_explicitly_forbidden_from_the_alignment_statistic |
| `G5` | null_reuse_discipline | same_null_classes_must_be_kept_or_predeclared_stronger_nulls_must_be_added_before_scoring |
| `G6` | forbidden_failure_tuning | the_previous_best_family_clock_cell_must_not_be_used_as_a_direct_template |
| `G7` | claim_boundary | no_survival_no_tau_validation_no_measurement_validation_until_frozen_scorecard_passes |

## Forbidden Move

The strongest observed family-by-clock cell from the failed scorecard cannot be used as a direct template for a new kernel.

That would turn the failure diagnostic into target-derived tuning.

## Allowed Next Work

The next legitimate work is one of the following:

- derive a clock-consistent support rule from the parent response object;
- derive a family-balanced support rule from the parent response object;
- define a stronger pre-score structural audit that must pass before any scorecard is authorized;
- explicitly close this path as a localized anomaly if no parent-derived balanced support rule exists.

## Claim Boundary

This artifact does not authorize scoring.

It authorizes only a pre-score design requirement:

> the next P-TauCov candidate must be clock-consistent and family-balanced before it can be scored.
