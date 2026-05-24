#!/usr/bin/env python3
"""Validate expanded parent-operator P-TauCov scorecard outputs."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
IN_SAMPLE = ROOT / "evidence/p_taucov_expanded_parent_operator_scorecard.csv"
OOS = ROOT / "evidence/p_taucov_expanded_parent_operator_oos_scorecard.csv"
NULLS = ROOT / "evidence/p_taucov_expanded_parent_operator_null_scorecard.csv"
GATES = ROOT / "evidence/p_taucov_expanded_parent_operator_survival_gates.csv"
SUMMARY = ROOT / "evidence/p_taucov_expanded_parent_operator_scorecard_summary.csv"
DOC = ROOT / "docs/p_taucov_expanded_parent_operator_scorecard.md"
OUT = ROOT / "evidence/p_taucov_expanded_parent_operator_scorecard_validation.csv"

AUDIT_ID = "P_TAUCOV_EXPANDED_PARENT_OPERATOR_SCORECARD_VALIDATION"
EXPECTED_STATUS = "P_TAUCOV_EXPANDED_PARENT_OPERATOR_PRIMARY_SCORECARD_DOES_NOT_SURVIVE_NO_CLAIM"


def main() -> int:
    records: list[dict] = []

    def add(check_id: str, passed: bool) -> None:
        records.append(
            {
                "AuditID": AUDIT_ID,
                "CheckID": check_id,
                "Passed": bool(passed),
                "Required": True,
                "Status": "PASS" if passed else "FAIL",
            }
        )

    for path in [IN_SAMPLE, OOS, NULLS, GATES, SUMMARY, DOC]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())

    if all(path.exists() for path in [IN_SAMPLE, OOS, NULLS, GATES, SUMMARY, DOC]):
        ins = pd.read_csv(IN_SAMPLE)
        oos = pd.read_csv(OOS)
        nulls = pd.read_csv(NULLS)
        gates = pd.read_csv(GATES)
        summary = pd.read_csv(SUMMARY).iloc[0]
        doc = DOC.read_text(encoding="utf-8")
        primary = oos[oos["PrimaryOOS"]]
        primary_delta = float(primary["DeltaNLL_BaselineMinusKernel"].sum())
        strongest_null = float(nulls["PrimaryOOSDeltaNLL_BaselineMinusKernel"].max())

        add("authorized_true", bool(summary["PTauCovScoringAuthorized"]) is True)
        add("survival_not_authorized", bool(summary["SurvivalClaimAuthorized"]) is False)
        add("measurement_not_authorized", bool(summary["MeasurementValidationAuthorized"]) is False)
        add("tau_validation_not_authorized", bool(summary["TauCoreValidationClaimAuthorized"]) is False)
        add("status_expected_non_survivor", str(summary["CurrentStatus"]) == EXPECTED_STATUS)
        add("has_in_sample_single_row", len(ins) == 1)
        add("has_primary_oos_rows", len(primary) > 0)
        add("summary_matches_oos", abs(float(summary["PrimaryOOSDeltaNLL_BaselineMinusKernel"]) - primary_delta) < 1e-9)
        add("summary_matches_strongest_null", abs(float(summary["StrongestNullPrimaryOOSDeltaNLL"]) - strongest_null) < 1e-9)
        add("all_required_nulls_present", len(nulls) == 11)
        add("gates_count_matches_summary", int(summary["GatesTotal"]) == len(gates) == 8)
        add("gates_passed_matches_summary", int(summary["GatesPassed"]) == int(gates["Passed"].sum()))
        add("null_defeat_gate_failed", not bool(gates.loc[gates["GateID"].eq("SURV-G5_BEATS_ALL_REQUIRED_NULLS"), "Passed"].iloc[0]))
        add("doc_forbids_validation_claim", "does not authorize survival language" in doc and "Tau Core validation claim" in doc)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    ok = bool(out["Passed"].all())
    print("P_TAUCOV_EXPANDED_PARENT_OPERATOR_SCORECARD_VALID" if ok else "P_TAUCOV_EXPANDED_PARENT_OPERATOR_SCORECARD_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
