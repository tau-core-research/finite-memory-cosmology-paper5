# P-TauCov Non-Smooth Parent-Hessian Constraint

Status: `THEORY_GATE_REQUIRED_BEFORE_NEXT_SCORING`

## Why This Gate Exists

The expanded parent-operator scorecard produced a strong positive covariance
gain, but it did not survive the required null suite. The decisive failure was
not a morphology-null or projection-null duplication. The decisive failure was
stronger:

`GENERIC_RANDOM_SMOOTH_PSD` beat the declared expanded parent-operator object.

This means the current object is still too close to a generic smooth covariance
shape. A future candidate must therefore be constrained by a parent-Hessian
feature that a generic smooth PSD covariance null cannot reproduce.

## Required New Ingredient

A future P-TauCov object must include at least one target-blind parent-Hessian
constraint of the following kind:

1. **Non-commuting operator structure**
   The object must depend on an explicitly declared non-commutator or
   commutator-residue term, not only on a smooth PSD covariance envelope.

2. **Spectral locality**
   The object must identify a compact set of parent-Hessian modes or a
   band-limited residue that is not equivalent to smooth redshift covariance.

3. **Orientation or sign residue**
   If orientation is used, the sign convention must come from a target-blind
   parent-side anchor and cannot be selected from score outcomes.

4. **Generic smooth PSD exclusion**
   Before scoring, the candidate must show that its declared structure is not
   well represented by the frozen generic smooth PSD null family.

5. **Dominance resistance**
   The candidate must retain support after family, clock, and context balancing.
   A candidate whose positive support collapses into one family, clock block, or
   context block is not eligible for survival scoring.

## Minimum Pre-Score Metrics

The next candidate should not be score-authorized unless a no-score structural
packet reports:

- `smooth_psd_projection_overlap`
- `parent_hessian_commutator_norm`
- `spectral_residue_rank`
- `orientation_anchor_margin`, if orientation is used
- `balanced_retained_norm`
- `max_family_share`
- `max_clock_share`
- `max_context_share`

The exact thresholds must be frozen before empirical scoring. Thresholds must
not be chosen from target residuals or score outcomes.

## Forbidden Shortcut

The following is not allowed:

> Build another PSD covariance object, observe that it improves the diagonal
> baseline, and then interpret the improvement as Tau-specific.

Positive covariance improvement is no longer enough. The next claim boundary is:

> Tau-specificity requires a parent-Hessian residue that survives generic smooth
> PSD exclusion before scoring.

## Recommended Next Artifact

`p_taucov_parent_hessian_residue_gate_v1`

This should be a no-score artifact that defines the parent-Hessian residue,
declares the allowed operator class, freezes the exclusion metrics, and only
then decides whether a new empirical scorecard may be authorized.
