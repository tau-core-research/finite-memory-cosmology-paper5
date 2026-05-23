# P-TauCov Finite-Dimensional Linear-Source Packet Gate

Status: source gate / no concrete source matrices / no linear objects / no
metric evaluation / no scoring authorization.

This gate specifies the finite-dimensional source objects required before the
linear matrices `L0_B`, `R_B`, `A_Phi`, `A_B`, and `P0` can be derived.

## Required Source Objects

| Source object | Role | Required for |
| --- | --- | --- |
| `K_B` | Branch potential Hessian component. | `L0_B` |
| `Gamma_B` | Branch relaxation/damping regularizer. | `L0_B` |
| `D_Phi_K_B` | Parent derivative of branch Hessian. | `R_B` |
| `D_Phi_J_B` | Parent derivative of branch source term. | `R_B` |
| `G_Phi` | Direct parent morphology derivative. | `A_Phi` |
| `G_B` | Branch morphology derivative. | `A_B` |
| `P0_SOURCE` | Fixed morphology projection source. | `P0` |

## Required Packet Files

```text
data/p_taucov/linear/source/K_B.csv
data/p_taucov/linear/source/Gamma_B.csv
data/p_taucov/linear/source/D_Phi_K_B.csv
data/p_taucov/linear/source/D_Phi_J_B.csv
data/p_taucov/linear/source/G_Phi.csv
data/p_taucov/linear/source/G_B.csv
data/p_taucov/linear/source/P0_source.csv
evidence/p_taucov_linear_source_manifest.yaml
evidence/p_taucov_linear_source.sha256
evidence/p_taucov_linear_source_leakage_audit.csv
```

## Acceptance Conditions

The source packet may be accepted only if:

```text
all required source files exist;
dimensions are compatible with the frozen coordinate basis and P_red domain;
source origins are target-blind and match the Tau-side definitions;
manifest declares OutcomeInformationUsed=false;
manifest declares ResidualInformationUsed=false;
manifest declares ScoreInformationUsed=false;
manifest declares PostScoringLocalizationUsed=false;
hash file matches every source object;
leakage audit contains no failing required checks.
```

## Claim Boundary

Allowed statement:

```text
The finite-dimensional linear-source packet gate is declared.
```

Forbidden statement:

```text
The finite-dimensional source objects or derived linear matrices are frozen.
```
