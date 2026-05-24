#!/usr/bin/env python3
"""Validate the P-TauCov embedding Q-clean support audit."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

FREEZE_ID = "P_TAUCOV_EMBEDDING_QCLEAN_SUPPORT_AUDIT_v1"
EXPECTED_STATUS = "P_TAUCOV_EMBEDDING_QCLEAN_SUPPORT_AUDIT_BLOCKS_CURRENT_EMBEDDING_NO_SCORING"

FILES = {
    "coords": EVIDENCE / "p_taucov_embedding_qclean_coordinate_support.csv",
    "pairs": EVIDENCE / "p_taucov_embedding_qclean_pair_support.csv",
    "summary": EVIDENCE / "p_taucov_embedding_qclean_support_audit_summary.csv",
    "validation": EVIDENCE / "p_taucov_embedding_qclean_support_audit_validation.csv",
    "doc": DOCS / "p_taucov_embedding_qclean_support_audit.md",
}


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
        coords = pd.read_csv(FILES["coords"])
        pairs = pd.read_csv(FILES["pairs"])
        summary = pd.read_csv(FILES["summary"]).iloc[0]
        doc = FILES["doc"].read_text(encoding="utf-8")
        add("status_expected", str(summary["Status"]) == EXPECTED_STATUS)
        add("eight_coordinates", len(coords) == 8)
        add("twenty_eight_pairs", len(pairs) == 28)
        add("current_embedding_blocks", bool(summary["CurrentEmbeddingBlocksParentDomainCurvatureSource"]))
        add("branch_support_below_threshold", float(summary["MaxBranchCoordinateSupportRatio"]) < 0.20)
        add("scoring_not_authorized", not bool(summary["ScoringAuthorized"]))
        add("survival_not_authorized", not bool(summary["SurvivalClaimAuthorized"]))
        add("tau_validation_not_authorized", not bool(summary["TauCoreValidationClaimAuthorized"]))
        add("doc_has_consequence", "parent-domain embedding" in doc and "domain metric" in doc)

    out = pd.DataFrame(checks)
    out.to_csv(FILES["validation"], index=False)
    ok = bool(out.loc[out["Required"], "Passed"].all())
    print("P_TAUCOV_EMBEDDING_QCLEAN_SUPPORT_AUDIT_VALID" if ok else "P_TAUCOV_EMBEDDING_QCLEAN_SUPPORT_AUDIT_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
