# P-TauCov Linear-Object Derivation Gate

Status: derivation gate / no concrete linear matrices / no covariance response
/ no metric evaluation / no scoring authorization.

The reference-domain packet freezes `Phi_0` and `P_red`. This gate defines what
must be supplied before the Tau-side linear objects can be accepted.

## Required Linear Objects

| Object | Required origin | Expected file |
| --- | --- | --- |
| `L0_B` | `P_red D_B F_B|(Phi_0,B_*) P_red` | `data/p_taucov/linear/L0_B.csv` |
| `R_B` | `- P_red D_Phi F_B|(Phi_0,B_*)` | `data/p_taucov/linear/R_B.csv` |
| `A_Phi` | `D_Phi M_parent|(Phi_0,B_*)` | `data/p_taucov/linear/A_Phi.csv` |
| `A_B` | `D_B M_parent|(Phi_0,B_*)` | `data/p_taucov/linear/A_B.csv` |
| `P0` | `P_morph(Phi_0,B_*(Phi_0))` or declared coordinate projection | `data/p_taucov/linear/P0.csv` |

## Required Packet Files

```text
data/p_taucov/linear/L0_B.csv
data/p_taucov/linear/R_B.csv
data/p_taucov/linear/A_Phi.csv
data/p_taucov/linear/A_B.csv
data/p_taucov/linear/P0.csv
evidence/p_taucov_linear_object_derivation_manifest.yaml
evidence/p_taucov_linear_object_derivation.sha256
evidence/p_taucov_linear_object_derivation_leakage_audit.csv
```

## Acceptance Conditions

The packet may be accepted only if:

```text
all required objects exist;
matrix dimensions match the frozen coordinate basis and P_red domain;
object origins match the declared Tau-side routes;
manifest declares OutcomeInformationUsed=false;
manifest declares ResidualInformationUsed=false;
manifest declares ScoreInformationUsed=false;
manifest declares PostScoringLocalizationUsed=false;
hash file matches every matrix;
leakage audit contains no failing required checks.
```

## Claim Boundary

Allowed statement:

```text
The linear-object derivation gate is declared.
```

Forbidden statement:

```text
The Tau-side linear matrices or covariance response are frozen.
```
