#!/usr/bin/env python3
"""Validate P3 balanced P-TauCov signed alignment scorecard."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OOS = ROOT / "evidence/p_taucov_p3_balanced_oos_scorecard.csv"
NULLS = ROOT / "evidence/p_taucov_p3_balanced_null_scorecard.csv"
SUMMARY = ROOT / "evidence/p_taucov_p3_balanced_scorecard_summary.csv"
AUTH = ROOT / "evidence/p_taucov_p3_balanced_final_authorization_summary.csv"
OUT = ROOT / "evidence/p_taucov_p3_balanced_scorecard_validation.csv"

AUDIT_ID = "P_TAUCOV_P3_BALANCED_SCORECARD_VALIDATION"


def add(rows: list[dict], check_id: str, passed: bool) -> None:
    rows.append({"AuditID": AUDIT_ID, "CheckID": check_id, "Passed": bool(passed), "Required": True, "Status": "PASS" if passed else "FAIL"})


def main() -> int:
    rows: list[dict] = []
    for path in [OOS, NULLS, SUMMARY, AUTH]:
        add(rows, f"exists_{path.relative_to(ROOT)}", path.exists())
    if not all(path.exists() for path in [OOS, NULLS, SUMMARY, AUTH]):
        pd.DataFrame(rows).to_csv(OUT, index=False)
        print("P_TAUCOV_P3_BALANCED_SCORECARD_INVALID")
        return 1

    oos = pd.read_csv(OOS)
    nulls = pd.read_csv(NULLS)
    summary = pd.read_csv(SUMMARY).iloc[0]
    auth = pd.read_csv(AUTH).iloc[0]
    primary = oos[oos["PrimaryOOS"].astype(bool)]
    add(rows, "authorized_true", bool(summary["P3BalancedScoringAuthorized"]) is True)
    add(rows, "auth_summary_authorized", bool(auth["P3BalancedScoringAuthorized"]) is True)
    add(rows, "covariance_survival_not_authorized", bool(summary["CovarianceSurvivalClaimAuthorized"]) is False)
    add(rows, "tau_validation_not_authorized", bool(summary["TauCoreValidationClaimAuthorized"]) is False)
    add(rows, "measurement_not_authorized", bool(summary["MeasurementValidationAuthorized"]) is False)
    add(rows, "has_primary_oos", len(primary) > 0)
    add(rows, "has_nulls", len(nulls) >= 5)
    add(rows, "summary_primary_matches", abs(float(summary["PrimarySignedS"]) - float(primary["SignedS"].sum())) < 1e-9)
    add(rows, "summary_family_matches", abs(float(summary["FamilySignedS"]) - float(primary[primary["FoldClass"].eq("primary_leave_one_family_out")]["SignedS"].sum())) < 1e-9)
    add(rows, "summary_clock_matches", abs(float(summary["ClockSignedS"]) - float(primary[primary["FoldClass"].eq("primary_contiguous_clock_block")]["SignedS"].sum())) < 1e-9)
    add(rows, "claim_boundary", str(summary["ClaimBoundary"]) == "p3_balanced_alignment_scorecard_no_survival_claim")
    add(rows, "negative_primary_fails", float(summary["PrimarySignedS"]) < 0.0 and "FAIL_NO_SURVIVAL" in str(summary["Status"]))

    out = pd.DataFrame(rows)
    out.to_csv(OUT, index=False)
    ok = bool(out["Passed"].all())
    print("P_TAUCOV_P3_BALANCED_SCORECARD_VALID" if ok else "P_TAUCOV_P3_BALANCED_SCORECARD_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
