#!/usr/bin/env python3
"""Validate the TCCS readiness matrix."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "evidence/p_taucov_tccs_readiness_matrix.csv"
SUMMARY = ROOT / "evidence/p_taucov_tccs_readiness_summary.csv"
DOC = ROOT / "docs/p_taucov_tccs_readiness_matrix.md"
OUT = ROOT / "evidence/p_taucov_tccs_readiness_validation.csv"

AUDIT_ID = "P_TAUCOV_TCCS_READINESS_MATRIX_VALIDATION"
EXPECTED_STATUS = "P_TAUCOV_TCCS_READY_AS_PROTOCOL_OBJECT_BLOCKED_NO_SCORING"


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
        print("P_TAUCOV_TCCS_READINESS_MATRIX_INVALID")
        return 1

    matrix = pd.read_csv(MATRIX)
    summary = pd.read_csv(SUMMARY).iloc[0]
    doc = DOC.read_text(encoding="utf-8")

    add(rows, "status_expected", str(summary["Status"]) == EXPECTED_STATUS)
    add(rows, "all_layers_ready", bool(summary["AllLayersReady"]) is True)
    add(rows, "object_construction_not_authorized", bool(summary["ObjectConstructionAuthorized"]) is False)
    add(rows, "scoring_not_authorized", bool(summary["ScoringAuthorized"]) is False)
    add(rows, "survival_not_authorized", bool(summary["SurvivalClaimAuthorized"]) is False)
    add(rows, "tau_validation_not_authorized", bool(summary["TauCoreValidationClaimAuthorized"]) is False)
    add(rows, "source_registry_blocks_object", bool(matrix[matrix["LayerID"].eq("TCCS_SOURCE_REGISTRY")]["BlocksObjectConstruction"].iloc[0]) is True)
    add(rows, "orientation_anchor_blocks_object", bool(matrix[matrix["LayerID"].eq("TCCS_ORIENTATION_ANCHOR")]["BlocksObjectConstruction"].iloc[0]) is True)
    add(rows, "doc_says_not_scoring", "not scoring" in doc and "not authorized" in doc)
    add(rows, "doc_forbids_empirical_tau_signal", "empirical Tau signal" in doc)

    out = pd.DataFrame(rows)
    out.to_csv(OUT, index=False)
    ok = bool(out["Passed"].all())
    print("P_TAUCOV_TCCS_READINESS_MATRIX_VALID" if ok else "P_TAUCOV_TCCS_READINESS_MATRIX_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
