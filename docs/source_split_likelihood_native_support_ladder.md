# Likelihood-Native K2 Support Ladder

Status: compact evidence summary; no measurement validation claim.

This note summarizes the current likelihood-native source-split evidence across
the route scorecard, covariance-gap audit, polynomial cross-validation, public
covariance proxy, and branch-scatter promotion gate.

Outputs:

- `evidence/source_split_likelihood_native_support_ladder.csv`;
- `evidence/source_split_likelihood_native_support_ladder_summary.csv`.

## Ladder

The current support ladder is:

1. `L1_K2_VS_K1`: supportive preflight.
   K2 improves over frozen K1/no-memory across route, row-level, and
   cross-validation diagnostics.

2. `L2_K2_VS_POLYNOMIAL_CONTROLS`: mixed conditional support.
   K2 beats polynomial controls on branch-scatter routes and most validation
   comparisons, but not on the public-proxy in-sample route.

3. `L3_PUBLIC_COVARIANCE_ROUTE`: weakening public proxy.
   The public covariance proxy is useful and K2 improves over K1/no-memory, but
   polynomial controls remain too competitive for stronger interpretation.

4. `L4_BRANCH_SCATTER_ROUTE`: declared preflight support.
   Branch scatter is the strongest current K2-supportive route, but it is not
   public full covariance.

5. `L5_MEASUREMENT_VALIDATION`: blocked.
   The finite-memory projection hypothesis is not measurement-validated by the
   current evidence.

## Current Interpretation

The current evidence no longer says simply that K2 is weak. It says:

- K2 is consistently better than K1/no-memory in the current preflight stack;
- K2 has conditional support against polynomial controls;
- the strongest support comes from the declared branch-scatter route;
- the public covariance route remains the main weakening factor;
- measurement validation remains blocked.

The next action is therefore to upgrade the public covariance transform or to
independently register the branch-scatter/systematic route. The locked K2 kernel
should not be changed to address this blocker.
