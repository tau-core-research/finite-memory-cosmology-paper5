#!/usr/bin/env python3
"""Build the frozen P4 morphology basis packet.

The packet is target-blind. It declares which tau-coordinate directions are
allowed to define the morphology-shared subspace before any P4 candidate is
constructed.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
BRANCH_WEIGHTS = ROOT / "evidence/p_taucov_epsilon_p3_branch_support_weights.csv"
OUT_BASIS = ROOT / "evidence/p_taucov_p4_morphology_basis.csv"
OUT_SUMMARY = ROOT / "evidence/p_taucov_p4_morphology_basis_summary.csv"
DOC = ROOT / "docs/p_taucov_p4_morphology_basis_packet.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_P4_MORPHOLOGY_BASIS_PACKET_v1"
CLAIM_BOUNDARY = "target_blind_morphology_basis_no_scoring_authorization"


def unit_matrix(n: int, entries: list[tuple[int, int, float]]) -> np.ndarray:
    mat = np.zeros((n, n), dtype=float)
    for i, j, value in entries:
        mat[i, j] = value
    mat = 0.5 * (mat + mat.T)
    fro = float(np.linalg.norm(mat, ord="fro"))
    if fro == 0.0:
        raise RuntimeError("Zero morphology basis matrix.")
    return mat / fro


def main() -> int:
    df = pd.read_csv(BRANCH_WEIGHTS)
    coords = sorted(set(df["RowCoordinate"].astype(str)) | set(df["ColumnCoordinate"].astype(str)))
    idx = {coord: i for i, coord in enumerate(coords)}
    required = ["TEMPLATE_M_PARENT_MORPHOLOGY", "TEMPLATE_P_MORPH_PROJECTION"]
    missing = [coord for coord in required if coord not in idx]
    if missing:
        raise RuntimeError(f"Missing required morphology coordinates: {missing}")

    m = idx["TEMPLATE_M_PARENT_MORPHOLOGY"]
    p = idx["TEMPLATE_P_MORPH_PROJECTION"]
    basis = {
        "M_PARENT_MORPHOLOGY_DIAGONAL": unit_matrix(len(coords), [(m, m, 1.0)]),
        "P_MORPH_PROJECTION_DIAGONAL": unit_matrix(len(coords), [(p, p, 1.0)]),
        "M_P_SYMMETRIC_COUPLING": unit_matrix(len(coords), [(m, p, 1.0), (p, m, 1.0)]),
    }

    rows = []
    for basis_id, mat in basis.items():
        for i, row_coord in enumerate(coords):
            for j, col_coord in enumerate(coords):
                value = float(mat[i, j])
                if value != 0.0:
                    rows.append(
                        {
                            "ProtocolID": PROTOCOL_ID,
                            "FreezeID": FREEZE_ID,
                            "BasisID": basis_id,
                            "RowCoordinate": row_coord,
                            "ColumnCoordinate": col_coord,
                            "Value": value,
                            "UsesTargetResiduals": False,
                            "UsesScoreOutcome": False,
                            "ScoringAuthorized": False,
                            "ClaimBoundary": CLAIM_BOUNDARY,
                        }
                    )
    out = pd.DataFrame(rows)
    out.to_csv(OUT_BASIS, index=False)

    gram = np.array([[float(np.sum(a * b)) for b in basis.values()] for a in basis.values()])
    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": "P_TAUCOV_P4_MORPHOLOGY_BASIS_FROZEN_NO_SCORING",
                "Coordinates": len(coords),
                "BasisCount": len(basis),
                "BasisIDs": ";".join(basis.keys()),
                "MaxAbsOffDiagonalGram": float(np.max(np.abs(gram - np.eye(len(basis))))),
                "UsesTargetResiduals": False,
                "UsesScoreOutcome": False,
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    DOC.write_text(
        "\n".join(
            [
                "# P-TauCov P4 Morphology Basis Packet",
                "",
                "Status: `P_TAUCOV_P4_MORPHOLOGY_BASIS_FROZEN_NO_SCORING`.",
                "",
                "This packet freezes the morphology-shared basis that a later P4",
                "candidate must project away before any Tau-specific covariance",
                "claim can be tested.",
                "",
                "## Frozen Basis",
                "",
                "- `M_PARENT_MORPHOLOGY_DIAGONAL`",
                "- `P_MORPH_PROJECTION_DIAGONAL`",
                "- `M_P_SYMMETRIC_COUPLING`",
                "",
                "The basis is constructed only from declared tau-coordinate names and",
                "does not use target residuals, fold outcomes, alpha behavior, or P3",
                "score margins.",
                "",
                "## Claim Boundary",
                "",
                "Allowed statement:",
                "",
                "```text",
                "A target-blind morphology-shared subspace has been frozen for later",
                "P4 morphology-orthogonalization.",
                "```",
                "",
                "Forbidden statement:",
                "",
                "```text",
                "The P4 candidate has been built, scored, or shown to be Tau-specific.",
                "```",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print("P_TAUCOV_P4_MORPHOLOGY_BASIS_FROZEN_NO_SCORING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
