# Physical Null Comparator Hierarchy

Status: hierarchy registered; physical null layer preflight-ready but not
measurement-calibrated.

The polynomial-control fairness audit shows that generic polynomial smoothing
is a mandatory overfit-risk control, but not a physical explanation. This
hierarchy separates physical nulls from diagnostic and overfit controls.

Outputs:

- `evidence/physical_null_hierarchy.csv`;
- `evidence/physical_null_hierarchy_readiness.csv`.

## Hierarchy

The registered comparator hierarchy is:

1. `LCDM_NO_MEMORY`: primary fair null / minimum baseline.
2. `BACKREACTION_ONLY`: physical null / cosmological averaging control.
3. `DYER_ROEDER_OPTICAL`: physical null / optical propagation control.
4. `RECONSTRUCTION_ARTIFACT`: diagnostic control / pipeline sensitivity.
5. `GENERIC_POLYNOMIAL_SMOOTHING`: overfit-risk control.
6. `SIGN_RANDOMIZED_CONTROL`: negative control.
7. `COORDINATE_REMAP_CONTROL`: coordinate control.

## Current Readiness

The readiness output reports:

```text
RegisteredNulls: 7
RequiredForNextBenchmark: 7
RequiredImplementedOrPartial: 4
RequiredImplementedOrTemplate: 6
PhysicalNullsRequired: 3
PhysicalNullsScoringReady: 1
PhysicalNullTemplatesAvailable: 0
PhysicalNullPreflightScoringPolicyAvailable: 2
MeasurementClaimReady: false
PrimaryBlockingIssue: physical_null_amplitudes_not_physically_calibrated
```

## Interpretation

The next stronger benchmark cannot rely only on K1/no-memory, polynomial
controls, and covariance policy. It also needs physical null controls that can
compete with the finite-memory projection hypothesis:

- a backreaction-only source-split proxy or public reconstruction envelope;
- a Dyer-Roeder / optical clumpiness proxy on the same source-split vector.

The backreaction-only and Dyer-Roeder/optical controls now have preflight
scoring policies:

- `PHYSNULL_AMP_UNIT_ONLY_V1`: unit-norm sanity comparison;
- `PHYSNULL_AMP_BOUNDED_GRID_V1`: bounded sensitivity grid with all amplitudes
  reported;
- `PHYSNULL_AMP_FORBIDDEN_FREE_FIT_V1`: explicit ban on post-hoc amplitude
  rescue.

They are not physically amplitude-calibrated. Until that calibration or a
public physical-null reconstruction source exists, the polynomial control
remains a blocker, but it does not become a physical explanation.

## First Preflight Scorecard

The first physical-null preflight scorecard is exported as:

- `evidence/physical_null_preflight_scorecard.csv`;
- `evidence/physical_null_preflight_summary.csv`.

On the branch-scatter preflight covariance scale, locked K2 is stronger than
K1/no-memory and the reported physical-null sanity/sensitivity rows. This is a
supportive preflight signal for K2, but it is not a measurement-validation
result because the physical-null amplitudes are not physically calibrated.

The row-level audit makes the support boundary sharper: K2 beats K1 on every
row, but it is split 4-4 against the best reported physical-null row. The
physical-null comparators therefore remain active blockers until their
amplitudes are calibrated independently.

The calibration requirement registry defines two allowed missing routes:
backreaction amplitude from a public reconstruction/envelope or independent
simulation prior, and Dyer-Roeder/optical amplitude from public clumpiness,
opacity, lensing, or `alpha(z)` constraints. Same-scorecard amplitude fitting is
explicitly forbidden.

The source registry breaks those routes into concrete candidate source classes
and a task queue. No candidate source is currently ingested or mapped, so the
physical-null layer remains preflight-only.
