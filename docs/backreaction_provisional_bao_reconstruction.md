# Provisional BAO-Only Backreaction Reconstruction

Status: provisional sensitivity input, not source-native measurement calibration.

This reconstruction uses public DESI DR2 BAO `DM/rs` and `DH/rs` pairs. It fits simple polynomials to build `D`, `D_prime`, `D_double_prime`, `H_D`, and `H_D_prime`, then evaluates the fixed backreaction formula. It does not reproduce the Pantheon+ plus BAO symbolic-regression bootstrap pipeline from the source papers.

## Outputs

- Reconstruction vector: `data/physical_nulls/backreaction_reproduction/provisional_bao_backreaction_reconstruction_vector.csv`
- Reconstruction covariance: `data/physical_nulls/backreaction_reproduction/provisional_bao_backreaction_reconstruction_covariance.csv`
- Backreaction curve: `data/physical_nulls/backreaction_reproduction/provisional_bao_backreaction_omega_curve.csv`
- Backreaction covariance: `data/physical_nulls/backreaction_reproduction/provisional_bao_backreaction_omega_covariance.csv`
- Bootstrap preview: `data/physical_nulls/backreaction_reproduction/provisional_bao_backreaction_bootstrap_samples.csv`
- Summary: `evidence/backreaction_provisional_bao_reconstruction_summary.csv`

## Claim Boundary

Allowed for preflight sensitivity only. Not measurement validation, not a backreaction-null rejection, and not a replacement for source-native symbolic-regression reconstruction.
