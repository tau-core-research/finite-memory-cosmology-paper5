# Source-Split Likelihood-Native Baseline Prediction

Status: preflight baseline prediction vector available; not primary K1.

The frozen CMB-only parameter source has been evaluated on the usable
source-split rows and written to:

```text
data/k1/source_split_likelihood_native_baseline_prediction.csv
evidence/source_split_likelihood_native_baseline_prediction_summary.csv
```

Current summary:

```text
Rows: 7
BaselineID: SOURCE_SPLIT_LIKELIHOOD_NATIVE_CMB_ONLY_BASELINE_V1
MeanAbsRawSourceSplitResponse: 0.1722387688855695
MeanAbsCenteredControlSourceSplitResponse: 0.07615159034107458
MeanJointSigmaDiagProxy: 0.08033396511428767
AllowedAsPrimaryK1Candidate: False
```

The vector contains both a raw source-split response and a same-sample-centered
control response. The centered response is useful as a nuisance-control
diagnostic, but it is not a primary K1 export because the SN nuisance treatment
has not yet been promoted to a likelihood-native policy.

The current blockers are:

- `sn_nuisance_not_likelihood_native`
- `coordinate_map_preflight_not_promoted`
- `joint_covariance_not_promoted`

This artifact is therefore an implementation step toward K1, not a K2 scoring
authorization.
