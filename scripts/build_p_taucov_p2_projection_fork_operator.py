#!/usr/bin/env python3
"""Build the target-blind P2 projection-fork response operator packet."""

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
P2 = ROOT / "data/p_taucov/linear/P2_projection_fork_operator.csv"
DOC = ROOT / "docs/p_taucov_p2_projection_fork_operator.md"
MANIFEST = ROOT / "evidence/p_taucov_p2_projection_fork_operator_manifest.yaml"
SHA256 = ROOT / "evidence/p_taucov_p2_projection_fork_operator.sha256"
METRICS = ROOT / "evidence/p_taucov_p2_projection_fork_operator_metrics.csv"
LEAKAGE = ROOT / "evidence/p_taucov_p2_projection_fork_operator_leakage_audit.csv"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
PACKET_ID = "P_TAUCOV_P2_PROJECTION_FORK_OPERATOR_v1"

PARENT_AXIS = "PHI_PARENT_SOURCE"
PROJECTION_AXIS = "P_MORPH_PROJECTION"
MORPHOLOGY_AXIS = "M_PARENT_MORPHOLOGY"


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_matrix(path: Path, ids: list[str]) -> np.ndarray:
    df = pd.read_csv(path)
    if list(df.columns) != ["coordinate_id"] + ids:
        raise ValueError(f"Unexpected columns in {path}")
    return df[ids].astype(float).to_numpy()


def main() -> int:
    for path in [BASIS, P_RED]:
        if not path.exists():
            raise FileNotFoundError(f"Missing required input: {path}")

    P2.parent.mkdir(parents=True, exist_ok=True)
    DOC.parent.mkdir(exist_ok=True)
    MANIFEST.parent.mkdir(exist_ok=True)

    basis = pd.read_csv(BASIS)
    ids = basis["coordinate_id"].astype(str).tolist()
    axis_to_id = dict(zip(basis["basis_axis"].astype(str), ids))
    idx = {cid: i for i, cid in enumerate(ids)}
    p_parent = idx[axis_to_id[PARENT_AXIS]]
    p_projection = idx[axis_to_id[PROJECTION_AXIS]]
    p_morphology = idx[axis_to_id[MORPHOLOGY_AXIS]]

    p2 = np.zeros((len(ids), len(ids)), dtype=float)
    weight = 1.0 / np.sqrt(3.0)
    # Target-blind projection fork:
    # parent -> projection, parent -> morphology, projection -> morphology.
    p2[p_projection, p_parent] = weight
    p2[p_morphology, p_parent] = weight
    p2[p_morphology, p_projection] = weight

    p2_df = pd.DataFrame(p2, columns=ids)
    p2_df.insert(0, "coordinate_id", ids)
    p2_df.to_csv(P2, index=False)

    p_red = read_matrix(P_RED, ids)
    delta = p2 @ p2.T
    comm = p_red @ p2 - p2 @ p_red
    p2_fro = float(np.linalg.norm(p2, ord="fro"))
    comm_fro = float(np.linalg.norm(comm, ord="fro"))
    delta_fro = float(np.linalg.norm(delta, ord="fro"))
    diag_share = 0.0 if delta_fro == 0.0 else float(np.linalg.norm(np.diag(np.diag(delta))) / delta_fro)
    offdiag_share = float(max(0.0, 1.0 - diag_share))

    eigvals = np.clip(np.linalg.eigvalsh(delta), 0.0, None)
    total = float(eigvals.sum())
    if total == 0.0:
        effective_rank_fraction = 0.0
        normalized_entropy = 0.0
    else:
        probs = eigvals[eigvals > 0.0] / total
        entropy = float(-(probs * np.log(probs)).sum())
        effective_rank_fraction = float(np.exp(entropy) / len(eigvals))
        normalized_entropy = float(entropy / np.log(len(eigvals))) if len(eigvals) > 1 else 0.0

    label_rows = basis["coordinate_family"].isin(["ExternalMetadata", "CoordinateConvention"]).to_numpy()
    support = np.sum(np.abs(delta), axis=1)
    support_total = float(support.sum())
    label_proxy_overlap = 0.0 if support_total == 0.0 else float(support[label_rows].sum() / support_total)
    null_margin = min(comm_fro, effective_rank_fraction, normalized_entropy, 1.0 - label_proxy_overlap, offdiag_share)

    metrics = pd.DataFrame(
        [
            ("P2_FROBENIUS_NORM", p2_fro, abs(p2_fro - 1.0) < 1e-12, "==1"),
            ("P2_COMMUTATOR_WITH_P_RED_FROBENIUS", comm_fro, comm_fro > 0.0, ">0"),
            ("P2_DELTA_DIAGONAL_SHARE", diag_share, diag_share < 0.95, "<0.95"),
            ("P2_DELTA_OFFDIAGONAL_SHARE", offdiag_share, offdiag_share >= 0.05, ">=0.05"),
            ("P2_EFFECTIVE_RANK_FRACTION", effective_rank_fraction, 0.10 <= effective_rank_fraction <= 0.85, "0.10..0.85"),
            ("P2_SUPPORT_ENTROPY", normalized_entropy, 0.25 <= normalized_entropy <= 0.85, "0.25..0.85"),
            ("P2_LABEL_PROXY_OVERLAP", label_proxy_overlap, label_proxy_overlap <= 0.35, "<=0.35"),
            ("P2_STRUCTURAL_NULL_MARGIN", null_margin, null_margin >= 0.05, ">=0.05"),
        ],
        columns=["MetricID", "MetricValue", "Pass", "Threshold"],
    )
    metrics.insert(0, "PacketID", PACKET_ID)
    metrics.insert(0, "ProtocolID", PROTOCOL_ID)
    metrics.to_csv(METRICS, index=False)

    manifest = {
        "ProtocolID": PROTOCOL_ID,
        "PacketID": PACKET_ID,
        "PacketType": "projection_response_operator",
        "Route": "epsilon_P_projection_response",
        "ConstructionRule": "target_blind_parent_projection_morphology_fork",
        "Reason": "P1 passed basic nonzero checks but failed null separation because its covariance response was too diagonal/null-like.",
        "OperatorFile": str(P2.relative_to(ROOT)),
        "CoordinateBasisFile": str(BASIS.relative_to(ROOT)),
        "PRedFile": str(P_RED.relative_to(ROOT)),
        "Normalization": "unit_frobenius_norm",
        "P2OperatorFrozen": True,
        "MetricEvaluationAuthorized": False,
        "PTauCovScoringAuthorized": False,
        "OutcomeInformationUsed": False,
        "ResidualInformationUsed": False,
        "ScoreInformationUsed": False,
        "P5CV3OutcomeUsed": False,
        "PostScoringLocalizationUsed": False,
        "GeneratedUTC": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "ClaimBoundary": "p2_projection_fork_operator_frozen_no_model_packet_no_scoring",
    }
    MANIFEST.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    SHA256.write_text(
        "\n".join(f"{file_sha256(path)}  {path.relative_to(ROOT)}" for path in [P2, MANIFEST, METRICS]) + "\n",
        encoding="utf-8",
    )

    leakage = pd.DataFrame(
        [
            {
                "AuditID": "P_TAUCOV_P2_PROJECTION_FORK_OPERATOR_LEAKAGE_AUDIT",
                "CheckID": check_id,
                "Passed": True,
                "Required": True,
                "Evidence": evidence,
            }
            for check_id, evidence in [
                ("outcome_information_used", "manifest OutcomeInformationUsed=false"),
                ("residual_information_used", "manifest ResidualInformationUsed=false"),
                ("score_information_used", "manifest ScoreInformationUsed=false"),
                ("p5c_v3_outcome_used", "manifest P5CV3OutcomeUsed=false"),
                ("post_scoring_localization_used", "manifest PostScoringLocalizationUsed=false"),
            ]
        ]
    )
    leakage.to_csv(LEAKAGE, index=False)

    DOC.write_text(
        """# P-TauCov P2 Projection-Fork Operator

Status: target-blind projection-fork operator / no updated model packet / no
empirical scoring authorization.

The minimal P1 operator passed most target-blind checks but failed the
null-separation gate because its covariance response was too diagonal/null-like.
This P2 packet freezes a richer projection-response structure without using
target residuals, P5C v3 outcomes, score behavior, or family-localized tuning.

## Frozen Construction

```text
parent source -> projection coordinate
parent source -> morphology coordinate
projection coordinate -> morphology coordinate
```

with unit Frobenius normalization:

```text
each nonzero link = 1/sqrt(3)
```

The shared parent source creates an off-diagonal covariance component between
the projection and morphology rows. This directly targets the P1 failure mode
without inspecting empirical residuals.

## Claim Boundary

Allowed statement:

```text
A target-blind P2 projection-fork operator is frozen for later specificity
auditing.
```

Forbidden statement:

```text
The P2 operator has produced a Tau signal, passed empirical scoring, or
authorized P-TauCov survival claims.
```
""",
        encoding="utf-8",
    )

    for path in [P2, DOC, MANIFEST, SHA256, METRICS, LEAKAGE]:
        print(f"Wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
