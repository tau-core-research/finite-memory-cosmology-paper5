#!/usr/bin/env python3
"""Validate the TCCS parent-to-score embedding freeze."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "evidence/p_taucov_tccs_parent_score_embedding_matrix.csv"
SUMMARY = ROOT / "evidence/p_taucov_tccs_parent_score_embedding_summary.csv"
MANIFEST = ROOT / "evidence/p_taucov_tccs_parent_score_embedding.yaml"
SHA = ROOT / "evidence/p_taucov_tccs_parent_score_embedding.sha256"
DOC = ROOT / "docs/p_taucov_tccs_parent_score_embedding.md"
OUT = ROOT / "evidence/p_taucov_tccs_parent_score_embedding_validation.csv"

AUDIT_ID = "P_TAUCOV_TCCS_PARENT_SCORE_EMBEDDING_VALIDATION"
EXPECTED_STATUS = "P_TAUCOV_TCCS_PARENT_SCORE_EMBEDDING_FROZEN_NO_OBJECT_NO_SCORING"


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
    for path in [MATRIX, SUMMARY, MANIFEST, SHA, DOC]:
        add(rows, f"exists_{path.relative_to(ROOT)}", path.exists())
    if not all(path.exists() for path in [MATRIX, SUMMARY, MANIFEST, SHA, DOC]):
        pd.DataFrame(rows).to_csv(OUT, index=False)
        print("P_TAUCOV_TCCS_PARENT_SCORE_EMBEDDING_INVALID")
        return 1

    matrix_df = pd.read_csv(MATRIX)
    summary = pd.read_csv(SUMMARY).iloc[0]
    coords = list(dict.fromkeys(matrix_df["TauCoordinate"].astype(str).tolist()))
    row_ids = list(dict.fromkeys(matrix_df["EmpiricalRowID"].astype(str).tolist()))
    pivot = matrix_df.pivot(index="EmpiricalRowID", columns="TauCoordinate", values="EmbeddingValue").loc[row_ids, coords]
    mat = pivot.to_numpy(float)
    doc = DOC.read_text(encoding="utf-8")

    add(rows, "status_expected", str(summary["Status"]) == EXPECTED_STATUS)
    add(rows, "empirical_rows_36", int(summary["EmpiricalRows"]) == 36 and mat.shape[0] == 36)
    add(rows, "tau_coordinates_8", int(summary["TauCoordinates"]) == 8 and mat.shape[1] == 8)
    add(rows, "active_columns_4", int(summary["ActiveEmbeddingColumns"]) == 4)
    add(rows, "rank_4", int(summary["EmbeddingRank"]) == 4 and int(np.linalg.matrix_rank(mat)) == 4)
    add(rows, "low_active_column_correlation", float(summary["MaxAbsActiveColumnCorrelation"]) < 0.05)
    add(rows, "no_target_residuals", bool(summary["UsesTargetResiduals"]) is False)
    add(rows, "no_score_outcomes", bool(summary["UsesScoreOutcomes"]) is False)
    add(rows, "object_construction_not_authorized", bool(summary["ObjectConstructionAuthorized"]) is False)
    add(rows, "scoring_not_authorized", bool(summary["ScoringAuthorized"]) is False)
    add(rows, "survival_not_authorized", bool(summary["SurvivalClaimAuthorized"]) is False)
    add(rows, "tau_validation_not_authorized", bool(summary["TauCoreValidationClaimAuthorized"]) is False)
    add(rows, "doc_forbids_signal_claim", "produces a Tau signal" in doc)

    out = pd.DataFrame(rows)
    out.to_csv(OUT, index=False)
    ok = bool(out["Passed"].all())
    print("P_TAUCOV_TCCS_PARENT_SCORE_EMBEDDING_VALID" if ok else "P_TAUCOV_TCCS_PARENT_SCORE_EMBEDDING_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
