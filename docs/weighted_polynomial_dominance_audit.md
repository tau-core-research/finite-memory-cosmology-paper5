# Weighted Polynomial Dominance Audit

Status: diagnostic audit; no measurement-validation claim.

This audit tests whether the weighted polynomial control remains stronger than locked K2 after row-level decomposition, small-sample AICc penalties, and simple out-of-sample checks.

## Outputs

- Row audit: `evidence/weighted_polynomial_dominance_row_audit.csv`
- Complexity audit: `evidence/weighted_polynomial_complexity_audit.csv`
- Out-of-sample audit: `evidence/weighted_polynomial_out_of_sample_audit.csv`
- Summary: `evidence/weighted_polynomial_dominance_summary.csv`

## Boundary

The audit does not change A2/K2, does not choose a polynomial penalty after inspecting the K2 score, and does not authorize a measurement claim.
