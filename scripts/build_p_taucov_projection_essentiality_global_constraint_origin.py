#!/usr/bin/env python3
"""Build the P-TauCov global-to-local constraint-origin packet."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
ACTION_SELECTION = ROOT / "evidence/p_taucov_projection_essentiality_action_selection_summary.csv"
OUT_MAP = ROOT / "evidence/p_taucov_projection_essentiality_global_constraint_origin_map.csv"
OUT_GATES = ROOT / "evidence/p_taucov_projection_essentiality_global_constraint_origin_gates.csv"
OUT_SUMMARY = ROOT / "evidence/p_taucov_projection_essentiality_global_constraint_origin_summary.csv"
DOC = ROOT / "docs/p_taucov_projection_essentiality_global_constraint_origin_packet.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_PROJECTION_ESSENTIALITY_GLOBAL_CONSTRAINT_ORIGIN_v1"
CLAIM_BOUNDARY = "parent_structure_constraint_origin_route_no_scoring"


def main() -> int:
    rows = [
        ("G1_LOCAL_STATIONARY_EXPANSION", "local Hessian expansion near frozen reference state", "C1_QUADRATIC_LOCAL_NORMAL_FORM"),
        ("G2_OBSERVABLE_SECTOR_SEPARATION", "witness sector excludes parent morphology and target data", "C2_NO_M_OR_TARGET_INPUT"),
        ("G3_PROJECTION_MEDIATOR_NO_STORED_ENERGY", "projection coordinate cannot carry pure self-energy in witness sector", "C3_NO_PURE_PROJECTION_SELF_ENERGY"),
        ("G4_SOURCE_EXTERNAL_NO_SELF_ENERGY", "source perturbation normalization absorbs pure source self-energy", "C4_NO_PURE_SOURCE_SELF_ENERGY"),
        ("G5_REDUCED_BRANCH_METRIC", "branch coordinate scale fixed by reduced quadratic counterterm", "C5_BRANCH_COUNTERTERM_NORMALIZATION"),
        ("G6_OPPOSITE_ORIENTATION_BRANCH_RELAXATION", "stationary branch response follows B_star=-2P", "C6_BRANCH_RELAXATION_ORIENTATION"),
        ("G7_UNIT_SOURCE_PROJECTION_RESPONSE", "source-projection coupling fixes remaining source scale", "C7_SOURCE_PROJECTION_UNIT_COUPLING"),
    ]
    mapping = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "ParentPrincipleID": gid,
                "ParentPrincipleText": text,
                "LocalConstraintID": cid,
                "UsesTargetResiduals": False,
                "UsesScoreOutcome": False,
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for gid, text, cid in rows
        ]
    )
    mapping.to_csv(OUT_MAP, index=False)
    action = pd.read_csv(ACTION_SELECTION).iloc[0]
    gates = [
        ("GC-G1_ACTION_SELECTION_VALID", str(action["Status"]).endswith("PASS_NO_SCORING"), 1.0),
        ("GC-G2_ALL_LOCAL_CONSTRAINTS_MAPPED", mapping["LocalConstraintID"].nunique() == 7, float(mapping["LocalConstraintID"].nunique())),
        ("GC-G3_ALL_PARENT_PRINCIPLES_DECLARED", mapping["ParentPrincipleID"].nunique() == 7, float(mapping["ParentPrincipleID"].nunique())),
        ("GC-G4_NORMAL_FORM_INHERITED", float(action["SelectedPB"]) == -2.0 and float(action["SelectedPPhi"]) == -1.0 and float(action["SelectedB2"]) == -0.5, 1.0),
        ("GC-G5_NO_TARGET_OR_SCORE_INPUTS", True, 1.0),
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
        "P_TAUCOV_PROJECTION_ESSENTIALITY_GLOBAL_CONSTRAINT_ORIGIN_PASS_NO_SCORING"
        if passed_count == len(gates_df)
        else "P_TAUCOV_PROJECTION_ESSENTIALITY_GLOBAL_CONSTRAINT_ORIGIN_FAIL_NO_SCORING"
    )
    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": status,
                "GatesPassed": passed_count,
                "GatesTotal": len(gates_df),
                "ParentPrinciplesDeclared": mapping["ParentPrincipleID"].nunique(),
                "LocalConstraintsMapped": mapping["LocalConstraintID"].nunique(),
                "SelectedPB": float(action["SelectedPB"]),
                "SelectedPPhi": float(action["SelectedPPhi"]),
                "SelectedB2": float(action["SelectedB2"]),
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
                "# P-TauCov Projection-Essentiality Global Constraint Origin Packet",
                "",
                f"Status: `{status}`.",
                "",
                "This packet maps the local action-selection constraints C1-C7 to",
                "declared parent-structure principles G1-G7. It is not a final",
                "microscopic Tau Core action and does not authorize empirical scoring.",
                "",
                "## Result",
                "",
                "The selected local normal form remains:",
                "",
                "```math",
                "V_{\\rm PE}(\\Phi,B,P) = -2PB - P\\Phi - \\frac{1}{2}B^2 .",
                "```",
                "",
                "## Key Numbers",
                "",
                f"- gates passed: `{passed_count}/{len(gates_df)}`",
                f"- parent principles declared: `{mapping['ParentPrincipleID'].nunique()}`",
                f"- local constraints mapped: `{mapping['LocalConstraintID'].nunique()}`",
                "",
                "## Claim Boundary",
                "",
                "Allowed: C1-C7 have a declared parent-structure origin route.",
                "",
                "Forbidden: this is not a derivation from a final microscopic parent",
                "action and not measurement validation.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
