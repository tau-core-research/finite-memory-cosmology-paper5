# Physical Null Alpha Covariance Preview

Status: covariance preview exported; measurement covariance remains missing.

This artifact propagates source-reported alpha uncertainty through the
non-scoring alpha-response preview. It exports two predeclared covariance
families:

- diagonal amplitude propagation;
- exponential correlation in source-split `x` with fixed length `0.35`.

Outputs:

- `evidence/physical_null_alpha_covariance_preview_policy.csv`;
- `evidence/physical_null_alpha_covariance_preview_matrix.csv`;
- `evidence/physical_null_alpha_covariance_preview_summary.csv`.

## Boundary

These matrices are plumbing and sensitivity-preview artifacts only. They do not
replace source-native covariance, do not authorize physical-null scoring, and do
not validate the finite-memory projection hypothesis. A measurement comparison
still requires a frozen sign convention and a source-native or explicitly
registered covariance propagation route.

The consolidated scoring guard is tracked in
`docs/physical_null_alpha_scoring_authorization.md`.
