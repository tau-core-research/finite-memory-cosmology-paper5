# D-Branch Derivative-Regularized Selector

Status: D_BRANCH_DERIVATIVE_REGULARIZED_SELECTOR_REGISTERED.

This selector adds an internal D-branch curvature guard to the normalized criteria-set-3 smoke selector. It does not use K2, K1, target signs, amplitude fitting, or measurement-validation language.

## Registered Rule

- Base score: normalized criteria-set-3 score
- Regularity metric: median low-depth |D''| / max(|D'|, epsilon)
- Low-depth range: z < 0.8
- Curvature budget: 1.0
- Regularization weight: 1.0

## Boundary

No K2 change, no rho>4, no K1 refit, no target-sign gate, and no measurement validation.
