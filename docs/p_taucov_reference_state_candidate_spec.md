# P-TauCov Reference-State Candidate Spec

Freeze ID: `P_TAUCOV_REFERENCE_STATE_CANDIDATE_SPEC_v1`

Status:

`P_TAUCOV_REFERENCE_STATE_CANDIDATE_SPEC_DEFINED_BLOCKED_NO_SCORING`

## Purpose

This artifact defines target-blind reference-state candidate routes for the
reduced branch-Jacobian program. It does not freeze a final reference state,
does not solve the full branch equation, and does not authorize scoring.

## Candidates

| Candidate | Expression | Stationarity | Stability | Branch equation |
|---|---|---|---|---|
| `RS_ORIGIN_ACTIVE_SCAFFOLD` | `Phi0=0; P0=0; B0=0` | `STATIONARY_IN_ACTIVE_SCAFFOLD` | `FULL_STABILITY_NOT_PROVEN` | `F_B_NOT_CONCRETE_FULL_BRANCH` |
| `RS_SOLVED_BRANCH_EQUATION` | `(Phi0,B*) such that F_B(Phi0,B*)=0` | `ROUTE_DEFINED_NOT_SOLVED` | `UNKNOWN_UNTIL_F_B_EXISTS` | `F_B_REQUIRED` |

## Interpretation

The active scaffold origin:

```text
Phi0=0; P0=0; B0=0
```

is the current best target-blind candidate because the active scaffold has a
stationary origin. However, it is not yet a full reference state for the
reduced branch-Jacobian because:

1. full stability still depends on the missing `S_rest` completion; and
2. the full branch equation `F_B` has not yet been declared.

## Claim Boundary

Allowed statement:

> A target-blind reference-state candidate route has been specified, with the active scaffold origin as the current primary candidate.

Forbidden statement:

> The reference state is frozen, the branch equation is solved, or empirical scoring is authorized.

## Next Gate

The next blocker is the branch-equation completion:

[`p_taucov_branch_equation_completion_gate.md`](p_taucov_branch_equation_completion_gate.md)
