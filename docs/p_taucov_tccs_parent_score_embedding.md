# P-TauCov TCCS Parent-To-Score Embedding

Freeze ID: `P_TAUCOV_TCCS_PARENT_SCORE_EMBEDDING_v1`

Status:

`P_TAUCOV_TCCS_PARENT_SCORE_EMBEDDING_FROZEN_NO_OBJECT_NO_SCORING`

## Purpose

This artifact freezes the parent-to-score embedding needed by the TCCS route.
It maps the 8-dimensional Tau-coordinate parent space into the 36-row
family-clock score geometry.

The embedding reuses the already validated target-blind coordinate bridge:

```text
evidence/p_taucov_epsilon_p3_coordinate_bridge.csv
```

It does not build the TCCS object and does not authorize scoring.

## Metrics

| Quantity | Value |
|---|---:|
| empirical rows | `36` |
| Tau coordinates | `8` |
| active embedding columns | `4` |
| embedding rank | `4` |
| max active-column abs correlation | `0.028643689079269605` |
| row-norm min | `0.23968063858108826` |
| row-norm max | `0.4305914548851069` |

## Claim Boundary

Allowed statement:

> A target-blind parent-to-score embedding has been frozen for the TCCS route.

Forbidden statement:

> The embedding constructs a TCCS object, authorizes scoring, or produces a Tau signal.
