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

## Claim Boundary

Allowed statement:

> The reduced branch-Jacobian blocker list has been narrowed after reusing the frozen Q-range and full-action-domain projectors.

Forbidden statement:

> The reduced branch-Jacobian has been constructed, scored, or shown to validate Tau Core.
