#!/usr/bin/env python3
"""Freeze the admissible zero-diagonal PB interaction object candidate."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_PB_ZERO_DIAGONAL_OBJECT_FREEZE_v1"
SOURCE_FREEZE_ID = "P_TAUCOV_PB_INTERACTION_OBJECT_PREFLIGHT_v1"
OBJECT_ID = "PB_ZERO_DIAGONAL_OUTER_PRODUCT"
CLAIM = "pb_zero_diagonal_object_frozen_no_scoring"

PREFLIGHT_MATRIX = EVIDENCE / "p_taucov_pb_interaction_object_preflight_matrix.csv"
PREFLIGHT_AUDIT = EVIDENCE / "p_taucov_pb_interaction_object_preflight.csv"

OUT_MATRIX = EVIDENCE / "p_taucov_pb_zero_diagonal_object_matrix.csv"
OUT_MANIFEST = EVIDENCE / "p_taucov_pb_zero_diagonal_object_manifest.csv"
OUT_SHA = EVIDENCE / "p_taucov_pb_zero_diagonal_object.sha256"
OUT_DOC = DOCS / "p_taucov_pb_zero_diagonal_object_freeze.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    if not PREFLIGHT_MATRIX.exists() or not PREFLIGHT_AUDIT.exists():
        raise RuntimeError("PB interaction object preflight must be built first.")
    audit = pd.read_csv(PREFLIGHT_AUDIT)
    row = audit[audit["ObjectCandidateID"].astype(str).eq(OBJECT_ID)]
    if len(row) != 1:
        raise RuntimeError(f"Expected exactly one {OBJECT_ID} audit row.")
    row = row.iloc[0]
    if not bool(row["PassesOverallPreflight"]):
        raise RuntimeError(f"{OBJECT_ID} did not pass overall preflight.")
    matrix = pd.read_csv(PREFLIGHT_MATRIX)
    matrix = matrix[matrix["ObjectCandidateID"].astype(str).eq(OBJECT_ID)].copy()
    matrix["FreezeID"] = FREEZE_ID
    matrix["ObjectFreezeAuthorized"] = True
    matrix["ScoringAuthorized"] = False
    matrix["ClaimBoundary"] = CLAIM
    matrix.to_csv(OUT_MATRIX, index=False)
    matrix_hash = sha256(OUT_MATRIX)
    OUT_SHA.write_text(f"{matrix_hash}  {OUT_MATRIX.name}\n", encoding="utf-8")

    manifest = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": "P_TAUCOV_PB_ZERO_DIAGONAL_OBJECT_FROZEN_NO_SCORING",
                "SourceFreezeID": SOURCE_FREEZE_ID,
                "ObjectID": OBJECT_ID,
                "RowsFrozen": int(matrix["RowID"].nunique()),
                "MatrixEntriesFrozen": len(matrix),
                "Formula": "zero_diagonal(outer_product(frozen_PB_interaction_coordinate))",
                "QCleanMatrixSupport": float(row["QCleanMatrixSupport"]),
                "MaxFamilyBlockEnergyShare": float(row["MaxFamilyBlockEnergyShare"]),
                "DiagonalEnergyShare": float(row["DiagonalEnergyShare"]),
                "MatrixSHA256": matrix_hash,
                "ObjectFreezeAuthorized": True,
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "ClaimBoundary": CLAIM,
            }
        ]
    )
    manifest.to_csv(OUT_MANIFEST, index=False)
    OUT_DOC.write_text(
        "\n".join(
            [
                "# P-TauCov PB Zero-Diagonal Object Freeze",
                "",
                f"Freeze ID: `{FREEZE_ID}`",
                "",
                "Status: `P_TAUCOV_PB_ZERO_DIAGONAL_OBJECT_FROZEN_NO_SCORING`",
                "",
                "## Purpose",
                "",
                "This packet freezes the first admissible object candidate derived from",
                "the frozen `P*B` interaction coordinate:",
                "",
                "```text",
                "PB_ZERO_DIAGONAL_OBJECT = zero_diagonal(",
                "  outer_product(frozen_PB_interaction_coordinate)",
                ")",
                "```",
                "",
                "The zero-diagonal convention is a fixed covariance-response convention",
                "that excludes pure variance inflation. It does not use the Q-clean",
                "projector as a source and does not use family masks or target outcomes.",
                "",
                "## Frozen Preflight Metrics",
                "",
                f"- Q-clean matrix support: `{float(row['QCleanMatrixSupport'])}`",
                f"- max family block energy share: `{float(row['MaxFamilyBlockEnergyShare'])}`",
                f"- diagonal energy share: `{float(row['DiagonalEnergyShare'])}`",
                f"- matrix SHA256: `{matrix_hash}`",
                "",
                "## Links",
                "",
                "- [`p_taucov_pb_interaction_object_preflight.md`](p_taucov_pb_interaction_object_preflight.md)",
                "- [`p_taucov_pb_interaction_coordinate_freeze.md`](p_taucov_pb_interaction_coordinate_freeze.md)",
                "",
                "## Claim Boundary",
                "",
                "Allowed statement:",
                "",
                "> A target-blind off-diagonal `P*B` covariance-response object has been frozen for later scoring-authorization review.",
                "",
                "Forbidden statement:",
                "",
                "> This object has survived empirical scoring, detects Tau Core, or validates the theory.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print("P_TAUCOV_PB_ZERO_DIAGONAL_OBJECT_FROZEN_NO_SCORING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
