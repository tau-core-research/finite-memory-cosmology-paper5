# Source-Split Likelihood-Native Public Covariance Proxy

Status: first public covariance proxy complete.

This artifact propagates raw public Pantheon+ and DESI covariance inputs into
the current likelihood-native source-split vector. It is a proxy, not a full
likelihood covariance:

```text
script: scripts/build_likelihood_native_public_covariance_proxy.py
covariance: evidence/source_split_likelihood_native_public_covariance_proxy.csv
marginals: evidence/source_split_likelihood_native_public_covariance_proxy_marginals.csv
scorecard: evidence/source_split_likelihood_native_public_covariance_proxy_scorecard.csv
summary: evidence/source_split_likelihood_native_public_covariance_proxy_summary.csv
```

## Method Boundary

The proxy uses:

- Pantheon+ covariance binned into the current redshift grid;
- DESI DR2 BAO log-residual covariance anchored to the same grid;
- linear standardization into the source-split residual coordinate;
- zero SN-BAO cross-covariance.

Because of the last assumption and the simplified transform, this is not a full
public likelihood product.

## Result

Under this public covariance proxy:

```text
K2 improves over K1/no-memory: true
K2 beats best polynomial control: false
Best model: POLY_DEG2
```

This is a mixed result. It supports the direction that K2 improves over the
frozen no-memory baseline, but it does not reproduce the stronger branch-scatter
benchmark where K2 beats the polynomial controls.

## Interpretation

The current covariance picture is now split:

- branch-scatter covariance: K2 is the best tested model;
- public covariance proxy: K2 improves over K1, but polynomial controls remain
  stronger.

This is not a contradiction. It means the next decisive work is covariance
quality: the project must upgrade the public proxy toward a full propagated
likelihood covariance, or independently justify why branch scatter is the
appropriate response-scale benchmark.

## Cross-Covariance Sensitivity

A follow-up audit varies a row-aligned SN-BAO cross-covariance proxy. K2
continues to improve over K1/no-memory across the valid positive-definite
range, but it does not beat the best polynomial control. This keeps the public
covariance proxy in mixed/weakening status relative to the stronger
branch-scatter preflight benchmark.
