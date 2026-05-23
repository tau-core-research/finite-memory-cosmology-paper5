# P-TauCov delta_C_Tau Source Schema

Status: source schema / readiness blocker / no scoring authorization.

This document is the input checklist for generating a real target-blind
`delta_C_Tau` artifact. It deliberately does not fabricate a response matrix.
The protocol remains blocked until the Tau-response source objects below are
provided.

## Required Source Objects

| Source object | Role | Current status |
| --- | --- | --- |
| `PhiPerturbationFamily` | parent perturbation family `deltaPhi` | `NOT_PROVIDED` |
| `BranchEquationFB` | reduced branch equation `F_B(Phi,B)=0` | `NOT_PROVIDED` |
| `ReducedBranchOperatorLBred` | branch linearization `L_B^red` | `NOT_PROVIDED` |
| `BranchDomainPolicy` | invertible reduced domain and excluded null modes | `NOT_PROVIDED` |
| `BranchResponseRule` | `deltaB_star = -(L_B^red)^-1 D_Phi F_B[deltaPhi]` | `FORMULA_DECLARED_ONLY` |
| `ParentMorphologyMap` | parent morphology `M_parent(Phi,B)` | `NOT_PROVIDED` |
| `ProjectionMorphologyMap` | projected map `P_morph(Phi,B)` | `NOT_PROVIDED` |
| `ProjectedMorphologyDerivativePhi` | `D_Phi M_proj` | `NOT_PROVIDED` |
| `ProjectedMorphologyDerivativeB` | `D_B M_proj` | `STRICT_LINEAR_PROVIDED` |
| `CovarianceFunctionalDerivative` | `D_M C` | `NOT_PROVIDED` |
| `ObservableCoordinateIndex` | frozen matrix row/column basis | `NOT_PROVIDED` |
| `NormalizationPolicy` | response normalization before support extraction | `NOT_PROVIDED` |
| `LeakageExclusionAudit` | proof no target residual or v3 outcome enters | `NOT_PROVIDED` |

## Readiness Meaning

The present status is:

```text
DeltaCTauGenerationStatus: BLOCKED_PENDING_CONCRETE_TAU_RESPONSE_INPUTS
BranchSupportFreezeAuthorized: false
PTauCovScoringAuthorized: false
V4KernelAuthorized: false
```

This is a useful negative state. It prevents the program from converting the
P5C v3 local anomaly into a Tau claim without first supplying the missing
Tau-side response machinery.

## Partial Update

The strict-linear projected morphology derivative audit is available at:

[`p_taucov_projected_morphology_derivative_audit.md`](p_taucov_projected_morphology_derivative_audit.md)

It provides `D_B M_proj = P0 A_B` as a target-blind readout derivative. This
does not yet provide a physical morphology model or a complete covariance map.

## Next Valid Step

Provide a concrete, target-blind Tau-response input packet with:

```text
F_B, L_B^red, branch-domain policy,
P_morph, M_parent, D_M C,
observable coordinate index,
normalization policy,
leakage exclusion audit.
```

Only after this source schema is ready may a hashed `delta_C_Tau` matrix be
generated.
