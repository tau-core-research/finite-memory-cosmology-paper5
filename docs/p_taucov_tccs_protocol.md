# P-TauCov TCCS Protocol

Freeze ID: `P_TAUCOV_TCCS_PROTOCOL_v1`

Status:

`P_TAUCOV_TCCS_PROTOCOL_DEFINED_NO_OBJECT_NO_SCORING`

## Name

Short name:

```text
TCCS
```

Long name:

```text
Tau Commutator Curvature Signature
```

Formal reading:

```text
oriented reduced parent-Hessian commutator signature
```

## Motivation

The previous P-TauCov ladder produced a useful negative-control result. Direct shape, covariance, diagonal-orthogonal, and P3 balanced candidates did not produce a surviving Tau-specific empirical signal.

The failure pattern suggests that the next Tau-side object should not be another shape or covariance kernel. It should test whether the parent-side branch response fails to commute with the morphology/projection readout.

## Candidate Class

The intended object class is:

```text
C_tau = [L_B_red, P_morph] = L_B_red P_morph - P_morph L_B_red
```

The scoreable form, if it ever passes pre-score gates, is:

```text
T_tau = Normalize(
  Pi_bal
  Pi_perp
  Orient_+([L_B_red, P_morph]; J_tau)
  Pi_perp
  Pi_bal
)
```

where:

- `L_B_red` is a target-blind reduced parent-Hessian or response operator;
- `P_morph` is the morphology/projection readout operator;
- `Pi_perp` removes projection-null and morphology-null directions;
- `Pi_bal` removes family/clock nuisance directions;
- `J_tau` is a target-blind parent-side orientation anchor;
- `Orient_+` rejects the object if the orientation margin is not positive.

## Required Gates

| Gate | Requirement | Threshold |
|---|---|---|
| `TCCS-G1` | parent Hessian source declared before score access | required |
| `TCCS-G2` | object is a commutator, not direct shape | required |
| `TCCS-G3` | projection-null overlap after orthogonalization | `<=0.50` |
| `TCCS-G4` | morphology-null overlap after orthogonalization | `<=0.50` |
| `TCCS-G5` | balance retention and leakage | `retention>=0.20`, `leakage<1e-10` |
| `TCCS-G6` | family balance | `max_family_energy_share<=0.50` |
| `TCCS-G7` | diagonal control | `diagonal_share<=0.10` |
| `TCCS-G8` | parent orientation anchor | `orientation_margin>0` |
| `TCCS-G9` | sign-flip not promoted to survival | required |
| `TCCS-G10` | target blindness | required |

## Forbidden Moves

- Do not choose the sign from empirical score behavior.
- Do not use the previous strongest family-clock cell as a template.
- Do not treat PSD projection as primary unless orientation retention is separately frozen and passes.
- Do not report signed diagnostic success as covariance survival.
- Do not call this Tau Core validation without a frozen held-out scorecard pass.

## Claim Boundary

Allowed statement:

> TCCS is a proposed next Tau-side observable class designed to avoid the failure modes exposed by the P3 balanced scorecard.

Forbidden statement:

> TCCS has produced a Tau signal, survived empirical scoring, or validated Tau Core.
