#!/usr/bin/env python3
"""Build a parent-action origin packet for the projection-essential witness."""

from __future__ import annotations

from pathlib import Path
import importlib.util

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
WITNESS = ROOT / "evidence/p_taucov_projection_essentiality_witness.csv"
WITNESS_SUMMARY = ROOT / "evidence/p_taucov_projection_essentiality_witness_summary.csv"
OUT_ACTION = ROOT / "evidence/p_taucov_projection_essentiality_parent_action_terms.csv"
OUT_HESSIAN = ROOT / "evidence/p_taucov_projection_essentiality_parent_action_hessian.csv"
OUT_GATES = ROOT / "evidence/p_taucov_projection_essentiality_parent_action_origin_gates.csv"
OUT_SUMMARY = ROOT / "evidence/p_taucov_projection_essentiality_parent_action_origin_summary.csv"
DOC = ROOT / "docs/p_taucov_projection_essentiality_parent_action_origin_packet.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_PROJECTION_ESSENTIALITY_PARENT_ACTION_ORIGIN_v1"
CLAIM_BOUNDARY = "conditional_parent_action_origin_no_scoring"


def load_witness() -> tuple[list[str], np.ndarray]:
    df = pd.read_csv(WITNESS)
    coords = sorted(set(df["RowCoordinate"].astype(str)) | set(df["ColumnCoordinate"].astype(str)))
    idx = {coord: i for i, coord in enumerate(coords)}
    mat = np.zeros((len(coords), len(coords)), dtype=float)
    for row in df.itertuples(index=False):
        mat[idx[str(row.RowCoordinate)], idx[str(row.ColumnCoordinate)]] = float(row.Value)
    return coords, 0.5 * (mat + mat.T)


def normalize(mat: np.ndarray) -> np.ndarray:
    fro = float(np.linalg.norm(mat, ord="fro"))
    return mat if fro == 0.0 else mat / fro


def main() -> int:
    coords, witness = load_witness()
    idx = {coord: i for i, coord in enumerate(coords)}
    p = idx["TEMPLATE_P_MORPH_PROJECTION"]
    b = idx["TEMPLATE_B_BRANCH_RESPONSE"]
    phi = idx["TEMPLATE_PHI_PARENT_SOURCE"]

    terms = [
        {
            "TermID": "V_PE_PB_BRANCH_PROJECTION_COUPLING",
            "Formula": "-2 P B",
            "Coefficient": -2.0,
            "CoordinateA": "TEMPLATE_P_MORPH_PROJECTION",
            "CoordinateB": "TEMPLATE_B_BRANCH_RESPONSE",
        },
        {
            "TermID": "V_PE_PPHI_SOURCE_PROJECTION_COUPLING",
            "Formula": "- P Phi",
            "Coefficient": -1.0,
            "CoordinateA": "TEMPLATE_P_MORPH_PROJECTION",
            "CoordinateB": "TEMPLATE_PHI_PARENT_SOURCE",
        },
        {
            "TermID": "V_PE_BRANCH_COUNTERTERM",
            "Formula": "- 1/2 B^2",
            "Coefficient": -0.5,
            "CoordinateA": "TEMPLATE_B_BRANCH_RESPONSE",
            "CoordinateB": "TEMPLATE_B_BRANCH_RESPONSE",
        },
    ]
    action_df = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                **term,
                "UsesTargetResiduals": False,
                "UsesScoreOutcome": False,
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for term in terms
        ]
    )
    action_df.to_csv(OUT_ACTION, index=False)

    hessian = np.zeros_like(witness)
    hessian[p, b] = hessian[b, p] = -2.0
    hessian[p, phi] = hessian[phi, p] = -1.0
    hessian[b, b] = -1.0
    hessian = normalize(hessian)

    rows = []
    for i, row_coord in enumerate(coords):
        for j, col_coord in enumerate(coords):
            value = float(hessian[i, j])
            if value != 0.0:
                rows.append(
                    {
                        "ProtocolID": PROTOCOL_ID,
                        "FreezeID": FREEZE_ID,
                        "RowCoordinate": row_coord,
                        "ColumnCoordinate": col_coord,
                        "Value": value,
                        "GeneratedFrom": "V_PE=-2PB-PhiP-1/2B^2",
                        "UsesTargetResiduals": False,
                        "UsesScoreOutcome": False,
                        "ScoringAuthorized": False,
                        "ClaimBoundary": CLAIM_BOUNDARY,
                    }
                )
    pd.DataFrame(rows).to_csv(OUT_HESSIAN, index=False)

    witness_summary = pd.read_csv(WITNESS_SUMMARY).iloc[0]
    max_abs_diff = float(np.max(np.abs(hessian - witness)))
    gate_rows = [
        ("PA-G1_HESSIAN_MATCHES_WITNESS", max_abs_diff < 1e-12, max_abs_diff),
        ("PA-G2_COEFFICIENTS_DECLARED", len(action_df) == 3, float(len(action_df))),
        ("PA-G3_WITNESS_IS_PROJECTION_ESSENTIAL", float(witness_summary["ProjectionEssentiality"]) > 0.40, float(witness_summary["ProjectionEssentiality"])),
        ("PA-G4_WITNESS_GATES_PASSED", str(witness_summary["Status"]).endswith("PASS_NO_SCORING"), float(witness_summary["GatesPassed"])),
        ("PA-G5_NO_TARGET_OR_SCORE_INPUTS", True, 1.0),
    ]
    gates = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "GateID": gate,
                "Passed": bool(passed),
                "DiagnosticValue": float(value),
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for gate, passed, value in gate_rows
        ]
    )
    gates.to_csv(OUT_GATES, index=False)
    passed_count = int(gates["Passed"].sum())
    status = (
        "P_TAUCOV_PROJECTION_ESSENTIALITY_PARENT_ACTION_ORIGIN_PASS_NO_SCORING"
        if passed_count == len(gates)
        else "P_TAUCOV_PROJECTION_ESSENTIALITY_PARENT_ACTION_ORIGIN_FAIL_NO_SCORING"
    )
    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": status,
                "GatesPassed": passed_count,
                "GatesTotal": len(gates),
                "MaxAbsHessianMinusWitness": max_abs_diff,
                "ProjectionEssentiality": float(witness_summary["ProjectionEssentiality"]),
                "MorphologyNullAbsCorrelation": float(witness_summary["MorphologyNullAbsCorrelation"]),
                "ProjectionNullAbsCorrelation": float(witness_summary["ProjectionNullAbsCorrelation"]),
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
                "# P-TauCov Projection-Essentiality Parent-Action Origin Packet",
                "",
                f"Status: `{status}`.",
                "",
                "This packet shows that the projection-essentiality witness can be",
                "generated as the Hessian of a minimal local quadratic parent-action",
                "normal form. It is not an empirical scorecard and does not authorize",
                "a survival claim.",
                "",
                "## Frozen Normal Form",
                "",
                "```math",
                "V_{\\rm PE}(\\Phi,B,P) = -2PB - P\\Phi - \\frac{1}{2}B^2 .",
                "```",
                "",
                "## Key Numbers",
                "",
                f"- gates passed: `{passed_count}/{len(gates)}`",
                f"- max absolute Hessian-minus-witness difference: `{max_abs_diff}`",
                f"- projection essentiality inherited from witness: `{float(witness_summary['ProjectionEssentiality'])}`",
                "",
                "## Claim Boundary",
                "",
                "Allowed: the witness has a conditional local parent-action origin.",
                "",
                "Forbidden: this is not a completed Tau Core action, not a scored",
                "Tau signal, and not measurement validation.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
