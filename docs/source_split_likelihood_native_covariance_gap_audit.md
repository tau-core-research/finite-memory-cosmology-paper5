# Likelihood-Native Covariance Gap Audit

Status: route-gap diagnostic only; no measurement validation claim.

The covariance route scorecard shows a split: branch-scatter covariance routes
make `K2_LOCKED_RHO4` competitive with polynomial controls, while the propagated
public covariance proxy remains mixed. This audit diagnoses that split at row
level without changing the locked K2 kernel, allowing `rho > 4`, or refitting
K1.

Outputs:

- `evidence/source_split_likelihood_native_covariance_gap_audit.csv`;
- `evidence/source_split_likelihood_native_covariance_gap_summary.csv`.

## What The Audit Measures

For each usable source-split row and each comparator, the audit records:

- target response;
- model prediction;
- residual;
- public-proxy sigma;
- branch-scatter sigma;
- public-to-branch sigma ratio;
- diagonal contribution under both sigma routes.

This row-level decomposition is not a replacement for the full covariance
scorecard. It is a diagnostic explaining where the route dependence comes from.

## Current Result

The current summary reports:

- rows: 8;
- median public-proxy sigma: 1.4950;
- median branch-scatter sigma: 1.2904;
- median public-to-branch sigma ratio: 1.1527;
- rows where the public sigma is tighter than branch scatter: 3;
- rows where K2 has lower public diagonal contribution than K1: 8;
- rows where K2 has lower branch-scatter diagonal contribution than K1: 8;
- rows where K2 has lower public contribution than the best polynomial control:
  1;
- rows where K2 has lower branch-scatter contribution than the best polynomial
  control: 1.

## Interpretation

The audit sharpens the current state:

- K2 consistently improves over K1/no-memory at row level;
- the remaining weakness is not K1 dominance, but polynomial-control dominance;
- the public-proxy route keeps polynomial controls competitive;
- the branch-scatter route can penalize flexible controls strongly on specific
  rows, which is why the route-level AIC result becomes K2-supportive there.

This is useful but still preflight-only. The decisive next step remains a better
covariance route: either a full likelihood-native public covariance transform or
an independently registered systematic/scatter route.
