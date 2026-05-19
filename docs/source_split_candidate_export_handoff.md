# Source-Split Candidate Export Handoff

Status: candidate export created and validated; K2 scoring remains blocked by
remaining upstream gates.

This handoff describes the data object needed by the source-split measurement
gate. The candidate export now exists, but this does not open K2 scoring.

## Run

```text
python3 scripts/build_source_split_candidate_export_handoff.py
```

It writes:

```text
evidence/source_split_candidate_export_handoff_manifest.csv
evidence/source_split_candidate_export_handoff_summary.csv
```

## Candidate Path

The required future export path is:

```text
data/reconstruction_families/source_split_reconstruction_family_responses.csv
```

The current non-scoring preview lives under `evidence/` and must not be treated
as the candidate export. The real candidate file now lives under `data/`.

## Required Branches

The first candidate export must include at least:

- `RFAM_SN_RESIDUAL_BRANCH`;
- `RFAM_BAO_RESIDUAL_BRANCH`.

Each family must cover every usable coordinate-native target row.

The SN branch row-level handoff is:

```text
python3 scripts/build_source_split_sn_branch_export_handoff.py
```

It writes:

```text
evidence/source_split_sn_branch_export_handoff.csv
evidence/source_split_sn_branch_export_handoff_summary.csv
```

The current SN handoff has eight ready rows and no missing rows. These rows are
now included in the real candidate export.

The BAO branch row-level handoff is:

```text
python3 scripts/build_source_split_bao_branch_export_handoff.py
```

It writes:

```text
evidence/source_split_bao_branch_export_handoff.csv
evidence/source_split_bao_branch_export_handoff_summary.csv
```

The current BAO handoff has eight ready rows and no missing rows. These rows
are now included in the real candidate export.

## Validation Order

After the candidate file exists, run:

```text
python3 scripts/check_source_split_candidate_path_guard.py
python3 scripts/validate_source_split_reconstruction_family_export.py
python3 scripts/check_source_split_sign_rule_promotion.py
python3 scripts/build_source_split_gate_dashboard.py
python3 scripts/check_source_split_k2_scoring_authorization.py
```

The candidate export validation is clean, but K2 scoring remains blocked unless
the final authorization output returns `AUTHORIZED`.

## Blocker Matrix

For a compact view of the remaining blockers, run:

```text
python3 scripts/build_source_split_blocker_matrix.py
```

It writes:

```text
evidence/source_split_blocker_matrix.csv
evidence/source_split_blocker_matrix_summary.csv
```

The candidate-export blocker is resolved. The expected remaining blockers are
the transform, K1, covariance, and sign-family gates.
