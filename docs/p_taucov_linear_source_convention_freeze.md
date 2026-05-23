# P-TauCov Minimal Linear-Source Convention Freeze

Status: source-convention freeze / no concrete source matrices / no derived
linear objects / no metric evaluation / no scoring authorization.

This artifact freezes the minimal target-blind source conventions that may be
used to build a first finite-dimensional source packet. These conventions are
baseline choices, not empirical evidence and not a Tau signal.

## Frozen Minimal Conventions

| Source object | Convention |
| --- | --- |
| `K_B` | identity on retained reduced-domain coordinates |
| `Gamma_B` | zero regularizer |
| `D_Phi_K_B` | zero derivative |
| `D_Phi_J_B` | identity parent-to-branch on shared retained axes |
| `G_Phi` | identity parent-to-morphology on shared retained axes |
| `G_B` | identity branch-to-morphology on shared retained axes |
| `P0_SOURCE` | identity on retained morphology coordinates |

## Guardrail

The minimal source packet built from these conventions is allowed only as a
target-blind baseline source packet. It must not be interpreted as a positive
P-TauCov result, and it must not be tuned after any metric or score is seen.

## Claim Boundary

Allowed statement:

```text
Minimal target-blind linear-source conventions are frozen.
```

Forbidden statement:

```text
Concrete source matrices, derived linear objects, covariance response, or
P-TauCov score are available.
```
