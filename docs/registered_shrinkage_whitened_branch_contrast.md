# Registered Shrinkage Whitened Branch Contrast

Status: preflight covariance-route sensitivity; no measurement-validation claim.

This run applies the pre-registered shrinkage covariance route to the standardized SN-BAO branch contrast. It keeps the locked K2 kernel and frozen K1 baseline unchanged.

## Outputs

- Vector: `evidence/registered_shrinkage_whitened_branch_contrast_vector.csv`
- Covariance: `evidence/registered_shrinkage_whitened_branch_contrast_covariance.csv`
- Scorecard: `evidence/registered_shrinkage_whitened_branch_contrast_scorecard.csv`
- Summary: `evidence/registered_shrinkage_whitened_branch_contrast_summary.csv`

## Boundary

The route is useful for covariance sensitivity, but it is not a substitute for a public full SN-BAO joint covariance.
