#!/usr/bin/env python3
"""Adjudicate the joint-covariance routes for the locked A2 preflight.

This is a route-level decision artifact. It does not change the locked K2/A2
prediction and does not promote any route to measurement validation.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

ROUTE_SUMMARY = EVIDENCE / "joint_covariance_route_summary.csv"
ROUTE_REGISTRY = EVIDENCE / "joint_covariance_route_registry.csv"

OUT_AUDIT = EVIDENCE / "joint_covariance_adjudication_audit.csv"
OUT_SUMMARY = EVIDENCE / "joint_covariance_adjudication_summary.csv"
OUT_DOC = DOCS / "joint_covariance_adjudication_audit.md"


def truthy(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def adjudicate(row: pd.Series) -> tuple[str, str, str]:
    route_class = str(row["RouteClass"])
    k2_over_k1 = truthy(row["K2ImprovesOverK1"])
    k2_over_poly = truthy(row["K2BeatsBestPoly"])

    if route_class == "calibrated_preflight_bridge":
        if k2_over_k1 and k2_over_poly:
            return (
                "PREFLIGHT_SUPPORTIVE_NOT_MEASUREMENT",
                "A2 is stronger than K1 and polynomial controls on this calibrated bridge, but the route is not a full public covariance route.",
                "use as calibrated preflight support only; replace or validate with full public covariance before any stronger interpretation",
            )
        return (
            "PREFLIGHT_BRIDGE_WEAKENED",
            "The calibrated bridge does not preserve A2 dominance over the registered controls.",
            "keep as warning route and do not use for measurement interpretation",
        )

    if "public" in route_class:
        if k2_over_k1 and not k2_over_poly:
            return (
                "PUBLIC_ROUTE_SUPPORTIVE_VS_K1_POLY_BLOCKED",
                "A2 improves over K1 under this public covariance proxy, but polynomial controls remain stronger.",
                "treat as K1-supportive but measurement-blocked; require likelihood-native transform and final null policy",
            )
        if k2_over_k1 and k2_over_poly:
            return (
                "PUBLIC_ROUTE_PREFLIGHT_SUPPORTIVE",
                "A2 improves over K1 and polynomial controls under this public proxy, but the route is still not measurement-grade.",
                "promote only after the transform/cross-covariance policy is likelihood-native and predeclared",
            )
        return (
            "PUBLIC_ROUTE_WEAKENING",
            "A2 does not improve over the K1 no-memory baseline under this public covariance route.",
            "retain as weakening evidence and do not promote measurement status",
        )

    return (
        "SENSITIVITY_ONLY_NOT_MEASUREMENT",
        "This route is a sensitivity/control route and cannot support measurement validation.",
        "use only to localize covariance sensitivity",
    )


def main() -> None:
    summary = pd.read_csv(ROUTE_SUMMARY)
    registry = pd.read_csv(ROUTE_REGISTRY)
    merged = summary.merge(
        registry[
            [
                "RouteID",
                "PositiveDefinite",
                "Predeclared",
                "CanSupportMeasurementValidation",
                "PrimaryLimitation",
            ]
        ],
        on="RouteID",
        how="left",
    )

    rows: list[dict[str, object]] = []
    for _, row in merged.iterrows():
        decision, finding, next_action = adjudicate(row)
        rows.append(
            {
                "RouteID": row["RouteID"],
                "RouteClass": row["RouteClass"],
                "BestModel": row["BestModel"],
                "DeltaAIC_K2_minus_K1": row["DeltaAIC_K2_minus_K1"],
                "DeltaAIC_K2_minus_BestPoly": row["DeltaAIC_K2_minus_BestPoly"],
                "K2ImprovesOverK1": row["K2ImprovesOverK1"],
                "K2BeatsBestPoly": row["K2BeatsBestPoly"],
                "PositiveDefinite": row["PositiveDefinite"],
                "Predeclared": row["Predeclared"],
                "CanSupportMeasurementValidation": False,
                "Adjudication": decision,
                "Finding": finding,
                "PrimaryLimitation": row["PrimaryLimitation"],
                "NextAction": next_action,
                "ClaimBoundary": "joint_covariance_adjudication_no_measurement_validation",
            }
        )

    audit = pd.DataFrame(rows)
    audit.to_csv(OUT_AUDIT, index=False)

    public = audit[audit["RouteClass"].astype(str).str.contains("public", case=False, na=False)]
    branch = audit[audit["RouteClass"].eq("calibrated_preflight_bridge")]
    public_k2_k1 = int(public["K2ImprovesOverK1"].map(truthy).sum())
    public_k2_poly = int(public["K2BeatsBestPoly"].map(truthy).sum())
    branch_support = bool(not branch.empty and truthy(branch.iloc[0]["K2BeatsBestPoly"]))
    blocking = ";".join(sorted(audit.loc[audit["K2BeatsBestPoly"].map(lambda v: not truthy(v)), "RouteID"].astype(str)))

    summary_out = pd.DataFrame(
        [
            {
                "AuditID": "JOINT_COVARIANCE_ADJUDICATION_V1",
                "Routes": len(audit),
                "PublicRoutes": len(public),
                "PublicRoutesK2OverK1": public_k2_k1,
                "PublicRoutesK2OverPolynomial": public_k2_poly,
                "BranchBridgeSupportiveAgainstPolynomial": branch_support,
                "MeasurementGradeRoutes": 0,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": "FG4_EXECUTABLE_PREFLIGHT_MEASUREMENT_BLOCKED",
                "StrongestAllowedClaim": "public joint-covariance routes support A2 over K1, while the calibrated branch bridge supports A2 over K1 and polynomial controls at preflight level",
                "PrimaryBlocker": "public covariance routes remain polynomial-dominated; branch bridge is not measurement-grade",
                "BlockedRouteIDs": blocking,
                "NextAction": "build likelihood-native joint transform and final K1/null policy, then rerun locked A2 unchanged",
                "ClaimBoundary": "joint_covariance_adjudication_no_measurement_validation",
            }
        ]
    )
    summary_out.to_csv(OUT_SUMMARY, index=False)

    DOCS.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Joint Covariance Adjudication Audit",
        "",
        "Status: FG_4 is executable at preflight level. Measurement validation remains closed.",
        "",
        "## Summary",
        "",
        f"- Public routes where A2 improves over K1: {public_k2_k1}/{len(public)}",
        f"- Public routes where A2 beats polynomial controls: {public_k2_poly}/{len(public)}",
        f"- Branch bridge supportive against polynomial controls: {branch_support}",
        "- Measurement-grade routes: 0",
        "- Primary blocker: public covariance routes remain polynomial-dominated; branch bridge is not measurement-grade.",
        "",
        "## Route Decisions",
        "",
    ]
    for _, row in audit.iterrows():
        lines.extend(
            [
                f"### {row['RouteID']}",
                "",
                f"- Class: {row['RouteClass']}",
                f"- Adjudication: {row['Adjudication']}",
                f"- Delta AIC A2-K1: {row['DeltaAIC_K2_minus_K1']}",
                f"- Delta AIC A2-best polynomial: {row['DeltaAIC_K2_minus_BestPoly']}",
                f"- Finding: {row['Finding']}",
                f"- Next action: {row['NextAction']}",
                "",
            ]
        )
    lines.extend(
        [
            "## Claim Boundary",
            "",
            "This audit does not alter the locked A2 prediction, does not fit K1, does not allow rho > 4, and does not authorize measurement validation.",
            "",
        ]
    )
    OUT_DOC.write_text("\n".join(lines), encoding="utf-8")

    print(f"Wrote {OUT_AUDIT}")
    print(f"Wrote {OUT_SUMMARY}")
    print(f"Wrote {OUT_DOC}")


if __name__ == "__main__":
    main()
