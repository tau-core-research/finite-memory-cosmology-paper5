# P-TauCov Signed-Response Statistic

Status: `P_TAUCOV_SIGNED_RESPONSE_STATISTIC_FROZEN_NO_SCORING`.

The signed-response statistic is frozen as:

```math
S = \operatorname{tr}\left[(rr^{\mathsf T}/\sigma^2-I)K_{\rm signed}\right].
```

A positive value means the held-out residual outer product aligns with
the frozen signed branch-localized operator. This is not a covariance
likelihood score and not a survival claim.

No scoring is authorized by this statistic freeze.
