# P-TauCov Q-Native Branch-Response Curvature Preflight

Freeze ID: `P_TAUCOV_Q_NATIVE_BRANCH_RESPONSE_CURVATURE_PREFLIGHT_v1`

Status:

`P_TAUCOV_Q_NATIVE_BRANCH_RESPONSE_CURVATURE_PREFLIGHT_FAIL_NO_SCORING`

## Purpose

This preflight tests the minimal target-blind Q-native branch-response
curvature candidate:

```text
v_branch = E[:, TEMPLATE_B_BRANCH_RESPONSE] - E[:, TEMPLATE_PHI_PARENT_SOURCE]
J_response = Q_clean v_branch
K_Q = J_response J_response^T
```

It does not inspect target residual scores and does not authorize empirical
scoring.

## Metrics

| Quantity | Value |
|---|---:|
| raw vector norm | `1.154700538379251` |
| clean vector norm | `6.833497769192341e-16` |
| support retention | `5.917982664824861e-16` |
| Q-native closure error | `0.7888917899683725` |
| projection leakage | `0.04864733816243413` |
| max family energy share | `0.41821620812162646` |
| diagonal energy share | `0.1072263245190529` |
| passed gates | `5 / 8` |

## Interpretation

This is a construction preflight only. If it passes, the candidate may be
considered for a future scoring manifest. If it fails, the minimal
branch-response contrast is not enough and a richer reduced-branch Jacobian is
needed.

## Claim Boundary

Allowed statement:

> A minimal Q-native branch-response curvature candidate has been inspected at pre-score level.

Forbidden statement:

> The branch-response curvature candidate validates Tau Core, authorizes scoring, or establishes empirical survival.
