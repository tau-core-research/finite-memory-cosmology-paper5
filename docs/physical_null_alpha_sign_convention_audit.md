# Physical Null Alpha Sign Convention Audit

Status: sign convention audited; no convention is promoted for scoring.

This audit checks the non-scoring Dyer-Roeder alpha response preview under two
explicit sign conventions:

- `AS_DECLARED_ALPHA_CLUMPINESS_SIGN`;
- `INVERTED_ALPHA_CLUMPINESS_SIGN`.

It compares preview signs to the current source-split response orientation
(`SN_standardized_minus_BAO_standardized`) only as metadata. It does not select a
physical-null convention by K2 performance and does not open measurement
scoring.

Outputs:

- `evidence/physical_null_alpha_sign_convention_audit.csv`;
- `evidence/physical_null_alpha_sign_convention_summary.csv`.

## Current Reading

For both full-coverage alpha candidates, the same pattern appears:

```text
AS_DECLARED_ALPHA_CLUMPINESS_SIGN:
  SignMatchFraction: 0.375
  SignStableMatchFraction: 0.600

INVERTED_ALPHA_CLUMPINESS_SIGN:
  SignMatchFraction: 0.625
  SignStableMatchFraction: 0.400
```

This is intentionally not promoted into a convention choice. The full-row and
sign-stable subsets point in different directions, so a future physical-null
scorecard must freeze the sign from external optical-response reasoning before
looking at model ranking.

## Boundary

Before a physical-null scorecard can use alpha-derived optical controls, the
sign convention must be frozen from external optical-response reasoning, and
covariance propagation must be attached. This audit is therefore a blocker
clarification, not a validation result.

The covariance-preview side of the same blocker is tracked in
`docs/physical_null_alpha_covariance_preview.md`.
The consolidated scoring guard is tracked in
`docs/physical_null_alpha_scoring_authorization.md`.
