# Source-Split Likelihood-Native K1 Plan

Status: preflight baseline vector and coordinate map added; likelihood-native K1 is not ready.

The family-mean future dry run weakens the secondary route. The primary route
therefore becomes a likelihood-native joint SN+BAO K1/no-memory baseline.

## Run

```text
python3 scripts/build_source_split_likelihood_native_k1_plan.py
```

It writes:

```text
evidence/source_split_likelihood_native_k1_plan.csv
evidence/source_split_likelihood_native_k1_readiness.csv
```

## Current Readiness

```text
RequiredArtifacts: 9
AvailableOrPreflightArtifacts: 9
BlockingArtifacts: 5
LikelihoodNativeK1ExportAllowed: False
PreferredNextArtifact: LNK1_BASELINE_PREDICTION_VECTOR
CurrentDecision: likelihood_native_k1_not_ready
```

## What Is Already Available

- Pantheon+ SN public data and covariance.
- DESI DR2 BAO public mean vector and covariance.
- The joint likelihood-native K1 specification.
- A frozen CMB-only no-memory parameter source.
- A preflight baseline prediction vector.
- A preflight CMB-parameter comoving-distance coordinate map.
- A preflight source-split covariance policy.
- A future-only family-mean K1 candidate, explicitly not likelihood-native.
- A null-comparator registry.

## Blocking Artifacts

- baseline prediction vector promotion to likelihood-native K1 quality;
- coordinate-map promotion with the joint vector/covariance policy;
- promoted joint covariance policy;
- likelihood-native external K1 export;
- null-comparator scores on the same likelihood-native vector.

## Next Step

Promote:

```text
data/k1/source_split_likelihood_native_baseline_prediction.csv
```

The baseline prediction vector now exists, but remains preflight because SN
nuisance handling, coordinate promotion, and joint covariance promotion are not
yet complete. It must not be used as primary K1 until those blockers are closed.

## Interpretation

This plan does not add measurement validation. It turns the best remaining
route into a concrete artifact checklist.
