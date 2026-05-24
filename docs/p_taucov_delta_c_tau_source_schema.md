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
| `CovarianceFunctionalDerivative` | `D_M C` | `TARGET_BLIND_PSD_LIFT_DECLARED` |
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

The target-blind covariance map declaration is available at:

[`p_taucov_covariance_map_declaration.md`](p_taucov_covariance_map_declaration.md)

It declares `D_M C[T] = TT^T / ||TT^T||_F` as the PSD covariance lift. This
does not yet generate a complete `delta_C_Tau` artifact or authorize scoring.

The first conservative `delta_C_Tau` candidate is available at:

[`p_taucov_reduced_jacobian_assembly.md`](p_taucov_reduced_jacobian_assembly.md)

It is strict branch-only and no-scoring. It is an assembly artifact, not a
survival result.

The first specificity preflight is available at:

[`p_taucov_reduced_jacobian_specificity_preflight.md`](p_taucov_reduced_jacobian_specificity_preflight.md)

It blocks scoring for the strict branch-only candidate. A future candidate must
include target-blind morphology/projection channel structure before scoring can
be reconsidered.

The projection/morphology coupling gate is available at:

[`p_taucov_projection_morphology_coupling_gate.md`](p_taucov_projection_morphology_coupling_gate.md)

It makes that requirement explicit. The next admissible route must declare a
target-blind `D_P M_proj` or equivalent projection derivative, must use the
active `TEMPLATE_P_MORPH_PROJECTION` channel, and must not leak direct forbidden
`TEMPLATE_M_PARENT_MORPHOLOGY` support into the reduced object. This is a gate
only; it constructs no new `delta_C_Tau` object and authorizes no scoring.

The first source derivative spec is available at:

[`p_taucov_d_p_mproj_source_spec.md`](p_taucov_d_p_mproj_source_spec.md)

It freezes the minimal target-blind active `B-P` coupling source:

```text
D_P M_proj(B, P) = (|B><P| + |P><B|) / sqrt(2)
```

This closes the immediate `D_P M_proj` source placeholder for the next assembly
attempt, but still does not construct a scoreable `delta_C_Tau` object.

The first projection-coupled assembly is available at:

[`p_taucov_projection_coupled_jacobian_assembly.md`](p_taucov_projection_coupled_jacobian_assembly.md)

Its specificity preflight is available at:

[`p_taucov_projection_coupled_specificity_preflight.md`](p_taucov_projection_coupled_specificity_preflight.md)

This preflight fixes the previous missing-projection-channel failure, but it
still blocks scoring because the PSD-lifted candidate is diagonal-dominated and
low-rank. The next valid route must therefore add a broader parent-side
curvature/operator source, not merely the minimal active `B-P` derivative.

The active-triad PSD ceiling audit is available at:

[`p_taucov_active_triad_psd_ceiling_audit.md`](p_taucov_active_triad_psd_ceiling_audit.md)

It checks deterministic target-blind off-diagonal source shapes on the active
`Phi/B/P` triad. No scanned triad object passes both the diagonal-energy and
effective-rank gates. This means the PSD route needs a broader parent-side
operator source or a different, separately frozen signed-contrast claim class.

The parent-operator source expansion gate is available at:

[`p_taucov_parent_operator_source_expansion_gate.md`](p_taucov_parent_operator_source_expansion_gate.md)

It freezes the requirements for a broader PSD route: at least five active
reduced coordinates, at least two new non-outcome axes, and a parent-side
operator/source rule before covariance lifting.

## Next Valid Step

Provide a concrete, target-blind Tau-response input packet with:

```text
F_B, L_B^red, branch-domain policy,
P_morph, frozen D_P M_proj source derivative,
expanded parent-side curvature/operator source with >=5 active coordinates,
D_M C,
observable coordinate index,
normalization policy,
leakage exclusion audit.
```

Only after this source schema is ready may a hashed `delta_C_Tau` matrix be
generated.
