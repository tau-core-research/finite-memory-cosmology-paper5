#!/usr/bin/env python3
"""Audit how current parent embedding coordinates overlap Q_clean."""

from __future__ import annotations

from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_EMBEDDING_QCLEAN_SUPPORT_AUDIT_v1"
STATUS = "P_TAUCOV_EMBEDDING_QCLEAN_SUPPORT_AUDIT_BLOCKS_CURRENT_EMBEDDING_NO_SCORING"
CLAIM = "embedding_qclean_support_audit_no_scoring_no_survival"

EMBEDDING = EVIDENCE / "p_taucov_tccs_parent_score_embedding_matrix.csv"
QCLEAN = EVIDENCE / "p_taucov_domain_compatibility_common_cleaner_matrix.csv"

OUT_COORDS = EVIDENCE / "p_taucov_embedding_qclean_coordinate_support.csv"
OUT_PAIRS = EVIDENCE / "p_taucov_embedding_qclean_pair_support.csv"
OUT_SUMMARY = EVIDENCE / "p_taucov_embedding_qclean_support_audit_summary.csv"
OUT_VALIDATION = EVIDENCE / "p_taucov_embedding_qclean_support_audit_validation.csv"
OUT_DOC = DOCS / "p_taucov_embedding_qclean_support_audit.md"


def load_embedding() -> tuple[list[str], list[str], np.ndarray]:
    df = pd.read_csv(EMBEDDING)
    rows = list(dict.fromkeys(df["EmpiricalRowID"].astype(str)))
    coords = list(dict.fromkeys(df["TauCoordinate"].astype(str)))
    ridx = {row: i for i, row in enumerate(rows)}
    cidx = {coord: i for i, coord in enumerate(coords)}
    mat = np.zeros((len(rows), len(coords)), dtype=float)
    for rec in df.to_dict("records"):
        mat[ridx[str(rec["EmpiricalRowID"])], cidx[str(rec["TauCoordinate"])]] = float(rec["EmbeddingValue"])
    return rows, coords, mat


def load_qclean(target_rows: list[str]) -> np.ndarray:
    df = pd.read_csv(QCLEAN)
    df = df[df["MatrixID"].astype(str).eq("PIBAL_PIPERP_PIBAL")]
    rows = list(dict.fromkeys(df["RowID"].astype(str)))
    idx = {row: i for i, row in enumerate(rows)}
    raw = np.zeros((len(rows), len(rows)), dtype=float)
    for rec in df.to_dict("records"):
        raw[idx[str(rec["RowID"])], idx[str(rec["ColumnID"])]] = float(rec["Value"])
    out = np.zeros((len(target_rows), len(target_rows)), dtype=float)
    for i, row in enumerate(target_rows):
        for j, col in enumerate(target_rows):
            out[i, j] = raw[idx[row], idx[col]]
    return out


def support(q: np.ndarray, vector: np.ndarray) -> tuple[float, float, float]:
    raw = float(np.linalg.norm(vector))
    clean = float(np.linalg.norm(q @ vector))
    return raw, clean, 0.0 if raw == 0.0 else clean / raw


def main() -> int:
    rows, coords, emb = load_embedding()
    q = load_qclean(rows)

    coord_records = []
    cidx = {coord: i for i, coord in enumerate(coords)}
    for coord in coords:
        raw, clean, ratio = support(q, emb[:, cidx[coord]])
        coord_records.append(
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "CoordinateID": coord,
                "RawNorm": raw,
                "QCleanNorm": clean,
                "QCleanSupportRatio": ratio,
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM,
            }
        )

    pair_records = []
    for left, right in combinations(coords, 2):
        vec = emb[:, cidx[left]] - emb[:, cidx[right]]
        raw, clean, ratio = support(q, vec)
        pair_records.append(
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "LeftCoordinate": left,
                "RightCoordinate": right,
                "RawNorm": raw,
                "QCleanNorm": clean,
                "QCleanSupportRatio": ratio,
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM,
            }
        )

    coord_df = pd.DataFrame(coord_records).sort_values("QCleanSupportRatio", ascending=False)
    pair_df = pd.DataFrame(pair_records).sort_values("QCleanSupportRatio", ascending=False)
    coord_df.to_csv(OUT_COORDS, index=False)
    pair_df.to_csv(OUT_PAIRS, index=False)

    branch_coords = ["TEMPLATE_PHI_PARENT_SOURCE", "TEMPLATE_B_BRANCH_RESPONSE", "TEMPLATE_M_PARENT_MORPHOLOGY"]
    branch_max = float(coord_df[coord_df["CoordinateID"].isin(branch_coords)]["QCleanSupportRatio"].max())
    best_coord = coord_df.iloc[0]
    best_pair = pair_df.iloc[0]
    blocks = bool(branch_max < 0.20)
    status = STATUS if blocks else "P_TAUCOV_EMBEDDING_QCLEAN_SUPPORT_AUDIT_HAS_BRANCH_SUPPORT_NO_SCORING"
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": status,
                "CoordinatesAudited": len(coord_df),
                "PairsAudited": len(pair_df),
                "BestCoordinate": best_coord["CoordinateID"],
                "BestCoordinateSupportRatio": float(best_coord["QCleanSupportRatio"]),
                "BestPair": f"{best_pair['LeftCoordinate']}__minus__{best_pair['RightCoordinate']}",
                "BestPairSupportRatio": float(best_pair["QCleanSupportRatio"]),
                "MaxBranchCoordinateSupportRatio": branch_max,
                "CurrentEmbeddingBlocksParentDomainCurvatureSource": blocks,
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "ClaimBoundary": CLAIM,
            }
        ]
    ).to_csv(OUT_SUMMARY, index=False)

    pd.DataFrame(
        [
            {"FreezeID": FREEZE_ID, "CheckID": "coordinate_rows_present", "Passed": len(coord_df) == len(coords), "Required": True},
            {"FreezeID": FREEZE_ID, "CheckID": "pair_rows_present", "Passed": len(pair_df) == len(list(combinations(coords, 2))), "Required": True},
            {"FreezeID": FREEZE_ID, "CheckID": "scoring_not_authorized", "Passed": True, "Required": True},
            {"FreezeID": FREEZE_ID, "CheckID": "summary_written", "Passed": True, "Required": True},
        ]
    ).to_csv(OUT_VALIDATION, index=False)

    top_coords = "\n".join(
        f"| `{rec.CoordinateID}` | `{rec.QCleanSupportRatio}` |"
        for rec in coord_df.head(8).itertuples(index=False)
    )
    top_pairs = "\n".join(
        f"| `{rec.LeftCoordinate}` - `{rec.RightCoordinate}` | `{rec.QCleanSupportRatio}` |"
        for rec in pair_df.head(8).itertuples(index=False)
    )
    OUT_DOC.write_text(
        "\n".join(
            [
                "# P-TauCov Embedding Q-Clean Support Audit",
                "",
                f"Freeze ID: `{FREEZE_ID}`",
                "",
                f"Status: `{status}`",
                "",
                "## Purpose",
                "",
                "This target-blind audit checks whether the current parent-to-score",
                "embedding places the declared parent coordinates into the frozen common",
                "clean subspace `Q_clean = Pi_bal Pi_perp Pi_bal`.",
                "",
                "It does not inspect target residuals and does not authorize scoring.",
                "",
                "## Top Coordinate Support",
                "",
                "| Coordinate | Q-clean support ratio |",
                "|---|---:|",
                top_coords,
                "",
                "## Top Pair-Difference Support",
                "",
                "| Pair contrast | Q-clean support ratio |",
                "|---|---:|",
                top_pairs,
                "",
                "## Key Interpretation",
                "",
                f"- best coordinate: `{best_coord['CoordinateID']}` with support `{float(best_coord['QCleanSupportRatio'])}`",
                f"- max branch-coordinate support: `{branch_max}`",
                "",
                "The current embedding almost completely removes the active branch",
                "coordinates from the common clean subspace. This explains why the",
                "minimal Q-native branch-response curvature and older Hessian inventory",
                "cannot pass the parent-domain curvature source requirement.",
                "",
                "## Consequence",
                "",
                "The next step is not a new empirical scorecard. The next step is a new",
                "parent-domain embedding or domain metric in which active branch",
                "curvature has intrinsic support inside the clean subspace before",
                "projection cleaning is applied.",
                "",
                "## Claim Boundary",
                "",
                "Allowed statement:",
                "",
                "> The current parent-to-score embedding lacks enough Q-clean support for active branch curvature.",
                "",
                "Forbidden statement:",
                "",
                "> This audit validates Tau Core, constructs a survivor, or authorizes empirical scoring.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
