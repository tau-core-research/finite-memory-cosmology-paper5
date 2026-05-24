# P-TauCov PB Zero-Diagonal Object Freeze

Freeze ID: `P_TAUCOV_PB_ZERO_DIAGONAL_OBJECT_FREEZE_v1`

Status: `P_TAUCOV_PB_ZERO_DIAGONAL_OBJECT_FROZEN_NO_SCORING`

## Purpose

This packet freezes the first admissible object candidate derived from
the frozen `P*B` interaction coordinate:

```text
PB_ZERO_DIAGONAL_OBJECT = zero_diagonal(
  outer_product(frozen_PB_interaction_coordinate)
)
```

The zero-diagonal convention is a fixed covariance-response convention
that excludes pure variance inflation. It does not use the Q-clean
projector as a source and does not use family masks or target outcomes.

## Frozen Preflight Metrics

- Q-clean matrix support: `0.2599617634925701`
- max family block energy share: `0.0976084093882015`
- diagonal energy share: `0.0`
- matrix SHA256: `14dd2f5d173caa602b27945e20eab9a3416ba9e7cca4a51c604b8791da05e579`

## Links

- [`p_taucov_pb_interaction_object_preflight.md`](p_taucov_pb_interaction_object_preflight.md)
- [`p_taucov_pb_interaction_coordinate_freeze.md`](p_taucov_pb_interaction_coordinate_freeze.md)

## Claim Boundary

Allowed statement:

> A target-blind off-diagonal `P*B` covariance-response object has been frozen for later scoring-authorization review.

Forbidden statement:

> This object has survived empirical scoring, detects Tau Core, or validates the theory.
