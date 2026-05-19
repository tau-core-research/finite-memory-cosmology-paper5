#!/usr/bin/env python3
"""Close the current A2 measurement-route audit without overclaiming.

This separates preflight closure from measurement validation. Several artifacts
are now usable for preflight scoring, but the public covariance route remains
blocked for measurement-grade interpretation by polynomial dominance under the
public proxy and by the lack of a full likelihood-native joint SN+BAO transform.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DATA = ROOT / "data"
DOCS = ROOT / "docs"

TRANSFORM_READINESS = EVIDENCE / "k2_a2_transform_matrix_readiness_v1.csv"
PUBLIC_COV = EVIDENCE / "full_public_covariance_transform_summary.csv"
SUPPORT = EVIDENCE / "source_split_likelihood_native_support_ladder_summary.csv"
POLY = EVIDENCE / "k2_a2_polynomial_tension_diagnosis.csv"
BRANCH_CAL = EVIDENCE / "branch_scatter_independent_calibration_summary.csv"
ROUTE = EVIDENCE / "tau_core_a2_route_decision_summary.csv"
K1 = DATA / "k1" / "source_split_external_k1_response.csv"
K2 = DATA / "predictions" / "k2_source_split_a2_prior_v1.csv"
NULLS = EVIDENCE / "null_model_registry.csv"

OUT = EVIDENCE / "measurement_route_closure_audit.csv"
SUMMARY = EVIDENCE / "measurement_route_closure_summary.csv"
DOC = DOCS / "measurement_route_closure_audit.md"


def truthy(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def first(path: Path) -> pd.Series:
    df = pd.read_csv(path)
    if df.empty:
        raise ValueError(f"empty evidence file: {path}")
    return df.iloc[0]


def main() -> None:
    transform = first(TRANSFORM_READINESS)
    public_cov = first(PUBLIC_COV)
    support = first(SUPPORT)
    branch_cal = first(BRANCH_CAL)
    route = first(ROUTE)
    poly = pd.read_csv(POLY)
    current_decision = poly[poly["DiagnosisID"].eq("CURRENT_DECISION")].iloc[0]
    poly_fairness = poly[poly["DiagnosisID"].eq("POLYNOMIAL_FAIRNESS")].iloc[0]

    rows = [
        {
            "ClosureID": "MRC_1_LOCKED_A2_AVAILABLE",
            "PreflightStatus": "PASS" if K2.exists() else "BLOCKED",
            "MeasurementStatus": "PASS" if K2.exists() else "BLOCKED",
            "Evidence": str(K2.relative_to(ROOT)),
            "Interpretation": "locked A2 prediction is available and unchanged",
            "BlocksMeasurementValidation": False,
        },
        {
            "ClosureID": "MRC_2_TRANSFORM_MATRICES",
            "PreflightStatus": "PASS" if truthy(transform["TransformMatricesFrozen"]) else "BLOCKED",
            "MeasurementStatus": "WARNING",
            "Evidence": (
                f"L_SN exported={transform['LSNExported']}; L_BAO exported={transform['LBAOExported']}; "
                f"status={transform['CurrentStatus']}"
            ),
            "Interpretation": "transform matrices are frozen for preflight but not promoted to full likelihood-native measurement route",
            "BlocksMeasurementValidation": True,
        },
        {
            "ClosureID": "MRC_3_PUBLIC_COVARIANCE_INPUTS",
            "PreflightStatus": "PASS" if truthy(public_cov["ZeroCrossCovariancePreflightUsable"]) else "BLOCKED",
            "MeasurementStatus": "WARNING",
            "Evidence": (
                f"raw SN={public_cov['RawPublicSNCovarianceAvailable']}; raw BAO={public_cov['RawPublicBAOCovarianceAvailable']}; "
                f"zero-cross usable={public_cov['ZeroCrossCovariancePreflightUsable']}"
            ),
            "Interpretation": "public covariance inputs are propagatable, but the public route is still a proxy",
            "BlocksMeasurementValidation": True,
        },
        {
            "ClosureID": "MRC_4_K1_BASELINE",
            "PreflightStatus": "PASS" if K1.exists() else "BLOCKED",
            "MeasurementStatus": "WARNING",
            "Evidence": str(K1.relative_to(ROOT)),
            "Interpretation": "K1 is available for preflight scoring, but measurement-grade K1 still depends on the same full transform/covariance policy",
            "BlocksMeasurementValidation": True,
        },
        {
            "ClosureID": "MRC_5_NULL_POLICY",
            "PreflightStatus": "PASS" if NULLS.exists() else "BLOCKED",
            "MeasurementStatus": "WARNING",
            "Evidence": str(NULLS.relative_to(ROOT)),
            "Interpretation": "MVP null registry exists, but full-gate null policy must be frozen under the final covariance route",
            "BlocksMeasurementValidation": True,
        },
        {
            "ClosureID": "MRC_6_K2_VS_K1",
            "PreflightStatus": "PASS" if str(support["K2VsK1Status"]) == "SUPPORTIVE_PREFLIGHT" else "WARNING",
            "MeasurementStatus": "WARNING",
            "Evidence": f"K2-vs-K1={support['K2VsK1Status']}",
            "Interpretation": "A2 is consistently stronger than K1/no-memory at preflight level",
            "BlocksMeasurementValidation": False,
        },
        {
            "ClosureID": "MRC_7_POLYNOMIAL_CONTROL",
            "PreflightStatus": "WARNING",
            "MeasurementStatus": "BLOCKED",
            "Evidence": f"{poly_fairness['Finding']}; current={current_decision['Finding']}",
            "Interpretation": "polynomial control cannot be dismissed and blocks stronger measurement interpretation",
            "BlocksMeasurementValidation": True,
        },
        {
            "ClosureID": "MRC_8_BRANCH_SCATTER_CALIBRATION",
            "PreflightStatus": "PASS" if truthy(branch_cal["IndependentCalibrationPreflightSupported"]) else "WARNING",
            "MeasurementStatus": "WARNING",
            "Evidence": (
                f"subset passes={branch_cal['ReconstructionFamilySubsetPasses']}/"
                f"{branch_cal['ReconstructionFamilySubsetTotal']}; route={route['BranchScatterStatus']}"
            ),
            "Interpretation": "branch-scatter bridge is independently calibrated for preflight, but it is not a full measurement route",
            "BlocksMeasurementValidation": True,
        },
        {
            "ClosureID": "MRC_9_FULL_LIKELIHOOD_NATIVE_ROUTE",
            "PreflightStatus": "WARNING",
            "MeasurementStatus": "BLOCKED",
            "Evidence": public_cov["CurrentStatus"],
            "Interpretation": "full likelihood-native joint SN+BAO transform is still missing",
            "BlocksMeasurementValidation": True,
        },
    ]
    detail = pd.DataFrame(rows)
    detail["ClaimBoundary"] = "measurement_route_closure_no_measurement_validation"
    detail.to_csv(OUT, index=False)

    preflight_blocked = int(detail["PreflightStatus"].eq("BLOCKED").sum())
    measurement_blocked = int(detail["MeasurementStatus"].eq("BLOCKED").sum())
    measurement_warnings = int(detail["MeasurementStatus"].eq("WARNING").sum())
    measurement_blocking_checks = int(detail["BlocksMeasurementValidation"].map(truthy).sum())
    summary = pd.DataFrame(
        [
            {
                "AuditID": "MEASUREMENT_ROUTE_CLOSURE_AUDIT_V1",
                "Checks": len(detail),
                "PreflightBlockedChecks": preflight_blocked,
                "MeasurementBlockedChecks": measurement_blocked,
                "MeasurementWarningChecks": measurement_warnings,
                "MeasurementBlockingChecks": measurement_blocking_checks,
                "PreflightRouteClosed": preflight_blocked == 0,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": (
                    "PREFLIGHT_ROUTE_CLOSED_MEASUREMENT_ROUTE_BLOCKED"
                    if preflight_blocked == 0
                    else "PREFLIGHT_ROUTE_STILL_BLOCKED"
                ),
                "StrongestAllowedClaim": "locked A2 has a closed preflight route with calibrated branch-scatter support",
                "PrimaryMeasurementBlockers": "polynomial_control;full_likelihood_native_joint_transform;measurement_grade_K1_and_null_policy",
                "NextAction": "build a full likelihood-native joint SN+BAO transform and freeze the same covariance/null/K1 policy before any measurement claim",
                "ClaimBoundary": "measurement_route_closure_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)

    DOCS.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Measurement Route Closure Audit",
        "",
        "Status: preflight route closed; measurement route still blocked.",
        "",
        "## Summary",
        "",
        f"- Preflight blocked checks: {preflight_blocked}",
        f"- Measurement blocked checks: {measurement_blocked}",
        f"- Measurement warnings: {measurement_warnings}",
        f"- Measurement validation allowed: False",
        f"- Strongest allowed claim: {summary.iloc[0]['StrongestAllowedClaim']}",
        "",
        "## Findings",
        "",
    ]
    for _, row in detail.iterrows():
        lines.extend(
            [
                f"### {row['ClosureID']}",
                "",
                f"- Preflight status: {row['PreflightStatus']}",
                f"- Measurement status: {row['MeasurementStatus']}",
                f"- Evidence: {row['Evidence']}",
                f"- Interpretation: {row['Interpretation']}",
                "",
            ]
        )
    DOC.write_text("\n".join(lines), encoding="utf-8")

    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")
    print(f"Wrote {DOC}")


if __name__ == "__main__":
    main()
