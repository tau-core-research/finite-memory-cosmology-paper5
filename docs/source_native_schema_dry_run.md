# Source-Native Schema Dry Run

Status: SOURCE_NATIVE_SCHEMA_DRY_RUN_READY_PROXY_NOT_SOURCE_NATIVE.

This dry run writes the 200-bootstrap proxy route into a source-native-like schema without using canonical source-native filenames. It tests import mechanics only.

## Outputs

- Reconstruction dry run: `data/physical_nulls/backreaction_reproduction/source_native_schema_dry_run_reconstruction_vector.csv`
- Metadata dry run: `data/physical_nulls/backreaction_reproduction/source_native_schema_dry_run_selection_metadata.csv`
- Backreaction vector dry run: `data/physical_nulls/backreaction_reproduction/source_native_schema_dry_run_backreaction_vector.csv`
- Bootstrap dry run: `data/physical_nulls/backreaction_reproduction/source_native_schema_dry_run_backreaction_bootstrap_samples.csv`
- Covariance dry run: `data/physical_nulls/backreaction_reproduction/source_native_schema_dry_run_backreaction_covariance.csv`

## Boundary

These files are explicitly proxy dry-run artifacts. They do not authorize source-native scoring or measurement validation.
