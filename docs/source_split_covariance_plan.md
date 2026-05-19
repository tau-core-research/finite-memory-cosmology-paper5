# Source-Split Joint Covariance Plan

Status: shrinkage covariance policy exported; no covariance is authorized for
K2 scoring.

The source-split branch now has standardized SN/BAO preflight rows and a
covariance-proxy sensitivity check. Those artifacts are useful for transform
development, but they are not a public joint covariance.

## Registry

The machine-readable registry is:

```text
evidence/source_split_covariance_registry.csv
```

The readiness output is:

```text
evidence/source_split_covariance_readiness.csv
```

Run:

```text
python3 scripts/check_source_split_covariance.py
```

## Current Candidates

- `SSCOV_DIAGONAL_STANDARDIZED_PROXY`: available for audit only.
- `SSCOV_WITHIN_ROW_CORRELATION_PROXY`: available for sensitivity checks only.
- `SSCOV_BLOCK_DIAGONAL_PUBLIC_SN_BAO`: planned interim covariance, not joint
  source-split covariance.
- `SSCOV_SHRINKAGE_SOURCE_SPLIT`: available as coordinate-native shrinkage
  covariance policy preflight.
- `SSCOV_PUBLIC_JOINT_SOURCE_SPLIT`: planned public joint covariance target.
- `SSCOV_LIKELIHOOD_NATIVE_PUBLIC`: planned likelihood-native covariance target.

## Decision

No covariance candidate is currently allowed for K2 scoring.

The immediate blockers are:

- no sign-family export from public reconstruction families.
- public full covariance remains preferred over the shrinkage policy.

The exported policy is:

```text
evidence/source_split_joint_covariance_policy.csv
evidence/source_split_joint_covariance_policy_summary.csv
```

It is positive definite on the eight usable source-split rows and uses a
declared shrinkage kernel in the coordinate-native target space. It remains a
preflight covariance policy, not a public full covariance.

The diagonal and correlation-proxy outputs can show whether a warning is
stable under simple assumptions. They cannot authorize measurement-gate scoring.
