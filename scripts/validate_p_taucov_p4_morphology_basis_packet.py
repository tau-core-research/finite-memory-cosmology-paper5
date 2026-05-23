#!/usr/bin/env python3
"""Validate the frozen P4 morphology basis packet."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
BASIS = ROOT / "evidence/p_taucov_p4_morphology_basis.csv"
SUMMARY = ROOT / "evidence/p_taucov_p4_morphology_basis_summary.csv"
DOC = ROOT / "docs/p_taucov_p4_morphology_basis_packet.md"
OUT = ROOT / "evidence/p_taucov_p4_morphology_basis_validation.csv"

AUDIT_ID = "P_TAUCOV_P4_MORPHOLOGY_BASIS_PACKET_VALIDATION"
EXPECTED = {
    "M_PARENT_MORPHOLOGY_DIAGONAL",
    "P_MORPH_PROJECTION_DIAGONAL",
    "M_P_SYMMETRIC_COUPLING",
}


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

    add(f"exists_{BASIS.relative_to(ROOT)}", BASIS.exists())
    add(f"exists_{SUMMARY.relative_to(ROOT)}", SUMMARY.exists())
    add(f"exists_{DOC.relative_to(ROOT)}", DOC.exists())
    if BASIS.exists() and SUMMARY.exists() and DOC.exists():
        basis = pd.read_csv(BASIS)
        summary = pd.read_csv(SUMMARY).iloc[0]
        doc = DOC.read_text(encoding="utf-8")
        add("status_frozen_no_scoring", str(summary["Status"]).endswith("FROZEN_NO_SCORING"))
        add("expected_basis_ids", set(basis["BasisID"].unique()) == EXPECTED)
        add("uses_no_target_residuals", not bool(basis["UsesTargetResiduals"].any()))
        add("uses_no_score_outcome", not bool(basis["UsesScoreOutcome"].any()))
        add("scoring_not_authorized", not bool(basis["ScoringAuthorized"].any()))
        add("summary_scoring_not_authorized", bool(summary["ScoringAuthorized"]) is False)
        add("orthogonal_basis", float(summary["MaxAbsOffDiagonalGram"]) < 1e-12)
        add("doc_contains_claim_boundary", "Claim Boundary" in doc)
        add("doc_forbids_scored_claim", "scored" in doc and "Tau-specific" in doc)

    out = pd.DataFrame(checks)
    out.to_csv(OUT, index=False)
    ok = bool(out.loc[out["Required"], "Passed"].all())
    print("P_TAUCOV_P4_MORPHOLOGY_BASIS_VALID" if ok else "P_TAUCOV_P4_MORPHOLOGY_BASIS_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
