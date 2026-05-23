# P-TauCov Reference-State Resolution Gate

Freeze ID: `P_TAUCOV_REFERENCE_STATE_RESOLUTION_GATE_v1`

Status:

`P_TAUCOV_REFERENCE_STATE_RESOLUTION_REQUIRED_NO_OBJECT_NO_SCORING`

## Motivation

The reduced branch-Jacobian blocker resolution narrows the active blockers to:

```text
ReferenceState
L_B_red
D_Phi_F_B
D_B_M_proj
```

Among these, `ReferenceState` is first in dependency order. Without a
target-blind expansion point:

```text
(Phi0, B*(Phi0))
```

the branch equation cannot be linearized and the derivatives cannot be
evaluated.

## Required Conditions

A valid reference state must satisfy:

| Gate | Requirement |
|---|---|
| RS-G1 | `Phi0` selected from target-blind parent-coordinate convention |
| RS-G2 | `B*(Phi0)` solves the declared branch equation `F_B(Phi0,B)=0` |
| RS-G3 | null/gauge/forbidden directions excluded by frozen `P_red` |
| RS-G4 | no target residuals or score outcomes used |
| RS-G5 | reference state hash frozen before any Jacobian construction |

## Current Status

Existing evidence:

```text
evidence/p_taucov_reference_domain_freeze_summary.csv
```

shows:

```text
ReferenceStateFrozen = False
ConcreteValuesPresent = 0
```

Therefore the reference state remains unresolved.

## Next Artifact

The candidate-spec artifact has now been created:

```text
docs/p_taucov_reference_state_candidate_spec.md
scripts/build_p_taucov_reference_state_candidate_spec.py
scripts/validate_p_taucov_reference_state_candidate_spec.py
```

See:

[`p_taucov_reference_state_candidate_spec.md`](p_taucov_reference_state_candidate_spec.md)

Result:

```text
P_TAUCOV_REFERENCE_STATE_CANDIDATE_SPEC_DEFINED_BLOCKED_NO_SCORING
```

The current primary candidate is:

```text
Phi0=0; P0=0; B0=0
```

because it is stationary in the active scaffold. It is not yet a frozen
reference state because full stability and the full branch equation `F_B` are
not yet available.

## Claim Boundary

Allowed statement:

> The next reduced branch-Jacobian step is to freeze a target-blind reference-state route.

Forbidden statement:

> The reference-state gate constructs a physical branch solution, validates Tau Core, or authorizes scoring.
