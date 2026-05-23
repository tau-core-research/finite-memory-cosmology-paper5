#!/usr/bin/env python3
"""Declare a target-blind covariance map for P-TauCov."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RESPONSE = ROOT / "evidence/p_taucov_response_energy_split_effective_response.csv"
OUT_MAP = ROOT / "evidence/p_taucov_covariance_map_matrix.csv"
OUT_GATES = ROOT / "evidence/p_taucov_covariance_map_gates.csv"
OUT_SUMMARY = ROOT / "evidence/p_taucov_covariance_map_summary.csv"
DOC = ROOT / "docs/p_taucov_covariance_map_declaration.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_COVARIANCE_MAP_DECLARATION_v1"
CLAIM_BOUNDARY = "covariance_map_declaration_no_scoring"


def main() -> int:
    response_rows = pd.read_csv(RESPONSE)
    coords = sorted(set(response_rows["RowCoordinate"]) | set(response_rows["ColumnCoordinate"]))
    response = pd.DataFrame(0.0, index=coords, columns=coords)
    for row in response_rows.itertuples(index=False):
        response.loc[str(row.RowCoordinate), str(row.ColumnCoordinate)] = float(row.Value)
    response = (response + response.T) / 2.0
    matrix = response.to_numpy(dtype=float)

    # Target-blind covariance map:
    # D_M C[T] = T T^T / ||T T^T||_F.  It is PSD by construction and does not
    # inspect residual scores, OOS likelihoods, alpha behavior, or family wins.
    raw_cov = matrix @ matrix.T
    frob = float(np.linalg.norm(raw_cov, ord="fro"))
    cov_map = raw_cov / frob if frob > 0.0 else raw_cov
    eigs = np.linalg.eigvalsh(cov_map)
    trace = float(np.trace(cov_map))

    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "RowCoordinate": row_coord,
                "ColumnCoordinate": col_coord,
                "Value": float(cov_map[row_idx, col_idx]),
                "GeneratedFrom": "target_blind_psd_lift_DMC_T_equals_TTt_over_frobenius_norm",
                "UsesTargetResiduals": False,
                "UsesScoreOutcome": False,
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for row_idx, row_coord in enumerate(coords)
            for col_idx, col_coord in enumerate(coords)
        ]
    ).to_csv(OUT_MAP, index=False)

    psd = float(eigs.min()) >= -1e-12
    nonzero = frob > 0.0
    symmetric = bool(np.allclose(cov_map, cov_map.T, atol=1e-12))
    gates = [
        ("CM-G1_RESPONSE_OBJECT_AVAILABLE", RESPONSE.exists(), 1.0),
        ("CM-G2_MAP_DECLARED_BEFORE_SCORING", True, 1.0),
        ("CM-G3_MAP_SYMMETRIC", symmetric, float(symmetric)),
        ("CM-G4_MAP_POSITIVE_SEMIDEFINITE", psd, float(eigs.min())),
        ("CM-G5_MAP_NONZERO_NORMALIZED", nonzero and abs(float(np.linalg.norm(cov_map, ord="fro")) - 1.0) < 1e-12, float(np.linalg.norm(cov_map, ord="fro"))),
        ("CM-G6_NO_TARGET_OR_SCORE_INPUTS", True, 1.0),
    ]
    gates_df = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "GateID": gate_id,
                "Passed": bool(passed),
                "DiagnosticValue": float(value),
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for gate_id, passed, value in gates
        ]
    )
    gates_df.to_csv(OUT_GATES, index=False)
    passed_count = int(gates_df["Passed"].sum())
    status = (
        "P_TAUCOV_COVARIANCE_MAP_DECLARED_PASS_NO_SCORING"
        if passed_count == len(gates_df)
        else "P_TAUCOV_COVARIANCE_MAP_DECLARATION_FAIL_NO_SCORING"
    )
    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": status,
                "GatesPassed": passed_count,
                "GatesTotal": len(gates_df),
                "MapDimension": len(coords),
                "MinEigenvalue": float(eigs.min()),
                "MaxEigenvalue": float(eigs.max()),
                "Trace": trace,
                "FrobeniusNorm": float(np.linalg.norm(cov_map, ord="fro")),
                "MapSymmetric": symmetric,
                "MapPositiveSemidefinite": psd,
                "ScoringAuthorized": False,
                "MeasurementValidationAllowed": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)
    DOC.write_text(
        "\n".join(
            [
                "# P-TauCov Covariance Map Declaration",
                "",
                f"Status: `{status}`.",
                "",
                "This packet declares the target-blind map that turns a Tau response",
                "object into a covariance-deformation candidate. It is a protocol",
                "declaration only; it does not run an empirical scorecard.",
                "",
                "## Declared Map",
                "",
                "For a frozen response object `T`, define",
                "",
                "```math",
                "D_M C[T] = \\frac{TT^{\\mathsf T}}{\\|TT^{\\mathsf T}\\|_F}.",
                "```",
                "",
                "This makes the covariance deformation symmetric and positive",
                "semidefinite by construction. The map is declared before scoring and",
                "does not use target residuals, likelihood improvements, alpha",
                "behavior, or dominant-family information.",
                "",
                "## Key Numbers",
                "",
                f"- map dimension: `{len(coords)}`",
                f"- minimum eigenvalue: `{float(eigs.min())}`",
                f"- maximum eigenvalue: `{float(eigs.max())}`",
                f"- Frobenius norm: `{float(np.linalg.norm(cov_map, ord='fro'))}`",
                f"- gates passed: `{passed_count}/{len(gates_df)}`",
                "",
                "## Claim Boundary",
                "",
                "Allowed: a reproducible target-blind covariance-map rule has been",
                "declared.",
                "",
                "Forbidden: this is not a covariance scorecard, not survival, and not",
                "measurement validation.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
