# Full Likelihood-Native Joint Transform Contract

Status: measurement route contracted, not open.

## Summary

- Requirements: 8
- Preflight satisfied: 8/8
- Measurement satisfied: 1/8
- Measurement validation allowed: False
- Locked A2 changes allowed: False

## Required Route

The measurement route must use the same likelihood-native SN transform, BAO transform, joint covariance, K1 baseline, and null policy for every scored model.
The locked A2 prediction is rerun unchanged after those objects are frozen.

## Requirements

### FLN_1_SN_RESIDUAL_DEFINITION

- Class: sn_likelihood_transform
- Required object: `r_SN(theta_SN,nuisance)`
- Preflight satisfied: True
- Measurement satisfied: False
- Blocking issue: SN nuisance centering and likelihood-native residual transform are not frozen
- Acceptance criterion: SN residual vector and L_SN are derived from the public likelihood definition, including nuisance/marginalization policy
- Next action: freeze SN residual definition and transform before rerunning locked A2

### FLN_2_BAO_RESIDUAL_DEFINITION

- Class: bao_likelihood_transform
- Required object: `r_BAO(theta_BAO)`
- Preflight satisfied: True
- Measurement satisfied: False
- Blocking issue: BAO observable prediction and anchor policy are not likelihood-native frozen
- Acceptance criterion: BAO residual vector and L_BAO are derived from the public BAO likelihood observable vector without nearest-anchor choices
- Next action: freeze BAO observable prediction vector and transform before rerunning locked A2

### FLN_3_SOURCE_SPLIT_VECTOR

- Class: joint_target
- Required object: `y_split = L_SN*r_SN - L_BAO*r_BAO`
- Preflight satisfied: True
- Measurement satisfied: False
- Blocking issue: source-split target is preflight/coordinate-native, not likelihood-native
- Acceptance criterion: y_split is regenerated from frozen SN and BAO likelihood-native transforms only
- Next action: rebuild y_split after FLN_1 and FLN_2 are satisfied

### FLN_4_JOINT_COVARIANCE

- Class: joint_covariance
- Required object: `C_split = L_SN C_SN L_SN^T + L_BAO C_BAO L_BAO^T - C_cross - C_cross^T`
- Preflight satisfied: True
- Measurement satisfied: False
- Blocking issue: public covariance routes remain polynomial-dominated; branch bridge is not measurement-grade
- Acceptance criterion: single declared covariance route scores A2, K1, polynomial, physical, sign, and coordinate controls without route switching
- Next action: build likelihood-native joint transform and final K1/null policy, then rerun locked A2 unchanged

### FLN_5_CROSS_COVARIANCE_POLICY

- Class: cross_covariance
- Required object: `C_cross policy`
- Preflight satisfied: True
- Measurement satisfied: False
- Blocking issue: preflight cross-covariance policy exists but is not a public full likelihood cross-covariance
- Acceptance criterion: cross-covariance policy is either public-likelihood derived or explicitly justified as zero with sensitivity retained
- Next action: promote cross-covariance policy only after likelihood-native route is frozen

### FLN_6_K1_BASELINE

- Class: baseline
- Required object: `K1_split`
- Preflight satisfied: True
- Measurement satisfied: False
- Blocking issue: K1 is available as preflight export, not final likelihood-native baseline under the final covariance route
- Acceptance criterion: K1 is exported under the final frozen transform/covariance policy with no same-data amplitude fit
- Next action: rerun K1 export after FLN_1 through FLN_5 are satisfied

### FLN_7_NULL_POLICY

- Class: null_comparators
- Required object: `final comparator set`
- Preflight satisfied: True
- Measurement satisfied: False
- Blocking issue: null policy is frozen for preflight, but must be rerun under the final likelihood-native route
- Acceptance criterion: K1, polynomial, physical, sign-randomized, and coordinate controls are scored under identical final covariance/transform policy
- Next action: reuse the frozen null registry after the final route is built; do not add post-hoc controls

### FLN_8_LOCKED_A2

- Class: locked_prediction
- Required object: `K2_A2 = 2*K1*(1+4*x^3)`
- Preflight satisfied: True
- Measurement satisfied: True
- Blocking issue: none
- Acceptance criterion: locked A2 remains unchanged: p=3, rho=4, A_tau=2, no K1 refit
- Next action: do not modify A2; rerun unchanged once the measurement route exists

## Claim Boundary

This contract does not claim measurement validation. It defines the route required before measurement scoring can be considered.
