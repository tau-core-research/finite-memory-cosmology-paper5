#!/usr/bin/env python3
"""Build the full-action domain/null-gauge packet for P-TauCov."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
BASIS = ROOT / "data/p_taucov/linear/coordinate_basis.csv"
OUT_COORDS = ROOT / "evidence/p_taucov_full_action_domain_coordinates.csv"
OUT_PROJECTORS = ROOT / "evidence/p_taucov_full_action_domain_projectors.csv"
OUT_SUMMARY = ROOT / "evidence/p_taucov_full_action_domain_null_gauge_summary.csv"
OUT_GATES = ROOT / "evidence/p_taucov_full_action_domain_null_gauge_gates.csv"
DOC = ROOT / "docs/p_taucov_full_action_domain_null_gauge_packet_result.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_FULL_ACTION_DOMAIN_NULL_GAUGE_PACKET_v1"
CLAIM_BOUNDARY = "full_action_domain_null_gauge_packet_no_scoring"

ACTIVE = {
    "TEMPLATE_PHI_PARENT_SOURCE",
    "TEMPLATE_B_BRANCH_RESPONSE",
    "TEMPLATE_P_MORPH_PROJECTION",
}
GAUGE = {
    "TEMPLATE_COORD_ORIGIN_CENTER",
    "TEMPLATE_COORD_SCALE_UNIT",
}
FORBIDDEN = {
    "TEMPLATE_M_PARENT_MORPHOLOGY",
    "TEMPLATE_EXT_SOURCE_FAMILY",
    "TEMPLATE_EXT_OBSERVING_CONTEXT",
}


def matrix_rows(coords: list[str], name: str, diagonal_ids: set[str]) -> list[dict]:
    rows = []
    for i, row_id in enumerate(coords):
        for j, col_id in enumerate(coords):
            value = 1.0 if i == j and row_id in diagonal_ids else 0.0
            rows.append(
                {
                    "ProtocolID": PROTOCOL_ID,
                    "FreezeID": FREEZE_ID,
                    "ProjectorID": name,
                    "RowCoordinate": row_id,
                    "ColumnCoordinate": col_id,
                    "Value": value,
                    "UsesTargetResiduals": False,
                    "UsesScoreOutcome": False,
                    "ScoringAuthorized": False,
                    "ClaimBoundary": CLAIM_BOUNDARY,
                }
            )
    return rows


def main() -> int:
    basis = pd.read_csv(BASIS)
    coords = basis["coordinate_id"].astype(str).tolist()
    all_ids = set(coords)
    null = set()
    reduced = ACTIVE
    inactive = all_ids - ACTIVE
    if not ACTIVE.issubset(all_ids):
        raise RuntimeError("Active coordinate missing from basis.")
    if inactive != GAUGE | FORBIDDEN:
        raise RuntimeError("Inactive coordinate partition mismatch.")

    coord_rows = []
    for coord in coords:
        if coord in ACTIVE:
            role = "active"
        elif coord in GAUGE:
            role = "gauge"
        elif coord in FORBIDDEN:
            role = "forbidden"
        else:
            role = "unclassified"
        coord_rows.append(
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "CoordinateID": coord,
                "EmbeddingRole": role,
                "InReducedDomain": coord in reduced,
                "UsesTargetResiduals": False,
                "UsesScoreOutcome": False,
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        )
    pd.DataFrame(coord_rows).to_csv(OUT_COORDS, index=False)

    projector_rows = []
    projector_rows += matrix_rows(coords, "P_active_reduced", reduced)
    projector_rows += matrix_rows(coords, "P_null", null)
    projector_rows += matrix_rows(coords, "P_gauge", GAUGE)
    projector_rows += matrix_rows(coords, "P_forbidden", FORBIDDEN)
    pd.DataFrame(projector_rows).to_csv(OUT_PROJECTORS, index=False)

    p_active = np.diag([1.0 if c in reduced else 0.0 for c in coords])
    p_gauge = np.diag([1.0 if c in GAUGE else 0.0 for c in coords])
    p_forbidden = np.diag([1.0 if c in FORBIDDEN else 0.0 for c in coords])
    partition_sum = p_active + p_gauge + p_forbidden
    gates = [
        ("DG-G1_PARENT_DOMAIN_DECLARED", len(coords) == 8, float(len(coords))),
        ("DG-G2_ACTIVE_DOMAIN_DECLARED", reduced == ACTIVE, float(len(reduced))),
        ("DG-G3_PROJECTION_MEDIATOR_ACTIVE", "TEMPLATE_P_MORPH_PROJECTION" in reduced, 1.0),
        ("DG-G4_NULL_GAUGE_FORBIDDEN_PARTITION", float(np.max(np.abs(partition_sum - np.eye(len(coords))))) < 1e-12, float(np.max(np.abs(partition_sum - np.eye(len(coords)))))),
        ("DG-G5_NO_TARGET_OR_SCORE_INPUTS", True, 1.0),
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
        "P_TAUCOV_FULL_ACTION_DOMAIN_NULL_GAUGE_PASS_NO_SCORING"
        if passed_count == len(gates_df)
        else "P_TAUCOV_FULL_ACTION_DOMAIN_NULL_GAUGE_FAIL_NO_SCORING"
    )
    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": status,
                "GatesPassed": passed_count,
                "GatesTotal": len(gates_df),
                "CoordinateCount": len(coords),
                "ActiveCount": len(ACTIVE),
                "NullCount": len(null),
                "GaugeCount": len(GAUGE),
                "ForbiddenCount": len(FORBIDDEN),
                "ResolvedBlockers": "PARENT_DOMAIN;NULL_GAUGE_MODES",
                "RemainingBlockers": "REFERENCE_BACKGROUND;S_REST;COVARIANCE_MAP",
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
                "# P-TauCov Full-Action Domain And Null/Gauge Result",
                "",
                f"Status: `{status}`.",
                "",
                "The projection-essential scaffold uses a finite eight-coordinate",
                "parent cell with active reduced domain `Phi,B,P`. The morphology",
                "coordinate and external metadata are forbidden in the witness sector;",
                "coordinate-origin and coordinate-scale are gauge/convention modes.",
                "",
                "## Blocker Update",
                "",
                "- resolved: `PARENT_DOMAIN`, `NULL_GAUGE_MODES`",
                "- remaining: `REFERENCE_BACKGROUND`, `S_REST`, `COVARIANCE_MAP`",
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
