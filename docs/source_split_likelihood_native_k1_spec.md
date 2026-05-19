# Source-Split Likelihood-Native K1 Specification

Status: specification draft frozen for the next implementation step; no
likelihood-native K1 export is authorized yet.

This document defines the intended likelihood-native joint SN+BAO K1 baseline
route. Its purpose is to prevent the K1/no-memory baseline from being chosen
after inspecting locked K2 performance.

## Scope

The target object is:

```text
data/k1/source_split_external_k1_response.csv
```

with:

```text
ProvenanceType = likelihood_native_baseline
K1SourceID = K1SRC_LIKELIHOOD_NATIVE_JOINT_BASELINE
```

The export must be produced before any new locked K2/null scorecard is run.

## Public Inputs

SN input:

```text
ProductID: PANTHEON_PLUS_SH0ES_SN
Data: data/public_ingest/pantheon_plus/Pantheon_SH0ES.dat
Covariance: data/public_ingest/pantheon_plus/Pantheon_SH0ES_STAT_SYS.cov
```

BAO input:

```text
ProductID: DESI_DR2_BAO_ALL_GAUSSIAN
Data: data/public_ingest/desi_dr2/desi_gaussian_bao_ALL_GCcomb_mean.txt
Covariance: data/public_ingest/desi_dr2/desi_gaussian_bao_ALL_GCcomb_cov.txt
```

These inputs are public-data products. Their presence does not by itself create
a finite-memory measurement benchmark.

## Joint Vector

The likelihood-native joint vector must be built as a common SN+BAO diagnostic
vector on the source-split target rows:

```text
target_grid = evidence/source_split_coordinate_native_target.csv
usable_rows = HasSNAndBAO == true
```

For each usable row, the implementation must define:

```text
y_obs(row)
y_baseline_no_memory(row)
K1Response(row) = y_baseline_no_memory(row)
K1Sigma(row)
x_likelihood_native(row)
```

The exact observable-to-diagnostic transform must be declared before scoring.
It may use the existing source-split standardized row layout as a preflight
guide, but the likelihood-native vector must not be retrofitted to improve K2.

## Baseline Model

The no-memory baseline must be one of:

```text
public_chain_or_bestfit_baseline
independent_public_model_response
reproducible_frozen_evaluator
```

The baseline parameter source must be exported to:

```text
data/k1/source_split_likelihood_native_parameters.yaml
```

Minimum fields:

```text
baseline_id
source_product_ids
parameter_source
frozen_before_k2_scoring
fitted_in_this_note: false
same_data_amplitude_fit: false
parameters
claim_boundary
```

Same-data nuisance treatment may be reported as a sensitivity control, but it
must not be the primary K1 amplitude source unless it was part of a public,
predeclared likelihood-native baseline.

## Coordinate

The likelihood-native coordinate map must be exported to:

```text
data/k1/source_split_likelihood_native_coordinate_map.csv
```

Required columns:

```text
GridIndex
z_grid
x_likelihood_native
CoordinateDefinition
Source
FrozenBeforeK2Scoring
```

The coordinate used by the locked operator must be frozen before K2 scoring.
If a comoving-distance coordinate is used as a fallback, it must be marked as
coordinate-native preflight rather than likelihood-native.

## Covariance

The primary covariance should be either:

```text
public_full_joint_covariance
declared_likelihood_native_shrinkage_covariance
```

The current shrinkage covariance:

```text
evidence/source_split_joint_covariance_policy.csv
```

may serve as a preflight placeholder only until the likelihood-native vector is
frozen. K1, K2, and all null comparators must be scored under the same
covariance.

## K1 Export Rule

The final K1 export must satisfy:

```text
K1Response is finite
K1Sigma > 0
K1Response is not identically zero
AllowedAsPrimaryK1Candidate = true
SameDataAmplitudeFit = false
FittedInThisNote = false
Predeclared = true
```

The validator is:

```text
python3 scripts/validate_source_split_external_k1_export.py
```

## Null Comparators

The same likelihood-native vector must be scored against:

```text
K1_NO_MEMORY
POLY_DEG2
POLY_DEG3
BACKREACTION_ONLY
DYER_ROEDER_OPTICAL
SIGN_RANDOMIZED_CONTROL
COORDINATE_REMAP_CONTROL
```

Null comparators must be reported even if K2 improves.

## Locked K2 Rule

The K2 operator remains:

```text
W(x) = 1 + rho*x^3
rho <= 4
p = 3
```

No kernel change and no `rho > 4` rescue is allowed.

## Outcome Interpretation

Supportive:

- K2 is competitive with null comparators under the same covariance;
- no sign-stable contradiction appears;
- no `rho > 4` or kernel change is required.

Weakening:

- K1/no-memory or simple nulls remain preferred;
- K2 only works under one coordinate choice;
- K2 requires post-hoc parameter selection.

Strong negative:

- sign-stable rows contradict locked K2;
- covariance-aware scoring rejects K2 while nulls remain viable;
- K2 requires `rho > 4`, kernel change, or a post-hoc K1 rescue.

## Current Status

This specification closes the first planning blocker only. The following
artifacts are still required:

```text
baseline prediction vector promotion
likelihood-native coordinate-map promotion
promoted joint covariance / nuisance policy
data/k1/source_split_external_k1_response.csv
likelihood-native null-comparator scorecard
```

This is a protocol document, not measurement validation.
