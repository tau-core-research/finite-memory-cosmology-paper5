# Likelihood-Native Covariance Route Scorecard

Status: route-level preflight summary; no measurement validation claim.

This note compares the current likelihood-native source-split K2 result across
the covariance routes that have been tested so far. The purpose is not to select
a final covariance model, but to separate three cases that were previously easy
to conflate:

- native or weak diagonal proxies;
- declared branch-scatter preflight covariance;
- propagated public covariance proxies and cross-covariance sensitivity.

The scorecard is exported to:

- `evidence/source_split_likelihood_native_covariance_route_scorecard.csv`;
- `evidence/source_split_likelihood_native_covariance_route_summary.csv`.

## Current Route Summary

The current route summary reports:

- routes tested: 9;
- routes where K2 improves over K1/no-memory: 9;
- routes where K2 beats the best polynomial control: 6;
- branch-scatter competitive routes: 5;
- public-proxy competitive routes: 0.

The best currently supported route is therefore
`BRANCH_SCATTER_DECLARED_PREFLIGHT`. This is not a public full-covariance
validation route. It is a declared preflight benchmark that uses the observed
SN/BAO branch scatter as a response-scale covariance.

## Interpretation

The result is route-dependent:

- under branch-scatter covariance variants, `K2_LOCKED_RHO4` is the best AIC
  model across all tested cases;
- under the propagated public covariance proxy, K2 improves over K1/no-memory
  but does not beat polynomial controls;
- under row-aligned cross-covariance sensitivity, K2 keeps improving over
  K1/no-memory but still does not beat the polynomial controls.

This strengthens the K2 preflight case conditionally, while keeping the public
measurement claim blocked. The primary blocking issue is still that the public
covariance proxy is not yet competitive with polynomial controls and is not a
full likelihood covariance.

## Next Action

The next technical step is not a kernel change. It is either:

1. upgrade the public covariance transform toward a full likelihood-native
   covariance, including the appropriate SN-BAO cross-covariance structure; or
2. independently justify the branch-scatter response-scale route as an
   externally registered systematic/scatter benchmark.

Until one of those routes is completed, this remains a preflight benchmark
result rather than measurement validation of the finite-memory projection
hypothesis.
