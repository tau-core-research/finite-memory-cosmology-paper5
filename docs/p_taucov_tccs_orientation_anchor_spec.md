# P-TauCov TCCS Orientation Anchor Spec

Freeze ID: `P_TAUCOV_TCCS_ORIENTATION_ANCHOR_SPEC_v1`

Status:

`P_TAUCOV_TCCS_ORIENTATION_ANCHOR_SPEC_DEFINED_NO_ANCHOR_FROZEN`

## Purpose

The TCCS object is signed:

```text
Orient_+([L_B_red, P_morph]; J_tau)
```

Therefore the sign must be fixed by a target-blind parent-side orientation anchor, not by empirical score behavior.

## Candidate Anchor Classes

| Anchor | Meaning | Current status |
|---|---|---|
| `JTAU_A_PARENT_COMPLEX_STRUCTURE` | fixed skew/complex structure of the reduced parent coordinates | `SOURCE_NOT_FROZEN` |
| `JTAU_B_BRANCH_ORDER_ORIENTATION` | orientation induced by the declared branch basis order | `SOURCE_NOT_FROZEN` |
| `JTAU_C_HESSIAN_SKEW_PAIRING` | antisymmetric pairing from the reduced Hessian block algebra | `SOURCE_NOT_FROZEN` |

## Freeze Rule

An anchor may be frozen only if all of the following are true:

1. its source exists before TCCS object construction;
2. its sign convention is independent of target residuals and empirical score signs;
3. it does not use the dominant family or clock cell identified by previous failed scorecards;
4. the anchor is a parent-side convention, not a data-fit convention;
5. the selected anchor is recorded before any orientation-margin or scorecard result is viewed.

## Forbidden Moves

- Do not flip the commutator sign after seeing alignment.
- Do not choose between anchor candidates after comparing score outcomes.
- Do not use the previous sign-flip control as a positive result.
- Do not promote a signed diagnostic if the primary frozen route fails.

## Claim Boundary

Allowed statement:

> The TCCS orientation-anchor spec defines what a valid target-blind sign convention would require.

Forbidden statement:

> A TCCS orientation anchor has already been selected, frozen, or empirically validated.
