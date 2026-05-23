#!/usr/bin/env python3
"""Validate the P-TauCov domain-compatibility audit artifact."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"
FREEZE_ID = "P_TAUCOV_DOMAIN_COMPATIBILITY_AUDIT_v1"


def main() -> None:
    summary_path = EVIDENCE / "p_taucov_domain_compatibility_audit_summary.csv"
    gates_path = EVIDENCE / "p_taucov_domain_compatibility_audit_gates.csv"
    doc_path = DOCS / "p_taucov_domain_compatibility_audit.md"
    comm_path = EVIDENCE / "p_taucov_domain_compatibility_commutator_matrix.csv"
    cleaner_path = EVIDENCE / "p_taucov_domain_compatibility_common_cleaner_matrix.csv"
    for path in [summary_path, gates_path, doc_path, comm_path, cleaner_path]:
        if not path.exists():
            raise SystemExit(f"Missing required artifact: {path}")

    summary = pd.read_csv(summary_path)
    gates = pd.read_csv(gates_path)
    if len(summary) != 1:
        raise SystemExit("Expected one summary row")
    row = summary.iloc[0]
    if row["FreezeID"] != FREEZE_ID:
        raise SystemExit("Unexpected FreezeID")
    if bool(row["ScoringAuthorized"]) or bool(row["SurvivalClaimAuthorized"]) or bool(row["TauCoreValidationClaimAuthorized"]):
        raise SystemExit("Audit must not authorize scoring, survival, or Tau validation")

    passed = int(gates["Passed"].astype(bool).sum())
    total = int(len(gates))
    if int(row["PassedGates"]) != passed or int(row["TotalGates"]) != total:
        raise SystemExit("Gate counts do not match")

    expected_status = (
        "P_TAUCOV_DOMAIN_COMPATIBILITY_AUDIT_PASS_NO_SCORING"
        if passed == total
        else "P_TAUCOV_DOMAIN_COMPATIBILITY_AUDIT_FAIL_NO_SCORING"
    )
    if row["Status"] != expected_status:
        raise SystemExit(f"Unexpected status: {row['Status']} != {expected_status}")

    validation_path = EVIDENCE / "p_taucov_domain_compatibility_audit_validation.csv"
    pd.DataFrame(
        [
            {
                "FreezeID": FREEZE_ID,
                "ValidationStatus": "P_TAUCOV_DOMAIN_COMPATIBILITY_AUDIT_VALID",
                "AuditStatus": row["Status"],
                "PassedGates": passed,
                "TotalGates": total,
                "ScoringAuthorized": False,
            }
        ]
    ).to_csv(validation_path, index=False)
    print("P_TAUCOV_DOMAIN_COMPATIBILITY_AUDIT_VALID")


if __name__ == "__main__":
    main()
