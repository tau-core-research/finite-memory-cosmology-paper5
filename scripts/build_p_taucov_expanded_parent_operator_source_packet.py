#!/usr/bin/env python3
"""Build a target-blind expanded parent-operator source packet."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EVIDENCE = ROOT / "evidence"

DOMAIN_SUMMARY = EVIDENCE / "p_taucov_expanded_parent_operator_domain_summary.csv"
DOMAIN_COORDS = EVIDENCE / "p_taucov_expanded_parent_operator_domain_coordinates.csv"

OUT_MATRIX = EVIDENCE / "p_taucov_expanded_parent_operator_source_matrix.csv"
OUT_GATES = EVIDENCE / "p_taucov_expanded_parent_operator_source_gates.csv"
OUT_SUMMARY = EVIDENCE / "p_taucov_expanded_parent_operator_source_summary.csv"
DOC = DOCS / "p_taucov_expanded_parent_operator_source_packet.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_EXPANDED_PARENT_OPERATOR_SOURCE_PACKET_v1"
CLAIM_BOUNDARY = "expanded_parent_operator_source_packet_no_scoring"

PHI = "TEMPLATE_PHI_PARENT_SOURCE"
B = "TEMPLATE_B_BRANCH_RESPONSE"
P = "TEMPLATE_P_MORPH_PROJECTION"
SCALE = "TEMPLATE_COORD_SCALE_UNIT"
CONTEXT = "TEMPLATE_EXT_OBSERVING_CONTEXT"
M_PARENT = "TEMPLATE_M_PARENT_MORPHOLOGY"
FAMILY = "TEMPLATE_EXT_SOURCE_FAMILY"


def write_sparse(path: Path, coords: list[str], matrix: np.ndarray) -> None:
    rows = []
    for i, row_coord in enumerate(coords):
        for j, col_coord in enumerate(coords):
            value = float(matrix[i, j])
            if abs(value) > 0.0:
                rows.append(
                    {
                        "ProtocolID": PROTOCOL_ID,
                        "FreezeID": FREEZE_ID,
                        "MatrixID": "ExpandedParentOperatorSource_v1",
                        "RowCoordinate": row_coord,
                        "ColumnCoordinate": col_coord,
                        "Value": value,
                        "CoefficientSource": "role_declared_parent_operator_normal_form",
                        "UsesTargetResiduals": False,
                        "UsesScoreOutcome": False,
                        "ScoringAuthorized": False,
                        "ClaimBoundary": CLAIM_BOUNDARY,
                    }
                )
    pd.DataFrame(rows).to_csv(path, index=False)


def main() -> int:
    DOCS.mkdir(exist_ok=True)
    EVIDENCE.mkdir(exist_ok=True)

    domain_summary = pd.read_csv(DOMAIN_SUMMARY).iloc[0]
    domain = pd.read_csv(DOMAIN_COORDS)
    coords = domain["CoordinateID"].astype(str).tolist()
    idx = {coord: i for i, coord in enumerate(coords)}
    active = set(domain.loc[domain["InReducedDomain"].astype(bool), "CoordinateID"].astype(str))
    forbidden = set(domain.loc[domain["EmbeddingRole"].eq("forbidden"), "CoordinateID"].astype(str))

    matrix = np.zeros((len(coords), len(coords)), dtype=float)

    def couple(a: str, b: str, value: float) -> None:
        matrix[idx[a], idx[b]] = value
        matrix[idx[b], idx[a]] = value

    # Core local parent-action normal form inherited from the
    # projection-essentiality parent-action origin note.
    couple(PHI, P, -1.0)
    couple(B, P, -2.0)
    matrix[idx[B], idx[B]] = -0.5

    # Scale is a coordinate-convention axis, so it enters as a symmetric
    # target-blind normalization response to all three core active axes.
    for coord in [PHI, B, P]:
        couple(SCALE, coord, 1.0)

    # Observing context is a published-metadata axis, so it enters only as an
    # antisymmetric role contrast between source and projection readout. This
    # avoids direct family localization and direct morphology support.
    couple(CONTEXT, PHI, 1.0)
    couple(CONTEXT, P, -1.0)

    write_sparse(OUT_MATRIX, coords, matrix)

    fro = float(np.linalg.norm(matrix, ord="fro"))
    active_ids = [idx[c] for c in coords if c in active]
    forbidden_ids = [idx[c] for c in coords if c in forbidden]
    active_norm = float(np.linalg.norm(matrix[np.ix_(active_ids, active_ids)], ord="fro"))
    forbidden_leakage = (
        float(np.linalg.norm(matrix[forbidden_ids, :], ord="fro") + np.linalg.norm(matrix[:, forbidden_ids], ord="fro"))
        if forbidden_ids
        else 0.0
    )
    nonzero_active_coords = {
        coords[i]
        for i in active_ids
        if np.linalg.norm(matrix[i, :], ord=2) + np.linalg.norm(matrix[:, i], ord=2) > 1e-12
    }
    new_active_touched = {SCALE, CONTEXT}.issubset(nonzero_active_coords)

    gates = [
        (
            "EPOS-G1_EXPANDED_DOMAIN_READY",
            str(domain_summary["Status"]) == "P_TAUCOV_EXPANDED_PARENT_OPERATOR_DOMAIN_READY_NO_OBJECT_NO_SCORING",
            1.0,
            "expanded parent-operator domain is ready",
        ),
        (
            "EPOS-G2_SOURCE_MATRIX_NONZERO",
            fro > 0.0,
            fro,
            "expanded parent-side source matrix is nonzero",
        ),
        (
            "EPOS-G3_ACTIVE_SUPPORT_GE_5",
            len(nonzero_active_coords) >= 5,
            float(len(nonzero_active_coords)),
            "all five active axes are touched by the source rule",
        ),
        (
            "EPOS-G4_NEW_NONOUTCOME_AXES_TOUCHED",
            new_active_touched,
            float(new_active_touched),
            "scale and observing-context axes are active in the source rule",
        ),
        (
            "EPOS-G5_NO_FORBIDDEN_SUPPORT",
            forbidden_leakage < 1e-12,
            forbidden_leakage,
            "direct morphology and source-family axes remain excluded",
        ),
        (
            "EPOS-G6_NOT_DIAGONAL_ONLY",
            float(np.linalg.norm(matrix - np.diag(np.diag(matrix)), ord="fro")) > 0.0,
            float(np.linalg.norm(matrix - np.diag(np.diag(matrix)), ord="fro")),
            "source rule has off-diagonal parent coupling",
        ),
        (
            "EPOS-G7_NO_TARGET_OR_SCORE_INPUTS",
            True,
            1.0,
            "coefficients are role-declared, not score-derived",
        ),
    ]
    gates_df = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "GateID": gate_id,
                "Passed": bool(passed),
                "DiagnosticValue": float(value),
                "Interpretation": interpretation,
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for gate_id, passed, value, interpretation in gates
        ]
    )
    gates_df.to_csv(OUT_GATES, index=False)
    status = (
        "P_TAUCOV_EXPANDED_PARENT_OPERATOR_SOURCE_READY_NO_SCORING"
        if bool(gates_df["Passed"].all())
        else "P_TAUCOV_EXPANDED_PARENT_OPERATOR_SOURCE_BLOCKED_NO_SCORING"
    )
    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": status,
                "CoordinateCount": len(coords),
                "ActiveCoordinateSupportCount": len(nonzero_active_coords),
                "NonzeroEntries": int(np.count_nonzero(np.abs(matrix) > 0.0)),
                "FrobeniusNorm": fro,
                "ActiveSubmatrixNorm": active_norm,
                "ForbiddenLeakageNorm": forbidden_leakage,
                "NewActiveAxesTouched": ";".join(sorted({SCALE, CONTEXT} & nonzero_active_coords)),
                "ObjectConstructionAuthorized": False,
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    )
    summary.to_csv(OUT_SUMMARY, index=False)

    DOC.write_text(
        f"""# P-TauCov Expanded Parent-Operator Source Packet

Freeze ID: `{FREEZE_ID}`

Status:

`{status}`

## Purpose

This packet freezes the first target-blind parent-side operator/source rule on
the expanded five-coordinate active domain. It does not construct a covariance
candidate and does not authorize scoring.

## Source Rule

The core `Phi/B/P` block inherits the local projection-essential parent-action
normal form:

```text
Phi -- P : -1
B   -- P : -2
B diagonal counterterm : -1/2
```

The two new non-outcome axes enter by role:

```text
SCALE_CONTEXT:
  SCALE -- Phi : +1
  SCALE -- B   : +1
  SCALE -- P   : +1

OBSERVING_CONTEXT:
  CONTEXT -- Phi : +1
  CONTEXT -- P   : -1
```

The source-family axis and direct parent-morphology axis remain excluded.

## Diagnostics

- active coordinate support count: `{len(nonzero_active_coords)}`
- nonzero entries: `{int(np.count_nonzero(np.abs(matrix) > 0.0))}`
- source Frobenius norm: `{fro}`
- forbidden leakage norm: `{forbidden_leakage}`
- gates passed: `{int(gates_df["Passed"].sum())}/{len(gates_df)}`

## Claim Boundary

Allowed statement:

> A target-blind expanded parent-side operator/source rule has been frozen.

Forbidden statement:

> This packet constructs a covariance object, authorizes scoring, or validates
> Tau Core.
""",
        encoding="utf-8",
    )
    print(status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
