# Finite-Memory Cosmology Paper Status

## Current Status

Release-candidate method note. Not ready for a measurement-validation paper.

## Allowed Core Claim

```text
A predeclared finite-memory projection operator with W(x)=1+rho*x^3 and rho<=4
defines a bounded K2 diagnostic window. This window is compatible with the
BAO-only reconstructed diagnostic envelope and remains non-violating under a
reconstruction-aware SN+BAO sign-stability gate.
```

## Claims To Avoid

```text
Any background theory is established.
The K2 operator is the final cosmological law.
The result rules out cosmic backreaction.
The current tests are a full covariance likelihood.
The current branch is a direct measurement claim.
The paper reconstructs a full background theory.
```

## Current Strengths

- The K2 operator is predeclared and bounded before the final diagnostic tests.
- The memory-depth bound is predeclared and not chosen by residual fitting.
- The cubic kernel is selected by low-depth invisibility and endpoint-smoothness
  rules.
- BAO-only diagnostics are compatible with the full reconstructed envelope.
- SN+BAO strict-sign tension is localized and resolved by a sign-stability
  diagnostic policy as a non-violating warning without widening the K2 window.
- Claim boundaries are explicit.

## Measurement Gate Status

The finite-memory measurement gate has been added as a Phase II planning layer,
not as a stronger claim in the current manuscript. The current result remains
diagnostic compatibility. The gate specifies how a locked prediction should be
compared against null comparators under a covariance-aware benchmark before any
measurement-validation language is considered.

Current gate state:

```text
measurement_gate_plan: documented
null_comparators: registered
current_gate_engine: runnable_mvp
coordinate_robustness_engine: runnable_mvp
covariance_aware_benchmark: required_next_stage
current_paper_claim: diagnostic_method_note
```

Current MVP output:

```text
script: scripts/run_gate_current_packet.py
output: evidence/gate_results_current.csv
covariance_status: diagonal_proxy_from_p16_p84
interpretation: reproducibility harness, not measurement validation
```

Coordinate robustness MVP:

```text
script: scripts/run_coordinate_robustness.py
output: evidence/coordinate_robustness_results.csv
method: frozen_k1_no_refit_coordinate_audit
result: chi_normalized_flat_lcdm_audit gives envelope-tension warning under operator-only remapping
next: row_level_tension_audit + bounded_rho_scan + mapping_geometry
```

Coordinate tension diagnosis:

```text
row_level_output: evidence/coordinate_tension_audit.csv
rho_scan_output: evidence/rho_coordinate_scan.csv
geometry_output: evidence/coordinate_mapping_geometry.csv
chi_warning_type: upper-envelope excess at mid-depth points, plus one diagonal residual warning
bounded_recovery: chi mapping has non-violating points inside rho in [3.0, 3.6]
interpretation: coordinate robustness warning, not final falsification
```

Null-model benchmark MVP:

```text
script: scripts/run_null_comparison.py
scorecard: evidence/model_scorecard.csv
fixed_k2_rho4: non-violating on 4/5 mappings
bounded_k2_grid_3_4: non-violating on 5/5 mappings, but with parameter penalty
k1_no_memory_proxy: stronger diagonal-proxy AIC/BIC in this distilled packet
interpretation: benchmark weakening signal; covariance-aware public test required
```

Null dominance diagnosis:

```text
scripts:
  - scripts/diagnose_null_dominance.py
  - scripts/run_subset_model_scorecard.py
  - scripts/run_packet_cross_validation.py
  - scripts/run_shrinkage_covariance_sensitivity.py
outputs:
  - evidence/null_dominance_audit.csv
  - evidence/null_dominance_summary.csv
  - evidence/subset_model_scorecard.csv
  - evidence/cross_validation_results.csv
  - evidence/shrinkage_covariance_sensitivity.csv
finding: K1_NO_MEMORY remains stronger than K2_LOCKED_RHO4 under current diagonal and validation proxies
covariance_sensitivity: K1 advantage shrinks under correlated covariance proxies
interpretation: weakening result for distinct finite-memory contribution in the current distilled packet; not final falsification
```

Likelihood-native error-floor sweep:

```text
script: scripts/run_likelihood_native_error_floor_sweep.py
detail: evidence/source_split_likelihood_native_error_floor_sweep.csv
summary: evidence/source_split_likelihood_native_error_floor_sweep_summary.csv
first_floor_where_k2_best: 0.14
first_floor_where_k2_beats_best_polynomial: 0.14
interpretation: diagnostic response-scale threshold, not a selected covariance model
next: justify any error floor independently before stronger K2 interpretation
```

Likelihood-native error-floor policy:

```text
script: scripts/build_likelihood_native_error_floor_policy.py
policy: evidence/source_split_likelihood_native_error_floor_policy.csv
summary: evidence/source_split_likelihood_native_error_floor_policy_summary.csv
required_floor_for_k2_aic_competitiveness: 0.14
cross_branch_scatter_median_fraction: above_required_floor_but_preflight_only
policy_status: error_floor_not_independently_justified
interpretation: conditional strengthening of K2, not measurement validation
```

Likelihood-native branch-scatter benchmark:

```text
script: scripts/run_likelihood_native_branch_scatter_benchmark.py
scatter: evidence/source_split_likelihood_native_branch_scatter_covariance.csv
scorecard: evidence/source_split_likelihood_native_branch_scatter_scorecard.csv
summary: evidence/source_split_likelihood_native_branch_scatter_summary.csv
result: K2_LOCKED_RHO4 is best AIC model under all tested branch-scatter covariance variants
interpretation: stronger conditional K2 signal under branch-scatter scale; still preflight, not measurement validation
```

Likelihood-native branch-scatter promotion:

```text
script: scripts/check_likelihood_native_branch_scatter_promotion.py
gate: evidence/source_split_likelihood_native_branch_scatter_promotion_gate.csv
summary: evidence/source_split_likelihood_native_branch_scatter_promotion_summary.csv
preflight_benchmark_promotion_allowed: true
measurement_validation_promotion_allowed: false
promotion_status: preflight_benchmark_allowed_measurement_validation_blocked
interpretation: K2 branch-scatter result can be treated as declared preflight benchmark, but not as public full-covariance validation
```

Likelihood-native covariance source registry:

```text
script: scripts/build_likelihood_native_covariance_source_registry.py
registry: evidence/source_split_likelihood_native_covariance_source_registry.csv
readiness: evidence/source_split_likelihood_native_covariance_source_readiness.csv
task_queue: evidence/source_split_likelihood_native_covariance_source_task_queue.csv
raw_public_covariances_available: true
public_covariance_proxy_available: true
preflight_benchmark_route_available: true
measurement_validation_route_available: false
primary_blocking_issue: full_likelihood_covariance_missing
interpretation: branch scatter is the declared preflight route; public covariance proxy exists, but stronger validation needs a full propagated likelihood covariance or an independent systematic/scatter source
```

Likelihood-native public covariance proxy:

```text
script: scripts/build_likelihood_native_public_covariance_proxy.py
covariance: evidence/source_split_likelihood_native_public_covariance_proxy.csv
scorecard: evidence/source_split_likelihood_native_public_covariance_proxy_scorecard.csv
summary: evidence/source_split_likelihood_native_public_covariance_proxy_summary.csv
result: K2 improves over K1/no-memory, but does not beat polynomial controls
interpretation: mixed preflight result; branch-scatter is stronger, public covariance proxy requires full-likelihood upgrade
```

Likelihood-native cross-covariance sensitivity:

```text
script: scripts/run_likelihood_native_cross_covariance_sensitivity.py
detail: evidence/source_split_likelihood_native_cross_covariance_sensitivity.csv
summary: evidence/source_split_likelihood_native_cross_covariance_summary.csv
result: K2 improves over K1/no-memory across valid rho_cross values, but never beats the best polynomial control
interpretation: public covariance proxy remains mixed/weakening relative to branch-scatter benchmark
```

Likelihood-native covariance route scorecard:

```text
script: scripts/build_likelihood_native_covariance_route_scorecard.py
scorecard: evidence/source_split_likelihood_native_covariance_route_scorecard.csv
summary: evidence/source_split_likelihood_native_covariance_route_summary.csv
routes: 9
routes_where_k2_improves_over_k1: 9
routes_where_k2_beats_best_polynomial: 6
branch_scatter_competitive_routes: 5
public_proxy_competitive_routes: 0
current_best_supported_route: BRANCH_SCATTER_DECLARED_PREFLIGHT
primary_blocking_issue: public_proxy_not_yet_competitive_with_polynomial_controls
interpretation: K2 support is route-dependent; branch-scatter is strong at preflight level, while the public covariance proxy remains mixed
```

Likelihood-native covariance gap audit:

```text
script: scripts/diagnose_likelihood_native_covariance_gap.py
audit: evidence/source_split_likelihood_native_covariance_gap_audit.csv
summary: evidence/source_split_likelihood_native_covariance_gap_summary.csv
rows: 8
rows_where_k2_public_contribution_below_k1: 8
rows_where_k2_branch_contribution_below_k1: 8
rows_where_k2_public_contribution_below_best_polynomial: 1
rows_where_k2_branch_contribution_below_best_polynomial: 1
interpretation: K2 consistently improves over K1 row-by-row; the remaining weakness is polynomial-control dominance, not no-memory dominance
```

Likelihood-native polynomial cross-validation:

```text
script: scripts/run_likelihood_native_polynomial_cv.py
detail: evidence/source_split_likelihood_native_polynomial_cv.csv
summary: evidence/source_split_likelihood_native_polynomial_cv_summary.csv
public_proxy_leave_one_out: K2 improves over K1, but POLY_DEG2 remains stronger
public_proxy_blocked_split: K2 improves over K1 and beats polynomial controls
branch_scatter_leave_one_out: K2 improves over K1 and beats polynomial controls
branch_scatter_blocked_split: K2 improves over K1 and beats polynomial controls
interpretation: polynomial-control dominance is not stable across validation modes; this weakens the in-sample polynomial objection but remains preflight-level
```

Likelihood-native support ladder:

```text
script: scripts/build_likelihood_native_support_ladder.py
ladder: evidence/source_split_likelihood_native_support_ladder.csv
summary: evidence/source_split_likelihood_native_support_ladder_summary.csv
k2_vs_k1_status: SUPPORTIVE_PREFLIGHT
k2_vs_polynomial_status: MIXED_CONDITIONAL_SUPPORT
public_covariance_status: WEAKENING_PUBLIC_PROXY
current_strongest_status: DECLARED_PREFLIGHT_SUPPORT
measurement_validation_status: BLOCKED
primary_next_action: upgrade public covariance transform or independently register branch-scatter/systematic route
```

Public covariance upgrade queue:

```text
script: scripts/build_public_covariance_upgrade_queue.py
queue: evidence/public_covariance_upgrade_queue.csv
readiness: evidence/public_covariance_upgrade_readiness.csv
k2_vs_k1_supportive: true
k2_vs_polynomial_resolved: false
public_covariance_strong_enough: false
measurement_validation_route_available: false
branch_scatter_preflight_allowed: true
blocking_task_count: 3
primary_next_action: freeze full public covariance or registered shrinkage route before stronger K2 interpretation
```

Public covariance locked rerun protocol:

```text
script: scripts/build_public_covariance_locked_rerun_protocol.py
protocol: evidence/public_covariance_locked_rerun_protocol.csv
readiness: evidence/public_covariance_locked_rerun_readiness.csv
preferred_protocol: PCOV_RERUN_FULL_LIKELIHOOD_NATIVE_V1
secondary_protocol: PCOV_RERUN_BRANCH_SCATTER_REGISTERED_V1
allowed_current_rerun_count: 0
measurement_validation_still_blocked: true
primary_blocking_issue: full_public_covariance_transform_or_registered_shrinkage_route_missing
interpretation: rerun protocol is locked, but no stronger public-covariance rerun is currently authorized
```

Public covariance policy registry:

```text
script: scripts/build_public_covariance_policy_registry.py
registry: evidence/public_covariance_policy_registry.csv
readiness: evidence/public_covariance_policy_readiness.csv
policies_registered: 5
currently_available_preflight_policies: 1
currently_available_measurement_policies: 0
primary_available_policy: PCOV_POLICY_ROW_ALIGNED_CROSS_COV_SENSITIVITY_V1
current_status: SENSITIVITY_POLICY_AVAILABLE_STRONGER_POLICY_BLOCKED
next_action: freeze registered shrinkage parameters or implement full likelihood-native public covariance
```

Registered shrinkage rerun template:

```text
script: scripts/build_registered_shrinkage_rerun_template.py
template: evidence/registered_shrinkage_rerun_template.csv
readiness: evidence/registered_shrinkage_rerun_readiness.csv
components: 8
locked_or_available_components: 6
template_only_components: 2
current_allowed_to_run: false
measurement_validation_allowed: false
primary_blocking_issue: shrinkage_parameters_and_cross_covariance_policy_not_registered
next_action: choose and freeze shrinkage lambda, correlation family, and cross-covariance handling before any registered-shrinkage rerun
```

Registered shrinkage parameter policy:

```text
script: scripts/build_registered_shrinkage_parameter_policy.py
policy: evidence/registered_shrinkage_parameter_policy.csv
readiness: evidence/registered_shrinkage_parameter_policy_readiness.csv
primary_policy_id: REG_SHRINK_PARAM_BASELINE_V1
lambda_shrink: 0.15
correlation_family: exp_minus_abs_delta_x_over_L
correlation_length: 0.25
rho_sn_bao: 0.0
parameter_policy_registered: true
cross_covariance_policy_registered: true
template_only_components_after_policy: 0
current_allowed_to_run: false
measurement_validation_allowed: false
```

Registered shrinkage activation gate:

```text
script: scripts/check_registered_shrinkage_activation_gate.py
gate: evidence/registered_shrinkage_activation_gate.csv
summary: evidence/registered_shrinkage_activation_summary.csv
checks: 8
passed_checks: 6
preflight_blocking_checks: 0
measurement_blocking_checks: 2
registered_shrinkage_preflight_activation_allowed: true
registered_shrinkage_measurement_validation_allowed: false
allowed_rerun_type: future_preflight_only
current_scorecard_should_run_now: false
primary_measurement_blocker: ACT_5_K2_VS_POLY_RESOLVED
```

Registered shrinkage future-preflight scorecard:

```text
script: scripts/run_registered_shrinkage_future_preflight.py
covariance: evidence/registered_shrinkage_future_preflight_covariance.csv
scorecard: evidence/registered_shrinkage_future_preflight_scorecard.csv
summary: evidence/registered_shrinkage_future_preflight_summary.csv
best_model: POLY_DEG2
k1_aic: 16.61788646383459
k2_aic: 13.922797314092838
best_poly_aic: 8.415746515836037
k2_improves_over_k1: true
k2_beats_best_poly: false
interpretation: registered shrinkage does not rescue K2 from the public-polynomial objection; useful weakening preflight
```

Polynomial control fairness audit:

```text
script: scripts/build_polynomial_control_fairness_audit.py
audit: evidence/polynomial_control_fairness_audit.csv
summary: evidence/polynomial_control_fairness_summary.csv
polynomial_control_role: mandatory_overfit_risk_control
polynomial_is_fair_physical_null: false
polynomial_can_be_dismissed: false
k2_beats_best_poly_cv: 5/6
registered_shrinkage_k2_beats_best_poly: false
current_status: POLYNOMIAL_CONTROL_REMAINS_MEASUREMENT_BLOCKER
interpretation: polynomial controls are not physical explanation but remain mandatory overfit-risk blockers
```

Physical null hierarchy:

```text
script: scripts/build_physical_null_hierarchy.py
hierarchy: evidence/physical_null_hierarchy.csv
readiness: evidence/physical_null_hierarchy_readiness.csv
registered_nulls: 7
required_for_next_benchmark: 7
required_implemented_or_partial: 4
required_implemented_or_template: 6
physical_nulls_required: 3
physical_nulls_scoring_ready: 1
physical_null_templates_available: 0
physical_null_preflight_scoring_policy_available: 2
measurement_claim_ready: false
primary_blocking_issue: physical_null_amplitudes_not_physically_calibrated
next_action: run physical null preflight scorecard only as sanity/sensitivity comparator, then seek physical amplitude calibration before stronger claims
```

Physical null proxy templates:

```text
script: scripts/build_physical_null_proxy_templates.py
templates: evidence/physical_null_proxy_templates.csv
readiness: evidence/physical_null_proxy_template_readiness.csv
backreaction_template_available: true
dyer_roeder_optical_template_available: true
template_artifact_amplitude_policy_declared: false
separate_amplitude_policy_declared: true
scoring_allowed_from_template_alone: false
preflight_scoring_allowed_with_policy: true
measurement_validation_allowed: false
```

Physical null amplitude policy:

```text
script: scripts/build_physical_null_amplitude_policy.py
policy: evidence/physical_null_amplitude_policy.csv
readiness: evidence/physical_null_amplitude_policy_readiness.csv
amplitude_policy_declared: true
scoring_preflight_allowed: true
measurement_validation_allowed: false
primary_blocking_issue: physical_null_amplitudes_not_physically_calibrated
primary_policy: PHYSNULL_AMP_UNIT_ONLY_V1
secondary_policy: PHYSNULL_AMP_BOUNDED_GRID_V1
forbidden_policy: PHYSNULL_AMP_FORBIDDEN_FREE_FIT_V1
interpretation: physical nulls may enter sanity/sensitivity preflight scorecards, but not measurement validation
```

Physical null preflight scorecard:

```text
script: scripts/run_physical_null_preflight_scorecard.py
scorecard: evidence/physical_null_preflight_scorecard.csv
summary: evidence/physical_null_preflight_summary.csv
rows: 8
physical_null_rows: 12
k1_aic: 13.429587993885114
k2_aic: 9.678203467277251
best_physical_null_aic: 13.67349220290881
delta_aic_k2_minus_k1: -3.751384526607863
delta_aic_k2_minus_best_physical_null: -3.995288735631558
amplitude_selected_for_interpretation: false
measurement_validation_allowed: false
interpretation: K2 is stronger than K1 and the reported physical-null sanity/sensitivity controls under the branch-scatter preflight scale, but physical-null amplitudes remain uncalibrated
```

Physical null row audit:

```text
script: scripts/diagnose_physical_null_preflight.py
audit: evidence/physical_null_preflight_row_audit.csv
summary: evidence/physical_null_preflight_row_summary.csv
rows_where_k2_beats_k1: 8
rows_where_k2_beats_best_physical_null: 4
rows_where_best_physical_null_beats_k2: 4
rows_where_k2_has_sign_violation: 0
net_delta_chi2_k2_minus_k1: -3.7513845266078616
net_delta_chi2_k2_minus_best_physical: -0.3601026940036727
interpretation: supportive but narrow preflight result; physical nulls remain competitive row-level controls
```

Physical null calibration requirements:

```text
script: scripts/build_physical_null_calibration_requirements.py
requirements: evidence/physical_null_calibration_requirements.csv
readiness: evidence/physical_null_calibration_readiness.csv
calibration_routes_registered: 3
allowed_calibration_routes: 2
allowed_routes_available: 0
forbidden_routes_registered: 1
backreaction_calibration_available: false
dyer_roeder_calibration_available: false
physical_null_measurement_ready: false
primary_blocking_issue: physical_null_calibration_inputs_missing
interpretation: physical null preflight is runnable, but measurement-level comparison needs independent backreaction and optical-propagation amplitude calibration
```

Physical null calibration source registry:

```text
script: scripts/build_physical_null_calibration_source_registry.py
registry: evidence/physical_null_calibration_source_registry.csv
readiness: evidence/physical_null_calibration_source_readiness.csv
task_queue: evidence/physical_null_calibration_task_queue.csv
candidate_sources_registered: 4
sources_available_in_repo: 0
preflight_calibration_sources_allowed: 0
measurement_calibration_sources_allowed: 0
forbidden_routes_registered: 1
primary_blocking_issue: candidate_sources_registered_but_not_ingested_or_mapped
interpretation: source classes are registered, but no physical-null calibration source is ingested or mapped yet
```

Physical null calibration mapping policy:

```text
script: scripts/build_physical_null_calibration_mapping_policy.py
policy: evidence/physical_null_calibration_mapping_policy.csv
readiness: evidence/physical_null_calibration_mapping_readiness.csv
mapping_policies_registered: 4
target_rows: 8
target_z_range: 0.51..2.33
target_x_range: 0.3416929010998006..1.0
mappings_implemented: 0
same_scorecard_tuning_allowed: false
physical_null_mapping_ready: false
primary_blocking_issue: source_data_not_ingested;mapping_not_executed
interpretation: mapping policy is frozen, but no physical-null calibration source is mapped yet
```

Physical null calibration covariance policy:

```text
script: scripts/build_physical_null_calibration_covariance_policy.py
policy: evidence/physical_null_calibration_covariance_policy.csv
readiness: evidence/physical_null_calibration_covariance_readiness.csv
policies_registered: 4
preflight_policies_registered: 3
measurement_policies_registered: 1
currently_available_preflight_policies: 0
currently_available_measurement_policies: 0
forbidden_policies_registered: 1
physical_null_covariance_ready: false
physical_null_measurement_ready: false
primary_blocking_issue: source_covariance_not_ingested_or_propagated
interpretation: covariance policy is registered, but no physical-null source covariance is available yet
```

Physical null readiness dashboard:

```text
script: scripts/build_physical_null_readiness_dashboard.py
dashboard: evidence/physical_null_readiness_dashboard.csv
summary: evidence/physical_null_readiness_summary.csv
gates: 7
ready_gates: 4
measurement_blocking_gates: 6
open_measurement_blockers: 3
k2_preflight_status: supportive_but_narrow
physical_null_measurement_ready: false
primary_blocking_issue: source_ingestion_mapping_and_covariance_missing
interpretation: physical-null branch has useful K2-supportive preflight evidence but remains blocked for measurement validation
```

Physical null public source candidates:

```text
script: scripts/build_physical_null_public_source_candidates.py
candidates: evidence/physical_null_public_source_candidates.csv
readiness: evidence/physical_null_public_source_candidate_readiness.csv
candidates_registered: 6
backreaction_candidates: 2
optical_candidates: 5
direct_amplitude_candidates: 2
method_reference_candidates: 3
candidates_ingested: 0
candidates_mapped: 0
candidates_with_covariance: 0
physical_null_source_candidate_ready: false
primary_blocking_issue: candidate_sources_not_ingested_digitized_or_mapped
interpretation: public candidates are registered for acquisition, but none is a usable calibration source yet
```

Physical null candidate triage:

```text
script: scripts/build_physical_null_candidate_triage.py
triage: evidence/physical_null_candidate_triage.csv
summary: evidence/physical_null_candidate_triage_summary.csv
candidates_triaged: 6
first_ingest_targets: 3
backreaction_first_targets: 1
optical_first_targets: 2
direct_numeric_constraint_candidates: 2
method_reference_candidates: 3
measurement_inputs_ready_now: 0
recommended_next_candidate: PNC_BACKREACTION_KOKSBANG_2604_11249
primary_blocking_issue: candidate_constraints_not_extracted_or_mapped
interpretation: candidate triage identifies first acquisition targets but does not create measurement inputs
```

Phase II public benchmark preflight:

```text
manifest: data/public_ingest_manifest.yaml
readiness_output: evidence/public_benchmark_readiness.csv
input_inventory: evidence/public_input_inventory.csv
raw_observable_preflight: evidence/public_diagnostic_transform_preflight.csv
raw_observable_summary: evidence/public_diagnostic_transform_summary.csv
transform_registry: evidence/diagnostic_transform_registry.csv
transform_readiness: evidence/diagnostic_transform_readiness.csv
bao_residual_preflight: evidence/bao_residual_transform_preflight.csv
bao_residual_summary: evidence/bao_residual_transform_summary.csv
bao_residual_null_benchmark: evidence/bao_residual_null_benchmark.csv
bao_residual_null_scorecard: evidence/bao_residual_null_scorecard.csv
bao_baseline_offset_diagnosis: evidence/bao_baseline_offset_diagnosis.csv
bao_baseline_export_registry: evidence/bao_baseline_export_registry.csv
bao_baseline_export_readiness: evidence/bao_baseline_export_readiness.csv
bao_rd_offset_sensitivity: evidence/bao_rd_offset_sensitivity_summary.csv
bao_likelihood_source_registry: evidence/bao_likelihood_baseline_source_registry.csv
bao_likelihood_source_readiness: evidence/bao_likelihood_baseline_source_readiness.csv
desi_bestfit_baseline_export: evidence/desi_bestfit_bao_baseline_export.csv
desi_bestfit_baseline_summary: evidence/desi_bestfit_bao_baseline_summary.csv
cmb_only_baseline_export: evidence/cmb_only_bao_baseline_export.csv
cmb_only_baseline_summary: evidence/cmb_only_bao_baseline_summary.csv
bao_baseline_scorecard: evidence/bao_baseline_scorecard.csv
bao_baseline_selection_policy: evidence/bao_baseline_selection_policy.csv
bao_k2_protocol_registry: evidence/bao_k2_protocol_registry.csv
bao_k2_protocol_readiness: evidence/bao_k2_protocol_readiness.csv
bao_k1_response_registry: evidence/bao_k1_response_registry.csv
bao_k1_response_readiness: evidence/bao_k1_response_readiness.csv
bao_k1_amplitude_policy: evidence/bao_k1_amplitude_policy.csv
bao_k1_locked_response_registry: evidence/bao_k1_locked_response_registry.csv
bao_k1_locked_response_readiness: evidence/bao_k1_locked_response_readiness.csv
bao_k1_candidate: evidence/bao_k1_cmb_only_unit_covnorm_candidate.csv
bao_k1_candidate_summary: evidence/bao_k1_cmb_only_unit_covnorm_summary.csv
bao_k1_candidate_null_scorecard: evidence/bao_k1_candidate_null_scorecard.csv
current_status: public BAO/SN inputs downloaded and shape-validated for preflight
available_inputs: DESI DR2 BAO, DESI DR1 BAO fallback, Pantheon+SH0ES SN
remaining_blockers: diagnostic transform, coordinate-native / likelihood-native mapping, covariance-aware benchmark definition
interpretation: public products are locally available, but no measurement validation has been performed
```

Source-split reconstruction-family source readiness:

```text
script: scripts/check_source_split_reconstruction_family_sources.py
registry: evidence/source_split_reconstruction_family_source_registry.csv
readiness_output: evidence/source_split_reconstruction_family_source_readiness.csv
current_status: no scoring-grade reconstruction-family source is available
available_source: RF_PUBLIC_SOURCE_SPLIT_RECONSTRUCTION_FAMILIES
available_control: public branch-sign preflight
missing_source: likelihood-native reconstruction families
missing_rule: none for the coordinate-native candidate export
interpretation: reconstruction-family source input is now available; K2 scoring remains blocked by transform, K1, covariance, and sign-family gates
```

Source-split reconstruction-family export schema:

```text
schema_script: scripts/build_source_split_reconstruction_family_export_schema.py
validator: scripts/validate_source_split_reconstruction_family_export.py
schema: evidence/source_split_reconstruction_family_export_schema.csv
template: evidence/source_split_reconstruction_family_export_template.csv
validation: evidence/source_split_reconstruction_family_export_validation.csv
candidate_path: data/reconstruction_families/source_split_reconstruction_family_responses.csv
current_status: candidate_export_available_and_valid
allowed_for_k2_scoring: true
interpretation: exact input schema is frozen and the candidate export validates; K2 scoring remains blocked by other gates
```

Source-split reconstruction-family candidate plan:

```text
script: scripts/build_source_split_reconstruction_family_candidate_plan.py
plan: evidence/source_split_reconstruction_family_candidate_plan.csv
summary: evidence/source_split_reconstruction_family_candidate_summary.csv
candidate_families: 5
primary_candidates: RFAM_SN_RESIDUAL_BRANCH, RFAM_BAO_RESIDUAL_BRANCH
allowed_for_k2_scoring_now: 0
primary_next_action: export SN and BAO residual branches into the reconstruction-family response schema
interpretation: candidate plan only; no K2 scorecard is opened
```

Source-split reconstruction-family response preview:

```text
script: scripts/build_source_split_reconstruction_family_response_preview.py
preview: evidence/source_split_reconstruction_family_response_preview.csv
summary: evidence/source_split_reconstruction_family_response_preview_summary.csv
rows: 16
families: 2
schema_valid: true
family_sign_stable_rows: 3
family_sign_unstable_rows: 5
allowed_for_k2_scoring: false
blocking_issue: preview_not_scoring_candidate; family_level_rule_not_locked; covariance_policy_not_promoted
interpretation: schema plumbing works on the SN/BAO branches, but the preview is not a measurement-gate input
```

Source-split family sign-rule preview:

```text
script: scripts/build_source_split_family_sign_rule_preview.py
rows: evidence/source_split_family_sign_rule_preview.csv
summary: evidence/source_split_family_sign_rule_preview_summary.csv
rule: stable if all nonzero public reconstruction-family signs agree
stable_rows: 3
warning_rows: 5
allowed_for_k2_scoring: false
blocking_issue: sign_rule_preview_only
interpretation: row-level warning policy is explicit; scoring promotion is handled by the promotion-readiness gate
```

Source-split sign-rule promotion readiness:

```text
script: scripts/check_source_split_sign_rule_promotion.py
output: evidence/source_split_sign_rule_promotion_readiness.csv
preview_rule_declared: true
candidate_export_exists: true
candidate_export_valid: true
warning_rows_retained: true
rule_promotion_authorized: true
blocking_issue: empty
interpretation: sign-rule promotion is authorized for the validated candidate export; warning rows remain explicit
```

Source-split K2 scoring authorization:

```text
script: scripts/check_source_split_k2_scoring_authorization.py
output: evidence/source_split_k2_scoring_authorization.csv
required_gates: SS_TRANSFORM, SS_K1_TARGET, SS_JOINT_COVARIANCE, SS_CANDIDATE_PATH_GUARD, SS_RECONSTRUCTION_FAMILY_EXPORT, SS_SIGN_RULE_PROMOTION
all_required_gates_allowed: false
dashboard_authorized: false
k2_scoring_authorized: false
authorization_decision: BLOCKED
primary_next_action: create a valid public reconstruction-family candidate export before promoting the sign rule or scoring K2
interpretation: final guard blocks K2 scoring while allowing preflight work to continue
```

Source-split candidate path guard:

```text
script: scripts/check_source_split_candidate_path_guard.py
output: evidence/source_split_candidate_path_guard.csv
candidate_exists: true
preview_exists: true
candidate_matches_preview: false
status: CANDIDATE_PRESENT_NEEDS_VALIDATION
blocking_issue: empty
allowed_for_k2_scoring: true
interpretation: real candidate path exists and is distinct from the non-scoring preview
```

Source-split blocker matrix:

```text
script: scripts/build_source_split_blocker_matrix.py
matrix: evidence/source_split_blocker_matrix.csv
summary: evidence/source_split_blocker_matrix_summary.csv
blockers: 12
k2_blocking_rows: 9
primary_blocking_issue: upstream_gates_blocked
primary_next_action: do not run K2/null scorecard unless authorization returns AUTHORIZED
k2_scoring_authorized: false
interpretation: compact operational view of all source-split K2 blockers
```

Source-split SN branch export handoff:

```text
script: scripts/build_source_split_sn_branch_export_handoff.py
rows: evidence/source_split_sn_branch_export_handoff.csv
summary: evidence/source_split_sn_branch_export_handoff_summary.csv
candidate_family_id: RFAM_SN_RESIDUAL_BRANCH
rows: 8
ready_rows: 8
missing_rows: 0
response_scale: source_split_standardized_units
candidate_path: data/reconstruction_families/source_split_reconstruction_family_responses.csv
allowed_for_k2_scoring_now: false
interpretation: SN branch rows are included in the real candidate export
```

Source-split BAO branch export handoff:

```text
script: scripts/build_source_split_bao_branch_export_handoff.py
rows: evidence/source_split_bao_branch_export_handoff.csv
summary: evidence/source_split_bao_branch_export_handoff_summary.csv
candidate_family_id: RFAM_BAO_RESIDUAL_BRANCH
rows: 8
ready_rows: 8
missing_rows: 0
response_scale: source_split_standardized_units
candidate_path: data/reconstruction_families/source_split_reconstruction_family_responses.csv
allowed_for_k2_scoring_now: false
interpretation: BAO branch rows are included in the real candidate export
```

Source-split candidate export handoff:

```text
script: scripts/build_source_split_candidate_export_handoff.py
manifest: evidence/source_split_candidate_export_handoff_manifest.csv
summary: evidence/source_split_candidate_export_handoff_summary.csv
steps: 6
blocked_steps: 1
candidate_path: data/reconstruction_families/source_split_reconstruction_family_responses.csv
primary_blocking_issue: upstream_gates_blocked
allowed_for_k2_scoring_now: false
next_action: resolve remaining transform, K1, covariance, and sign-family gates before K2 scoring
interpretation: candidate export exists and validates cleanly, but K2 scoring is still blocked by upstream gates
```

Source-split K2/null preflight scorecard:

```text
script: scripts/run_source_split_k2_null_scorecard.py
scorecard: evidence/source_split_k2_null_scorecard.csv
summary: evidence/source_split_k2_null_scorecard_summary.csv
authorized: true
rows: 8
k2_degenerate_with_k1_no_memory: true
k2_rho4_status: STRICT_GATE_WARNING
k2_rho4_sign_stable_violations: 3
best_aic_model: POLY_DEG2_CONTROL
interpretation: weakening preflight result; locked multiplicative K2 is runnable but indistinguishable from zero-contrast no-memory K1 on this target
```

Source-split K1 degeneracy audit:

```text
script: scripts/diagnose_source_split_k1_degeneracy.py
audit: evidence/source_split_k1_degeneracy_audit.csv
summary: evidence/source_split_k1_degeneracy_summary.csv
requirements: evidence/source_split_k1_response_requirements.csv
zero_k1_rows: 8
rows_where_k2_equals_k1: 8
rows_with_finite_memory_leverage: 0
conclusion: multiplicative_k2_degenerate_with_zero_k1
interpretation: next source-split work must define an externally derived nonzero K1 response target or move to likelihood-native K1
```

Source-split K1 candidate sensitivity:

```text
candidate_audit: evidence/source_split_k1_response_candidate_audit.csv
candidate_summary: evidence/source_split_k1_response_candidate_summary.csv
sensitivity: evidence/source_split_k1_candidate_sensitivity.csv
sensitivity_summary: evidence/source_split_k1_candidate_sensitivity_summary.csv
nonzero_candidate_count: 3
best_aic_model: K1_SN_BRANCH_RESPONSE_AS_K1
best_aic_candidate_allowed_as_primary_k1: false
interpretation: nonzero K1 candidates exist as sensitivity controls, but none is promoted to primary K1; nonzero alone does not rescue K2
```

Source-split K1 candidate promotion:

```text
script: scripts/check_source_split_k1_candidate_promotion.py
readiness: evidence/source_split_k1_candidate_promotion_readiness.csv
summary: evidence/source_split_k1_candidate_promotion_summary.csv
promoted_primary_k1_count: 0
best_aic_model: K1_SN_BRANCH_RESPONSE_AS_K1
best_aic_candidate_promotion_authorized: false
interpretation: no candidate is promoted; source-split K2 needs an externally derived nonzero K1 or likelihood-native K1 target before a distinct measurement-gate comparison
```

Source-split external K1 export contract:

```text
schema_script: scripts/build_source_split_external_k1_export_schema.py
validator: scripts/validate_source_split_external_k1_export.py
schema: evidence/source_split_external_k1_export_schema.csv
template: evidence/source_split_external_k1_export_template.csv
readiness: evidence/source_split_external_k1_export_readiness.csv
candidate_path: data/k1/source_split_external_k1_response.csv
current_status: external_k1_export_missing
allowed_for_primary_k1: false
interpretation: the repo now defines the required external nonzero K1 object, but no such K1 has been inserted
```

Source-split external K1 source registry:

```text
script: scripts/build_source_split_external_k1_source_registry.py
registry: evidence/source_split_external_k1_source_registry.csv
readiness: evidence/source_split_external_k1_source_readiness.csv
authorized_sources: 0
preferred_future_route: K1SRC_LIKELIHOOD_NATIVE_JOINT_BASELINE
blocked_controls: K1SRC_CURRENT_ZERO_CONTRAST_CONTROL, K1SRC_SINGLE_BRANCH_RESPONSE_CONTROL, K1SRC_SAME_DATA_AMPLITUDE_RESCUE
interpretation: possible external K1 routes are now explicit, but no source route is authorized yet
```

Source-split family-mean K1 policy:

```text
script: scripts/build_source_split_family_mean_k1_policy.py
policy: evidence/source_split_family_mean_k1_policy.csv
readiness: evidence/source_split_family_mean_k1_policy_readiness.csv
family_count: 2
usable_rows: 8
equal_weight_nonzero_rows: 8
mean_abs_equal_weight_response: 0.9367627784351423
allowed_policy_count: 0
interpretation: family-mean K1 is a possible future predeclared route, but it is not authorized as current external K1 because no policy was frozen before the current scorecard
```

Source-split future rerun protocol:

```text
script: scripts/build_source_split_future_rerun_protocol.py
protocol: evidence/source_split_future_rerun_protocol.csv
summary: evidence/source_split_future_rerun_protocol_summary.csv
allowed_current_rerun_count: 0
preferred_protocol: SSRERUN_LIKELIHOOD_NATIVE_K1_V1
secondary_protocol: SSRERUN_FAMILY_MEAN_EQUAL_WEIGHT_V1
forbidden_protocol: SSRERUN_FORBIDDEN_CURRENT_SCORECARD_RESCUE
rho_upper_bound: 4.0
interpretation: no current rerun is authorized; future rerun requires predeclared K1 export before locked K2/null scoring
```

Source-split family-mean K1 future export:

```text
script: scripts/build_source_split_family_mean_k1_future_export.py
candidate: data/k1/source_split_external_k1_response.csv
summary: evidence/source_split_family_mean_k1_future_export_summary.csv
validator: evidence/source_split_external_k1_export_readiness.csv
rows: 8
nonzero_rows: 8
mean_abs_k1_response: 0.9367627784351423
mean_k1_sigma: 0.7071067811865476
allowed_for_current_rerun: false
allowed_for_future_rerun: true
validator_allowed_for_primary_k1: false
blocking_issue: not_marked_primary_candidate
interpretation: future K1 candidate exists, but the current measurement gate remains closed
```

Source-split future K1/K2 dry run:

```text
script: scripts/run_source_split_future_k1_k2_dry_run.py
scorecard: evidence/source_split_future_k1_k2_dry_run.csv
summary: evidence/source_split_future_k1_k2_dry_run_summary.csv
current_rerun_authorized: false
best_aic_model: POLY_DEG2_CONTROL
k1_family_mean_aic: 25.062371419386807
k2_rho4_aic: 52.5499794390236
delta_aic_k2_rho4_minus_k1: 27.487608019636795
k2_rho4_sign_stable_violations: 2
interpretation: future-only dry run weakens the family-mean route; likelihood-native joint SN+BAO K1 remains the cleaner next path
```

Source-split likelihood-native K1 plan:

```text
script: scripts/build_source_split_likelihood_native_k1_plan.py
spec: docs/source_split_likelihood_native_k1_spec.md
plan: evidence/source_split_likelihood_native_k1_plan.csv
readiness: evidence/source_split_likelihood_native_k1_readiness.csv
required_artifacts: 9
available_or_preflight_artifacts: 9
blocking_artifacts: 5
likelihood_native_k1_export_allowed: false
preferred_next_artifact: LNK1_BASELINE_PREDICTION_VECTOR
current_decision: likelihood_native_k1_not_ready
interpretation: all required artifacts now have data or preflight placeholders, but baseline/vector promotion, covariance promotion, K1 export, and null scoring are still blocking
```

Source-split likelihood-native parameter source:

```text
script: scripts/build_source_split_likelihood_native_parameters.py
parameters: data/k1/source_split_likelihood_native_parameters.yaml
summary: evidence/source_split_likelihood_native_parameters_summary.csv
baseline_id: SOURCE_SPLIT_LIKELIHOOD_NATIVE_CMB_ONLY_BASELINE_V1
parameter_source: public_cmb_only_bestfit_preflight
H0: 67.060759
OmegaM: 0.31779326
rd_mpc: 147.30766
allowed_for_k1_export_now: false
blocking_issue: baseline_prediction_preflight_not_primary;coordinate_map_preflight_not_promoted
interpretation: parameter source is frozen, but this is not yet a K1 response export or measurement validation
```

Source-split likelihood-native baseline prediction:

```text
script: scripts/build_source_split_likelihood_native_baseline_prediction.py
baseline_prediction: data/k1/source_split_likelihood_native_baseline_prediction.csv
summary: evidence/source_split_likelihood_native_baseline_prediction_summary.csv
rows: 7
mean_abs_raw_source_split_response: 0.1722387688855695
mean_abs_centered_control_source_split_response: 0.07615159034107458
allowed_as_primary_k1_candidate: false
blocking_issue: sn_nuisance_not_likelihood_native;coordinate_map_preflight_not_promoted;joint_covariance_not_promoted
interpretation: baseline vector is available as preflight only; it is not a primary K1 export
```

Source-split likelihood-native coordinate map:

```text
script: scripts/build_source_split_likelihood_native_coordinate_map.py
coordinate_map: data/k1/source_split_likelihood_native_coordinate_map.csv
summary: evidence/source_split_likelihood_native_coordinate_map_summary.csv
rows: 7
coordinate_map_id: SOURCE_SPLIT_CMB_CHI_COORDINATE_PREFLIGHT_V1
omega_m: 0.31779326
x_min: 0.38793451852076766
x_max: 1.0
allowed_for_k1_export: false
interpretation: coordinate map is frozen as preflight, but not yet promoted to likelihood-native K1 export quality
```

Source-split likelihood-native K1 promotion gate:

```text
script: scripts/check_source_split_likelihood_native_k1_promotion.py
gate: evidence/source_split_likelihood_native_k1_promotion_gate.csv
summary: evidence/source_split_likelihood_native_k1_promotion_summary.csv
checks: 5
available_checks: 4
promotable_checks: 0
blocking_checks: 5
primary_k1_promotion_allowed: false
blocking_issue: PROMO_BASELINE_VECTOR;PROMO_COORDINATE_MAP;PROMO_COVARIANCE_POLICY;PROMO_NULL_SCORECARD;PROMO_EXTERNAL_K1_EXPORT
interpretation: promotion gate remains closed; baseline and coordinate artifacts exist, but K1 export quality is not reached
```

Source-split likelihood-native nuisance policy:

```text
policy: docs/source_split_likelihood_native_nuisance_policy.md
primary_response_column: RawSourceSplitResponse
control_response_column: CenteredControlSourceSplitResponse
same_sample_centering_for_primary_k1: false
interpretation: nuisance ambiguity is now bounded; centered response is a control, not primary K1
```

Source-split likelihood-native coordinate promotion:

```text
policy: docs/source_split_likelihood_native_coordinate_promotion.md
coordinate_policy_id: SOURCE_SPLIT_CMB_CHI_COORDINATE_POLICY_V1
coordinate_map_id: SOURCE_SPLIT_CMB_CHI_COORDINATE_PREFLIGHT_V1
coordinate_selected_after_k2_scoring: false
coordinate_controls_reported: true
interpretation: CMB-chi coordinate is declared for the next benchmark candidate, but K1 export remains blocked by covariance/null promotion
```

Source-split likelihood-native covariance promotion:

```text
policy: docs/source_split_likelihood_native_covariance_promotion.md
covariance_class: declared_shrinkage_benchmark_covariance
public_full_covariance: false
shrinkage_benchmark: true
measurement_validation_allowed: false
interpretation: covariance policy can support internally consistent preflight null scoring, but not measurement validation
```

Source-split likelihood-native null-scorecard guard:

```text
script: scripts/run_source_split_likelihood_native_null_scorecard.py
readiness: evidence/source_split_likelihood_native_null_scorecard_readiness.csv
scorecard: evidence/source_split_likelihood_native_null_scorecard.csv
scorecard_allowed: true
best_aic_model: POLY_DEG2
k1_no_memory_aic: 139789.55908762495
k2_locked_rho4_aic: 136480.7438339473
poly_deg2_aic: 2667.832384218718
interpretation: K2 improves over K1 on this preflight vector, but polynomial controls dominate; not measurement validation
```

Source-split likelihood-native external K1 export:

```text
script: scripts/build_source_split_likelihood_native_external_k1_export.py
export: data/k1/source_split_external_k1_response.csv
summary: evidence/source_split_likelihood_native_external_k1_export_summary.csv
validator: evidence/source_split_external_k1_export_readiness.csv
rows: 8
allowed_for_primary_k1: true
provenance_type: likelihood_native_baseline
mean_abs_k1_response: 0.17046820413894592
interpretation: primary K1 export validates for preflight scoring, but does not create measurement validation
```

Source-split likelihood-native promotion final state:

```text
primary_k1_promotion_allowed: true
promotable_checks: 5
blocking_checks: 0
interpretation: K1 promotion gate is clean for preflight scoring; scientific result remains weak because simple controls outperform K2
```

Source-split likelihood-native dominance diagnosis:

```text
script: scripts/diagnose_likelihood_native_scorecard_dominance.py
audit: evidence/source_split_likelihood_native_scorecard_dominance_audit.csv
summary: evidence/source_split_likelihood_native_scorecard_dominance_summary.csv
best_chi2_model: POLY_DEG2
k2_interpretation: k2_improves_over_k1_but_not_over_flexible_controls
top_k2_contribution_grid_index: 0
interpretation: K2 is no longer degenerate with K1, but flexible controls dominate the proxy score
```

Source-split likelihood-native amplitude gap:

```text
script: scripts/diagnose_likelihood_native_amplitude_gap.py
audit: evidence/source_split_likelihood_native_amplitude_gap_audit.csv
summary: evidence/source_split_likelihood_native_amplitude_gap_summary.csv
rows_target_gt_5x_k2: 4
mean_abs_target: 2.2234938839612974
mean_abs_k1: 0.17046820413894592
mean_abs_k2_rho4: 0.4831648049861127
low_depth_mean_abs_target: 4.572063629864912
low_depth_mean_abs_k2_rho4: 0.27297731740775516
interpretation: low-depth amplitude gap dominates the likelihood-native preflight chi2; do not rescale K1 post hoc
```

Source-split likelihood-native rho requirement:

```text
script: scripts/diagnose_likelihood_native_rho_requirement.py
audit: evidence/source_split_likelihood_native_rho_requirement_audit.csv
scan: evidence/source_split_likelihood_native_bounded_rho_scan.csv
summary: evidence/source_split_likelihood_native_rho_requirement_summary.csv
rows_exact_match_within_rho_bound: 0
rows_rho_exceeds_bound: 8
best_bounded_rho: 4.0
best_bounded_rho_chi2: 136480.7438339473
k1_no_memory_chi2: 139789.55908762495
interpretation: bounded rho prefers the upper bound and improves over K1, but cannot close the amplitude gap; rho>4 rescue is not allowed
```

Source-split likelihood-native scale/covariance sensitivity:

```text
script: scripts/run_likelihood_native_scale_covariance_sensitivity.py
results: evidence/source_split_likelihood_native_scale_covariance_sensitivity.csv
summary: evidence/source_split_likelihood_native_scale_covariance_summary.csv
cases_tested: 9
k2_improves_over_k1_cases: 9
k2_beats_best_poly_cases: 1
competitive_case: diag_target_fraction_floor_25pct
interpretation: K2 consistently improves over K1, but only beats flexible controls under a strong target-fraction error floor; this is scale/covariance sensitivity, not validation
```

Source-split reconstruction-family candidate export:

```text
script: scripts/build_source_split_reconstruction_family_candidate_export.py
candidate_export: data/reconstruction_families/source_split_reconstruction_family_responses.csv
validation: evidence/source_split_reconstruction_family_export_validation.csv
families: 2
usable_target_rows: 8
data_rows: 16
export_validation_allowed_for_k2_scoring: true
interpretation: candidate export blocker is resolved; this is benchmark input plumbing, not a measurement result
```

Transform contract status:

```text
available_transform: T0_RAW_OBSERVABLE_PREFLIGHT
available_residual_preflight: T1_BAO_DISTANCE_RATIO_RESIDUAL
measurement_gate_allowed_transforms: none
reason: T0 is not a finite-memory diagnostic vector; T1 uses an audit-fiducial baseline and has no K1 export
next_transform_target: likelihood-native or coordinate-native BAO baseline export
```

BAO residual null benchmark:

```text
script: scripts/run_bao_residual_null_benchmark.py
finding: CONSTANT_OFFSET is the best AIC model for DR1 and DR2 under the T1 audit baseline
interpretation: the audit-fiducial BAO baseline leaves a global residual offset; this is not a finite-memory detection
measurement_gate_status: closed
```

BAO baseline offset diagnosis:

```text
script: scripts/diagnose_bao_baseline_offset.py
output: evidence/bao_baseline_offset_diagnosis.csv
finding: audit baseline leaves an approximately 1.5 percent BAO scale offset
effective_rd_if_absorbed: about 144.8 Mpc for both DR1 and DR2
interpretation: baseline scale calibration issue, not finite-memory evidence
next: likelihood-native or coordinate-native BAO baseline export
```

BAO baseline export readiness:

```text
script: scripts/check_bao_baseline_export_readiness.py
output: evidence/bao_baseline_export_readiness.csv
eligible_measurement_gate_baselines: none
available_preflight_baseline: AUDIT_FLAT_LCDM_BAO_V0 only
reason: audit baseline is not likelihood-native or coordinate-native
next: freeze a public likelihood-native BAO baseline export before K2 scoring
```

BAO rd-offset sensitivity:

```text
script: scripts/build_bao_rd_offset_sensitivity.py
output: evidence/bao_rd_offset_sensitivity_summary.csv
finding: absorbing the same-data BAO scale offset reduces the zero-residual chi2 to the constant-offset benchmark level
interpretation: confirms the T1 issue is baseline-scale dominated
measurement_gate_status: closed because rd is calibrated from the same data
```

BAO likelihood-native baseline source readiness:

```text
script: scripts/check_bao_likelihood_baseline_sources.py
output: evidence/bao_likelihood_baseline_source_readiness.csv
eligible_baseline_sources: none
finding: official DESI DR2 iminuit base/desi-bao-all best-fit is ingested as a baseline-export preflight
recomputed_chi2: 10.255 versus reported DESI BAO chi2 10.282
blocked_paths: public best-fit baseline is optimized on the same BAO data; independent K2 scoring protocol and K1/null policy are not registered
interpretation: source gate correctly prevents data-only inputs or same-data rd offsets from becoming K2 baselines
```

BAO branch decision:

```text
script: scripts/build_bao_branch_decision.py
output: evidence/bao_branch_decision_matrix.csv
decision: BAO measurement-gate scoring remains closed
reason: public inputs and transform plumbing are solved, but no locked BAO K1 response target is selected
k1_candidate_status: CMB-only unit-covariance candidate is normalizable but zero-response null is AIC-preferred
interpretation: BAO is a documented preflight/control branch, not the next primary measurement route
recommended_next_branch: SN+BAO/source-split or coordinate-native public benchmark work
```

BAO baseline scorecard:

```text
script: scripts/build_bao_baseline_scorecard.py
output: evidence/bao_baseline_scorecard.csv
same_data_bestfit_chi2: about 10.26
same_data_rd_offset_chi2: about 10.33
cmb_only_independent_chi2: about 33.82
audit_baseline_chi2: about 41.35
interpretation: same-data baselines fit best; CMB-only is more independent but less BAO-compatible
measurement_gate_status: closed until K2/null protocol is registered
```

BAO K2 protocol readiness:

```text
script: scripts/check_bao_k2_protocol_readiness.py
output: evidence/bao_k2_protocol_readiness.csv
ready_for_k2_scoring: false
reason: protocol is registered but intentionally blocked
baseline_policy: same-data baselines are sensitivity controls; independent baseline required for interpretation
required_nulls: ZERO_RESIDUAL, CONSTANT_OFFSET, POLY_DEG1, POLY_DEG2
rho_policy: rho<=4, p=3 locked
```

BAO K1 response readiness:

```text
script: scripts/check_bao_k1_response_readiness.py
output: evidence/bao_k1_response_readiness.csv
allowed_for_k2_scoring: none
usable_controls: ZERO_RESIDUAL, CONSTANT_OFFSET, DESI same-data bestfit, CMB-only residual
missing_object: BAO_K1_LOCKED_RESPONSE_TARGET
interpretation: K2 remains blocked because the no-memory response/amplitude target is not frozen
```

BAO locked K1 response target:

```text
script: scripts/check_bao_k1_locked_response.py
output: evidence/bao_k1_locked_response_readiness.csv
required_object: BAO_K1_LOCKED_RESPONSE_TARGET
current_status: missing
candidate: BAO_K1_CMB_ONLY_UNIT_COVNORM_CANDIDATE
candidate_status: null scorecard attached; zero response is AIC-preferred
measurement_gate_status: closed
```

SN+BAO/source-split readiness:

```text
script: scripts/check_source_split_readiness.py
output: evidence/source_split_readiness.csv
public_sn_input: available
public_bao_input: available
current_sign_family_packet: available, with 5 sign-stable and 4 sign-unstable rows
null_comparators: registered
blocking_issue: coordinate-native K1/no-memory target is not selected
measurement_gate_status: closed
next: build source-split diagnostic transform and coordinate-native K1 target before K2 scoring
```

SN+BAO/source-split transform contract:

```text
script: scripts/check_source_split_transform_contract.py
registry: evidence/source_split_transform_registry.csv
output: evidence/source_split_transform_readiness.csv
available_template: current distilled packet with sign-family columns
available_control: BAO anchor/control path
blocking_issue: coordinate-native K1/no-memory target and public joint transform are not exported
measurement_gate_status: closed
next: define source-split diagnostic vector, covariance propagation, sign-family export, and K1 target
```

SN residual preflight:

```text
script: scripts/build_sn_residual_preflight.py
rows: evidence/sn_residual_preflight.csv
binned_rows: evidence/sn_residual_binned_preflight.csv
summary: evidence/sn_residual_preflight_summary.csv
input: Pantheon+SH0ES SN data and covariance
status: available as transform-development artifact
blocking_issue: same-sample offset is not a coordinate-native K1 target; no joint SN+BAO covariance yet
measurement_gate_status: closed
```

SN+BAO joint source-split preflight:

```text
script: scripts/build_source_split_joint_preflight.py
rows: evidence/source_split_joint_preflight.csv
summary: evidence/source_split_joint_preflight_summary.csv
rows_on_current_grid: 9
rows_with_sn_and_bao: 8
status: available as transform-development artifact
blocking_issue: SN and BAO residuals are in different units; coordinate-native K1 and joint covariance are missing
measurement_gate_status: closed
```

SN+BAO standardized source-split preflight:

```text
script: scripts/build_source_split_standardized_preflight.py
rows: evidence/source_split_standardized_preflight.csv
summary: evidence/source_split_standardized_preflight_summary.csv
rows_with_sn_and_bao: 8
same_sign_rows: 3
opposite_sign_rows: 5
status: common diagonal standardized audit scale available
blocking_issue: diagonal standardization only; coordinate-native K1 and joint covariance are missing
interpretation: source-split warning / transform-development evidence, not K2 scoring
```

SN+BAO source-split sign-tension diagnosis:

```text
script: scripts/diagnose_source_split_sign_tension.py
audit: evidence/source_split_sign_tension_audit.csv
summary: evidence/source_split_sign_tension_summary.csv
rows_with_sn_and_bao: 8
sign_stable_rows_with_sn_and_bao: 5
sign_stable_opposite_sign_rows: 4
sign_unstable_rows_with_sn_and_bao: 3
sign_unstable_opposite_sign_rows: 1
interpretation: source-split tension is concentrated in sign-stable rows under the diagonal standardized preflight
measurement_gate_status: closed
```

SN+BAO source-split covariance sensitivity:

```text
script: scripts/run_source_split_covariance_sensitivity.py
rows: evidence/source_split_covariance_sensitivity.csv
summary: evidence/source_split_covariance_sensitivity_summary.csv
rho_sn_bao_grid: -0.75 to 0.75
opposite_sign_rows: 5 of 8 across proxy correlations
sign_stable_opposite_sign_rows: 4 of 5 across proxy correlations
interpretation: source-split warning persists under simple within-row correlation proxies
measurement_gate_status: closed because public joint covariance and coordinate-native K1 are missing
```

SN+BAO source-split K1 target readiness:

```text
script: scripts/check_source_split_k1_target.py
registry: evidence/source_split_k1_target_registry.csv
output: evidence/source_split_k1_target_readiness.csv
allowed_for_k2_scoring: none
usable_controls: current distilled K1, SN-only centered residual, BAO-only CMB candidate, standardized zero response
required_target: SSK1_COORDINATE_NATIVE_SOURCE_SPLIT_TARGET
blocking_issue: joint covariance and sign-family export are missing; no coordinate-native K1 target is selected
measurement_gate_status: closed
```

SN+BAO source-split covariance readiness:

```text
script: scripts/check_source_split_covariance.py
registry: evidence/source_split_covariance_registry.csv
output: evidence/source_split_covariance_readiness.csv
allowed_for_k2_scoring: none
available_controls: diagonal standardized proxy, within-row correlation proxy
required_target: public or shrinkage joint source-split covariance
blocking_issue: no coordinate-native K1 target and no public joint covariance
measurement_gate_status: closed
```

SN+BAO source-split sign-family export readiness:

```text
script: scripts/check_sign_family_export.py
registry: evidence/sign_family_export_registry.csv
output: evidence/sign_family_export_readiness.csv
allowed_for_k2_scoring: none
available_controls: current distilled packet, standardized source-split branch-sign audit
required_target: SF_PUBLIC_SOURCE_SPLIT_FAMILIES
blocking_issue: public reconstruction families and sign-stable rule are not exported in coordinate-native source-split space
measurement_gate_status: closed
```

SN+BAO source-split gate dashboard:

```text
script: scripts/build_source_split_gate_dashboard.py
dashboard: evidence/source_split_gate_dashboard.csv
summary: evidence/source_split_gate_dashboard_summary.csv
open_input_gate: true
k2_scoring_authorized: false
closed_core_gates: SS_TRANSFORM, SS_K1_TARGET, SS_JOINT_COVARIANCE, SS_SIGN_FAMILY, SS_RECONSTRUCTION_FAMILY_EXPORT, SS_CANDIDATE_PATH_GUARD, SS_RECONSTRUCTION_FAMILY_PREVIEW, SS_SIGN_RULE_PROMOTION
primary_next_action: create a valid public reconstruction-family candidate export before promoting the sign rule or scoring K2
dashboard_gates: 9
```

SN+BAO source-split export task queue:

```text
script: scripts/build_source_split_export_task_queue.py
queue: evidence/source_split_export_task_queue.csv
summary: evidence/source_split_export_task_queue_summary.csv
completed_preflight_task: TQ1_COORDINATE_NATIVE_TRANSFORM
completed_control_preflight_task: TQ2_COORDINATE_NATIVE_K1
completed_policy_preflight_task: TQ3_JOINT_COVARIANCE
completed_branch_sign_preflight_task: TQ4_PUBLIC_SIGN_FAMILY
completed_schema_preflight_task: TQ4A_CANDIDATE_EXPORT_SCHEMA
completed_preview_task: TQ4B_CANDIDATE_EXPORT_PREVIEW
next_task: TQ4C_SIGN_RULE_PROMOTION
blocked_tasks: 3
k2_scoring_task: TQ5_LOCKED_K2_SCORECARD
k2_scoring_status: blocked_by_authorization_guard
```

SN+BAO coordinate-native source-split target:

```text
script: scripts/build_source_split_coordinate_native_target.py
rows: evidence/source_split_coordinate_native_target.csv
summary: evidence/source_split_coordinate_native_target_summary.csv
target_id: SS_TARGET_COORDINATE_NATIVE_V1
x_mapping: x_chi_normalized_flat_lcdm_audit
response: SN_standardized_minus_BAO_standardized
rows: 9
usable_rows: 8
mean_abs_response: 2.2234938839612974
sign_stable_usable_rows: 5
opposite_sign_usable_rows: 5
status: preflight target exported
ready_for_k2_scoring: false
blocking_issue: coordinate-native K1, joint covariance, and public sign-family export are still missing
interpretation: TQ1 is completed as a target-vector preflight only; TQ2 is now the main next task
```

SN+BAO coordinate-native K1/no-memory control:

```text
script: scripts/build_source_split_k1_coordinate_native_target.py
rows: evidence/source_split_k1_coordinate_native_target.csv
summary: evidence/source_split_k1_coordinate_native_target_summary.csv
k1_target_id: SSK1_COORDINATE_NATIVE_SOURCE_SPLIT_TARGET
no_memory_definition: zero_source_split_branch_contrast
usable_rows: 8
mean_k1_no_memory_response: 0.0
mean_abs_source_split_response: 2.2234938839612974
status: K1 control exported, not scoring target
ready_for_k2_scoring: false
blocking_issue: joint covariance and public sign-family export are still missing
interpretation: TQ2 is completed as a conservative no-memory control preflight only; TQ3 and TQ4 remain required before scoring
```

SN+BAO source-split covariance policy:

```text
script: scripts/build_source_split_joint_covariance_policy.py
matrix: evidence/source_split_joint_covariance_policy.csv
summary: evidence/source_split_joint_covariance_policy_summary.csv
covariance_id: SSCOV_SHRINKAGE_SOURCE_SPLIT
rows: 8
matrix_entries: 64
rho_sn_bao: 0.0
lambda_shrink: 0.15
correlation_length: 0.25
min_eigenvalue: 1.7479466832147477
positive_definite: true
status: shrinkage covariance policy exported, not public full covariance
ready_for_k2_scoring: false
blocking_issue: public sign-family export is still missing; public full covariance remains preferred
interpretation: TQ3 is completed as a covariance-policy preflight only; TQ4 remains required before scoring
```

SN+BAO source-split sign-family preflight:

```text
script: scripts/build_source_split_public_sign_family.py
rows: evidence/source_split_public_sign_family.csv
summary: evidence/source_split_public_sign_family_summary.csv
sign_family_id: SF_PUBLIC_SOURCE_SPLIT_FAMILIES
families: SN_standardized_branch; BAO_standardized_branch
usable_rows: 8
public_branch_stable_rows: 3
public_branch_opposite_rows: 5
template_stable_rows: 5
status: public branch sign-family preflight exported, not full reconstruction-family
ready_for_k2_scoring: false
blocking_issue: full public reconstruction-family export is still missing
interpretation: TQ4 is completed as a branch-sign preflight only; K2 scoring remains blocked
```

SN+BAO reconstruction-family upgrade contract:

```text
script: scripts/build_source_split_reconstruction_family_upgrade.py
contract: evidence/source_split_reconstruction_family_upgrade_contract.csv
summary: evidence/source_split_reconstruction_family_upgrade_summary.csv
requirements: 5
satisfied_requirements: 3
blocking_requirements: 2
blocking_issue: reconstruction_families_missing; family_level_sign_rule_missing
status: reconstruction-family upgrade required
ready_for_k2_scoring: false
interpretation: the repo now records exactly why branch-sign preflight cannot be treated as scoring-grade sign-family evidence
```

Physical-null source-package probe:

```text
script: scripts/probe_physical_null_candidate_sources.py
rows: evidence/physical_null_candidate_source_probe.csv
summary: evidence/physical_null_candidate_source_probe_summary.csv
targets_probed: 3
probe_completed: 3
sources_with_data_like_files: 1
sources_with_tex_tables: 2
sources_with_figures: 3
calibration_inputs_ready_now: 0
recommended_next_action: begin provisional extraction from highest-priority completed source probe
primary_blocking_issue: candidate_values_not_extracted_or_mapped
interpretation: acquisition-positive source probe, not measurement validation
```

Physical-null provisional extraction manifest:

```text
script: scripts/build_physical_null_provisional_extraction_manifest.py
rows: evidence/physical_null_provisional_extraction_manifest.csv
summary: evidence/physical_null_provisional_extraction_summary.csv
rows_extracted: 8
backreaction_rows: 1
dyer_roeder_rows: 7
benchmark_inputs_ready_now: 0
rows_blocked_for_benchmark: 8
interpretation: optical candidates recorded, backreaction route remains numeric-extraction blocked
```

Physical-null mapping readiness:

```text
script: scripts/check_physical_null_mapping_readiness.py
rows: evidence/physical_null_mapping_readiness.csv
summary: evidence/physical_null_mapping_readiness_summary.csv
rows_checked: 8
rows_with_full_target_coverage: 2
rows_with_transform_to_source_split: 0
rows_with_covariance_propagation: 0
benchmark_inputs_ready_now: 0
best_coverage_extraction_id: PX_ZKDR_1303_TABLE1_JOINT_ALPHA_PRIOR
interpretation: full-coverage optical candidates exist, but transform/covariance blockers remain
```

Physical-null mapping task queue:

```text
script: scripts/build_physical_null_mapping_task_queue.py
rows: evidence/physical_null_mapping_task_queue.csv
summary: evidence/physical_null_mapping_task_queue_summary.csv
recommended_first_task: PNMAP_01
recommended_first_extraction_id: PX_ZKDR_1303_TABLE1_JOINT_ALPHA_PRIOR
benchmark_gate_open_tasks: 0
primary_blocking_issue: transform_and_covariance_missing
```

Physical-null alpha transform contract:

```text
script: scripts/build_physical_null_alpha_transform_contract.py
policy: evidence/physical_null_alpha_transform_policy.csv
preview: evidence/physical_null_alpha_response_preview.csv
summary: evidence/physical_null_alpha_transform_summary.csv
candidate_extractions_previewed: 2
preview_rows: 16
scoring_allowed_rows: 0
transform_formula: response_i=(1-alpha)*DYER_ROEDER_OPTICAL_UNIT_NORM_V1_i
primary_blocking_issue: full_covariance_propagation_missing;sign_convention_audit_missing
interpretation: alpha transform preview exists but remains non-scoring
```

Physical-null alpha sign-convention audit:

```text
script: scripts/audit_physical_null_alpha_sign_convention.py
rows: evidence/physical_null_alpha_sign_convention_audit.csv
summary: evidence/physical_null_alpha_sign_convention_summary.csv
as_declared_sign_match_fraction: 0.375
as_declared_sign_stable_match_fraction: 0.600
inverted_sign_match_fraction: 0.625
inverted_sign_stable_match_fraction: 0.400
scoring_allowed: false
interpretation: sign convention remains externally unresolved; do not select by score
```

Physical-null alpha covariance preview:

```text
script: scripts/build_physical_null_alpha_covariance_preview.py
policy: evidence/physical_null_alpha_covariance_preview_policy.csv
matrix: evidence/physical_null_alpha_covariance_preview_matrix.csv
summary: evidence/physical_null_alpha_covariance_preview_summary.csv
covariance_families: ALPHA_COV_DIAGONAL_PREVIEW_V1; ALPHA_COV_EXP_X_PREVIEW_V1
candidate_extractions: 2
scoring_allowed: false
interpretation: alpha covariance plumbing exists, but source-native covariance remains missing
```

Physical-null alpha scoring authorization:

```text
script: scripts/check_physical_null_alpha_scoring_authorization.py
rows: evidence/physical_null_alpha_scoring_authorization.csv
summary: evidence/physical_null_alpha_scoring_authorization_summary.csv
candidates_checked: 2
transform_preview_candidates: 2
sign_audited_candidates: 2
covariance_preview_candidates: 2
source_native_covariance_ready_candidates: 0
scorecard_authorized_candidates: 0
measurement_validation_authorized_candidates: 0
primary_blocking_issue: external_sign_convention_not_frozen;source_native_covariance_missing;measurement_scorecard_not_authorized
```

## Remaining Work

- Decide release target: GitHub/Zenodo first, arXiv only with diagnostic-proposal
  framing.
- Build a full covariance or shrinkage-likelihood proxy before any strong
  observational paper.
- Replace the current diagonal-proxy gate score with a public covariance-aware
  benchmark.
- Define the public diagnostic transform from DESI/Pantheon+ products into the
  finite-memory benchmark space.
- Upgrade the SN+BAO/source-split branch-sign preflight to a public
  reconstruction-family export; the coordinate-native target-vector,
  zero-contrast K1 control, shrinkage covariance policy, and branch-sign
  preflights are already exported, and the upgrade contract is now explicit.
- Derive or ingest an externally predeclared nonzero source-split K1 target, or
  a likelihood-native K1 target; mechanically available K1 candidates are not
  promoted by the current gate.
- Fill and validate `data/k1/source_split_external_k1_response.csv` only from a
  predeclared external K1 source; do not derive it from the current scorecard.
- Select one external K1 source route from
  `evidence/source_split_external_k1_source_registry.csv`, preferably a
  likelihood-native joint SN+BAO no-memory baseline, before creating the K1
  export.
- If using the reconstruction-family mean route, freeze the family-mean and
  amplitude policy before a new scorecard rerun; the current equal-weight mean
  is only a future policy candidate.
- Do not rerun the source-split K2/null scorecard until a future rerun protocol
  has an external K1 export available before the comparison.
- Treat the current family-mean K1 export as future-only; promote it only in a
  new pre-registered rerun, not in the current scorecard.
- Pivot the next primary K1 work toward a likelihood-native joint SN+BAO
  baseline, because the family-mean future dry run weakens the secondary route.
- Create `data/k1/source_split_likelihood_native_parameters.yaml` as the next
  concrete artifact before attempting any likelihood-native K1 export.
- Replace the provisional `x=z/z_max` mapping with a frozen comoving-distance,
  optical-depth, or likelihood-native coordinate mapping.
- Publish threshold-sensitivity checks for the low-depth and endpoint
  admissibility gates.
- Keep the paper self-contained: bounded diagnostic module only.

## Paper Readiness Estimate

```text
theory-method diagnostic paper: 70-80%
measurement-validation paper: 20-30%
```
