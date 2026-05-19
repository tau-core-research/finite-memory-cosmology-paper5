# A2 Public-Covariance Replacement Plan

Status: implementation plan for replacing the calibrated preflight bridge. Measurement validation remains closed.

## Summary

- Ready components: 3/11
- Partial components: 3
- Rerun-ready components: 4
- Rerun-complete components: 1
- Blocked components: 0
- Measurement-blocking components: 8
- Raw public SN covariance available: True
- Raw public BAO covariance available: True
- Locked A2 rerun rule: no kernel change, no rho>4, no K1 refit, no target-sign gate.
- Locked rerun candidate status: LOCKED_A2_RERUN_CANDIDATE_MIXED_OR_WEAKENING

## Components

### PCOV_01_LOCKED_A2_INPUT

- Class: locked_prediction
- Status: READY
- Artifact: `data/predictions/k2_source_split_a2_prior_v1.csv`
- Evidence signal: p=3 rho=4 A_tau=2 locked; keep unchanged
- Blocks measurement: False
- Required action: none; rerun unchanged under final public covariance
- Acceptance criterion: same locked K2 vector is scored with no rho>4, no kernel change, no K1 refit

### PCOV_02_PUBLIC_SN_COVARIANCE

- Class: public_covariance_input
- Status: READY
- Artifact: `data/public_ingest/pantheon_plus/Pantheon_SH0ES_STAT_SYS.cov`
- Evidence signal: raw SN covariance available=True
- Blocks measurement: False
- Required action: validate indexing against the final SN residual vector
- Acceptance criterion: SN data vector and covariance rows/columns use the same public likelihood ordering

### PCOV_03_PUBLIC_BAO_COVARIANCE

- Class: public_covariance_input
- Status: READY
- Artifact: `data/public_ingest/desi_dr2/desi_gaussian_bao_ALL_GCcomb_cov.txt`
- Evidence signal: raw BAO covariance available=True
- Blocks measurement: False
- Required action: validate indexing against the final BAO residual vector
- Acceptance criterion: BAO data vector and covariance rows/columns use the same public likelihood ordering

### PCOV_04_SN_RESIDUAL_POLICY

- Class: likelihood_native_residual
- Status: RERUN_READY
- Artifact: `evidence/likelihood_native_residual_definition_readiness.csv`
- Evidence signal: rerun-resolved residual contracts=6/6
- Blocks measurement: True
- Required action: freeze SN nuisance, marginalization, and residual definition used by the covariance transform
- Acceptance criterion: SN residual vector is likelihood-native rather than binned diagnostic proxy

### PCOV_05_BAO_RESIDUAL_POLICY

- Class: likelihood_native_residual
- Status: RERUN_READY
- Artifact: `evidence/likelihood_native_residual_definition_readiness.csv`
- Evidence signal: rerun-resolved residual contracts=6/6
- Blocks measurement: True
- Required action: freeze BAO observable, baseline/r_d policy, and residual definition used by the covariance transform
- Acceptance criterion: BAO residual vector is likelihood-native rather than nearest-anchor diagnostic proxy

### PCOV_06_SOURCE_SPLIT_VECTOR

- Class: joint_target_vector
- Status: RERUN_READY
- Artifact: `evidence/likelihood_native_rerun_candidate_vector.csv`
- Evidence signal: candidate y_split ready=True; preflight usable objects=4/4; measurement usable=0/4
- Blocks measurement: True
- Required action: export final y_split vector from the same SN and BAO residual policies
- Acceptance criterion: one coordinate-native source-split vector is shared by K1, locked A2, and all null comparators

### PCOV_07_JOINT_COVARIANCE

- Class: joint_covariance
- Status: RERUN_READY
- Artifact: `evidence/likelihood_native_rerun_candidate_covariance.csv`
- Evidence signal: candidate C_split ready=True; positive definite=True; measurement blocker=public covariance routes remain polynomial-dominated; branch bridge is not measurement-grade
- Blocks measurement: True
- Required action: construct C_split from the final SN/BAO transforms and an explicit SN-BAO cross-covariance policy
- Acceptance criterion: same positive-definite C_split is used for K1, locked A2, polynomial, physical, and randomized controls

### PCOV_08_CROSS_COVARIANCE_POLICY

- Class: cross_covariance_policy
- Status: PARTIAL
- Artifact: `evidence/a2_cross_covariance_policy_summary.csv`
- Evidence signal: preflight rule=rho_cross_fixed_at_0_for_primary_preflight; PD rho range=-0.9..0.4
- Blocks measurement: True
- Required action: promote or replace the zero-cross preflight rule with a public/source-native policy before measurement scoring
- Acceptance criterion: cross-covariance policy is declared before scoring and is not selected by K2 performance

### PCOV_09_COORDINATE_NATIVE_K1

- Class: baseline
- Status: PARTIAL
- Artifact: `data/k1/source_split_external_k1_response.csv`
- Evidence signal: sn_nuisance_not_likelihood_native;coordinate_map_preflight_not_promoted;joint_covariance_not_promoted
- Blocks measurement: True
- Required action: export K1 under the same coordinate map, residual vector, and C_split used by locked A2
- Acceptance criterion: K1 is not fitted in this note and is not exported from a different covariance scale

### PCOV_10_NULL_AND_POLY_CONTROLS

- Class: null_policy
- Status: PARTIAL
- Artifact: `evidence/null_model_registry.csv`
- Evidence signal: The preflight scorecard is allowed and A2 is stronger than K1/unit K2, but polynomial tension keeps the result at preflight-support level.
- Blocks measurement: True
- Required action: freeze final fair nulls, polynomial complexity penalties, and physical-null controls under C_split
- Acceptance criterion: locked A2 is compared against the registered null set with identical data vector and covariance

### PCOV_11_LOCKED_RERUN_SCORECARD

- Class: final_rerun
- Status: RERUN_COMPLETE
- Artifact: `evidence/likelihood_native_rerun_candidate_scorecard.csv`
- Evidence signal: status=LOCKED_A2_RERUN_CANDIDATE_MIXED_OR_WEAKENING; DeltaAIC K2-K1=2.57966055836601; DeltaAIC K2-poly=3.205863767204125; K2>K1=False; K2>poly=False
- Blocks measurement: True
- Required action: rerun K1, locked A2, polynomial, physical-null, sign-randomized, and coordinate controls without changing locked A2
- Acceptance criterion: supportive, weakening, or strong-negative outcome is reported from the same final route

## Interpretation

This plan does not strengthen the empirical claim by itself. It turns the remaining public-covariance gap into an executable checklist for the next locked rerun.
