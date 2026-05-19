# Source-Native Backreaction Export Validation

Status: validation gate ready.

This script validates future source-native reconstruction exports and computes the fixed-formula `Omega_R + 3 Omega_Q` vector when possible. It does not alter locked K2 or authorize measurement validation.

## Outputs

- Audit: `evidence/source_native_backreaction_export_validation.csv`
- Summary: `evidence/source_native_backreaction_export_validation_summary.csv`
- Backreaction vector, if valid: `data/physical_nulls/backreaction_reproduction/source_native_backreaction_vector.csv`
