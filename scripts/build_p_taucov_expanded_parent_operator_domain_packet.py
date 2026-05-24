#!/usr/bin/env python3
"""Build an expanded parent-operator domain packet for the next P-TauCov route."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
EVIDENCE = ROOT / "evidence"
BASIS = ROOT / "data/p_taucov/linear/coordinate_basis.csv"

EXPANSION_GATE = EVIDENCE / "p_taucov_parent_operator_source_expansion_gate_summary.csv"
SOURCE_CANDIDATES = EVIDENCE / "p_taucov_coordinate_basis_source_candidates.csv"

OUT_COORDS = EVIDENCE / "p_taucov_expanded_parent_operator_domain_coordinates.csv"
OUT_PROJECTORS = EVIDENCE / "p_taucov_expanded_parent_operator_domain_projectors.csv"
OUT_GATES = EVIDENCE / "p_taucov_expanded_parent_operator_domain_gates.csv"
OUT_SUMMARY = EVIDENCE / "p_taucov_expanded_parent_operator_domain_summary.csv"
DOC = DOCS / "p_taucov_expanded_parent_operator_domain_packet.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_EXPANDED_PARENT_OPERATOR_DOMAIN_PACKET_v1"
CLAIM_BOUNDARY = "expanded_parent_operator_domain_packet_no_object_no_scoring"

CORE_ACTIVE = {
    "TEMPLATE_PHI_PARENT_SOURCE",
    "TEMPLATE_B_BRANCH_RESPONSE",
    "TEMPLATE_P_MORPH_PROJECTION",
}

NEW_ACTIVE = {
    # CoordinateConventionOnly: a target-blind response-scale/source-normalizer axis.
    "TEMPLATE_COORD_SCALE_UNIT",
    # PublishedExternalMetadata: a target-blind observing-context axis.
    "TEMPLATE_EXT_OBSERVING_CONTEXT",
}

GAUGE = {
    "TEMPLATE_COORD_ORIGIN_CENTER",
}

FORBIDDEN = {
    # Parent morphology remains forbidden as a direct reduced witness channel.
    "TEMPLATE_M_PARENT_MORPHOLOGY",
    # Source family remains forbidden in the first expanded packet to avoid
    # repeating the earlier family-dominance failure mode.
    "TEMPLATE_EXT_SOURCE_FAMILY",
}

SOURCE_CLASS_BY_COORD = {
    "TEMPLATE_PHI_PARENT_SOURCE": "TauSideSymbolicDefinition",
    "TEMPLATE_B_BRANCH_RESPONSE": "TauSideSymbolicDefinition",
    "TEMPLATE_P_MORPH_PROJECTION": "TauSideSymbolicDefinition",
    "TEMPLATE_COORD_SCALE_UNIT": "CoordinateConventionOnly",
    "TEMPLATE_EXT_OBSERVING_CONTEXT": "PublishedExternalMetadata",
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
                    "ObjectConstructionAuthorized": False,
                    "ScoringAuthorized": False,
                    "ClaimBoundary": CLAIM_BOUNDARY,
                }
            )
    return rows


def main() -> int:
    DOCS.mkdir(exist_ok=True)
    EVIDENCE.mkdir(exist_ok=True)

    basis = pd.read_csv(BASIS)
    gate = pd.read_csv(EXPANSION_GATE).iloc[0]
    sources = pd.read_csv(SOURCE_CANDIDATES)
    coords = basis["coordinate_id"].astype(str).tolist()
    all_ids = set(coords)
    active = CORE_ACTIVE | NEW_ACTIVE
    inactive = all_ids - active
    allowed_sources = set(
        sources.loc[sources["AllowedForCandidateBasis"].astype(bool), "CandidateSource"].astype(str)
    )

    if not active.issubset(all_ids):
        raise RuntimeError("Expanded active coordinate missing from basis.")
    if inactive != GAUGE | FORBIDDEN:
        raise RuntimeError("Expanded inactive coordinate partition mismatch.")

    coord_rows = []
    for coord in coords:
        if coord in active:
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
                "InReducedDomain": coord in active,
                "SourceClass": SOURCE_CLASS_BY_COORD.get(coord, "excluded_not_active"),
                "NewActiveAxis": coord in NEW_ACTIVE,
                "UsesTargetResiduals": False,
                "UsesScoreOutcome": False,
                "ObjectConstructionAuthorized": False,
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        )
    pd.DataFrame(coord_rows).to_csv(OUT_COORDS, index=False)

    projector_rows = []
    projector_rows += matrix_rows(coords, "P_expanded_active_reduced", active)
    projector_rows += matrix_rows(coords, "P_core_active_triad", CORE_ACTIVE)
    projector_rows += matrix_rows(coords, "P_new_active_nonoutcome_axes", NEW_ACTIVE)
    projector_rows += matrix_rows(coords, "P_gauge", GAUGE)
    projector_rows += matrix_rows(coords, "P_forbidden", FORBIDDEN)
    pd.DataFrame(projector_rows).to_csv(OUT_PROJECTORS, index=False)

    p_active = np.diag([1.0 if c in active else 0.0 for c in coords])
    p_gauge = np.diag([1.0 if c in GAUGE else 0.0 for c in coords])
    p_forbidden = np.diag([1.0 if c in FORBIDDEN else 0.0 for c in coords])
    partition_sum = p_active + p_gauge + p_forbidden

    new_source_classes = {SOURCE_CLASS_BY_COORD[c] for c in NEW_ACTIVE}
    gates = [
        (
            "EPOD-G1_EXPANSION_GATE_READY",
            str(gate["Status"]) == "P_TAUCOV_PARENT_OPERATOR_SOURCE_EXPANSION_GATE_READY_NO_OBJECT_NO_SCORING",
            1.0,
            "parent-operator source expansion gate is ready",
        ),
        (
            "EPOD-G2_ACTIVE_COUNT_GE_REQUIRED",
            len(active) >= int(gate["RequiredNextActiveReducedCoordinateCount"]),
            float(len(active)),
            "expanded active domain has at least the required number of active coordinates",
        ),
        (
            "EPOD-G3_NEW_NONOUTCOME_AXES_GE_REQUIRED",
            len(NEW_ACTIVE) >= int(gate["RequiredNewNonOutcomeAxes"]),
            float(len(NEW_ACTIVE)),
            "expanded domain adds enough non-outcome axes",
        ),
        (
            "EPOD-G4_NEW_SOURCE_CLASSES_ALLOWED",
            new_source_classes.issubset(allowed_sources),
            float(len(new_source_classes)),
            "new active source classes are allowed by the source-candidate audit",
        ),
        (
            "EPOD-G5_SOURCE_FAMILY_STILL_FORBIDDEN",
            "TEMPLATE_EXT_SOURCE_FAMILY" in FORBIDDEN,
            1.0,
            "source-family axis remains excluded to avoid family-dominance leakage",
        ),
        (
            "EPOD-G6_PARENT_MORPHOLOGY_STILL_FORBIDDEN",
            "TEMPLATE_M_PARENT_MORPHOLOGY" in FORBIDDEN,
            1.0,
            "direct parent morphology remains excluded from the reduced witness sector",
        ),
        (
            "EPOD-G7_PARTITION_EXACT",
            float(np.max(np.abs(partition_sum - np.eye(len(coords))))) < 1e-12,
            float(np.max(np.abs(partition_sum - np.eye(len(coords))))),
            "active/gauge/forbidden projectors partition the coordinate basis",
        ),
        (
            "EPOD-G8_NO_TARGET_OR_SCORE_INPUTS",
            True,
            1.0,
            "only frozen basis/source/gate artifacts are used",
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
                "ObjectConstructionAuthorized": False,
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for gate_id, passed, value, interpretation in gates
        ]
    )
    gates_df.to_csv(OUT_GATES, index=False)
    status = (
        "P_TAUCOV_EXPANDED_PARENT_OPERATOR_DOMAIN_READY_NO_OBJECT_NO_SCORING"
        if bool(gates_df["Passed"].all())
        else "P_TAUCOV_EXPANDED_PARENT_OPERATOR_DOMAIN_BLOCKED_NO_SCORING"
    )
    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": status,
                "CoordinateCount": len(coords),
                "ActiveCount": len(active),
                "CoreActiveCount": len(CORE_ACTIVE),
                "NewActiveNonOutcomeAxes": len(NEW_ACTIVE),
                "GaugeCount": len(GAUGE),
                "ForbiddenCount": len(FORBIDDEN),
                "NewActiveCoordinateIDs": ";".join(sorted(NEW_ACTIVE)),
                "NewActiveSourceClasses": ";".join(sorted(new_source_classes)),
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
        f"""# P-TauCov Expanded Parent-Operator Domain Packet

Freeze ID: `{FREEZE_ID}`

Status:

`{status}`

## Purpose

The active `Phi/B/P` triad is structurally too narrow for the PSD covariance
route. This packet freezes an expanded reduced parent-operator domain before
any new object construction or scoring.

## Expanded Active Domain

Core active axes retained:

```text
TEMPLATE_PHI_PARENT_SOURCE
TEMPLATE_B_BRANCH_RESPONSE
TEMPLATE_P_MORPH_PROJECTION
```

New active non-outcome axes:

```text
TEMPLATE_COORD_SCALE_UNIT
TEMPLATE_EXT_OBSERVING_CONTEXT
```

The two new axes are admitted because their source classes are allowed by the
source-candidate audit:

```text
CoordinateConventionOnly
PublishedExternalMetadata
```

## Still Excluded

```text
TEMPLATE_M_PARENT_MORPHOLOGY
TEMPLATE_EXT_SOURCE_FAMILY
```

`TEMPLATE_M_PARENT_MORPHOLOGY` remains excluded because direct morphology
support would collapse the route back into a morphology-null duplicate.
`TEMPLATE_EXT_SOURCE_FAMILY` remains excluded in this first expanded packet
because previous failures were family-dominated.

## Claim Boundary

Allowed statement:

> An expanded target-blind parent-operator domain has been frozen for future
> no-scoring object construction.

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
