#!/usr/bin/env python3
"""Validate the frozen PB zero-diagonal object."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

FREEZE_ID = "P_TAUCOV_PB_ZERO_DIAGONAL_OBJECT_FREEZE_v1"
EXPECTED_STATUS = "P_TAUCOV_PB_ZERO_DIAGONAL_OBJECT_FROZEN_NO_SCORING"

FILES = {
    "matrix": EVIDENCE / "p_taucov_pb_zero_diagonal_object_matrix.csv",
    "manifest": EVIDENCE / "p_taucov_pb_zero_diagonal_object_manifest.csv",
    "sha": EVIDENCE / "p_taucov_pb_zero_diagonal_object.sha256",
    "doc": DOCS / "p_taucov_pb_zero_diagonal_object_freeze.md",
}
OUT = EVIDENCE / "p_taucov_pb_zero_diagonal_object_validation.csv"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
        manifest = pd.read_csv(FILES["manifest"]).iloc[0]
        doc = FILES["doc"].read_text(encoding="utf-8")
        actual_hash = sha256(FILES["matrix"])
        add("status_expected", str(manifest["Status"]) == EXPECTED_STATUS)
        add("hash_matches_manifest", str(manifest["MatrixSHA256"]) == actual_hash)
        add("hash_matches_sha_file", FILES["sha"].read_text(encoding="utf-8").startswith(actual_hash))
        add("matrix_entries_match_manifest", len(matrix) == int(manifest["MatrixEntriesFrozen"]))
        add("diagonal_entries_zero", bool(matrix.loc[matrix["RowID"].eq(matrix["ColumnID"]), "Value"].abs().max() == 0.0))
        add("object_freeze_authorized", bool(manifest["ObjectFreezeAuthorized"]))
        add("scoring_not_authorized", not bool(manifest["ScoringAuthorized"]))
        add("survival_not_authorized", not bool(manifest["SurvivalClaimAuthorized"]))
        add("tau_validation_not_authorized", not bool(manifest["TauCoreValidationClaimAuthorized"]))
        add("doc_links_preflight", "p_taucov_pb_interaction_object_preflight.md" in doc)
        add("doc_forbids_validation", "validates the theory" in doc)

    out = pd.DataFrame(checks)
    out.to_csv(OUT, index=False)
    ok = bool(out.loc[out["Required"], "Passed"].all())
    print("P_TAUCOV_PB_ZERO_DIAGONAL_OBJECT_FREEZE_VALID" if ok else "P_TAUCOV_PB_ZERO_DIAGONAL_OBJECT_FREEZE_INVALID")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
