# P-TauCov Clock/Family Balance Projector

Audit ID: `P_TAUCOV_CLOCK_FAMILY_BALANCE_PROJECTOR_v1`

Status:

`P_TAUCOV_BALANCE_PROJECTOR_FROZEN_NO_CANDIDATE_NO_SCORING`

## Purpose

The previous diagonal-orthogonal P-TauCov candidate failed because its positive alignment was family-localized and clock-inconsistent. This artifact freezes a target-blind balance projector that can be applied to any future parent-derived response kernel before scoring is authorized.

This is not a candidate and not a scorecard.

## Construction

Let `X` contain only target-blind nuisance directions:

- the intercept;
- registered family indicators;
- frozen clock-block indicators.

The balance projector is:

```text
R_balance = I - X (X^T X)^+ X^T
```

For any future parent-derived kernel `K_parent`, the admissible balanced form must be constructed before scoring as:

```text
K_balanced = R_balance K_parent R_balance
```

Then diagonal leakage must be removed or explicitly excluded by the signed statistic policy.

## Frozen Metrics

```text
Rows = 36
Families = 3
ClockBlocks = 3
ProjectorRank = 31
ProjectorTrace = 31.0
SymmetryErrorFrobenius = 0.0
IdempotenceErrorFrobenius = 2.8219680460491534e-15
FamilyIndicatorLeakageFrobenius = 3.608585100767701e-15
ClockIndicatorLeakageFrobenius = 3.746495106488568e-15
InterceptLeakageFrobenius = 9.976575541032722e-16
```

## Claim Boundary

This artifact authorizes only a preprocessing constraint for future P-TauCov candidate construction.

It does not authorize:

- scoring;
- a new candidate;
- covariance survival;
- Tau Core validation;
- measurement validation.

## Forbidden Use

This projector must not be used to tune a candidate after scoring. It must be applied only to a parent-derived response object that was declared before score access.
