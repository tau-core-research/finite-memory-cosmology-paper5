# Source-Native Derivative Pilot Uncertainty

Status: bootstrap uncertainty stress test ready; source-native uncertainty still missing.

This bootstrap perturbs public SN distance-proxy and radial BAO H_D-proxy training inputs using diagonal errors, refits the fixed polynomial pilot, and propagates the fixed backreaction formula. It is not the published symbolic-regression bootstrap.

## Outputs

- Bootstrap samples: `data/physical_nulls/backreaction_reproduction/source_native_derivative_pilot_bootstrap_omega_samples.csv`
- Omega covariance: `data/physical_nulls/backreaction_reproduction/source_native_derivative_pilot_omega_covariance.csv`
- Omega band: `data/physical_nulls/backreaction_reproduction/source_native_derivative_pilot_omega_band.csv`
- Summary: `evidence/source_native_derivative_pilot_uncertainty_summary.csv`
