# P-TauCov Expanded Parent-Operator PSD Preflight

Freeze ID: `P_TAUCOV_EXPANDED_PARENT_OPERATOR_PSD_PREFLIGHT_v1`

Status:

`P_TAUCOV_EXPANDED_PARENT_OPERATOR_PSD_PREFLIGHT_PASS_NO_SCORING`

## Purpose

This preflight checks whether the expanded parent-side operator source clears
the structural PSD blockers that stopped the active `Phi/B/P` triad. It uses no
target residuals and no score outcomes.

## PSD Lift

```text
C_expanded = O_expanded O_expanded^T / ||O_expanded O_expanded^T||_F
```

where `O_expanded` is frozen in:

[`p_taucov_expanded_parent_operator_source_packet.md`](p_taucov_expanded_parent_operator_source_packet.md)

## Result

- diagonal energy share: `0.7635407354643848`
- effective-rank fraction: `0.36310855287953075`
- support entropy: `0.7501370237638488`
- active support count: `5`
- forbidden leakage norm: `0.0`
- failed gates: ``

## Interpretation

The expanded non-outcome parent-side source clears the structural PSD
specificity blockers that stopped the minimal `Phi/B/P` route. This is still a
pre-score structural result only. It does not authorize empirical scoring.

## Claim Boundary

Allowed statement:

> The expanded parent-operator PSD artifact passes target-blind structural
> specificity preflight.

Forbidden statement:

> This preflight is empirical survival, scoring authorization, or Tau Core
> validation.
