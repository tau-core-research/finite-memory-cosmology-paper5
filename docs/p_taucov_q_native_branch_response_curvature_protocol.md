# P-TauCov Q-Native Branch-Response Curvature Protocol

Freeze ID: `P_TAUCOV_Q_NATIVE_BRANCH_RESPONSE_CURVATURE_PROTOCOL_v1`

Status:

`P_TAUCOV_Q_NATIVE_BRANCH_RESPONSE_CURVATURE_PREFLIGHT_FAIL_NO_SCORING`

## Purpose

This protocol instantiates the highest-priority Q-native route:

```text
QN_ROUTE_4_BRANCH_RESPONSE_CURVATURE
```

It is a construction protocol only. It does not authorize empirical scoring.

## Theory Form

The target branch-response relation is:

```text
L_B^red delta B = -D_Phi F_B[delta Phi]
```

The Q-native score-space response is represented as:

```text
J_response = Q_clean v_branch
K_Q = J_response J_response^T
```

where:

```text
Q_clean = Pi_bal Pi_perp Pi_bal
```

and `v_branch` must be built from frozen parent-to-score coordinates, not from
target residual scores.

## Minimal Preflight Candidate

The first admissible minimal candidate is:

```text
v_branch = E[:, TEMPLATE_B_BRANCH_RESPONSE] - E[:, TEMPLATE_PHI_PARENT_SOURCE]
```

where `E` is the frozen parent-to-score embedding matrix.

This is not claimed to be the final physical response. It is the smallest
target-blind branch-response contrast that tests whether a Q-native response
can exist at all.

## Minimal Preflight Result

The minimal candidate has been tested:

[`p_taucov_q_native_branch_response_curvature_preflight.md`](p_taucov_q_native_branch_response_curvature_preflight.md)

Result:

```text
P_TAUCOV_Q_NATIVE_BRANCH_RESPONSE_CURVATURE_PREFLIGHT_FAIL_NO_SCORING
```

Key blocker:

```text
support_retention = 5.917982664824861e-16
```

The simple `B - Phi` contrast is nearly annihilated by the common clean
subspace. Therefore the minimal coordinate contrast is not a scoreable
Q-native branch-response object.

This does not close the branch-response route. It shows that the route needs a
real reduced-branch Jacobian:

```text
J_response = Q_range D_B M_proj (L_B^red)^(-1) D_Phi F_B
```

rather than a bare coordinate difference.

Here `Q_range` denotes the orthogonal projector onto the range of the common
cleaner. This projector is now frozen here:

[`p_taucov_q_range_projector_freeze.md`](p_taucov_q_range_projector_freeze.md)

Therefore the next branch-response preflight should test `Q_range` membership,
not repeated `Q_clean` closure.

## Q-Range Retest

The minimal branch-response contrast was retested with the frozen `Q_range`
projector:

[`p_taucov_q_range_branch_response_preflight.md`](p_taucov_q_range_branch_response_preflight.md)

Result:

```text
P_TAUCOV_Q_RANGE_BRANCH_RESPONSE_PREFLIGHT_FAIL_NO_SCORING
```

The decisive number is:

```text
QRangeRetention = 9.11401163254385e-16
```

Therefore the simple coordinate contrast:

```text
B_BRANCH_RESPONSE - PHI_PARENT_SOURCE
```

is not a viable Q-native branch-response object. The next branch-response
candidate must derive a real reduced Jacobian, not a coordinate difference.

## Pre-Score Gates

The preflight candidate must pass:

| Gate | Requirement |
|---|---|
| BRQ-G1 | source contrast declared before scoring |
| BRQ-G2 | `norm(v_branch) > 0` |
| BRQ-G3 | `norm(Q_clean v_branch) / norm(v_branch) >= 0.20` |
| BRQ-G4 | `norm(Q_clean K_Q Q_clean - K_Q) / norm(K_Q) <= 1e-10` |
| BRQ-G5 | projection leakage below frozen threshold |
| BRQ-G6 | max family energy share below frozen threshold |
| BRQ-G7 | diagonal energy share below frozen threshold |
| BRQ-G8 | no target residuals, no score outcomes, no scoring authorization |

## Claim Boundary

Allowed statement:

> A minimal Q-native branch-response curvature preflight has been specified without target residual scoring.

Forbidden statement:

> The protocol validates Tau Core, authorizes empirical scoring, or proves physical branch response.
