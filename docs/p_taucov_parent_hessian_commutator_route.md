# P-TauCov Parent-Hessian Commutator Route

Status: theory-first route / no matrix candidate / no scoring authorization.

The P4 preflight showed that subtracting an internally declared morphology
basis is not enough. The residual candidate remained too close to generic
morphology/projection covariance:

```text
kernel correlation with morphology-null = 0.8893567053441822
projection-null abs correlation         = 0.8565316433152965
```

This document therefore defines the next admissible Tau-specific construction
route. The goal is not to tune a new covariance kernel. The goal is to derive a
non-morphology response term from the parent branch operator itself.

## Core Idea

The previous epsilon-P3 route used a symmetric core-mixing template. It was
good enough to produce a strong local covariance anomaly, but not specific
enough to beat the morphology-null comparator. The next route must make the
Tau-specific component depend on a non-commuting parent structure:

```math
K_{\tau,\mathrm{comm}}
=
\Pi_{\perp \mathrm{morph}}
\left(
[P_{\mathrm{morph}},L_{\tau}]
\right)
\Pi_{\perp \mathrm{morph}} ,
```

or on an equivalent parent-Hessian cross term:

```math
K_{\tau,\mathrm{hess}}
=
\Pi_{\perp \mathrm{morph}}
H_{\Phi B}^{\mathrm{red}}
\left(L_B^{\mathrm{red}}\right)^{-1}
H_{B\Phi}^{\mathrm{red}}
\Pi_{\perp \mathrm{morph}} .
```

Here `Pi_perp_morph` is the projection away from the frozen P4 morphology
basis. It is a structural filter, not an empirical fit.

## Why This Is More Tau-Specific

A generic morphology covariance response can survive if it depends only on:

```text
M_parent
P_morph
their symmetric covariance closure
```

A Tau-specific branch response should require one of the following:

- a nonzero commutator between the projection map and the parent tau operator;
- a reduced-branch Hessian cross term that remains after morphology projection;
- a protected antisymmetric or signed component that cannot be represented by
  the frozen morphology basis;
- a parent-domain selection rule that fixes the operator before empirical
  scoring.

If the commutator or Hessian route collapses back into the morphology basis,
then it is not a clean Tau-specific route.

## Required Pre-Score Object

The next candidate may only be built from a frozen object of the form:

```text
P_TAUCOV_PARENT_HESSIAN_COMMUTATOR_OBJECT
```

with the following declared components:

| Component | Required declaration |
| --- | --- |
| `L_tau` | parent tau linearized operator or toy proxy |
| `P_morph` | projection/morphology operator |
| `L_B_red` | reduced branch linearization, if Hessian route is used |
| `H_PhiB_red` | reduced parent-branch cross Hessian |
| `Pi_perp_morph` | frozen morphology-basis orthogonal projector |
| domain | coordinate basis and excluded null/gauge directions |
| normalization | Frobenius or operator-norm convention |
| failure modes | conditions under which the object is declared non-specific |

## Specificity Gates

Before any covariance scorecard is allowed, the object must pass:

| Gate | Requirement |
| --- | --- |
| HC-G1 | nonzero commutator or Hessian-cross residual after morphology projection |
| HC-G2 | morphology-null correlation below `0.75` |
| HC-G3 | projection-null correlation below `0.60` |
| HC-G4 | shuffled-support correlation below `0.60` |
| HC-G5 | no family or clock-block pre-score energy dominance above `0.60` |
| HC-G6 | construction uses no target residuals, OOS scores, alpha behavior, or dominant-family identity |

Failure of HC-G1 means the route is mathematically empty. Failure of HC-G2 or
HC-G3 means the route is still a morphology/projection duplicate.

## Allowed Claims

Allowed:

```text
The parent-Hessian/commutator route defines what a Tau-specific covariance
response would have to look like before scoring.
```

Forbidden:

```text
The commutator route has already demonstrated a Tau signal.
```

## Next Implementation Step

The next implementation should not run a covariance scorecard. It should build
only a target-blind object packet:

```text
scripts/build_p_taucov_parent_hessian_commutator_object.py
scripts/validate_p_taucov_parent_hessian_commutator_object.py
evidence/p_taucov_parent_hessian_commutator_object.csv
evidence/p_taucov_parent_hessian_commutator_summary.csv
```

If that packet fails HC-G1 to HC-G6, the branch stops before scoring.
