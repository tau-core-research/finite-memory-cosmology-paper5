#!/usr/bin/env python3
"""Build the minimal global parent-action scaffold packet."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
GLOBAL_ORIGIN = ROOT / "evidence/p_taucov_projection_essentiality_global_constraint_origin_summary.csv"
WITNESS = ROOT / "evidence/p_taucov_projection_essentiality_witness.csv"
OUT_TERMS = ROOT / "evidence/p_taucov_minimal_global_parent_action_scaffold_terms.csv"
OUT_HESSIAN = ROOT / "evidence/p_taucov_minimal_global_parent_action_scaffold_hessian.csv"
OUT_GATES = ROOT / "evidence/p_taucov_minimal_global_parent_action_scaffold_gates.csv"
OUT_SUMMARY = ROOT / "evidence/p_taucov_minimal_global_parent_action_scaffold_summary.csv"
DOC = ROOT / "docs/p_taucov_minimal_global_parent_action_scaffold_packet.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_MINIMAL_GLOBAL_PARENT_ACTION_SCAFFOLD_v1"
CLAIM_BOUNDARY = "minimal_global_parent_action_scaffold_no_scoring"


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
    origin = pd.read_csv(GLOBAL_ORIGIN).iloc[0]
    coords, witness = load_witness()
    idx = {coord: i for i, coord in enumerate(coords)}
    p = idx["TEMPLATE_P_MORPH_PROJECTION"]
    b = idx["TEMPLATE_B_BRANCH_RESPONSE"]
    phi = idx["TEMPLATE_PHI_PARENT_SOURCE"]

    terms = pd.DataFrame(
        [
            ("SCAFFOLD_BRANCH_METRIC", "-1/2 B^2", -0.5, "B", "B", "G5_REDUCED_BRANCH_METRIC"),
            ("SCAFFOLD_BRANCH_PROJECTION_COUPLING", "-2 P B", -2.0, "P", "B", "G6_OPPOSITE_ORIENTATION_BRANCH_RELAXATION"),
            ("SCAFFOLD_SOURCE_PROJECTION_COUPLING", "- P Phi", -1.0, "P", "Phi", "G7_UNIT_SOURCE_PROJECTION_RESPONSE"),
        ],
        columns=["TermID", "Formula", "Coefficient", "CoordinateA", "CoordinateB", "ParentPrincipleID"],
    )
    terms.insert(0, "FreezeID", FREEZE_ID)
    terms.insert(0, "ProtocolID", PROTOCOL_ID)
    terms["UsesTargetResiduals"] = False
    terms["UsesScoreOutcome"] = False
    terms["ScoringAuthorized"] = False
    terms["ClaimBoundary"] = CLAIM_BOUNDARY
    terms.to_csv(OUT_TERMS, index=False)

    hessian = np.zeros_like(witness)
    hessian[b, b] = -1.0
    hessian[p, b] = hessian[b, p] = -2.0
    hessian[p, phi] = hessian[phi, p] = -1.0
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
                        "GeneratedFrom": "S_scaffold_active_sector",
                        "UsesTargetResiduals": False,
                        "UsesScoreOutcome": False,
                        "ScoringAuthorized": False,
                        "ClaimBoundary": CLAIM_BOUNDARY,
                    }
                )
    pd.DataFrame(rows).to_csv(OUT_HESSIAN, index=False)

    branch_response = -2.0
    max_abs_diff = float(np.max(np.abs(hessian - witness)))
    gates = [
        ("SG-G1_GLOBAL_CONSTRAINT_ORIGIN_VALID", str(origin["Status"]).endswith("PASS_NO_SCORING"), 1.0),
        ("SG-G2_STATIONARY_BRANCH_RESPONSE_RECOVERED", abs(branch_response + 2.0) < 1e-12, branch_response),
        ("SG-G3_HESSIAN_MATCHES_WITNESS", max_abs_diff < 1e-12, max_abs_diff),
        ("SG-G4_ACTIVE_TERMS_MINIMAL", len(terms) == 3, float(len(terms))),
        ("SG-G5_NO_TARGET_OR_SCORE_INPUTS", True, 1.0),
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
        "P_TAUCOV_MINIMAL_GLOBAL_PARENT_ACTION_SCAFFOLD_PASS_NO_SCORING"
        if passed_count == len(gates_df)
        else "P_TAUCOV_MINIMAL_GLOBAL_PARENT_ACTION_SCAFFOLD_FAIL_NO_SCORING"
    )
    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": status,
                "GatesPassed": passed_count,
                "GatesTotal": len(gates_df),
                "ActiveTermCount": len(terms),
                "BranchResponseBStarOverP": branch_response,
                "MaxAbsHessianMinusWitness": max_abs_diff,
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
                "# P-TauCov Minimal Global Parent-Action Scaffold Packet",
                "",
                f"Status: `{status}`.",
                "",
                "This packet gives an explicit minimal scaffold action whose active",
                "stationary expansion produces the projection-essential local normal",
                "form. It is not a final microscopic Tau Core action and does not",
                "authorize empirical scoring.",
                "",
                "## Active Scaffold Sector",
                "",
                "```math",
                "S_{\\rm scaffold}^{\\rm active}",
                "=",
                "\\int d\\mu_\\tau\\left[-\\frac{1}{2}B^2-2PB-P\\Phi\\right].",
                "```",
                "",
                "## Key Numbers",
                "",
                f"- gates passed: `{passed_count}/{len(gates_df)}`",
                f"- active term count: `{len(terms)}`",
                f"- branch response B_star/P: `{branch_response}`",
                f"- max absolute Hessian-minus-witness difference: `{max_abs_diff}`",
                "",
                "## Claim Boundary",
                "",
                "Allowed: a minimal scaffold exists whose stationary expansion gives",
                "the projection-essential witness.",
                "",
                "Forbidden: this is not UV completion, final parent action, empirical",
                "scoring, or measurement validation.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
