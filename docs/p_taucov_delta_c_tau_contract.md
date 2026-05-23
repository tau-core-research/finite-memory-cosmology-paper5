# P-TauCov delta_C_Tau Construction Contract

Status: construction contract / no branch-support freeze / no scoring
authorization.

This document defines the only admissible construction path for the future
`delta_C_Tau` artifact used by P-TauCov. It does not compute `delta_C_Tau`; it
locks the rule that must be satisfied before `W_branch`, `Omega_branch`, or
`S_tau` can be evaluated.

## 1. Required Branch Equation

The reduced branch must be declared as:

```math
B = B_*(\Phi),
```

with first-order branch response:

```math
\delta B_*
=
- (L_B^{\rm red})^{-1} D_\Phi F_B[\delta\Phi].
```

`L_B^{red}` must be invertible only on the declared reduced branch domain. Any
null space, gauge direction, or excluded mode must be declared before scoring.

## 2. Required Projected Morphology

The observable morphology map must have the declared form:

```math
M_{\rm proj}(\Phi,B)
=
P_{\rm morph}(\Phi,B)M_{\rm parent}(\Phi,B).
```

`P_morph`, `M_parent`, and the observable coordinate index must be frozen before
the response is converted into covariance space.

## 3. Required Tau Morphology Response

The only admissible Tau morphology response is:

```math
T_{\tau}
=
D_\Phi M_{\rm proj}
-
D_B M_{\rm proj}(L_B^{\rm red})^{-1}D_\Phi F_B.
```

The second term is mandatory. Dropping it converts the test into a generic
morphology response and invalidates P-TauCov.

## 4. Required Covariance Response

The predicted covariance response must be constructed as:

```math
\delta C_{\tau}
=
D_M C[T_{\tau}\delta\Phi].
```

The output must be a square symmetric response matrix indexed on the frozen
observable coordinates. Its normalization must be frozen before branch support
is computed.

## 5. Allowed Inputs

Allowed inputs are limited to:

```text
Phi grid or perturbation family;
B_star rule;
L_B^red;
D_Phi F_B;
P_morph;
M_parent;
D_M C;
frozen observable coordinate index;
normalization convention.
```

## 6. Forbidden Inputs

The construction must not use:

```text
held-out residuals;
P5C v3 family-localized gain pattern;
dominant positive family;
observed OOS DeltaNLL pattern;
signed diagnostic advantage;
failed family-permutation gate;
post-score branch choice.
```

## 7. Authorization Boundary

This contract does not authorize scoring. It also does not authorize a concrete
branch-support freeze until a hashed `delta_C_Tau` artifact and its
normalization are present.

Allowed statement:

```text
The construction path for a future Tau-derived covariance-response artifact is
predeclared.
```

Forbidden statement:

```text
P-TauCov has already demonstrated a Tau-specific covariance response.
```

## 8. Next Valid Step

The next valid step is a target-blind generator that produces:

```text
evidence/p_taucov_delta_c_tau.csv
evidence/p_taucov_delta_c_tau.yaml
evidence/p_taucov_delta_c_tau.sha256
docs/p_taucov_delta_c_tau_freeze.md
```

Only after that can `q_branch`, `W_branch`, and `Omega_branch` be frozen.
