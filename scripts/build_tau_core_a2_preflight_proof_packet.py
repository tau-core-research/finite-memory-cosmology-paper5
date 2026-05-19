#!/usr/bin/env python3
"""Build the Tau Core A2 preflight proof packet.

This packet aggregates the existing locked-A2 evidence into one auditable
summary. It does not introduce a new claim, tune a parameter, or authorize
measurement validation.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

FILES = {
    "prediction_lock": EVIDENCE / "k2_a2_prediction_lock_readiness.csv",
    "preflight_gate": EVIDENCE / "k2_a2_preflight_scoring_gate_summary.csv",
    "full_gate": EVIDENCE / "k2_a2_full_likelihood_gate_readiness.csv",
    "memory_claim": EVIDENCE / "k2_a2_memory_active_claim_summary.csv",
    "depth_activation": EVIDENCE / "tau_core_depth_activation_summary.csv",
    "source_geometry": EVIDENCE / "tau_core_source_split_geometry_summary.csv",
    "a2_amplitude": EVIDENCE / "tau_core_a2_amplitude_specificity_summary.csv",
    "memory_score": EVIDENCE / "k2_a2_memory_active_scorecard_summary.csv",
    "cross_covariance": EVIDENCE / "k2_a2_memory_active_cross_covariance_summary.csv",
    "transform_variants": EVIDENCE / "k2_a2_transform_variant_robustness_summary.csv",
    "randomization": EVIDENCE / "k2_a2_memory_active_randomization_summary.csv",
    "polynomial_tension": EVIDENCE / "k2_a2_polynomial_tension_diagnosis.csv",
    "target_regime_polynomial": EVIDENCE / "tau_core_target_regime_polynomial_summary.csv",
    "physical_null_preflight": EVIDENCE / "tau_core_physical_null_preflight_summary.csv",
    "alpha_residual": EVIDENCE / "tau_core_alpha_residual_summary.csv",
    "target_regime_stress": EVIDENCE / "tau_core_target_regime_stress_summary.csv",
    "support_ladder": EVIDENCE / "source_split_likelihood_native_support_ladder_summary.csv",
    "route_decision": EVIDENCE / "tau_core_a2_route_decision_summary.csv",
    "branch_scatter_registration": EVIDENCE / "branch_scatter_systematic_registration_summary.csv",
    "branch_scatter_calibration": EVIDENCE / "branch_scatter_independent_calibration_summary.csv",
    "full_public_covariance": EVIDENCE / "full_public_covariance_transform_summary.csv",
    "joint_covariance_adjudication": EVIDENCE / "joint_covariance_adjudication_summary.csv",
    "input_object_audit": EVIDENCE / "likelihood_native_input_object_summary.csv",
    "residual_definition_contract": EVIDENCE / "likelihood_native_residual_definition_readiness.csv",
    "full_likelihood_native_contract": EVIDENCE / "full_likelihood_native_joint_transform_readiness.csv",
    "rerun_candidate": EVIDENCE / "likelihood_native_rerun_candidate_summary.csv",
    "rerun_weakening": EVIDENCE / "likelihood_native_rerun_weakening_summary.csv",
    "rerun_tension_axes": EVIDENCE / "public_covariance_rerun_tension_axes_summary.csv",
    "rerun_target_construction": EVIDENCE / "public_rerun_target_construction_summary.csv",
    "rerun_branch_contribution": EVIDENCE / "public_rerun_branch_contribution_summary.csv",
    "rerun_target_variants": EVIDENCE / "public_rerun_target_variant_summary.csv",
    "a2_projection_gated_candidate": EVIDENCE / "a2_projection_gated_candidate_summary.csv",
    "a2_projection_gated_v3_candidate": EVIDENCE / "a2_projection_gated_v3_candidate_summary.csv",
    "a2_v3_stress": EVIDENCE / "a2_v3_stress_test_summary.csv",
    "a2_v3_polynomial_cv": EVIDENCE / "a2_v3_polynomial_cv_summary.csv",
    "a2_v3_residual_mechanism": EVIDENCE / "a2_v3_residual_mechanism_summary.csv",
    "a2_common_mode_baseline": EVIDENCE / "a2_common_mode_baseline_summary.csv",
    "a2_k1_null_degeneracy": EVIDENCE / "a2_k1_null_degeneracy_summary.csv",
    "a2_active_memory_overshoot": EVIDENCE / "a2_active_memory_overshoot_summary.csv",
    "a2_source_branch_normalization": EVIDENCE / "a2_source_branch_normalization_summary.csv",
    "a2_cross_covariance_policy": EVIDENCE / "a2_cross_covariance_policy_summary.csv",
    "measurement_route_closure": EVIDENCE / "measurement_route_closure_summary.csv",
    "full_gate_plan": EVIDENCE / "full_gate_implementation_summary.csv",
    "public_covariance_replacement_plan": EVIDENCE / "a2_public_covariance_replacement_summary.csv",
    "target_convention_adjudication": EVIDENCE / "public_target_convention_adjudication_summary.csv",
    "whitened_standardized_branch_contrast": EVIDENCE / "whitened_standardized_branch_contrast_summary.csv",
    "registered_shrinkage_whitened": EVIDENCE / "registered_shrinkage_whitened_branch_contrast_summary.csv",
    "whitened_covariance_route_comparison": EVIDENCE / "whitened_covariance_route_comparison_summary.csv",
    "weighted_polynomial_dominance": EVIDENCE / "weighted_polynomial_dominance_summary.csv",
    "whitened_physical_null_benchmark": EVIDENCE / "whitened_physical_null_benchmark_summary.csv",
    "external_calibration_sources": EVIDENCE / "external_physical_null_calibration_source_summary.csv",
    "whitened_alpha_calibrated": EVIDENCE / "whitened_alpha_calibrated_preflight_summary.csv",
    "backreaction_source_availability": EVIDENCE / "backreaction_numeric_source_availability_summary.csv",
    "backreaction_reproduction_contract": EVIDENCE / "backreaction_reproduction_readiness.csv",
    "backreaction_formula_engine": EVIDENCE / "backreaction_formula_engine_readiness.csv",
    "backreaction_provisional_bao": EVIDENCE / "backreaction_provisional_bao_reconstruction_summary.csv",
    "backreaction_provisional_comparison": EVIDENCE / "provisional_backreaction_preflight_summary.csv",
    "backreaction_bridge_diagnosis": EVIDENCE / "provisional_backreaction_bridge_diagnosis_summary.csv",
    "backreaction_k2_component_split": EVIDENCE / "backreaction_k2_component_split_summary.csv",
    "k2_residual_after_backreaction": EVIDENCE / "k2_residual_after_backreaction_summary.csv",
    "backreaction_bridge_variant_stability": EVIDENCE / "backreaction_bridge_variant_stability_summary.csv",
    "backreaction_depth_stability": EVIDENCE / "backreaction_depth_stability_summary.csv",
    "source_native_backreaction_upgrade": EVIDENCE / "source_native_backreaction_upgrade_summary.csv",
    "source_native_public_inputs": EVIDENCE / "source_native_public_input_validation_summary.csv",
    "source_native_runtime": EVIDENCE / "source_native_runtime_validation_summary.csv",
    "symbolic_regression_online_sources": EVIDENCE / "symbolic_regression_online_source_probe_summary.csv",
    "source_native_templates": EVIDENCE / "source_native_backreaction_template_summary.csv",
    "source_native_export_validation": EVIDENCE / "source_native_backreaction_export_validation_summary.csv",
    "source_native_uncertainty_validation": EVIDENCE / "source_native_backreaction_uncertainty_validation_summary.csv",
    "source_native_backreaction_bridge": EVIDENCE / "source_native_backreaction_bridge_summary.csv",
    "source_native_fixture_smoke": EVIDENCE / "source_native_backreaction_fixture_smoke_summary.csv",
    "source_native_uncertainty_fixture_smoke": EVIDENCE / "source_native_uncertainty_fixture_smoke_summary.csv",
    "source_native_training_datasets": EVIDENCE / "source_native_training_dataset_summary.csv",
    "source_native_derivative_pilot": EVIDENCE / "source_native_derivative_pilot_summary.csv",
    "source_native_derivative_pilot_uncertainty": EVIDENCE / "source_native_derivative_pilot_uncertainty_summary.csv",
    "source_native_derivative_pilot_bridge": EVIDENCE / "source_native_derivative_pilot_bridge_comparison_summary.csv",
    "derivative_pilot_k2_component_split": EVIDENCE / "derivative_pilot_k2_component_split_summary.csv",
    "derivative_pilot_component_uncertainty": EVIDENCE / "derivative_pilot_component_uncertainty_summary.csv",
    "derivative_pilot_noise_source": EVIDENCE / "derivative_pilot_noise_source_summary.csv",
    "derivative_pilot_degree_sensitivity": EVIDENCE / "derivative_pilot_degree_sensitivity_summary.csv",
    "midhigh_component_stability": EVIDENCE / "midhigh_component_stability_summary.csv",
    "low_depth_tau_core_support": EVIDENCE / "low_depth_tau_core_support_summary.csv",
    "tau_core_a2_claim_ladder": EVIDENCE / "tau_core_a2_claim_ladder_summary.csv",
    "source_native_surrogate_family_export": EVIDENCE / "source_native_surrogate_family_export_summary.csv",
    "source_native_surrogate_bridge": EVIDENCE / "source_native_surrogate_bridge_summary.csv",
    "source_native_surrogate_bridge_shape": EVIDENCE / "source_native_surrogate_bridge_shape_summary.csv",
    "source_native_surrogate_family_rank": EVIDENCE / "source_native_surrogate_family_rank_summary.csv",
    "source_native_backreaction_decision_rules": EVIDENCE / "source_native_backreaction_decision_rules_summary.csv",
    "source_native_backreaction_decision_dry_run": EVIDENCE / "source_native_backreaction_decision_dry_run_summary.csv",
    "source_native_symbolic_protocol": EVIDENCE / "source_native_symbolic_protocol_extract_summary.csv",
    "pysr_criteria3_contract": EVIDENCE / "pysr_criteria3_reproduction_readiness.csv",
    "pysr_criteria3_smoke": EVIDENCE / "pysr_criteria3_smoke_summary.csv",
    "pysr_criteria3_structured_smoke": EVIDENCE / "pysr_criteria3_structured_smoke_summary.csv",
    "pysr_penalty_normalization": EVIDENCE / "pysr_penalty_normalization_summary.csv",
    "source_native_normalized_criteria3_selector": EVIDENCE / "source_native_normalized_criteria3_selector_summary.csv",
    "source_native_normalized_criteria3_bootstrap_smoke": EVIDENCE / "source_native_normalized_criteria3_bootstrap_smoke_summary.csv",
    "normalized_pysr_backreaction_smoke": EVIDENCE / "normalized_pysr_backreaction_smoke_summary.csv",
    "source_native_normalized_criteria3_d_branch_smoke": EVIDENCE / "source_native_normalized_criteria3_d_branch_bootstrap_smoke_summary.csv",
    "full_normalized_pysr_backreaction_smoke": EVIDENCE / "full_normalized_pysr_backreaction_smoke_summary.csv",
    "full_normalized_pysr_backreaction_sensitivity": EVIDENCE / "full_normalized_pysr_backreaction_sensitivity_summary.csv",
    "d_branch_derivative_regularized_selector": EVIDENCE / "d_branch_derivative_regularized_selector_summary.csv",
    "d_branch_derivative_regularized_smoke": EVIDENCE / "d_branch_derivative_regularized_bootstrap_smoke_summary.csv",
    "d_branch_derivative_regularized_bootstrap_200": EVIDENCE / "d_branch_derivative_regularized_bootstrap_200_summary.csv",
    "h_branch_normalized_criteria3_bootstrap_200": EVIDENCE / "h_branch_normalized_criteria3_bootstrap_200_summary.csv",
    "regularized_full_pysr_backreaction_smoke": EVIDENCE / "regularized_full_pysr_backreaction_smoke_summary.csv",
    "regularized_full_pysr_backreaction_sensitivity": EVIDENCE / "regularized_full_pysr_backreaction_sensitivity_summary.csv",
    "regularized_vs_unregularized_decision": EVIDENCE / "regularized_vs_unregularized_decision_summary.csv",
    "regularized_full_pysr_backreaction_200": EVIDENCE / "regularized_full_pysr_backreaction_200_summary.csv",
    "regularized_full_pysr_backreaction_200_sensitivity": EVIDENCE / "regularized_full_pysr_backreaction_200_sensitivity_summary.csv",
    "regularized_200_null_dominance": EVIDENCE / "regularized_200_null_dominance_summary.csv",
    "source_native_after_200_blocker": EVIDENCE / "source_native_after_200_blocker_summary.csv",
    "source_native_schema_dry_run": EVIDENCE / "source_native_schema_dry_run_summary.csv",
    "source_native_reproduction_candidate": EVIDENCE / "source_native_reproduction_candidate_summary.csv",
    "source_native_reproduction_candidate_bridge": EVIDENCE
    / "source_native_reproduction_candidate_bridge_summary.csv",
    "source_native_reproduction_candidate_dominance": EVIDENCE
    / "source_native_reproduction_candidate_dominance_summary.csv",
    "source_native_reproduction_family": EVIDENCE / "source_native_reproduction_family_export_summary.csv",
    "source_native_reproduction_family_bridge": EVIDENCE
    / "source_native_reproduction_family_bridge_summary.csv",
    "source_native_reproduction_family_dominance": EVIDENCE
    / "source_native_reproduction_family_dominance_summary.csv",
    "author_protocol_guided_reproduction": EVIDENCE / "author_protocol_guided_reproduction_summary.csv",
    "author_protocol_guided_bridge": EVIDENCE / "author_protocol_guided_bridge_summary.csv",
    "author_protocol_guided_dominance": EVIDENCE / "author_protocol_guided_dominance_summary.csv",
    "backreaction_route_adjudication": EVIDENCE / "backreaction_route_adjudication_summary.csv",
    "source_native_reproduction_tasks": EVIDENCE / "source_native_reproduction_task_readiness.csv",
}

OUT_PACKET = EVIDENCE / "tau_core_a2_preflight_proof_packet.csv"
OUT_SUMMARY = EVIDENCE / "tau_core_a2_preflight_proof_packet_summary.csv"
OUT_DOC = DOCS / "tau_core_a2_preflight_proof_packet.md"


def truthy(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def read_first(path: Path) -> pd.Series:
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_csv(path)
    if df.empty:
        raise ValueError(f"empty evidence file: {path}")
    return df.iloc[0]


def prediction_lock_passed(path: Path) -> bool:
    """Return True when the row-oriented lock audit has no failing checks."""
    df = pd.read_csv(path)
    if df.empty:
        return False
    if {"CheckID", "Status"}.issubset(df.columns):
        overall = df[df["CheckID"].astype(str).str.lower().eq("overall_lock_status")]
        if not overall.empty:
            return bool(overall["Status"].astype(str).str.upper().eq("PASS").all())
        return bool(df["Status"].astype(str).str.upper().eq("PASS").all())
    return bool(truthy(df.iloc[0].get("OverallLockStatus", df.iloc[0].get("overall_lock_status", False))))


def add(rows: list[dict[str, object]], gate_id: str, evidence_file: str, status: str, finding: str, role: str) -> None:
    rows.append(
        {
            "PacketID": "TAU_CORE_A2_PREFLIGHT_PROOF_PACKET_V1",
            "GateID": gate_id,
            "EvidenceFile": evidence_file,
            "Status": status,
            "Finding": finding,
            "RoleInProofChain": role,
            "ClaimBoundary": "tau_core_a2_preflight_packet_no_measurement_validation",
        }
    )


def build_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []

    add(
        rows,
        "LOCKED_A2_PREDICTION",
        str(FILES["prediction_lock"].relative_to(ROOT)),
        "PASS" if prediction_lock_passed(FILES["prediction_lock"]) else "CHECK",
        "Locked A2 prediction exists with p=3, rho=4, A_tau=2; no rho>4 or K1 refit is authorized.",
        "claim_integrity",
    )

    preflight = read_first(FILES["preflight_gate"])
    add(
        rows,
        "PREFLIGHT_SCORING_GATE",
        str(FILES["preflight_gate"].relative_to(ROOT)),
        "PASS" if truthy(preflight["PreflightScorecardAllowed"]) and not truthy(preflight["MeasurementValidationAllowed"]) else "BLOCKED",
        f"Preflight scorecard allowed={preflight['PreflightScorecardAllowed']}; measurement validation allowed={preflight['MeasurementValidationAllowed']}.",
        "execution_boundary",
    )

    full_gate = pd.read_csv(FILES["full_gate"])
    overall = full_gate[full_gate["GateClass"].eq("overall")].iloc[0]
    blockers = full_gate[(full_gate["GateClass"].eq("required")) & (full_gate["Status"].eq("BLOCKED"))]
    add(
        rows,
        "FULL_MEASUREMENT_GATE",
        str(FILES["full_gate"].relative_to(ROOT)),
        str(overall["Status"]),
        f"{overall['Observed']}; blockers={';'.join(blockers['GateID'].astype(str))}",
        "measurement_boundary",
    )

    memory_claim = read_first(FILES["memory_claim"])
    add(
        rows,
        "MEMORY_ACTIVE_CLAIM_BOUNDARY",
        str(FILES["memory_claim"].relative_to(ROOT)),
        "PASS" if truthy(memory_claim["MemoryActivePreflightClaimAllowed"]) else "BLOCKED",
        str(memory_claim["RecommendedPaperLanguage"]),
        "claim_boundary",
    )

    depth = read_first(FILES["depth_activation"])
    add(
        rows,
        "DEPTH_ACTIVATION",
        str(FILES["depth_activation"].relative_to(ROOT)),
        "PASS" if truthy(depth["DepthActivationPatternSupported"]) else "BLOCKED",
        f"Depth activation checks={depth['PassedChecks']}/{depth['Checks']}; {depth['CurrentInterpretation']}",
        "tau_core_signature",
    )

    geometry = read_first(FILES["source_geometry"])
    add(
        rows,
        "SOURCE_SPLIT_GEOMETRY",
        str(FILES["source_geometry"].relative_to(ROOT)),
        "PASS" if truthy(geometry["GeometrySupportsATau2Preflight"]) else "BLOCKED",
        f"Geometry checks={geometry['PassedChecks']}/{geometry['Checks']}; {geometry['CurrentInterpretation']}",
        "tau_core_signature",
    )

    amp = read_first(FILES["a2_amplitude"])
    add(
        rows,
        "A_TAU_2_AMPLITUDE_SPECIFICITY",
        str(FILES["a2_amplitude"].relative_to(ROOT)),
        "PASS",
        (
            f"Memory-subset A_opt median={amp['PublicProxyMedianAOptMemorySubsets']}; "
            f"range={amp['PublicProxyMinAOptMemorySubsets']}..{amp['PublicProxyMaxAOptMemorySubsets']}; "
            f"within A2 half-band={amp['PublicProxyMemorySubsetsWithinA2HalfBand']}/{amp['PublicProxyMemorySubsetCount']}."
        ),
        "amplitude_specificity",
    )

    score = pd.read_csv(FILES["memory_score"])
    mid_high = score[score["SubsetID"].eq("mid_high_memory_active")].iloc[0]
    add(
        rows,
        "MEMORY_ACTIVE_SCORECARD",
        str(FILES["memory_score"].relative_to(ROOT)),
        "PASS"
        if truthy(mid_high["A2ImprovesOverK1"])
        and truthy(mid_high["A2ImprovesOverUnitK2"])
        and truthy(mid_high["A2BeatsBestPoly"])
        else "BLOCKED",
        (
            f"mid/high DeltaAIC A2-K1={mid_high['DeltaAIC_A2_minus_K1']}; "
            f"A2-unit={mid_high['DeltaAIC_A2_minus_UnitK2']}; "
            f"A2-poly={mid_high['DeltaAIC_A2_minus_BestPoly']}."
        ),
        "control_comparison",
    )

    cross = pd.read_csv(FILES["cross_covariance"])
    cross_mid = cross[cross["SubsetID"].eq("mid_high_memory_active")]
    add(
        rows,
        "CROSS_COVARIANCE_ROBUSTNESS",
        str(FILES["cross_covariance"].relative_to(ROOT)),
        "PASS" if int(cross_mid["A2BeatsBestPoly"].map(truthy).sum()) == len(cross_mid) else "MIXED",
        f"mid/high A2 beats best polynomial {int(cross_mid['A2BeatsBestPoly'].map(truthy).sum())}/{len(cross_mid)} rho_cross values.",
        "robustness",
    )

    variants = pd.read_csv(FILES["transform_variants"])
    var_mid = variants[variants["SubsetID"].eq("mid_high_memory_active")]
    add(
        rows,
        "TRANSFORM_VARIANT_ROBUSTNESS",
        str(FILES["transform_variants"].relative_to(ROOT)),
        "PASS" if int(var_mid["A2BeatsBestPoly"].map(truthy).sum()) == len(var_mid) else "MIXED",
        f"mid/high A2 beats best polynomial {int(var_mid['A2BeatsBestPoly'].map(truthy).sum())}/{len(var_mid)} transform variants.",
        "robustness",
    )

    random = pd.read_csv(FILES["randomization"])
    random_mid = random[random["SubsetID"].eq("mid_high_memory_active")]
    add(
        rows,
        "RANDOMIZATION_CONTROLS",
        str(FILES["randomization"].relative_to(ROOT)),
        "PASS"
        if int(random_mid["ObservedBeatsControlMedianCount"].sum()) == int(random_mid["TransformVariants"].sum())
        else "MIXED",
        (
            f"mid/high observed beats randomized medians="
            f"{int(random_mid['ObservedBeatsControlMedianCount'].sum())}/"
            f"{int(random_mid['TransformVariants'].sum())}; "
            f"median p={random_mid['MedianEmpiricalP_ControlLEObserved'].min()}.."
            f"{random_mid['MedianEmpiricalP_ControlLEObserved'].max()}."
        ),
        "negative_control",
    )

    target_poly = read_first(FILES["target_regime_polynomial"])
    add(
        rows,
        "TARGET_REGIME_POLYNOMIAL_AUDIT",
        str(FILES["target_regime_polynomial"].relative_to(ROOT)),
        "PASS" if truthy(target_poly["MemoryActivePolynomialCheckPassed"]) and truthy(target_poly["AllDepthPolynomialWarningRetained"]) else "WARNING",
        (
            f"{target_poly['StrongestAllowedClaim']}; "
            f"status={target_poly['CurrentStatus']}; measurement validation allowed={target_poly['MeasurementValidationAllowed']}."
        ),
        "target_regime_control_boundary",
    )

    physical_null = read_first(FILES["physical_null_preflight"])
    add(
        rows,
        "PHYSICAL_NULL_PREFLIGHT_LAYER",
        str(FILES["physical_null_preflight"].relative_to(ROOT)),
        "PASS" if truthy(physical_null["K2BeatsBestPhysicalNullProxy"]) and truthy(physical_null["K2ImprovesOverK1Context"]) else "WARNING",
        (
            f"{physical_null['StrongestAllowedClaim']}; "
            f"status={physical_null['CurrentStatus']}; residual risk={physical_null['PrimaryResidualRisk']}."
        ),
        "physical_null_control_boundary",
    )

    alpha_residual = read_first(FILES["alpha_residual"])
    add(
        rows,
        "OPTICAL_ALPHA_RESIDUAL_AUDIT",
        str(FILES["alpha_residual"].relative_to(ROOT)),
        "PASS" if truthy(alpha_residual["AlphaSubtractionDoesNotRemoveK2Structure"]) else "WARNING",
        (
            f"{alpha_residual['StrongestAllowedClaim']}; "
            f"status={alpha_residual['CurrentStatus']}; residual risk={alpha_residual['PrimaryResidualRisk']}."
        ),
        "physical_null_residual_boundary",
    )

    target_stress = read_first(FILES["target_regime_stress"])
    add(
        rows,
        "TARGET_REGIME_STRESS_AUDIT",
        str(FILES["target_regime_stress"].relative_to(ROOT)),
        "PASS"
        if str(target_stress["CurrentStatus"]) == "LOCKED_A2_TARGET_REGIME_STRESS_SURVIVED_PREFLIGHT"
        and int(target_stress["WarningCriteria"]) == 0
        and not truthy(target_stress["MeasurementValidationAllowed"])
        else "WARNING",
        (
            f"{target_stress['StrongestAllowedClaim']}; "
            f"leave-one-out fraction={target_stress['LeaveOneOutA2WinsFraction']}; "
            f"rebinning={target_stress['RebinningSchemesA2Best']}/{target_stress['RebinningSchemesTotal']}; "
            f"transform variants={target_stress['TransformVariantsA2BeatsPoly']}/{target_stress['TransformVariantsTotal']}; "
            f"randomization controls={target_stress['RandomizationControlsObservedBeatsMedian']}/{target_stress['RandomizationControlsTotal']}."
        ),
        "target_regime_stress_backbone",
    )

    support_ladder = read_first(FILES["support_ladder"])
    add(
        rows,
        "LIKELIHOOD_NATIVE_SUPPORT_LADDER",
        str(FILES["support_ladder"].relative_to(ROOT)),
        "PASS"
        if str(support_ladder["CurrentStrongestStatus"]) == "DECLARED_PREFLIGHT_SUPPORT"
        and str(support_ladder["MeasurementValidationStatus"]) == "BLOCKED"
        else "WARNING",
        (
            f"strongest status={support_ladder['CurrentStrongestStatus']}; "
            f"K2-vs-K1={support_ladder['K2VsK1Status']}; "
            f"K2-vs-polynomial={support_ladder['K2VsPolynomialStatus']}; "
            f"public covariance={support_ladder['PublicCovarianceStatus']}; "
            f"measurement validation={support_ladder['MeasurementValidationStatus']}."
        ),
        "likelihood_native_scorecard_rerun",
    )

    route_decision = read_first(FILES["route_decision"])
    add(
        rows,
        "A2_ROUTE_DECISION_MATRIX",
        str(FILES["route_decision"].relative_to(ROOT)),
        "PASS"
        if str(route_decision["RecommendedNextRoute"]) == "R3_BRANCH_SCATTER_SYSTEMATIC"
        and not truthy(route_decision["MeasurementValidationAllowed"])
        else "WARNING",
        (
            f"recommended route={route_decision['RecommendedNextRoute']}; "
            f"public covariance={route_decision['PublicCovarianceStatus']}; "
            f"registered shrinkage={route_decision['RegisteredShrinkageStatus']}; "
            f"branch scatter={route_decision['BranchScatterStatus']}; "
            f"measurement validation allowed={route_decision['MeasurementValidationAllowed']}."
        ),
        "route_selection_boundary",
    )

    branch_registration = read_first(FILES["branch_scatter_registration"])
    add(
        rows,
        "BRANCH_SCATTER_SYSTEMATIC_REGISTRATION",
        str(FILES["branch_scatter_registration"].relative_to(ROOT)),
        "PASS"
        if truthy(branch_registration["PreflightRouteRegistered"])
        and not truthy(branch_registration["MeasurementValidationAllowed"])
        and int(branch_registration["BlockedChecks"]) == 0
        else "WARNING",
        (
            f"{branch_registration['StrongestAllowedClaim']}; "
            f"status={branch_registration['CurrentStatus']}; "
            f"warnings={branch_registration['WarningChecks']}; "
            f"measurement blockers={branch_registration['MeasurementBlockingChecks']}."
        ),
        "registered_preflight_bridge",
    )

    branch_calibration = read_first(FILES["branch_scatter_calibration"])
    add(
        rows,
        "BRANCH_SCATTER_INDEPENDENT_CALIBRATION",
        str(FILES["branch_scatter_calibration"].relative_to(ROOT)),
        "PASS"
        if truthy(branch_calibration["IndependentCalibrationPreflightSupported"])
        and not truthy(branch_calibration["MeasurementValidationAllowed"])
        and int(branch_calibration["BlockedCriteria"]) == 0
        else "WARNING",
        (
            f"{branch_calibration['StrongestAllowedClaim']}; "
            f"reconstruction-family subsets={branch_calibration['ReconstructionFamilySubsetPasses']}/"
            f"{branch_calibration['ReconstructionFamilySubsetTotal']}; "
            f"branch-scatter K2-best={branch_calibration['BranchScatterK2BestCases']}/"
            f"{branch_calibration['BranchScatterCases']}; "
            f"measurement validation allowed={branch_calibration['MeasurementValidationAllowed']}."
        ),
        "independent_preflight_calibration",
    )

    public_covariance = read_first(FILES["full_public_covariance"])
    add(
        rows,
        "FULL_PUBLIC_COVARIANCE_TRANSFORM_AUDIT",
        str(FILES["full_public_covariance"].relative_to(ROOT)),
        "WARNING"
        if not truthy(public_covariance["FullPublicCovarianceTransformReady"])
        and not truthy(public_covariance["MeasurementValidationAllowed"])
        else "PASS",
        (
            f"{public_covariance['StrongestAllowedClaim']}; "
            f"raw SN covariance={public_covariance['RawPublicSNCovarianceAvailable']}; "
            f"raw BAO covariance={public_covariance['RawPublicBAOCovarianceAvailable']}; "
            f"zero-cross usable={public_covariance['ZeroCrossCovariancePreflightUsable']}; "
            f"K2 beats polynomial={public_covariance['K2BeatsBestPolyUnderPublicProxy']}."
        ),
        "measurement_route_blocker",
    )

    joint_adjudication = read_first(FILES["joint_covariance_adjudication"])
    add(
        rows,
        "JOINT_COVARIANCE_ADJUDICATION",
        str(FILES["joint_covariance_adjudication"].relative_to(ROOT)),
        "WARNING"
        if str(joint_adjudication["CurrentStatus"]) == "FG4_EXECUTABLE_PREFLIGHT_MEASUREMENT_BLOCKED"
        and not truthy(joint_adjudication["MeasurementValidationAllowed"])
        else "BLOCKED",
        (
            f"{joint_adjudication['StrongestAllowedClaim']}; "
            f"public routes K2>K1={joint_adjudication['PublicRoutesK2OverK1']}/"
            f"{joint_adjudication['PublicRoutes']}; "
            f"public routes K2>poly={joint_adjudication['PublicRoutesK2OverPolynomial']}/"
            f"{joint_adjudication['PublicRoutes']}; "
            f"primary blocker={joint_adjudication['PrimaryBlocker']}."
        ),
        "joint_covariance_route_boundary",
    )

    input_audit = read_first(FILES["input_object_audit"])
    add(
        rows,
        "LIKELIHOOD_NATIVE_INPUT_OBJECT_AUDIT",
        str(FILES["input_object_audit"].relative_to(ROOT)),
        "PASS"
        if int(input_audit["PreflightUsableObjects"]) == int(input_audit["Objects"])
        and not truthy(input_audit["MeasurementValidationAllowed"])
        else "WARNING",
        (
            f"{input_audit['StrongestAllowedClaim']}; "
            f"preflight usable objects={input_audit['PreflightUsableObjects']}/"
            f"{input_audit['Objects']}; "
            f"measurement usable objects={input_audit['MeasurementUsableObjects']}/"
            f"{input_audit['Objects']}; primary blocker={input_audit['PrimaryBlocker']}."
        ),
        "public_input_availability_boundary",
    )

    residual_contract = read_first(FILES["residual_definition_contract"])
    add(
        rows,
        "LIKELIHOOD_NATIVE_RESIDUAL_DEFINITION_CONTRACT",
        str(FILES["residual_definition_contract"].relative_to(ROOT)),
        "WARNING"
        if str(residual_contract["CurrentStatus"])
        in {
            "RESIDUAL_DEFINITIONS_CONTRACTED_MEASUREMENT_BLOCKED",
            "RESIDUAL_DEFINITIONS_RESOLVED_FOR_RERUN_MEASUREMENT_BLOCKED",
        }
        and not truthy(residual_contract["MeasurementValidationAllowed"])
        else "BLOCKED",
        (
            f"{residual_contract['StrongestAllowedClaim']}; "
            f"measurement-ready residual contracts={residual_contract['MeasurementReadyResidualContracts']}/"
            f"{residual_contract['ResidualContracts']}; "
            f"rerun-resolved contracts={residual_contract.get('ResolvedForRerunCandidateContracts', 0)}/"
            f"{residual_contract['ResidualContracts']}; "
            f"primary blocker={residual_contract['PrimaryBlocker']}."
        ),
        "residual_definition_measurement_boundary",
    )

    full_ln_contract = read_first(FILES["full_likelihood_native_contract"])
    add(
        rows,
        "FULL_LIKELIHOOD_NATIVE_JOINT_TRANSFORM_CONTRACT",
        str(FILES["full_likelihood_native_contract"].relative_to(ROOT)),
        "WARNING"
        if str(full_ln_contract["CurrentStatus"])
        in {
            "FULL_LIKELIHOOD_NATIVE_ROUTE_CONTRACTED_MEASUREMENT_BLOCKED",
            "FULL_LIKELIHOOD_NATIVE_RERUN_ROUTE_READY_MEASUREMENT_BLOCKED",
        }
        and not truthy(full_ln_contract["MeasurementValidationAllowed"])
        else "BLOCKED",
        (
            f"{full_ln_contract['StrongestAllowedClaim']}; "
            f"measurement satisfied={full_ln_contract['MeasurementSatisfied']}/"
            f"{full_ln_contract['Requirements']}; "
            f"blocking requirements={full_ln_contract['BlockingRequirements']}."
        ),
        "full_likelihood_native_measurement_contract",
    )

    rerun_candidate = read_first(FILES["rerun_candidate"])
    add(
        rows,
        "LIKELIHOOD_NATIVE_RERUN_CANDIDATE",
        str(FILES["rerun_candidate"].relative_to(ROOT)),
        "WARNING"
        if not truthy(rerun_candidate["MeasurementValidationAllowed"])
        else "BLOCKED",
        (
            f"{rerun_candidate['StrongestAllowedClaim']}; "
            f"status={rerun_candidate['CurrentStatus']}; "
            f"DeltaAIC K2-K1={rerun_candidate['DeltaAIC_K2_minus_K1']}; "
            f"DeltaAIC K2-poly={rerun_candidate['DeltaAIC_K2_minus_BestPoly']}; "
            f"K2>K1={rerun_candidate['K2ImprovesOverK1']}; "
            f"K2>poly={rerun_candidate['K2BeatsBestPoly']}."
        ),
        "locked_rerun_candidate_boundary",
    )

    rerun_weakening = read_first(FILES["rerun_weakening"])
    add(
        rows,
        "LIKELIHOOD_NATIVE_RERUN_WEAKENING_DIAGNOSTIC",
        str(FILES["rerun_weakening"].relative_to(ROOT)),
        "WARNING"
        if not truthy(rerun_weakening["MeasurementValidationAllowed"])
        else "BLOCKED",
        (
            f"{rerun_weakening['StrongestAllowedClaim']}; "
            f"status={rerun_weakening['CurrentStatus']}; "
            f"full-cov DeltaAIC K2-K1={rerun_weakening['FullCovDeltaAIC_K2MinusK1']}; "
            f"full-cov DeltaAIC K2-poly={rerun_weakening['FullCovDeltaAIC_K2MinusBestPoly']}; "
            f"diag DeltaChi2 K2-K1={rerun_weakening['DiagDeltaChi2K2MinusK1']}; "
            f"worst K1 grid={rerun_weakening['WorstK1GridIndex']}; "
            f"worst mechanism={rerun_weakening['WorstK1Mechanism']}."
        ),
        "locked_rerun_weakening_boundary",
    )

    tension_axes = read_first(FILES["rerun_tension_axes"])
    add(
        rows,
        "PUBLIC_COVARIANCE_RERUN_TENSION_AXES",
        str(FILES["rerun_tension_axes"].relative_to(ROOT)),
        "WARNING"
        if not truthy(tension_axes["MeasurementValidationAllowed"])
        else "BLOCKED",
        (
            f"{tension_axes['StrongestAllowedClaim']}; "
            f"status={tension_axes['CurrentStatus']}; "
            f"K2 sign-mismatch rows={tension_axes['K2SignMismatchRows']}; "
            f"K2 overshoot rows={tension_axes['K2OvershootRows']}; "
            f"median |local A_tau required|={tension_axes['MedianAbsLocalATauRequired']}; "
            f"best counterfactual K2 scale full-cov={tension_axes['BetaFullCovarianceBestK2Scale']}; "
            f"locked scale={tension_axes['LockedScale']}."
        ),
        "public_rerun_tension_axis_boundary",
    )

    target_construction = read_first(FILES["rerun_target_construction"])
    add(
        rows,
        "PUBLIC_RERUN_TARGET_CONSTRUCTION_AUDIT",
        str(FILES["rerun_target_construction"].relative_to(ROOT)),
        "WARNING"
        if not truthy(target_construction["MeasurementValidationAllowed"])
        else "BLOCKED",
        (
            f"{target_construction['StrongestAllowedClaim']}; "
            f"status={target_construction['CurrentStatus']}; "
            f"candidate/coordinate sign mismatches={target_construction['CandidateCoordinateSignMismatchRows']}; "
            f"candidate/K2 sign mismatches={target_construction['CandidateK2SignMismatchRows']}; "
            f"compressed rows={target_construction['CandidateScaleCompressedRows']}; "
            f"below locked K2 rows={target_construction['CandidateScaleBelowLockedK2Rows']}; "
            f"median |candidate/coordinate|={target_construction['MedianAbsCandidateOverAbsCoordinateTarget']}."
        ),
        "public_rerun_target_construction_boundary",
    )

    branch_contribution = read_first(FILES["rerun_branch_contribution"])
    add(
        rows,
        "PUBLIC_RERUN_BRANCH_CONTRIBUTION_AUDIT",
        str(FILES["rerun_branch_contribution"].relative_to(ROOT)),
        "WARNING"
        if not truthy(branch_contribution["MeasurementValidationAllowed"])
        else "BLOCKED",
        (
            f"{branch_contribution['StrongestAllowedClaim']}; "
            f"status={branch_contribution['CurrentStatus']}; "
            f"projected/standardized sign mismatch rows={branch_contribution['ProjectedVsStandardizedSignMismatchRows']}; "
            f"SN branch sign changed rows={branch_contribution['SNBranchSignChangedRows']}; "
            f"BAO branch sign changed rows={branch_contribution['BAOBranchSignChangedRows']}; "
            f"compressed rows={branch_contribution['RawProjectedTargetCompressedRows']}; "
            f"median |candidate/coordinate|={branch_contribution['MedianAbsCandidateOverAbsCoordinate']}."
        ),
        "public_rerun_branch_contribution_boundary",
    )

    target_variants = read_first(FILES["rerun_target_variants"])
    add(
        rows,
        "PUBLIC_RERUN_TARGET_VARIANT_DIAGNOSTIC",
        str(FILES["rerun_target_variants"].relative_to(ROOT)),
        "WARNING"
        if not truthy(target_variants["MeasurementValidationAllowed"])
        else "BLOCKED",
        (
            f"{target_variants['StrongestAllowedClaim']}; "
            f"status={target_variants['CurrentStatus']}; "
            f"current DeltaAIC K2-K1={target_variants['DeltaAIC_K2_minus_K1']}; "
            f"current DeltaAIC K2-poly={target_variants['DeltaAIC_K2_minus_BestPoly']}; "
            f"counterfactual variants K2>K1={target_variants['CounterfactualVariantsK2OverK1']}/"
            f"{target_variants['CounterfactualVariants']}; "
            f"counterfactual variants K2>poly={target_variants['CounterfactualVariantsK2OverPoly']}/"
            f"{target_variants['CounterfactualVariants']}."
        ),
        "public_rerun_target_variant_boundary",
    )

    a2_v2 = read_first(FILES["a2_projection_gated_candidate"])
    add(
        rows,
        "A2_PROJECTION_GATED_STRUCTURAL_REFINEMENT",
        str(FILES["a2_projection_gated_candidate"].relative_to(ROOT)),
        "WARNING"
        if not truthy(a2_v2["MeasurementValidationAllowed"])
        and not truthy(a2_v2["KernelChanged"])
        and not truthy(a2_v2["K1Refit"])
        and not truthy(a2_v2["TargetSignUsedForGate"])
        else "BLOCKED",
        (
            f"{a2_v2['StrongestAllowedClaim']}; "
            f"active memory rows={a2_v2['ActiveMemoryRows']}/{a2_v2['Rows']}; "
            f"DeltaAIC V2-V1={a2_v2['DeltaAIC_V2_minus_V1']}; "
            f"DeltaAIC V2-K1={a2_v2['DeltaAIC_V2_minus_K1']}; "
            f"DeltaAIC V2-poly={a2_v2['DeltaAIC_V2_minus_BestPoly']}; "
            f"status={a2_v2['CurrentStatus']}."
        ),
        "a2_structural_refinement_boundary",
    )

    a2_v3 = read_first(FILES["a2_projection_gated_v3_candidate"])
    add(
        rows,
        "A2_PROJECTION_GATED_V3_CANDIDATE",
        str(FILES["a2_projection_gated_v3_candidate"].relative_to(ROOT)),
        "WARNING"
        if not truthy(a2_v3["MeasurementValidationAllowed"])
        and not truthy(a2_v3["KernelChanged"])
        and not truthy(a2_v3["K1Refit"])
        and not truthy(a2_v3["TargetSignUsedForGate"])
        else "BLOCKED",
        (
            f"{a2_v3['StrongestAllowedClaim']}; "
            f"sign-unstable unit rows={a2_v3['SignUnstableUnitRows']}/{a2_v3['Rows']}; "
            f"DeltaAIC V3-V2={a2_v3['DeltaAIC_V3_minus_V2']}; "
            f"DeltaAIC V3-K1={a2_v3['DeltaAIC_V3_minus_K1']}; "
            f"DeltaAIC V3-poly={a2_v3['DeltaAIC_V3_minus_BestPoly']}; "
            f"status={a2_v3['CurrentStatus']}."
        ),
        "a2_structural_candidate_boundary",
    )

    v3_stress = read_first(FILES["a2_v3_stress"])
    add(
        rows,
        "A2_V3_STRESS_TEST",
        str(FILES["a2_v3_stress"].relative_to(ROOT)),
        "WARNING"
        if not truthy(v3_stress["MeasurementValidationAllowed"])
        else "BLOCKED",
        (
            f"{v3_stress['StrongestAllowedClaim']}; "
            f"all-row DeltaAIC V3-K1={v3_stress['AllRowsDeltaAIC_V3_minus_K1']}; "
            f"LOO V3>K1={v3_stress['LeaveOneOutV3BeatsK1']}/"
            f"{v3_stress['LeaveOneOutFolds']}; "
            f"LOO V3>V2={v3_stress['LeaveOneOutV3BeatsV2']}/"
            f"{v3_stress['LeaveOneOutFolds']}; "
            f"status={v3_stress['CurrentStatus']}."
        ),
        "a2_v3_stress_boundary",
    )

    v3_poly_cv = pd.read_csv(FILES["a2_v3_polynomial_cv"])
    cv_comp = v3_poly_cv[v3_poly_cv["ModelID"].eq("V3_CV_COMPARISON")]
    cv_findings = []
    for _, row in cv_comp.iterrows():
        cv_findings.append(
            f"{row['ValidationMode']}:V3>K1={row['V3ImprovesOverK1']},"
            f"V3>poly={row['V3BeatsBestPoly']},"
            f"dK1={row['DeltaChi2_V3_minus_K1']},"
            f"dPoly={row['DeltaChi2_V3_minus_BestPoly']}"
        )
    add(
        rows,
        "A2_V3_POLYNOMIAL_CROSS_VALIDATION",
        str(FILES["a2_v3_polynomial_cv"].relative_to(ROOT)),
        "PASS"
        if bool(cv_comp["V3BeatsBestPoly"].map(truthy).all())
        and not bool(cv_comp["MeasurementValidationAllowed"].map(truthy).any())
        else "WARNING",
        "Polynomial CV comparison: " + " | ".join(cv_findings),
        "polynomial_control_cv_boundary",
    )

    v3_mech = pd.read_csv(FILES["a2_v3_residual_mechanism"])
    v3_overview = v3_mech[v3_mech["SummaryID"].eq("A2_V3_RESIDUAL_MECHANISM_OVERVIEW")].iloc[0]
    worst_mechs = v3_mech[v3_mech["SummaryID"].eq("A2_V3_RESIDUAL_MECHANISM_WORST_ROWS")]
    worst_finding = "; ".join(
        f"{row['MechanismClass']}@grid{int(row['WorstGridIndex'])}:{row['RequiredNextCheck']}"
        for _, row in worst_mechs.head(3).iterrows()
    )
    add(
        rows,
        "A2_V3_RESIDUAL_MECHANISM_AUDIT",
        str(FILES["a2_v3_residual_mechanism"].relative_to(ROOT)),
        "WARNING"
        if not truthy(v3_overview["MeasurementValidationAllowed"])
        else "BLOCKED",
        (
            "A2 v3 residual mechanism audit separates the remaining K1 advantage "
            "from common-mode, K1-null, and active-memory scale effects; "
            f"diag DeltaChi2 V3-K1={v3_overview['DeltaChi2V3MinusK1']}; "
            f"status={v3_overview['CurrentStatus']}; "
            f"primary mechanisms={v3_overview['PrimaryResidualMechanisms']}; "
            f"next checks={worst_finding}."
        ),
        "a2_v3_residual_mechanism_boundary",
    )

    common_mode = read_first(FILES["a2_common_mode_baseline"])
    add(
        rows,
        "A2_COMMON_MODE_BASELINE_AUDIT",
        str(FILES["a2_common_mode_baseline"].relative_to(ROOT)),
        "WARNING"
        if not truthy(common_mode["MeasurementValidationAllowed"])
        and not truthy(common_mode["AllowedToPromoteCommonModeA2"])
        else "BLOCKED",
        (
            f"{common_mode['StrongestAllowedClaim']}; "
            f"common-mode rows={common_mode['CommonModeRows']}; "
            f"stable common-mode rows={common_mode['StableCommonModeRows']}; "
            f"blocker rows={common_mode['CommonModeBlockerRows']} "
            f"({common_mode['CommonModeBlockerGridIndices']}); "
            f"grid2 class={common_mode['Grid2Class']}; "
            f"grid2 target/branch sign mismatch={common_mode['Grid2TargetBranchContrastSignMismatch']}; "
            f"grid2 K1/target sign mismatch={common_mode['Grid2K1TargetSignMismatch']}; "
            f"status={common_mode['CurrentStatus']}; "
            f"next={common_mode['RequiredNextCheck']}."
        ),
        "common_mode_baseline_boundary",
    )

    k1_null = read_first(FILES["a2_k1_null_degeneracy"])
    add(
        rows,
        "A2_K1_NULL_DEGENERACY_AUDIT",
        str(FILES["a2_k1_null_degeneracy"].relative_to(ROOT)),
        "WARNING"
        if not truthy(k1_null["MeasurementValidationAllowed"])
        and not truthy(k1_null["AllowedToUnsuppressA2"])
        else "BLOCKED",
        (
            f"{k1_null['StrongestAllowedClaim']}; "
            f"local null rows={k1_null['LocalNullRows']}; "
            f"cancellation-null rows={k1_null['CancellationNullRows']}; "
            f"grid3 class={k1_null['Grid3NullClass']}; "
            f"grid3 K1={k1_null['Grid3K1Response']}; "
            f"grid3 K1/sigma={k1_null['Grid3K1AbsOverSigma']}; "
            f"grid3 centered control={k1_null['Grid3CenteredControl']}; "
            f"grid3 target/centered={k1_null['Grid3TargetOverCenteredControl']}; "
            f"status={k1_null['CurrentStatus']}; "
            f"next={k1_null['RequiredNextCheck']}."
        ),
        "k1_null_degeneracy_boundary",
    )

    overshoot = read_first(FILES["a2_active_memory_overshoot"])
    add(
        rows,
        "A2_ACTIVE_MEMORY_OVERSHOOT_AUDIT",
        str(FILES["a2_active_memory_overshoot"].relative_to(ROOT)),
        "WARNING"
        if not truthy(overshoot["MeasurementValidationAllowed"])
        and not truthy(overshoot["AllowedToChangeATau"])
        else "BLOCKED",
        (
            f"{overshoot['StrongestAllowedClaim']}; "
            f"active rows={overshoot['ActiveMemoryRows']}; "
            f"overshoot rows={overshoot['OvershootRows']}; "
            f"target-implied A_tau range="
            f"{overshoot['MinTargetImpliedATau']}..{overshoot['MaxTargetImpliedATau']} "
            f"(mean={overshoot['MeanTargetImpliedATau']}); "
            f"locked A_tau={overshoot['LockedATau']}; "
            f"mid/high common gain={overshoot['MidHighCommonGain']}; "
            f"high-depth common gain={overshoot['HighDepthCommonGain']}; "
            f"status={overshoot['CurrentStatus']}; "
            f"next={overshoot['RequiredNextCheck']}."
        ),
        "active_memory_overshoot_boundary",
    )

    source_norm = read_first(FILES["a2_source_branch_normalization"])
    add(
        rows,
        "A2_SOURCE_BRANCH_NORMALIZATION_AUDIT",
        str(FILES["a2_source_branch_normalization"].relative_to(ROOT)),
        "WARNING"
        if not truthy(source_norm["MeasurementValidationAllowed"])
        and not truthy(source_norm["AllowedToChangeATau"])
        else "BLOCKED",
        (
            f"{source_norm['StrongestAllowedClaim']}; "
            f"active rows={source_norm['ActiveMemoryRows']}; "
            f"public-rescaled active rows={source_norm['ActiveRowsRescaledByPublicCovariance']}; "
            f"mean public/K1 sigma={source_norm['ActiveMeanPublicSigmaOverK1Sigma']}; "
            f"mean |target|/K1 sigma={source_norm['ActiveMeanAbsTargetOverK1Sigma']}; "
            f"mean |target|/public sigma={source_norm['ActiveMeanAbsTargetOverPublicSigma']}; "
            f"target-fraction 25pct K2>K1={source_norm['TargetFraction25pctK2ImprovesOverK1']}; "
            f"target-fraction 25pct K2>poly={source_norm['TargetFraction25pctK2BeatsBestPoly']}; "
            f"status={source_norm['CurrentStatus']}; "
            f"next={source_norm['RequiredNextCheck']}."
        ),
        "source_branch_normalization_boundary",
    )

    cross_policy = read_first(FILES["a2_cross_covariance_policy"])
    add(
        rows,
        "A2_CROSS_COVARIANCE_POLICY_AUDIT",
        str(FILES["a2_cross_covariance_policy"].relative_to(ROOT)),
        "WARNING"
        if not truthy(cross_policy["MeasurementValidationAllowed"])
        and not truthy(cross_policy["PolicySelectionAllowed"])
        else "BLOCKED",
        (
            f"{cross_policy['StrongestAllowedClaim']}; "
            f"primary rule={cross_policy['PrimaryBenchmarkRule']}; "
            f"positive-definite rho rows={cross_policy['PositiveDefiniteRhoRows']}; "
            f"rho PD range={cross_policy['RhoMinPD']}..{cross_policy['RhoMaxPD']}; "
            f"zero-rho K2>K1={cross_policy['ZeroRhoK2ImprovesOverK1']}; "
            f"zero-rho K2>poly={cross_policy['ZeroRhoK2BeatsBestPoly']}; "
            f"all-PD K2>K1={cross_policy['AllPDK2ImprovesOverK1']}; "
            f"any-PD K2>poly={cross_policy['AnyPDK2BeatsBestPoly']}; "
            f"source norm={cross_policy['SourceNormalizationStatus']}; "
            f"status={cross_policy['CurrentStatus']}; "
            f"next={cross_policy['RequiredNextCheck']}."
        ),
        "cross_covariance_policy_boundary",
    )

    closure = read_first(FILES["measurement_route_closure"])
    add(
        rows,
        "MEASUREMENT_ROUTE_CLOSURE_AUDIT",
        str(FILES["measurement_route_closure"].relative_to(ROOT)),
        "PASS"
        if truthy(closure["PreflightRouteClosed"]) and not truthy(closure["MeasurementValidationAllowed"])
        else "WARNING",
        (
            f"{closure['StrongestAllowedClaim']}; "
            f"preflight blocked={closure['PreflightBlockedChecks']}; "
            f"measurement blocked={closure['MeasurementBlockedChecks']}; "
            f"primary blockers={closure['PrimaryMeasurementBlockers']}."
        ),
        "preflight_closure_measurement_boundary",
    )

    full_gate_plan = read_first(FILES["full_gate_plan"])
    add(
        rows,
        "FULL_GATE_IMPLEMENTATION_PLAN",
        str(FILES["full_gate_plan"].relative_to(ROOT)),
        "PASS"
        if str(full_gate_plan["CurrentStatus"]) == "IMPLEMENTATION_PLAN_READY_MEASUREMENT_ROUTE_BLOCKED"
        and not truthy(full_gate_plan["MeasurementValidationAllowed"])
        else "WARNING",
        (
            f"{full_gate_plan['StrongestAllowedClaim']}; "
            f"preflight closed={full_gate_plan['PreflightClosedComponents']}/{full_gate_plan['Components']}; "
            f"measurement ready={full_gate_plan['MeasurementReadyComponents']}; "
            f"blocked={full_gate_plan['MeasurementBlockedComponents']}; "
            f"primary next={full_gate_plan['PrimaryNextComponent']}."
        ),
        "measurement_gate_execution_plan",
    )

    public_replacement = read_first(FILES["public_covariance_replacement_plan"])
    add(
        rows,
        "PUBLIC_COVARIANCE_REPLACEMENT_PLAN",
        str(FILES["public_covariance_replacement_plan"].relative_to(ROOT)),
        "PASS"
        if str(public_replacement["CurrentStatus"])
        in {
            "PUBLIC_COVARIANCE_REPLACEMENT_PLAN_READY_MEASUREMENT_BLOCKED",
            "PUBLIC_COVARIANCE_LOCKED_RERUN_COMPLETE_MEASUREMENT_BLOCKED",
        }
        and not truthy(public_replacement["MeasurementValidationAllowed"])
        else "WARNING",
        (
            f"{public_replacement['StrongestAllowedClaim']}; "
            f"ready={public_replacement['ReadyComponents']}/{public_replacement['Components']}; "
            f"partial={public_replacement['PartialComponents']}; "
            f"rerun-ready={public_replacement.get('RerunReadyComponents', 0)}; "
            f"rerun-complete={public_replacement.get('RerunCompleteComponents', 0)}; "
            f"blocked={public_replacement['BlockedComponents']}; "
            f"measurement blockers={public_replacement['MeasurementBlockingComponents']}; "
            f"primary blockers={public_replacement['PrimaryBlockers']}."
        ),
        "public_covariance_replacement_boundary",
    )

    target_convention = read_first(FILES["target_convention_adjudication"])
    add(
        rows,
        "PUBLIC_TARGET_CONVENTION_ADJUDICATION",
        str(FILES["target_convention_adjudication"].relative_to(ROOT)),
        "PASS"
        if str(target_convention["CurrentStatus"]) == "TARGET_CONVENTION_ADJUDICATED_MEASUREMENT_STILL_BLOCKED"
        and not truthy(target_convention["SelectionUsesK2Score"])
        and not truthy(target_convention["MeasurementValidationAllowed"])
        else "WARNING",
        (
            f"{target_convention['StrongestAllowedClaim']}; "
            f"preferred preflight convention={target_convention['PreferredPreflightConvention']}; "
            f"recommended next candidate={target_convention['RecommendedNextMeasurementCandidate']}; "
            f"current raw target promoted={target_convention['CurrentRawProjectedTargetPromoted']}; "
            f"selection uses K2 score={target_convention['SelectionUsesK2Score']}; "
            f"next={target_convention['NextAction']}."
        ),
        "target_convention_boundary",
    )

    whitened = read_first(FILES["whitened_standardized_branch_contrast"])
    add(
        rows,
        "WHITENED_STANDARDIZED_BRANCH_CONTRAST",
        str(FILES["whitened_standardized_branch_contrast"].relative_to(ROOT)),
        "PASS"
        if not truthy(whitened["SelectionUsesK2Score"])
        and not truthy(whitened["LockedA2Changed"])
        and not truthy(whitened["K1Refit"])
        and not truthy(whitened["MeasurementValidationAllowed"])
        and truthy(whitened["CovariancePositiveDefinite"])
        else "WARNING",
        (
            f"{whitened['StrongestAllowedClaim']}; "
            f"status={whitened['CurrentStatus']}; "
            f"DeltaAIC K2-K1={whitened['DeltaAIC_K2_minus_K1']}; "
            f"DeltaAIC K2-poly={whitened['DeltaAIC_K2_minus_BestPoly']}; "
            f"K2>K1={whitened['K2ImprovesOverK1']}; "
            f"K2>poly={whitened['K2BeatsBestPoly']}; "
            f"primary risk={whitened['PrimaryResidualRisk']}."
        ),
        "whitened_target_preflight_boundary",
    )

    registered_whitened = read_first(FILES["registered_shrinkage_whitened"])
    add(
        rows,
        "REGISTERED_SHRINKAGE_WHITENED_BRANCH_CONTRAST",
        str(FILES["registered_shrinkage_whitened"].relative_to(ROOT)),
        "PASS"
        if truthy(registered_whitened["RegisteredBeforeThisScore"])
        and not truthy(registered_whitened["LockedA2Changed"])
        and not truthy(registered_whitened["K1Refit"])
        and not truthy(registered_whitened["MeasurementValidationAllowed"])
        and truthy(registered_whitened["PositiveDefinite"])
        else "WARNING",
        (
            f"{registered_whitened['StrongestAllowedClaim']}; "
            f"status={registered_whitened['CurrentStatus']}; "
            f"DeltaAIC K2-K1={registered_whitened['DeltaAIC_K2_minus_K1']}; "
            f"DeltaAIC K2-poly={registered_whitened['DeltaAIC_K2_minus_BestPoly']}; "
            f"K2>K1={registered_whitened['K2ImprovesOverK1']}; "
            f"K2>poly={registered_whitened['K2BeatsBestPoly']}; "
            f"lambda={registered_whitened['LambdaShrink']}; "
            f"L={registered_whitened['CorrelationLength']}; "
            f"risk={registered_whitened['PrimaryResidualRisk']}."
        ),
        "registered_shrinkage_covariance_route_boundary",
    )

    route_comparison = read_first(FILES["whitened_covariance_route_comparison"])
    add(
        rows,
        "WHITENED_COVARIANCE_ROUTE_COMPARISON",
        str(FILES["whitened_covariance_route_comparison"].relative_to(ROOT)),
        "WARNING"
        if not truthy(route_comparison["MeasurementValidationAllowed"])
        and truthy(route_comparison["AllRoutesK2ImproveOverK1"])
        else "BLOCKED",
        (
            f"{route_comparison['StrongestAllowedClaim']}; "
            f"routes={route_comparison['Routes']}; "
            f"K2>K1 routes={route_comparison['K2ImprovesOverK1Routes']}; "
            f"K2>poly routes={route_comparison['K2BeatsBestPolyRoutes']}; "
            f"status={route_comparison['CurrentStatus']}; "
            f"risk={route_comparison['PrimaryResidualRisk']}; "
            f"next={route_comparison['NextAction']}."
        ),
        "covariance_route_comparison_boundary",
    )

    poly_dom = pd.read_csv(FILES["weighted_polynomial_dominance"])
    poly_findings = []
    for _, row in poly_dom.iterrows():
        poly_findings.append(
            f"{row['RouteID']}:AIC={row['BestAICModel']},AICc={row['BestAICcModel']},"
            f"LOO={row['BestLeaveOneOutModel']},blocked={row['BestBlockedDepthModel']}"
        )
    add(
        rows,
        "WEIGHTED_POLYNOMIAL_DOMINANCE_AUDIT",
        str(FILES["weighted_polynomial_dominance"].relative_to(ROOT)),
        "WARNING"
        if not bool(poly_dom["MeasurementValidationAllowed"].map(truthy).any())
        else "BLOCKED",
        (
            "Weighted polynomial dominance audit completed without changing locked A2/K2; "
            f"findings={' | '.join(poly_findings)}; "
            "small-sample/out-of-sample checks determine whether the in-sample polynomial advantage is stable."
        ),
        "polynomial_dominance_boundary",
    )

    phys_white = pd.read_csv(FILES["whitened_physical_null_benchmark"])
    phys_findings = []
    for _, row in phys_white.iterrows():
        phys_findings.append(
            f"{row['RouteID']}:K2>phys={row['K2BeatsBestPhysicalNull']},"
            f"dPhys={row['DeltaAIC_K2_minus_BestPhysicalNull']},"
            f"rows={row['RowsWhereK2StrongerThanBestPhysical']}/{row['Rows']}"
        )
    add(
        rows,
        "WHITENED_PHYSICAL_NULL_BENCHMARK",
        str(FILES["whitened_physical_null_benchmark"].relative_to(ROOT)),
        "PASS"
        if bool(phys_white["K2BeatsBestPhysicalNull"].map(truthy).all())
        and not bool(phys_white["MeasurementValidationAllowed"].map(truthy).any())
        else "WARNING",
        (
            "Whitened physical-null proxy benchmark completed without selecting amplitudes for interpretation; "
            f"findings={' | '.join(phys_findings)}; "
            "physical-null amplitudes remain proxy/sensitivity values."
        ),
        "physical_null_whitened_benchmark_boundary",
    )

    external_sources = read_first(FILES["external_calibration_sources"])
    add(
        rows,
        "EXTERNAL_PHYSICAL_NULL_CALIBRATION_SOURCES",
        str(FILES["external_calibration_sources"].relative_to(ROOT)),
        "WARNING"
        if int(external_sources["DyerRoederPreflightCalibrationSourcesAllowed"]) > 0
        and int(external_sources["MeasurementCalibrationSourcesAllowed"]) == 0
        else "BLOCKED",
        (
            f"{external_sources['StrongestAllowedClaim']}; "
            f"Dyer-Roeder sources={external_sources['DyerRoederSources']}; "
            f"backreaction sources={external_sources['BackreactionSources']}; "
            f"backreaction status={external_sources['BackreactionStatus']}; "
            f"risk={external_sources['PrimaryResidualRisk']}."
        ),
        "external_physical_null_calibration_boundary",
    )

    alpha_cal = pd.read_csv(FILES["whitened_alpha_calibrated"])
    alpha_findings = []
    for _, row in alpha_cal.iterrows():
        alpha_findings.append(
            f"{row['RouteID']}:K2>alpha={row['K2BeatsBestExternalAlpha']},"
            f"dAlpha={row['DeltaAIC_K2_minus_BestAlpha']},"
            f"rows={row['RowsWhereK2StrongerThanBestAlpha']}/{row['Rows']}"
        )
    add(
        rows,
        "WHITENED_ALPHA_CALIBRATED_PREFLIGHT",
        str(FILES["whitened_alpha_calibrated"].relative_to(ROOT)),
        "PASS"
        if bool(alpha_cal["K2BeatsBestExternalAlpha"].map(truthy).all())
        and not bool(alpha_cal["MeasurementValidationAllowed"].map(truthy).any())
        else "WARNING",
        (
            "Externally sourced Dyer-Roeder alpha preflight completed without fitting alpha to the target; "
            f"findings={' | '.join(alpha_findings)}; "
            "alpha remains an optical-null preflight control, not measurement validation."
        ),
        "external_alpha_preflight_boundary",
    )

    backreaction_availability = read_first(FILES["backreaction_source_availability"])
    add(
        rows,
        "BACKREACTION_NUMERIC_SOURCE_AVAILABILITY",
        str(FILES["backreaction_source_availability"].relative_to(ROOT)),
        "WARNING"
        if not truthy(backreaction_availability["AllowedForBackreactionCalibrationNow"])
        and not truthy(backreaction_availability["MeasurementValidationAllowed"])
        else "PASS",
        (
            f"{backreaction_availability['StrongestAllowedClaim']}; "
            f"machine-readable numeric sources={backreaction_availability['MachineReadableNumericConstraintSources']}; "
            f"upstream route detected={backreaction_availability['UpstreamSymbolicRegressionRouteDetected']}; "
            f"status={backreaction_availability['CurrentStatus']}."
        ),
        "backreaction_physical_null_boundary",
    )

    backreaction_contract = read_first(FILES["backreaction_reproduction_contract"])
    add(
        rows,
        "BACKREACTION_REPRODUCTION_CONTRACT",
        str(FILES["backreaction_reproduction_contract"].relative_to(ROOT)),
        "WARNING"
        if not truthy(backreaction_contract["AllowedForBackreactionScoringNow"])
        and not truthy(backreaction_contract["MeasurementValidationAllowed"])
        else "PASS",
        (
            f"{backreaction_contract['StrongestAllowedClaim']}; "
            f"available required items={backreaction_contract['AvailableRequiredItems']}/{backreaction_contract['RequiredItems']}; "
            f"extracted upstream BAO rows={backreaction_contract['ExtractedUpstreamBAORows']}; "
            f"status={backreaction_contract['CurrentStatus']}."
        ),
        "backreaction_reproduction_boundary",
    )

    backreaction_engine = read_first(FILES["backreaction_formula_engine"])
    add(
        rows,
        "BACKREACTION_FORMULA_ENGINE",
        str(FILES["backreaction_formula_engine"].relative_to(ROOT)),
        "WARNING"
        if truthy(backreaction_engine["FormulaEngineAlgebraPassed"])
        and not truthy(backreaction_engine["AllowedForBackreactionScoringNow"])
        and not truthy(backreaction_engine["MeasurementValidationAllowed"])
        else "PASS",
        (
            f"formula algebra passed={backreaction_engine['FormulaEngineAlgebraPassed']}; "
            f"source vector exists={backreaction_engine['SourceNativeVectorExists']}; "
            f"source covariance exists={backreaction_engine['SourceNativeCovarianceExists']}; "
            f"status={backreaction_engine['CurrentStatus']}; "
            f"blocking={backreaction_engine['BlockingIssue']}."
        ),
        "backreaction_formula_engine_boundary",
    )

    backreaction_provisional = read_first(FILES["backreaction_provisional_bao"])
    add(
        rows,
        "BACKREACTION_PROVISIONAL_BAO_RECONSTRUCTION",
        str(FILES["backreaction_provisional_bao"].relative_to(ROOT)),
        "WARNING"
        if truthy(backreaction_provisional["AllowedForBackreactionPreflightScoring"])
        and not truthy(backreaction_provisional["AllowedForMeasurementValidation"])
        else "BLOCKED",
        (
            f"{backreaction_provisional['StrongestAllowedClaim']}; "
            f"rows={backreaction_provisional['Rows']}; "
            f"bootstrap used={backreaction_provisional['BootstrapDrawsUsed']}; "
            f"omega range={backreaction_provisional['OmegaMin']}..{backreaction_provisional['OmegaMax']}; "
            f"risk={backreaction_provisional['PrimaryResidualRisk']}."
        ),
        "backreaction_provisional_sensitivity_boundary",
    )

    backreaction_comparison = pd.read_csv(FILES["backreaction_provisional_comparison"])
    comparison_findings = []
    for _, row in backreaction_comparison.iterrows():
        comparison_findings.append(
            f"{row['RouteID']}:status={row['CurrentStatus']},"
            f"dK2Raw={row['DeltaChi2_K2_minus_RawBackreaction']},"
            f"corrTarget={row['RawCorrelationWithTarget']},"
            f"stableSigns={row['RawStableSignMatches']}/{row['StableRows']}"
        )
    add(
        rows,
        "BACKREACTION_PROVISIONAL_PREFLIGHT_COMPARISON",
        str(FILES["backreaction_provisional_comparison"].relative_to(ROOT)),
        "WARNING"
        if not bool(backreaction_comparison["AllowedForMeasurementValidation"].map(truthy).any())
        else "BLOCKED",
        (
            "Provisional BAO-only backreaction bridge comparison completed; "
            f"findings={' | '.join(comparison_findings)}; "
            "observable bridge and fitted scales remain non-claim diagnostics."
        ),
        "backreaction_provisional_comparison_boundary",
    )

    bridge_diagnosis = read_first(FILES["backreaction_bridge_diagnosis"])
    add(
        rows,
        "BACKREACTION_PROVISIONAL_BRIDGE_DIAGNOSIS",
        str(FILES["backreaction_bridge_diagnosis"].relative_to(ROOT)),
        "WARNING" if not truthy(bridge_diagnosis["MeasurementValidationAllowed"]) else "BLOCKED",
        (
            f"{bridge_diagnosis['StrongestAllowedClaim']}; "
            f"K2-aligned/target-anti rows={bridge_diagnosis['K2AlignedTargetAntiAlignedRows']}/{bridge_diagnosis['Rows']}; "
            f"K2 closer rows={bridge_diagnosis['RowsWhereK2CloserThanBackreactionToTarget']}/{bridge_diagnosis['Rows']}; "
            f"status={bridge_diagnosis['CurrentStatus']}."
        ),
        "backreaction_bridge_diagnosis_boundary",
    )

    component_split = read_first(FILES["backreaction_k2_component_split"])
    add(
        rows,
        "BACKREACTION_K2_COMPONENT_SPLIT",
        str(FILES["backreaction_k2_component_split"].relative_to(ROOT)),
        "WARNING" if not truthy(component_split["MeasurementValidationAllowed"]) else "BLOCKED",
        (
            f"{component_split['StrongestAllowedClaim']}; "
            f"mid/high backreaction-like K2 energy fraction mean={component_split['MidHighBackreactionEnergyFractionMean']}; "
            f"high-depth fraction mean={component_split['HighBackreactionEnergyFractionMean']}; "
            f"status={component_split['CurrentStatus']}."
        ),
        "backreaction_k2_component_split_boundary",
    )

    residual_after_backreaction = read_first(FILES["k2_residual_after_backreaction"])
    add(
        rows,
        "K2_RESIDUAL_AFTER_BACKREACTION",
        str(FILES["k2_residual_after_backreaction"].relative_to(ROOT)),
        "WARNING" if not truthy(residual_after_backreaction["MeasurementValidationAllowed"]) else "BLOCKED",
        (
            f"{residual_after_backreaction['StrongestAllowedClaim']}; "
            f"mid/high residual fraction mean={residual_after_backreaction['MidHighResidualEnergyFractionMean']}; "
            f"high residual fraction mean={residual_after_backreaction['HighResidualEnergyFractionMean']}; "
            f"status={residual_after_backreaction['CurrentStatus']}."
        ),
        "finite_memory_residual_boundary",
    )

    bridge_variant = read_first(FILES["backreaction_bridge_variant_stability"])
    add(
        rows,
        "BACKREACTION_BRIDGE_VARIANT_STABILITY",
        str(FILES["backreaction_bridge_variant_stability"].relative_to(ROOT)),
        "WARNING" if not truthy(bridge_variant["MeasurementValidationAllowed"]) else "BLOCKED",
        (
            f"{bridge_variant['StrongestAllowedClaim']}; "
            f"allowed variants={bridge_variant['AllowedVariants']}/{bridge_variant['Variants']}; "
            f"mid/high allowed component fraction mean={bridge_variant['MidHighAllowedEnergyFractionMean']}; "
            f"high-depth allowed component fraction mean={bridge_variant['HighAllowedEnergyFractionMean']}; "
            f"status={bridge_variant['CurrentStatus']}."
        ),
        "backreaction_bridge_variant_stability_boundary",
    )

    depth_stability = pd.read_csv(FILES["backreaction_depth_stability"])
    status_counts = depth_stability["DepthStabilityStatus"].value_counts().to_dict()
    add(
        rows,
        "BACKREACTION_DEPTH_STABILITY",
        str(FILES["backreaction_depth_stability"].relative_to(ROOT)),
        "WARNING" if not bool(depth_stability["MeasurementValidationAllowed"].map(truthy).any()) else "BLOCKED",
        (
            "Leave-one-depth audit completed without changing locked K2; "
            f"statuses={status_counts}; "
            f"min leave-one component fraction={depth_stability['LeaveOneEnergyFractionMin'].min()}; "
            f"max drop={depth_stability['MaxDropFromBaseMean'].max()}."
        ),
        "backreaction_depth_stability_boundary",
    )

    source_native_upgrade = read_first(FILES["source_native_backreaction_upgrade"])
    add(
        rows,
        "SOURCE_NATIVE_BACKREACTION_UPGRADE",
        str(FILES["source_native_backreaction_upgrade"].relative_to(ROOT)),
        "WARNING" if not truthy(source_native_upgrade["MeasurementValidationAllowed"]) else "BLOCKED",
        (
            f"{source_native_upgrade['StrongestAllowedClaim']}; "
            f"families={source_native_upgrade['FamiliesRequired']}; "
            f"blocking items={source_native_upgrade['BlockingItems']}/{source_native_upgrade['TotalRequiredItems']}; "
            f"status={source_native_upgrade['CurrentStatus']}."
        ),
        "source_native_backreaction_upgrade_boundary",
    )

    source_native_inputs = read_first(FILES["source_native_public_inputs"])
    add(
        rows,
        "SOURCE_NATIVE_PUBLIC_INPUT_VALIDATION",
        str(FILES["source_native_public_inputs"].relative_to(ROOT)),
        "PASS" if truthy(source_native_inputs["AllPublicInputsValidated"]) else "WARNING",
        (
            f"{source_native_inputs['StrongestAllowedClaim']}; "
            f"SN input validated={source_native_inputs['SNInputValidated']}; "
            f"BAO products validated={source_native_inputs['BAOProductsValidated']}/{source_native_inputs['BAOProductsAudited']}; "
            f"status={source_native_inputs['CurrentStatus']}."
        ),
        "source_native_public_input_boundary",
    )

    source_native_runtime = read_first(FILES["source_native_runtime"])
    add(
        rows,
        "SOURCE_NATIVE_RUNTIME_VALIDATION",
        str(FILES["source_native_runtime"].relative_to(ROOT)),
        "WARNING" if not truthy(source_native_runtime["SymbolicRegressionRuntimeReady"]) else "PASS",
        (
            f"{source_native_runtime['StrongestAllowedClaim']}; "
            f"minimum runtime ready={source_native_runtime['MinimumFormulaAuditRuntimeReady']}; "
            f"symbolic runtime ready={source_native_runtime['SymbolicRegressionRuntimeReady']}; "
            f"status={source_native_runtime['CurrentStatus']}."
        ),
        "source_native_runtime_boundary",
    )

    symbolic_online = read_first(FILES["symbolic_regression_online_sources"])
    add(
        rows,
        "SYMBOLIC_REGRESSION_ONLINE_SOURCE_PROBE",
        str(FILES["symbolic_regression_online_sources"].relative_to(ROOT)),
        "WARNING" if not truthy(symbolic_online["SourceNativeScoringReady"]) else "PASS",
        (
            f"{symbolic_online['StrongestAllowedClaim']}; "
            f"sources probed={symbolic_online['SourcesProbed']}; "
            f"generic tooling sources={symbolic_online['GenericToolingSources']}; "
            f"paper-specific derivative export sources={symbolic_online['PaperSpecificDerivativeExportSources']}; "
            f"status={symbolic_online['CurrentStatus']}."
        ),
        "symbolic_regression_online_source_boundary",
    )

    source_native_templates = read_first(FILES["source_native_templates"])
    add(
        rows,
        "SOURCE_NATIVE_BACKREACTION_EXPORT_TEMPLATES",
        str(FILES["source_native_templates"].relative_to(ROOT)),
        "PASS" if truthy(source_native_templates["ReconstructionTemplateCreated"]) and truthy(source_native_templates["SelectionMetadataTemplateCreated"]) else "WARNING",
        (
            f"{source_native_templates['StrongestAllowedClaim']}; "
            f"families={source_native_templates['FamiliesDeclared']}; "
            f"status={source_native_templates['CurrentStatus']}."
        ),
        "source_native_export_template_boundary",
    )

    source_native_export_validation = read_first(FILES["source_native_export_validation"])
    add(
        rows,
        "SOURCE_NATIVE_BACKREACTION_EXPORT_VALIDATION",
        str(FILES["source_native_export_validation"].relative_to(ROOT)),
        "WARNING" if not truthy(source_native_export_validation["SourceNativeBackreactionExportsReady"]) else "PASS",
        (
            f"{source_native_export_validation['StrongestAllowedClaim']}; "
            f"reconstruction valid={source_native_export_validation['ReconstructionVectorValid']}; "
            f"metadata valid={source_native_export_validation['SelectionMetadataValid']}; "
            f"status={source_native_export_validation['CurrentStatus']}."
        ),
        "source_native_export_validation_boundary",
    )

    source_native_uncertainty = read_first(FILES["source_native_uncertainty_validation"])
    add(
        rows,
        "SOURCE_NATIVE_BACKREACTION_UNCERTAINTY_VALIDATION",
        str(FILES["source_native_uncertainty_validation"].relative_to(ROOT)),
        "WARNING" if not truthy(source_native_uncertainty["AnySourceNativeUncertaintyReady"]) else "PASS",
        (
            f"{source_native_uncertainty['StrongestAllowedClaim']}; "
            f"bootstrap valid={source_native_uncertainty['BootstrapSamplesValid']}; "
            f"covariance valid={source_native_uncertainty['CovarianceValid']}; "
            f"status={source_native_uncertainty['CurrentStatus']}."
        ),
        "source_native_uncertainty_validation_boundary",
    )

    source_native_bridge = read_first(FILES["source_native_backreaction_bridge"])
    add(
        rows,
        "SOURCE_NATIVE_BACKREACTION_BRIDGE_SCORECARD",
        str(FILES["source_native_backreaction_bridge"].relative_to(ROOT)),
        "WARNING" if not truthy(source_native_bridge["SourceNativeBridgeScoringReady"]) else "PASS",
        (
            f"{source_native_bridge['StrongestAllowedClaim']}; "
            f"vector available={source_native_bridge['SourceNativeVectorAvailable']}; "
            f"families scored={source_native_bridge['FamiliesScored']}; "
            f"status={source_native_bridge['CurrentStatus']}."
        ),
        "source_native_backreaction_bridge_scorecard_boundary",
    )

    source_native_fixture = read_first(FILES["source_native_fixture_smoke"])
    add(
        rows,
        "SOURCE_NATIVE_BACKREACTION_FIXTURE_SMOKE_TEST",
        str(FILES["source_native_fixture_smoke"].relative_to(ROOT)),
        "PASS" if truthy(source_native_fixture["FixturePipelinePasses"]) else "WARNING",
        (
            f"{source_native_fixture['StrongestAllowedClaim']}; "
            f"omega rows={source_native_fixture['OmegaRowsWritten']}; "
            f"bridge score rows={source_native_fixture['BridgeScoreRowsWritten']}; "
            f"fixture only={source_native_fixture['FixtureDataOnly']}; "
            f"status={source_native_fixture['CurrentStatus']}."
        ),
        "source_native_fixture_smoke_boundary",
    )

    source_native_uncertainty_fixture = read_first(FILES["source_native_uncertainty_fixture_smoke"])
    add(
        rows,
        "SOURCE_NATIVE_UNCERTAINTY_FIXTURE_SMOKE_TEST",
        str(FILES["source_native_uncertainty_fixture_smoke"].relative_to(ROOT)),
        "PASS" if truthy(source_native_uncertainty_fixture["FixtureUncertaintyPipelinePasses"]) else "WARNING",
        (
            f"{source_native_uncertainty_fixture['StrongestAllowedClaim']}; "
            f"bootstrap rows={source_native_uncertainty_fixture['BootstrapRowsWritten']}; "
            f"covariance rows={source_native_uncertainty_fixture['CovarianceRowsWritten']}; "
            f"fixture only={source_native_uncertainty_fixture['FixtureDataOnly']}; "
            f"status={source_native_uncertainty_fixture['CurrentStatus']}."
        ),
        "source_native_uncertainty_fixture_smoke_boundary",
    )

    source_native_training = read_first(FILES["source_native_training_datasets"])
    add(
        rows,
        "SOURCE_NATIVE_TRAINING_DATASETS",
        str(FILES["source_native_training_datasets"].relative_to(ROOT)),
        "PASS" if truthy(source_native_training["TrainingDatasetsReady"]) else "WARNING",
        (
            f"{source_native_training['StrongestAllowedClaim']}; "
            f"SN rows={source_native_training['SNTrainingRows']}; "
            f"BAO rows={source_native_training['BAOTrainingRows']}; "
            f"derivative exports ready={source_native_training['DerivativeExportsReady']}; "
            f"status={source_native_training['CurrentStatus']}."
        ),
        "source_native_training_input_boundary",
    )

    source_native_derivative_pilot = read_first(FILES["source_native_derivative_pilot"])
    add(
        rows,
        "SOURCE_NATIVE_DERIVATIVE_PILOT",
        str(FILES["source_native_derivative_pilot"].relative_to(ROOT)),
        "PASS" if truthy(source_native_derivative_pilot["DerivativePilotReady"]) else "WARNING",
        (
            f"{source_native_derivative_pilot['StrongestAllowedClaim']}; "
            f"grid rows={source_native_derivative_pilot['GridRows']}; "
            f"omega median={source_native_derivative_pilot['OmegaMedian']}; "
            f"source-native export ready={source_native_derivative_pilot['SourceNativeExportReady']}; "
            f"status={source_native_derivative_pilot['CurrentStatus']}."
        ),
        "source_native_derivative_pilot_boundary",
    )

    source_native_derivative_pilot_uncertainty = read_first(FILES["source_native_derivative_pilot_uncertainty"])
    add(
        rows,
        "SOURCE_NATIVE_DERIVATIVE_PILOT_UNCERTAINTY",
        str(FILES["source_native_derivative_pilot_uncertainty"].relative_to(ROOT)),
        "PASS" if truthy(source_native_derivative_pilot_uncertainty["BootstrapUncertaintyReady"]) else "WARNING",
        (
            f"{source_native_derivative_pilot_uncertainty['StrongestAllowedClaim']}; "
            f"samples={source_native_derivative_pilot_uncertainty['SuccessfulSamples']}; "
            f"median relative sigma={source_native_derivative_pilot_uncertainty['MedianRelativeOmegaSigma']}; "
            f"source-native uncertainty ready={source_native_derivative_pilot_uncertainty['SourceNativeUncertaintyReady']}; "
            f"status={source_native_derivative_pilot_uncertainty['CurrentStatus']}."
        ),
        "source_native_derivative_pilot_uncertainty_boundary",
    )

    source_native_derivative_bridge = read_first(FILES["source_native_derivative_pilot_bridge"])
    add(
        rows,
        "SOURCE_NATIVE_DERIVATIVE_PILOT_BRIDGE_COMPARISON",
        str(FILES["source_native_derivative_pilot_bridge"].relative_to(ROOT)),
        "WARNING",
        (
            f"{source_native_derivative_bridge['StrongestAllowedClaim']}; "
            f"rows compared={source_native_derivative_bridge['RowsCompared']}; "
            f"sign matches={source_native_derivative_bridge['SignMatchesProvisional']}; "
            f"correlation={source_native_derivative_bridge['CorrelationPilotProvisional']}; "
            f"status={source_native_derivative_bridge['CurrentStatus']}."
        ),
        "source_native_derivative_pilot_bridge_boundary",
    )

    derivative_pilot_split = read_first(FILES["derivative_pilot_k2_component_split"])
    add(
        rows,
        "DERIVATIVE_PILOT_K2_COMPONENT_SPLIT",
        str(FILES["derivative_pilot_k2_component_split"].relative_to(ROOT)),
        "WARNING",
        (
            f"{derivative_pilot_split['StrongestAllowedClaim']}; "
            f"mid/high pilot fraction={derivative_pilot_split['MidHighPilotEnergyFractionMean']}; "
            f"high pilot fraction={derivative_pilot_split['HighPilotEnergyFractionMean']}; "
            f"low pilot fraction={derivative_pilot_split['LowPilotEnergyFractionMean']}; "
            f"status={derivative_pilot_split['CurrentStatus']}."
        ),
        "derivative_pilot_k2_component_split_boundary",
    )

    derivative_pilot_component_uncertainty = read_first(FILES["derivative_pilot_component_uncertainty"])
    add(
        rows,
        "DERIVATIVE_PILOT_COMPONENT_UNCERTAINTY",
        str(FILES["derivative_pilot_component_uncertainty"].relative_to(ROOT)),
        "WARNING",
        (
            f"{derivative_pilot_component_uncertainty['StrongestAllowedClaim']}; "
            f"mid/high P50={derivative_pilot_component_uncertainty['mid_high_depth_P50']}; "
            f"mid/high P16..P84={derivative_pilot_component_uncertainty['mid_high_depth_P16']}.."
            f"{derivative_pilot_component_uncertainty['mid_high_depth_P84']}; "
            f"low P50={derivative_pilot_component_uncertainty['low_depth_P50']}; "
            f"status={derivative_pilot_component_uncertainty['CurrentStatus']}."
        ),
        "derivative_pilot_component_uncertainty_boundary",
    )

    noise_summary = pd.read_csv(FILES["derivative_pilot_noise_source"])
    noise_overall = noise_summary[noise_summary["NoiseMode"].eq("OVERALL")].iloc[0]
    add(
        rows,
        "DERIVATIVE_PILOT_NOISE_SOURCE_AUDIT",
        str(FILES["derivative_pilot_noise_source"].relative_to(ROOT)),
        "WARNING",
        (
            f"{noise_overall['StrongestAllowedClaim']}; "
            f"dominant low-depth spread mode={noise_overall['DominantLowDepthSpreadMode']}; "
            f"mid/high P50={noise_overall['ComponentFractionP50']}; "
            f"status={noise_overall['CurrentStatus']}."
        ),
        "derivative_pilot_noise_source_boundary",
    )

    degree_sensitivity = read_first(FILES["derivative_pilot_degree_sensitivity"])
    add(
        rows,
        "DERIVATIVE_PILOT_DEGREE_SENSITIVITY",
        str(FILES["derivative_pilot_degree_sensitivity"].relative_to(ROOT)),
        "WARNING",
        (
            f"{degree_sensitivity['StrongestAllowedClaim']}; "
            f"mid/high P50={degree_sensitivity['MidHighComponentFractionP50']}; "
            f"low P50={degree_sensitivity['LowComponentFractionP50']}; "
            f"low-depth degree sensitive={degree_sensitivity['LowDepthDegreeSensitive']}; "
            f"status={degree_sensitivity['CurrentStatus']}."
        ),
        "derivative_pilot_degree_sensitivity_boundary",
    )

    midhigh_stability = read_first(FILES["midhigh_component_stability"])
    add(
        rows,
        "MIDHIGH_COMPONENT_STABILITY_AUDIT",
        str(FILES["midhigh_component_stability"].relative_to(ROOT)),
        "PASS" if int(midhigh_stability["ChecksSurvivingThreshold"]) == int(midhigh_stability["Checks"]) else "WARNING",
        (
            f"{midhigh_stability['StrongestAllowedClaim']}; "
            f"checks={midhigh_stability['ChecksSurvivingThreshold']}/{midhigh_stability['Checks']}; "
            f"mid/high lower min={midhigh_stability['MidHighLowerMinAcrossChecks']}; "
            f"low stable suppression={midhigh_stability['LowDepthStableSuppression']}; "
            f"status={midhigh_stability['CurrentStatus']}."
        ),
        "midhigh_component_stability_boundary",
    )

    low_depth_support = read_first(FILES["low_depth_tau_core_support"])
    add(
        rows,
        "LOW_DEPTH_TAU_CORE_SUPPORT_AUDIT",
        str(FILES["low_depth_tau_core_support"].relative_to(ROOT)),
        "PASS" if int(low_depth_support["TauCoreSuppressionChecks"]) >= 3 else "WARNING",
        (
            f"{low_depth_support['StrongestAllowedClaim']}; "
            f"tau-core suppression checks={low_depth_support['TauCoreSuppressionChecks']}; "
            f"locked K2 low/high target ratio={low_depth_support['LockedK2TargetLowToHighRatio']}; "
            f"pilot physical-null stable={low_depth_support['LowDepthStableAsPilotPhysicalNull']}; "
            f"status={low_depth_support['CurrentStatus']}."
        ),
        "low_depth_tau_core_support_boundary",
    )

    claim_ladder = read_first(FILES["tau_core_a2_claim_ladder"])
    add(
        rows,
        "TAU_CORE_A2_CLAIM_LADDER",
        str(FILES["tau_core_a2_claim_ladder"].relative_to(ROOT)),
        "PASS"
        if str(claim_ladder["CurrentStatus"]) == "A2_PREFLIGHT_CLAIM_LADDER_READY_MEASUREMENT_CLOSED"
        and not truthy(claim_ladder["MeasurementValidationAllowed"])
        else "WARNING",
        (
            f"{claim_ladder['StrongestAllowedClaim']}; "
            f"strong preflight claims={claim_ladder['StrongPreflightClaims']}/{claim_ladder['Claims']}; "
            f"low-depth operator support={claim_ladder['LockedOperatorLowDepthSuppression']}; "
            f"mid/high stable={claim_ladder['MidHighBackreactionLikeComponentStable']}; "
            f"low-depth physical null stable={claim_ladder['LowDepthPhysicalNullStable']}; "
            f"source-native ready={claim_ladder['SourceNativeScoringReady']}."
        ),
        "paper_language_claim_ladder",
    )

    surrogate_export = read_first(FILES["source_native_surrogate_family_export"])
    add(
        rows,
        "SOURCE_NATIVE_SURROGATE_FAMILY_EXPORT",
        str(FILES["source_native_surrogate_family_export"].relative_to(ROOT)),
        "WARNING"
        if truthy(surrogate_export["SurrogateFamilyExportsReady"])
        and not truthy(surrogate_export["SourceNativeExportsReady"])
        and not truthy(surrogate_export["MeasurementValidationAllowed"])
        else "BLOCKED",
        (
            f"{surrogate_export['StrongestAllowedClaim']}; "
            f"families={surrogate_export['Families']}; "
            f"grid rows/family={surrogate_export['GridRowsPerFamily']}; "
            f"finite derivatives={surrogate_export['FiniteDerivativeVectors']}; "
            f"source-native exports ready={surrogate_export['SourceNativeExportsReady']}; "
            f"status={surrogate_export['CurrentStatus']}."
        ),
        "source_native_pipeline_rehearsal_boundary",
    )

    surrogate_bridge = read_first(FILES["source_native_surrogate_bridge"])
    add(
        rows,
        "SOURCE_NATIVE_SURROGATE_BRIDGE_SCORECARD",
        str(FILES["source_native_surrogate_bridge"].relative_to(ROOT)),
        "WARNING"
        if truthy(surrogate_bridge["SurrogateBridgeScoringReady"])
        and not truthy(surrogate_bridge["SourceNativeBridgeScoringReady"])
        and not truthy(surrogate_bridge["MeasurementValidationAllowed"])
        else "BLOCKED",
        (
            f"{surrogate_bridge['StrongestAllowedClaim']}; "
            f"route-family cases={surrogate_bridge['RouteFamilyCases']}; "
            f"K2 beats surrogate cases={surrogate_bridge['K2BeatsSurrogateBackreactionCases']}; "
            f"K2 beats K1 cases={surrogate_bridge['K2BeatsK1Cases']}; "
            f"median corr(surrogate,K2)={surrogate_bridge['MedianCorrelationSurrogateWithK2']}; "
            f"source-native bridge ready={surrogate_bridge['SourceNativeBridgeScoringReady']}."
        ),
        "source_native_pipeline_rehearsal_boundary",
    )

    surrogate_shape = read_first(FILES["source_native_surrogate_bridge_shape"])
    add(
        rows,
        "SOURCE_NATIVE_SURROGATE_BRIDGE_SHAPE_DIAGNOSIS",
        str(FILES["source_native_surrogate_bridge_shape"].relative_to(ROOT)),
        "WARNING"
        if str(surrogate_shape["CurrentStatus"]) == "SURROGATE_BRIDGE_MISMATCH_DIAGNOSED_SOURCE_NATIVE_STILL_MISSING"
        and not truthy(surrogate_shape["MeasurementValidationAllowed"])
        else "BLOCKED",
        (
            f"{surrogate_shape['StrongestAllowedClaim']}; "
            f"cases={surrogate_shape['Cases']}; "
            f"K2-like shape cases={surrogate_shape['K2LikeShapeCases']}; "
            f"amplitude-dominated cases={surrogate_shape['AmplitudeDominatedCases']}; "
            f"sign/shape mismatch cases={surrogate_shape['SignOrShapeMismatchCases']}; "
            f"median corr(surrogate,K2)={surrogate_shape['MedianCorrelationSurrogateWithK2']}."
        ),
        "source_native_pipeline_rehearsal_boundary",
    )

    surrogate_rank = read_first(FILES["source_native_surrogate_family_rank"])
    add(
        rows,
        "SOURCE_NATIVE_SURROGATE_FAMILY_RANK",
        str(FILES["source_native_surrogate_family_rank"].relative_to(ROOT)),
        "WARNING"
        if str(surrogate_rank["CurrentStatus"]) == "SURROGATE_FAMILY_RANK_READY_SOURCE_NATIVE_FOLLOWUP_PRIORITIZED"
        and not truthy(surrogate_rank["MeasurementValidationAllowed"])
        else "BLOCKED",
        (
            f"{surrogate_rank['StrongestAllowedClaim']}; "
            f"families ranked={surrogate_rank['FamiliesRanked']}; "
            f"top family={surrogate_rank['TopFamilyID']}; "
            f"top corr(K2)={surrogate_rank['TopFamilyMeanCorrelationWithK2']}; "
            f"positive K2-corr families={surrogate_rank['FamiliesWithPositiveMeanK2Correlation']}; "
            f"families with sign/shape mismatch={surrogate_rank['FamiliesWithSignOrShapeMismatch']}."
        ),
        "source_native_followup_prioritization_boundary",
    )

    decision_rules = read_first(FILES["source_native_backreaction_decision_rules"])
    add(
        rows,
        "SOURCE_NATIVE_BACKREACTION_DECISION_RULES",
        str(FILES["source_native_backreaction_decision_rules"].relative_to(ROOT)),
        "PASS"
        if str(decision_rules["CurrentStatus"]) == "SOURCE_NATIVE_BACKREACTION_DECISION_RULES_REGISTERED"
        and not truthy(decision_rules["MeasurementValidationAllowed"])
        else "WARNING",
        (
            f"{decision_rules['StrongestAllowedClaim']}; "
            f"rules={decision_rules['Rules']}; "
            f"top surrogate comparator={decision_rules['TopSurrogateFamilyForFutureComparison']}; "
            f"source-native export ready={decision_rules['SourceNativeExportReady']}; "
            f"source-native covariance ready={decision_rules['SourceNativeCovarianceReady']}."
        ),
        "source_native_future_interpretation_policy",
    )

    decision_dry_run = read_first(FILES["source_native_backreaction_decision_dry_run"])
    add(
        rows,
        "SOURCE_NATIVE_BACKREACTION_DECISION_DRY_RUN",
        str(FILES["source_native_backreaction_decision_dry_run"].relative_to(ROOT)),
        "WARNING"
        if str(decision_dry_run["CurrentStatus"]) == "SOURCE_NATIVE_DECISION_RULES_DRY_RUN_EXECUTABLE"
        and not truthy(decision_dry_run["MeasurementValidationAllowed"])
        else "BLOCKED",
        (
            f"{decision_dry_run['StrongestAllowedClaim']}; "
            f"rules evaluated={decision_dry_run['RulesEvaluated']}; "
            f"supportive dry-run rules={decision_dry_run['SupportiveDryRunRules']}; "
            f"weakening dry-run rules={decision_dry_run['WeakeningDryRunRules']}; "
            f"K2 beats surrogate cases={decision_dry_run['K2BeatsSurrogateCases']}/"
            f"{decision_dry_run['RouteFamilyCases']}; "
            f"source-native export ready={decision_dry_run['SourceNativeExportReady']}."
        ),
        "source_native_future_interpretation_policy",
    )

    symbolic_protocol = read_first(FILES["source_native_symbolic_protocol"])
    add(
        rows,
        "SOURCE_NATIVE_SYMBOLIC_PROTOCOL_EXTRACT",
        str(FILES["source_native_symbolic_protocol"].relative_to(ROOT)),
        "WARNING"
        if str(symbolic_protocol["CurrentStatus"]) == "UPSTREAM_PROTOCOL_EXTRACTED_SOURCE_NATIVE_VECTOR_STILL_MISSING"
        and not truthy(symbolic_protocol["MeasurementValidationAllowed"])
        else "BLOCKED",
        (
            f"{symbolic_protocol['StrongestAllowedClaim']}; "
            f"protocol items={symbolic_protocol['ProtocolItems']}; "
            f"BAO rows extracted={symbolic_protocol['BAOTableRowsExtracted']}; "
            f"directly executable items={symbolic_protocol['DirectlyExecutableItems']}; "
            f"manual judgment items={symbolic_protocol['ManualJudgmentItems']}; "
            f"author vectors available={symbolic_protocol['AuthorDerivativeVectorsAvailable']}."
        ),
        "source_native_reproduction_protocol_boundary",
    )

    pysr_contract = read_first(FILES["pysr_criteria3_contract"])
    add(
        rows,
        "PYSR_CRITERIA3_REPRODUCTION_CONTRACT",
        str(FILES["pysr_criteria3_contract"].relative_to(ROOT)),
        "WARNING"
        if str(pysr_contract["CurrentStatus"]) == "PYSR_CRITERIA3_CONTRACT_READY_RUNTIME_BLOCKED"
        and not truthy(pysr_contract["MeasurementValidationAllowed"])
        else ("PASS" if truthy(pysr_contract["ExecutionReady"]) else "BLOCKED"),
        (
            f"{pysr_contract['StrongestAllowedClaim']}; "
            f"inputs ready={pysr_contract['InputsReady']}; "
            f"runtime ready={pysr_contract['RuntimeReady']}; "
            f"PySR={pysr_contract['PySRAvailable']}; "
            f"Julia={pysr_contract['JuliaAvailable']}; "
            f"execution ready={pysr_contract['ExecutionReady']}."
        ),
        "source_native_reproduction_runtime_boundary",
    )

    pysr_smoke = read_first(FILES["pysr_criteria3_smoke"])
    add(
        rows,
        "PYSR_CRITERIA3_SMOKE_RUN",
        str(FILES["pysr_criteria3_smoke"].relative_to(ROOT)),
        "WARNING"
        if str(pysr_smoke["CurrentStatus"]) == "PYSR_CRITERIA3_SMOKE_EXECUTED_NO_MEASUREMENT_VALIDATION"
        and not truthy(pysr_smoke["MeasurementValidationAllowed"])
        and not truthy(pysr_smoke["K2KernelChanged"])
        and not truthy(pysr_smoke["RhoGreaterThan4Allowed"])
        and not truthy(pysr_smoke["K1Refit"])
        else "BLOCKED",
        (
            f"{pysr_smoke['StrongestAllowedClaim']}; "
            f"selected equation={pysr_smoke['SelectedEquation']}; "
            f"complexity={pysr_smoke['SelectedComplexity']}; "
            f"criteria3 score={pysr_smoke['Criteria3Score']}; "
            f"weighted MSE={pysr_smoke['WeightedMSE']}; "
            f"source-native covariance ready={pysr_smoke['SourceNativeCovarianceReady']}."
        ),
        "source_native_reproduction_smoke_boundary",
    )

    pysr_structured = read_first(FILES["pysr_criteria3_structured_smoke"])
    add(
        rows,
        "PYSR_CRITERIA3_STRUCTURED_SMOKE",
        str(FILES["pysr_criteria3_structured_smoke"].relative_to(ROOT)),
        "WARNING"
        if str(pysr_structured["CurrentStatus"])
        == "STRICT_CRITERIA3_SELECTS_CONSTANT_NONCONSTANT_SHAPE_AVAILABLE"
        and not truthy(pysr_structured["MeasurementValidationAllowed"])
        and not truthy(pysr_structured["K2KernelChanged"])
        and not truthy(pysr_structured["RhoGreaterThan4Allowed"])
        and not truthy(pysr_structured["K1Refit"])
        else "BLOCKED",
        (
            f"{pysr_structured['StrongestAllowedClaim']}; "
            f"strict equation={pysr_structured['StrictSelectedEquation']}; "
            f"strict W-MSE={pysr_structured['StrictWeightedMSEOriginal']}; "
            f"best nonconstant equation={pysr_structured['BestNonconstantEquation']}; "
            f"best nonconstant W-MSE={pysr_structured['BestNonconstantWeightedMSEOriginal']}; "
            f"penalty-one selects constant={pysr_structured['PenaltyOneSelectsConstant']}."
        ),
        "source_native_reproduction_penalty_diagnosis_boundary",
    )

    pysr_penalty = read_first(FILES["pysr_penalty_normalization"])
    add(
        rows,
        "PYSR_PENALTY_NORMALIZATION_AUDIT",
        str(FILES["pysr_penalty_normalization"].relative_to(ROOT)),
        "WARNING"
        if str(pysr_penalty["CurrentStatus"])
        == "PYSR_PENALTY_NORMALIZATION_REQUIRED_BEFORE_SOURCE_NATIVE_SCORING"
        and not truthy(pysr_penalty["MeasurementValidationAllowed"])
        else "BLOCKED",
        (
            f"{pysr_penalty['StrongestAllowedClaim']}; "
            f"break-even penalty={pysr_penalty['BreakEvenPenaltyBestNonconstantVsConstant']}; "
            f"strict penalty-one constant={pysr_penalty['StrictPenaltyOneSelectedIsConstant']}; "
            f"best nonconstant W-MSE={pysr_penalty['BestNonconstantWeightedMSEOriginal']}; "
            f"normalization required={pysr_penalty['PenaltyNormalizationRequiredBeforeSourceNativeScoring']}."
        ),
        "source_native_reproduction_penalty_governance_boundary",
    )

    normalized_selector = read_first(FILES["source_native_normalized_criteria3_selector"])
    add(
        rows,
        "SOURCE_NATIVE_NORMALIZED_CRITERIA3_SELECTOR",
        str(FILES["source_native_normalized_criteria3_selector"].relative_to(ROOT)),
        "WARNING"
        if str(normalized_selector["CurrentStatus"])
        == "SOURCE_NATIVE_NORMALIZED_CRITERIA3_PRE_REGISTERED_NOT_MEASUREMENT_ACTIVE"
        and not truthy(normalized_selector["MeasurementValidationAllowed"])
        and not truthy(normalized_selector["AllowedForRetroactiveMeasurementScoring"])
        else "BLOCKED",
        (
            f"{normalized_selector['StrongestAllowedClaim']}; "
            f"selected equation={normalized_selector['NormalizedSelectorSelectedEquation']}; "
            f"selected constant={normalized_selector['NormalizedSelectorSelectedIsConstant']}; "
            f"selected score={normalized_selector['NormalizedSelectorScore']}; "
            f"weighted MSE={normalized_selector['NormalizedSelectorWeightedMSEOriginal']}; "
            f"future bootstrap allowed={normalized_selector['AllowedForFutureBootstrap']}."
        ),
        "source_native_normalized_selector_boundary",
    )

    normalized_bootstrap_smoke = read_first(FILES["source_native_normalized_criteria3_bootstrap_smoke"])
    add(
        rows,
        "SOURCE_NATIVE_NORMALIZED_CRITERIA3_BOOTSTRAP_SMOKE",
        str(FILES["source_native_normalized_criteria3_bootstrap_smoke"].relative_to(ROOT)),
        "WARNING"
        if str(normalized_bootstrap_smoke["CurrentStatus"])
        == "NORMALIZED_CRITERIA3_BOOTSTRAP_SMOKE_EXECUTED_NOT_FULL_SCALE"
        and not truthy(normalized_bootstrap_smoke["MeasurementValidationAllowed"])
        and not truthy(normalized_bootstrap_smoke["K2KernelChanged"])
        and not truthy(normalized_bootstrap_smoke["RhoGreaterThan4Allowed"])
        and not truthy(normalized_bootstrap_smoke["K1Refit"])
        else "BLOCKED",
        (
            f"{normalized_bootstrap_smoke['StrongestAllowedClaim']}; "
            f"runs={normalized_bootstrap_smoke['BootstrapRuns']}; "
            f"finite runs={normalized_bootstrap_smoke['FiniteRuns']}; "
            f"nonconstant selections={normalized_bootstrap_smoke['NonconstantSelectedRuns']}; "
            f"median complexity={normalized_bootstrap_smoke['MedianSelectedComplexity']}; "
            f"smoke covariance ready={normalized_bootstrap_smoke['SmokeCovarianceReady']}."
        ),
        "source_native_normalized_bootstrap_smoke_boundary",
    )

    normalized_pysr_smoke = read_first(FILES["normalized_pysr_backreaction_smoke"])
    add(
        rows,
        "NORMALIZED_PYSR_BACKREACTION_SMOKE_NULL",
        str(FILES["normalized_pysr_backreaction_smoke"].relative_to(ROOT)),
        "WARNING"
        if str(normalized_pysr_smoke["CurrentStatus"]) == "HYBRID_NORMALIZED_PYSR_BACKREACTION_SMOKE_SCORED"
        and not truthy(normalized_pysr_smoke["MeasurementValidationAllowed"])
        and not truthy(normalized_pysr_smoke["K2KernelChanged"])
        and not truthy(normalized_pysr_smoke["K1Refit"])
        and not truthy(normalized_pysr_smoke["ScaleFitAllowed"])
        else "BLOCKED",
        (
            f"{normalized_pysr_smoke['StrongestAllowedClaim']}; "
            f"K2 beats smoke cases={normalized_pysr_smoke['K2BeatsSmokeBackreactionCases']}/"
            f"{normalized_pysr_smoke['RoutesScored']}; "
            f"median corr smoke-K2={normalized_pysr_smoke['MedianCorrelationSmokeWithK2']}; "
            f"median DeltaChi2 K2-smoke={normalized_pysr_smoke['MedianDeltaChi2_K2_minus_SmokeBackreaction']}; "
            f"D branch source-native={normalized_pysr_smoke['DBranchSourceNative']}."
        ),
        "hybrid_backreaction_smoke_null_boundary",
    )

    d_branch_smoke = read_first(FILES["source_native_normalized_criteria3_d_branch_smoke"])
    add(
        rows,
        "SOURCE_NATIVE_NORMALIZED_CRITERIA3_D_BRANCH_SMOKE",
        str(FILES["source_native_normalized_criteria3_d_branch_smoke"].relative_to(ROOT)),
        "WARNING"
        if str(d_branch_smoke["CurrentStatus"])
        == "NORMALIZED_CRITERIA3_D_BRANCH_BOOTSTRAP_SMOKE_EXECUTED_NOT_FULL_SCALE"
        and not truthy(d_branch_smoke["MeasurementValidationAllowed"])
        and not truthy(d_branch_smoke["K2KernelChanged"])
        and not truthy(d_branch_smoke["K1Refit"])
        else "BLOCKED",
        (
            f"{d_branch_smoke['StrongestAllowedClaim']}; "
            f"binned rows={d_branch_smoke['BinnedTrainingRows']}; "
            f"runs={d_branch_smoke['BootstrapRuns']}; "
            f"finite runs={d_branch_smoke['FiniteRuns']}; "
            f"nonconstant selections={d_branch_smoke['NonconstantSelectedRuns']}; "
            f"median complexity={d_branch_smoke['MedianSelectedComplexity']}."
        ),
        "source_native_d_branch_smoke_boundary",
    )

    full_pysr_smoke = read_first(FILES["full_normalized_pysr_backreaction_smoke"])
    add(
        rows,
        "FULL_NORMALIZED_PYSR_BACKREACTION_SMOKE_NULL",
        str(FILES["full_normalized_pysr_backreaction_smoke"].relative_to(ROOT)),
        "WARNING"
        if str(full_pysr_smoke["CurrentStatus"]) == "FULL_NORMALIZED_PYSR_BACKREACTION_SMOKE_SCORED"
        and not truthy(full_pysr_smoke["MeasurementValidationAllowed"])
        and not truthy(full_pysr_smoke["K2KernelChanged"])
        and not truthy(full_pysr_smoke["K1Refit"])
        and not truthy(full_pysr_smoke["ScaleFitAllowed"])
        else "BLOCKED",
        (
            f"{full_pysr_smoke['StrongestAllowedClaim']}; "
            f"K2 beats smoke cases={full_pysr_smoke['K2BeatsSmokeBackreactionCases']}/"
            f"{full_pysr_smoke['RoutesScored']}; "
            f"median corr smoke-K2={full_pysr_smoke['MedianCorrelationSmokeWithK2']}; "
            f"median DeltaChi2 K2-smoke={full_pysr_smoke['MedianDeltaChi2_K2_minus_SmokeBackreaction']}; "
            f"Omega abs max={full_pysr_smoke['OmegaAbsMax']}."
        ),
        "full_normalized_backreaction_smoke_boundary",
    )

    full_pysr_sensitivity = read_first(FILES["full_normalized_pysr_backreaction_sensitivity"])
    add(
        rows,
        "FULL_NORMALIZED_PYSR_BACKREACTION_SENSITIVITY",
        str(FILES["full_normalized_pysr_backreaction_sensitivity"].relative_to(ROOT)),
        "WARNING"
        if str(full_pysr_sensitivity["CurrentStatus"])
        == "FULL_NORMALIZED_PYSR_BACKREACTION_LOW_DEPTH_DERIVATIVE_SENSITIVITY_WARNING"
        and not truthy(full_pysr_sensitivity["MeasurementValidationAllowed"])
        else "BLOCKED",
        (
            f"{full_pysr_sensitivity['StrongestAllowedClaim']}; "
            f"low-depth Omega abs max={full_pysr_sensitivity['LowDepthOmegaAbsMax']}; "
            f"mid/high Omega abs max={full_pysr_sensitivity['MidHighOmegaAbsMax']}; "
            f"median D2/D1 low={full_pysr_sensitivity['MedianDSecondOverDPrimeLowDepth']}; "
            f"median D2/D1 mid/high={full_pysr_sensitivity['MedianDSecondOverDPrimeMidHigh']}."
        ),
        "full_normalized_backreaction_derivative_sensitivity_boundary",
    )

    derivative_selector = read_first(FILES["d_branch_derivative_regularized_selector"])
    add(
        rows,
        "D_BRANCH_DERIVATIVE_REGULARIZED_SELECTOR",
        str(FILES["d_branch_derivative_regularized_selector"].relative_to(ROOT)),
        "WARNING"
        if str(derivative_selector["CurrentStatus"]) == "D_BRANCH_DERIVATIVE_REGULARIZED_SELECTOR_REGISTERED"
        and not truthy(derivative_selector["MeasurementValidationAllowed"])
        and not truthy(derivative_selector["K2KernelChanged"])
        and not truthy(derivative_selector["K1Refit"])
        and not truthy(derivative_selector["TargetSignGateUsed"])
        else "BLOCKED",
        (
            f"{derivative_selector['StrongestAllowedClaim']}; "
            f"curvature budget={derivative_selector['CurvatureBudget']}; "
            f"lambda={derivative_selector['LambdaRegularization']}; "
            f"status={derivative_selector['CurrentStatus']}."
        ),
        "d_branch_regularized_selector_boundary",
    )

    derivative_smoke = read_first(FILES["d_branch_derivative_regularized_smoke"])
    add(
        rows,
        "D_BRANCH_DERIVATIVE_REGULARIZED_BOOTSTRAP_SMOKE",
        str(FILES["d_branch_derivative_regularized_smoke"].relative_to(ROOT)),
        "WARNING"
        if str(derivative_smoke["CurrentStatus"])
        == "D_BRANCH_DERIVATIVE_REGULARIZED_BOOTSTRAP_SMOKE_EXECUTED_NOT_FULL_SCALE"
        and not truthy(derivative_smoke["MeasurementValidationAllowed"])
        and not truthy(derivative_smoke["K2KernelChanged"])
        and not truthy(derivative_smoke["K1Refit"])
        and not truthy(derivative_smoke["TargetSignGateUsed"])
        else "BLOCKED",
        (
            f"{derivative_smoke['StrongestAllowedClaim']}; "
            f"runs={derivative_smoke['BootstrapRuns']}; "
            f"finite runs={derivative_smoke['FiniteRuns']}; "
            f"median low-depth curvature={derivative_smoke['MedianLowDepthCurvatureMetric']}; "
            f"median mid/high curvature={derivative_smoke['MedianMidHighCurvatureMetric']}."
        ),
        "d_branch_regularized_smoke_boundary",
    )

    derivative_200 = read_first(FILES["d_branch_derivative_regularized_bootstrap_200"])
    add(
        rows,
        "D_BRANCH_DERIVATIVE_REGULARIZED_BOOTSTRAP_200",
        str(FILES["d_branch_derivative_regularized_bootstrap_200"].relative_to(ROOT)),
        "WARNING"
        if str(derivative_200["CurrentStatus"]) == "D_BRANCH_DERIVATIVE_REGULARIZED_BOOTSTRAP_200_EXECUTED"
        and truthy(derivative_200["FullBootstrapScale"])
        and int(derivative_200["FiniteRuns"]) == int(derivative_200["BootstrapRuns"])
        and not truthy(derivative_200["MeasurementValidationAllowed"])
        and not truthy(derivative_200["K2KernelChanged"])
        and not truthy(derivative_200["K1Refit"])
        and not truthy(derivative_200["TargetSignGateUsed"])
        else "BLOCKED",
        (
            f"{derivative_200['StrongestAllowedClaim']}; "
            f"runs={derivative_200['BootstrapRuns']}; "
            f"finite runs={derivative_200['FiniteRuns']}; "
            f"nonconstant selections={derivative_200['NonconstantSelectedRuns']}; "
            f"median low-depth curvature={derivative_200['MedianLowDepthCurvatureMetric']}; "
            f"p95 low-depth curvature={derivative_200['P95LowDepthCurvatureMetric']}; "
            f"next={derivative_200['NextAction']}."
        ),
        "d_branch_regularized_200_scale_boundary",
    )

    h_branch_200 = read_first(FILES["h_branch_normalized_criteria3_bootstrap_200"])
    add(
        rows,
        "H_BRANCH_NORMALIZED_CRITERIA3_BOOTSTRAP_200",
        str(FILES["h_branch_normalized_criteria3_bootstrap_200"].relative_to(ROOT)),
        "WARNING"
        if str(h_branch_200["CurrentStatus"]) == "H_BRANCH_NORMALIZED_CRITERIA3_BOOTSTRAP_200_EXECUTED"
        and truthy(h_branch_200["FullBootstrapScale"])
        and int(h_branch_200["FiniteRuns"]) == int(h_branch_200["BootstrapRuns"])
        and not truthy(h_branch_200["MeasurementValidationAllowed"])
        and not truthy(h_branch_200["K2KernelChanged"])
        and not truthy(h_branch_200["K1Refit"])
        and not truthy(h_branch_200["TargetSignGateUsed"])
        else "BLOCKED",
        (
            f"{h_branch_200['StrongestAllowedClaim']}; "
            f"runs={h_branch_200['BootstrapRuns']}; "
            f"finite runs={h_branch_200['FiniteRuns']}; "
            f"nonconstant selections={h_branch_200['NonconstantSelectedRuns']}; "
            f"median band width={h_branch_200['MedianHDBandWidth']}; "
            f"next={h_branch_200['NextAction']}."
        ),
        "h_branch_normalized_200_scale_boundary",
    )

    regularized_smoke = read_first(FILES["regularized_full_pysr_backreaction_smoke"])
    add(
        rows,
        "REGULARIZED_FULL_PYSR_BACKREACTION_SMOKE_NULL",
        str(FILES["regularized_full_pysr_backreaction_smoke"].relative_to(ROOT)),
        "WARNING"
        if str(regularized_smoke["CurrentStatus"]) == "REGULARIZED_FULL_PYSR_BACKREACTION_SMOKE_SCORED"
        and not truthy(regularized_smoke["MeasurementValidationAllowed"])
        and not truthy(regularized_smoke["K2KernelChanged"])
        and not truthy(regularized_smoke["K1Refit"])
        and not truthy(regularized_smoke["ScaleFitAllowed"])
        else "BLOCKED",
        (
            f"{regularized_smoke['StrongestAllowedClaim']}; "
            f"K2 beats smoke cases={regularized_smoke['K2BeatsSmokeBackreactionCases']}/"
            f"{regularized_smoke['RoutesScored']}; "
            f"median corr smoke-K2={regularized_smoke['MedianCorrelationSmokeWithK2']}; "
            f"median DeltaChi2 K2-smoke={regularized_smoke['MedianDeltaChi2_K2_minus_SmokeBackreaction']}; "
            f"Omega abs max={regularized_smoke['OmegaAbsMax']}."
        ),
        "regularized_full_backreaction_smoke_boundary",
    )

    regularized_sensitivity = read_first(FILES["regularized_full_pysr_backreaction_sensitivity"])
    add(
        rows,
        "REGULARIZED_FULL_PYSR_BACKREACTION_SENSITIVITY",
        str(FILES["regularized_full_pysr_backreaction_sensitivity"].relative_to(ROOT)),
        "WARNING"
        if str(regularized_sensitivity["CurrentStatus"]) == "REGULARIZED_FULL_PYSR_BACKREACTION_SENSITIVITY_AUDITED"
        and not truthy(regularized_sensitivity["MeasurementValidationAllowed"])
        else "BLOCKED",
        (
            f"{regularized_sensitivity['StrongestAllowedClaim']}; "
            f"low-depth Omega abs max={regularized_sensitivity['LowDepthOmegaAbsMax']}; "
            f"mid/high Omega abs max={regularized_sensitivity['MidHighOmegaAbsMax']}; "
            f"median D2/D1 low={regularized_sensitivity['MedianDSecondOverDPrimeLowDepth']}; "
            f"median D2/D1 mid/high={regularized_sensitivity['MedianDSecondOverDPrimeMidHigh']}."
        ),
        "regularized_full_backreaction_derivative_sensitivity_boundary",
    )

    regularized_decision = read_first(FILES["regularized_vs_unregularized_decision"])
    add(
        rows,
        "REGULARIZED_VS_UNREGULARIZED_DECISION_AUDIT",
        str(FILES["regularized_vs_unregularized_decision"].relative_to(ROOT)),
        "WARNING"
        if str(regularized_decision["CurrentStatus"]) == "REGULARIZED_SELECTOR_SCALE_UP_RECOMMENDED"
        and not truthy(regularized_decision["MeasurementValidationAllowed"])
        and truthy(regularized_decision["NoForbiddenChanges"])
        else "BLOCKED",
        (
            f"{regularized_decision['StrongestAllowedClaim']}; "
            f"low-depth Omega reduction ratio={regularized_decision['LowDepthOmegaReductionRatio']}; "
            f"low-depth derivative reduction ratio={regularized_decision['LowDepthDerivativeReductionRatio']}; "
            f"K2 beats regularized smoke={regularized_decision['K2BeatsRegularizedSmokeCases']}/"
            f"{regularized_decision['RoutesScored']}; "
            f"recommendation={regularized_decision['ScaleRecommendation']}."
        ),
        "regularized_selector_scale_decision_boundary",
    )

    regularized_200 = read_first(FILES["regularized_full_pysr_backreaction_200"])
    add(
        rows,
        "REGULARIZED_FULL_PYSR_BACKREACTION_200",
        str(FILES["regularized_full_pysr_backreaction_200"].relative_to(ROOT)),
        "WARNING"
        if str(regularized_200["CurrentStatus"]) == "REGULARIZED_FULL_PYSR_BACKREACTION_200_SCORED"
        and truthy(regularized_200["FullBootstrapScale"])
        and not truthy(regularized_200["MeasurementValidationAllowed"])
        and not truthy(regularized_200["K2KernelChanged"])
        and not truthy(regularized_200["K1Refit"])
        and not truthy(regularized_200["ScaleFitAllowed"])
        else "BLOCKED",
        (
            f"{regularized_200['StrongestAllowedClaim']}; "
            f"samples={regularized_200['OmegaSamples']}; "
            f"K2 beats 200-null={regularized_200['K2BeatsSmokeBackreactionCases']}/"
            f"{regularized_200['RoutesScored']}; "
            f"median corr null-K2={regularized_200['MedianCorrelationSmokeWithK2']}; "
            f"median DeltaChi2 K2-null={regularized_200['MedianDeltaChi2_K2_minus_SmokeBackreaction']}; "
            f"Omega abs max={regularized_200['OmegaAbsMax']}."
        ),
        "regularized_full_200_backreaction_boundary",
    )

    regularized_200_sensitivity = read_first(FILES["regularized_full_pysr_backreaction_200_sensitivity"])
    add(
        rows,
        "REGULARIZED_FULL_PYSR_BACKREACTION_200_SENSITIVITY",
        str(FILES["regularized_full_pysr_backreaction_200_sensitivity"].relative_to(ROOT)),
        "WARNING"
        if str(regularized_200_sensitivity["CurrentStatus"])
        == "REGULARIZED_FULL_PYSR_BACKREACTION_200_SENSITIVITY_AUDITED"
        and not truthy(regularized_200_sensitivity["MeasurementValidationAllowed"])
        else "BLOCKED",
        (
            f"{regularized_200_sensitivity['StrongestAllowedClaim']}; "
            f"low-depth Omega abs max={regularized_200_sensitivity['LowDepthOmegaAbsMax']}; "
            f"mid/high Omega abs max={regularized_200_sensitivity['MidHighOmegaAbsMax']}; "
            f"median D2/D1 low={regularized_200_sensitivity['MedianDSecondOverDPrimeLowDepth']}; "
            f"median D2/D1 mid/high={regularized_200_sensitivity['MedianDSecondOverDPrimeMidHigh']}."
        ),
        "regularized_full_200_sensitivity_boundary",
    )

    dominance_200 = read_first(FILES["regularized_200_null_dominance"])
    add(
        rows,
        "REGULARIZED_200_NULL_DOMINANCE_AUDIT",
        str(FILES["regularized_200_null_dominance"].relative_to(ROOT)),
        "PASS"
        if str(dominance_200["CurrentStatus"]) == "K2_DOMINATES_REGULARIZED_200_NULL_PREFLIGHT"
        and int(dominance_200["K2BeatsRegularizedNullRoutes"]) == int(dominance_200["RoutesScored"])
        and int(dominance_200["K2BeatsRegularizedNullZones"]) == int(dominance_200["Zones"])
        and not truthy(dominance_200["MeasurementValidationAllowed"])
        and not truthy(dominance_200["K2KernelChanged"])
        and not truthy(dominance_200["K1Refit"])
        and not truthy(dominance_200["ScaleFitAllowed"])
        else "WARNING",
        (
            f"{dominance_200['StrongestAllowedClaim']}; "
            f"routes={dominance_200['K2BeatsRegularizedNullRoutes']}/{dominance_200['RoutesScored']}; "
            f"rows={dominance_200['K2BeatsRegularizedNullRows']}/{dominance_200['Rows']}; "
            f"stable rows={dominance_200['StableK2BeatsRegularizedNullRows']}/"
            f"{dominance_200['StableRows']}; "
            f"zones={dominance_200['K2BeatsRegularizedNullZones']}/{dominance_200['Zones']}; "
            f"median DeltaChi2 K2-null={dominance_200['MedianDeltaChi2_K2_minus_RegularizedNull_Route']}."
        ),
        "regularized_200_null_dominance_boundary",
    )

    after_200_blocker = read_first(FILES["source_native_after_200_blocker"])
    add(
        rows,
        "SOURCE_NATIVE_AFTER_200_BLOCKER_AUDIT",
        str(FILES["source_native_after_200_blocker"].relative_to(ROOT)),
        "WARNING"
        if str(after_200_blocker["CurrentStatus"]) == "SOURCE_NATIVE_BLOCKED_AFTER_200_PROXY_PREFLIGHT"
        and truthy(after_200_blocker["DBranch200Ready"])
        and truthy(after_200_blocker["HBranch200Ready"])
        and truthy(after_200_blocker["FullProxy200Ready"])
        and truthy(after_200_blocker["K2DominatesProxy200"])
        and not truthy(after_200_blocker["MeasurementValidationAllowed"])
        else "BLOCKED",
        (
            f"{after_200_blocker['StrongestAllowedClaim']}; "
            f"available required tasks={after_200_blocker['AvailableRequiredTasks']}/"
            f"{after_200_blocker['RequiredTasks']}; "
            f"blocking tasks={after_200_blocker['BlockingTaskIDs']}; "
            f"source-native exports ready={after_200_blocker['SourceNativeExportsReady']}; "
            f"source-native uncertainty ready={after_200_blocker['SourceNativeUncertaintyReady']}."
        ),
        "source_native_after_200_blocker_boundary",
    )

    schema_dry_run = read_first(FILES["source_native_schema_dry_run"])
    add(
        rows,
        "SOURCE_NATIVE_SCHEMA_DRY_RUN",
        str(FILES["source_native_schema_dry_run"].relative_to(ROOT)),
        "PASS"
        if str(schema_dry_run["CurrentStatus"]) == "SOURCE_NATIVE_SCHEMA_DRY_RUN_READY_PROXY_NOT_SOURCE_NATIVE"
        and int(schema_dry_run["SchemaObjectsValid"]) == int(schema_dry_run["SchemaObjectsTotal"])
        and truthy(schema_dry_run["ProxyDryRun"])
        and not truthy(schema_dry_run["SourceNativeScoringReady"])
        and not truthy(schema_dry_run["MeasurementValidationAllowed"])
        else "WARNING",
        (
            f"{schema_dry_run['StrongestAllowedClaim']}; "
            f"schema objects={schema_dry_run['SchemaObjectsValid']}/"
            f"{schema_dry_run['SchemaObjectsTotal']}; "
            f"bootstrap samples={schema_dry_run['BootstrapSamples']}; "
            f"cov min eig={schema_dry_run['CovarianceMinEigenvalue']}; "
            f"source-native scoring ready={schema_dry_run['SourceNativeScoringReady']}."
        ),
        "source_native_schema_dry_run_boundary",
    )

    reproduction_candidate = read_first(FILES["source_native_reproduction_candidate"])
    add(
        rows,
        "SOURCE_NATIVE_REPRODUCTION_CANDIDATE_EXPORT",
        str(FILES["source_native_reproduction_candidate"].relative_to(ROOT)),
        "PASS"
        if str(reproduction_candidate["CurrentStatus"])
        == "REPRODUCTION_CANDIDATE_EXPORTS_READY_NOT_AUTHOR_SOURCE_NATIVE"
        and truthy(reproduction_candidate["ReproductionCandidate"])
        and not truthy(reproduction_candidate["AuthorExport"])
        and not truthy(reproduction_candidate["SourceNativeScoringReady"])
        and not truthy(reproduction_candidate["MeasurementValidationAllowed"])
        else "WARNING",
        (
            f"{reproduction_candidate['StrongestAllowedClaim']}; "
            f"rows={reproduction_candidate['ReconstructionRows']}; "
            f"bootstrap samples={reproduction_candidate['BootstrapSamples']}; "
            f"cov min eig={reproduction_candidate['CovarianceMinEigenvalue']}; "
            f"author export={reproduction_candidate['AuthorExport']}."
        ),
        "source_native_reproduction_candidate_boundary",
    )

    reproduction_bridge = read_first(FILES["source_native_reproduction_candidate_bridge"])
    add(
        rows,
        "SOURCE_NATIVE_REPRODUCTION_CANDIDATE_BRIDGE",
        str(FILES["source_native_reproduction_candidate_bridge"].relative_to(ROOT)),
        "WARNING"
        if str(reproduction_bridge["CurrentStatus"])
        == "REPRODUCTION_CANDIDATE_BRIDGE_SCORED_SOURCE_NATIVE_STILL_BLOCKED"
        and int(reproduction_bridge["K2BeatsCandidateBackreactionCases"])
        == int(reproduction_bridge["RouteFamilyCases"])
        and not truthy(reproduction_bridge["AuthorExport"])
        and not truthy(reproduction_bridge["SourceNativeBridgeScoringReady"])
        and not truthy(reproduction_bridge["MeasurementValidationAllowed"])
        else "BLOCKED",
        (
            f"{reproduction_bridge['StrongestAllowedClaim']}; "
            f"K2 beats candidate={reproduction_bridge['K2BeatsCandidateBackreactionCases']}/"
            f"{reproduction_bridge['RouteFamilyCases']}; "
            f"median corr candidate-K2={reproduction_bridge['MedianCorrelationCandidateWithK2']}; "
            f"median DeltaChi2 K2-candidate="
            f"{reproduction_bridge['MedianDeltaChi2_K2_minus_CandidateBackreaction']}."
        ),
        "source_native_reproduction_candidate_bridge_boundary",
    )

    reproduction_dominance = read_first(FILES["source_native_reproduction_candidate_dominance"])
    add(
        rows,
        "SOURCE_NATIVE_REPRODUCTION_CANDIDATE_DOMINANCE",
        str(FILES["source_native_reproduction_candidate_dominance"].relative_to(ROOT)),
        "PASS"
        if str(reproduction_dominance["CurrentStatus"]) == "K2_DOMINATES_REPRODUCTION_CANDIDATE_PREFLIGHT"
        and int(reproduction_dominance["K2BeatsCandidateRoutes"]) == int(reproduction_dominance["RoutesScored"])
        and int(reproduction_dominance["K2BeatsCandidateZones"]) == int(reproduction_dominance["Zones"])
        and not truthy(reproduction_dominance["MeasurementValidationAllowed"])
        and not truthy(reproduction_dominance["K2KernelChanged"])
        and not truthy(reproduction_dominance["K1Refit"])
        and not truthy(reproduction_dominance["ScaleFitAllowed"])
        else "WARNING",
        (
            f"{reproduction_dominance['StrongestAllowedClaim']}; "
            f"routes={reproduction_dominance['K2BeatsCandidateRoutes']}/"
            f"{reproduction_dominance['RoutesScored']}; "
            f"rows={reproduction_dominance['K2BeatsCandidateRows']}/{reproduction_dominance['Rows']}; "
            f"stable rows={reproduction_dominance['StableK2BeatsCandidateRows']}/"
            f"{reproduction_dominance['StableRows']}; "
            f"zones={reproduction_dominance['K2BeatsCandidateZones']}/{reproduction_dominance['Zones']}; "
            f"median DeltaChi2 K2-candidate="
            f"{reproduction_dominance['MedianDeltaChi2_K2_minus_Candidate_Route']}."
        ),
        "source_native_reproduction_candidate_dominance_boundary",
    )

    reproduction_family = read_first(FILES["source_native_reproduction_family"])
    add(
        rows,
        "SOURCE_NATIVE_REPRODUCTION_FAMILY_EXPORT",
        str(FILES["source_native_reproduction_family"].relative_to(ROOT)),
        "PASS"
        if str(reproduction_family["CurrentStatus"])
        == "LOCAL_REPRODUCTION_FAMILY_EXPORTS_READY_NOT_AUTHOR_SOURCE_NATIVE"
        and truthy(reproduction_family["ReproductionFamily"])
        and not truthy(reproduction_family["AuthorExport"])
        and not truthy(reproduction_family["SourceNativeScoringReady"])
        and not truthy(reproduction_family["MeasurementValidationAllowed"])
        else "WARNING",
        (
            f"{reproduction_family['StrongestAllowedClaim']}; "
            f"families={reproduction_family['Families']}; "
            f"sample range={reproduction_family['MinBootstrapSamplesPerFamily']}.."
            f"{reproduction_family['MaxBootstrapSamplesPerFamily']}; "
            f"omega rows={reproduction_family['OmegaRows']}; "
            f"omega bootstrap rows={reproduction_family['OmegaBootstrapRows']}; "
            f"omega abs max={reproduction_family['OmegaAbsMax']}."
        ),
        "source_native_reproduction_family_boundary",
    )

    reproduction_family_bridge = read_first(FILES["source_native_reproduction_family_bridge"])
    add(
        rows,
        "SOURCE_NATIVE_REPRODUCTION_FAMILY_BRIDGE",
        str(FILES["source_native_reproduction_family_bridge"].relative_to(ROOT)),
        "WARNING"
        if str(reproduction_family_bridge["CurrentStatus"])
        == "REPRODUCTION_FAMILY_BRIDGE_SCORED_SOURCE_NATIVE_STILL_BLOCKED"
        and int(reproduction_family_bridge["K2BeatsFamilyBackreactionCases"])
        == int(reproduction_family_bridge["RouteFamilyCases"])
        and not truthy(reproduction_family_bridge["AuthorExport"])
        and not truthy(reproduction_family_bridge["SourceNativeBridgeScoringReady"])
        and not truthy(reproduction_family_bridge["MeasurementValidationAllowed"])
        else "BLOCKED",
        (
            f"{reproduction_family_bridge['StrongestAllowedClaim']}; "
            f"K2 beats families={reproduction_family_bridge['K2BeatsFamilyBackreactionCases']}/"
            f"{reproduction_family_bridge['RouteFamilyCases']}; "
            f"best family={reproduction_family_bridge['BestFamilyByMeanChi2']}; "
            f"median corr family-K2={reproduction_family_bridge['MedianCorrelationFamilyWithK2']}; "
            f"median DeltaChi2 K2-family="
            f"{reproduction_family_bridge['MedianDeltaChi2_K2_minus_FamilyBackreaction']}."
        ),
        "source_native_reproduction_family_bridge_boundary",
    )

    reproduction_family_dominance = read_first(FILES["source_native_reproduction_family_dominance"])
    add(
        rows,
        "SOURCE_NATIVE_REPRODUCTION_FAMILY_DOMINANCE",
        str(FILES["source_native_reproduction_family_dominance"].relative_to(ROOT)),
        "PASS"
        if str(reproduction_family_dominance["CurrentStatus"])
        == "K2_DOMINATES_LOCAL_REPRODUCTION_FAMILIES_PREFLIGHT"
        and int(reproduction_family_dominance["K2BeatsFamilyRouteCases"])
        == int(reproduction_family_dominance["RouteFamilyCases"])
        and int(reproduction_family_dominance["K2BeatsFamilyZones"])
        == int(reproduction_family_dominance["Zones"])
        and not truthy(reproduction_family_dominance["MeasurementValidationAllowed"])
        and not truthy(reproduction_family_dominance["K2KernelChanged"])
        and not truthy(reproduction_family_dominance["K1Refit"])
        and not truthy(reproduction_family_dominance["ScaleFitAllowed"])
        else "WARNING",
        (
            f"{reproduction_family_dominance['StrongestAllowedClaim']}; "
            f"route-family cases={reproduction_family_dominance['K2BeatsFamilyRouteCases']}/"
            f"{reproduction_family_dominance['RouteFamilyCases']}; "
            f"rows={reproduction_family_dominance['K2BeatsFamilyRows']}/"
            f"{reproduction_family_dominance['Rows']}; "
            f"stable rows={reproduction_family_dominance['StableK2BeatsFamilyRows']}/"
            f"{reproduction_family_dominance['StableRows']}; "
            f"zones={reproduction_family_dominance['K2BeatsFamilyZones']}/"
            f"{reproduction_family_dominance['Zones']}; "
            f"median DeltaChi2 K2-family="
            f"{reproduction_family_dominance['MedianDeltaChi2_K2_minus_Family_Route']}."
        ),
        "source_native_reproduction_family_dominance_boundary",
    )

    author_protocol = read_first(FILES["author_protocol_guided_reproduction"])
    add(
        rows,
        "AUTHOR_PROTOCOL_GUIDED_REPRODUCTION",
        str(FILES["author_protocol_guided_reproduction"].relative_to(ROOT)),
        "PASS"
        if str(author_protocol["CurrentStatus"]) == "AUTHOR_PROTOCOL_GUIDED_LOCAL_REPRODUCTION_READY"
        and truthy(author_protocol["PublishedProtocolBasisAvailable"])
        and not truthy(author_protocol["AuthorExport"])
        and not truthy(author_protocol["ExactAuthorNative"])
        and not truthy(author_protocol["MeasurementValidationAllowed"])
        else "WARNING",
        (
            f"{author_protocol['StrongestAllowedClaim']}; "
            f"registered families={author_protocol['RegisteredFamilies']}; "
            f"used families={author_protocol['UsedFamilies']}; "
            f"blocked protocol families={author_protocol['BlockedProtocolFamilies']}; "
            f"sample range={author_protocol['MinBootstrapSamplesPerFamily']}.."
            f"{author_protocol['MaxBootstrapSamplesPerFamily']}; "
            f"omega abs max={author_protocol['OmegaAbsMax']}."
        ),
        "author_protocol_guided_reproduction_boundary",
    )

    author_bridge = read_first(FILES["author_protocol_guided_bridge"])
    add(
        rows,
        "AUTHOR_PROTOCOL_GUIDED_BRIDGE",
        str(FILES["author_protocol_guided_bridge"].relative_to(ROOT)),
        "WARNING"
        if str(author_bridge["CurrentStatus"]) == "AUTHOR_PROTOCOL_GUIDED_BRIDGE_SCORED_EXACT_AUTHOR_NATIVE_BLOCKED"
        and int(author_bridge["K2BeatsFamilyBackreactionCases"]) == int(author_bridge["RouteFamilyCases"])
        and not truthy(author_bridge["AuthorExport"])
        and not truthy(author_bridge["ExactAuthorNative"])
        and not truthy(author_bridge["MeasurementValidationAllowed"])
        else "BLOCKED",
        (
            f"{author_bridge['StrongestAllowedClaim']}; "
            f"K2 beats protocol-guided families={author_bridge['K2BeatsFamilyBackreactionCases']}/"
            f"{author_bridge['RouteFamilyCases']}; "
            f"best family={author_bridge['BestFamilyByMeanChi2']}; "
            f"median corr family-K2={author_bridge['MedianCorrelationFamilyWithK2']}; "
            f"median DeltaChi2 K2-family={author_bridge['MedianDeltaChi2_K2_minus_FamilyBackreaction']}."
        ),
        "author_protocol_guided_bridge_boundary",
    )

    author_dominance = read_first(FILES["author_protocol_guided_dominance"])
    add(
        rows,
        "AUTHOR_PROTOCOL_GUIDED_DOMINANCE",
        str(FILES["author_protocol_guided_dominance"].relative_to(ROOT)),
        "PASS"
        if str(author_dominance["CurrentStatus"]) == "K2_DOMINATES_AUTHOR_PROTOCOL_GUIDED_FAMILIES_PREFLIGHT"
        and int(author_dominance["K2BeatsFamilyRouteCases"]) == int(author_dominance["RouteFamilyCases"])
        and int(author_dominance["K2BeatsFamilyZones"]) == int(author_dominance["Zones"])
        and not truthy(author_dominance["MeasurementValidationAllowed"])
        and not truthy(author_dominance["K2KernelChanged"])
        and not truthy(author_dominance["K1Refit"])
        and not truthy(author_dominance["ScaleFitAllowed"])
        else "WARNING",
        (
            f"{author_dominance['StrongestAllowedClaim']}; "
            f"route-family cases={author_dominance['K2BeatsFamilyRouteCases']}/"
            f"{author_dominance['RouteFamilyCases']}; "
            f"rows={author_dominance['K2BeatsFamilyRows']}/{author_dominance['Rows']}; "
            f"stable rows={author_dominance['StableK2BeatsFamilyRows']}/{author_dominance['StableRows']}; "
            f"zones={author_dominance['K2BeatsFamilyZones']}/{author_dominance['Zones']}; "
            f"median DeltaChi2 K2-family={author_dominance['MedianDeltaChi2_K2_minus_Family_Route']}."
        ),
        "author_protocol_guided_dominance_boundary",
    )

    route_adjudication = read_first(FILES["backreaction_route_adjudication"])
    add(
        rows,
        "BACKREACTION_ROUTE_ADJUDICATION",
        str(FILES["backreaction_route_adjudication"].relative_to(ROOT)),
        "WARNING",
        (
            f"{route_adjudication['StrongestAllowedClaim']}; "
            f"mid/high range={route_adjudication['MinMidHighComponentFraction']}.."
            f"{route_adjudication['MaxMidHighComponentFraction']}; "
            f"high range={route_adjudication['MinHighComponentFraction']}.."
            f"{route_adjudication['MaxHighComponentFraction']}; "
            f"pilot low={route_adjudication['PilotLowComponentFraction']}; "
            f"status={route_adjudication['CurrentStatus']}."
        ),
        "backreaction_route_adjudication_boundary",
    )

    source_native_tasks = read_first(FILES["source_native_reproduction_tasks"])
    add(
        rows,
        "SOURCE_NATIVE_REPRODUCTION_TASK_QUEUE",
        str(FILES["source_native_reproduction_tasks"].relative_to(ROOT)),
        "WARNING" if not truthy(source_native_tasks["SourceNativeScoringReady"]) else "PASS",
        (
            f"{source_native_tasks['StrongestAllowedClaim']}; "
            f"available tasks={source_native_tasks['AvailableRequiredTasks']}/{source_native_tasks['RequiredTasks']}; "
            f"blocking tasks={source_native_tasks['BlockingTasks']}; "
            f"status={source_native_tasks['CurrentStatus']}."
        ),
        "source_native_reproduction_task_boundary",
    )

    poly = pd.read_csv(FILES["polynomial_tension"])
    current = poly[poly["DiagnosisID"].eq("CURRENT_DECISION")].iloc[0]
    add(
        rows,
        "POLYNOMIAL_TENSION_BOUNDARY",
        str(FILES["polynomial_tension"].relative_to(ROOT)),
        "WARNING",
        f"{current['Finding']} Measurement impact: {current['MeasurementValidationImpact']}.",
        "residual_risk",
    )

    return rows


def write_doc(packet: pd.DataFrame, summary: pd.Series) -> None:
    DOCS.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Tau Core A2 Preflight Proof Packet",
        "",
        "Status: preflight support packet; no measurement-validation claim.",
        "",
        "## Summary",
        "",
        f"- Passed gates: {summary['PassedGates']}/{summary['TotalGates']}",
        f"- Warning gates: {summary['WarningGates']}",
        f"- Blocked gates: {summary['BlockedGates']}",
        f"- Preflight critical blocked gates: {summary['PreflightCriticalBlockedGates']}",
        f"- Measurement boundary blocked: {summary['MeasurementGateBlocked']}",
        f"- Strongest allowed claim: {summary['StrongestAllowedClaim']}",
        f"- Disallowed claim: {summary['DisallowedClaim']}",
        "",
        "## Gate Findings",
        "",
    ]
    for _, row in packet.iterrows():
        lines.extend(
            [
                f"### {row['GateID']}",
                "",
                f"- Status: {row['Status']}",
                f"- Role: {row['RoleInProofChain']}",
                f"- Evidence: `{row['EvidenceFile']}`",
                f"- Finding: {row['Finding']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Claim Boundary",
            "",
            "This packet supports a locked memory-active preflight interpretation of A2.",
            "It keeps measurement-validation language closed for Tau Core, A_tau=2, and finite-memory claims.",
            "",
        ]
    )
    OUT_DOC.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    packet = pd.DataFrame(build_rows())
    packet.to_csv(OUT_PACKET, index=False)

    passed = int(packet["Status"].eq("PASS").sum())
    warnings = int(packet["Status"].eq("WARNING").sum())
    blocked = int(packet["Status"].eq("BLOCKED").sum())
    measurement_blocked = packet["Status"].eq("BLOCKED") & packet["RoleInProofChain"].eq("measurement_boundary")
    preflight_critical_blocked = packet["Status"].eq("BLOCKED") & ~packet["RoleInProofChain"].eq("measurement_boundary")
    if bool(measurement_blocked.any()):
        primary_risk = "full measurement gate still requires SN and BAO likelihood-native transforms; all-depth polynomial tension remains"
        next_action = "promote SN/BAO likelihood-native transforms and rerun locked A2 packet unchanged"
    else:
        primary_risk = (
            "likelihood-native preflight rerun and independently calibrated branch-scatter preflight bridge are operational, but "
            "whitened covariance routes remove the K1 no-memory advantage while in-sample all-depth polynomial tension requires small-sample/out-of-sample interpretation, and "
            "externally sourced optical alpha controls remain too weak while the backreaction source route is identified but lacks a machine-readable numeric constraint table"
        )
        next_action = (
            "obtain or reproduce the upstream D_A,H_D derivative reconstruction table and attach source-native covariance; keep locked A2 unchanged"
        )
    total = len(packet)
    summary = pd.DataFrame(
        [
            {
                "PacketID": "TAU_CORE_A2_PREFLIGHT_PROOF_PACKET_V1",
                "TotalGates": total,
                "PassedGates": passed,
                "WarningGates": warnings,
                "BlockedGates": blocked,
                "ExpectedMeasurementBoundaryGates": int(measurement_blocked.sum()),
                "PreflightCriticalBlockedGates": int(preflight_critical_blocked.sum()),
                "PreflightSupportPacketComplete": int(preflight_critical_blocked.sum()) == 0,
                "MeasurementGateBlocked": bool(measurement_blocked.any()),
                "MeasurementValidationAllowed": False,
        "StrongestAllowedClaim": "Tau Core A2 has strong preflight support for locked low-depth operator suppression and a stable mid/high memory-active component",
                "DisallowedClaim": "measurement validation is not authorized",
                "PrimaryResidualRisk": primary_risk,
                "NextAction": next_action,
                "ClaimBoundary": "tau_core_a2_preflight_packet_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)
    write_doc(packet, summary.iloc[0])
    print(f"Wrote {OUT_PACKET}")
    print(f"Wrote {OUT_SUMMARY}")
    print(f"Wrote {OUT_DOC}")


if __name__ == "__main__":
    main()
