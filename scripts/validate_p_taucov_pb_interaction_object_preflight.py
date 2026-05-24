#!/usr/bin/env python3
"""Validate the P-TauCov PB interaction object preflight."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

FREEZE_ID = "P_TAUCOV_PB_INTERACTION_OBJECT_PREFLIGHT_v1"
ALLOWED_STATUSES = {
    "P_TAUCOV_PB_INTERACTION_OBJECT_PREFLIGHT_HAS_CANDIDATE_NO_SCORING",
    "P_TAUCOV_PB_INTERACTION_OBJECT_PREFLIGHT_BLOCKED_NO_SCORING",
}

FILES = {
    "matrix": EVIDENCE / "p_taucov_pb_interaction_object_preflight_matrix.csv",
    "audit": EVIDENCE / "p_taucov_pb_interaction_object_preflight.csv",
    "summary": EVIDENCE / "p_taucov_pb_interaction_object_preflight_summary.csv",
    "doc": DOCS / "p_taucov_pb_interaction_object_preflight.md",
}
OUT = EVIDENCE / "p_taucov_pb_interaction_object_preflight_validation.csv"


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
        matrix = pd.read_csv(FILES["matrix"])
        audit = pd.read_csv(FILES["audit"])
        summary = pd.read_csv(FILES["summary"]).iloc[0]
        doc = FILES["doc"].read_text(encoding="utf-8")
        add("status_allowed", str(summary["Status"]) in ALLOWED_STATUSES)
        add("four_object_candidates", len(audit) == 4)
        add("matrix_has_four_candidates", matrix["ObjectCandidateID"].nunique() == 4)
        add("object_freeze_not_authorized", not bool(summary["ObjectFreezeAuthorized"]))
        add("scoring_not_authorized", not bool(summary["ScoringAuthorized"]))
        add("survival_not_authorized", not bool(summary["SurvivalClaimAuthorized"]))
        add("tau_validation_not_authorized", not bool(summary["TauCoreValidationClaimAuthorized"]))
        add("cleaned_candidate_not_parent_source", not bool(audit.loc[audit["ObjectCandidateID"].eq("PB_QCLEAN_RESTRICTED_OUTER_PRODUCT"), "ParentSourceAllowed"].iloc[0]))
        add("cross_family_candidate_not_parent_source", not bool(audit.loc[audit["ObjectCandidateID"].eq("PB_CROSS_FAMILY_ONLY_DIAGNOSTIC"), "ParentSourceAllowed"].iloc[0]))
        add("zero_diagonal_is_best_passing_candidate", str(summary["BestPassingObjectCandidateID"]) == "PB_ZERO_DIAGONAL_OUTER_PRODUCT")
        add("best_matches_audit", str(summary["BestObjectCandidateID"]) == str(audit.iloc[0]["ObjectCandidateID"]))
        add("doc_links_coordinate_freeze", "p_taucov_pb_interaction_coordinate_freeze.md" in doc)
        add("doc_forbids_scoring", "scoring is authorized" in doc)

    out = pd.DataFrame(checks)
    out.to_csv(OUT, index=False)
    ok = bool(out.loc[out["Required"], "Passed"].all())
    print("P_TAUCOV_PB_INTERACTION_OBJECT_PREFLIGHT_VALID" if ok else "P_TAUCOV_PB_INTERACTION_OBJECT_PREFLIGHT_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
