#!/usr/bin/env python3
"""Validate the TCCS orientation-anchor spec."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = ROOT / "evidence/p_taucov_tccs_orientation_anchor_candidates.csv"
SUMMARY = ROOT / "evidence/p_taucov_tccs_orientation_anchor_summary.csv"
DOC = ROOT / "docs/p_taucov_tccs_orientation_anchor_spec.md"
OUT = ROOT / "evidence/p_taucov_tccs_orientation_anchor_validation.csv"

AUDIT_ID = "P_TAUCOV_TCCS_ORIENTATION_ANCHOR_SPEC_VALIDATION"
EXPECTED_STATUS = "P_TAUCOV_TCCS_ORIENTATION_ANCHOR_SPEC_DEFINED_NO_ANCHOR_FROZEN"
REQUIRED_ANCHORS = {
    "JTAU_A_PARENT_COMPLEX_STRUCTURE",
    "JTAU_B_BRANCH_ORDER_ORIENTATION",
    "JTAU_C_HESSIAN_SKEW_PAIRING",
}


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
    for path in [CANDIDATES, SUMMARY, DOC]:
        add(rows, f"exists_{path.relative_to(ROOT)}", path.exists())
    if not all(path.exists() for path in [CANDIDATES, SUMMARY, DOC]):
        pd.DataFrame(rows).to_csv(OUT, index=False)
        print("P_TAUCOV_TCCS_ORIENTATION_ANCHOR_SPEC_INVALID")
        return 1

    candidates = pd.read_csv(CANDIDATES)
    summary = pd.read_csv(SUMMARY).iloc[0]
    doc = DOC.read_text(encoding="utf-8")
    anchors = set(candidates["AnchorID"].astype(str))

    add(rows, "status_expected", str(summary["Status"]) == EXPECTED_STATUS)
    add(rows, "required_anchor_classes_present", REQUIRED_ANCHORS.issubset(anchors))
    add(rows, "no_anchor_can_freeze_now", not bool(candidates["CanFreezeNow"].any()))
    add(rows, "anchor_not_selected", bool(summary["AnchorSelected"]) is False)
    add(rows, "object_construction_not_authorized", bool(summary["ObjectConstructionAuthorized"]) is False)
    add(rows, "scoring_not_authorized_candidates", not bool(candidates["ScoringAuthorized"].any()))
    add(rows, "scoring_not_authorized_summary", bool(summary["ScoringAuthorized"]) is False)
    add(rows, "survival_not_authorized", bool(summary["SurvivalClaimAuthorized"]) is False)
    add(rows, "tau_validation_not_authorized", bool(summary["TauCoreValidationClaimAuthorized"]) is False)
    add(rows, "doc_forbids_score_based_flip", "Do not flip the commutator sign after seeing alignment" in doc)
    add(rows, "doc_forbids_empirical_validation_claim", "empirically validated" in doc)

    out = pd.DataFrame(rows)
    out.to_csv(OUT, index=False)
    ok = bool(out["Passed"].all())
    print("P_TAUCOV_TCCS_ORIENTATION_ANCHOR_SPEC_VALID" if ok else "P_TAUCOV_TCCS_ORIENTATION_ANCHOR_SPEC_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
