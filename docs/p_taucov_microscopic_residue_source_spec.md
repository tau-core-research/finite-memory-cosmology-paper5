# P-TauCov Microscopic Residue Source Specification

Status: `P_TAUCOV_MICROSCOPIC_RESIDUE_SOURCE_SPEC_DEFINED_NO_OBJECT_NO_SCORING`

This is a no-score source specification. It exists because the previous
parent-Hessian residue candidate collapsed to numerical zero after
smooth-PSD, projection-null, and balance cleaning.

## Source Requirement

A future candidate must be selected upstream of the empirical bridge by a
microscopic parent source selector. It cannot be another empirical
covariance shape.

## Declared Routes

| Route | Selector | Primary |
|---|---|---|
| `MRS_ROUTE_A_COMPACT_SPECTRAL_RESIDUE` | compact-spectrum mode selection | `True` |
| `MRS_ROUTE_B_BOUNDARY_DOMAIN_RESIDUE` | boundary/domain condition | `False` |
| `MRS_ROUTE_C_INDEX_RESIDUE` | index or protected-kernel residue | `False` |
| `MRS_ROUTE_D_PARENT_ACTION_HESSIAN_RESIDUE` | microscopic parent-action Hessian | `False` |

The first route to try is:

`MRS_ROUTE_A_COMPACT_SPECTRAL_RESIDUE`

because it directly targets the current blocker: the need for a non-smooth
spectral residue that generic smooth PSD covariance cannot reproduce.

## Required Before Any Object

- declare the parent operator or action source;
- declare the compact domain or boundary condition;
- declare the spectral/index/boundary residue selector;
- declare the smooth complement to be excluded;
- declare projection-null and gauge exclusion before empirical bridge;
- freeze all thresholds before scoring;
- use no target residuals, OOS scores, alpha behavior, or winning nulls to
  choose the object.

## Forbidden Claim

> The source specification produces a Tau Core signal.

## Allowed Claim

> The source specification defines which microscopic parent-source routes
> are admissible after the parent-source gap failure.

## Next Allowed Artifact

`p_taucov_compact_spectral_residue_source_v1_no_score_preflight`
