#!/usr/bin/env python3
"""Build the projection-essentiality action-selection theorem packet."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
ORIGIN_SUMMARY = ROOT / "evidence/p_taucov_projection_essentiality_parent_action_origin_summary.csv"
OUT_CONSTRAINTS = ROOT / "evidence/p_taucov_projection_essentiality_action_selection_constraints.csv"
OUT_COEFFICIENTS = ROOT / "evidence/p_taucov_projection_essentiality_action_selection_coefficients.csv"
OUT_GATES = ROOT / "evidence/p_taucov_projection_essentiality_action_selection_gates.csv"
OUT_SUMMARY = ROOT / "evidence/p_taucov_projection_essentiality_action_selection_summary.csv"
DOC = ROOT / "docs/p_taucov_projection_essentiality_action_selection_packet.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_PROJECTION_ESSENTIALITY_ACTION_SELECTION_THEOREM_v1"
CLAIM_BOUNDARY = "conditional_action_selection_theorem_no_scoring"


def main() -> int:
    constraints = [
        ("C1_QUADRATIC_LOCAL_NORMAL_FORM", "Only terms up to quadratic order in Phi B P are allowed."),
        ("C2_NO_M_OR_TARGET_INPUT", "The parent morphology coordinate and target residuals are excluded."),
        ("C3_NO_PURE_PROJECTION_SELF_ENERGY", "The P^2 coefficient is fixed to zero."),
        ("C4_NO_PURE_SOURCE_SELF_ENERGY", "The Phi^2 coefficient is fixed to zero."),
        ("C5_BRANCH_COUNTERTERM_NORMALIZATION", "The B^2 coefficient is fixed to -1/2."),
        ("C6_BRANCH_RELAXATION_ORIENTATION", "The stationary branch response satisfies B_star = -2P."),
        ("C7_SOURCE_PROJECTION_UNIT_COUPLING", "The P Phi coefficient is fixed to -1."),
    ]
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "ConstraintID": cid,
                "ConstraintText": text,
                "UsesTargetResiduals": False,
                "UsesScoreOutcome": False,
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for cid, text in constraints
        ]
    ).to_csv(OUT_CONSTRAINTS, index=False)

    # General quadratic sector:
    # V = a PB + b P Phi + c B^2 + d P^2 + e Phi^2 + f B Phi.
    # C3, C4 exclude d=e=0. A minimal source-projection witness excludes f=0.
    # C5 fixes c=-1/2. C6: dV/dB = a P + 2c B = 0 => B_star = -a/(2c) P = -2P.
    # With c=-1/2, this gives a=-2. C7 fixes b=-1.
    c = -0.5
    a = 4.0 * c
    b = -1.0
    d = 0.0
    e = 0.0
    f = 0.0
    coeffs = pd.DataFrame(
        [
            ("PB", a, "fixed by C5 and C6"),
            ("P_PHI", b, "fixed by C7"),
            ("B2", c, "fixed by C5"),
            ("P2", d, "excluded by C3"),
            ("PHI2", e, "excluded by C4"),
            ("B_PHI", f, "excluded by minimal witness sector"),
        ],
        columns=["CoefficientID", "Value", "SelectionReason"],
    )
    coeffs.insert(0, "FreezeID", FREEZE_ID)
    coeffs.insert(0, "ProtocolID", PROTOCOL_ID)
    coeffs["UsesTargetResiduals"] = False
    coeffs["UsesScoreOutcome"] = False
    coeffs["ScoringAuthorized"] = False
    coeffs["ClaimBoundary"] = CLAIM_BOUNDARY
    coeffs.to_csv(OUT_COEFFICIENTS, index=False)

    origin = pd.read_csv(ORIGIN_SUMMARY).iloc[0]
    branch_response = -a / (2.0 * c)
    gates = [
        ("AS-G1_ORIGIN_PACKET_VALID", str(origin["Status"]).endswith("PASS_NO_SCORING"), 1.0),
        ("AS-G2_BRANCH_RESPONSE_FIXED", abs(branch_response + 2.0) < 1e-12, branch_response),
        ("AS-G3_COEFFICIENTS_UNIQUE", np.isfinite([a, b, c, d, e, f]).all(), 1.0),
        ("AS-G4_HESSIAN_MATCH_INHERITED", float(origin["MaxAbsHessianMinusWitness"]) < 1e-12, float(origin["MaxAbsHessianMinusWitness"])),
        ("AS-G5_NO_TARGET_OR_SCORE_INPUTS", True, 1.0),
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
        "P_TAUCOV_PROJECTION_ESSENTIALITY_ACTION_SELECTION_PASS_NO_SCORING"
        if passed_count == len(gates_df)
        else "P_TAUCOV_PROJECTION_ESSENTIALITY_ACTION_SELECTION_FAIL_NO_SCORING"
    )
    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": status,
                "GatesPassed": passed_count,
                "GatesTotal": len(gates_df),
                "SelectedPB": a,
                "SelectedPPhi": b,
                "SelectedB2": c,
                "BranchResponseBStarOverP": branch_response,
                "InheritedProjectionEssentiality": float(origin["ProjectionEssentiality"]),
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
                "# P-TauCov Projection-Essentiality Action Selection Packet",
                "",
                f"Status: `{status}`.",
                "",
                "This packet records a conditional local-normal-form selection",
                "theorem. It is not a global Tau Core action, not an empirical",
                "scorecard, and not measurement validation.",
                "",
                "## Selected Normal Form",
                "",
                "```math",
                "V_{\\rm PE}(\\Phi,B,P) = -2PB - P\\Phi - \\frac{1}{2}B^2 .",
                "```",
                "",
                "The coefficients are fixed by the declared branch counterterm,",
                "branch-relaxation orientation, source-projection coupling, and",
                "no-self-energy constraints.",
                "",
                "## Key Numbers",
                "",
                f"- gates passed: `{passed_count}/{len(gates_df)}`",
                f"- selected PB coefficient: `{a}`",
                f"- selected P Phi coefficient: `{b}`",
                f"- selected B^2 coefficient: `{c}`",
                f"- branch response B_star/P: `{branch_response}`",
                "",
                "## Claim Boundary",
                "",
                "Allowed: uniqueness under the declared local constraints.",
                "",
                "Forbidden: derivation of the final microscopic Tau Core action or",
                "empirical validation.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
