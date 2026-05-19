#!/usr/bin/env python3
"""Build the implementation plan for the full A2 measurement gate.

The goal is to make the remaining measurement route executable in a disciplined
way. The plan distinguishes closed preflight components from measurement-grade
components that remain blocked.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DATA = ROOT / "data"
DOCS = ROOT / "docs"

TRANSFORM = EVIDENCE / "k2_a2_transform_matrix_readiness_v1.csv"
PUBLIC_COV = EVIDENCE / "full_public_covariance_transform_summary.csv"
CLOSURE = EVIDENCE / "measurement_route_closure_summary.csv"
K1_SUMMARY = EVIDENCE / "source_split_likelihood_native_baseline_prediction_summary.csv"
JOINT_ROUTE = EVIDENCE / "joint_covariance_route_summary.csv"
JOINT_ADJUDICATION = EVIDENCE / "joint_covariance_adjudication_summary.csv"
FULL_LN_CONTRACT = EVIDENCE / "full_likelihood_native_joint_transform_readiness.csv"
K1_EXPORT = DATA / "k1" / "source_split_external_k1_response.csv"
K2 = DATA / "predictions" / "k2_source_split_a2_prior_v1.csv"
NULLS = EVIDENCE / "null_model_registry.csv"
POLY = EVIDENCE / "k2_a2_polynomial_tension_diagnosis.csv"

OUT = EVIDENCE / "full_gate_implementation_plan.csv"
SUMMARY = EVIDENCE / "full_gate_implementation_summary.csv"
DOC = DOCS / "full_gate_implementation_plan.md"


def truthy(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def first(path: Path) -> pd.Series:
    df = pd.read_csv(path)
    if df.empty:
        raise ValueError(f"empty evidence file: {path}")
    return df.iloc[0]


def main() -> None:
    transform = first(TRANSFORM)
    public_cov = first(PUBLIC_COV)
    closure = first(CLOSURE)
    k1_summary = first(K1_SUMMARY)
    joint_route = pd.read_csv(JOINT_ROUTE)
    joint_adjudication = first(JOINT_ADJUDICATION)
    full_ln_contract = first(FULL_LN_CONTRACT)
    poly = pd.read_csv(POLY)
    current_poly = poly[poly["DiagnosisID"].eq("CURRENT_DECISION")].iloc[0]

    rows = [
        {
            "ComponentID": "FG_1_LOCKED_A2",
            "ComponentClass": "prediction",
            "PreflightStatus": "CLOSED" if K2.exists() else "BLOCKED",
            "MeasurementStatus": "READY" if K2.exists() else "BLOCKED",
            "CurrentArtifact": str(K2.relative_to(ROOT)),
            "RemainingWork": "none; do not modify locked prediction",
            "AcceptanceCriterion": "K2 file exists and kernel/gain/rho/p remain unchanged",
            "BlocksMeasurement": False,
        },
        {
            "ComponentID": "FG_2_SN_TRANSFORM",
            "ComponentClass": "transform",
            "PreflightStatus": "CLOSED" if truthy(transform["LSNExported"]) else "BLOCKED",
            "MeasurementStatus": "PARTIAL",
            "CurrentArtifact": "data/transforms/k2_a2_l_sn_transform_v1.csv",
            "RemainingWork": "replace binned SN residual transform with likelihood-native SN nuisance/marginalization transform",
            "AcceptanceCriterion": "SN transform is derived from the same public likelihood definition used for final covariance",
            "BlocksMeasurement": True,
        },
        {
            "ComponentID": "FG_3_BAO_TRANSFORM",
            "ComponentClass": "transform",
            "PreflightStatus": "CLOSED" if truthy(transform["LBAOExported"]) else "BLOCKED",
            "MeasurementStatus": "PARTIAL",
            "CurrentArtifact": "data/transforms/k2_a2_l_bao_transform_v1.csv",
            "RemainingWork": "replace nearest-anchor BAO transform with likelihood-native BAO observable transform",
            "AcceptanceCriterion": "BAO transform maps the DESI vector/covariance into the same source-split target without post-hoc anchor choices",
            "BlocksMeasurement": True,
        },
        {
            "ComponentID": "FG_4_JOINT_COVARIANCE",
            "ComponentClass": "covariance",
            "PreflightStatus": "CLOSED" if truthy(public_cov["ZeroCrossCovariancePreflightUsable"]) else "BLOCKED",
            "MeasurementStatus": "BLOCKED",
            "CurrentArtifact": "evidence/joint_covariance_route_summary.csv",
            "RemainingWork": (
                f"{joint_adjudication['PrimaryBlocker']}; {joint_adjudication['NextAction']}"
            ),
            "AcceptanceCriterion": "same covariance is used for K1, locked A2, polynomial controls, and physical/null controls",
            "BlocksMeasurement": True,
        },
        {
            "ComponentID": "FG_5_K1_BASELINE",
            "ComponentClass": "baseline",
            "PreflightStatus": "CLOSED" if K1_EXPORT.exists() else "BLOCKED",
            "MeasurementStatus": "PARTIAL",
            "CurrentArtifact": str(K1_EXPORT.relative_to(ROOT)),
            "RemainingWork": str(k1_summary["BlockingIssue"]),
            "AcceptanceCriterion": "K1 is exported under final transform and covariance policy, with no same-data amplitude fit",
            "BlocksMeasurement": True,
        },
        {
            "ComponentID": "FG_6_NULL_POLICY",
            "ComponentClass": "nulls",
            "PreflightStatus": "CLOSED" if NULLS.exists() else "BLOCKED",
            "MeasurementStatus": "PARTIAL",
            "CurrentArtifact": str(NULLS.relative_to(ROOT)),
            "RemainingWork": "freeze final null set and complexity penalties under the final covariance route",
            "AcceptanceCriterion": "K1, polynomial, physical, sign-randomized, and coordinate-remap nulls score under identical covariance/transform policy",
            "BlocksMeasurement": True,
        },
        {
            "ComponentID": "FG_7_POLYNOMIAL_CONTROL",
            "ComponentClass": "overfit_risk_control",
            "PreflightStatus": "WARNING",
            "MeasurementStatus": "BLOCKED",
            "CurrentArtifact": str(POLY.relative_to(ROOT)),
            "RemainingWork": str(current_poly["MeasurementValidationImpact"]),
            "AcceptanceCriterion": "locked A2 remains competitive against polynomial controls under final public covariance and validation policy",
            "BlocksMeasurement": True,
        },
        {
            "ComponentID": "FG_8_BRANCH_SCATTER_BRIDGE",
            "ComponentClass": "calibrated_preflight_bridge",
            "PreflightStatus": "CLOSED" if truthy(closure["PreflightRouteClosed"]) else "WARNING",
            "MeasurementStatus": "WARNING",
            "CurrentArtifact": "evidence/branch_scatter_independent_calibration_summary.csv",
            "RemainingWork": "replace or validate bridge with full public covariance route",
            "AcceptanceCriterion": "branch-scatter bridge is reported only as preflight unless independently promoted",
            "BlocksMeasurement": True,
        },
    ]
    detail = pd.DataFrame(rows)
    detail["ClaimBoundary"] = "full_gate_implementation_plan_no_measurement_validation"
    detail.to_csv(OUT, index=False)

    preflight_closed = int(detail["PreflightStatus"].eq("CLOSED").sum())
    measurement_ready = int(detail["MeasurementStatus"].eq("READY").sum())
    measurement_blocked = int(detail["MeasurementStatus"].eq("BLOCKED").sum())
    measurement_partial = int(detail["MeasurementStatus"].eq("PARTIAL").sum())
    measurement_warnings = int(detail["MeasurementStatus"].eq("WARNING").sum())
    public_routes = joint_route[joint_route["RouteClass"].astype(str).str.contains("public", case=False, na=False)]
    branch_routes = joint_route[joint_route["RouteID"].eq("JCOV_BRANCH_SCATTER_BRIDGE_V1")]
    public_routes_k2_over_k1 = int(public_routes["K2ImprovesOverK1"].map(truthy).sum())
    public_routes_k2_over_poly = int(public_routes["K2BeatsBestPoly"].map(truthy).sum())
    branch_k2_over_poly = bool(not branch_routes.empty and truthy(branch_routes.iloc[0]["K2BeatsBestPoly"]))

    summary = pd.DataFrame(
        [
            {
                "PlanID": "FULL_GATE_IMPLEMENTATION_PLAN_V1",
                "Components": len(detail),
                "PreflightClosedComponents": preflight_closed,
                "MeasurementReadyComponents": measurement_ready,
                "MeasurementPartialComponents": measurement_partial,
                "MeasurementBlockedComponents": measurement_blocked,
                "MeasurementWarningComponents": measurement_warnings,
                "PublicJointRoutesK2OverK1": public_routes_k2_over_k1,
                "PublicJointRoutes": len(public_routes),
                "PublicJointRoutesK2OverPolynomial": public_routes_k2_over_poly,
                "BranchBridgeK2OverPolynomial": branch_k2_over_poly,
                "JointCovarianceAdjudicationStatus": joint_adjudication["CurrentStatus"],
                "JointCovariancePrimaryBlocker": joint_adjudication["PrimaryBlocker"],
                "FullLikelihoodNativeContractStatus": full_ln_contract["CurrentStatus"],
                "FullLikelihoodNativeMeasurementSatisfied": full_ln_contract["MeasurementSatisfied"],
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "IMPLEMENTATION_PLAN_READY_MEASUREMENT_ROUTE_BLOCKED",
                "StrongestAllowedClaim": "preflight route is closed; full measurement gate has an executable component plan",
                "PrimaryNextComponent": "FG_4_JOINT_COVARIANCE",
                "NextAction": "implement final joint covariance/transform route first, then rerun K1/null/polynomial scorecard unchanged",
                "ClaimBoundary": "full_gate_implementation_plan_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)

    DOCS.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Full Gate Implementation Plan",
        "",
        "Status: executable plan for the full measurement gate. Measurement validation remains closed.",
        "",
        "## Summary",
        "",
        f"- Preflight closed components: {preflight_closed}/{len(detail)}",
        f"- Measurement ready components: {measurement_ready}/{len(detail)}",
        f"- Measurement blocked components: {measurement_blocked}",
        f"- Measurement partial components: {measurement_partial}",
        f"- Primary next component: {summary.iloc[0]['PrimaryNextComponent']}",
        "",
        "## Components",
        "",
    ]
    for _, row in detail.iterrows():
        lines.extend(
            [
                f"### {row['ComponentID']}",
                "",
                f"- Class: {row['ComponentClass']}",
                f"- Preflight: {row['PreflightStatus']}",
                f"- Measurement: {row['MeasurementStatus']}",
                f"- Current artifact: `{row['CurrentArtifact']}`",
                f"- Remaining work: {row['RemainingWork']}",
                f"- Acceptance criterion: {row['AcceptanceCriterion']}",
                "",
            ]
        )
    DOC.write_text("\n".join(lines), encoding="utf-8")

    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")
    print(f"Wrote {DOC}")


if __name__ == "__main__":
    main()
