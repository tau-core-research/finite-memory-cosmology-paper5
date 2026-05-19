# Source-Split Export Task Queue

Status: TQ1-TQ4 and candidate export validation completed; K2 scoring remains
blocked.

The source-split gate dashboard shows that the input/null side is open, but the
core scoring gates are closed. This queue turns those closed gates into an
ordered export plan.

## Outputs

Run:

```text
python3 scripts/build_source_split_export_task_queue.py
```

It writes:

```text
evidence/source_split_export_task_queue.csv
evidence/source_split_export_task_queue_summary.csv
```

## Current Queue

The completed preflight task is:

```text
TQ1_COORDINATE_NATIVE_TRANSFORM
```

It must produce:

```text
evidence/source_split_coordinate_native_target.csv
```

This artifact maps public SN and BAO rows into one declared coordinate-native
source-split target without scoring K2.

The completed K1/control preflight task is:

```text
TQ2_COORDINATE_NATIVE_K1
```

It writes:

```text
evidence/source_split_k1_coordinate_native_target.csv
```

The completed covariance-policy preflight task is:

```text
TQ3_JOINT_COVARIANCE
```

It writes:

```text
evidence/source_split_joint_covariance_policy.csv
```

The completed branch-sign preflight task is:

```text
TQ4_PUBLIC_SIGN_FAMILY
```

It writes:

```text
evidence/source_split_public_sign_family.csv
```

The next required upgrade is:

```text
TQ4_RECONSTRUCTION_FAMILY_UPGRADE
```

The upgrade contract is:

```text
evidence/source_split_reconstruction_family_upgrade_contract.csv
```

It records the missing scoring-grade reconstruction-family responses and
family-level sign-stability rule. It does not open K2 scoring.

The source-readiness check for this upgrade is:

```text
python3 scripts/check_source_split_reconstruction_family_sources.py
```

It writes:

```text
evidence/source_split_reconstruction_family_source_readiness.csv
```

The current readiness table confirms that the public branch-sign preflight is
row-aligned and coordinate-native, but it is still branch-sign only. The missing
object is `RF_PUBLIC_SOURCE_SPLIT_RECONSTRUCTION_FAMILIES`: exported public
reconstruction-family responses plus a declared family-level sign-stability
rule on the same coordinate-native rows.

The exact export schema for that missing object is:

```text
evidence/source_split_reconstruction_family_export_schema.csv
evidence/source_split_reconstruction_family_export_template.csv
```

The validator currently writes:

```text
evidence/source_split_reconstruction_family_export_validation.csv
```

The compact dashboard now includes these later blocker gates as well:

```text
SS_RECONSTRUCTION_FAMILY_EXPORT
SS_RECONSTRUCTION_FAMILY_PREVIEW
SS_SIGN_RULE_PROMOTION
```

with the candidate export now validated and remaining upstream gates still
closed.

The task queue now tracks the same later gates:

```text
TQ4A_CANDIDATE_EXPORT_SCHEMA
TQ4B_CANDIDATE_EXPORT_PREVIEW
TQ4C_SIGN_RULE_PROMOTION
TQ5_LOCKED_K2_SCORECARD
```

`TQ4A` and `TQ4B` are completed preflight/schema tasks. The real candidate
export now exists and validates cleanly, so `TQ4C` can be treated as promoted
for the current artifact chain.

The candidate-family plan for the missing response table is:

```text
evidence/source_split_reconstruction_family_candidate_plan.csv
evidence/source_split_reconstruction_family_candidate_summary.csv
```

It identifies the SN residual branch and BAO residual branch as the first
public-input candidates to export into the required schema. Both remain blocked
until the response rows exist.

The non-scoring response preview is:

```text
evidence/source_split_reconstruction_family_response_preview.csv
evidence/source_split_reconstruction_family_response_preview_summary.csv
```

It shows that the existing branch rows can be represented in the frozen schema,
but it is not the candidate export and does not open `TQ5_LOCKED_K2_SCORECARD`.

The downstream blocked task is:

- `TQ5_LOCKED_K2_SCORECARD`.

The final authorization guard is:

```text
python3 scripts/check_source_split_k2_scoring_authorization.py
```

It writes:

```text
evidence/source_split_k2_scoring_authorization.csv
```

The candidate-export handoff is:

```text
python3 scripts/build_source_split_candidate_export_handoff.py
```

It writes:

```text
evidence/source_split_candidate_export_handoff_manifest.csv
evidence/source_split_candidate_export_handoff_summary.csv
```

It records the declared candidate path and the exact validation order. It does
not create the candidate export.

The branch-level handoff rows feeding that future export are:

```text
python3 scripts/build_source_split_sn_branch_export_handoff.py
python3 scripts/build_source_split_bao_branch_export_handoff.py
```

They write:

```text
evidence/source_split_sn_branch_export_handoff.csv
evidence/source_split_sn_branch_export_handoff_summary.csv
evidence/source_split_bao_branch_export_handoff.csv
evidence/source_split_bao_branch_export_handoff_summary.csv
```

Both branches currently have eight ready rows and no missing rows, and both are
now written to the real candidate export.

The candidate path guard is:

```text
python3 scripts/check_source_split_candidate_path_guard.py
```

It writes:

```text
evidence/source_split_candidate_path_guard.csv
```

It blocks accidental promotion if the real candidate file is missing or if it
is merely a copy of the non-scoring preview.

The queue explicitly keeps `TQ5_LOCKED_K2_SCORECARD` blocked until the required
K1, covariance, transform, sign-family, and final authorization gates are
complete.
