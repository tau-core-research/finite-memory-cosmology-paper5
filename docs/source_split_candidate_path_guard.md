# Source-Split Candidate Path Guard

Status: guard added; candidate path is currently absent.

This guard protects the real candidate-export path from accidental promotion of
the non-scoring preview.

## Run

```text
python3 scripts/check_source_split_candidate_path_guard.py
```

It writes:

```text
evidence/source_split_candidate_path_guard.csv
```

## Current Expected State

The expected current state is:

```text
CandidateExists = False
Status = CANDIDATE_MISSING_EXPECTED_BLOCK
AllowedForK2Scoring = False
```

If a candidate file appears and exactly matches the non-scoring preview, the
guard marks it as:

```text
BLOCKED_PREVIEW_COPY_DETECTED
```

The real candidate export must be a documented public reconstruction-family
response export, not a shortcut copy from `evidence/`.
