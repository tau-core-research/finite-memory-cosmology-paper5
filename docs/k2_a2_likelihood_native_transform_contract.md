# K2 A2 Likelihood-Native Source-Split Transform Contract

Status: contract draft / no scorecard authorization / no measurement-validation claim

## Purpose

The locked A2 prediction is ready:

```text
K2_SOURCE_SPLIT_A2_PRIOR_V1 = 2 * K1(x) * (1 + 4*x^3)
```

The next blocker is not data availability. Pantheon+ and DESI DR2 public data
and covariance files are present locally. The blocker is the exact
likelihood-native transform that maps those public products into the same
source-split vector used to test A2.

## Required Vector Form

The full gate must define a source-split vector:

```text
y_split = L_SN * r_SN - L_BAO * r_BAO
```

where:

```text
r_SN  = Pantheon+ SN residual vector under a frozen nuisance/baseline policy
r_BAO = DESI DR2 BAO residual vector under a frozen baseline policy
L_SN  = SN transform / binning / standardization matrix
L_BAO = BAO transform / anchor / standardization matrix
```

No K2 or A2 score may be used to choose these matrices.

## Required Covariance Form

The covariance of the source-split vector must be:

```text
C_split =
    L_SN  C_SN  L_SN^T
  + L_BAO C_BAO L_BAO^T
  - C_SN_BAO_cross
  - C_SN_BAO_cross^T
```

If public SN-BAO cross-covariance is unavailable, the policy must be frozen
before scoring. Allowed predeclared policies:

```text
1. zero cross-covariance with explicit limitation;
2. registered shrinkage cross-covariance;
3. row-aligned sensitivity grid reported as sensitivity only.
```

Forbidden:

```text
choosing cross-covariance after seeing A2 vs null scores
tuning cross-covariance to make A2 win
dropping polynomial/null comparators after inspection
```

## Required K1 Form

The K1/no-memory baseline must be exported in the same vector space:

```text
K1_split = L_K1 * r_no_memory
```

It must be frozen before A2 scoring and must not be fitted to the A2 residual.

## Required Nulls

The full benchmark must score at least:

```text
K1_NO_MEMORY
K2_UNIT_LOCKED_RHO4
K2_SOURCE_SPLIT_A2_PRIOR_V1
POLY_DEG2
POLY_DEG3
ZERO_RESPONSE_CONTROL
SIGN_RANDOMIZED_CONTROL
COORDINATE_REMAP_CONTROL
```

Physical nulls such as optical/Dyer-Roeder or backreaction may be included only
if their amplitude/covariance mapping is registered before scoring.

## Success / Weakening / Negative Outcomes

Supportive:

```text
A2 improves over K1 and unit K2 and remains competitive with frozen nulls under
the same covariance and validation policy.
```

Weakening:

```text
A2 improves over K1 and unit K2 but a frozen null dominates under full
covariance-native validation.
```

Strong negative:

```text
A2 requires rho>4, p change, K1 refit, pointwise A_tau, or post-hoc covariance
selection.
```

## Current State

Available:

```text
Pantheon+ table and covariance
DESI DR2 BAO mean vector and covariance
locked A2 prediction
public covariance proxy
```

Blocked:

```text
SN likelihood-native transform matrix
BAO likelihood-native transform matrix
SN-BAO cross-covariance policy
likelihood-native K1 baseline
frozen full-gate null comparator policy
```

