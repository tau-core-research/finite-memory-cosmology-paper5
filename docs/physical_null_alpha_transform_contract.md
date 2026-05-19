# Physical Null Alpha Transform Contract

Status: transform preview defined; measurement scoring remains closed.

This contract defines the first source-derived optical physical-null transform
for provisional Dyer-Roeder smoothness rows. The transform is intentionally
simple and predeclared:

```text
response_i = (1 - alpha) * DYER_ROEDER_OPTICAL_UNIT_NORM_V1_i
```

The amplitude is therefore the source-reported clumpiness contrast, not a fit to
the current K2 residuals. The unit shape is the existing optical template
`unit_norm(centered[x^2])`.

Outputs:

- `evidence/physical_null_alpha_transform_policy.csv`;
- `evidence/physical_null_alpha_response_preview.csv`;
- `evidence/physical_null_alpha_transform_summary.csv`.

## Current Reading

The contract can produce response previews for the two full-coverage joint
Dyer-Roeder alpha rows. These previews are useful for checking signs, scale, and
uncertainty plumbing, but they are not scorecard inputs yet.

Before scoring, the branch still needs:

- a sign-convention audit against the source-split response definition;
- source-native covariance or a declared covariance propagation rule;
- a registered decision about whether optical alpha is a fair physical null or
  only a sensitivity control for the present benchmark.

The sign-convention audit is tracked in
`docs/physical_null_alpha_sign_convention_audit.md`. It reports both
as-declared and inverted signs, but promotes neither.

The covariance preview is tracked in
`docs/physical_null_alpha_covariance_preview.md`. It propagates alpha
uncertainty into diagonal and fixed exponential-correlation preview matrices,
but keeps all rows non-scoring.

The consolidated scoring guard is tracked in
`docs/physical_null_alpha_scoring_authorization.md`.

## Boundary

This contract does not change the locked K2 kernel, does not choose alpha by K2
performance, does not fit a physical-null amplitude, and does not validate the
finite-memory projection hypothesis.
