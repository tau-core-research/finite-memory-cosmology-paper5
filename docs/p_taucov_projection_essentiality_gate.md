# P-TauCov Projection-Essentiality Gate

Status: theory/preflight gate / no empirical scorecard / no survival claim.

The parent-Hessian/commutator object solved the morphology-null problem but
failed the projection-null gate:

```text
morphology-null abs correlation = 0.1686357268015766
projection-null abs correlation = 0.7337111972818574
```

This means the object was not generic morphology, but its empirical covariance
image remained too similar after the projection coordinate was removed. A
Tau-specific projection response must instead be projection-essential.

## Definition

A candidate object is projection-essential only if removing the declared
projection coordinate substantially changes its empirical covariance image.

The pre-score diagnostic is:

```math
E_{\rm proj}
=
1 -
|\mathrm{corr}(K_{\rm full},K_{\rm projection-null})|.
```

The gate is:

```text
E_proj > 0.40
```

equivalently:

```text
abs correlation with projection-null < 0.60
```

This is not an empirical success criterion. It is a structural admissibility
criterion before scoring.

## Why This Matters

If a response survives after the projection coordinate is removed, then it is
probably not testing a projection-specific Tau channel. It may still be a real
covariance pattern, but it cannot support the P-TauCov claim boundary.

## Minimal Algebraic Witness

A non-scoring witness may use a trace-balanced projection-essential contrast on
the frozen tau-coordinate basis:

```math
O_{\rm PE}
=
-2(PB+BP)
-(P\Phi+\Phi P)
-BB .
```

Here:

- `P` is the declared projection coordinate;
- `B` is the branch-response coordinate;
- `Phi` is the parent-source coordinate;
- the `BB` counterterm makes the witness branch-balanced rather than a pure
  projection spike.

The witness is allowed only to test whether the projection-essential route is
structurally non-empty. It does not authorize a covariance scorecard.

## Required Gates

| Gate | Requirement |
| --- | --- |
| PE-G1 | nonzero morphology-orthogonal residual |
| PE-G2 | morphology-null correlation below `0.75` |
| PE-G3 | projection-null correlation below `0.60` |
| PE-G4 | shuffled-support correlation below `0.60` |
| PE-G5 | no family or clock-block pre-score energy dominance above `0.60` |
| PE-G6 | no target residuals, scores, alpha behavior, or dominant-family identity |

Passing these gates means only that a projection-essential Tau-side route is
structurally possible. It does not mean a Tau signal has been found.
