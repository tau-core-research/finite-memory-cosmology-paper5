# P-TauCov Linear Model Packet Schema

Status: packet schema / no packet / no metric evaluation / no scoring
authorization.

The prescore evaluator requires a concrete target-blind linear model packet
before it can evaluate the linear specificity metrics. This schema defines the
required files. It does not create or approve the packet.

## Required Packet Files

| Object | Required path | Role |
| --- | --- | --- |
| `L0_B` | `data/p_taucov/linear/L0_B.csv` | linear branch relaxation operator |
| `R_B` | `data/p_taucov/linear/R_B.csv` | parent perturbation to branch forcing operator |
| `P_red` | `data/p_taucov/linear/P_red.csv` | projector onto invertible reduced branch domain |
| `A_Phi` | `data/p_taucov/linear/A_Phi.csv` | parent perturbation to morphology map |
| `A_B` | `data/p_taucov/linear/A_B.csv` | branch state to morphology map |
| `P0` | `data/p_taucov/linear/P0.csv` | fixed projection morphology map for `epsilon_P=0` |
| `coordinate_basis` | `data/p_taucov/linear/coordinate_basis.csv` | frozen observable/source coordinate basis |
| `packet_manifest` | `evidence/p_taucov_linear_model_packet.yaml` | hash manifest |
| `packet_sha256` | `evidence/p_taucov_linear_model_packet.sha256` | manifest hash |
| `leakage_audit` | `evidence/p_taucov_linear_model_packet_leakage_audit.csv` | no outcome leakage audit |

## Required Manifest Claims

The future manifest must state:

```text
lambda_B: 0
epsilon_P: 0
uses_target_residuals: false
uses_p5c_v3_outcome: false
metric_evaluation_authorized: true or false
p_taucov_scoring_authorized: false
```

## Boundary

Allowed statement:

```text
The required target-blind linear model packet schema is declared.
```

Forbidden statement:

```text
The linear model packet exists or passes the specificity audit.
```
