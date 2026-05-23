# P-TauCov Minimal Global Parent-Action Scaffold

Status: scaffold theorem candidate / no empirical scorecard / no survival
claim.

The global constraint-origin packet maps the local constraints C1-C7 to
parent-structure principles G1-G7. This document gives the first explicit
minimal global parent-action scaffold whose stationary expansion produces the
projection-essential local normal form.

## Scaffold Action

Let the parent state contain a source sector `Phi`, a reduced branch sector
`B`, and a projection-response sector `P`. The minimal scaffold action is:

```math
S_{\rm scaffold}
=
S_{\rm rest}
+
\int d\mu_\tau
\left[
-\frac{1}{2}B^2
-2PB
-P\Phi
\right].
```

`S_rest` contains all sectors not active in the projection-essential witness.
The witness sector is restricted by:

```text
no P^2 term,
no Phi^2 term,
no M-coordinate term,
no target-residual term.
```

## Stationary Branch Equation

Varying the active local potential with respect to `B` gives:

```math
\frac{\partial V_{\rm scaffold}}{\partial B}
=
-B - 2P .
```

The stationary branch condition is therefore:

```math
B_* = -2P .
```

This recovers the branch-relaxation orientation used in the local
action-selection theorem.

## Hessian Sector

The Hessian of the active scaffold sector on `(Phi,B,P)` is:

```math
H_{\rm scaffold}
=
-2(PB+BP)
-
(P\Phi+\Phi P)
-
BB .
```

After the frozen morphology projection filter, this is the
projection-essential witness.

## Claim Boundary

Allowed:

```text
There is a minimal explicit global scaffold whose stationary branch expansion
produces the projection-essential local normal form.
```

Forbidden:

```text
This is the final microscopic Tau Core action, a UV completion, or an
empirical Tau signal.
```

## Remaining Gate

The next gate is to embed this scaffold in a full Tau Core action with:

- compact-cell or continuum domain;
- gauge/null-mode handling;
- stable background selection;
- covariance map derivation;
- external validation path.
