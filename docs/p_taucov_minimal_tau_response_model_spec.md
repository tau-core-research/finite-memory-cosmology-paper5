# P-TauCov Minimal Tau-Response Model Specification

Status: candidate model specification / not frozen / no `delta_C_Tau` / no
scoring authorization.

This note proposes a minimal target-blind mathematical form for the four
Tau-side blockers isolated by the P-TauCov input packet:

```text
F_B, L_B^red, M_parent, P_morph
```

It is not an empirical result. It is a candidate specification that must either
be frozen into concrete matrices/operators or rejected before any
`delta_C_Tau`, branch support, or alignment score is generated.

## 1. Minimal Branch State

Let `B` be a reduced branch-amplitude vector on the frozen observable/source
coordinate basis. The basis must be declared before scoring and cannot be
chosen from P5C v3 gains.

## 2. Candidate Branch Equation

The minimal branch equation is:

```math
F_B(\Phi,B)
=
L^0_B B - R_B\Phi + \lambda_B N_B(B).
```

The linear part carries the target-blind branch relaxation. The optional
nonlinear term is allowed only if `lambda_B`, `N_B`, and its derivative are
frozen before scoring. The strictly linear candidate is recovered by
`lambda_B = 0`.

## 3. Reduced Branch Operator

The reduced branch operator is:

```math
L_B^{\rm red}
=
P_{\rm red}
\left(L^0_B + \lambda_B D_B N_B(B_*)\right)
P_{\rm red}.
```

`P_red` declares the invertible branch domain. Null modes, gauge-like modes,
and excluded directions must be frozen before inversion.

## 4. Parent Morphology Map

The minimal morphology carrier is:

```math
M_{\rm parent}(\Phi,B)
=
A_\Phi\Phi + A_B B.
```

This is intentionally conservative. Any nonlinear morphology term is a new
model family and requires a separate freeze.

## 5. Projection Morphology Map

The minimal projection map is:

```math
P_{\rm morph}(\Phi,B)
=
P_0 + \epsilon_P P_1(\Phi,B).
```

The safest first candidate is `epsilon_P = 0`, which tests whether a fixed
projection geometry plus branch relaxation already predicts a localized
covariance response. If `epsilon_P` is nonzero, `P_1` must be frozen before any
score is seen.

## 6. Resulting Tau Response

After the above objects are frozen, the admissible response remains:

```math
T_\tau
=
D_\Phi M_{\rm proj}
-
D_B M_{\rm proj}(L_B^{\rm red})^{-1}D_\Phi F_B.
```

and:

```math
\delta C_\tau
=
D_M C[T_\tau\delta\Phi].
```

## 7. Reviewer-Safe Claim Boundary

Allowed statement:

```text
A minimal target-blind Tau-response model family has been specified for future
P-TauCov freezing.
```

Forbidden statement:

```text
This specification already produces a Tau-specific covariance signal.
```

## 8. Strictly Linear Candidate Is Not Yet Frozen

The strictly linear candidate is useful as the minimal reference model, but it
must not be frozen automatically. A purely linear branch-response model may be
too generic: it can behave like a broad covariance backreaction template rather
than a Tau-specific branch/projection signature.

Required intermediate gate:

```text
P_TAUCOV_LINEAR_SPECIFICITY_AUDIT
```

This audit must be target-blind. It must ask whether the strictly linear
candidate produces a branch/projection/covariance signature that is more
specific than generic linear covariance response families before any
`delta_C_Tau` score is run.

## 9. Next Valid Step

The next valid step is one of:

```text
run P_TAUCOV_LINEAR_SPECIFICITY_AUDIT;
if it passes, freeze concrete matrices/operators for the strictly linear candidate;
if it fails, reject the strictly linear candidate as too generic and consider a
predeclared minimal nonzero backreaction/projection term.
```

Only a frozen concrete model can produce a hashed `delta_C_Tau` artifact.
