# Finite-Memory Projection Corrections

This repository contains a public method-note packet for a bounded
finite-memory projection correction in cosmological consistency diagnostics.
Its role is to present a reproducible, predeclared diagnostic operator and a
modest comparison protocol for reconstruction-level envelopes.

## Status

Release-candidate method note. This is suitable for a disciplined diagnostic
proposal, not for a measurement-validation claim.

## Scope

The paper may claim that a predeclared finite-memory projection operator,

```text
W(x) = 1 + rho*x^3,  rho <= 4
```

defines a bounded diagnostic correction window that is compatible with the
BAO-only reconstructed consistency envelope and remains non-violating under a
reconstruction-aware SN+BAO sign-stability gate.

The paper must not claim that:

- the K2 operator is the final cosmological law;
- any background theory is established;
- cosmic backreaction is ruled out;
- a full covariance likelihood has been completed;
- the current diagnostics constitute a direct measurement claim.

## Measurement Gate Extension

The repository now includes a finite-memory measurement gate plan. This plan
keeps the present manuscript at diagnostic method-note level while specifying
what would be needed to test the finite-memory projection hypothesis against
locked prediction outputs, null comparators, covariance-aware benchmarks, and
explicit falsification criteria.

## Files

- `draft.md`: initial manuscript scaffold.
- `finite_memory_projection_corrections.pdf`: rendered PDF of the current draft.
- `outline.md`: section-level outline.
- `status.md`: claim discipline, current strength, and blockers.
- `reproducibility.md`: regeneration commands and source packets.
- `make_pdf.py`: lightweight ReportLab PDF renderer with display-equation support.
- `src/fmc/`: minimal finite-memory gate engine helpers.
- `scripts/run_gate_current_packet.py`: regenerates the current packet gate table.
- `scripts/run_coordinate_robustness.py`: checks locked K2 under predeclared coordinate mappings.
- `scripts/diagnose_coordinate_tension.py`: row-level diagnosis for the chi-normalized warning.
- `scripts/run_rho_coordinate_scan.py`: bounded rho scan with p fixed at 3.
- `scripts/build_coordinate_mapping_geometry.py`: coordinate mapping geometry table.
- `scripts/run_null_comparison.py`: null-model benchmark over current mappings.
- `scripts/build_model_scorecard.py`: compact summary of null-model results.
- `scripts/build_physical_null_proxy_templates.py`: physical-null unit-shape templates for backreaction and optical controls.
- `scripts/build_physical_null_amplitude_policy.py`: preflight amplitude policy for physical-null sanity/sensitivity controls.
- `scripts/build_physical_null_hierarchy.py`: comparator hierarchy separating physical nulls from overfit-risk controls.
- `scripts/run_physical_null_preflight_scorecard.py`: preflight scorecard for physical-null sanity/sensitivity controls.
- `scripts/diagnose_physical_null_preflight.py`: row-level audit for physical-null preflight competitiveness.
- `scripts/build_physical_null_calibration_requirements.py`: required independent calibration routes for physical-null amplitudes.
- `scripts/build_physical_null_calibration_source_registry.py`: candidate source registry and task queue for physical-null calibration.
- `scripts/build_physical_null_calibration_mapping_policy.py`: row-alignment policy for future physical-null calibration sources.
- `scripts/build_physical_null_calibration_covariance_policy.py`: uncertainty/covariance policy for future physical-null calibration sources.
- `scripts/build_physical_null_readiness_dashboard.py`: compact dashboard for the physical-null calibration branch.
- `scripts/build_physical_null_public_source_candidates.py`: concrete public-paper candidates for physical-null source acquisition.
- `scripts/build_physical_null_candidate_triage.py`: acquisition priority triage for physical-null source candidates.
- `scripts/probe_physical_null_candidate_sources.py`: arXiv source-package extractability probe for the first physical-null acquisition targets.
- `scripts/build_physical_null_provisional_extraction_manifest.py`: provisional physical-null source extraction manifest; not a benchmark ingestion script.
- `scripts/check_physical_null_mapping_readiness.py`: mapping/covariance readiness check for provisional physical-null rows.
- `scripts/build_physical_null_mapping_task_queue.py`: ranked follow-up queue for physical-null mapping work.
- `scripts/build_physical_null_alpha_transform_contract.py`: non-scoring alpha-to-source-split transform contract and response preview.
- `scripts/audit_physical_null_alpha_sign_convention.py`: non-scoring sign-convention audit for alpha-derived optical previews.
- `scripts/build_physical_null_alpha_covariance_preview.py`: non-scoring covariance-preview matrices for alpha-derived optical previews.
- `scripts/check_physical_null_alpha_scoring_authorization.py`: consolidated guard keeping alpha-derived physical-null scorecards closed until sign and covariance blockers are resolved.
- `scripts/diagnose_null_dominance.py`: row-level null dominance diagnosis.
- `scripts/run_subset_model_scorecard.py`: subset scorecards for sign/depth partitions.
- `scripts/run_packet_cross_validation.py`: current-packet leave-one-out and blocked validation.
- `scripts/run_shrinkage_covariance_sensitivity.py`: covariance-proxy sensitivity checks.
- `scripts/check_public_benchmark_readiness.py`: Phase II public benchmark readiness check.
- `scripts/validate_public_inputs.py`: local DESI/Pantheon+ input shape validation.
- `scripts/build_public_diagnostic_preflight.py`: raw public-observable preflight table builder.
- `scripts/check_diagnostic_transform_contract.py`: diagnostic-transform readiness check.
- `scripts/build_bao_residual_preflight.py`: T1 BAO log-residual preflight transform.
- `scripts/run_bao_residual_null_benchmark.py`: null-comparator benchmark on T1 BAO residuals.
- `scripts/diagnose_bao_baseline_offset.py`: constant-offset diagnosis for T1 BAO residuals.
- `scripts/check_bao_baseline_export_readiness.py`: BAO baseline export eligibility check.
- `scripts/build_bao_rd_offset_sensitivity.py`: same-data `rd` offset sensitivity check.
- `scripts/check_bao_likelihood_baseline_sources.py`: likelihood-native BAO baseline source check.
- `scripts/build_desi_bestfit_bao_baseline.py`: DESI DR2 public iminuit best-fit BAO baseline export.
- `scripts/build_cmb_only_bao_baseline.py`: public CMB-only best-fit BAO baseline export.
- `scripts/build_bao_baseline_scorecard.py`: compact BAO baseline preflight comparison.
- `scripts/check_bao_k2_protocol_readiness.py`: pre-K2 BAO protocol readiness gate.
- `scripts/check_bao_k1_response_readiness.py`: BAO K1/no-memory response readiness gate.
- `scripts/check_bao_k1_locked_response.py`: locked BAO K1 response target readiness gate.
- `scripts/build_bao_k1_candidate.py`: CMB-only unit-covariance-norm K1 candidate builder.
- `scripts/run_bao_k1_candidate_null_scorecard.py`: null scorecard for the K1 candidate.
- `scripts/build_bao_branch_decision.py`: BAO branch stop/pivot decision matrix builder.
- `scripts/check_source_split_readiness.py`: SN+BAO/source-split branch readiness check.
- `scripts/check_source_split_transform_contract.py`: source-split transform contract check.
- `scripts/build_sn_residual_preflight.py`: Pantheon+ SN residual preflight transform.
- `scripts/build_source_split_joint_preflight.py`: joint SN+BAO source-split preflight builder.
- `scripts/build_source_split_standardized_preflight.py`: standardized SN+BAO source-split preflight builder.
- `scripts/diagnose_source_split_sign_tension.py`: sign-tension diagnosis for standardized source-split rows.
- `scripts/run_source_split_covariance_sensitivity.py`: covariance-proxy sensitivity for source-split warning.
- `scripts/check_source_split_k1_target.py`: source-split K1/no-memory target readiness gate.
- `scripts/check_source_split_covariance.py`: source-split joint covariance readiness gate.
- `scripts/check_sign_family_export.py`: source-split sign-family export readiness gate.
- `scripts/build_source_split_gate_dashboard.py`: compact source-split gate dashboard builder.
- `scripts/build_source_split_export_task_queue.py`: ordered source-split export task queue builder.
- `scripts/build_source_split_coordinate_native_target.py`: coordinate-native source-split target preflight builder.
- `scripts/build_source_split_k1_coordinate_native_target.py`: coordinate-native zero-contrast K1/no-memory control builder.
- `scripts/build_source_split_joint_covariance_policy.py`: coordinate-native shrinkage covariance policy builder.
- `scripts/build_source_split_public_sign_family.py`: coordinate-native public branch sign-family preflight builder.
- `scripts/build_source_split_reconstruction_family_upgrade.py`: reconstruction-family sign export upgrade contract builder.
- `scripts/check_source_split_reconstruction_family_sources.py`: source-split reconstruction-family source readiness check.
- `scripts/build_source_split_reconstruction_family_export_schema.py`: required schema/template builder for future public reconstruction-family responses.
- `scripts/validate_source_split_reconstruction_family_export.py`: validator for a future public reconstruction-family response export.
- `scripts/build_source_split_reconstruction_family_candidate_plan.py`: candidate-family plan for the missing public source-split response export.
- `scripts/build_source_split_reconstruction_family_response_preview.py`: non-scoring schema preview for SN/BAO branch responses.
- `scripts/build_source_split_family_sign_rule_preview.py`: non-scoring row-level family sign-stability preview.
- `scripts/check_source_split_sign_rule_promotion.py`: readiness check before the preview sign rule can become a scoring rule.
- `scripts/check_source_split_k2_scoring_authorization.py`: final source-split guard before any K2/null scorecard.
- `scripts/run_source_split_k2_null_scorecard.py`: authorized source-split K2/null preflight scorecard.
- `scripts/diagnose_source_split_k1_degeneracy.py`: row-level audit for zero-K1 multiplicative K2 degeneracy.
- `scripts/build_source_split_k1_response_candidate_audit.py`: nonzero K1 candidate provenance audit.
- `scripts/run_source_split_k1_candidate_sensitivity.py`: sensitivity scorecard for K1 candidates and their K2 responses.
- `scripts/check_source_split_k1_candidate_promotion.py`: promotion gate for primary K1 eligibility.
- `scripts/build_source_split_external_k1_export_schema.py`: required schema/template builder for external nonzero source-split K1 exports.
- `scripts/validate_source_split_external_k1_export.py`: validator for future external nonzero source-split K1 exports.
- `scripts/build_source_split_external_k1_source_registry.py`: registry of allowed, blocked, and control source routes for external K1.
- `scripts/build_source_split_family_mean_k1_policy.py`: policy gate for possible reconstruction-family mean K1 exports.
- `scripts/build_source_split_future_rerun_protocol.py`: preregistered rerun protocol for future source-split K2 scorecards.
- `scripts/build_source_branch_baseline_response_export.py`: diagnostic source-branch baseline response export for future source-realization gates.
- `scripts/build_source_realization_future_freeze_packet.py`: future-only source-realization freeze packet builder.
- `scripts/validate_source_realization_future_freeze_packet.py`: validator for the future-only source-realization freeze packet.
- `scripts/check_source_realization_rerun_readiness.py`: aggregate guard for whether a source-realization A2/K2 rerun is currently allowed.
- `scripts/audit_source_realization_poly2_dominance.py`: row-level POLY_DEG2 dominance audit for the source-realization dry run.
- `scripts/adjudicate_source_realization_poly2_role.py`: adjudicates whether POLY_DEG2 is a physical null, overfit control, or baseline/target absorber.
- `scripts/audit_source_realization_target_convention_absorber.py`: audits whether POLY_DEG2 is absorbing target-convention sign/scale structure.
- `scripts/audit_source_realization_baseline_drift_absorber.py`: audits whether POLY_DEG2 is absorbing baseline drift, local K1 cancellation, or source-branch normalization drift.
- `scripts/run_source_realization_survival_suite.py`: runs the source-realization penalty, out-of-sample, baseline-drift null, and K2 survival scorecard checks.
- `scripts/audit_source_realization_morphological_rule_tuning.py`: tests Tau Core morphological sector classifiers against global K2 and null-demotion readings.
- `scripts/build_source_split_family_mean_k1_future_export.py`: future-only equal-weight family-mean K1 export builder.
- `scripts/run_source_split_future_k1_k2_dry_run.py`: future-only dry run for the family-mean K1 route.
- `scripts/build_source_split_likelihood_native_k1_plan.py`: artifact checklist for the likelihood-native joint SN+BAO K1 route.
- `scripts/build_source_split_likelihood_native_parameters.py`: frozen CMB-only parameter source for the likelihood-native K1 route.
- `scripts/build_source_split_likelihood_native_baseline_prediction.py`: preflight baseline prediction vector from the frozen parameter source.
- `scripts/build_source_split_likelihood_native_coordinate_map.py`: preflight CMB-parameter comoving-distance coordinate map.
- `scripts/check_source_split_likelihood_native_k1_promotion.py`: promotion gate before any likelihood-native primary K1 export.
- `scripts/run_source_split_likelihood_native_null_scorecard.py`: guarded entry point that refuses scoring until primary K1 validates.
- `scripts/build_source_split_likelihood_native_external_k1_export.py`: exports the likelihood-native CMB-only raw source-split K1 baseline.
- `scripts/diagnose_likelihood_native_scorecard_dominance.py`: row-level diagnosis of K2/null dominance on the likelihood-native preflight scorecard.
- `scripts/diagnose_likelihood_native_amplitude_gap.py`: amplitude-gap diagnosis for the promoted likelihood-native K1/K2 preflight vector.
- `scripts/diagnose_likelihood_native_rho_requirement.py`: bounded-rho audit for the likelihood-native amplitude gap.
- `scripts/run_likelihood_native_scale_covariance_sensitivity.py`: covariance/scale sensitivity for the likelihood-native preflight scorecard.
- `scripts/run_likelihood_native_error_floor_sweep.py`: target-fraction error-floor sweep for the likelihood-native preflight scorecard.
- `scripts/build_likelihood_native_error_floor_policy.py`: policy gate for independent error-floor justification.
- `scripts/run_likelihood_native_branch_scatter_benchmark.py`: branch-scatter covariance preflight benchmark for likelihood-native K2.
- `scripts/check_likelihood_native_branch_scatter_promotion.py`: promotion gate for branch-scatter covariance status.
- `scripts/build_likelihood_native_covariance_source_registry.py`: registry and task queue for independent covariance/systematic routes.
- `scripts/build_likelihood_native_public_covariance_proxy.py`: first propagated public SN+BAO covariance proxy for the likelihood-native vector.
- `scripts/run_likelihood_native_cross_covariance_sensitivity.py`: SN-BAO cross-covariance sensitivity for the public covariance proxy.
- `scripts/build_likelihood_native_covariance_route_scorecard.py`: compact route-level comparison of covariance paths for likelihood-native K2.
- `scripts/diagnose_likelihood_native_covariance_gap.py`: row-level audit explaining branch-scatter versus public-proxy route dependence.
- `scripts/run_likelihood_native_polynomial_cv.py`: cross-validation audit for polynomial control stability on the likelihood-native source split.
- `scripts/build_likelihood_native_support_ladder.py`: compact evidence ladder for likelihood-native K2 support levels.
- `scripts/build_public_covariance_upgrade_queue.py`: task queue and readiness matrix for upgrading the public covariance route.
- `scripts/build_public_covariance_locked_rerun_protocol.py`: preregistered rerun protocol for future public-covariance K2 comparisons.
- `scripts/build_public_covariance_policy_registry.py`: policy registry for full-public, shrinkage, cross-covariance sensitivity, and forbidden covariance routes.
- `scripts/build_registered_shrinkage_rerun_template.py`: future registered-shrinkage rerun template with locked components and missing parameter policy.
- `scripts/build_registered_shrinkage_parameter_policy.py`: freezes shrinkage parameters and cross-covariance policy for a future preflight route.
- `scripts/check_registered_shrinkage_activation_gate.py`: activation gate for whether registered shrinkage may be used in a future preflight rerun.
- `scripts/run_registered_shrinkage_future_preflight.py`: future-preflight scorecard using the registered shrinkage policy; not measurement validation.
- `scripts/build_polynomial_control_fairness_audit.py`: policy audit for whether polynomial controls are fair nulls, overfit-risk controls, or blockers.
- `scripts/build_physical_null_hierarchy.py`: physical/null/control hierarchy separating physical comparators from overfit-risk controls.
- `scripts/build_physical_null_proxy_templates.py`: non-scoring backreaction and Dyer-Roeder/optical proxy templates on the source-split vector.
- `scripts/build_physical_null_amplitude_policy.py`: preflight amplitude policy for physical-null proxy templates.
- `scripts/build_source_split_candidate_export_handoff.py`: handoff manifest for the missing reconstruction-family candidate export.
- `scripts/build_source_split_reconstruction_family_candidate_export.py`: real source-split reconstruction-family candidate export builder.
- `scripts/check_source_split_candidate_path_guard.py`: guard against copying the non-scoring preview into the candidate path.
- `scripts/build_source_split_blocker_matrix.py`: compact matrix of all source-split K2 blockers.
- `scripts/build_source_split_sn_branch_export_handoff.py`: row-level handoff for the SN residual branch candidate rows.
- `scripts/build_source_split_bao_branch_export_handoff.py`: row-level handoff for the BAO residual branch candidate rows.
- `src/fmc/public_data.py`: skeleton public-product manifest validation.
- `src/fmc/covariance.py`: shared covariance proxy builders and public covariance placeholder.
- `data/public_ingest_manifest.yaml`: machine-readable public benchmark preflight manifest.
- `docs/public_data_candidates.md`: candidate public BAO/SN products for Phase II.
- `docs/diagnostic_transform_contract.md`: contract separating raw public inputs from K2 diagnostics.
- `docs/bao_residual_transform_preflight.md`: T1 BAO residual preflight definition.
- `docs/bao_baseline_export_plan.md`: BAO baseline export contract and blockers.
- `docs/bao_likelihood_baseline_source_plan.md`: source-readiness plan for fair BAO baseline export.
- `docs/bao_baseline_selection_policy.md`: baseline selection policy before K2 scoring.
- `docs/bao_k1_response_policy.md`: BAO K1/no-memory response policy before K2 scoring.
- `docs/bao_k1_locked_response_plan.md`: locked BAO K1 response target plan.
- `docs/bao_branch_pivot_decision.md`: BAO preflight branch decision and pivot rationale.
- `docs/source_split_benchmark_plan.md`: next-branch SN+BAO/source-split benchmark plan.
- `docs/source_split_transform_contract.md`: source-split diagnostic transform contract.
- `docs/sn_residual_transform_preflight.md`: SN residual transform preflight note.
- `docs/source_split_joint_preflight.md`: joint source-split preflight note.
- `docs/source_split_standardized_preflight.md`: standardized source-split preflight note.
- `docs/source_split_k1_target_plan.md`: source-split K1/no-memory target plan.
- `docs/source_split_covariance_plan.md`: source-split joint covariance plan.
- `docs/sign_family_export_plan.md`: source-split sign-family export plan.
- `docs/source_split_export_task_queue.md`: ordered source-split export task queue.
- `docs/source_split_coordinate_native_target.md`: coordinate-native source-split target preflight note.
- `docs/source_split_reconstruction_family_sources.md`: source registry for scoring-grade reconstruction-family inputs.
- `docs/source_split_reconstruction_family_export_schema.md`: required export schema for future reconstruction-family response inputs.
- `docs/source_split_reconstruction_family_candidate_plan.md`: candidate family plan for the missing response export.
- `docs/source_split_reconstruction_family_response_preview.md`: non-scoring response preview in the frozen schema.
- `docs/source_split_family_sign_rule_preview.md`: non-scoring family sign-stability preview.
- `docs/source_split_sign_rule_promotion_readiness.md`: promotion-readiness gate for the family sign rule.
- `docs/source_split_k2_scoring_authorization.md`: final K2 scoring authorization guard.
- `docs/source_split_k2_null_scorecard.md`: source-split K2/null preflight scorecard result.
- `docs/source_split_k1_degeneracy_audit.md`: source-split K1 degeneracy diagnosis and requirements.
- `docs/source_split_k1_candidate_sensitivity.md`: nonzero K1 candidate sensitivity result.
- `docs/source_split_k1_candidate_promotion.md`: primary-K1 promotion gate result.
- `docs/source_split_external_k1_export_schema.md`: schema and validator for the missing external nonzero K1 target.
- `docs/source_split_external_k1_source_registry.md`: source-route registry for the missing external K1 target.
- `docs/paper5_tau_specific_observable_blocker.md`: current Paper 5 blocker stating that further scoring is paused until the Tau Core theory hub derives and freezes a Tau-specific observable class.
- `docs/source_split_family_mean_k1_policy.md`: family-mean K1 policy gate result.
- `docs/source_split_future_rerun_protocol.md`: future rerun protocol for source-split K2 comparisons.
- `docs/source_split_family_mean_k1_future_export.md`: future-only family-mean K1 export status.
- `docs/source_split_future_k1_k2_dry_run.md`: future-only family-mean K1/K2 dry-run result.
- `docs/source_split_likelihood_native_k1_plan.md`: readiness plan for the preferred likelihood-native K1 route.
- `docs/source_split_likelihood_native_k1_spec.md`: frozen specification for the joint SN+BAO likelihood-native K1 route.
- `docs/source_split_likelihood_native_parameters.md`: status note for the frozen no-memory parameter source.
- `docs/source_split_likelihood_native_baseline_prediction.md`: status note for the preflight baseline prediction vector.
- `docs/source_split_likelihood_native_coordinate_map.md`: status note for the preflight coordinate map.
- `docs/source_split_likelihood_native_k1_promotion.md`: promotion-gate result for primary K1 eligibility.
- `docs/source_split_likelihood_native_scorecard_dominance.md`: dominance and amplitude-gap diagnosis for the likelihood-native preflight scorecard.
- `docs/source_split_likelihood_native_rho_requirement.md`: bounded-rho audit showing no rho rescue is authorized.
- `docs/source_split_likelihood_native_scale_covariance_sensitivity.md`: scale/covariance sensitivity for the likelihood-native preflight scorecard.
- `docs/source_split_likelihood_native_error_floor_sweep.md`: target-fraction error-floor sweep status for the likelihood-native preflight scorecard.
- `docs/source_split_likelihood_native_error_floor_policy.md`: policy gate for whether an error floor can be used in stronger K2 interpretation.
- `docs/source_split_likelihood_native_branch_scatter_benchmark.md`: branch-scatter covariance preflight benchmark result.
- `docs/source_split_likelihood_native_covariance_source_registry.md`: independent covariance/source registry for the likelihood-native branch.
- `docs/source_split_likelihood_native_public_covariance_proxy.md`: first public covariance proxy result for the likelihood-native branch.
- `docs/source_split_likelihood_native_cross_covariance_sensitivity.md`: cross-covariance sensitivity for the public covariance proxy.
- `docs/source_split_likelihood_native_covariance_route_scorecard.md`: route-level covariance scorecard separating branch-scatter strength from public-proxy weakness.
- `docs/source_split_likelihood_native_covariance_gap_audit.md`: row-level covariance-gap diagnosis for public-proxy versus branch-scatter routes.
- `docs/source_split_likelihood_native_polynomial_cv.md`: out-of-sample audit for polynomial control dominance.
- `docs/source_split_likelihood_native_support_ladder.md`: compact support ladder summarizing current K2 evidence strength and blockers.
- `docs/public_covariance_upgrade_queue.md`: upgrade queue for the public covariance route after the support ladder.
- `docs/public_covariance_locked_rerun_protocol.md`: locked protocol for future public-covariance reruns.
- `docs/public_covariance_policy_registry.md`: covariance and cross-covariance policy registry for future public benchmark routes.
- `docs/registered_shrinkage_rerun_template.md`: future registered-shrinkage rerun template; not executable yet.
- `docs/registered_shrinkage_parameter_policy.md`: registered shrinkage parameters for future preflight; no current rerun authorized.
- `docs/registered_shrinkage_activation_gate.md`: gate showing registered-shrinkage is future-preflight activatable but not validating.
- `docs/registered_shrinkage_future_preflight.md`: future-preflight result under the registered shrinkage policy.
- `docs/polynomial_control_fairness_audit.md`: audit deciding how polynomial controls should block or qualify stronger claims.
- `docs/physical_null_hierarchy.md`: hierarchy of physical nulls, diagnostic controls, and overfit-risk controls.
- `docs/physical_null_proxy_templates.md`: non-scoring physical-null proxy templates requiring amplitude policy before scorecard use.
- `docs/physical_null_amplitude_policy.md`: amplitude policy allowing physical-null preflight only as sanity/sensitivity controls.
- `docs/physical_null_preflight_scorecard.md`: first physical-null sanity/sensitivity scorecard result.
- `docs/physical_null_row_audit.md`: row-level reading of the physical-null preflight scorecard.
- `docs/physical_null_calibration_requirements.md`: missing calibration routes before physical-null measurement comparison.
- `docs/physical_null_calibration_source_registry.md`: candidate source classes and task queue for physical-null amplitude calibration.
- `docs/physical_null_calibration_mapping_policy.md`: mapping policy for projecting future physical-null sources to the source-split vector.
- `docs/physical_null_calibration_covariance_policy.md`: covariance policy for future physical-null calibration sources.
- `docs/physical_null_readiness_dashboard.md`: compact physical-null branch readiness summary.
- `docs/physical_null_public_source_candidates.md`: public candidate papers for future physical-null calibration input.
- `docs/physical_null_candidate_triage.md`: prioritized acquisition order for physical-null source candidates.
- `docs/source_split_likelihood_native_nuisance_policy.md`: policy separating raw baseline response from centered nuisance control.
- `docs/source_split_likelihood_native_coordinate_promotion.md`: policy for the CMB-chi depth coordinate used by the next benchmark candidate.
- `docs/source_split_likelihood_native_covariance_promotion.md`: policy for using shrinkage covariance as a declared preflight benchmark.
- `docs/source_split_candidate_export_handoff.md`: handoff and validation plan for the candidate export.
- `docs/source_split_reconstruction_family_candidate_export.md`: current validated candidate export note.
- `docs/source_split_candidate_path_guard.md`: guard for the real candidate-export path.
- `docs/source_split_blocker_matrix.md`: compact source-split blocker matrix.
- `docs/source_split_sn_branch_export_handoff.md`: SN residual branch export handoff.
- `docs/source_split_bao_branch_export_handoff.md`: BAO residual branch export handoff.
- `frozen/k2_operator_v1.yaml`: locked K2 operator configuration.
- `frozen/k1_baseline_v1.csv`: frozen K1 baseline derived from the current packet.
- `frozen/k1_baseline_manifest.yaml`: provenance manifest for the frozen K1 baseline.
- `data/k1/source_split_likelihood_native_parameters.yaml`: frozen CMB-only parameter source for the likelihood-native K1 route.
- `data/k1/source_split_likelihood_native_baseline_prediction.csv`: preflight baseline prediction vector, not primary K1.
- `data/k1/source_split_likelihood_native_coordinate_map.csv`: preflight coordinate map, not primary likelihood-native coordinate.
- `evidence/claim_matrix.csv`: distilled allowed/forbidden claims.
- `evidence/result_summary.csv`: minimal result table for the draft.
- `evidence/diagnostic_point_audit.csv`: point-level SN+BAO diagnostic gate table.
- `evidence/coordinate_mapping_policy.csv`: coordinate-mapping status and risks.
- `evidence/threshold_sensitivity.csv`: threshold-policy sensitivity plan.
- `evidence/threshold_kernel_outcomes.csv`: simple power-kernel outcomes under threshold variants.
- `evidence/open_problem_resolution_matrix.csv`: audit map from weakness to resolution.
- `docs/measurement_gate_plan.md`: roadmap from diagnostic compatibility to a measurement gate.
- `evidence/measurement_gate_matrix.csv`: staged measurement-gate checklist.
- `evidence/null_model_registry.csv`: null comparators for future benchmark tests.
- `evidence/gate_results_current.csv`: current packet gate-engine output.
- `evidence/coordinate_robustness_results.csv`: current coordinate-mapping robustness output.
- `evidence/coordinate_tension_audit.csv`: row-level chi-normalized tension diagnosis.
- `evidence/rho_coordinate_scan.csv`: bounded rho scan across coordinate mappings.
- `evidence/coordinate_mapping_geometry.csv`: geometry of the coordinate mappings.
- `evidence/null_comparison_results.csv`: null-model benchmark output.
- `evidence/model_scorecard.csv`: compact model comparison scorecard.
- `evidence/null_dominance_audit.csv`: row-level null dominance audit.
- `evidence/null_dominance_summary.csv`: summarized null dominance drivers.
- `evidence/subset_model_scorecard.csv`: subset model scorecard.
- `evidence/cross_validation_results.csv`: current-packet validation diagnostics.
- `evidence/shrinkage_covariance_sensitivity.csv`: covariance-proxy sensitivity results.
- `evidence/k1_baseline_provenance_audit.csv`: K1 baseline provenance and Phase II requirements.
- `evidence/public_benchmark_readiness.csv`: machine-readable public benchmark readiness status.
- `evidence/public_input_inventory.csv`: downloaded public input shape inventory.
- `evidence/public_diagnostic_transform_preflight.csv`: standardized raw public-observable rows.
- `evidence/public_diagnostic_transform_summary.csv`: public preflight transform summary.
- `evidence/diagnostic_transform_registry.csv`: registered diagnostic-transform candidates.
- `evidence/diagnostic_transform_readiness.csv`: transform contract readiness output.
- `evidence/bao_residual_transform_preflight.csv`: T1 BAO log-residual rows.
- `evidence/bao_residual_transform_summary.csv`: T1 BAO residual summary.
- `evidence/bao_residual_transform_covariance.csv`: propagated BAO residual covariance.
- `evidence/bao_residual_null_benchmark.csv`: T1 BAO residual null-comparator scores.
- `evidence/bao_residual_null_scorecard.csv`: compact T1 null benchmark scorecard.
- `evidence/bao_baseline_offset_diagnosis.csv`: T1 audit-baseline offset diagnosis.
- `evidence/bao_baseline_export_registry.csv`: BAO baseline export candidates and policy.
- `evidence/bao_baseline_export_readiness.csv`: BAO baseline export readiness check.
- `evidence/bao_rd_offset_sensitivity_preflight.csv`: non-eligible `rd` offset sensitivity rows.
- `evidence/bao_rd_offset_sensitivity_summary.csv`: non-eligible `rd` offset sensitivity summary.
- `evidence/bao_likelihood_baseline_source_registry.csv`: BAO baseline source candidates.
- `evidence/bao_likelihood_baseline_source_readiness.csv`: BAO baseline source readiness output.
- `evidence/desi_bestfit_bao_baseline_export.csv`: DESI DR2 best-fit BAO baseline rows.
- `evidence/desi_bestfit_bao_baseline_summary.csv`: DESI DR2 best-fit BAO baseline summary.
- `evidence/cmb_only_bao_baseline_export.csv`: CMB-only best-fit BAO baseline rows.
- `evidence/cmb_only_bao_baseline_summary.csv`: CMB-only best-fit BAO baseline summary.
- `evidence/bao_baseline_scorecard.csv`: BAO baseline preflight scorecard.
- `evidence/bao_baseline_selection_policy.csv`: active BAO baseline selection rules.
- `evidence/bao_k2_protocol_registry.csv`: predeclared BAO K2 scoring protocol.
- `evidence/bao_k2_protocol_readiness.csv`: BAO K2 protocol readiness output.
- `evidence/bao_k1_response_registry.csv`: BAO K1/no-memory response candidates.
- `evidence/bao_k1_response_readiness.csv`: BAO K1/no-memory response readiness output.
- `evidence/bao_k1_amplitude_policy.csv`: BAO K1 amplitude-normalization policy.
- `evidence/bao_k1_locked_response_registry.csv`: locked BAO K1 response candidates.
- `evidence/bao_k1_locked_response_readiness.csv`: locked BAO K1 response readiness output.
- `evidence/bao_k1_cmb_only_unit_covnorm_candidate.csv`: normalized CMB-only K1 candidate rows.
- `evidence/bao_k1_cmb_only_unit_covnorm_summary.csv`: normalized CMB-only K1 candidate summary.
- `evidence/bao_k1_candidate_null_scorecard.csv`: null scorecard for the CMB-only K1 candidate.
- `evidence/bao_branch_decision_matrix.csv`: BAO branch decision matrix.
- `evidence/source_split_readiness.csv`: SN+BAO/source-split branch readiness output.
- `evidence/source_split_transform_registry.csv`: source-split transform registry.
- `evidence/source_split_transform_readiness.csv`: source-split transform readiness output.
- `evidence/sn_residual_preflight.csv`: Pantheon+ SN residual preflight rows.
- `evidence/sn_residual_binned_preflight.csv`: SN residual rows binned to the current diagnostic grid.
- `evidence/sn_residual_preflight_summary.csv`: SN residual preflight summary.
- `evidence/source_split_joint_preflight.csv`: joint SN+BAO source-split preflight rows.
- `evidence/source_split_joint_preflight_summary.csv`: joint source-split preflight summary.
- `evidence/source_split_standardized_preflight.csv`: standardized source-split preflight rows.
- `evidence/source_split_standardized_preflight_summary.csv`: standardized source-split preflight summary.
- `evidence/source_split_sign_tension_audit.csv`: row-level standardized source-split sign-tension audit.
- `evidence/source_split_sign_tension_summary.csv`: source-split sign-tension summary.
- `evidence/source_split_covariance_sensitivity.csv`: source-split covariance-proxy sensitivity rows.
- `evidence/source_split_covariance_sensitivity_summary.csv`: source-split covariance-proxy sensitivity summary.
- `evidence/source_split_k1_target_registry.csv`: source-split K1/no-memory target registry.
- `evidence/source_split_k1_target_readiness.csv`: source-split K1/no-memory target readiness output.
- `evidence/source_split_covariance_registry.csv`: source-split joint covariance registry.
- `evidence/source_split_covariance_readiness.csv`: source-split joint covariance readiness output.
- `evidence/sign_family_export_registry.csv`: sign-family export registry.
- `evidence/sign_family_export_readiness.csv`: sign-family export readiness output.
- `evidence/source_split_gate_dashboard.csv`: compact source-split gate dashboard.
- `evidence/source_split_gate_dashboard_summary.csv`: source-split dashboard summary.
- `evidence/source_split_export_task_queue.csv`: ordered source-split export task queue.
- `evidence/source_split_export_task_queue_summary.csv`: source-split task queue summary.
- `evidence/source_split_coordinate_native_target.csv`: coordinate-native source-split target preflight rows.
- `evidence/source_split_coordinate_native_target_summary.csv`: coordinate-native target preflight summary.
- `evidence/source_split_k1_coordinate_native_target.csv`: coordinate-native zero-contrast K1/no-memory control rows.
- `evidence/source_split_k1_coordinate_native_target_summary.csv`: coordinate-native K1/no-memory control summary.
- `evidence/source_split_joint_covariance_policy.csv`: coordinate-native shrinkage covariance policy matrix.
- `evidence/source_split_joint_covariance_policy_summary.csv`: shrinkage covariance policy summary.
- `evidence/source_split_public_sign_family.csv`: coordinate-native public branch sign-family preflight rows.
- `evidence/source_split_public_sign_family_summary.csv`: public branch sign-family preflight summary.
- `evidence/source_split_reconstruction_family_upgrade_contract.csv`: requirements before branch signs become scoring-grade reconstruction-family signs.
- `evidence/source_split_reconstruction_family_upgrade_summary.csv`: reconstruction-family upgrade contract summary.
- `evidence/source_split_reconstruction_family_source_registry.csv`: registry separating templates, branch-sign preflights, and missing reconstruction-family sources.
- `evidence/source_split_reconstruction_family_source_readiness.csv`: readiness check for scoring-grade reconstruction-family source inputs.
- `evidence/source_split_reconstruction_family_export_schema.csv`: required columns and validation rules for a future reconstruction-family response export.
- `evidence/source_split_reconstruction_family_export_template.csv`: empty CSV template for that future export.
- `data/reconstruction_families/source_split_reconstruction_family_responses.csv`: validated source-split reconstruction-family candidate export.
- `evidence/source_split_reconstruction_family_export_validation.csv`: current validation output for the candidate export.
- `evidence/source_split_reconstruction_family_candidate_plan.csv`: candidate families for a future source-split response export.
- `evidence/source_split_reconstruction_family_candidate_summary.csv`: summary of the candidate-family plan.
- `evidence/source_split_reconstruction_family_response_preview.csv`: non-scoring SN/BAO branch response preview in the frozen schema.
- `evidence/source_split_reconstruction_family_response_preview_summary.csv`: summary of the response preview; K2 scoring remains blocked.
- `evidence/source_split_family_sign_rule_preview.csv`: row-level family sign-stability preview.
- `evidence/source_split_family_sign_rule_preview_summary.csv`: summary of the family sign-rule preview.
- `evidence/source_split_sign_rule_promotion_readiness.csv`: readiness check for promoting the preview sign rule.
- `evidence/source_split_k2_scoring_authorization.csv`: final source-split K2 scoring authorization output.
- `evidence/source_split_k2_null_scorecard.csv`: source-split K2/null preflight scorecard.
- `evidence/source_split_k2_null_scorecard_summary.csv`: summary of the source-split scorecard.
- `evidence/source_split_k1_degeneracy_audit.csv`: row-level zero-K1 degeneracy audit.
- `evidence/source_split_k1_degeneracy_summary.csv`: summary of the K1 degeneracy audit.
- `evidence/source_split_k1_response_requirements.csv`: requirements for a non-degenerate K1 response target.
- `evidence/source_split_k1_response_candidate_audit.csv`: row-level nonzero K1 candidate audit.
- `evidence/source_split_k1_response_candidate_summary.csv`: summary of K1 candidate provenance.
- `evidence/source_split_k1_candidate_sensitivity.csv`: sensitivity scores for K1 candidates and K2 responses.
- `evidence/source_split_k1_candidate_sensitivity_summary.csv`: summary of K1 candidate sensitivity.
- `evidence/source_split_k1_candidate_promotion_readiness.csv`: primary-K1 promotion readiness table.
- `evidence/source_split_k1_candidate_promotion_summary.csv`: summary of primary-K1 promotion status.
- `evidence/source_split_external_k1_export_schema.csv`: required external K1 export schema.
- `evidence/source_split_external_k1_export_template.csv`: row-aligned template for future external K1 exports.
- `evidence/source_split_external_k1_export_readiness.csv`: validation status for the future external K1 export.
- `evidence/source_split_external_k1_source_registry.csv`: registry of possible external K1 source routes.
- `evidence/source_split_external_k1_source_readiness.csv`: readiness status for external K1 source routes.
- `evidence/source_split_family_mean_k1_policy.csv`: candidate policies for a future reconstruction-family mean K1.
- `evidence/source_split_family_mean_k1_policy_readiness.csv`: readiness summary for family-mean K1 policies.
- `evidence/source_split_future_rerun_protocol.csv`: preregistered future rerun protocol options.
- `evidence/source_split_future_rerun_protocol_summary.csv`: summary of future rerun authorization status.
- `evidence/source_branch_baseline_response_export.csv`: diagnostic branch-baseline response export for source-realization audits.
- `evidence/source_branch_baseline_response_summary.csv`: summary of branch-baseline mismatch diagnostics.
- `evidence/source_realization_future_freeze_packet.csv`: future-only freeze checklist for source-realization promotion gates.
- `evidence/source_realization_future_freeze_summary.csv`: summary of source-realization future freeze status.
- `evidence/source_realization_rerun_readiness.csv`: aggregate source-realization rerun readiness gate.
- `evidence/source_realization_rerun_readiness_summary.csv`: summary of current source-realization rerun authorization.
- `evidence/source_realization_poly2_dominance_row_audit.csv`: row-level K2 versus POLY_DEG2 dominance audit.
- `evidence/source_realization_poly2_dominance_zone_summary.csv`: depth-zone summary for K2 versus POLY_DEG2 dominance.
- `evidence/source_realization_poly2_dominance_summary.csv`: summary of source-realization POLY_DEG2 dominance.
- `evidence/source_realization_poly2_role_adjudication.csv`: source-realization adjudication of POLY_DEG2's role.
- `evidence/source_realization_poly2_role_adjudication_summary.csv`: summary of POLY_DEG2 role adjudication.
- `evidence/source_realization_target_convention_absorber_audit.csv`: target-convention absorber audit for source-realization POLY_DEG2 dominance.
- `evidence/source_realization_target_convention_absorber_summary.csv`: summary of target-convention absorber status.
- `evidence/source_realization_baseline_drift_absorber_audit.csv`: row-level baseline-drift absorber audit for source-realization POLY_DEG2 dominance.
- `evidence/source_realization_baseline_drift_absorber_summary.csv`: summary of baseline-drift absorber status.
- `evidence/source_realization_poly2_penalty_audit.csv`: AIC/BIC-style penalty check for K2 versus POLY_DEG2.
- `evidence/source_realization_oos_zone_audit.csv`: leave-one-out and zone-holdout source-realization control audit.
- `evidence/source_realization_baseline_drift_null_scorecard.csv`: explicit baseline-drift null scorecard.
- `evidence/source_realization_k2_survival_scorecard.csv`: consolidated source-realization K2 survival gate table.
- `evidence/source_realization_k2_survival_summary.csv`: summary of current K2 survival status under source-realization controls.
- `evidence/source_realization_morphological_rule_tuning_audit.csv`: row-level Tau Core morphology classifier tuning audit.
- `evidence/source_realization_morphological_rule_tuning_summary.csv`: summary of morphology classifier fit and sector counts.
- `data/k1/source_split_external_k1_response.csv`: future-only equal-weight family-mean K1 export.
- `evidence/source_split_family_mean_k1_future_export_summary.csv`: summary of the future-only K1 export.
- `evidence/source_split_future_k1_k2_dry_run.csv`: future-only K1/K2 dry-run score table.
- `evidence/source_split_future_k1_k2_dry_run_summary.csv`: summary of the future-only dry run.
- `evidence/source_split_likelihood_native_k1_plan.csv`: artifact checklist for likelihood-native K1.
- `evidence/source_split_likelihood_native_k1_readiness.csv`: readiness status for likelihood-native K1.
- `evidence/source_split_candidate_export_handoff_manifest.csv`: step-by-step handoff for the candidate export.
- `evidence/source_split_candidate_export_handoff_summary.csv`: summary of the candidate export handoff.
- `evidence/source_split_candidate_path_guard.csv`: guard output for the real candidate-export path.
- `evidence/source_split_blocker_matrix.csv`: consolidated source-split blocker matrix.
- `evidence/source_split_blocker_matrix_summary.csv`: summary of the blocker matrix.
- `evidence/source_split_sn_branch_export_handoff.csv`: row-level SN residual branch export handoff.
- `evidence/source_split_sn_branch_export_handoff_summary.csv`: summary of the SN branch handoff.
- `evidence/source_split_bao_branch_export_handoff.csv`: row-level BAO residual branch export handoff.
- `evidence/source_split_bao_branch_export_handoff_summary.csv`: summary of the BAO branch handoff.
- `evidence/source_packet_manifest.csv`: source packet map.

## Run The Current Gate MVP

```text
python3 scripts/run_gate_current_packet.py
```

This regenerates `evidence/gate_results_current.csv` from the current
diagnostic packet. The score is a diagonal covariance proxy, not a full
covariance likelihood.

```text
python3 scripts/run_coordinate_robustness.py
```

This regenerates `evidence/coordinate_robustness_results.csv` without refitting
the frozen K1 baseline.

## Regenerate The PDF

```text
python3 -m pip install -r requirements.txt
python3 make_pdf.py
```

## Scope Boundary

This paper is self-contained as a bounded diagnostic proposal. It does not
require or establish any broader background theory.
