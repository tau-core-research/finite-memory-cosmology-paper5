# BAO Baseline Export Plan

Status: Phase II preflight.

The T1 BAO residual transform exposed a global scale offset under the audit
baseline. The next step is not to compare K2 against that residual directly,
but to define which BAO baselines are admissible for future measurement-gate
work.

## Registry

Machine-readable registry:

```text
evidence/bao_baseline_export_registry.csv
```

Current baseline states:

- `AUDIT_FLAT_LCDM_BAO_V0` is available for transform plumbing only.
- `AUDIT_RD_OFFSET_ABSORBED_V0` is a planned sensitivity check, not an evidence
  baseline, because it absorbs a scale offset measured from the same BAO data.
- `PUBLIC_LIKELIHOOD_NATIVE_BAO_BASELINE` is required before public
  measurement-gate scoring.
- `COORDINATE_NATIVE_BAO_BASELINE` is required before coordinate-robust K2
  interpretation.
- `NULL_COMPARATOR_BAO_BASELINE` is required before any locked prediction is
  evaluated against public residuals.

## Same-Data Offset Sensitivity

The non-eligible sensitivity script is:

```text
scripts/build_bao_rd_offset_sensitivity.py
```

Outputs:

```text
evidence/bao_rd_offset_sensitivity_preflight.csv
evidence/bao_rd_offset_sensitivity_summary.csv
```

This check absorbs the constant BAO residual offset into an effective `rd`
value using the same DESI product being tested. It is useful because it verifies
that the dominant T1 residual mode is a global scale mode. It is not eligible
for measurement-gate scoring because the scale correction is learned from the
same data vector.

## Why The Audit Baseline Is Insufficient

The current audit baseline uses:

```text
H0 = 70.0
omega_m = 0.3
rd = 147.0 Mpc
```

The offset diagnosis finds that the DESI BAO residuals prefer a roughly
1.5 percent global scale adjustment, equivalent to `rd` near 144.8 Mpc if the
shift is absorbed into the sound-horizon scale. This is a baseline calibration
issue. It is not a finite-memory signal.

## Required Export Conditions

A BAO baseline export becomes eligible for measurement-gate work only if:

- the export source is public or exactly reproducible;
- the coordinate mapping is frozen before scoring;
- covariance propagation is documented;
- null comparators are evaluated on the same residual vector;
- K2 is not allowed to change its kernel or exceed `rho <= 4`;
- fitted baseline parameters are counted separately from K2 parameters.

## Next Implementation Step

Implement a baseline-export readiness check that reads
`evidence/bao_baseline_export_registry.csv` and reports which baseline, if any,
is eligible for T1 measurement-gate scoring. The expected current result is:

```text
no BAO baseline export is measurement-gate eligible
```

That negative result is useful because it prevents the audit-fiducial offset
from being misread as a finite-memory residual.

The source-readiness layer is documented in:

```text
docs/bao_likelihood_baseline_source_plan.md
evidence/bao_likelihood_baseline_source_registry.csv
evidence/bao_likelihood_baseline_source_readiness.csv
```

It currently finds no eligible likelihood-native source. The Cobaya DESI files
provide public data and covariance, but not a baseline prediction export by
themselves.

The official DESI DR2 `iminuit/base/desi-bao-all` best-fit has now been ingested
as a baseline-export preflight. The local evaluator recomputes the BAO chi2 to
within a small difference of the reported value. This validates the export path,
but it remains a same-data posterior maximum and is not an independent K2
measurement baseline.

The CMB-only public best-fit export has also been ingested. It provides a more
independent BAO prediction baseline, but its BAO chi2 is substantially higher
than the same-data DESI best-fit baseline. The resulting baseline scorecard is:

```text
evidence/bao_baseline_scorecard.csv
```
