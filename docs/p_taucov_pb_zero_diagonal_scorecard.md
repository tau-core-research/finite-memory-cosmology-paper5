# P-TauCov PB Zero-Diagonal Scorecard

Status: `P_TAUCOV_PB_ZERO_DIAGONAL_PRIMARY_SCORECARD_DOES_NOT_SURVIVE_NO_CLAIM`

This is the authorized primary covariance scorecard for the frozen
PB zero-diagonal covariance-response object. It does not authorize
survival language, measurement validation, or a Tau Core validation claim.

## Key Numbers

- rows: 36
- families: 3
- clock positions: 12
- primary OOS Delta NLL: -675.4214689498501
- primary OOS Delta NLL without context blocks: -470.33028559666553
- strongest null primary OOS Delta NLL: 232.6856008891671
- gates passed: 1/8

## Interpretation

The object does not survive the frozen global P-TauCov scorecard. The
family aggregate is positive, but clock/context aggregates are strongly
negative and the object does not defeat the strongest required null.
This is therefore a branch-local diagnostic anomaly at most, not a
global covariance survivor.

Positive Delta NLL means the declared covariance deformation beats the
diagonal covariance baseline on that score. A failed survival gate remains
a failed survival gate even if individual folds or diagnostics look
interesting.
