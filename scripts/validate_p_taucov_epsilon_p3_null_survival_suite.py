#!/usr/bin/env python3
"""Validate epsilon-P3 null/survival suite outputs."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SCORECARD = ROOT / "evidence/p_taucov_epsilon_p3_null_suite_scorecard.csv"
GATES = ROOT / "evidence/p_taucov_epsilon_p3_survival_gate_results.csv"
SUMMARY = ROOT / "evidence/p_taucov_epsilon_p3_null_survival_summary.csv"
DOC = ROOT / "docs/p_taucov_epsilon_p3_null_survival_suite.md"
OUT = ROOT / "evidence/p_taucov_epsilon_p3_null_survival_validation.csv"


def bool_from_csv(value: object) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "pass"}


def main() -> int:
    records = []

    def add(check_id: str, passed: bool, required: bool = True) -> None:
        records.append({"AuditID": "P_TAUCOV_EPSILON_P3_NULL_SURVIVAL_VALIDATION", "CheckID": check_id, "Passed": bool(passed), "Required": bool(required), "Status": "PASS" if passed else "FAIL"})

    for path in [SCORECARD, GATES, SUMMARY, DOC]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())
    if not all(path.exists() for path in [SCORECARD, GATES, SUMMARY, DOC]):
        pd.DataFrame(records).to_csv(OUT, index=False)
        print("P_TAUCOV_EPSILON_P3_NULL_SURVIVAL_INVALID")
        return 1

    score = pd.read_csv(SCORECARD)
    gates = pd.read_csv(GATES)
    summary = pd.read_csv(SUMMARY).iloc[0]
    text = DOC.read_text(encoding="utf-8")
    status = str(summary["Status"])

    add("primary_positive", float(summary["PrimaryOOSDeltaNLL"]) > 0.0)
    add("survival_not_allowed", not bool_from_csv(summary["SurvivalClaimAllowed"]))
    add("measurement_not_allowed", not bool_from_csv(summary["MeasurementValidationAllowed"]))
    add("status_no_survival", status == "P_TAUCOV_EPSILON_P3_PRIMARY_POSITIVE_BUT_NO_SURVIVAL")
    add("gates_4_of_7", int(summary["GatesPassed"]) == 4 and int(summary["GatesTotal"]) == 7)
    add("morphology_null_strongest", str(summary["StrongestNullID"]) == "MORPHOLOGY_NULL")
    add("has_failed_gate", not gates["Passed"].map(bool_from_csv).all())
    add("scorecard_has_primary_and_nulls", {"TAU_EPSILON_P3_PRIMARY", "MORPHOLOGY_NULL", "OUTSIDE_BRANCH", "SHUFFLED_SUPPORT"}.issubset(set(score["KernelID"].astype(str))))
    for phrase in ["PRIMARY_POSITIVE_BUT_NO_SURVIVAL", "Measurement validation remains forbidden"]:
        add(f"doc_contains_{phrase[:40]}", phrase in text)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    failed = out[out["Required"] & ~out["Passed"]]
    if not failed.empty:
        print("P_TAUCOV_EPSILON_P3_NULL_SURVIVAL_INVALID")
        print(failed.to_string(index=False))
        return 1
    print("P_TAUCOV_EPSILON_P3_NULL_SURVIVAL_VALID_PRIMARY_POSITIVE_BUT_NO_SURVIVAL")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
