# P-TauCov PB Interaction Coordinate Freeze

Freeze ID: `P_TAUCOV_PB_INTERACTION_COORDINATE_FREEZE_v1`

Status: `P_TAUCOV_PB_INTERACTION_COORDINATE_FROZEN_NO_OBJECT_NO_SCORING`

## Purpose

This packet freezes the first passing admissible source-coordinate candidate:
`COORD_PB_INTERACTION`.

The coordinate is derived target-blind from the already frozen parent-to-score
embedding as:

```text
COORD_PB_INTERACTION = center_normalize(
  TEMPLATE_P_MORPH_PROJECTION * TEMPLATE_B_BRANCH_RESPONSE
)
```

The term is interpreted only as a parent-side projection-branch interaction
coordinate. It is not a covariance object, not a Tau signal, and not a
scorecard result.

## Frozen Source Metrics

- Q-clean support: `0.4243943834779418`
- max family energy share: `0.3333333333333333`
- diagonal share if used as an outer product: `0.0572816039005382`
- coordinate SHA256: `3bba541f8ce56a053e35cff21d8d17bf62b77e7dea709d76eb2e81c05bacb8de`

## Links

- [`p_taucov_admissible_source_coordinate_extension.md`](p_taucov_admissible_source_coordinate_extension.md)
- [`p_taucov_parent_domain_curvature_source_requirement.md`](p_taucov_parent_domain_curvature_source_requirement.md)

## Claim Boundary

Allowed statement:

> A target-blind parent-derived `P*B` interaction coordinate has been frozen for later object-construction preflight.

Forbidden statement:

> This coordinate is a detected Tau signal, a covariance survivor, or an authorized empirical scorecard.
