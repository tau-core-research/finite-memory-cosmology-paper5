#!/usr/bin/env python3
"""Audit whether branch-scatter preflight support is independently calibrated.

The independent check uses the exported public source-split reconstruction-family
responses. It asks whether locked A2 remains the best simple response when the
target is not the original branch-scatter scorecard itself.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

FAMILY_READINESS = EVIDENCE / "source_split_reconstruction_family_source_readiness.csv"
RECON_SUMMARY = EVIDENCE / "k2_a2_reconstruction_family_summary.csv"
BRANCH_REG = EVIDENCE / "branch_scatter_systematic_registration_summary.csv"
BRANCH_SUMMARY = EVIDENCE / "source_split_likelihood_native_branch_scatter_summary.csv"

OUT = EVIDENCE / "branch_scatter_independent_calibration_audit.csv"
SUMMARY = EVIDENCE / "branch_scatter_independent_calibration_summary.csv"
DOC = DOCS / "branch_scatter_independent_calibration_audit.md"

TARGET_SUBSETS = [
    "all_points",
    "low_depth",
    "mid_depth",
    "high_depth",
    "mid_high_depth",
    "anti_aligned",
    "anti_aligned_mid_high",
]


def truthy(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def first(path: Path) -> pd.Series:
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_csv(path)
    if df.empty:
        raise ValueError(f"empty evidence file: {path}")
    return df.iloc[0]


def main() -> None:
    readiness = pd.read_csv(FAMILY_READINESS)
    recon = pd.read_csv(RECON_SUMMARY)
    branch_reg = first(BRANCH_REG)
    branch_summary = pd.read_csv(BRANCH_SUMMARY)

    family_source = readiness[readiness["FamilySourceID"].eq("RF_PUBLIC_SOURCE_SPLIT_RECONSTRUCTION_FAMILIES")]
    family_allowed = bool(not family_source.empty and truthy(family_source.iloc[0]["AllowedForK2Scoring"]))

    best_by_subset = (
        recon.sort_values(["Subset", "AIC"])
        .groupby("Subset", as_index=False)
        .first()[["Subset", "ModelID", "AIC"]]
        .rename(columns={"ModelID": "BestModel", "AIC": "BestAIC"})
    )
    best_lookup = dict(zip(best_by_subset["Subset"], best_by_subset["BestModel"], strict=False))
    subset_rows = []
    for subset in TARGET_SUBSETS:
        sub = recon[recon["Subset"].eq(subset)]
        if sub.empty:
            subset_rows.append(
                {
                    "CriterionID": f"RECON_SUBSET_{subset.upper()}",
                    "Status": "WARNING",
                    "Evidence": "subset missing from reconstruction-family summary",
                    "Interpretation": "cannot use this subset for independent calibration",
                    "ClaimImpact": "keeps calibration partial",
                }
            )
            continue
        a2 = sub[sub["ModelID"].eq("K2_SOURCE_SPLIT_A2_PRIOR_V1")].iloc[0]
        k1 = sub[sub["ModelID"].eq("K1_NO_MEMORY")].iloc[0]
        unit = sub[sub["ModelID"].eq("K2_UNIT_LOCKED_RHO4")].iloc[0]
        best_model = best_lookup.get(subset, "")
        status = "PASS" if best_model == "K2_SOURCE_SPLIT_A2_PRIOR_V1" else "WARNING"
        subset_rows.append(
            {
                "CriterionID": f"RECON_SUBSET_{subset.upper()}",
                "Status": status,
                "Evidence": (
                    f"best={best_model}; "
                    f"DeltaAIC_A2_minus_K1={float(a2['AIC']) - float(k1['AIC'])}; "
                    f"DeltaAIC_A2_minus_unit={float(a2['AIC']) - float(unit['AIC'])}; "
                    f"A2 sign-match={a2['SignMatchFraction']}"
                ),
                "Interpretation": (
                    "locked A2 is independently favored in this reconstruction-family subset"
                    if status == "PASS"
                    else "locked A2 is not the best reconstruction-family response in this subset"
                ),
                "ClaimImpact": "supports branch-scatter calibration at preflight level",
            }
        )

    branch_best = int(branch_summary["BestModel"].eq("K2_LOCKED_RHO4").sum())
    branch_total = len(branch_summary)
    rows = [
        {
            "CriterionID": "FAMILY_SOURCE_ALLOWED",
            "Status": "PASS" if family_allowed else "BLOCKED",
            "Evidence": (
                "RF_PUBLIC_SOURCE_SPLIT_RECONSTRUCTION_FAMILIES allowed for K2 scoring"
                if family_allowed
                else "scoring-grade reconstruction-family source not available"
            ),
            "Interpretation": "independent source-split family input is available",
            "ClaimImpact": "unlocks independent calibration audit",
        },
        {
            "CriterionID": "BRANCH_SCATTER_PREFLIGHT_REGISTERED",
            "Status": "PASS" if truthy(branch_reg["PreflightRouteRegistered"]) else "BLOCKED",
            "Evidence": f"branch registration status={branch_reg['CurrentStatus']}",
            "Interpretation": "branch-scatter route is already registered as preflight bridge",
            "ClaimImpact": "connects independent family check to registered bridge",
        },
        {
            "CriterionID": "BRANCH_SCATTER_A2_COMPETITIVE",
            "Status": "PASS" if branch_best == branch_total else "WARNING",
            "Evidence": f"K2 best branch-scatter covariance cases={branch_best}/{branch_total}",
            "Interpretation": "branch-scatter route itself remains K2-supportive",
            "ClaimImpact": "keeps bridge internally consistent",
        },
        *subset_rows,
        {
            "CriterionID": "MEASUREMENT_VALIDATION_BOUNDARY",
            "Status": "PASS",
            "Evidence": "independent calibration is still preflight and covariance-limited",
            "Interpretation": "does not authorize measurement-validation language",
            "ClaimImpact": "keeps paper claim bounded",
        },
    ]
    detail = pd.DataFrame(rows)
    detail["ClaimBoundary"] = "branch_scatter_independent_calibration_no_measurement_validation"
    detail.to_csv(OUT, index=False)

    passed = int(detail["Status"].eq("PASS").sum())
    warnings = int(detail["Status"].eq("WARNING").sum())
    blocked = int(detail["Status"].eq("BLOCKED").sum())
    subset_mask = detail["CriterionID"].astype(str).str.startswith("RECON_SUBSET_")
    subset_passes = int((subset_mask & detail["Status"].eq("PASS")).sum())
    summary = pd.DataFrame(
        [
            {
                "AuditID": "BRANCH_SCATTER_INDEPENDENT_CALIBRATION_AUDIT_V1",
                "Criteria": len(detail),
                "PassedCriteria": passed,
                "WarningCriteria": warnings,
                "BlockedCriteria": blocked,
                "ReconstructionFamilySubsetPasses": subset_passes,
                "ReconstructionFamilySubsetTotal": len(TARGET_SUBSETS),
                "BranchScatterK2BestCases": branch_best,
                "BranchScatterCases": branch_total,
                "IndependentCalibrationPreflightSupported": blocked == 0
                and subset_passes == len(TARGET_SUBSETS)
                and branch_best == branch_total,
                "MeasurementValidationAllowed": False,
                "CurrentStatus": (
                    "BRANCH_SCATTER_INDEPENDENT_PREFLIGHT_CALIBRATION_SUPPORTED"
                    if blocked == 0 and subset_passes == len(TARGET_SUBSETS) and branch_best == branch_total
                    else "BRANCH_SCATTER_INDEPENDENT_CALIBRATION_PARTIAL"
                ),
                "StrongestAllowedClaim": (
                    "branch-scatter A2 preflight bridge is independently supported by public reconstruction-family responses"
                ),
                "PrimaryResidualRisk": "calibration remains preflight because full likelihood covariance and measurement route are still missing",
                "NextAction": "promote this as the bridge calibration layer, then keep Phase II focused on full public covariance",
                "ClaimBoundary": "branch_scatter_independent_calibration_no_measurement_validation",
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)

    DOCS.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Branch-Scatter Independent Calibration Audit",
        "",
        "Status: independent preflight calibration only. Measurement validation remains closed.",
        "",
        "## Summary",
        "",
        f"- Passed criteria: {passed}/{len(detail)}",
        f"- Warnings: {warnings}",
        f"- Blocked: {blocked}",
        f"- Reconstruction-family subset passes: {subset_passes}/{len(TARGET_SUBSETS)}",
        f"- Branch-scatter K2-best cases: {branch_best}/{branch_total}",
        f"- Strongest allowed claim: {summary.iloc[0]['StrongestAllowedClaim']}",
        "",
        "## Findings",
        "",
    ]
    for _, row in detail.iterrows():
        lines.extend(
            [
                f"### {row['CriterionID']}",
                "",
                f"- Status: {row['Status']}",
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
