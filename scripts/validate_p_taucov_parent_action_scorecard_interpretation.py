#!/usr/bin/env python3
"""Validate parent-action P-TauCov scorecard interpretation."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
INTERPRETATION = ROOT / "evidence/p_taucov_parent_action_scorecard_interpretation.csv"
DOC = ROOT / "docs/p_taucov_parent_action_scorecard_interpretation.md"
OUT = ROOT / "evidence/p_taucov_parent_action_scorecard_interpretation_validation.csv"


def main() -> int:
    records: list[dict] = []

    def add(check_id: str, passed: bool) -> None:
        records.append({"AuditID": "P_TAUCOV_PARENT_ACTION_SCORECARD_INTERPRETATION_VALIDATION", "CheckID": check_id, "Passed": bool(passed), "Required": True, "Status": "PASS" if passed else "FAIL"})

    for path in [INTERPRETATION, DOC]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())
    if INTERPRETATION.exists() and DOC.exists():
        row = pd.read_csv(INTERPRETATION).iloc[0]
        doc = DOC.read_text(encoding="utf-8")
        add("negative_status", str(row["Status"]) == "P_TAUCOV_PARENT_ACTION_PRIMARY_SCORECARD_NEGATIVE_NO_SURVIVAL_CLAIM")
        add("delta_nonpositive", float(row["PrimaryOOSDeltaNLL_BaselineMinusKernel"]) <= 0.0)
        add("survival_not_authorized", bool(row["SurvivalClaimAuthorized"]) is False)
        add("measurement_not_authorized", bool(row["MeasurementValidationAuthorized"]) is False)
        add("doc_says_not_falsification", "not a Tau Core falsification" in doc)
        add("doc_says_no_survival", "No survival claim" in doc)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    ok = bool(out["Passed"].all())
    print("P_TAUCOV_PARENT_ACTION_SCORECARD_INTERPRETATION_VALID" if ok else "P_TAUCOV_PARENT_ACTION_SCORECARD_INTERPRETATION_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
