#!/usr/bin/env python3
"""Validate epsilon-P3 bridge-projected primary scorecard."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
AUTH = ROOT / "evidence/p_taucov_epsilon_p3_final_authorization.yaml"
INS = ROOT / "evidence/p_taucov_epsilon_p3_alignment_scorecard.csv"
OOS = ROOT / "evidence/p_taucov_epsilon_p3_alignment_oos_scorecard.csv"
SUMMARY = ROOT / "evidence/p_taucov_epsilon_p3_alignment_scorecard_summary.csv"
OUT = ROOT / "evidence/p_taucov_epsilon_p3_alignment_scorecard_validation.csv"


def bool_from_csv(value: object) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "pass"}


def main() -> int:
    records = []

    def add(check_id: str, passed: bool, required: bool = True) -> None:
        records.append({"AuditID": "P_TAUCOV_EPSILON_P3_ALIGNMENT_SCORECARD_VALIDATION", "CheckID": check_id, "Passed": bool(passed), "Required": bool(required), "Status": "PASS" if passed else "FAIL"})

    for path in [AUTH, INS, OOS, SUMMARY]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())
    if not all(path.exists() for path in [AUTH, INS, OOS, SUMMARY]):
        pd.DataFrame(records).to_csv(OUT, index=False)
        print("P_TAUCOV_EPSILON_P3_ALIGNMENT_SCORECARD_INVALID")
        return 1

    auth = yaml.safe_load(AUTH.read_text(encoding="utf-8")) or {}
    ins = pd.read_csv(INS)
    oos = pd.read_csv(OOS)
    summary = pd.read_csv(SUMMARY).iloc[0]
    primary = oos[oos["PrimaryOOS"].map(bool_from_csv)]

    add("authorization_scoring_true", auth.get("PTauCovScoringAuthorized") is True)
    add("survival_not_authorized", auth.get("SurvivalClaimAuthorized") is False)
    add("measurement_not_authorized", auth.get("MeasurementValidationAuthorized") is False)
    add("in_sample_one_row", len(ins) == 1)
    add("oos_rows_present", len(oos) >= 6)
    add("primary_rows_six", len(primary) == 6)
    add("summary_scoring_authorized", bool_from_csv(summary["PTauCovScoringAuthorized"]))
    add("summary_primary_positive", float(summary["PrimaryOOSDeltaNLL_BaselineMinusKernel"]) > 0.0)
    add("summary_no_survival_claim_column_absent", "SurvivalClaimAuthorized" not in summary.index)

    status = "PRIMARY_POSITIVE_NO_SURVIVAL_CLAIM" if float(summary["PrimaryOOSDeltaNLL_BaselineMinusKernel"]) > 0.0 else "PRIMARY_NONPOSITIVE_NO_SURVIVAL_CLAIM"
    pd.DataFrame(records).to_csv(OUT, index=False)
    failed = pd.DataFrame(records)
    failed = failed[failed["Required"] & ~failed["Passed"]]
    if not failed.empty:
        print("P_TAUCOV_EPSILON_P3_ALIGNMENT_SCORECARD_INVALID")
        print(failed.to_string(index=False))
        return 1
    print(f"P_TAUCOV_EPSILON_P3_ALIGNMENT_SCORECARD_VALID_{status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
