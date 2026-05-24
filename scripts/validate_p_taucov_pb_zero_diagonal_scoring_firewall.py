#!/usr/bin/env python3
"""Validate the PB zero-diagonal scoring firewall."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

FREEZE_ID = "P_TAUCOV_PB_ZERO_DIAGONAL_SCORING_FIREWALL_v1"
EXPECTED_STATUS = "P_TAUCOV_PB_ZERO_DIAGONAL_SCORING_FIREWALL_BLOCKED"

FILES = {
    "table": EVIDENCE / "p_taucov_pb_zero_diagonal_scoring_firewall.csv",
    "summary": EVIDENCE / "p_taucov_pb_zero_diagonal_scoring_firewall_summary.csv",
    "doc": DOCS / "p_taucov_pb_zero_diagonal_scoring_firewall.md",
}
OUT = EVIDENCE / "p_taucov_pb_zero_diagonal_scoring_firewall_validation.csv"


def main() -> int:
    checks: list[dict] = []

    def add(check_id: str, passed: bool, required: bool = True) -> None:
        checks.append(
            {
                "FreezeID": FREEZE_ID,
                "CheckID": check_id,
                "Passed": bool(passed),
                "Required": bool(required),
                "Status": "PASS" if passed else "FAIL",
            }
        )

    for key, path in FILES.items():
        add(f"exists_{key}", path.exists())
    if all(path.exists() for path in FILES.values()):
        table = pd.read_csv(FILES["table"])
        summary = pd.read_csv(FILES["summary"]).iloc[0]
        doc = FILES["doc"].read_text(encoding="utf-8")
        add("status_blocked", str(summary["Status"]) == EXPECTED_STATUS)
        add("object_items_satisfied", bool(table.loc[table["FirewallItemID"].isin(["PB-FW1_OBJECT_FROZEN", "PB-FW2_OBJECT_VALIDATION_PASS", "PB-FW3_OBJECT_HASH_READY"]), "Satisfied"].all()))
        add("policy_items_missing", bool((~table.loc[table["FirewallItemID"].str.startswith("PB-FW_POLICY_"), "Satisfied"]).all()))
        add("scoring_not_authorized", not bool(summary["ScoringAuthorized"]))
        add("survival_not_authorized", not bool(summary["SurvivalClaimAuthorized"]))
        add("tau_validation_not_authorized", not bool(summary["TauCoreValidationClaimAuthorized"]))
        add("doc_links_object_freeze", "p_taucov_pb_zero_diagonal_object_freeze.md" in doc)
        add("doc_forbids_scoring", "authorizes scoring" in doc)

    out = pd.DataFrame(checks)
    out.to_csv(OUT, index=False)
    ok = bool(out.loc[out["Required"], "Passed"].all())
    print("P_TAUCOV_PB_ZERO_DIAGONAL_SCORING_FIREWALL_VALID" if ok else "P_TAUCOV_PB_ZERO_DIAGONAL_SCORING_FIREWALL_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
