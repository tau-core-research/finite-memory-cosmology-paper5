#!/usr/bin/env python3
"""Validate parent-action P-TauCov primary scorecard outputs."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
IN_SAMPLE = ROOT / "evidence/p_taucov_parent_action_scorecard.csv"
OOS = ROOT / "evidence/p_taucov_parent_action_oos_scorecard.csv"
SUMMARY = ROOT / "evidence/p_taucov_parent_action_scorecard_summary.csv"
OUT = ROOT / "evidence/p_taucov_parent_action_scorecard_validation.csv"


def main() -> int:
    records: list[dict] = []

    def add(check_id: str, passed: bool) -> None:
        records.append({"AuditID": "P_TAUCOV_PARENT_ACTION_SCORECARD_VALIDATION", "CheckID": check_id, "Passed": bool(passed), "Required": True, "Status": "PASS" if passed else "FAIL"})

    for path in [IN_SAMPLE, OOS, SUMMARY]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())
    if all(path.exists() for path in [IN_SAMPLE, OOS, SUMMARY]):
        ins = pd.read_csv(IN_SAMPLE)
        oos = pd.read_csv(OOS)
        summary = pd.read_csv(SUMMARY).iloc[0]
        add("authorized_true", bool(summary["PTauCovScoringAuthorized"]) is True)
        add("survival_not_authorized", bool(summary["SurvivalClaimAuthorized"]) is False)
        add("measurement_not_authorized", bool(summary["MeasurementValidationAuthorized"]) is False)
        add("has_primary_oos", bool(oos["PrimaryOOS"].any()))
        add("summary_matches_oos", abs(float(summary["PrimaryOOSDeltaNLL_BaselineMinusKernel"]) - float(oos[oos["PrimaryOOS"]]["DeltaNLL_BaselineMinusKernel"].sum())) < 1e-9)
        add("in_sample_single_row", len(ins) == 1)
        add("claim_boundary_no_survival", str(summary["ClaimBoundary"]) == "parent_action_primary_scorecard_no_survival_claim")

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    ok = bool(out["Passed"].all())
    print("P_TAUCOV_PARENT_ACTION_SCORECARD_VALID" if ok else "P_TAUCOV_PARENT_ACTION_SCORECARD_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
