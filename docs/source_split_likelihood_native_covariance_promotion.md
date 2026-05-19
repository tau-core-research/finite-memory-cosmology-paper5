# Source-Split Likelihood-Native Covariance Promotion

Status: covariance promotion policy added; public full covariance is still
preferred for measurement validation.

This policy resolves the covariance-boundary task:

```text
LNPROMO_3_COVARIANCE_PROMOTION
```

## Current Covariance Object

The current covariance artifact is:

```text
evidence/source_split_joint_covariance_policy.csv
evidence/source_split_joint_covariance_policy_summary.csv
```

It is positive definite and K1-compatible, but it is explicitly marked as a
shrinkage preflight policy rather than a public full covariance.

## Promotion Decision

The shrinkage covariance may be used for a likelihood-native null-scorecard
preflight only if the report labels it as:

```text
declared_shrinkage_benchmark_covariance
```

It must not be described as:

```text
public_full_joint_covariance
```

and it must not support a measurement-validation claim.

## Required Metadata

Any likelihood-native K1/null scorecard using this covariance must include:

```text
CovariancePolicyID
CovarianceClass
PublicFullCovariance
ShrinkageBenchmark
UsedForK1
UsedForK2
UsedForNulls
MeasurementValidationAllowed
```

with:

```text
CovarianceClass = declared_shrinkage_benchmark_covariance
PublicFullCovariance = false
ShrinkageBenchmark = true
UsedForK1 = true
UsedForK2 = true
UsedForNulls = true
MeasurementValidationAllowed = false
```

## Current Boundary

This policy allows a future preflight null-scorecard to be internally
consistent, because K1, locked K2, and null comparators can be evaluated under
the same covariance rule. It does not turn the result into a public
covariance-aware measurement benchmark.
