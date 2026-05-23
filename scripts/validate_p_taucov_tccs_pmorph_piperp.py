#!/usr/bin/env python3
"""Validate TCCS P_morph and Pi_perp freeze."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PMORPH_PARENT = ROOT / "evidence/p_taucov_tccs_pmorph_parent_operator.csv"
PMORPH_SCORE = ROOT / "evidence/p_taucov_tccs_pmorph_score_operator.csv"
PIPERP = ROOT / "evidence/p_taucov_tccs_piperp_matrix.csv"
SUMMARY = ROOT / "evidence/p_taucov_tccs_pmorph_piperp_summary.csv"
DOC = ROOT / "docs/p_taucov_tccs_pmorph_piperp.md"
OUT = ROOT / "evidence/p_taucov_tccs_pmorph_piperp_validation.csv"

AUDIT_ID = "P_TAUCOV_TCCS_PMORPH_PIPERP_VALIDATION"
EXPECTED_STATUS = "P_TAUCOV_TCCS_PMORPH_PIPERP_FROZEN_NO_OBJECT_NO_SCORING"


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


def sparse_to_matrix(path: Path) -> tuple[np.ndarray, list[str]]:
    df = pd.read_csv(path)
    ids = sorted(set(df["RowID"].astype(str)).union(set(df["ColumnID"].astype(str))))
    index = {row_id: i for i, row_id in enumerate(ids)}
    mat = np.zeros((len(ids), len(ids)), dtype=float)
    for _, row in df.iterrows():
        mat[index[str(row["RowID"])]][index[str(row["ColumnID"])]] = float(row["Value"])
    return mat, ids


def main() -> int:
    rows: list[dict] = []
    for path in [PMORPH_PARENT, PMORPH_SCORE, PIPERP, SUMMARY, DOC]:
        add(rows, f"exists_{path.relative_to(ROOT)}", path.exists())
    if not all(path.exists() for path in [PMORPH_PARENT, PMORPH_SCORE, PIPERP, SUMMARY, DOC]):
        pd.DataFrame(rows).to_csv(OUT, index=False)
        print("P_TAUCOV_TCCS_PMORPH_PIPERP_INVALID")
        return 1

    p_parent, _ = sparse_to_matrix(PMORPH_PARENT)
    piperp, _ = sparse_to_matrix(PIPERP)
    summary = pd.read_csv(SUMMARY).iloc[0]
    doc = DOC.read_text(encoding="utf-8")

    add(rows, "status_expected", str(summary["Status"]) == EXPECTED_STATUS)
    add(rows, "parent_pmorph_symmetric", float(np.max(np.abs(p_parent - p_parent.T))) < 1e-12)
    add(rows, "parent_pmorph_idempotent", float(np.max(np.abs(p_parent @ p_parent - p_parent))) < 1e-12)
    add(rows, "piperp_symmetric", float(np.max(np.abs(piperp - piperp.T))) < 1e-12)
    add(rows, "piperp_idempotent", float(np.max(np.abs(piperp @ piperp - piperp))) < 1e-12)
    add(rows, "piperp_rank_34", int(summary["PiPerpRank"]) == 34)
    add(rows, "nuisance_leakage_zero", float(summary["NuisanceLeakageNorm"]) < 1e-12)
    add(rows, "no_target_residuals", bool(summary["UsesTargetResiduals"]) is False)
    add(rows, "no_score_outcomes", bool(summary["UsesScoreOutcomes"]) is False)
    add(rows, "object_construction_not_authorized", bool(summary["ObjectConstructionAuthorized"]) is False)
    add(rows, "scoring_not_authorized", bool(summary["ScoringAuthorized"]) is False)
    add(rows, "survival_not_authorized", bool(summary["SurvivalClaimAuthorized"]) is False)
    add(rows, "tau_validation_not_authorized", bool(summary["TauCoreValidationClaimAuthorized"]) is False)
    add(rows, "doc_forbids_signal_claim", "produce a Tau signal" in doc)

    out = pd.DataFrame(rows)
    out.to_csv(OUT, index=False)
    ok = bool(out["Passed"].all())
    print("P_TAUCOV_TCCS_PMORPH_PIPERP_VALID" if ok else "P_TAUCOV_TCCS_PMORPH_PIPERP_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
