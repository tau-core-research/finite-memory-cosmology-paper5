# P-TauCov Parent-Action Freeze Plan

Status: `P_TAUCOV_PARENT_ACTION_FREEZE_PLAN_DECLARED_NO_SCORING`.

This document lists the artifacts that must be frozen before any
parent-action P-TauCov scorecard can be authorized.

## Freeze Steps

- `FREEZE_01_PRIMARY_SCORECARD_SCRIPT` -> `scripts/run_p_taucov_parent_action_scorecard.py` (done)
- `FREEZE_02_FOLD_POLICY` -> `evidence/p_taucov_parent_action_fold_policy.csv` (done)
- `FREEZE_03_NULL_COMPARATORS` -> `evidence/p_taucov_parent_action_null_comparators.csv` (open)
- `FREEZE_04_SURVIVAL_KILL_GATES` -> `evidence/p_taucov_parent_action_survival_kill_gates.csv` (open)
- `FREEZE_05_DF_COVARIANCE_POLICY` -> `evidence/p_taucov_parent_action_df_covariance_policy.csv` (open)
- `FREEZE_06_FINAL_MANIFEST` -> `evidence/p_taucov_parent_action_final_manifest.yaml` (open)

## Boundary

This is a planning packet only. It does not authorize scoring, does
not inspect target outcomes, and does not create a survival claim.
