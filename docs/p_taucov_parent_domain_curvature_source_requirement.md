# P-TauCov Parent-Domain Curvature Source Requirement

Freeze ID: `P_TAUCOV_PARENT_DOMAIN_CURVATURE_SOURCE_REQUIREMENT_v1`

Status: `P_TAUCOV_PARENT_DOMAIN_CURVATURE_SOURCE_REQUIREMENT_DEFINED_NO_OBJECT_NO_SCORING`

## Why This Gate Exists

The compact spectral scorecard failed as an empirical covariance
survivor, and the TCCS/common-clean sequence showed a sharper
structural blocker: existing parent-derived candidates do not place
enough energy into the frozen projection-orthogonal, branch-balanced
clean subspace.

Therefore the next object is not another scorecard variant. It must be
a parent-domain curvature source whose clean-subspace support is a
pre-score property.

## Requirement Table

| Requirement | Policy | Meaning |
|---|---:|---|
| `PDCS-R1_PARENT_DOMAIN_ORIGIN` | `required` | The source must be derived from an explicit parent-domain curvature, Hessian, boundary, or self-adjoint-domain term. |
| `PDCS-R2_NOT_CLEANER_GENERATED` | `forbidden_shortcut` | The source may be tested with Q_clean, but it must not be defined as Q_clean K Q_clean without an independent parent origin. |
| `PDCS-R3_COMMON_CLEAN_SUPPORT` | `>=0.20` | Support retention norm(Q_clean K Q_clean) / norm(K) must pass the frozen common-clean threshold before scoring. |
| `PDCS-R4_LOW_PROJECTION_LEAKAGE` | `<=0.10` | Projection leakage after common-clean restriction must remain below the frozen threshold. |
| `PDCS-R5_BRANCH_BALANCED_SUPPORT` | `<=0.50` | No single family, clock, or observing-context block may dominate pre-score energy. |
| `PDCS-R6_DIAGONAL_CONTROL` | `<=0.10` | The object must not reduce to diagonal variance inflation. |
| `PDCS-R7_NULL_SEPARATION_REQUIRED` | `required` | The object must remain separated from morphology-null, projection-null, shuffled-support, and generic smooth baselines before scoring authorization. |
| `PDCS-R8_TARGET_BLINDNESS` | `required` | No target residuals, OOS scores, fitted alpha behavior, or winning null information may enter source construction. |

## Forbidden Shortcut

A future candidate must not be created by taking an arbitrary matrix and
declaring its cleaned version to be the Tau object:

```text
K_tau := Q_clean K_arbitrary Q_clean
```

Cleaning may be used as an audit. It may not be the source of the
physics. The source must come from a declared parent-domain term first.

## Current Status

This artifact defines the next gate only. It constructs no object and
authorizes no empirical scoring.

Relevant precursor audits:

- [`p_taucov_compact_spectral_scorecard.md`](p_taucov_compact_spectral_scorecard.md)
- [`p_taucov_tccs_transfer_curvature_preflight.md`](p_taucov_tccs_transfer_curvature_preflight.md)
- [`p_taucov_common_clean_subspace_support_audit.md`](p_taucov_common_clean_subspace_support_audit.md)
- [`p_taucov_embedding_qclean_support_audit.md`](p_taucov_embedding_qclean_support_audit.md)

The embedding audit is now the sharpest blocker. In the current
parent-to-score embedding, the active branch coordinates have essentially no
support in the frozen common clean subspace. The next candidate must therefore
come with a revised parent-domain embedding or domain metric, not merely a new
matrix on the old embedding.

The rule constraining such a revised metric or embedding is:

[`p_taucov_domain_metric_update_rule.md`](p_taucov_domain_metric_update_rule.md)

This rule keeps the next step target-blind: the metric may be derived from
parent-domain provenance, source conventions, symmetry, constraint algebra, or
self-adjoint-domain structure, but not from residual outcomes or scorecard
success.

The first metric-candidate audit did not find a passing metric on the current
eight-coordinate embedding:

[`p_taucov_domain_metric_candidate_audit.md`](p_taucov_domain_metric_candidate_audit.md)

Therefore the next admissible route should focus on a richer parent-domain
embedding/source coordinate rather than another metric on the same coordinate
inventory.

The coordinate-extension gate and first target-blind preflight are now:

[`p_taucov_admissible_source_coordinate_extension.md`](p_taucov_admissible_source_coordinate_extension.md)

That packet defines admissible parent-derived coordinate classes and audits a
small set of nonlinear candidates before any scoring. Its first passing
preflight coordinate is the projection-branch interaction `COORD_PB_INTERACTION`,
derived from the parent `P*B` coupling. This is only a coordinate-source
preflight result; it does not freeze a covariance object and does not authorize
empirical scoring.

## Claim Boundary

Allowed statement:

> The next P-TauCov object class must be parent-domain sourced and pass common-clean support before scoring.

Forbidden statement:

> This requirement defines a Tau signal, constructs a covariance survivor, or validates Tau Core.
