#!/usr/bin/env python3
"""Validate the P-TauCov branch-equation completion audit."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "evidence/p_taucov_branch_equation_completion_audit.csv"
SUMMARY = ROOT / "evidence/p_taucov_branch_equation_completion_audit_summary.csv"
DOC = ROOT / "docs/p_taucov_branch_equation_completion_audit.md"
OUT = ROOT / "evidence/p_taucov_branch_equation_completion_audit_validation.csv"

AUDIT_ID = "P_TAUCOV_BRANCH_EQUATION_COMPLETION_AUDIT_VALIDATION"


def main() -> int:
    checks: list[dict] = []

    def add(check_id: str, passed: bool, required: bool = True) -> None:
        checks.append(
            {
                "AuditID": AUDIT_ID,
                "CheckID": check_id,
                "Passed": bool(passed),
                "Required": bool(required),
                "Status": "PASS" if passed else "FAIL",
            }
        )

    for path in [AUDIT, SUMMARY, DOC]:
        add(f"exists_{path.relative_to(ROOT)}", path.exists())

    if all(path.exists() for path in [AUDIT, SUMMARY, DOC]):
        audit = pd.read_csv(AUDIT)
        summary = pd.read_csv(SUMMARY).iloc[0]
        doc = DOC.read_text(encoding="utf-8")

        add("status_no_scoring", str(summary["Status"]).endswith("NO_SCORING"))
        add("l_b_red_computable", abs(float(summary["L_B_red"])) > 1e-12)
        add("direct_forcing_not_falsely_complete", bool(summary["DirectBranchForcingComplete"]) is False)
        add("mediated_path_recorded", bool(summary["MediatedParentPathExists"]) is True)
        add("remaining_blocker_declared", "DIRECT_D_PHI_F_B" in str(summary["RemainingBlockers"]))
        add("scoring_not_authorized", bool(summary["ScoringAuthorized"]) is False)
        add("survival_not_authorized", bool(summary["SurvivalClaimAuthorized"]) is False)
        add("tau_validation_not_authorized", bool(summary["TauCoreValidationClaimAuthorized"]) is False)
        add("audit_has_expected_gate_count", len(audit) == 8)
        add("doc_states_forbidden_claim", "Forbidden statement" in doc and "Tau Core has been validated" in doc)

    out = pd.DataFrame(checks)
    out.to_csv(OUT, index=False)
    ok = bool(out.loc[out["Required"], "Passed"].all())
    print("P_TAUCOV_BRANCH_EQUATION_COMPLETION_AUDIT_VALID" if ok else "P_TAUCOV_BRANCH_EQUATION_COMPLETION_AUDIT_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
