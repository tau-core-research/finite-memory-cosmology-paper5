# P-TauCov Branch-Equation Completion Gate

Freeze ID: `P_TAUCOV_BRANCH_EQUATION_COMPLETION_GATE_v1`

Status:

`P_TAUCOV_BRANCH_EQUATION_COMPLETION_REQUIRED_NO_OBJECT_NO_SCORING`

## Motivation

The reference-state candidate spec identifies:

```text
Phi0=0; P0=0; B0=0
```

as the current primary target-blind reference-state candidate. The active
scaffold is stationary there, but the candidate is still blocked because:

1. the full branch equation `F_B` is not concrete; and
2. full stability depends on the missing `S_rest` completion.

## Required Completion

The next theory-side object is a branch equation:

```text
F_B(Phi,B)=0
```

with a reduced linearization:

```text
L_B^red = P_red D_B F_B|_(Phi0,B*) P_red
```

and parent forcing:

```text
D_Phi F_B|_(Phi0,B*)
```

## Minimum Conditions

Before the reduced branch-Jacobian can be built, a branch-equation completion
must satisfy:

| Gate | Requirement |
|---|---|
| BE-G1 | `F_B` declared independently of empirical score behavior |
| BE-G2 | origin candidate solves `F_B(Phi0,B*)=0`, or a new target-blind solution is given |
| BE-G3 | `L_B^red` computable on frozen `P_red` |
| BE-G4 | invertibility or regularization policy declared before scoring |
| BE-G5 | `D_Phi F_B` computable |
| BE-G6 | no target residuals, OOS score outcomes, or family-gain pattern used |

## Candidate Direction

The active scaffold suggests a local branch equation of the schematic form:

```text
F_B = D_B V_active + D_B S_rest
```

The active part alone gives a stationary origin, but it is not enough to prove
full stability. The missing `S_rest` must supply the stabilizing completion
without becoming an empirical fit term.

## Claim Boundary

Allowed statement:

> The next reduced branch-Jacobian blocker is a target-blind branch-equation completion around the active-scaffold origin.

Forbidden statement:

> The branch equation is solved, the reference state is frozen, or empirical scoring is authorized.
