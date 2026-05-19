# Backreaction Formula Engine

Status: algebra validated; source-native scoring input still required.

The engine computes `Omega_R + 3 Omega_Q` from an externally supplied reconstruction vector. It does not reconstruct the vector, fit amplitudes, or digitize figures.

## Inputs

- Required vector: `data/physical_nulls/backreaction_reproduction/source_native_backreaction_reconstruction_vector.csv`
- Required covariance: `data/physical_nulls/backreaction_reproduction/source_native_backreaction_reconstruction_covariance.csv`
- Template: `data/physical_nulls/backreaction_reproduction/source_native_backreaction_reconstruction_vector_template.csv`

## Current Readiness

- Algebra smoke test passed: True
- Source-native vector exists: False
- Source-native covariance exists: False
- Allowed for backreaction scoring now: False

Measurement validation remains closed.
