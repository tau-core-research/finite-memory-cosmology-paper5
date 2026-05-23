# P-TauCov TCCS J_tau Anchor Candidate

Freeze ID: `P_TAUCOV_TCCS_JTAU_ANCHOR_CANDIDATE_v1`

Status:

`P_TAUCOV_TCCS_JTAU_ANCHOR_CANDIDATE_FROZEN_NO_OBJECT_NO_SCORING`

## Anchor

Selected candidate class:

```text
JTAU_A_PARENT_COMPLEX_STRUCTURE
```

The anchor is a fixed skew parent-coordinate orientation on the frozen linear coordinate basis:

```text
Phi -> B
M   -> P
```

where:

- `Phi` is the parent source coordinate;
- `B` is the branch response coordinate;
- `M` is the parent morphology coordinate;
- `P` is the morphology/projection readout coordinate.

The matrix is antisymmetric by construction:

```text
J_tau^T = -J_tau
```

## Why This Is Target-Blind

The pair ordering is inherited from the Tau-side symbolic coordinate packet and the projection-essential parent-action normal-form route. It does not use:

- target residuals;
- empirical score signs;
- P5C gains;
- dominant family identity;
- post-score sign flipping.

## What This Does Not Authorize

This file does not build the TCCS object. It does not compute an orientation margin. It does not authorize scoring.

The next required gate is a pre-score validation that this `J_tau` candidate can orient a projection-orthogonal, branch-balanced commutator without collapsing into projection-null, morphology-null, diagonal, or family-localized structure.

## Diagnostics

| Quantity | Value |
|---|---:|
| skew-symmetry max error | `0.0` |
| trace | `0.0` |
| Frobenius norm | `2.0` |
| rank | `4` |
| active axes | `4` |

## Claim Boundary

Allowed statement:

> A target-blind parent-coordinate orientation anchor candidate has been frozen for the TCCS route.

Forbidden statement:

> The anchor has oriented a valid TCCS object, authorized scoring, or produced a Tau signal.
