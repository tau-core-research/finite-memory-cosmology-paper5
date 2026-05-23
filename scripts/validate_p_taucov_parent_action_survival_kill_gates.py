#!/usr/bin/env python3
"""Validate parent-action P-TauCov survival and kill gates."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
GATES = ROOT / "evidence/p_taucov_parent_action_survival_kill_gates.csv"
SUMMARY = ROOT / "evidence/p_taucov_parent_action_survival_kill_gates_summary.csv"
DOC = ROOT / "docs/p_taucov_parent_action_survival_kill_gates.md"
OUT = ROOT / "evidence/p_taucov_parent_action_survival_kill_gates_validation.csv"


def main() -> int:
    records: list[dict] = []

    def add(check_id: str, passed: bool) -> None:
        records.append({"AuditID": "P_TAUCOV_PARENT_ACTION_SURVIVAL_KILL_GATES_VALIDATION", "CheckID": check_id, "Passed": bool(passed), "Required": True, "Status": "PASS" if passed else "FAIL"})

    for path in [GATES, SUMMARY, DOC]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())
    if all(path.exists() for path in [GATES, SUMMARY, DOC]):
        gates = pd.read_csv(GATES)
        summary = pd.read_csv(SUMMARY).iloc[0]
        doc = DOC.read_text(encoding="utf-8")
        gate_ids = set(gates["GateID"])
        add("status_frozen", str(summary["Status"]) == "P_TAUCOV_PARENT_ACTION_SURVIVAL_KILL_GATES_FROZEN_NO_SCORING")
        add("has_survival_gates", int(summary["SurvivalGates"]) >= 7)
        add("has_kill_gates", int(summary["KillGates"]) >= 5)
        add("required_null_defeat_present", "SURV-G4_BEATS_ALL_REQUIRED_NULLS" in gate_ids)
        add("single_family_kill_present", "KILL-K3_SINGLE_FAMILY_DOMINANCE" in gate_ids)
        add("no_target_policy", not bool(gates["TargetResidualsUsedForPolicy"].any()))
        add("no_score_policy", not bool(gates["ScoreOutcomeUsedForPolicy"].any()))
        add("scoring_not_authorized", bool(summary["PTauCovScoringAuthorized"]) is False)
        add("measurement_not_allowed", bool(summary["MeasurementValidationAllowed"]) is False)
        add("doc_mentions_before_scoring", "frozen before scoring" in doc)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    ok = bool(out["Passed"].all())
    print("P_TAUCOV_PARENT_ACTION_SURVIVAL_KILL_GATES_VALID" if ok else "P_TAUCOV_PARENT_ACTION_SURVIVAL_KILL_GATES_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
