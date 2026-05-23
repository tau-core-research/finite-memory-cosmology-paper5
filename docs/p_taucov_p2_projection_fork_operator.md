# P-TauCov P2 Projection-Fork Operator

Status: target-blind projection-fork operator / no updated model packet / no
empirical scoring authorization.

The minimal P1 operator passed most target-blind checks but failed the
null-separation gate because its covariance response was too diagonal/null-like.
This P2 packet freezes a richer projection-response structure without using
target residuals, P5C v3 outcomes, score behavior, or family-localized tuning.

## Frozen Construction

```text
parent source -> projection coordinate
parent source -> morphology coordinate
projection coordinate -> morphology coordinate
```

with unit Frobenius normalization:

```text
each nonzero link = 1/sqrt(3)
```

The shared parent source creates an off-diagonal covariance component between
the projection and morphology rows. This directly targets the P1 failure mode
without inspecting empirical residuals.

## Claim Boundary

Allowed statement:

```text
A target-blind P2 projection-fork operator is frozen for later specificity
auditing.
```

Forbidden statement:

```text
The P2 operator has produced a Tau signal, passed empirical scoring, or
authorized P-TauCov survival claims.
```
