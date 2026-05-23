# P-TauCov TCCS Transfer-Curvature Protocol

Freeze ID: `P_TAUCOV_TCCS_TRANSFER_CURVATURE_PROTOCOL_v1`

Status:

`P_TAUCOV_TCCS_TRANSFER_CURVATURE_PROTOCOL_DEFINED_NO_OBJECT_NO_SCORING`

## Motivation

The double-sided projected commutator is mathematically blocked:

```text
Pi_perp [H,P] Pi_perp = 0
```

for an exact projector `P` and its complement `Pi_perp`.

Therefore the next TCCS object class must measure transfer between the
morphology/projection subspace and its complement, not a double-sided
complement restriction of the raw commutator.

## Corrected Candidate Class

Signed transfer:

```text
T_transfer = Pi_perp [H,P] P
```

Covariance-safe curvature:

```text
K_curv = Pi_perp [H,P] P [H,P]^T Pi_perp
```

The PSD form may become a reviewer-friendly covariance-deformation candidate
only after pre-score gates pass and a separate scoring manifest is frozen.

## Forbidden Move

Do not return to:

```text
Pi_perp [H,P] Pi_perp
```

as a scoreable object. The no-go theorem already rules it out.

## Claim Boundary

Allowed statement:

> The TCCS no-go theorem implies a transfer-curvature object class as the next pre-score candidate.

Forbidden statement:

> The transfer-curvature protocol has produced a Tau signal or authorizes empirical scoring.
