#!/usr/bin/env python3
"""Validate program-level status after P3 balanced scorecard."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "evidence/p_taucov_program_status_after_p3_balanced.csv"
DOC = ROOT / "docs/p_taucov_program_status_after_p3_balanced.md"
OUT = ROOT / "evidence/p_taucov_program_status_after_p3_balanced_validation.csv"

AUDIT_ID = "P_TAUCOV_PROGRAM_STATUS_AFTER_P3_BALANCED_VALIDATION"
EXPECTED_STATUS = "P_TAUCOV_PROTOCOL_INFRASTRUCTURE_VALID_BUT_P3_BALANCED_NEGATIVE_NO_TAU_SIGNAL"


def add(rows: list[dict], check_id: str, passed: bool) -> None:
    rows.append({"AuditID": AUDIT_ID, "CheckID": check_id, "Passed": bool(passed), "Required": True, "Status": "PASS" if passed else "FAIL"})


def main() -> int:
    rows: list[dict] = []
    for path in [CSV, DOC]:
        add(rows, f"exists_{path.relative_to(ROOT)}", path.exists())
    if not (CSV.exists() and DOC.exists()):
        pd.DataFrame(rows).to_csv(OUT, index=False)
        print("P_TAUCOV_PROGRAM_STATUS_AFTER_P3_BALANCED_INVALID")
        return 1
    summary = pd.read_csv(CSV).iloc[0]
    doc = DOC.read_text(encoding="utf-8")
    add(rows, "status_expected", str(summary["Status"]) == EXPECTED_STATUS)
    add(rows, "p3_primary_negative", float(summary["P3BalancedPrimaryS"]) < 0.0)
    add(rows, "diag_partial_positive_recorded", bool(summary["DiagonalOrthogonalBeatsNullMax"]) is True)
    add(rows, "diag_clock_gate_failed", bool(summary["DiagonalOrthogonalClockGatePassed"]) is False)
    add(rows, "diag_family_gate_failed", bool(summary["DiagonalOrthogonalFamilyGatePassed"]) is False)
    add(rows, "survival_not_authorized", bool(summary["SurvivalClaimAuthorized"]) is False)
    add(rows, "tau_validation_not_authorized", bool(summary["TauCoreValidationClaimAuthorized"]) is False)
    add(rows, "doc_forbids_tau_validation", "P-TauCov validates Tau Core" in doc)
    add(rows, "doc_says_not_v4_tweak", "not be a v4 support tweak" in doc)
    out = pd.DataFrame(rows)
    out.to_csv(OUT, index=False)
    ok = bool(out["Passed"].all())
    print("P_TAUCOV_PROGRAM_STATUS_AFTER_P3_BALANCED_VALID" if ok else "P_TAUCOV_PROGRAM_STATUS_AFTER_P3_BALANCED_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
