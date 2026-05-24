#!/usr/bin/env python3
"""Freeze the target-blind P*B source-coordinate candidate."""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_PB_INTERACTION_COORDINATE_FREEZE_v1"
SOURCE_FREEZE_ID = "P_TAUCOV_ADMISSIBLE_SOURCE_COORDINATE_EXTENSION_v1"
CLAIM = "pb_interaction_coordinate_frozen_no_object_no_scoring"

EMBEDDING = EVIDENCE / "p_taucov_tccs_parent_score_embedding_matrix.csv"
SOURCE_AUDIT = EVIDENCE / "p_taucov_admissible_source_coordinate_extension_audit.csv"
SOURCE_SUMMARY = EVIDENCE / "p_taucov_admissible_source_coordinate_extension_summary.csv"

OUT_COORD = EVIDENCE / "p_taucov_pb_interaction_coordinate.csv"
OUT_MANIFEST = EVIDENCE / "p_taucov_pb_interaction_coordinate_manifest.csv"
OUT_SHA = EVIDENCE / "p_taucov_pb_interaction_coordinate.sha256"
OUT_DOC = DOCS / "p_taucov_pb_interaction_coordinate_freeze.md"

COORD_ID = "COORD_PB_INTERACTION"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_embedding() -> tuple[list[str], list[str], pd.DataFrame, np.ndarray]:
    df = pd.read_csv(EMBEDDING)
    rows = list(dict.fromkeys(df["EmpiricalRowID"].astype(str)))
    coords = list(dict.fromkeys(df["TauCoordinate"].astype(str)))
    ridx = {row: i for i, row in enumerate(rows)}
    cidx = {coord: i for i, coord in enumerate(coords)}
    mat = np.zeros((len(rows), len(coords)), dtype=float)
    for rec in df.to_dict("records"):
        mat[ridx[str(rec["EmpiricalRowID"])], cidx[str(rec["TauCoordinate"])]] = float(rec["EmbeddingValue"])
    meta = df.drop_duplicates("EmpiricalRowID").set_index("EmpiricalRowID").loc[rows].reset_index()
    return rows, coords, meta, mat


def normalize(vector: np.ndarray) -> np.ndarray:
    centered = vector - float(np.mean(vector))
    norm = float(np.linalg.norm(centered))
    if norm == 0.0:
        raise RuntimeError("Cannot freeze zero-norm PB interaction coordinate.")
    return centered / norm


def main() -> int:
    if not SOURCE_AUDIT.exists() or not SOURCE_SUMMARY.exists():
        raise RuntimeError("Admissible source-coordinate extension must be built first.")
    audit = pd.read_csv(SOURCE_AUDIT)
    source = audit[audit["CoordinateCandidateID"].astype(str).eq(COORD_ID)]
    if len(source) != 1:
        raise RuntimeError(f"Expected exactly one {COORD_ID} source-audit row.")
    source_row = source.iloc[0]
    if not bool(source_row["PassesQCleanSupportGate"]):
        raise RuntimeError(f"{COORD_ID} did not pass Q-clean support gate.")
    if not bool(source_row["PassesFamilyBalanceGate"]):
        raise RuntimeError(f"{COORD_ID} did not pass family-balance gate.")
    if not bool(source_row["PassesDiagonalControlGate"]):
        raise RuntimeError(f"{COORD_ID} did not pass diagonal-control gate.")

    rows, coords, meta, emb = load_embedding()
    cidx = {coord: i for i, coord in enumerate(coords)}
    p = emb[:, cidx["TEMPLATE_P_MORPH_PROJECTION"]]
    b = emb[:, cidx["TEMPLATE_B_BRANCH_RESPONSE"]]
    raw = p * b
    frozen = normalize(raw)

    out = pd.DataFrame(
        {
            "ProtocolID": PROTOCOL_ID,
            "FreezeID": FREEZE_ID,
            "EmpiricalRowID": rows,
            "EmpiricalIndex": meta["EmpiricalIndex"].astype(int).to_numpy(),
            "FamilyID": meta["FamilyID"].astype(str).to_numpy(),
            "ClockIndex": meta["ClockIndex"].astype(int).to_numpy(),
            "CoordinateID": COORD_ID,
            "RawPBValue": raw,
            "FrozenCoordinateValue": frozen,
            "ParentProvenance": "P*B interaction from frozen parent embedding columns TEMPLATE_P_MORPH_PROJECTION and TEMPLATE_B_BRANCH_RESPONSE",
            "UsesTargetResiduals": False,
            "UsesScoreOutcomes": False,
            "CoordinateFreezeAuthorized": True,
            "ObjectConstructionAuthorized": False,
            "ScoringAuthorized": False,
            "SurvivalClaimAuthorized": False,
            "TauCoreValidationClaimAuthorized": False,
            "ClaimBoundary": CLAIM,
        }
    )
    out.to_csv(OUT_COORD, index=False)
    coord_hash = sha256(OUT_COORD)
    OUT_SHA.write_text(f"{coord_hash}  {OUT_COORD.name}\n", encoding="utf-8")

    manifest = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": "P_TAUCOV_PB_INTERACTION_COORDINATE_FROZEN_NO_OBJECT_NO_SCORING",
                "SourceFreezeID": SOURCE_FREEZE_ID,
                "CoordinateID": COORD_ID,
                "RowsFrozen": len(out),
                "Formula": "center_normalize(TEMPLATE_P_MORPH_PROJECTION * TEMPLATE_B_BRANCH_RESPONSE)",
                "SourceQCleanSupport": float(source_row["QCleanSupport"]),
                "SourceMaxFamilyEnergyShare": float(source_row["MaxFamilyEnergyShare"]),
                "SourceDiagonalEnergyShareIfOuterProduct": float(source_row["DiagonalEnergyShareIfOuterProduct"]),
                "CoordinateSHA256": coord_hash,
                "CoordinateFreezeAuthorized": True,
                "ObjectConstructionAuthorized": False,
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
                "# P-TauCov PB Interaction Coordinate Freeze",
                "",
                f"Freeze ID: `{FREEZE_ID}`",
                "",
                "Status: `P_TAUCOV_PB_INTERACTION_COORDINATE_FROZEN_NO_OBJECT_NO_SCORING`",
                "",
                "## Purpose",
                "",
                "This packet freezes the first passing admissible source-coordinate candidate:",
                "`COORD_PB_INTERACTION`.",
                "",
                "The coordinate is derived target-blind from the already frozen parent-to-score",
                "embedding as:",
                "",
                "```text",
                "COORD_PB_INTERACTION = center_normalize(",
                "  TEMPLATE_P_MORPH_PROJECTION * TEMPLATE_B_BRANCH_RESPONSE",
                ")",
                "```",
                "",
                "The term is interpreted only as a parent-side projection-branch interaction",
                "coordinate. It is not a covariance object, not a Tau signal, and not a",
                "scorecard result.",
                "",
                "## Frozen Source Metrics",
                "",
                f"- Q-clean support: `{float(source_row['QCleanSupport'])}`",
                f"- max family energy share: `{float(source_row['MaxFamilyEnergyShare'])}`",
                f"- diagonal share if used as an outer product: `{float(source_row['DiagonalEnergyShareIfOuterProduct'])}`",
                f"- coordinate SHA256: `{coord_hash}`",
                "",
                "## Links",
                "",
                "- [`p_taucov_admissible_source_coordinate_extension.md`](p_taucov_admissible_source_coordinate_extension.md)",
                "- [`p_taucov_parent_domain_curvature_source_requirement.md`](p_taucov_parent_domain_curvature_source_requirement.md)",
                "",
                "## Claim Boundary",
                "",
                "Allowed statement:",
                "",
                "> A target-blind parent-derived `P*B` interaction coordinate has been frozen for later object-construction preflight.",
                "",
                "Forbidden statement:",
                "",
                "> This coordinate is a detected Tau signal, a covariance survivor, or an authorized empirical scorecard.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print("P_TAUCOV_PB_INTERACTION_COORDINATE_FROZEN_NO_OBJECT_NO_SCORING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
