#!/usr/bin/env python3
"""Validate the frozen J_tau anchor candidate."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "evidence/p_taucov_tccs_jtau_anchor_candidate_matrix.csv"
SUMMARY = ROOT / "evidence/p_taucov_tccs_jtau_anchor_candidate_summary.csv"
DOC = ROOT / "docs/p_taucov_tccs_jtau_anchor_candidate.md"
OUT = ROOT / "evidence/p_taucov_tccs_jtau_anchor_candidate_validation.csv"

AUDIT_ID = "P_TAUCOV_TCCS_JTAU_ANCHOR_CANDIDATE_VALIDATION"
EXPECTED_STATUS = "P_TAUCOV_TCCS_JTAU_ANCHOR_CANDIDATE_FROZEN_NO_OBJECT_NO_SCORING"


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
    for path in [MATRIX, SUMMARY, DOC]:
        add(rows, f"exists_{path.relative_to(ROOT)}", path.exists())
    if not all(path.exists() for path in [MATRIX, SUMMARY, DOC]):
        pd.DataFrame(rows).to_csv(OUT, index=False)
        print("P_TAUCOV_TCCS_JTAU_ANCHOR_CANDIDATE_INVALID")
        return 1

    matrix_df = pd.read_csv(MATRIX)
    ids = list(matrix_df["coordinate_id"].astype(str))
    j = matrix_df[ids].to_numpy(dtype=float)
    summary = pd.read_csv(SUMMARY).iloc[0]
    doc = DOC.read_text(encoding="utf-8")

    add(rows, "status_expected", str(summary["Status"]) == EXPECTED_STATUS)
    add(rows, "matrix_square", j.shape[0] == j.shape[1])
    add(rows, "matrix_antisymmetric", float(np.max(np.abs(j + j.T))) < 1e-12)
    add(rows, "nonzero_anchor", float(np.linalg.norm(j)) > 0.0)
    add(rows, "trace_zero", abs(float(np.trace(j))) < 1e-12)
    add(rows, "uses_no_target_residuals", bool(summary["UsesTargetResiduals"]) is False)
    add(rows, "uses_no_score_outcomes", bool(summary["UsesScoreOutcomes"]) is False)
    add(rows, "uses_no_dominant_family", bool(summary["UsesDominantFamilyIdentity"]) is False)
    add(rows, "object_construction_not_authorized", bool(summary["ObjectConstructionAuthorized"]) is False)
    add(rows, "scoring_not_authorized", bool(summary["ScoringAuthorized"]) is False)
    add(rows, "survival_not_authorized", bool(summary["SurvivalClaimAuthorized"]) is False)
    add(rows, "tau_validation_not_authorized", bool(summary["TauCoreValidationClaimAuthorized"]) is False)
    add(rows, "doc_forbids_signal_claim", "produced a Tau signal" in doc)

    out = pd.DataFrame(rows)
    out.to_csv(OUT, index=False)
    ok = bool(out["Passed"].all())
    print("P_TAUCOV_TCCS_JTAU_ANCHOR_CANDIDATE_VALID" if ok else "P_TAUCOV_TCCS_JTAU_ANCHOR_CANDIDATE_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
