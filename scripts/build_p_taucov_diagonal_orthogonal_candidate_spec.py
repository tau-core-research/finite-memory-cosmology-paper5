#!/usr/bin/env python3
"""Build a diagonal-orthogonal signed-response candidate spec for P-TauCov."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SIGNED_MAP = ROOT / "evidence/p_taucov_branch_localized_map.csv"
ADMISSIBILITY = ROOT / "evidence/p_taucov_next_candidate_admissibility_gate_summary.csv"
OUT = ROOT / "evidence/p_taucov_diagonal_orthogonal_candidate_matrix.csv"
SUMMARY = ROOT / "evidence/p_taucov_diagonal_orthogonal_candidate_summary.csv"
DOC = ROOT / "docs/p_taucov_diagonal_orthogonal_candidate_spec.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
CANDIDATE_ID = "P_TAUCOV_DIAGONAL_ORTHOGONAL_SIGNED_RESPONSE_CANDIDATE_v1"
CLAIM_BOUNDARY = "diagonal_orthogonal_candidate_spec_no_scoring"


def main() -> int:
    admissibility = pd.read_csv(ADMISSIBILITY).iloc[0]
    if str(admissibility["Status"]) != "P_TAUCOV_NEXT_CANDIDATE_ADMISSIBILITY_GATE_PASS_NO_SCORING":
        raise RuntimeError("Next-candidate admissibility gate has not passed.")
    src = pd.read_csv(SIGNED_MAP)
    coords = sorted(set(src["RowCoordinate"].astype(str)) | set(src["ColumnCoordinate"].astype(str)))
    mat = pd.DataFrame(0.0, index=coords, columns=coords)
    for row in src.itertuples(index=False):
        mat.loc[str(row.RowCoordinate), str(row.ColumnCoordinate)] = float(row.Value)
    mat = (mat + mat.T) / 2.0
    raw_diag_norm = float(np.linalg.norm(np.diag(mat.to_numpy(float))))
    for coord in coords:
        mat.loc[coord, coord] = 0.0
    arr = mat.to_numpy(float)
    fro = float(np.linalg.norm(arr, ord="fro"))
    if fro > 0:
        arr = arr / fro
    diag_norm = float(np.linalg.norm(np.diag(arr)))
    eigs = np.linalg.eigvalsh(arr)
    rows = []
    for i, row_coord in enumerate(coords):
        for j, col_coord in enumerate(coords):
            rows.append(
                {
                    "ProtocolID": PROTOCOL_ID,
                    "CandidateID": CANDIDATE_ID,
                    "RowCoordinate": row_coord,
                    "ColumnCoordinate": col_coord,
                    "Value": float(arr[i, j]),
                    "Construction": "zero_diagonal_then_frobenius_normalize",
                    "UsesTargetResiduals": False,
                    "UsesScoreOutcome": False,
                    "ScoringAuthorized": False,
                    "ClaimBoundary": CLAIM_BOUNDARY,
                }
            )
    pd.DataFrame(rows).to_csv(OUT, index=False)
    status = "P_TAUCOV_DIAGONAL_ORTHOGONAL_CANDIDATE_SPEC_PASS_NO_SCORING"
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "CandidateID": CANDIDATE_ID,
                "Status": status,
                "Dimension": len(coords),
                "RawDiagonalNorm": raw_diag_norm,
                "FinalDiagonalNorm": diag_norm,
                "FrobeniusNorm": float(np.linalg.norm(arr, ord="fro")),
                "MinEigenvalue": float(eigs.min()),
                "MaxEigenvalue": float(eigs.max()),
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    ).to_csv(SUMMARY, index=False)
    DOC.write_text(
        "\n".join(
            [
                "# P-TauCov Diagonal-Orthogonal Candidate Spec",
                "",
                f"Status: `{status}`.",
                "",
                "This candidate removes the diagonal component from the failed",
                "branch-localized signed map before any new scoring. It directly",
                "addresses the diagonal-control failure mode observed in the signed",
                "scorecard.",
                "",
                "Construction:",
                "",
                "```text",
                "K_signed -> K_signed with diagonal set to zero -> Frobenius normalize",
                "```",
                "",
                f"- raw diagonal norm: `{raw_diag_norm}`",
                f"- final diagonal norm: `{diag_norm}`",
                f"- minimum eigenvalue: `{float(eigs.min())}`",
                f"- maximum eigenvalue: `{float(eigs.max())}`",
                "",
                "This is a candidate specification only. It does not authorize scoring.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
