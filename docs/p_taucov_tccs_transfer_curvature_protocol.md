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

## Theoretical Refinement From The Preflight

The transfer-curvature route fixes the algebraic no-go of the double-sided
commutator, but it exposes a deeper parent-structure requirement.

The current construction uses:

```text
Pi_perp
```

to remove projection/morphology directions, and:

```text
Pi_bal
```

to suppress family-localized artifacts.

The preflight shows that these two operations cannot be treated as independent
clean-up steps. A Tau-specific object requires a common parent metric, common
inner product, or common self-adjoint domain in which both the projection
orthogonal complement and the branch-balanced subspace are compatible.

Otherwise the following failure mode is possible:

```text
nonzero parent transfer-curvature
-> balance projection retains almost no clean norm
-> projection leakage reappears after the balance step
-> no scoreable Tau object exists
```

Therefore the next theoretical refinement is not a new scorecard. It is a
domain-compatibility condition:

```text
Pi_bal Pi_perp K_curv Pi_perp Pi_bal
```

must be defined in a parent geometry where balance and projection orthogonality
commute sufficiently, or where their non-commutation is itself part of the
declared Tau observable.

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
