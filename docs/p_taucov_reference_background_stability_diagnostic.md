# P-TauCov Reference Background Stability Diagnostic

Status: `P_TAUCOV_REFERENCE_BACKGROUND_ACTIVE_SADDLE_STABILITY_NOT_PROVEN_NO_SCORING`.

This diagnostic tests whether the stationary reference background is
already a locally stable energy background under the active scaffold
Hessian. It does not use target residuals, score outcomes, or empirical
covariance performance.

## Result

- minimum active Hessian eigenvalue: `-0.8168772564552302`
- maximum active Hessian eigenvalue: `0.5738399867980275`
- negative eigenvalue count: `2`
- positive eigenvalue count: `1`
- active Hessian positive semidefinite: `False`
- full stability proven: `False`

The active scaffold is an indefinite response witness, not yet a
positive local energy Hessian. The `S_rest` packet stabilizes the
inactive complement and prevents leakage, but it cannot by itself
turn the active witness Hessian into a positive energy form without
changing the witness.

## Consequence

The background-stability blocker remains open. The next derivation
must explain whether the active Hessian is a response operator rather
than an energy Hessian, or must supply a constrained/dynamical
stability theorem that preserves the projection-essential witness.

## Claim Boundary

Allowed: the current active scaffold has a stationary reference point
and an explicit saddle-like Hessian diagnostic.

Forbidden: this is not a stable Tau Core background, not a covariance
scorecard, and not measurement validation.
