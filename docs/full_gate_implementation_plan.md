# Full Gate Implementation Plan

Status: executable plan for the full measurement gate. Measurement validation remains closed.

## Summary

- Preflight closed components: 7/8
- Measurement ready components: 1/8
- Measurement blocked components: 2
- Measurement partial components: 4
- Primary next component: FG_4_JOINT_COVARIANCE

## Components

### FG_1_LOCKED_A2

- Class: prediction
- Preflight: CLOSED
- Measurement: READY
- Current artifact: `data/predictions/k2_source_split_a2_prior_v1.csv`
- Remaining work: none; do not modify locked prediction
- Acceptance criterion: K2 file exists and kernel/gain/rho/p remain unchanged

### FG_2_SN_TRANSFORM

- Class: transform
- Preflight: CLOSED
- Measurement: PARTIAL
- Current artifact: `data/transforms/k2_a2_l_sn_transform_v1.csv`
- Remaining work: replace binned SN residual transform with likelihood-native SN nuisance/marginalization transform
- Acceptance criterion: SN transform is derived from the same public likelihood definition used for final covariance

### FG_3_BAO_TRANSFORM

- Class: transform
- Preflight: CLOSED
- Measurement: PARTIAL
- Current artifact: `data/transforms/k2_a2_l_bao_transform_v1.csv`
- Remaining work: replace nearest-anchor BAO transform with likelihood-native BAO observable transform
- Acceptance criterion: BAO transform maps the DESI vector/covariance into the same source-split target without post-hoc anchor choices

### FG_4_JOINT_COVARIANCE

- Class: covariance
- Preflight: CLOSED
- Measurement: BLOCKED
- Current artifact: `evidence/joint_covariance_route_summary.csv`
- Remaining work: public covariance routes remain polynomial-dominated; branch bridge is not measurement-grade; build likelihood-native joint transform and final K1/null policy, then rerun locked A2 unchanged
- Acceptance criterion: same covariance is used for K1, locked A2, polynomial controls, and physical/null controls

### FG_5_K1_BASELINE

- Class: baseline
- Preflight: CLOSED
- Measurement: PARTIAL
- Current artifact: `data/k1/source_split_external_k1_response.csv`
- Remaining work: sn_nuisance_not_likelihood_native;coordinate_map_preflight_not_promoted;joint_covariance_not_promoted
- Acceptance criterion: K1 is exported under final transform and covariance policy, with no same-data amplitude fit

### FG_6_NULL_POLICY

- Class: nulls
- Preflight: CLOSED
- Measurement: PARTIAL
- Current artifact: `evidence/null_model_registry.csv`
- Remaining work: freeze final null set and complexity penalties under the final covariance route
- Acceptance criterion: K1, polynomial, physical, sign-randomized, and coordinate-remap nulls score under identical covariance/transform policy

### FG_7_POLYNOMIAL_CONTROL

- Class: overfit_risk_control
- Preflight: WARNING
- Measurement: BLOCKED
- Current artifact: `evidence/k2_a2_polynomial_tension_diagnosis.csv`
- Remaining work: full_likelihood_native_public_benchmark_required
- Acceptance criterion: locked A2 remains competitive against polynomial controls under final public covariance and validation policy

### FG_8_BRANCH_SCATTER_BRIDGE

- Class: calibrated_preflight_bridge
- Preflight: CLOSED
- Measurement: WARNING
- Current artifact: `evidence/branch_scatter_independent_calibration_summary.csv`
- Remaining work: replace or validate bridge with full public covariance route
- Acceptance criterion: branch-scatter bridge is reported only as preflight unless independently promoted
