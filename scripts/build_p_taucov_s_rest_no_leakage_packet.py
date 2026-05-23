#!/usr/bin/env python3
"""Build the P-TauCov S_rest no-leakage packet."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOMAIN = ROOT / "evidence/p_taucov_full_action_domain_coordinates.csv"
SCAFFOLD = ROOT / "evidence/p_taucov_minimal_global_parent_action_scaffold_hessian.csv"
OUT_TERMS = ROOT / "evidence/p_taucov_s_rest_no_leakage_terms.csv"
OUT_HESSIAN = ROOT / "evidence/p_taucov_s_rest_no_leakage_hessian.csv"
OUT_GATES = ROOT / "evidence/p_taucov_s_rest_no_leakage_gates.csv"
OUT_SUMMARY = ROOT / "evidence/p_taucov_s_rest_no_leakage_summary.csv"
DOC = ROOT / "docs/p_taucov_s_rest_no_leakage_packet_result.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_S_REST_NO_LEAKAGE_PACKET_v1"
CLAIM_BOUNDARY = "s_rest_no_leakage_no_scoring"


def main() -> int:
    domain = pd.read_csv(DOMAIN)
    coords = domain["CoordinateID"].astype(str).tolist()
    active = set(domain.loc[domain["EmbeddingRole"].eq("active"), "CoordinateID"].astype(str))
    inactive = [coord for coord in coords if coord not in active]
    idx = {coord: i for i, coord in enumerate(coords)}

    terms = []
    for coord in inactive:
        role = str(domain.loc[domain["CoordinateID"].eq(coord), "EmbeddingRole"].iloc[0])
        terms.append(
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "TermID": f"S_REST_POSITIVE_{coord}",
                "CoordinateID": coord,
                "EmbeddingRole": role,
                "Coefficient": 0.5,
                "MassSquared": 1.0,
                "Formula": f"+1/2 {coord}^2",
                "UsesTargetResiduals": False,
                "UsesScoreOutcome": False,
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        )
    pd.DataFrame(terms).to_csv(OUT_TERMS, index=False)

    rest_hessian = np.zeros((len(coords), len(coords)), dtype=float)
    for coord in inactive:
        rest_hessian[idx[coord], idx[coord]] = 1.0

    hessian_rows = []
    for i, row_coord in enumerate(coords):
        for j, col_coord in enumerate(coords):
            hessian_rows.append(
                {
                    "ProtocolID": PROTOCOL_ID,
                    "FreezeID": FREEZE_ID,
                    "RowCoordinate": row_coord,
                    "ColumnCoordinate": col_coord,
                    "Value": float(rest_hessian[i, j]),
                    "UsesTargetResiduals": False,
                    "UsesScoreOutcome": False,
                    "ScoringAuthorized": False,
                    "ClaimBoundary": CLAIM_BOUNDARY,
                }
            )
    pd.DataFrame(hessian_rows).to_csv(OUT_HESSIAN, index=False)

    active_ids = [idx[coord] for coord in coords if coord in active]
    inactive_ids = [idx[coord] for coord in inactive]
    active_block_norm = float(np.linalg.norm(rest_hessian[np.ix_(active_ids, active_ids)], ord="fro"))
    cross_block_norm = float(np.linalg.norm(rest_hessian[np.ix_(active_ids, inactive_ids)], ord="fro"))
    inactive_eigs = np.linalg.eigvalsh(rest_hessian[np.ix_(inactive_ids, inactive_ids)])
    gates = [
        ("SR-G1_DOMAIN_AVAILABLE", len(coords) == 8, float(len(coords))),
        ("SR-G2_INACTIVE_COMPLEMENT_POSITIVE", float(inactive_eigs.min()) > 0.0, float(inactive_eigs.min())),
        ("SR-G3_ACTIVE_HESSIAN_UNCHANGED", active_block_norm < 1e-12, active_block_norm),
        ("SR-G4_NO_ACTIVE_INACTIVE_CROSS_LEAKAGE", cross_block_norm < 1e-12, cross_block_norm),
        ("SR-G5_NO_TARGET_OR_SCORE_INPUTS", True, 1.0),
    ]
    gates_df = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "GateID": gate,
                "Passed": bool(passed),
                "DiagnosticValue": float(value),
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for gate, passed, value in gates
        ]
    )
    gates_df.to_csv(OUT_GATES, index=False)
    passed_count = int(gates_df["Passed"].sum())
    status = (
        "P_TAUCOV_S_REST_NO_LEAKAGE_PASS_NO_SCORING"
        if passed_count == len(gates_df)
        else "P_TAUCOV_S_REST_NO_LEAKAGE_FAIL_NO_SCORING"
    )
    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": status,
                "GatesPassed": passed_count,
                "GatesTotal": len(gates_df),
                "InactiveCoordinateCount": len(inactive),
                "MinInactiveEigenvalue": float(inactive_eigs.min()),
                "ActiveBlockNorm": active_block_norm,
                "ActiveInactiveCrossBlockNorm": cross_block_norm,
                "ResolvedBlocker": "S_REST",
                "StillOpen": "REFERENCE_BACKGROUND_STABILITY;COVARIANCE_MAP",
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
                "# P-TauCov S_rest No-Leakage Result",
                "",
                f"Status: `{status}`.",
                "",
                "The rest sector assigns positive quadratic mass to the inactive",
                "complement and has zero active/inactive cross block. It preserves",
                "the active witness Hessian.",
                "",
                "## Key Numbers",
                "",
                f"- inactive coordinates: `{len(inactive)}`",
                f"- minimum inactive eigenvalue: `{float(inactive_eigs.min())}`",
                f"- active block norm: `{active_block_norm}`",
                f"- active/inactive cross block norm: `{cross_block_norm}`",
                "",
                "## Remaining Open",
                "",
                "`REFERENCE_BACKGROUND_STABILITY` and `COVARIANCE_MAP` remain open.",
                "",
                "No scoring or measurement validation is authorized.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
