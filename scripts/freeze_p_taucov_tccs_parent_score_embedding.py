#!/usr/bin/env python3
"""Freeze the TCCS parent-to-score embedding from the existing target-blind bridge."""

from __future__ import annotations

import hashlib
from pathlib import Path

import numpy as np
import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "evidence"
DOCS = ROOT / "docs"

SOURCE_BRIDGE = EVIDENCE / "p_taucov_epsilon_p3_coordinate_bridge.csv"
SOURCE_SUMMARY = EVIDENCE / "p_taucov_epsilon_p3_coordinate_bridge_summary.csv"
SOURCE_VALIDATION = EVIDENCE / "p_taucov_epsilon_p3_coordinate_bridge_validation.csv"

OUT_MATRIX = EVIDENCE / "p_taucov_tccs_parent_score_embedding_matrix.csv"
OUT_SUMMARY = EVIDENCE / "p_taucov_tccs_parent_score_embedding_summary.csv"
OUT_MANIFEST = EVIDENCE / "p_taucov_tccs_parent_score_embedding.yaml"
OUT_SHA = EVIDENCE / "p_taucov_tccs_parent_score_embedding.sha256"
OUT_DOC = DOCS / "p_taucov_tccs_parent_score_embedding.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_TCCS_PARENT_SCORE_EMBEDDING_v1"
STATUS = "P_TAUCOV_TCCS_PARENT_SCORE_EMBEDDING_FROZEN_NO_OBJECT_NO_SCORING"
CLAIM_BOUNDARY = "tccs_parent_score_embedding_frozen_no_object_no_scoring"


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    for path in [SOURCE_BRIDGE, SOURCE_SUMMARY, SOURCE_VALIDATION]:
        if not path.exists():
            raise FileNotFoundError(f"Missing source bridge artifact: {path.relative_to(ROOT)}")

    source_summary = pd.read_csv(SOURCE_SUMMARY).iloc[0]
    if str(source_summary["Status"]) != "FROZEN_COORDINATE_BRIDGE_NO_SCORING":
        raise ValueError("Source bridge is not frozen")
    if bool(source_summary["TargetResidualsUsed"]) or bool(source_summary["P5CV3OutcomeUsed"]):
        raise ValueError("Source bridge is not target-blind")
    validation = pd.read_csv(SOURCE_VALIDATION)
    if not bool(validation["Passed"].all()):
        raise ValueError("Source bridge validation did not pass")

    bridge = pd.read_csv(SOURCE_BRIDGE)
    rows = bridge[["EmpiricalRowID", "EmpiricalIndex", "FamilyID", "ClockIndex"]].drop_duplicates().sort_values("EmpiricalIndex")
    coords = list(dict.fromkeys(bridge["TauCoordinate"].astype(str).tolist()))
    mat = np.zeros((len(rows), len(coords)), dtype=float)
    row_index = {row_id: i for i, row_id in enumerate(rows["EmpiricalRowID"].astype(str))}
    coord_index = {coord: j for j, coord in enumerate(coords)}
    for _, rec in bridge.iterrows():
        mat[row_index[str(rec["EmpiricalRowID"])], coord_index[str(rec["TauCoordinate"])]] = float(rec["BridgeValue"])

    records = []
    for i, row in rows.iterrows():
        local_i = row_index[str(row["EmpiricalRowID"])]
        for coord, j in coord_index.items():
            records.append(
                {
                    "ProtocolID": PROTOCOL_ID,
                    "FreezeID": FREEZE_ID,
                    "EmpiricalRowID": row["EmpiricalRowID"],
                    "EmpiricalIndex": int(row["EmpiricalIndex"]),
                    "FamilyID": row["FamilyID"],
                    "ClockIndex": int(row["ClockIndex"]),
                    "TauCoordinate": coord,
                    "EmbeddingValue": float(mat[local_i, j]),
                    "SourceBridge": str(SOURCE_BRIDGE.relative_to(ROOT)),
                    "UsesTargetResiduals": False,
                    "UsesScoreOutcomes": False,
                    "ObjectConstructionAuthorized": False,
                    "ScoringAuthorized": False,
                    "ClaimBoundary": CLAIM_BOUNDARY,
                }
            )
    pd.DataFrame(records).to_csv(OUT_MATRIX, index=False)

    col_norms = np.linalg.norm(mat, axis=0)
    active = mat[:, col_norms > 0.0]
    rank = int(np.linalg.matrix_rank(mat))
    active_cols = int(active.shape[1])
    max_abs_corr = 0.0
    if active_cols > 1:
        corr = np.corrcoef(active.T) - np.eye(active_cols)
        max_abs_corr = float(np.max(np.abs(corr)))
    row_norm_min = float(np.min(np.linalg.norm(mat, axis=1)))
    row_norm_max = float(np.max(np.linalg.norm(mat, axis=1)))

    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": STATUS,
                "SourceFreezeID": str(source_summary["FreezeID"]),
                "EmpiricalRows": int(mat.shape[0]),
                "TauCoordinates": int(mat.shape[1]),
                "ActiveEmbeddingColumns": active_cols,
                "EmbeddingRank": rank,
                "MaxAbsActiveColumnCorrelation": max_abs_corr,
                "RowNormMin": row_norm_min,
                "RowNormMax": row_norm_max,
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

    manifest = {
        "ProtocolID": PROTOCOL_ID,
        "FreezeID": FREEZE_ID,
        "Status": STATUS,
        "SourceBridge": str(SOURCE_BRIDGE.relative_to(ROOT)),
        "SourceSummary": str(SOURCE_SUMMARY.relative_to(ROOT)),
        "SourceValidation": str(SOURCE_VALIDATION.relative_to(ROOT)),
        "MatrixFile": str(OUT_MATRIX.relative_to(ROOT)),
        "SummaryFile": str(OUT_SUMMARY.relative_to(ROOT)),
        "EmbeddingRule": "reuse_target_blind_epsilon_p3_coordinate_bridge_as_tccs_parent_to_score_embedding",
        "ObjectConstructionAuthorized": False,
        "ScoringAuthorized": False,
        "ClaimBoundary": CLAIM_BOUNDARY,
    }
    OUT_MANIFEST.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    OUT_SHA.write_text(
        "\n".join(
            f"{file_sha256(path)}  {path.relative_to(ROOT)}"
            for path in [OUT_MATRIX, OUT_SUMMARY, OUT_MANIFEST]
        )
        + "\n",
        encoding="utf-8",
    )
    OUT_DOC.write_text(
        f"""# P-TauCov TCCS Parent-To-Score Embedding

Freeze ID: `P_TAUCOV_TCCS_PARENT_SCORE_EMBEDDING_v1`

Status:

`{STATUS}`

## Purpose

This artifact freezes the parent-to-score embedding needed by the TCCS route.
It maps the 8-dimensional Tau-coordinate parent space into the 36-row
family-clock score geometry.

The embedding reuses the already validated target-blind coordinate bridge:

```text
{SOURCE_BRIDGE.relative_to(ROOT)}
```

It does not build the TCCS object and does not authorize scoring.

## Metrics

| Quantity | Value |
|---|---:|
| empirical rows | `{mat.shape[0]}` |
| Tau coordinates | `{mat.shape[1]}` |
| active embedding columns | `{active_cols}` |
| embedding rank | `{rank}` |
| max active-column abs correlation | `{max_abs_corr}` |
| row-norm min | `{row_norm_min}` |
| row-norm max | `{row_norm_max}` |

## Claim Boundary

Allowed statement:

> A target-blind parent-to-score embedding has been frozen for the TCCS route.

Forbidden statement:

> The embedding constructs a TCCS object, authorizes scoring, or produces a Tau signal.
""",
        encoding="utf-8",
    )
    print(STATUS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
