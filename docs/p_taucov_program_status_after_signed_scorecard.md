# P-TauCov Program Status After Signed Scorecard

Status: protocol-success / candidate-failure / no Tau Core validation.

## Completed Gates

The P-TauCov program now has two fully executed, predeclared branches:

1. Parent-action PSD covariance scorecard.
2. Branch-localized signed-response alignment scorecard.

Both were frozen before scoring, authorized by manifests, executed, validated,
and interpreted with no survival claim.

## Results

| Route | Primary result | Status |
|---|---:|---|
| Parent-action PSD covariance | `-0.2996400323571766` | fail |
| Signed-response alignment | `31.70572026946584` | positive raw alignment, but fail |

The signed-response route failed because the diagonal signed control was much
larger and the family contribution was single-family dominated:

```text
RequiredNullMaxSignedS = 152.41444638165376
MaxPositiveFamilyShare = 0.998171886220409
```

## Scientific Meaning

This is a useful negative result. It shows that the current minimal
parent-action/signed-response construction does not yet isolate a
Tau-specific empirical signal.

The program did not fail methodologically. The candidate failed scientifically.

## Current Best Claim

```text
P_TAUCOV_PROTOCOL_INFRASTRUCTURE_VALID_BUT_NO_SURVIVING_TAU_SPECIFIC_SIGNAL
```

Allowed:

- the protocol machinery is reproducible and disciplined;
- the tested minimal PSD and signed candidates are non-survivors;
- future candidates must be more constrained before scoring.

Forbidden:

- Tau Core validation;
- covariance-survival claim;
- signed-response survival claim;
- post-hoc rescue by diagonal or family-dominated diagnostics.

## Next Admissible Direction

The next route must remove diagonal and single-family dominance at the
model-design stage, before scoring. A valid next candidate would need:

1. off-diagonal-only or diagonal-orthogonal signed support;
2. held-out branch-support rule;
3. family-balance constraint frozen before scoring;
4. the same null and aggregation discipline retained.
