# Physical Null Preflight Scorecard

Status: preflight sanity / sensitivity scorecard; no measurement validation
claim.

This scorecard adds the registered physical-null proxy templates to the
source-split likelihood-native preflight vector. It does not change the locked
K2 operator, does not fit a new K1 baseline, and does not select a best
physical-null amplitude for interpretation.

Outputs:

- `evidence/physical_null_preflight_scorecard.csv`;
- `evidence/physical_null_preflight_summary.csv`.

## Inputs

The scorecard uses:

- the coordinate-native source-split target;
- the external likelihood-native K1 response export;
- the branch-scatter preflight covariance scale;
- the backreaction-only and Dyer-Roeder/optical unit-norm proxy templates;
- the physical-null amplitude policy registry.

## Allowed Physical-Null Amplitudes

The allowed amplitudes are exactly the policy amplitudes:

- unit-only sanity comparison: `A=1`;
- bounded sensitivity grid: `A in {-1.0, -0.5, 0.0, 0.5, 1.0}`.

Every grid row is reported. The scorecard does not promote a best amplitude
after seeing the scores.

## Boundary

This artifact is useful because it stops the benchmark from comparing K2 only
against generic smoothing controls. It is still not measurement validation:
the physical-null amplitudes are not independently calibrated, and the
covariance is still a preflight branch-scatter scale rather than a public full
likelihood covariance.

## Current Reading

The current summary reports:

```text
K1AIC: 13.429587993885114
K2AIC: 9.678203467277251
BestPhysicalNullAIC: 13.67349220290881
DeltaAIC_K2_minus_K1: -3.751384526607863
DeltaAIC_K2_minus_BestPhysicalNull: -3.995288735631558
MeasurementValidationAllowed: false
```

This is K2-supportive at preflight level: locked K2 is better than K1/no-memory
and the reported physical-null template controls under this branch-scatter
scale. It remains below measurement validation because no physical-null
amplitude has been calibrated from an independent source.

The row-level audit qualifies this result. K2 beats K1/no-memory on all eight
rows, but it beats the best reported physical-null template on four rows while
the physical-null template is better on four rows. The net contribution still
slightly favors K2, so the scorecard is supportive but narrow.

The next required step is not a post-hoc amplitude fit. It is an independent
calibration route for the physical-null amplitudes, registered in
`docs/physical_null_calibration_requirements.md`.
