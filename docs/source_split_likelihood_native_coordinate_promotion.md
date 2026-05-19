# Source-Split Likelihood-Native Coordinate Promotion

Status: coordinate promotion policy added; K1 export still blocked.

This policy resolves the coordinate-choice boundary for:

```text
LNPROMO_2_COORDINATE_PROMOTION
```

## Candidate Coordinate

The current preflight coordinate map is:

```text
CoordinateMapID: SOURCE_SPLIT_CMB_CHI_COORDINATE_PREFLIGHT_V1
CoordinateDefinition: flat_lcdm_comoving_distance_normalized_with_frozen_cmb_omega_m
Source: data/k1/source_split_likelihood_native_parameters.yaml
```

It uses the frozen CMB-only `OmegaM` value, not a K2-selected coordinate.

## Promotion Decision

The CMB-chi coordinate is accepted as the predeclared depth coordinate for the
next likelihood-native benchmark candidate, subject to two restrictions:

1. It must be used consistently for K1, locked K2, and all null comparators.
2. It does not erase the earlier coordinate-robustness warning; z-normalized
   and index/optical controls must remain reportable controls.

## Required Metadata For Export

Any promoted K1 export must include:

```text
CoordinatePolicyID
CoordinateMapID
x_likelihood_native
CoordinateDefinition
CoordinateSelectedAfterK2Scoring
CoordinateControlsReported
```

with:

```text
CoordinatePolicyID = SOURCE_SPLIT_CMB_CHI_COORDINATE_POLICY_V1
CoordinateSelectedAfterK2Scoring = false
CoordinateControlsReported = true
```

## Current Boundary

This policy promotes the coordinate convention for the next benchmark
candidate, but it does not by itself promote the K1 export. Covariance promotion
and null-comparator scoring are still required before any locked K2 result can
be interpreted.
