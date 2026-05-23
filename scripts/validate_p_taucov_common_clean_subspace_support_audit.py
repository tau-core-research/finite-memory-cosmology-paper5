#!/usr/bin/env python3
"""Validate the common-clean-subspace support audit."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"
FREEZE_ID = "P_TAUCOV_COMMON_CLEAN_SUBSPACE_SUPPORT_AUDIT_v1"


def main() -> None:
    required = [
        EVIDENCE / "p_taucov_common_clean_subspace_support_audit_summary.csv",
        EVIDENCE / "p_taucov_common_clean_subspace_support_audit_gates.csv",
        EVIDENCE / "p_taucov_common_clean_subspace_support_audit_matrices.csv",
        EVIDENCE / "p_taucov_common_clean_subspace_support_audit_overview.csv",
        DOCS / "p_taucov_common_clean_subspace_support_audit.md",
    ]
    for path in required:
        if not path.exists():
            raise SystemExit(f"Missing required artifact: {path}")

    summary = pd.read_csv(required[0])
    gates = pd.read_csv(required[1])
    overview = pd.read_csv(required[3])
    if len(overview) != 1:
        raise SystemExit("Expected one overview row")
    if overview.iloc[0]["FreezeID"] != FREEZE_ID:
        raise SystemExit("Unexpected FreezeID")

    if bool(overview.iloc[0]["ScoringAuthorized"]) or bool(overview.iloc[0]["SurvivalClaimAuthorized"]):
        raise SystemExit("Audit must not authorize scoring or survival")
    if bool(overview.iloc[0]["TauCoreValidationClaimAuthorized"]):
        raise SystemExit("Audit must not authorize Tau Core validation")

    for rec in summary.to_dict("records"):
        cid = rec["CandidateID"]
        subset = gates[gates["CandidateID"] == cid]
        passed = int(subset["Passed"].astype(bool).sum())
        total = int(len(subset))
        if int(rec["PassedGates"]) != passed or int(rec["TotalGates"]) != total:
            raise SystemExit(f"Gate count mismatch for {cid}")
        expected = "CANDIDATE_SUPPORT_PASS_NO_SCORING" if passed == total else "CANDIDATE_SUPPORT_FAIL_NO_SCORING"
        if rec["Status"] != expected:
            raise SystemExit(f"Unexpected status for {cid}: {rec['Status']} != {expected}")
        if bool(rec["ScoringAuthorized"]):
            raise SystemExit(f"Candidate {cid} must not authorize scoring")

    passing = int((summary["PassedGates"] == summary["TotalGates"]).sum())
    expected_overview = (
        "P_TAUCOV_COMMON_CLEAN_SUBSPACE_SUPPORT_AUDIT_HAS_PREFLIGHT_CANDIDATE_NO_SCORING"
        if passing
        else "P_TAUCOV_COMMON_CLEAN_SUBSPACE_SUPPORT_AUDIT_NO_PASSING_CANDIDATE_NO_SCORING"
    )
    if overview.iloc[0]["Status"] != expected_overview:
        raise SystemExit("Unexpected overview status")

    pd.DataFrame(
        [
            {
                "FreezeID": FREEZE_ID,
                "ValidationStatus": "P_TAUCOV_COMMON_CLEAN_SUBSPACE_SUPPORT_AUDIT_VALID",
                "AuditStatus": overview.iloc[0]["Status"],
                "CandidatesTested": len(summary),
                "PassingCandidates": passing,
                "ScoringAuthorized": False,
            }
        ]
    ).to_csv(EVIDENCE / "p_taucov_common_clean_subspace_support_audit_validation.csv", index=False)
    print("P_TAUCOV_COMMON_CLEAN_SUBSPACE_SUPPORT_AUDIT_VALID")


if __name__ == "__main__":
    main()
