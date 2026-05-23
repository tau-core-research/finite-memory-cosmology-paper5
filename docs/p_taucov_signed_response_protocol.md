# P-TauCov Signed-Response Protocol

Status: `P_TAUCOV_SIGNED_RESPONSE_PROTOCOL_FROZEN_READY_FOR_MANIFEST_NO_SCORING`.

The branch-localized map is signed rather than PSD. Therefore it
must not be scored as a covariance-deformation survival candidate.
The allowed next path is a separate signed operator-contrast protocol.

The eventual statistic must be frozen before scoring, for example:

```math
S = \operatorname{tr}\left[(rr^{\mathsf T}/\sigma^2-I)K_{\rm signed}\right].
```

This is an alignment statistic, not a covariance likelihood claim.
It requires its own signed nulls and blocked aggregation.

No scoring is authorized by this protocol declaration.
