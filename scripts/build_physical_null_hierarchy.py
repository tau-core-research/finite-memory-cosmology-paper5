#!/usr/bin/env python3
"""Build a physical null-comparator hierarchy after the polynomial audit."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

NULL_REGISTRY = ROOT / "evidence" / "null_model_registry.csv"
POLY_FAIRNESS = ROOT / "evidence" / "polynomial_control_fairness_summary.csv"
PHYSICAL_TEMPLATE_READINESS = ROOT / "evidence" / "physical_null_proxy_template_readiness.csv"
PHYSICAL_AMP_READINESS = ROOT / "evidence" / "physical_null_amplitude_policy_readiness.csv"
OUT_HIERARCHY = ROOT / "evidence" / "physical_null_hierarchy.csv"
OUT_READINESS = ROOT / "evidence" / "physical_null_hierarchy_readiness.csv"


def main() -> None:
    registry = pd.read_csv(NULL_REGISTRY)
    fairness = pd.read_csv(POLY_FAIRNESS).iloc[0]
    template_ready = (
        pd.read_csv(PHYSICAL_TEMPLATE_READINESS).iloc[0]
        if PHYSICAL_TEMPLATE_READINESS.exists()
        else None
    )
    amp_ready = (
        pd.read_csv(PHYSICAL_AMP_READINESS).iloc[0]
        if PHYSICAL_AMP_READINESS.exists()
        else None
    )
    backreaction_status = "registered_not_implemented"
    optical_status = "registered_not_implemented"
    if template_ready is not None and str(template_ready.get("BackreactionTemplateAvailable", "")).lower() == "true":
        backreaction_status = "template_available_not_scoring"
    if template_ready is not None and str(template_ready.get("DyerRoederOpticalTemplateAvailable", "")).lower() == "true":
        optical_status = "template_available_not_scoring"
    if amp_ready is not None and str(amp_ready.get("AmplitudePolicyDeclared", "")).lower() == "true":
        if backreaction_status == "template_available_not_scoring":
            backreaction_status = "preflight_scoring_policy_available"
        if optical_status == "template_available_not_scoring":
            optical_status = "preflight_scoring_policy_available"

    roles = {
        "LCDM_NO_MEMORY": {
            "HierarchyLevel": 1,
            "ComparatorClass": "primary_fair_null",
            "MeasurementRole": "minimum_required_baseline",
            "CanExplainPhysically": True,
            "CanBlockMeasurementClaim": True,
            "RequiredForNextBenchmark": True,
            "ImplementationStatus": "implemented_as_K1_NO_MEMORY",
            "NextAction": "keep as mandatory baseline in every scorecard",
        },
        "BACKREACTION_ONLY": {
            "HierarchyLevel": 2,
            "ComparatorClass": "physical_null",
            "MeasurementRole": "cosmological_averaging_control",
            "CanExplainPhysically": True,
            "CanBlockMeasurementClaim": True,
            "RequiredForNextBenchmark": True,
            "ImplementationStatus": backreaction_status,
            "NextAction": "run only as sanity/sensitivity comparator until physical amplitude calibration exists",
        },
        "DYER_ROEDER_OPTICAL": {
            "HierarchyLevel": 3,
            "ComparatorClass": "physical_null",
            "MeasurementRole": "optical_propagation_control",
            "CanExplainPhysically": True,
            "CanBlockMeasurementClaim": True,
            "RequiredForNextBenchmark": True,
            "ImplementationStatus": optical_status,
            "NextAction": "run only as sanity/sensitivity comparator until optical amplitude calibration exists",
        },
        "RECONSTRUCTION_ARTIFACT": {
            "HierarchyLevel": 4,
            "ComparatorClass": "diagnostic_control",
            "MeasurementRole": "pipeline_sensitivity_control",
            "CanExplainPhysically": False,
            "CanBlockMeasurementClaim": True,
            "RequiredForNextBenchmark": True,
            "ImplementationStatus": "partially_implemented_sign_family",
            "NextAction": "connect to public reconstruction-family sign and amplitude export",
        },
        "GENERIC_POLYNOMIAL_SMOOTHING": {
            "HierarchyLevel": 5,
            "ComparatorClass": "overfit_risk_control",
            "MeasurementRole": "generic_flexibility_blocker",
            "CanExplainPhysically": False,
            "CanBlockMeasurementClaim": True,
            "RequiredForNextBenchmark": True,
            "ImplementationStatus": "implemented_and_blocks_current_measurement_claim",
            "NextAction": "keep mandatory; report in-sample and CV results",
        },
        "SIGN_RANDOMIZED_CONTROL": {
            "HierarchyLevel": 6,
            "ComparatorClass": "negative_control",
            "MeasurementRole": "accidental_sign_control",
            "CanExplainPhysically": False,
            "CanBlockMeasurementClaim": False,
            "RequiredForNextBenchmark": True,
            "ImplementationStatus": "registered_not_currently_scored_in_source_split_route",
            "NextAction": "score only as sanity control after sign-family table is public",
        },
        "COORDINATE_REMAP_CONTROL": {
            "HierarchyLevel": 7,
            "ComparatorClass": "coordinate_control",
            "MeasurementRole": "post_hoc_mapping_guard",
            "CanExplainPhysically": False,
            "CanBlockMeasurementClaim": True,
            "RequiredForNextBenchmark": True,
            "ImplementationStatus": "implemented_in_coordinate_robustness_mvp",
            "NextAction": "keep all predeclared mappings visible in future benchmark",
        },
    }

    rows = []
    for _, row in registry.iterrows():
        null_id = row["NullID"]
        meta = roles.get(null_id)
        if meta is None:
            continue
        rows.append(
            {
                "NullID": null_id,
                "Name": row["Name"],
                "OriginalNullCategory": row["NullCategory"],
                "HierarchyLevel": meta["HierarchyLevel"],
                "ComparatorClass": meta["ComparatorClass"],
                "MeasurementRole": meta["MeasurementRole"],
                "FreeParameters": row["FreeParameters"],
                "CanExplainPhysically": meta["CanExplainPhysically"],
                "CanBlockMeasurementClaim": meta["CanBlockMeasurementClaim"],
                "RequiredForNextBenchmark": meta["RequiredForNextBenchmark"],
                "ImplementationStatus": meta["ImplementationStatus"],
                "NextAction": meta["NextAction"],
                "ClaimBoundary": "physical_null_hierarchy_no_measurement_validation",
            }
        )
    hierarchy = pd.DataFrame(rows).sort_values("HierarchyLevel")
    hierarchy.to_csv(OUT_HIERARCHY, index=False)

    required = hierarchy[hierarchy["RequiredForNextBenchmark"].astype(bool)]
    implemented_statuses = {
        "implemented_as_K1_NO_MEMORY",
        "implemented_and_blocks_current_measurement_claim",
        "implemented_in_coordinate_robustness_mvp",
        "partially_implemented_sign_family",
    }
    template_statuses = implemented_statuses | {
        "template_available_not_scoring",
        "preflight_scoring_policy_available",
    }
    implemented = required[required["ImplementationStatus"].isin(implemented_statuses)]
    implemented_or_template = required[required["ImplementationStatus"].isin(template_statuses)]
    physical_required = hierarchy[
        hierarchy["CanExplainPhysically"].astype(bool) & hierarchy["RequiredForNextBenchmark"].astype(bool)
    ]
    physical_implemented = physical_required[physical_required["ImplementationStatus"].isin(implemented_statuses)]
    physical_templates = physical_required[physical_required["ImplementationStatus"].eq("template_available_not_scoring")]
    physical_preflight = physical_required[
        physical_required["ImplementationStatus"].eq("preflight_scoring_policy_available")
    ]
    summary = pd.DataFrame(
        [
            {
                "HierarchyID": "PHYSICAL_NULL_HIERARCHY_V1",
                "RegisteredNulls": len(hierarchy),
                "RequiredForNextBenchmark": len(required),
                "RequiredImplementedOrPartial": len(implemented),
                "RequiredImplementedOrTemplate": len(implemented_or_template),
                "PhysicalNullsRequired": len(physical_required),
                "PhysicalNullsScoringReady": len(physical_implemented),
                "PhysicalNullTemplatesAvailable": len(physical_templates),
                "PhysicalNullPreflightScoringPolicyAvailable": len(physical_preflight),
                "PolynomialControlRole": fairness["PolynomialControlRole"],
                "PolynomialCanBeDismissed": fairness["PolynomialCanBeDismissed"],
                "PolynomialCanExplainPhysically": False,
                "MeasurementClaimReady": False,
                "PrimaryBlockingIssue": "physical_null_amplitudes_not_physically_calibrated",
                "NextAction": "run physical null preflight scorecard only as sanity/sensitivity comparator, then seek physical amplitude calibration before stronger claims",
                "Interpretation": "physical nulls have preflight scoring policy but are not measurement-calibrated; polynomial remains mandatory overfit blocker",
                "ClaimBoundary": "physical_null_hierarchy_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(OUT_READINESS, index=False)
    print(f"Wrote {OUT_HIERARCHY}")
    print(f"Wrote {OUT_READINESS}")


if __name__ == "__main__":
    main()
