#!/usr/bin/env python3
"""Validate epsilon_P3 P-TauCov specificity prescore output."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/p_taucov_epsilon_p3_specificity_prescore.md"
CSV = ROOT / "evidence/p_taucov_epsilon_p3_specificity_prescore.csv"
SUMMARY = ROOT / "evidence/p_taucov_epsilon_p3_specificity_prescore_summary.csv"
MODEL_VALIDATION = ROOT / "evidence/p_taucov_epsilon_p3_model_packet_validation.csv"
OUT = ROOT / "evidence/p_taucov_epsilon_p3_specificity_prescore_validation.csv"


def bool_from_csv(value: object) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "pass"}


def main() -> int:
    records = []

    def add(check_id: str, passed: bool, required: bool = True) -> None:
        records.append(
            {
                "AuditID": "P_TAUCOV_EPSILON_P3_SPECIFICITY_PRESCORE_VALIDATION",
                "CheckID": check_id,
                "Passed": bool(passed),
                "Required": bool(required),
                "Status": "PASS" if passed else "FAIL",
            }
        )

    for path in [DOC, CSV, SUMMARY, MODEL_VALIDATION]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())
    if not all(path.exists() for path in [DOC, CSV, SUMMARY, MODEL_VALIDATION]):
        pd.DataFrame(records).to_csv(OUT, index=False)
        print("P_TAUCOV_EPSILON_P3_SPECIFICITY_PRESCORE_INVALID")
        return 1

    text = DOC.read_text(encoding="utf-8")
    df = pd.read_csv(CSV)
    summary = pd.read_csv(SUMMARY)
    model_validation = pd.read_csv(MODEL_VALIDATION)
    status = str(summary["Status"].iloc[0])

    add("model_packet_validation_passed", model_validation["Passed"].map(bool_from_csv).all())
    add("status_valid", status in {"BLOCKED", "PASS_NOT_FROZEN", "FAIL_EPSILON_P3_NOT_SPECIFIC"})
    add("metrics_evaluated_if_not_blocked", (status == "BLOCKED") or bool_from_csv(summary["MetricsEvaluated"].iloc[0]))
    add("metric_count_six", len(df) == 6)
    add("candidate_not_frozen", not bool_from_csv(summary["EpsilonP3CandidateFrozen"].iloc[0]))
    add("scoring_not_authorized", not bool_from_csv(summary["PTauCovScoringAuthorized"].iloc[0]))
    add("no_target_residuals", not df["UsesTargetResiduals"].map(bool_from_csv).any())
    add("no_p5c_v3_outcome", not df["UsesP5Cv3Outcome"].map(bool_from_csv).any())
    add("all_rows_pass_or_fail_or_blocked", set(df["Status"]).issubset({"PASS", "FAIL", "BLOCKED"}))

    for phrase in [
        "T_tau_epsilon",
        "epsilon_P P3",
        "PTauCovScoringAuthorized: false",
        "Forbidden statement",
    ]:
        add(f"doc_contains_{phrase[:40]}", phrase in text)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    failed = out[out["Required"] & ~out["Passed"]]
    if not failed.empty:
        print("P_TAUCOV_EPSILON_P3_SPECIFICITY_PRESCORE_INVALID")
        print(failed.to_string(index=False))
        return 1

    if status == "PASS_NOT_FROZEN":
        print("P_TAUCOV_EPSILON_P3_SPECIFICITY_PRESCORE_VALID_PASS_NOT_FROZEN")
    elif status == "FAIL_EPSILON_P3_NOT_SPECIFIC":
        print("P_TAUCOV_EPSILON_P3_SPECIFICITY_PRESCORE_VALID_FAIL_NOT_SPECIFIC")
    else:
        print("P_TAUCOV_EPSILON_P3_SPECIFICITY_PRESCORE_VALID_BLOCKED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
