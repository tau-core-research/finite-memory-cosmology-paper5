# P-TauCov Tau-Side Definition Spec

Status: candidate Tau-side definitions / not frozen / no concrete packet / no
metric evaluation / no scoring authorization.

This document gives the first explicit target-blind definitions for the
Tau-side objects required by the matrix-origin route:

```text
F_B
M_parent
P_morph
```

It still does not produce concrete matrices. It defines the symbolic origin from
which those matrices must later be derived.

## 1. Branch Equation

The branch equation is proposed as a stationarity/relaxation equation:

```math
F_B(\Phi,B)
=
\nabla_B U_{\rm branch}(B;\Phi)
+
\Gamma_B B.
```

The branch potential is:

```math
U_{\rm branch}(B;\Phi)
=
\frac{1}{2}\langle B,K_B(\Phi)B\rangle
-
\langle J_B(\Phi),B\rangle.
```

Therefore the linear packet objects must come from:

```math
D_B F_B = K_B(\Phi_0)+\Gamma_B,
```

and:

```math
D_\Phi F_B[\delta\Phi]
=
\frac{1}{2}\langle B,D_\Phi K_B[\delta\Phi]B\rangle_B
-
D_\Phi J_B[\delta\Phi].
```

The exact finite-dimensional representation of `K_B`, `J_B`, and `Gamma_B`
is not yet frozen.

## 2. Parent Morphology

The minimal morphology carrier is:

```math
M_{\rm parent}(\Phi,B)
=
M_0 + G_\Phi\Phi + G_B B.
```

Thus:

```math
A_\Phi = D_\Phi M_{\rm parent}=G_\Phi,
\qquad
A_B = D_B M_{\rm parent}=G_B.
```

`G_Phi` and `G_B` must be derived from a target-blind morphology definition or
frozen as a candidate morphology map before metric evaluation.

## 3. Projection Map

For the strictly linear candidate:

```math
P_{\rm morph}(\Phi,B)=P_0,
\qquad
\epsilon_P=0.
```

This means the first specificity audit tests branch relaxation under a fixed
projection map. A nonzero projection-response term `epsilon_P P_1(Phi,B)` is a
separate future model family and cannot rescue a failed strict-linear audit.

## 4. Remaining Required Freezes

The following are still missing:

```text
reference state Phi_0;
branch null/gauge/forbidden basis;
finite-dimensional K_B, J_B, Gamma_B;
target-blind G_Phi and G_B;
fixed P0.
```

## Claim Boundary

Allowed statement:

```text
The Tau-side objects now have explicit candidate symbolic definitions.
```

Forbidden statement:

```text
The Tau-side definitions have produced a valid linear packet or covariance
response.
```
