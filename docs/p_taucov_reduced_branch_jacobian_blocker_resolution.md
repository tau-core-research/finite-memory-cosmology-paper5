# P-TauCov Reduced Branch-Jacobian Blocker Resolution

Freeze ID: `P_TAUCOV_REDUCED_BRANCH_JACOBIAN_BLOCKER_RESOLUTION_v1`

Status:

`P_TAUCOV_REDUCED_BRANCH_JACOBIAN_BLOCKERS_REDUCED_STILL_BLOCKED_NO_SCORING`

## Purpose

This audit updates the reduced branch-Jacobian blocker list after the Q-range
freeze and the full-action-domain null/gauge packet.

It does not construct `J_response`, does not construct `K_Q`, and does not
authorize empirical scoring.

## Blocker Status

| Object | Resolution status | Evidence | Still blocks |
|---|---|---|---|
| `Q_range` | `RESOLVED_AVAILABLE` | `evidence/p_taucov_q_range_projector_matrix.csv` | `False` |
| `P_red` | `PARTIALLY_RESOLVED_BY_FULL_ACTION_DOMAIN_PACKET` | `evidence/p_taucov_full_action_domain_projectors.csv` | `False` |
| `ReferenceState` | `UNRESOLVED_REFERENCE_BACKGROUND` | `evidence/p_taucov_reference_domain_freeze_summary.csv` | `True` |
| `L_B_red` | `UNRESOLVED_DEPENDS_ON_F_B_AND_REFERENCE_STATE` | `docs/p_taucov_tau_matrix_origin_route.md` | `True` |
| `D_Phi_F_B` | `UNRESOLVED_REQUIRES_BRANCH_EQUATION` | `docs/p_taucov_tau_matrix_origin_route.md` | `True` |
| `D_B_M_proj` | `UNRESOLVED_REQUIRES_M_PARENT_AND_P_MORPH` | `docs/p_taucov_tau_response_input_packet.md` | `True` |

## Key Update

`P_red` is no longer the same kind of blocker as before. The full-action-domain
packet provides a target-blind active/reduced projector. The remaining central
blockers are:

```text
ReferenceState
L_B_red
D_Phi_F_B
D_B_M_proj
```

`L_B_red` and `D_Phi_F_B` remain blocked because the branch equation `F_B` and
the reference state are not yet concrete. `D_B_M_proj` remains blocked because
`M_parent` and `P_morph` are still only route-level objects.

The next dependency-ordered gate is the reference state:

[`p_taucov_reference_state_resolution_gate.md`](p_taucov_reference_state_resolution_gate.md)

The first reference-state candidate spec is:

[`p_taucov_reference_state_candidate_spec.md`](p_taucov_reference_state_candidate_spec.md)

The first branch-equation completion audit is:

[`p_taucov_branch_equation_completion_audit.md`](p_taucov_branch_equation_completion_audit.md)

It narrows the blocker further: `L_B_red` is computable in the current
one-dimensional branch row, but `D_Phi_F_B` remains blocked unless the
projection-mediated parent-forcing chain is made explicit.

The mediated-chain audit is:

[`p_taucov_mediated_parent_forcing_chain_audit.md`](p_taucov_mediated_parent_forcing_chain_audit.md)

It shows that the current scaffold has a nonzero target-blind path
`Phi -> P_morph -> B`. This resolves the forcing route at algebraic scaffold
level, but active stability and `D_B_M_proj` remain open.

The strict-linear projected morphology derivative audit is:

[`p_taucov_projected_morphology_derivative_audit.md`](p_taucov_projected_morphology_derivative_audit.md)

It computes `D_B_M_proj = P0 A_B` from frozen linear inputs and resolves the
`D_B_M_proj` source blocker at strict-linear readout level. It does not provide
a physical morphology model and does not authorize scoring.

The current blocker rollup is:

[`p_taucov_reduced_jacobian_current_blocker_rollup.md`](p_taucov_reduced_jacobian_current_blocker_rollup.md)

It records no remaining reduced-Jacobian source-assembly blockers. The
operational reference/domain package is frozen, the covariance-map declaration
is available as a target-blind PSD lift, and the linear dynamical-stability
packet is assembly-ready. Complete `delta_C_Tau` assembly remains a later step,
and physical validation remains forbidden.

The dynamical-stability reconciliation is:

[`p_taucov_dynamical_stability_status_reconciliation.md`](p_taucov_dynamical_stability_status_reconciliation.md)

The first conservative reduced-Jacobian assembly artifact is:

[`p_taucov_reduced_jacobian_assembly.md`](p_taucov_reduced_jacobian_assembly.md)

It assembles a strict branch-only no-scoring `J_response` and PSD-lift
`delta_C_Tau` candidate after applying the full-action reduced projector. This
does not authorize scoring.

The strict branch-only specificity preflight is:

[`p_taucov_reduced_jacobian_specificity_preflight.md`](p_taucov_reduced_jacobian_specificity_preflight.md)

It rejects that first assembly before scoring because the candidate is
diagonal-only, low-support, and has no explicit morphology/projection channel.

The next admissible projection/morphology coupling gate is:

[`p_taucov_projection_morphology_coupling_gate.md`](p_taucov_projection_morphology_coupling_gate.md)

It requires a future candidate to include a target-blind `D_P M_proj` or
equivalent projection derivative while keeping direct `M_parent` support
forbidden in the reduced object.

The first `D_P M_proj` source derivative spec is:

[`p_taucov_d_p_mproj_source_spec.md`](p_taucov_d_p_mproj_source_spec.md)

It freezes a minimal active branch/projection coupling source. This resolves
the next derivative placeholder at source-spec level only; a new assembled
candidate and object-specific preflight are still required before scoring.

The first projection-coupled assembly is:

[`p_taucov_projection_coupled_jacobian_assembly.md`](p_taucov_projection_coupled_jacobian_assembly.md)

The corresponding specificity preflight is:

[`p_taucov_projection_coupled_specificity_preflight.md`](p_taucov_projection_coupled_specificity_preflight.md)

It confirms the projection channel is present, but rejects the object before
scoring because the PSD lift is still diagonal-dominated and low-rank. The next
blocker is no longer simply missing `D_P M_proj`; it is missing a broader
parent-side curvature/operator source that can distribute support without
target-derived tuning.

The active-triad PSD ceiling audit is:

[`p_taucov_active_triad_psd_ceiling_audit.md`](p_taucov_active_triad_psd_ceiling_audit.md)

It shows that this is not merely a bad choice of minimal `Phi/B/P` weights. The
current active triad itself is too narrow for the PSD covariance survival route
under the frozen specificity gates.

## Claim Boundary

Allowed statement:

> The reduced branch-Jacobian blocker list has been narrowed after reusing the frozen Q-range and full-action-domain projectors.

Forbidden statement:

> The reduced branch-Jacobian has been constructed, scored, or shown to validate Tau Core.
