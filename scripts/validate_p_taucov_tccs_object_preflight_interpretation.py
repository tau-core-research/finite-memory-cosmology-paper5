#!/usr/bin/env python3
"""Validate TCCS object preflight interpretation."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
INTERPRETATION = ROOT / "evidence/p_taucov_tccs_object_preflight_interpretation.csv"
DOC = ROOT / "docs/p_taucov_tccs_object_preflight_interpretation.md"
OUT = ROOT / "evidence/p_taucov_tccs_object_preflight_interpretation_validation.csv"

AUDIT_ID = "P_TAUCOV_TCCS_OBJECT_PREFLIGHT_INTERPRETATION_VALIDATION"
EXPECTED_STATUS = "TCCS_OBJECT_PREFLIGHT_NEGATIVE_COLLAPSES_UNDER_PERP_BALANCE"


def add(rows: list[dict], check_id: str, passed: bool) -> None:
    rows.append({"AuditID": AUDIT_ID, "CheckID": check_id, "Passed": bool(passed), "Required": True, "Status": "PASS" if passed else "FAIL"})


def main() -> int:
    rows: list[dict] = []
    for path in [INTERPRETATION, DOC]:
        add(rows, f"exists_{path.relative_to(ROOT)}", path.exists())
    if not all(path.exists() for path in [INTERPRETATION, DOC]):
        pd.DataFrame(rows).to_csv(OUT, index=False)
        print("P_TAUCOV_TCCS_OBJECT_PREFLIGHT_INTERPRETATION_INVALID")
        return 1
    row = pd.read_csv(INTERPRETATION).iloc[0]
    doc = DOC.read_text(encoding="utf-8")
    add(rows, "status_expected", str(row["Status"]) == EXPECTED_STATUS)
    add(rows, "scoring_not_authorized", bool(row["ScoringAuthorized"]) is False)
    add(rows, "survival_not_authorized", bool(row["SurvivalClaimAuthorized"]) is False)
    add(rows, "tau_validation_not_authorized", bool(row["TauCoreValidationClaimAuthorized"]) is False)
    add(rows, "doc_says_must_not_be_scored", "must not be scored" in doc)
    add(rows, "doc_forbids_tau_signal", "has produced a Tau signal" in doc)
    out = pd.DataFrame(rows)
    out.to_csv(OUT, index=False)
    ok = bool(out["Passed"].all())
    print("P_TAUCOV_TCCS_OBJECT_PREFLIGHT_INTERPRETATION_VALID" if ok else "P_TAUCOV_TCCS_OBJECT_PREFLIGHT_INTERPRETATION_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
