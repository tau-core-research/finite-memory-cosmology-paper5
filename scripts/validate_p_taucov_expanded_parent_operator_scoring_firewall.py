#!/usr/bin/env python3
"""Validate the expanded parent-operator scoring firewall."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
TABLE = ROOT / "evidence/p_taucov_expanded_parent_operator_scoring_firewall.csv"
SUMMARY = ROOT / "evidence/p_taucov_expanded_parent_operator_scoring_firewall_summary.csv"
DOC = ROOT / "docs/p_taucov_expanded_parent_operator_scoring_firewall.md"
OUT = ROOT / "evidence/p_taucov_expanded_parent_operator_scoring_firewall_validation.csv"

AUDIT_ID = "P_TAUCOV_EXPANDED_PARENT_OPERATOR_SCORING_FIREWALL_VALIDATION"


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

    for path in [TABLE, SUMMARY, DOC]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())

    if all(path.exists() for path in [TABLE, SUMMARY, DOC]):
        table = pd.read_csv(TABLE)
        summary = pd.read_csv(SUMMARY).iloc[0]
        doc = DOC.read_text(encoding="utf-8")
        missing = set(str(summary["MissingItems"]).split(";"))

        add("status_blocked_freeze_required", str(summary["Status"]) == "P_TAUCOV_EXPANDED_PARENT_OPERATOR_SCORING_BLOCKED_FREEZE_REQUIRED")
        add("structural_items_satisfied", int(summary["SatisfiedItems"]) == 4)
        add("scorecard_missing", "ESO-FW5_SCORECARD_SCRIPT_FROZEN" in missing)
        add("fold_policy_missing", "ESO-FW6_FOLD_POLICY_FROZEN" in missing)
        add("null_policy_missing", "ESO-FW7_NULL_COMPARATORS_FROZEN" in missing)
        add("df_policy_missing", "ESO-FW8_DF_COVARIANCE_POLICY_FROZEN" in missing)
        add("survival_gates_missing", "ESO-FW9_SURVIVAL_KILL_GATES_FROZEN" in missing)
        add("final_manifest_missing", "ESO-FW10_FINAL_MANIFEST_READY" in missing)
        add("hashes_present", all(str(summary[col]) for col in ["CandidateSHA256", "SourceSHA256", "DomainSHA256"]))
        add("scoring_not_authorized", bool(summary["ScoringAuthorized"]) is False)
        add("survival_not_authorized", bool(summary["SurvivalClaimAuthorized"]) is False)
        add("tau_validation_not_authorized", bool(summary["TauCoreValidationClaimAuthorized"]) is False)
        add("uses_no_target_residuals", not bool(table["UsesTargetResiduals"].any()))
        add("uses_no_score_outcomes", not bool(table["UsesScoreOutcome"].any()))
        add("doc_states_forbidden_scoring", "authorizes empirical scoring" in doc)

    out = pd.DataFrame(records)
    out.to_csv(OUT, index=False)
    ok = bool(out["Passed"].all())
    print("P_TAUCOV_EXPANDED_PARENT_OPERATOR_SCORING_FIREWALL_VALID" if ok else "P_TAUCOV_EXPANDED_PARENT_OPERATOR_SCORING_FIREWALL_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
