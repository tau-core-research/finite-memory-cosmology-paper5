# P-TauCov Reference-State And Reduced-Domain Freeze

Status: freeze policy / no concrete reference state / no reduced-domain matrix /
no metric evaluation / no scoring authorization.

The Tau-side definition spec requires derivatives at a reference state and an
invertible reduced branch domain. This artifact declares the freeze policy for
those objects without yet supplying their concrete values.

## Required Reference Objects

| Item | Policy |
| --- | --- |
| `Phi_0` | Select from a target-blind coordinate/source convention. |
| `B_star(Phi_0)` | Solve `F_B(Phi_0,B)=0` under the declared branch equation. |
| `P_null` | Declare null directions before inversion. |
| `P_gauge` | Exclude gauge-like or coordinate redundancy directions. |
| `P_forbidden` | Exclude outcome-derived directions if present. |
| `P_red` | Build `P_red = I - P_null - P_gauge - P_forbidden`. |
| `InvertibilityAudit` | Verify or predeclare regularization of `L_B^red`. |

## Hard Rule

`Phi_0`, `P_null`, `P_gauge`, and `P_forbidden` must not be selected from:

```text
held-out residuals;
P5C v3 family gains;
OOS DeltaNLL pattern;
linear specificity metric pass/fail result;
post-hoc support localization.
```

## Claim Boundary

Allowed statement:

```text
The reference-state and reduced-domain freeze policy is declared.
```

Forbidden statement:

```text
The reference state or reduced branch domain is already frozen.
```
