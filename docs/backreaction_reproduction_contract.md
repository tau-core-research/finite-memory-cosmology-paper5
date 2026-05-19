# Backreaction Reproduction Contract

Status: formula and upstream input route identified; scoring blocked until the derivative reconstruction vector and covariance are available.

## Fixed Formula

`Omega_R + 3 Omega_Q = ((1+z)^2 / D) * (H_D_prime * D_prime / H_D + D_double_prime)`

The formula is implemented in `src/fmc/backreaction.py`. The implementation does not fit, smooth, digitize figures, or infer covariance.

## What Is Available

- Upstream BAO table rows extracted from arXiv:2604.05822: 10
- Pantheon+ local files available: True
- DESI DR1/DR2 local BAO mean/covariance files available: True

## What Is Still Missing

- `z,D,D_prime,D_double_prime,H_D,H_D_prime` on a source-native reconstruction grid.
- Source-native covariance or bootstrap samples for those reconstructed quantities.
- A declared mapping from the reconstructed backreaction vector into the locked A2/K2 preflight score vector.

## Claim Boundary

This contract does not authorize a backreaction-null rejection claim or measurement validation. Figure digitization remains fallback-only.

## Outputs

- BAO table: `data/physical_nulls/backreaction_reproduction/upstream_2604_05822_bao_radial_table.csv`
- Schema: `data/physical_nulls/backreaction_reproduction/backreaction_reconstruction_vector_schema.csv`
- Contract: `evidence/backreaction_reproduction_contract.csv`
- Readiness: `evidence/backreaction_reproduction_readiness.csv`
