#!/usr/bin/env python3
"""Freeze TCCS P_morph convention and Pi_perp matrix."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data/p_taucov/linear"
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

COORDINATES = DATA / "coordinate_basis.csv"
EMBEDDING = EVIDENCE / "p_taucov_tccs_parent_score_embedding_matrix.csv"

OUT_PMORPH_PARENT = EVIDENCE / "p_taucov_tccs_pmorph_parent_operator.csv"
OUT_PMORPH_SCORE = EVIDENCE / "p_taucov_tccs_pmorph_score_operator.csv"
OUT_PIPERP = EVIDENCE / "p_taucov_tccs_piperp_matrix.csv"
OUT_SUMMARY = EVIDENCE / "p_taucov_tccs_pmorph_piperp_summary.csv"
OUT_DOC = DOCS / "p_taucov_tccs_pmorph_piperp.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_TCCS_PMORPH_PIPERP_v1"
STATUS = "P_TAUCOV_TCCS_PMORPH_PIPERP_FROZEN_NO_OBJECT_NO_SCORING"
CLAIM_BOUNDARY = "tccs_pmorph_piperp_frozen_no_object_no_scoring"

MORPH_AXES = {"M_PARENT_MORPHOLOGY", "P_MORPH_PROJECTION"}


def matrix_records(matrix: np.ndarray, rows: list[str], cols: list[str], value_name: str = "Value") -> list[dict]:
    records = []
    for i, row_id in enumerate(rows):
        for j, col_id in enumerate(cols):
            value = float(matrix[i, j])
            if abs(value) > 1e-15:
                records.append({"RowID": row_id, "ColumnID": col_id, value_name: value})
    return records


def main() -> int:
    for path in [COORDINATES, EMBEDDING]:
        if not path.exists():
            raise FileNotFoundError(f"Missing input: {path.relative_to(ROOT)}")

    coords = pd.read_csv(COORDINATES)
    coord_ids = coords["coordinate_id"].astype(str).tolist()
    axes = dict(zip(coords["coordinate_id"].astype(str), coords["basis_axis"].astype(str)))
    morph_indices = [i for i, coord_id in enumerate(coord_ids) if axes[coord_id] in MORPH_AXES]
    if len(morph_indices) != 2:
        raise ValueError(f"Expected exactly two morphology/projection axes, got {morph_indices}")

    p_parent = np.zeros((len(coord_ids), len(coord_ids)), dtype=float)
    for i in morph_indices:
        p_parent[i, i] = 1.0

    emb = pd.read_csv(EMBEDDING)
    row_ids = list(dict.fromkeys(emb["EmpiricalRowID"].astype(str).tolist()))
    emb_coords = list(dict.fromkeys(emb["TauCoordinate"].astype(str).tolist()))
    e = emb.pivot(index="EmpiricalRowID", columns="TauCoordinate", values="EmbeddingValue").loc[row_ids, emb_coords].to_numpy(float)
    if emb_coords != coord_ids:
        raise ValueError("Embedding coordinate order does not match coordinate basis")

    p_score_raw = e @ p_parent @ e.T
    # Build Pi_perp as the orthogonal complement to the embedded morphology/projection columns.
    nuisance = e[:, morph_indices]
    q, r = np.linalg.qr(nuisance)
    active_rank = int(np.linalg.matrix_rank(nuisance))
    q = q[:, :active_rank]
    piperp = np.eye(e.shape[0]) - q @ q.T

    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                **record,
                "UsesTargetResiduals": False,
                "UsesScoreOutcomes": False,
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for record in matrix_records(p_parent, coord_ids, coord_ids)
        ]
    ).to_csv(OUT_PMORPH_PARENT, index=False)
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                **record,
                "UsesTargetResiduals": False,
                "UsesScoreOutcomes": False,
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for record in matrix_records(p_score_raw, row_ids, row_ids)
        ]
    ).to_csv(OUT_PMORPH_SCORE, index=False)
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                **record,
                "UsesTargetResiduals": False,
                "UsesScoreOutcomes": False,
                "ScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
            for record in matrix_records(piperp, row_ids, row_ids)
        ]
    ).to_csv(OUT_PIPERP, index=False)

    p_parent_sym = float(np.max(np.abs(p_parent - p_parent.T)))
    p_parent_idem = float(np.max(np.abs(p_parent @ p_parent - p_parent)))
    piperp_sym = float(np.max(np.abs(piperp - piperp.T)))
    piperp_idem = float(np.max(np.abs(piperp @ piperp - piperp)))
    piperp_rank = int(np.linalg.matrix_rank(piperp))
    nuisance_leakage = float(np.linalg.norm(piperp @ nuisance))

    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": STATUS,
                "ParentCoordinates": len(coord_ids),
                "EmpiricalRows": len(row_ids),
                "MorphAxes": ";".join(axes[coord_ids[i]] for i in morph_indices),
                "ParentPmorhSymmetryError": p_parent_sym,
                "ParentPmorphIdempotenceError": p_parent_idem,
                "PiPerpSymmetryError": piperp_sym,
                "PiPerpIdempotenceError": piperp_idem,
                "PiPerpRank": piperp_rank,
                "NuisanceLeakageNorm": nuisance_leakage,
                "UsesTargetResiduals": False,
                "UsesScoreOutcomes": False,
                "ObjectConstructionAuthorized": False,
                "ScoringAuthorized": False,
                "SurvivalClaimAuthorized": False,
                "TauCoreValidationClaimAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    ).to_csv(OUT_SUMMARY, index=False)

    OUT_DOC.write_text(
        f"""# P-TauCov TCCS P_morph And Pi_perp Freeze

Freeze ID: `P_TAUCOV_TCCS_PMORPH_PIPERP_v1`

Status:

`{STATUS}`

## P_morph Convention

The morphology/projection readout operator is frozen as the parent-coordinate
projector onto:

```text
M_PARENT_MORPHOLOGY
P_MORPH_PROJECTION
```

This is a convention freeze, not a score result.

## Pi_perp Convention

`Pi_perp` is the 36-row orthogonal complement to the embedded morphology and
projection columns under the frozen TCCS parent-to-score embedding.

## Diagnostics

| Quantity | Value |
|---|---:|
| parent P_morph symmetry error | `{p_parent_sym}` |
| parent P_morph idempotence error | `{p_parent_idem}` |
| Pi_perp symmetry error | `{piperp_sym}` |
| Pi_perp idempotence error | `{piperp_idem}` |
| Pi_perp rank | `{piperp_rank}` |
| nuisance leakage norm | `{nuisance_leakage}` |

## Claim Boundary

Allowed statement:

> The TCCS morphology operator convention and projection/morphology-orthogonal complement have been frozen without score access.

Forbidden statement:

> These matrices construct a TCCS object, authorize scoring, or produce a Tau signal.
""",
        encoding="utf-8",
    )
    print(STATUS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
