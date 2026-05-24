# P-TauCov Expanded Parent-Operator Scoring Firewall

Freeze ID: `P_TAUCOV_EXPANDED_PARENT_OPERATOR_SCORING_FIREWALL_v1`

Status:

`P_TAUCOV_EXPANDED_PARENT_OPERATOR_SCORING_BLOCKED_FREEZE_REQUIRED`

## Purpose

The expanded parent-operator PSD artifact passes structural no-score
specificity preflight. This firewall records what must still be frozen before
any empirical scorecard may be run.

## Current Ready Items

- structural preflight pass: `True`
- candidate hash ready: `True`
- source hash ready: `True`
- domain hash ready: `True`
- scorecard script frozen: `True`
- fold policy frozen: `True`
- null comparator policy frozen: `True`
- DF/covariance policy frozen: `True`
- survival/kill gates frozen: `True`

## Missing Before Scoring

```text
ESO-FW10_FINAL_MANIFEST_READY
```

Required missing freezes:

- expanded scorecard script hash;
- fold policy;
- null comparator policy for expanded non-outcome axes;
- degrees-of-freedom and covariance policy;
- survival and kill gates;
- final manifest binding all hashes and policies.

## Claim Boundary

Allowed statement:

> The expanded parent-operator artifact is structurally ready for a future
> scoring-freeze packet.

Forbidden statement:

> This firewall authorizes empirical scoring, survival language, or Tau Core
> validation.
