#!/usr/bin/env python3
"""Freeze branch-localized covariance map for P-TauCov."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SUPPORT = ROOT / "evidence/p_taucov_branch_localized_support_rule.csv"
OUT = ROOT / "evidence/p_taucov_branch_localized_map.csv"
SUMMARY = ROOT / "evidence/p_taucov_branch_localized_map_summary.csv"
DOC = ROOT / "docs/p_taucov_branch_localized_map.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_BRANCH_LOCALIZED_MAP_FREEZE_v1"
CLAIM_BOUNDARY = "branch_localized_map_freeze_no_scoring"


def main() -> int:
    support = pd.read_csv(SUPPORT)
    coords = sorted(set(support["RowCoordinate"].astype(str)) | set(support["ColumnCoordinate"].astype(str)))
    raw = pd.DataFrame(0.0, index=coords, columns=coords)
    localized = pd.DataFrame(0.0, index=coords, columns=coords)
    for row in support.itertuples(index=False):
        raw.loc[str(row.RowCoordinate), str(row.ColumnCoordinate)] = float(row.Value)
        if bool(row.BranchSupport):
            localized.loc[str(row.RowCoordinate), str(row.ColumnCoordinate)] = float(row.Value)
    # Enforce symmetric covariance support after target-blind localization.
    localized = (localized + localized.T) / 2.0
    raw = (raw + raw.T) / 2.0
    mat = localized.to_numpy(dtype=float)
    fro = float(np.linalg.norm(mat, ord="fro"))
    if fro > 0.0:
        mat = mat / fro
    eigs = np.linalg.eigvalsh(mat)
    rows = []
    for i, row_coord in enumerate(coords):
        for j, col_coord in enumerate(coords):
            rows.append(
                {
                    "ProtocolID": PROTOCOL_ID,
                    "FreezeID": FREEZE_ID,
                    "RowCoordinate": row_coord,
                    "ColumnCoordinate": col_coord,
                    "Value": float(mat[i, j]),
                    "RawLocalizedValue": float(localized.iloc[i, j]),
                    "LocalizationRule": "symmetrized_support_mask_then_frobenius_normalize",
                    "UsesTargetResiduals": False,
                    "UsesScoreOutcome": False,
                    "ScoringAuthorized": False,
                    "ClaimBoundary": CLAIM_BOUNDARY,
                }
            )
    pd.DataFrame(rows).to_csv(OUT, index=False)
    status = (
        "P_TAUCOV_BRANCH_LOCALIZED_MAP_FROZEN_PSD_NO_SCORING"
        if float(eigs.min()) >= -1e-12
        else "P_TAUCOV_BRANCH_LOCALIZED_MAP_FROZEN_SIGNED_NO_SCORING"
    )
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": status,
                "MapDimension": len(coords),
                "FrobeniusNorm": float(np.linalg.norm(mat, ord="fro")),
                "MinEigenvalue": float(eigs.min()),
                "MaxEigenvalue": float(eigs.max()),
                "PositiveSemidefinite": float(eigs.min()) >= -1e-12,
                "ScoringAuthorized": False,
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    ).to_csv(SUMMARY, index=False)
    DOC.write_text(
        "\n".join(
            [
                "# P-TauCov Branch-Localized Map",
                "",
                f"Status: `{status}`.",
                "",
                "The localized map applies the frozen support mask to the parent-action",
                "covariance map, symmetrizes the retained support, and Frobenius",
                "normalizes the result. It does not inspect target residuals or score",
                "outcomes.",
                "",
                f"- map dimension: `{len(coords)}`",
                f"- minimum eigenvalue: `{float(eigs.min())}`",
                f"- maximum eigenvalue: `{float(eigs.max())}`",
                f"- Frobenius norm: `{float(np.linalg.norm(mat, ord='fro'))}`",
                "",
                "If the localized map is not PSD, it must use a signed-response",
                "protocol rather than a covariance-deformation survival claim.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
