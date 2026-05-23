# P-TauCov Projection-Essentiality Parent-Action Origin

Status: conditional parent-action origin / no empirical scorecard / no survival
claim.

The projection-essentiality witness passed the structural gates, but by itself
it is only an algebraic witness. This note records the next stricter step: the
witness must arise from a declared parent action rather than from a manually
chosen contrast.

## Minimal Parent Action

On the frozen coordinate sector

```text
Phi = parent source
B   = branch response
P   = morphology/projection response
M   = parent morphology
```

the minimal projection-essential quadratic parent potential is declared as

```math
V_{\rm PE}(\Phi,B,P)
=
-2PB - P\Phi - \frac{1}{2}B^2 .
```

Its Hessian on the `(Phi,B,P)` sector is

```math
H_{\rm PE}
=
-2(PB+BP) - (P\Phi+\Phi P) - BB .
```

This is exactly the projection-essential witness form used in the structural
preflight. The minus signs are not fit to data; they encode a branch-relaxation
orientation in which the projection coordinate couples oppositely to the
source and branch directions, while the branch counterterm prevents a pure
projection spike.

## Why This Is Still Conditional

This is not a final microscopic Tau Core action. It is a local quadratic
normal-form candidate. It establishes only:

```text
there exists a simple parent-action normal form whose Hessian gives the
projection-essential witness.
```

It does not establish:

```text
the global Tau Core action;
the physical normalization of the coefficients;
the empirical survival of the resulting covariance object;
measurement validation.
```

## Required Origin Gates

| Gate | Requirement |
| --- | --- |
| PA-G1 | the generated Hessian exactly matches the witness matrix |
| PA-G2 | all coefficients are declared before scoring |
| PA-G3 | the Hessian remains morphology-orthogonal after frozen projection |
| PA-G4 | the witness still passes the projection-essentiality gates |
| PA-G5 | no target residuals, score outcomes, alpha behavior, or dominant-family identity are used |

If these gates pass, the claim boundary becomes:

```text
The projection-essential witness has a conditional local parent-action origin.
```

It still does not become a scored Tau signal.
