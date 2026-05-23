# P-TauCov P3 Balanced Structural Null Audit

Audit ID: `P_TAUCOV_P3_BALANCED_STRUCTURAL_NULL_AUDIT_v1`

Status:

`P_TAUCOV_P3_BALANCED_STRUCTURAL_NULL_AUDIT_PASS_NO_SCORING`

## Purpose

This audit checks whether the frozen P3 balanced object is merely a row-order, clock-shift, family-cycle, support-shuffle, or random symmetric off-diagonal pattern.

The sign flip is tracked separately as an orientation control. It is not included in the absolute structured-null maximum because every signed kernel has absolute correlation one with its own negative.

It uses no target residuals and authorizes no empirical scoring.

## Summary Metrics

```text
SignFlipCorrelation = -1.0
MaxStructuredAbsCorrelation = 0.45781430645125276
RandomMedianAbsCorrelation = 0.030709358467327683
RandomMaxAbsCorrelation = 0.08222484731109514
```

## Interpretation

Passing this audit means only that the frozen P3 balanced object is structurally nontrivial relative to the declared target-blind nulls.

It does not mean that the object predicts data, survives a scorecard, or validates Tau Core.

## Claim Boundary

Allowed statement:

> The frozen P3 balanced object is not identical to the declared structural null patterns and remains eligible for later protocol design.

Forbidden statement:

> The structural null audit establishes a Tau signal or empirical survival.
