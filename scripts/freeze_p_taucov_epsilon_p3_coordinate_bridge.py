#!/usr/bin/env python3
"""Freeze target-blind Tau-coordinate to empirical family-clock bridge."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
BASIS = ROOT / "data/p_taucov/linear/coordinate_basis.csv"
P5C_TARGET = ROOT / "data/physical_nulls/backreaction_reproduction/registered_protocol_guided_reproduction_backreaction_vector.csv"
P5C_MANIFEST = ROOT / "evidence/p5c_bstar_kernel_v3_manifest.yaml"
BRIDGE = ROOT / "evidence/p_taucov_epsilon_p3_coordinate_bridge.csv"
SUMMARY = ROOT / "evidence/p_taucov_epsilon_p3_coordinate_bridge_summary.csv"
MANIFEST = ROOT / "evidence/p_taucov_epsilon_p3_coordinate_bridge.yaml"
SHA256 = ROOT / "evidence/p_taucov_epsilon_p3_coordinate_bridge.sha256"
DOC = ROOT / "docs/p_taucov_epsilon_p3_coordinate_bridge.md"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
FREEZE_ID = "P_TAUCOV_EPSILON_P3_COORDINATE_BRIDGE_v1"
CLAIM_BOUNDARY = "epsilon_p3_coordinate_bridge_frozen_no_empirical_scoring"


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def clock_block(clock_index: int) -> str:
    if clock_index < 4:
        return "protected"
    if clock_index < 8:
        return "active"
    return "null"


def normalize(values: np.ndarray) -> np.ndarray:
    norm = float(np.linalg.norm(values))
    if norm == 0.0:
        return values
    return values / norm


def main() -> int:
    for path in [BASIS, P5C_TARGET, P5C_MANIFEST]:
        if not path.exists():
            raise FileNotFoundError(f"Missing bridge input: {path.relative_to(ROOT)}")

    basis = pd.read_csv(BASIS)
    ids = basis["coordinate_id"].astype(str).tolist()
    manifest = yaml.safe_load(P5C_MANIFEST.read_text(encoding="utf-8")) or {}
    config = manifest.get("config", {})
    branch_signs = {str(k): float(v) for k, v in config.get("branch_signs", {}).items()}
    sector_weights = {str(k): float(v) for k, v in config.get("sector_weights", {}).items()}
    rows = pd.read_csv(P5C_TARGET).sort_values(["FamilyID", "z", "SampleID"]).reset_index(drop=True)
    rows["ClockIndex"] = rows.groupby("FamilyID").cumcount()
    rows["RowID"] = [f"{family}::z_{z:.6g}" for family, z in zip(rows["FamilyID"], rows["z"])]

    family = rows["FamilyID"].astype(str)
    clock_index = rows["ClockIndex"].astype(int).to_numpy()
    theta = 2.0 * np.pi * clock_index / 12.0
    sector = np.array([clock_block(int(idx)) for idx in clock_index], dtype=object)
    bsign = family.map(branch_signs).fillna(0.0).to_numpy(float)
    sweights = np.array([sector_weights.get(str(s), 0.0) for s in sector], dtype=float)

    feature_by_axis = {
        "PHI_PARENT_SOURCE": np.ones(len(rows), dtype=float),
        "B_BRANCH_RESPONSE": bsign,
        "M_PARENT_MORPHOLOGY": sweights,
        "P_MORPH_PROJECTION": bsign * sweights * np.cos(theta),
    }
    records = []
    bridge_matrix = np.zeros((len(rows), len(ids)), dtype=float)
    for j, coord_id in enumerate(ids):
        axis = str(basis.loc[basis["coordinate_id"].astype(str).eq(coord_id), "basis_axis"].iloc[0])
        raw = feature_by_axis.get(axis, np.zeros(len(rows), dtype=float))
        values = normalize(raw)
        bridge_matrix[:, j] = values
        for i, row in rows.iterrows():
            records.append(
                {
                    "ProtocolID": PROTOCOL_ID,
                    "FreezeID": FREEZE_ID,
                    "EmpiricalRowID": row["RowID"],
                    "EmpiricalIndex": int(i),
                    "FamilyID": row["FamilyID"],
                    "ClockIndex": int(row["ClockIndex"]),
                    "TauCoordinate": coord_id,
                    "TauBasisAxis": axis,
                    "BridgeValue": float(values[i]),
                    "RawFeatureValue": float(raw[i]),
                    "FeatureRule": feature_by_axis.get(axis) is not None,
                    "UsesTargetResiduals": False,
                    "UsesP5Cv3Outcome": False,
                    "PTauCovScoringAuthorized": False,
                    "ClaimBoundary": CLAIM_BOUNDARY,
                }
            )
    pd.DataFrame(records).to_csv(BRIDGE, index=False)

    rank = int(np.linalg.matrix_rank(bridge_matrix))
    col_norms = np.linalg.norm(bridge_matrix, axis=0)
    active_cols = int(np.sum(col_norms > 0.0))
    max_abs_corr = 0.0
    active = bridge_matrix[:, col_norms > 0.0]
    if active.shape[1] > 1:
        corr = np.corrcoef(active.T)
        corr = corr - np.eye(corr.shape[0])
        max_abs_corr = float(np.max(np.abs(corr)))
    status = "FROZEN_COORDINATE_BRIDGE_NO_SCORING" if rank >= 3 and active_cols == 4 else "BLOCKED"
    pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "FreezeID": FREEZE_ID,
                "Status": status,
                "EmpiricalRows": len(rows),
                "TauCoordinates": len(ids),
                "ActiveBridgeColumns": active_cols,
                "BridgeRank": rank,
                "MaxAbsActiveColumnCorrelation": max_abs_corr,
                "TargetResidualsUsed": False,
                "P5CV3OutcomeUsed": False,
                "PTauCovScoringAuthorized": False,
                "ClaimBoundary": CLAIM_BOUNDARY,
            }
        ]
    ).to_csv(SUMMARY, index=False)
    out_manifest = {
        "ProtocolID": PROTOCOL_ID,
        "FreezeID": FREEZE_ID,
        "Status": status,
        "BridgeFile": str(BRIDGE.relative_to(ROOT)),
        "SummaryFile": str(SUMMARY.relative_to(ROOT)),
        "BridgeRule": "metadata_only_family_sign_clock_sector_phase_features_from_frozen_p5c_v3_manifest",
        "EmpiricalRows": len(rows),
        "TauCoordinates": len(ids),
        "ActiveBridgeColumns": active_cols,
        "BridgeRank": rank,
        "TargetResidualsUsed": False,
        "P5CV3OutcomeUsed": False,
        "PTauCovScoringAuthorized": False,
        "InputFiles": {
            "coordinate_basis": str(BASIS.relative_to(ROOT)),
            "p5c_target_rows": str(P5C_TARGET.relative_to(ROOT)),
            "p5c_v3_manifest": str(P5C_MANIFEST.relative_to(ROOT)),
        },
        "InputSHA256": {
            "coordinate_basis": file_sha256(BASIS),
            "p5c_target_rows": file_sha256(P5C_TARGET),
            "p5c_v3_manifest": file_sha256(P5C_MANIFEST),
        },
        "GeneratedUTC": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "ClaimBoundary": CLAIM_BOUNDARY,
    }
    MANIFEST.write_text(yaml.safe_dump(out_manifest, sort_keys=False), encoding="utf-8")
    SHA256.write_text(
        "\n".join(f"{file_sha256(path)}  {path.relative_to(ROOT)}" for path in [BRIDGE, SUMMARY, MANIFEST]) + "\n",
        encoding="utf-8",
    )
    DOC.write_text(
        f"""# P-TauCov Epsilon-P3 Coordinate Bridge

Status: `{status}`.

This artifact freezes a target-blind bridge from the 8-dimensional P-TauCov
Tau-coordinate basis to the 36-row empirical family-clock grid used by the
P5C covariance scorecard family.

The bridge uses only metadata and frozen P5C v3 manifest conventions:

```text
PHI_PARENT_SOURCE      -> constant source feature
B_BRANCH_RESPONSE     -> frozen branch-sign feature
M_PARENT_MORPHOLOGY   -> frozen clock-sector weight
P_MORPH_PROJECTION    -> branch-sign * sector-weight * cos(clock phase)
other coordinates     -> zero
```

It does not use target residuals, P5C v3 gain patterns, OOS DeltaNLL values, or
family-localized outcome information.

## Metrics

```text
EmpiricalRows: {len(rows)}
TauCoordinates: {len(ids)}
ActiveBridgeColumns: {active_cols}
BridgeRank: {rank}
MaxAbsActiveColumnCorrelation: {max_abs_corr:.12g}
PTauCovScoringAuthorized: false
```

Allowed statement:

```text
A target-blind coordinate bridge has been frozen for epsilon-P3 P-TauCov.
```

Forbidden statement:

```text
The bridge has produced an empirical Tau signal or authorizes scoring by
itself.
```
""",
        encoding="utf-8",
    )
    for path in [BRIDGE, SUMMARY, MANIFEST, SHA256, DOC]:
        print(f"Wrote {path.relative_to(ROOT)}")
    if status != "FROZEN_COORDINATE_BRIDGE_NO_SCORING":
        print("P_TAUCOV_EPSILON_P3_COORDINATE_BRIDGE_BLOCKED")
        return 1
    print("P_TAUCOV_EPSILON_P3_COORDINATE_BRIDGE_FROZEN_NO_SCORING")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
