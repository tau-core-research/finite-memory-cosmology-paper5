# Source-Split K2 Scoring Authorization

Status: authorization guard added; K2 scoring is blocked.

This is the final guard before any source-split K2/null scorecard can run. It
does not compute K2. It only checks whether all required upstream gates are open.

## Run

```text
python3 scripts/check_source_split_k2_scoring_authorization.py
```

It writes:

```text
evidence/source_split_k2_scoring_authorization.csv
```

## Required Gates

The guard requires:

- `SS_TRANSFORM`;
- `SS_K1_TARGET`;
- `SS_JOINT_COVARIANCE`;
- `SS_CANDIDATE_PATH_GUARD`;
- `SS_RECONSTRUCTION_FAMILY_EXPORT`;
- `SS_SIGN_RULE_PROMOTION`.

## Current Decision

The current decision is expected to be:

```text
K2ScoringAuthorized = False
AuthorizationDecision = BLOCKED
```

The primary next action is still to create a valid public reconstruction-family
candidate export before promoting the sign rule or scoring K2.

The compact blocker matrix is:

```text
evidence/source_split_blocker_matrix.csv
evidence/source_split_blocker_matrix_summary.csv
```

It aggregates the dashboard, handoff, and authorization blockers into one
operational table.
