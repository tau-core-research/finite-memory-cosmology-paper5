#!/usr/bin/env python3
"""Build the target-blind P1 projection-response operator packet."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
BASIS = ROOT / "data/p_taucov/linear/coordinate_basis.csv"
P_RED = ROOT / "data/p_taucov/linear/p_red.csv"
P1 = ROOT / "data/p_taucov/linear/P1_projection_response_operator.csv"
DOC = ROOT / "docs/p_taucov_p1_projection_response_operator.md"
MANIFEST = ROOT / "evidence/p_taucov_p1_projection_response_operator_manifest.yaml"
SHA256 = ROOT / "evidence/p_taucov_p1_projection_response_operator.sha256"
METRICS = ROOT / "evidence/p_taucov_p1_projection_response_operator_metrics.csv"
LEAKAGE = ROOT / "evidence/p_taucov_p1_projection_response_operator_leakage_audit.csv"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
PACKET_ID = "P_TAUCOV_P1_PROJECTION_RESPONSE_OPERATOR_v1_MINIMAL_CHAIN"

PARENT_AXIS = "PHI_PARENT_SOURCE"
PROJECTION_AXIS = "P_MORPH_PROJECTION"
MORPHOLOGY_AXIS = "M_PARENT_MORPHOLOGY"


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def matrix_from_csv(path: Path, ids: list[str]) -> np.ndarray:
    df = pd.read_csv(path)
    if list(df.columns) != ["coordinate_id"] + ids:
        raise ValueError(f"Unexpected matrix columns in {path}")
    return df[ids].astype(float).to_numpy()


def main() -> int:
    for path in [BASIS, P_RED]:
        if not path.exists():
            raise FileNotFoundError(f"Missing required input: {path}")

    P1.parent.mkdir(parents=True, exist_ok=True)
    DOC.parent.mkdir(exist_ok=True)
    MANIFEST.parent.mkdir(exist_ok=True)

    basis = pd.read_csv(BASIS)
    ids = basis["coordinate_id"].astype(str).tolist()
    axis_to_id = dict(zip(basis["basis_axis"].astype(str), ids))
    required_axes = {PARENT_AXIS, PROJECTION_AXIS, MORPHOLOGY_AXIS}
    missing_axes = sorted(required_axes - set(axis_to_id))
    if missing_axes:
        raise ValueError("Missing required P1 axes: " + ", ".join(missing_axes))

    idx = {cid: i for i, cid in enumerate(ids)}
    p_parent = idx[axis_to_id[PARENT_AXIS]]
    p_projection = idx[axis_to_id[PROJECTION_AXIS]]
    p_morphology = idx[axis_to_id[MORPHOLOGY_AXIS]]

    p1 = np.zeros((len(ids), len(ids)), dtype=float)
    # Minimal projection response chain:
    # parent source -> projection coordinate -> morphology coordinate.
    # The 1/sqrt(2) normalization gives unit Frobenius norm for two links.
    weight = 1.0 / np.sqrt(2.0)
    p1[p_projection, p_parent] = weight
    p1[p_morphology, p_projection] = weight

    p1_df = pd.DataFrame(p1, columns=ids)
    p1_df.insert(0, "coordinate_id", ids)
    p1_df.to_csv(P1, index=False)

    p_red = matrix_from_csv(P_RED, ids)
    comm = p_red @ p1 - p1 @ p_red
    fro = float(np.linalg.norm(p1, ord="fro"))
    comm_fro = float(np.linalg.norm(comm, ord="fro"))
    diagonal_share = 0.0 if fro == 0.0 else float(np.linalg.norm(np.diag(np.diag(p1))) / fro)
    projection_axis_energy = float(
        np.linalg.norm(p1[p_projection, :]) ** 2 + np.linalg.norm(p1[:, p_projection]) ** 2
    )
    projection_axis_energy_share = 0.0 if fro == 0.0 else float(projection_axis_energy / (fro**2))

    metrics = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "PacketID": PACKET_ID,
                "MetricID": "P1_FROBENIUS_NORM",
                "MetricValue": fro,
                "Pass": abs(fro - 1.0) < 1e-12,
                "Threshold": "==1",
            },
            {
                "ProtocolID": PROTOCOL_ID,
                "PacketID": PACKET_ID,
                "MetricID": "P1_COMMUTATOR_WITH_P_RED_FROBENIUS",
                "MetricValue": comm_fro,
                "Pass": comm_fro > 0.0,
                "Threshold": ">0",
            },
            {
                "ProtocolID": PROTOCOL_ID,
                "PacketID": PACKET_ID,
                "MetricID": "P1_DIAGONAL_ENERGY_SHARE",
                "MetricValue": diagonal_share,
                "Pass": diagonal_share == 0.0,
                "Threshold": "==0",
            },
            {
                "ProtocolID": PROTOCOL_ID,
                "PacketID": PACKET_ID,
                "MetricID": "P1_PROJECTION_AXIS_ENERGY_SHARE",
                "MetricValue": projection_axis_energy_share,
                "Pass": projection_axis_energy_share >= 1.0,
                "Threshold": ">=1",
            },
        ]
    )
    metrics.to_csv(METRICS, index=False)

    manifest = {
        "ProtocolID": PROTOCOL_ID,
        "PacketID": PACKET_ID,
        "PacketType": "projection_response_operator",
        "Route": "epsilon_P_projection_response",
        "ConstructionRule": "minimal_target_blind_parent_projection_morphology_chain",
        "OperatorFile": str(P1.relative_to(ROOT)),
        "CoordinateBasisFile": str(BASIS.relative_to(ROOT)),
        "PRedFile": str(P_RED.relative_to(ROOT)),
        "ParentAxis": PARENT_AXIS,
        "ProjectionAxis": PROJECTION_AXIS,
        "MorphologyAxis": MORPHOLOGY_AXIS,
        "Normalization": "unit_frobenius_norm",
        "P1OperatorFrozen": True,
        "LinearModelPacketUpdated": False,
        "MetricEvaluationAuthorized": False,
        "PTauCovScoringAuthorized": False,
        "OutcomeInformationUsed": False,
        "ResidualInformationUsed": False,
        "ScoreInformationUsed": False,
        "P5CV3OutcomeUsed": False,
        "PostScoringLocalizationUsed": False,
        "GeneratedUTC": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "ClaimBoundary": "p1_projection_response_operator_frozen_no_model_packet_no_scoring",
    }
    MANIFEST.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")

    hash_paths = [P1, MANIFEST, METRICS]
    SHA256.write_text(
        "\n".join(f"{file_sha256(path)}  {path.relative_to(ROOT)}" for path in hash_paths) + "\n",
        encoding="utf-8",
    )

    leakage = pd.DataFrame(
        [
            {
                "AuditID": "P_TAUCOV_P1_PROJECTION_RESPONSE_OPERATOR_LEAKAGE_AUDIT",
                "CheckID": "outcome_information_used",
                "Passed": True,
                "Required": True,
                "Evidence": "manifest OutcomeInformationUsed=false",
            },
            {
                "AuditID": "P_TAUCOV_P1_PROJECTION_RESPONSE_OPERATOR_LEAKAGE_AUDIT",
                "CheckID": "residual_information_used",
                "Passed": True,
                "Required": True,
                "Evidence": "manifest ResidualInformationUsed=false",
            },
            {
                "AuditID": "P_TAUCOV_P1_PROJECTION_RESPONSE_OPERATOR_LEAKAGE_AUDIT",
                "CheckID": "score_information_used",
                "Passed": True,
                "Required": True,
                "Evidence": "manifest ScoreInformationUsed=false",
            },
            {
                "AuditID": "P_TAUCOV_P1_PROJECTION_RESPONSE_OPERATOR_LEAKAGE_AUDIT",
                "CheckID": "p5c_v3_outcome_used",
                "Passed": True,
                "Required": True,
                "Evidence": "manifest P5CV3OutcomeUsed=false",
            },
        ]
    )
    leakage.to_csv(LEAKAGE, index=False)

    DOC.write_text(
        """# P-TauCov P1 Projection-Response Operator

Status: target-blind minimal projection-response operator / no updated model
packet / no scoring authorization.

This packet freezes the first nonzero `epsilon_P` route after the strict-linear
negative gate. It defines a minimal projection-response operator from the
already frozen coordinate basis:

```text
parent source -> projection coordinate -> morphology coordinate
```

The construction uses only the declared axis roles:

```text
PHI_PARENT_SOURCE
P_MORPH_PROJECTION
M_PARENT_MORPHOLOGY
```

and assigns two normalized links:

```text
P1[P_MORPH_PROJECTION, PHI_PARENT_SOURCE] = 1/sqrt(2)
P1[M_PARENT_MORPHOLOGY, P_MORPH_PROJECTION] = 1/sqrt(2)
```

This is intentionally a structural projection-response perturbation. It is not
derived from target residuals, P5C v3 outcomes, family-localized score behavior,
or empirical covariance survival.

## Gate Metrics

The packet records only target-blind structural checks:

```text
unit Frobenius norm
nonzero commutator with P_red
zero diagonal energy
projection-axis support
```

## Claim Boundary

Allowed statement:

```text
A minimal target-blind P1 projection-response operator is frozen.
```

Forbidden statement:

```text
The P1 operator has produced a Tau signal, passed a covariance score, or
authorized empirical P-TauCov scoring.
```
""",
        encoding="utf-8",
    )

    for path in [P1, MANIFEST, SHA256, METRICS, LEAKAGE, DOC]:
        print(f"Wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
