# P-TauCov Q-Range Branch-Response Preflight

Freeze ID: `P_TAUCOV_Q_RANGE_BRANCH_RESPONSE_PREFLIGHT_v1`

Status:

`P_TAUCOV_Q_RANGE_BRANCH_RESPONSE_PREFLIGHT_FAIL_NO_SCORING`

## Purpose

This preflight retests the minimal branch-response contrast using the frozen
orthogonal range projector `Q_range`, rather than repeated multiplication by
the non-idempotent cleaner `Q_clean`.

```text
v_branch = E[:, B_BRANCH_RESPONSE] - E[:, PHI_PARENT_SOURCE]
v_Q = Q_range v_branch
K_Q = v_Q v_Q^T
```

It does not inspect target residual scores and does not authorize empirical scoring.

## Metrics

| Quantity | Value |
|---|---:|
| raw vector norm | `1.154700538379251` |
| Q-range vector norm | `1.0523954138893142e-15` |
| Q-range retention | `9.11401163254385e-16` |
| Q-range closure error | `0.8675145371499277` |
| projection leakage | `0.09598481368096215` |
| max family energy share | `0.240471382653207` |
| diagonal energy share | `0.05985323919754852` |
| passed gates | `4 / 6` |

## Claim Boundary

Allowed statement:

> The minimal branch-response contrast has been retested with the frozen Q-range projector.

Forbidden statement:

> This preflight validates Tau Core, authorizes scoring, or establishes empirical survival.
