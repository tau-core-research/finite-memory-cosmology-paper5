# MVP Benchmark Findings

Status: operational MVP, not measurement validation.

## What Survives

- The locked finite-memory projection hypothesis is runnable and auditable.
- Most tested coordinate mappings remain non-violating under the current gate.
- The flat-LCDM chi-normalized warning is recoverable within `rho <= 4` in the
  bounded scan.
- The null-model and covariance-proxy scripts now produce reproducible evidence
  tables rather than narrative-only claims.

## What Weakens The Claim

- `K1_NO_MEMORY` beats fixed `K2_LOCKED_RHO4` under the current distilled
  diagonal-proxy AIC/BIC benchmark.
- Simple validation checks preserve this weakening signal.
- The current packet is distilled and does not contain a public full covariance
  matrix or likelihood-native coordinate map.

## Why This Is Not Final Falsification

- Correlated covariance proxies shrink the `K1_NO_MEMORY` advantage.
- The chi-normalized warning is an operator-only remapping warning, not a
  coordinate-native reconstruction result.
- The benchmark still lacks public covariance-aware likelihood products.
- No post-hoc kernel change or `rho > 4` extension has been used.

## Required Next Benchmark

The next benchmark must ingest public BAO-only and SN+BAO diagnostic products,
attach a full or declared shrinkage covariance, define likelihood-native or
coordinate-native mappings, and rerun the locked prediction against the
registered null comparators.
