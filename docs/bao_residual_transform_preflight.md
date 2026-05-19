# BAO Residual Transform Preflight

Status: diagnostic preflight, not measurement-gate scoring.

The first public residual transform is `T1_BAO_DISTANCE_RATIO_RESIDUAL`. It
uses the local DESI BAO mean/covariance files and maps the raw observables into
log residuals against a fixed audit baseline:

```text
residual = log(observed / audit_prediction)
```

The audit baseline is:

```text
baseline_id = AUDIT_FLAT_LCDM_BAO_V0
H0 = 70.0
omega_m = 0.3
rd_mpc = 147.0
```

This baseline is not fitted in this note and is not a likelihood-native
cosmology result. Its role is to make the residual-transform plumbing explicit
and reproducible before a public covariance-aware benchmark is attempted.

## Outputs

```text
evidence/bao_residual_transform_preflight.csv
evidence/bao_residual_transform_summary.csv
evidence/bao_residual_transform_covariance.csv
```

The covariance is propagated by the diagonal Jacobian of the log residual with
respect to the observed BAO mean vector:

```text
C_residual = J C_observed J^T
J_ii = 1 / observed_i
```

## Boundary

This transform is still blocked from measurement-gate scoring because:

- the baseline is audit-fiducial, not likelihood-native;
- no coordinate-native K1 baseline has been exported;
- null comparators have not yet been evaluated on this residual vector;
- the finite-memory diagnostic mapping from this residual vector to a locked
  K2 comparison has not been registered.

The next step is a BAO residual null benchmark using the same residual vector
and propagated covariance, without changing the locked K2 kernel or allowing
`rho > 4`.

## Null Benchmark Preflight

The T1 null benchmark is:

```text
scripts/run_bao_residual_null_benchmark.py
```

Outputs:

```text
evidence/bao_residual_null_benchmark.csv
evidence/bao_residual_null_scorecard.csv
```

Current preflight finding: under the audit-fiducial baseline, a simple
`CONSTANT_OFFSET` control is the best AIC model for both DESI DR1 and DESI DR2
across the tested audit coordinates. This indicates that the audit baseline
leaves a global BAO residual offset. It is not evidence for a finite-memory
effect and does not open the measurement gate.

The next step is therefore not a K2 comparison. It is a likelihood-native or
coordinate-native BAO baseline export, so that the residual vector is not
dominated by an arbitrary audit-baseline offset.

## Baseline Offset Diagnosis

The constant-offset mode is decomposed by:

```text
scripts/diagnose_bao_baseline_offset.py
```

Output:

```text
evidence/bao_baseline_offset_diagnosis.csv
```

The diagnosis shows an approximately 1.5 percent global observed-over-audit
scale factor in both DESI DR1 and DESI DR2. If absorbed into the audit BAO
sound-horizon scale, this corresponds to an effective `rd` of about 144.8 Mpc
instead of the audit value 147.0 Mpc.

This is a baseline-scale calibration warning. It is not a finite-memory signal.
It supports the decision to keep the measurement gate closed until a
likelihood-native or coordinate-native BAO baseline is exported.

The baseline export policy is documented in:

```text
docs/bao_baseline_export_plan.md
evidence/bao_baseline_export_registry.csv
evidence/bao_baseline_export_readiness.csv
```

The same-data `rd` offset sensitivity confirms the interpretation: after
absorbing the measured global scale offset into `rd`, the zero-residual score
falls to the same level as the constant-offset control. This is a calibration
sensitivity check only and remains blocked from measurement-gate scoring.
