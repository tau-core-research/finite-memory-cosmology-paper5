# Whitened Standardized Branch Contrast

Status: executable preflight target convention; no measurement-validation claim.

This target implements `WHITENED_STANDARDIZED_BRANCH_CONTRAST_V1` by applying a declared public-covariance proxy whitening matrix to the standardized `SN - BAO` branch contrast.

The construction is score-independent: it does not choose a target because of the K2 score, does not change the locked A2/K2 kernel, and does not refit K1.

## Outputs

- Vector: `evidence/whitened_standardized_branch_contrast_vector.csv`
- Whitening matrix: `evidence/whitened_standardized_branch_contrast_matrix.csv`
- Scorecard: `evidence/whitened_standardized_branch_contrast_scorecard.csv`
- Summary: `evidence/whitened_standardized_branch_contrast_summary.csv`

## Boundary

The route is still preflight-only because SN-BAO cross-covariance is not yet provided as a full public joint product. The result may strengthen or weaken A2/K2, but it cannot validate the measurement claim by itself.
