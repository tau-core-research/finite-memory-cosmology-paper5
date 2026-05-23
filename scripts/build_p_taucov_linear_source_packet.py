#!/usr/bin/env python3
"""Build the minimal target-blind P-TauCov linear-source packet."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
BASIS = ROOT / "data/p_taucov/linear/coordinate_basis.csv"
P_RED = ROOT / "data/p_taucov/linear/p_red.csv"
SOURCE_DIR = ROOT / "data/p_taucov/linear/source"
DOC = ROOT / "docs/p_taucov_linear_source_packet.md"
MANIFEST = ROOT / "evidence/p_taucov_linear_source_manifest.yaml"
SHA256 = ROOT / "evidence/p_taucov_linear_source.sha256"
LEAKAGE = ROOT / "evidence/p_taucov_linear_source_leakage_audit.csv"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
PACKET_ID = "P_TAUCOV_LINEAR_SOURCE_PACKET_v1_MINIMAL_BASELINE"

SOURCE_FILES = {
    "K_B": "K_B.csv",
    "Gamma_B": "Gamma_B.csv",
    "D_Phi_K_B": "D_Phi_K_B.csv",
    "D_Phi_J_B": "D_Phi_J_B.csv",
    "G_Phi": "G_Phi.csv",
    "G_B": "G_B.csv",
    "P0_SOURCE": "P0_source.csv",
}


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def zero_matrix(ids: list[str]) -> pd.DataFrame:
    rows = []
    for row_id in ids:
        row = {"coordinate_id": row_id}
        row.update({col_id: 0.0 for col_id in ids})
        rows.append(row)
    return pd.DataFrame(rows)


def write_matrix(path: Path, matrix: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    matrix.to_csv(path, index=False)


def main() -> int:
    if not BASIS.exists():
        raise FileNotFoundError(f"Missing coordinate basis: {BASIS}")
    if not P_RED.exists():
        raise FileNotFoundError(f"Missing P_red: {P_RED}")

    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    DOC.parent.mkdir(exist_ok=True)
    MANIFEST.parent.mkdir(exist_ok=True)

    basis = pd.read_csv(BASIS)
    ids = basis["coordinate_id"].astype(str).tolist()
    p_red = pd.read_csv(P_RED)
    expected_cols = ["coordinate_id"] + ids
    if list(p_red.columns) != expected_cols:
        raise ValueError("P_red columns do not match coordinate basis")

    zero = zero_matrix(ids)
    matrices = {
        "K_B": p_red.copy(),
        "Gamma_B": zero.copy(),
        "D_Phi_K_B": zero.copy(),
        "D_Phi_J_B": p_red.copy(),
        "G_Phi": p_red.copy(),
        "G_B": p_red.copy(),
        "P0_SOURCE": p_red.copy(),
    }

    written = {}
    for key, filename in SOURCE_FILES.items():
        path = SOURCE_DIR / filename
        write_matrix(path, matrices[key])
        written[key] = path

    hashes = {str(path.relative_to(ROOT)): file_sha256(path) for path in written.values()}
    SHA256.write_text("\n".join(f"{digest}  {path}" for path, digest in hashes.items()) + "\n", encoding="utf-8")

    manifest = {
        "ProtocolID": PROTOCOL_ID,
        "PacketID": PACKET_ID,
        "PacketType": "linear_source",
        "SourcePolicy": "minimal_target_blind_baseline_on_retained_reduced_domain",
        "SourceObjectsFrozen": True,
        "LinearObjectsDerivable": True,
        "MetricEvaluationAuthorized": False,
        "PTauCovScoringAuthorized": False,
        "OutcomeInformationUsed": False,
        "ResidualInformationUsed": False,
        "ScoreInformationUsed": False,
        "PostScoringLocalizationUsed": False,
        "CoordinateBasisFile": str(BASIS.relative_to(ROOT)),
        "PRedFile": str(P_RED.relative_to(ROOT)),
        "SourceFiles": {key: str(path.relative_to(ROOT)) for key, path in written.items()},
        "GeneratedUTC": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "ClaimBoundary": "minimal_linear_source_packet_no_metrics_no_scores",
    }
    MANIFEST.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")

    leakage = pd.DataFrame(
        [
            {
                "AuditID": "P_TAUCOV_LINEAR_SOURCE_LEAKAGE_AUDIT",
                "CheckID": "outcome_information_used",
                "Passed": True,
                "Required": True,
                "Evidence": "manifest OutcomeInformationUsed=false",
            },
            {
                "AuditID": "P_TAUCOV_LINEAR_SOURCE_LEAKAGE_AUDIT",
                "CheckID": "residual_information_used",
                "Passed": True,
                "Required": True,
                "Evidence": "manifest ResidualInformationUsed=false",
            },
            {
                "AuditID": "P_TAUCOV_LINEAR_SOURCE_LEAKAGE_AUDIT",
                "CheckID": "score_information_used",
                "Passed": True,
                "Required": True,
                "Evidence": "manifest ScoreInformationUsed=false",
            },
            {
                "AuditID": "P_TAUCOV_LINEAR_SOURCE_LEAKAGE_AUDIT",
                "CheckID": "post_scoring_localization_used",
                "Passed": True,
                "Required": True,
                "Evidence": "manifest PostScoringLocalizationUsed=false",
            },
            {
                "AuditID": "P_TAUCOV_LINEAR_SOURCE_LEAKAGE_AUDIT",
                "CheckID": "sources_are_minimal_baseline_conventions",
                "Passed": True,
                "Required": True,
                "Evidence": "K_B/D_Phi_J_B/G_Phi/G_B/P0_SOURCE=P_red; Gamma_B/D_Phi_K_B=0",
            },
        ]
    )
    leakage.to_csv(LEAKAGE, index=False)

    DOC.write_text(
        """# P-TauCov Linear-Source Packet

Status: minimal target-blind finite-dimensional source packet / no derived
linear objects / no metric evaluation / no scoring authorization.

This packet instantiates the frozen minimal source conventions on the retained
reduced domain:

```text
K_B        = P_red
Gamma_B    = 0
D_Phi_K_B  = 0
D_Phi_J_B  = P_red
G_Phi      = P_red
G_B        = P_red
P0_SOURCE  = P_red
```

These are baseline source conventions, not empirical evidence and not a
positive P-TauCov result.

## Claim Boundary

Allowed statement:

```text
Minimal target-blind finite-dimensional source objects are frozen.
```

Forbidden statement:

```text
Derived linear objects, covariance response, metric evaluation, or P-TauCov
score are available.
```
""",
        encoding="utf-8",
    )

    for path in list(written.values()) + [MANIFEST, SHA256, LEAKAGE, DOC]:
        print(f"Wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
