# Physical Null Amplitude Policy

Status: preflight amplitude policy; no measurement validation claim.

The physical-null proxy templates define shapes for backreaction-only and
Dyer-Roeder/optical comparators. This policy declares how those shapes may be
amplitude-weighted before they enter any preflight scorecard.

Outputs:

- `evidence/physical_null_amplitude_policy.csv`;
- `evidence/physical_null_amplitude_policy_readiness.csv`.

## Registered Policies

The primary policy is:

```text
PHYSNULL_AMP_UNIT_ONLY_V1
AmplitudeRule: A=1 on unit-norm template
```

This is a sanity comparator only. It is not a physical calibration.

The secondary policy is:

```text
PHYSNULL_AMP_BOUNDED_GRID_V1
AmplitudeRule: A in {-1.0,-0.5,0.0,0.5,1.0}; report all grid outcomes
```

This is sensitivity only. The best amplitude must not be promoted after seeing
the scorecard.

The forbidden policy is:

```text
PHYSNULL_AMP_FORBIDDEN_FREE_FIT_V1
```

Any least-squares or AIC-selected amplitude chosen after inspecting the result
is forbidden for stronger interpretation.

## Readiness

The readiness output reports:

```text
AmplitudePolicyDeclared: true
ScoringPreflightAllowed: true
MeasurementValidationAllowed: false
PrimaryBlockingIssue: physical_null_amplitudes_not_physically_calibrated
```

Thus the physical nulls may enter a future preflight scorecard as sanity /
sensitivity controls, but not as measurement-calibrated physical explanations.

The first such preflight scorecard is now exported in
`evidence/physical_null_preflight_scorecard.csv`. Its physical-null rows should
be read as reported sanity / sensitivity controls only; the best physical-null
row is diagnostic bookkeeping, not an amplitude selected for interpretation.
