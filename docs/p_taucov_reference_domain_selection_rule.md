# P-TauCov Reference-Domain Selection Rule

Status: target-blind selection rule / no concrete `Phi_0` / no concrete basis /
no reduced-domain matrix / no linear packet / no metric evaluation / no scoring
authorization.

This note sharpens the reference-domain freeze policy into a selection rule. It
does not choose a numerical reference state. It only declares how the reference
state and excluded subspaces may be chosen once the coordinate basis and Tau-side
operators exist.

## Selection Rule

| Object | Target-blind rule |
| --- | --- |
| `Phi_0` | Choose the frozen coordinate-basis origin if physically declared; otherwise choose the frozen coordinate-basis center. The choice must be made from the coordinate/source convention only. |
| `B_*(Phi_0)` | Solve `F_B(Phi_0,B)=0` only after `F_B` and `Phi_0` are frozen. |
| `P_null` | Use the span of exact zero modes of the candidate `L_B` on the frozen branch basis, declared before inversion. |
| `P_gauge` | Use the span of coordinate-duplicate or symmetry-redundant source modes defined by basis symmetries. If no such modes exist, an explicit no-redundancy certificate is required. |
| `P_forbidden` | Use the span of outcome-derived columns or target-leaking fields. If empty, an input-provenance leakage certificate is required. |
| `P_red` | Build `P_red = I - P_null - P_gauge - P_forbidden` only after all three exclusion subspaces are frozen. |

## Forbidden Inputs

The selection rule must not use:

```text
held-out residuals
P5C v3 gains
OOS DeltaNLL
family localization after scoring
linear specificity metric result
post-hoc support localization
```

## What Is Still Missing

This artifact does not supply:

```text
concrete Phi_0
concrete coordinate basis
concrete null/gauge/forbidden bases
concrete P_red
linear model packet
linear specificity metric evaluation
P-TauCov scoring authorization
```

## Claim Boundary

Allowed statement:

```text
A target-blind reference-domain selection rule is declared.
```

Forbidden statement:

```text
The P-TauCov reference state or reduced domain has been frozen.
```

## Next Gate

The next gate is to freeze a coordinate/source basis, then apply this rule to
produce concrete `Phi_0`, `P_null`, `P_gauge`, `P_forbidden`, and `P_red`
artifacts with provenance hashes.
