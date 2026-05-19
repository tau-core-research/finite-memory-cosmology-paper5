#!/usr/bin/env python3
"""Build a compact source-split gate dashboard."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
OUT = EVIDENCE / "source_split_gate_dashboard.csv"
SUMMARY = EVIDENCE / "source_split_gate_dashboard_summary.csv"


def read_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(EVIDENCE / name)


def any_allowed(df: pd.DataFrame) -> bool:
    if "AllowedForK2Scoring" not in df.columns:
        return False
    return df["AllowedForK2Scoring"].astype(str).str.lower().eq("true").any()


def available_count(df: pd.DataFrame) -> int:
    if "Status" not in df.columns:
        return 0
    return int(df["Status"].astype(str).str.lower().eq("available").sum())


def target_row(df: pd.DataFrame, id_column: str, target_id: str) -> pd.Series | None:
    rows = df[df[id_column].astype(str).eq(target_id)]
    if rows.empty:
        return None
    return rows.iloc[0]


def optional_read_csv(name: str) -> pd.DataFrame | None:
    path = EVIDENCE / name
    if not path.exists():
        return None
    return pd.read_csv(path)


def main() -> None:
    readiness = read_csv("source_split_readiness.csv")
    k1 = read_csv("source_split_k1_target_readiness.csv")
    covariance = read_csv("source_split_covariance_readiness.csv")
    sign_family = read_csv("sign_family_export_readiness.csv")
    transform = read_csv("source_split_transform_readiness.csv")
    export_validation = optional_read_csv("source_split_reconstruction_family_export_validation.csv")
    response_preview = optional_read_csv("source_split_reconstruction_family_response_preview_summary.csv")
    sign_promotion = optional_read_csv("source_split_sign_rule_promotion_readiness.csv")
    candidate_guard = optional_read_csv("source_split_candidate_path_guard.csv")

    k1_target = target_row(k1, "TargetID", "SSK1_COORDINATE_NATIVE_SOURCE_SPLIT_TARGET")
    cov_target = target_row(covariance, "CovarianceID", "SSCOV_SHRINKAGE_SOURCE_SPLIT")
    sign_target = target_row(sign_family, "SignFamilyID", "SF_PUBLIC_SOURCE_SPLIT_FAMILIES")
    transform_target = target_row(transform, "TransformID", "SST3_PUBLIC_SN_BAO_SOURCE_SPLIT")

    rows = [
        {
            "GateID": "SS_INPUTS_AND_NULLS",
            "GateName": "Public inputs and null registry",
            "Status": "OPEN",
            "AllowedForK2Scoring": False,
            "Evidence": "SN/BAO inputs and null comparator registry are available",
            "BlockingIssue": "downstream_gates_closed",
            "NextAction": "Use as inputs for transform/export work only.",
        },
        {
            "GateID": "SS_TRANSFORM",
            "GateName": "Coordinate-native source-split transform",
            "Status": str(transform_target["Status"]) if transform_target is not None else "missing",
            "AllowedForK2Scoring": bool(transform_target["AllowedForK2Scoring"]) if transform_target is not None else False,
            "Evidence": "source_split_transform_readiness.csv",
            "BlockingIssue": str(transform_target["BlockingIssue"]) if transform_target is not None else "missing_transform_target",
            "NextAction": str(transform_target["NextAction"]) if transform_target is not None else "Register transform target.",
        },
        {
            "GateID": "SS_K1_TARGET",
            "GateName": "Coordinate-native K1/no-memory target",
            "Status": str(k1_target["Status"]) if k1_target is not None else "missing",
            "AllowedForK2Scoring": any_allowed(k1),
            "Evidence": f"available_candidates={available_count(k1)}",
            "BlockingIssue": str(k1_target["BlockingIssue"]) if k1_target is not None else "missing_k1_target",
            "NextAction": str(k1_target["NextAction"]) if k1_target is not None else "Register K1 target.",
        },
        {
            "GateID": "SS_JOINT_COVARIANCE",
            "GateName": "Joint source-split covariance",
            "Status": str(cov_target["Status"]) if cov_target is not None else "missing",
            "AllowedForK2Scoring": any_allowed(covariance),
            "Evidence": f"available_controls={available_count(covariance)}",
            "BlockingIssue": str(cov_target["BlockingIssue"]) if cov_target is not None else "missing_covariance_target",
            "NextAction": str(cov_target["NextAction"]) if cov_target is not None else "Register covariance target.",
        },
        {
            "GateID": "SS_SIGN_FAMILY",
            "GateName": "Public source-split sign-family export",
            "Status": str(sign_target["Status"]) if sign_target is not None else "missing",
            "AllowedForK2Scoring": any_allowed(sign_family),
            "Evidence": f"available_templates={available_count(sign_family)}",
            "BlockingIssue": str(sign_target["BlockingIssue"]) if sign_target is not None else "missing_sign_family_target",
            "NextAction": str(sign_target["NextAction"]) if sign_target is not None else "Register sign-family target.",
        },
    ]
    if export_validation is not None and not export_validation.empty:
        export_row = export_validation.iloc[0]
        rows.append(
            {
                "GateID": "SS_RECONSTRUCTION_FAMILY_EXPORT",
                "GateName": "Public reconstruction-family response export",
                "Status": "available" if bool(export_row["Available"]) else "missing",
                "AllowedForK2Scoring": bool(export_row["AllowedForK2Scoring"]),
                "Evidence": "source_split_reconstruction_family_export_validation.csv",
                "BlockingIssue": str(export_row["BlockingIssue"]),
                "NextAction": str(export_row["NextAction"]),
            }
        )
    if candidate_guard is not None and not candidate_guard.empty:
        guard_row = candidate_guard.iloc[0]
        rows.append(
            {
                "GateID": "SS_CANDIDATE_PATH_GUARD",
                "GateName": "Candidate export path guard",
                "Status": str(guard_row["Status"]),
                "AllowedForK2Scoring": bool(guard_row["AllowedForK2Scoring"]),
                "Evidence": "source_split_candidate_path_guard.csv",
                "BlockingIssue": str(guard_row["BlockingIssue"]),
                "NextAction": str(guard_row["NextAction"]),
            }
        )
    if response_preview is not None and not response_preview.empty:
        preview_row = response_preview.iloc[0]
        rows.append(
            {
                "GateID": "SS_RECONSTRUCTION_FAMILY_PREVIEW",
                "GateName": "Non-scoring reconstruction-family response preview",
                "Status": "schema_valid" if bool(preview_row["SchemaValid"]) else "schema_warning",
                "AllowedForK2Scoring": bool(preview_row["AllowedForK2Scoring"]),
                "Evidence": "source_split_reconstruction_family_response_preview_summary.csv",
                "BlockingIssue": str(preview_row["BlockingIssue"]),
                "NextAction": str(preview_row["NextAction"]),
            }
        )
    if sign_promotion is not None and not sign_promotion.empty:
        promotion_row = sign_promotion[sign_promotion["CheckID"].eq("SRP5_RULE_PROMOTION_AUTHORIZED")]
        row = promotion_row.iloc[0] if not promotion_row.empty else sign_promotion.iloc[-1]
        rows.append(
            {
                "GateID": "SS_SIGN_RULE_PROMOTION",
                "GateName": "Family sign-rule promotion readiness",
                "Status": "authorized" if bool(row["Available"]) else "blocked",
                "AllowedForK2Scoring": bool(row["AllowedForK2Scoring"]),
                "Evidence": "source_split_sign_rule_promotion_readiness.csv",
                "BlockingIssue": str(row["BlockingIssue"]),
                "NextAction": str(row["NextAction"]),
            }
        )

    scoring_row = readiness[readiness["CheckID"].eq("SS9_SCORING_AUTHORIZATION")]
    scoring_open = (
        not scoring_row.empty
        and str(scoring_row.iloc[0]["Available"]).lower() == "true"
    )
    blockers = [row["GateID"] for row in rows if not row["AllowedForK2Scoring"] and row["GateID"] != "SS_INPUTS_AND_NULLS"]

    dashboard = pd.DataFrame(rows)
    dashboard.to_csv(OUT, index=False)
    remaining = [row for row in rows if not row["AllowedForK2Scoring"] and row["GateID"] != "SS_INPUTS_AND_NULLS"]
    primary_next_action = (
        "Resolve remaining transform, K1, covariance, and sign-family gates before K2 scoring."
        if any(row["GateID"] == "SS_RECONSTRUCTION_FAMILY_EXPORT" and row["AllowedForK2Scoring"] for row in rows)
        else "Create a valid public reconstruction-family candidate export before promoting the sign rule or scoring K2."
    )
    if not remaining and not scoring_open:
        primary_next_action = "Update source-split readiness authorization after all gate artifacts are synchronized."

    summary = pd.DataFrame(
        [
            {
                "DashboardID": "SOURCE_SPLIT_GATE_DASHBOARD",
                "Gates": len(rows),
                "OpenInputGate": True,
                "K2ScoringAuthorized": scoring_open,
                "ClosedCoreGates": "|".join(blockers),
                "PrimaryNextAction": primary_next_action,
                "ClaimBoundary": "readiness_dashboard_only_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)

    print(f"Wrote {OUT}")
    print(f"Wrote {SUMMARY}")


if __name__ == "__main__":
    main()
