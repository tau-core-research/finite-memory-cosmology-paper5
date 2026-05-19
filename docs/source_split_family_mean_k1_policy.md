# Source-Split Family-Mean K1 Policy

Status: policy gate added; no family-mean policy is authorized for the current
external K1 export.

The validated source-split reconstruction-family export contains two public
branch responses: an SN residual branch and a BAO residual branch. Their
equal-weight signed mean is nonzero on all eight usable source-split rows.
However, that is not enough to promote it to primary K1 for the current
scorecard.

## Run

```text
python3 scripts/build_source_split_family_mean_k1_policy.py
```

It writes:

```text
evidence/source_split_family_mean_k1_policy.csv
evidence/source_split_family_mean_k1_policy_readiness.csv
```

## Current Result

```text
FamilyCount: 2
UsableRows: 8
EqualWeightNonzeroRows: 8
MeanAbsEqualWeightResponse: 0.9367627784351423
AllowedPolicyCount: 0
CurrentExternalK1ExportAllowed: False
```

## Why It Is Still Blocked

The equal-weight signed mean is a plausible future K1 policy, but it was not
frozen before the current K2/null scorecard. Using it now as the primary K1
would turn a sensitivity observation into a post-hoc baseline choice.

The policy table also records stricter alternatives:

- inverse-variance family mean, blocked until family covariance weights are
  declared;
- robust median family response, blocked because at least three reconstruction
  families are required;
- sign-stable rows only, kept as a subset diagnostic rather than a primary K1.

## Interpretation

This is a useful narrowing step. It says that a nonzero family-mean K1 route is
possible for a future rerun, but the current paper cannot use it as measurement
validation. The cleanest next route remains a likelihood-native joint SN+BAO
baseline; the family-mean route is a secondary future preflight route if its
policy is frozen before scoring.
