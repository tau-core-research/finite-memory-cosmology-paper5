# P-TauCov Branch-Support Freeze Template

Status: template only / no scoring authorization.

This artifact is the pre-scoring branch-support contract for
`P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1`.

It does not compute `W_branch` or `Omega_branch`. It specifies the admissible
source and the hard exclusions that must remain in force when a future branch
support is actually frozen.

## Required Source

The only admissible support source is:

```text
delta_C_Tau_only
```

The default continuous support weight is:

```math
W_{\rm branch}(i,j)
=
\frac{|\delta C_{\tau}(i,j)|}
{\sum_{a,b}|\delta C_{\tau}(a,b)|}.
```

The default binary support is the smallest set carrying a predeclared response
mass fraction `q_branch`. In this template `q_branch` is deliberately `NOT_SET`;
it must be frozen before scoring.

## Hard Blocks

The branch support must not use:

```text
P5C v3 family-localized gain pattern;
held-out residuals;
dominant positive family;
observed OOS DeltaNLL pattern;
signed diagnostic advantage;
failed family-permutation gate.
```

## Current Status

```text
P5Cv3Status: P5C_V3_STRONG_LOCAL_COVARIANCE_SIGNAL_BUT_NO_GLOBAL_SURVIVAL
P5Cv3Meaning: anomaly candidate only
PTauCovScoringAuthorized: false
V4KernelAuthorized: false
```

## Next Valid Step

The next valid step is to build a concrete `delta_C_Tau` artifact from the
declared Tau morphology response and then freeze `q_branch`, `W_branch`, and
`Omega_branch` before any alignment score is run.
