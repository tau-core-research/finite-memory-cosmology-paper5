#!/usr/bin/env python3
"""Validate TCCS operator assembly preflight."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
CHECKS = ROOT / "evidence/p_taucov_tccs_operator_assembly_preflight.csv"
SUMMARY = ROOT / "evidence/p_taucov_tccs_operator_assembly_preflight_summary.csv"
DOC = ROOT / "docs/p_taucov_tccs_operator_assembly_preflight.md"
OUT = ROOT / "evidence/p_taucov_tccs_operator_assembly_preflight_validation.csv"

AUDIT_ID = "P_TAUCOV_TCCS_OPERATOR_ASSEMBLY_PREFLIGHT_VALIDATION"
EXPECTED_STATUS = "P_TAUCOV_TCCS_OPERATOR_ASSEMBLY_BLOCKED_BY_PARENT_TO_SCORE_EMBEDDING"
REQUIRED_BLOCKERS = {"P_MORPH_OPERATOR_CONVENTION", "PI_PERP_ASSEMBLY", "PARENT_TO_SCORE_EMBEDDING"}


def add(rows: list[dict], check_id: str, passed: bool) -> None:
    rows.append(
        {
            "AuditID": AUDIT_ID,
            "CheckID": check_id,
            "Passed": bool(passed),
            "Required": True,
            "Status": "PASS" if passed else "FAIL",
        }
    )


def main() -> int:
    rows: list[dict] = []
    for path in [CHECKS, SUMMARY, DOC]:
        add(rows, f"exists_{path.relative_to(ROOT)}", path.exists())
    if not all(path.exists() for path in [CHECKS, SUMMARY, DOC]):
        pd.DataFrame(rows).to_csv(OUT, index=False)
        print("P_TAUCOV_TCCS_OPERATOR_ASSEMBLY_PREFLIGHT_INVALID")
        return 1

    checks = pd.read_csv(CHECKS)
    summary = pd.read_csv(SUMMARY).iloc[0]
    doc = DOC.read_text(encoding="utf-8")

    blockers = set(checks.loc[checks["BlocksObjectConstruction"].astype(bool), "CheckID"].astype(str))
    add(rows, "status_expected", str(summary["Status"]) == EXPECTED_STATUS)
    add(rows, "required_blockers_present", REQUIRED_BLOCKERS.issubset(blockers))
    add(rows, "object_construction_not_authorized", bool(summary["ObjectConstructionAuthorized"]) is False)
    add(rows, "scoring_not_authorized_checks", not bool(checks["ScoringAuthorized"].any()))
    add(rows, "scoring_not_authorized_summary", bool(summary["ScoringAuthorized"]) is False)
    add(rows, "survival_not_authorized", bool(summary["SurvivalClaimAuthorized"]) is False)
    add(rows, "tau_validation_not_authorized", bool(summary["TauCoreValidationClaimAuthorized"]) is False)
    add(rows, "doc_mentions_embedding_block", "parent-to-score embedding" in doc)
    add(rows, "doc_forbids_signal_claim", "shown to carry a Tau signal" in doc)

    out = pd.DataFrame(rows)
    out.to_csv(OUT, index=False)
    ok = bool(out["Passed"].all())
    print("P_TAUCOV_TCCS_OPERATOR_ASSEMBLY_PREFLIGHT_VALID" if ok else "P_TAUCOV_TCCS_OPERATOR_ASSEMBLY_PREFLIGHT_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
