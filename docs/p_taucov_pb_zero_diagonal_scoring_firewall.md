# P-TauCov PB Zero-Diagonal Scoring Firewall

Freeze ID: `P_TAUCOV_PB_ZERO_DIAGONAL_SCORING_FIREWALL_v1`

Status: `P_TAUCOV_PB_ZERO_DIAGONAL_SCORING_FIREWALL_BLOCKED`

## Purpose

This firewall checks whether the frozen `PB_ZERO_DIAGONAL_OUTER_PRODUCT`
object is ready for a future empirical scorecard. It deliberately does
not authorize scoring by itself.

## Missing Items

- `PB-FW_POLICY_SCORECARD_SCRIPT_FREEZE`
- `PB-FW_POLICY_FOLD_POLICY`
- `PB-FW_POLICY_NULL_COMPARATORS`
- `PB-FW_POLICY_DF_COVARIANCE_POLICY`
- `PB-FW_POLICY_SURVIVAL_KILL_GATES`

## Interpretation

A frozen object is now available, but a separate scorecard-script freeze,
fold policy, null-comparator policy, df/covariance policy, and survival/
kill-gate policy must be declared for this object before scoring.

## Links

- [`p_taucov_pb_zero_diagonal_object_freeze.md`](p_taucov_pb_zero_diagonal_object_freeze.md)
- [`p_taucov_pb_interaction_object_preflight.md`](p_taucov_pb_interaction_object_preflight.md)

## Claim Boundary

Allowed statement:

> The PB zero-diagonal object has a scoring firewall that records which pre-scoring policies remain missing.

Forbidden statement:

> This firewall authorizes scoring, reports survival, or validates Tau Core.
