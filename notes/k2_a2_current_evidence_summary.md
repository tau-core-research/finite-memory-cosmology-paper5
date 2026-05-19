# K2 A2 Current Evidence Summary

Status: locked diagnostic prediction candidate / no measurement-validation claim

## Locked prediction

```text
K2_SOURCE_SPLIT_A2_PRIOR_V1 = 2 * K1(x) * (1 + 4*x^3)
```

The prediction is locked:

```text
p = 3
rho = 4
A_tau = 2
K1 refit = forbidden
pointwise gain = forbidden
measurement-validation claim = forbidden
```

The `A_tau=2` factor is interpreted as an anti-aligned SN/BAO source-split
projection prior, not as a fitted amplitude.

## What is strong

The A2 prediction improves over K1 and unit K2 in the current preflight chain.
It survives:

```text
lock readiness
pointwise benchmark
leave-one-out stability
depth transition
anti-alignment conditioning
reconstruction-family branch benchmark
rebinning stress
public covariance proxy against K1 and unit K2
blocked/covariance CV against polynomial controls
```

The most important structural result:

```text
low-depth  amplitude recovery ~= 0.12
mid-depth  amplitude recovery ~= 0.56
high-depth amplitude recovery ~= 0.95
```

This is compatible with the finite-memory expectation that the response is weak
at low depth and becomes active at mid/high depth.

## What is still weak

The current public covariance proxy is not a full likelihood-native benchmark.
It assumes a simplified public SN/BAO covariance propagation and no full
SN-BAO cross-covariance.

Under public-proxy leave-one-out, a flexible polynomial control still scores
better than A2:

```text
public_proxy_diag LOO:
A2 chi2       ~= 12.48
POLY_DEG2 chi2 ~= 7.21
```

However, the polynomial advantage is not stable under blocked/out-of-sample
stress:

```text
public_proxy_diag blocked:
A2 chi2       ~= 12.58
POLY_DEG2 chi2 ~= 27.15
```

So the polynomial is a relevant local-interpolation warning, not yet a stable
physical null.

## Current interpretation

The correct claim boundary is:

```text
The locked A2 source-split projection prediction is a strong preflight
candidate. It is not a measurement validation and not a discovery claim.
```

The result is strongest in:

```text
memory-active mid/high depth
anti-aligned SN/BAO branch rows
blocked / rebinning / branch-scatter robustness checks
```

The result remains limited by:

```text
small grid
proxy covariance
no full likelihood-native source-split transform
incomplete public SN-BAO cross-covariance handling
```

## Next measurement gate

The next serious gate is:

```text
full covariance-native / likelihood-native public source-split benchmark
```

Required:

```text
1. public SN vector and covariance transform;
2. public BAO vector and covariance transform;
3. declared SN-BAO cross-covariance rule;
4. likelihood-native source-split grid;
5. locked A2 prediction applied without change;
6. null comparators frozen before scoring.
```

Success would mean:

```text
A2 improves over K1 and unit K2, remains competitive against frozen nulls, and
does not require changing p, rho, K1, or A_tau.
```

Failure would mean:

```text
the full covariance-native benchmark rejects A2 or requires post-hoc changes.
```

