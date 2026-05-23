# P-TauCov P4 Morphology Basis Packet

Status: `P_TAUCOV_P4_MORPHOLOGY_BASIS_FROZEN_NO_SCORING`.

This packet freezes the morphology-shared basis that a later P4
candidate must project away before any Tau-specific covariance
claim can be tested.

## Frozen Basis

- `M_PARENT_MORPHOLOGY_DIAGONAL`
- `P_MORPH_PROJECTION_DIAGONAL`
- `M_P_SYMMETRIC_COUPLING`

The basis is constructed only from declared tau-coordinate names and
does not use target residuals, fold outcomes, alpha behavior, or P3
score margins.

## Claim Boundary

Allowed statement:

```text
A target-blind morphology-shared subspace has been frozen for later
P4 morphology-orthogonalization.
```

Forbidden statement:

```text
The P4 candidate has been built, scored, or shown to be Tau-specific.
```
