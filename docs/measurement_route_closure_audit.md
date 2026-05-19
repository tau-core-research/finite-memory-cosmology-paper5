# Measurement Route Closure Audit

Status: preflight route closed; measurement route still blocked.

## Summary

- Preflight blocked checks: 0
- Measurement blocked checks: 2
- Measurement warnings: 6
- Measurement validation allowed: False
- Strongest allowed claim: locked A2 has a closed preflight route with calibrated branch-scatter support

## Findings

### MRC_1_LOCKED_A2_AVAILABLE

- Preflight status: PASS
- Measurement status: PASS
- Evidence: data/predictions/k2_source_split_a2_prior_v1.csv
- Interpretation: locked A2 prediction is available and unchanged

### MRC_2_TRANSFORM_MATRICES

- Preflight status: PASS
- Measurement status: WARNING
- Evidence: L_SN exported=True; L_BAO exported=True; status=EXPORTED_PREFLIGHT_TRANSFORMS_NOT_FULL_LIKELIHOOD_NATIVE
- Interpretation: transform matrices are frozen for preflight but not promoted to full likelihood-native measurement route

### MRC_3_PUBLIC_COVARIANCE_INPUTS

- Preflight status: PASS
- Measurement status: WARNING
- Evidence: raw SN=True; raw BAO=True; zero-cross usable=True
- Interpretation: public covariance inputs are propagatable, but the public route is still a proxy

### MRC_4_K1_BASELINE

- Preflight status: PASS
- Measurement status: WARNING
- Evidence: data/k1/source_split_external_k1_response.csv
- Interpretation: K1 is available for preflight scoring, but measurement-grade K1 still depends on the same full transform/covariance policy

### MRC_5_NULL_POLICY

- Preflight status: PASS
- Measurement status: WARNING
- Evidence: evidence/null_model_registry.csv
- Interpretation: MVP null registry exists, but full-gate null policy must be frozen under the final covariance route

### MRC_6_K2_VS_K1

- Preflight status: PASS
- Measurement status: WARNING
- Evidence: K2-vs-K1=SUPPORTIVE_PREFLIGHT
- Interpretation: A2 is consistently stronger than K1/no-memory at preflight level

### MRC_7_POLYNOMIAL_CONTROL

- Preflight status: WARNING
- Measurement status: BLOCKED
- Evidence: No. It is not a physical null, but it remains a mandatory overfit-risk blocker.; current=The preflight scorecard is allowed and A2 is stronger than K1/unit K2, but polynomial tension keeps the result at preflight-support level.
- Interpretation: polynomial control cannot be dismissed and blocks stronger measurement interpretation

### MRC_8_BRANCH_SCATTER_CALIBRATION

- Preflight status: PASS
- Measurement status: WARNING
- Evidence: subset passes=7/7; route=INDEPENDENTLY_CALIBRATED_PREFLIGHT_SUPPORT
- Interpretation: branch-scatter bridge is independently calibrated for preflight, but it is not a full measurement route

### MRC_9_FULL_LIKELIHOOD_NATIVE_ROUTE

- Preflight status: WARNING
- Measurement status: BLOCKED
- Evidence: PUBLIC_COVARIANCE_INPUTS_AVAILABLE_FULL_TRANSFORM_BLOCKED
- Interpretation: full likelihood-native joint SN+BAO transform is still missing
