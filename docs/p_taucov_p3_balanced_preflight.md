# P-TauCov P3 Balanced Preflight

Audit ID: `P_TAUCOV_P3_BALANCED_PREFLIGHT_v1`

Status:

`P_TAUCOV_P3_BALANCED_PREFLIGHT_READY_NO_CANDIDATE_NO_SCORING`

## Purpose

This preflight applies the frozen clock/family balance projector to the target-blind P3 parent-side core-mixing operator. It checks whether nontrivial structure remains after removing intercept, family, and clock-block nuisance directions.

This is not a candidate and not a scorecard.

## Construction

```text
K_parent = bridge P3 P3^T bridge^T
K_balanced = R_balance K_parent R_balance
K_preflight = offdiag(K_balanced) / ||offdiag(K_balanced)||_F
```

The off-diagonal matrix is emitted only as a preflight artifact. It is not authorized for scoring.

## Metrics

```text
Rows = 36
BalanceRetention = 0.17126525621250607
BalancedRank = 1
MinEigenvalueBalanced = -2.8450047872033735e-16
MaxEigenvalueBalanced = 1.0000000000000004
DiagonalShareBeforeOffdiagRemoval = 0.2682447858602269
OffDiagonalShareBeforeOffdiagRemoval = 0.9633507849474153
BalanceProjectorLeftLeakageFrobenius = 9.968755665897105e-16
BalanceProjectorSandwichLeakageFrobenius = 1.4792507540671696e-15
```

## Interpretation

If retention is nonzero and balance leakage is numerical-noise level, then the parent-side P3 object has a score-independent balanced residual structure that can be audited further.

This still does not authorize scoring. A separate readiness and manifest gate would be required.

## Claim Boundary

Allowed statement:

> The target-blind P3 parent-side operator retains a balanced, nontrivial off-diagonal structure after family/clock nuisance removal.

Forbidden statement:

> The balanced P3 object has produced a Tau signal, survived P-TauCov scoring, or validated Tau Core.
