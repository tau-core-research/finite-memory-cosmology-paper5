# P-TauCov Reduced-Jacobian Current Blocker Rollup

Freeze ID: `P_TAUCOV_REDUCED_JACOBIAN_CURRENT_BLOCKER_ROLLUP_v1`

Status:

`P_TAUCOV_REDUCED_JACOBIAN_CURRENT_BLOCKERS_REDUCED_STILL_BLOCKED_NO_SCORING`

## Purpose

This rollup updates the reduced-Jacobian blocker state after the mediated
parent-forcing and projected morphology derivative audits. It does not build
`J_response`, does not generate `delta_C_Tau`, and does not authorize scoring.

## Current Blocker Table

| Object | Current status | Still blocks | Evidence |
|---|---|---:|---|
| `ReferenceState` | `CANDIDATE_SPECIFIED_NOT_FROZEN` | `True` | `docs/p_taucov_reference_state_candidate_spec.md` |
| `L_B_red` | `COMPUTABLE_IN_CURRENT_BRANCH_ROW` | `False` | `docs/p_taucov_branch_equation_completion_audit.md` |
| `D_Phi_F_B` | `RESOLVED_AS_MEDIATED_CHAIN` | `False` | `docs/p_taucov_mediated_parent_forcing_chain_audit.md` |
| `D_B_M_proj` | `STRICT_LINEAR_PROVIDED` | `False` | `docs/p_taucov_projected_morphology_derivative_audit.md` |
| `DynamicalStability` | `RESPONSE_ENERGY_SPLIT_PASS_FULL_DYNAMICS_OPEN` | `True` | `docs/p_taucov_response_energy_split_packet.md` |
| `CovarianceMap` | `DECLARED_TARGET_BLIND_PSD_LIFT` | `False` | `docs/p_taucov_covariance_map_declaration.md` |

## Current Meaning

The previous source blockers have narrowed:

```text
D_Phi_F_B -> resolved as mediated Phi -> P_morph -> B chain
D_B_M_proj -> strict-linear provided as P0 A_B
L_B_red -> computable in the current branch row
CovarianceMap -> target-blind PSD lift declared
```

The remaining primary blockers are:

```text
ReferenceState;DynamicalStability
```

## Claim Boundary

Allowed statement:

> The reduced-Jacobian blocker list has been narrowed, but the object is still
> not complete.

Forbidden statement:

> `J_response` or `delta_C_Tau` has been constructed, empirical scoring is
> authorized, or Tau Core has been validated.
