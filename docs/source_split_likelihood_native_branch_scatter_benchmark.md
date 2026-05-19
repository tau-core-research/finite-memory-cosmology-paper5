# Source-Split Likelihood-Native Branch-Scatter Benchmark

Status: branch-scatter preflight benchmark complete.

This benchmark tests whether the source-split branch scatter can explain the
response scale required by the likelihood-native K2 comparison. It is not a
public full-covariance likelihood. It is a preflight covariance route that asks
whether the SN/BAO branch split itself supplies a plausible response-scale
model.

```text
script: scripts/run_likelihood_native_branch_scatter_benchmark.py
scatter: evidence/source_split_likelihood_native_branch_scatter_covariance.csv
scorecard: evidence/source_split_likelihood_native_branch_scatter_scorecard.csv
summary: evidence/source_split_likelihood_native_branch_scatter_summary.csv
```

The promotion gate is:

```text
script: scripts/check_likelihood_native_branch_scatter_promotion.py
gate: evidence/source_split_likelihood_native_branch_scatter_promotion_gate.csv
summary: evidence/source_split_likelihood_native_branch_scatter_promotion_summary.csv
```

## Main Result

Under all tested branch-scatter covariance variants, `K2_LOCKED_RHO4` is the
best AIC model:

```text
branch_scatter_diagonal: K2 best
native_plus_branch_scatter_quadrature: K2 best
max_native_or_branch_scatter: K2 best
branch_scatter_nearest_neighbor_corr_0p25: K2 best
branch_scatter_constant_offdiag_corr_0p25: K2 best
```

K2 improves over K1/no-memory in every case and also beats the best polynomial
control in every tested branch-scatter case.

## Why This Strengthens K2

The earlier native diagonal proxy was extremely narrow at low depth, causing a
few amplitude residuals to dominate the score. The branch-scatter model uses
the observed split between the public SN and BAO branch responses as a
row-level scale. Under that scale, the locked K2 correction becomes competitive
without changing the kernel, using `rho>4`, or rescaling K1.

## Claim Boundary

This is conditional strengthening, not measurement validation.

The branch-scatter route is still a preflight covariance model. It must not be
called public full covariance, and it must not be treated as a final likelihood
benchmark. The next required step is to promote or replace it with an
independently declared covariance, systematic-floor, or reconstruction-family
scatter rule before making a stronger empirical claim.

## Promotion Gate

The promotion gate now permits branch scatter to be treated as a declared
preflight benchmark, but not as measurement validation:

```text
PreflightBenchmarkPromotionAllowed: True
MeasurementValidationPromotionAllowed: False
PromotionStatus: preflight_benchmark_allowed_measurement_validation_blocked
```

The two blocking checks are exactly the intended safeguards:

```text
NOT_PUBLIC_FULL_COVARIANCE: false
INDEPENDENT_SYSTEMATIC_OR_COVARIANCE_SOURCE: false
```

Thus the current state is stronger than a loose diagnostic clue, but still below
a public covariance-aware measurement gate.

The covariance-source registry then identifies the next blocker: raw public SN
and BAO covariance inputs exist, but no propagated likelihood-native
source-split covariance exists yet. Branch scatter remains the declared
preflight route until that transform or another independent source is available.

A first public covariance proxy now exists and gives a mixed comparison: K2
still improves over K1/no-memory, but does not beat polynomial controls. This
does not erase the branch-scatter result; it shows that the next discriminant is
the quality and status of the covariance model.

The first cross-covariance sensitivity check does not close that gap: public
covariance proxy scores remain mixed even when a row-aligned SN-BAO
cross-covariance term is varied.
