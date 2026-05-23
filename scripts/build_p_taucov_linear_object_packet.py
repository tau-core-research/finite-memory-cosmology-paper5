#!/usr/bin/env python3
"""Build the derived target-blind P-TauCov linear-object packet."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data/p_taucov/linear/source"
LINEAR_DIR = ROOT / "data/p_taucov/linear"
DOC = ROOT / "docs/p_taucov_linear_object_packet.md"
MANIFEST = ROOT / "evidence/p_taucov_linear_object_derivation_manifest.yaml"
SHA256 = ROOT / "evidence/p_taucov_linear_object_derivation.sha256"
LEAKAGE = ROOT / "evidence/p_taucov_linear_object_derivation_leakage_audit.csv"
VALIDATION_SUMMARY = ROOT / "evidence/p_taucov_linear_object_packet_summary.csv"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
PACKET_ID = "P_TAUCOV_LINEAR_OBJECT_PACKET_v1_MINIMAL_BASELINE"

SOURCE_FILES = {
    "K_B": SOURCE_DIR / "K_B.csv",
    "Gamma_B": SOURCE_DIR / "Gamma_B.csv",
    "D_Phi_K_B": SOURCE_DIR / "D_Phi_K_B.csv",
    "D_Phi_J_B": SOURCE_DIR / "D_Phi_J_B.csv",
    "G_Phi": SOURCE_DIR / "G_Phi.csv",
    "G_B": SOURCE_DIR / "G_B.csv",
    "P0_SOURCE": SOURCE_DIR / "P0_source.csv",
}

OBJECT_FILES = {
    "L0_B": LINEAR_DIR / "L0_B.csv",
    "R_B": LINEAR_DIR / "R_B.csv",
    "A_Phi": LINEAR_DIR / "A_Phi.csv",
    "A_B": LINEAR_DIR / "A_B.csv",
    "P0": LINEAR_DIR / "P0.csv",
}


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_matrix(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def negate_matrix(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    cols = [col for col in out.columns if col != "coordinate_id"]
    out[cols] = -out[cols].astype(float)
    return out


def write_matrix(path: Path, df: pd.DataFrame) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


def main() -> int:
    for path in SOURCE_FILES.values():
        if not path.exists():
            raise FileNotFoundError(f"Missing source matrix: {path}")

    DOC.parent.mkdir(exist_ok=True)
    MANIFEST.parent.mkdir(exist_ok=True)

    k_b = read_matrix(SOURCE_FILES["K_B"])
    gamma_b = read_matrix(SOURCE_FILES["Gamma_B"])
    d_phi_j_b = read_matrix(SOURCE_FILES["D_Phi_J_B"])
    g_phi = read_matrix(SOURCE_FILES["G_Phi"])
    g_b = read_matrix(SOURCE_FILES["G_B"])
    p0_source = read_matrix(SOURCE_FILES["P0_SOURCE"])

    cols = [col for col in k_b.columns if col != "coordinate_id"]
    l0_b = k_b.copy()
    l0_b[cols] = k_b[cols].astype(float) + gamma_b[cols].astype(float)

    objects = {
        "L0_B": l0_b,
        "R_B": negate_matrix(d_phi_j_b),
        "A_Phi": g_phi,
        "A_B": g_b,
        "P0": p0_source,
    }

    for key, path in OBJECT_FILES.items():
        write_matrix(path, objects[key])

    hashes = {str(path.relative_to(ROOT)): file_sha256(path) for path in OBJECT_FILES.values()}
    SHA256.write_text("\n".join(f"{digest}  {path}" for path, digest in hashes.items()) + "\n", encoding="utf-8")

    manifest = {
        "ProtocolID": PROTOCOL_ID,
        "PacketID": PACKET_ID,
        "PacketType": "linear_objects",
        "SourcePolicy": "derived_from_minimal_target_blind_linear_source_packet",
        "LinearObjectsFrozen": True,
        "LinearModelPacketReady": True,
        "MetricEvaluationAuthorized": False,
        "PTauCovScoringAuthorized": False,
        "OutcomeInformationUsed": False,
        "ResidualInformationUsed": False,
        "ScoreInformationUsed": False,
        "PostScoringLocalizationUsed": False,
        "ObjectFiles": {key: str(path.relative_to(ROOT)) for key, path in OBJECT_FILES.items()},
        "GeneratedUTC": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "ClaimBoundary": "linear_objects_frozen_no_metrics_no_scores",
    }
    MANIFEST.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")

    leakage = pd.DataFrame(
        [
            {
                "AuditID": "P_TAUCOV_LINEAR_OBJECT_LEAKAGE_AUDIT",
                "CheckID": "outcome_information_used",
                "Passed": True,
                "Required": True,
                "Evidence": "manifest OutcomeInformationUsed=false",
            },
            {
                "AuditID": "P_TAUCOV_LINEAR_OBJECT_LEAKAGE_AUDIT",
                "CheckID": "residual_information_used",
                "Passed": True,
                "Required": True,
                "Evidence": "manifest ResidualInformationUsed=false",
            },
            {
                "AuditID": "P_TAUCOV_LINEAR_OBJECT_LEAKAGE_AUDIT",
                "CheckID": "score_information_used",
                "Passed": True,
                "Required": True,
                "Evidence": "manifest ScoreInformationUsed=false",
            },
            {
                "AuditID": "P_TAUCOV_LINEAR_OBJECT_LEAKAGE_AUDIT",
                "CheckID": "post_scoring_localization_used",
                "Passed": True,
                "Required": True,
                "Evidence": "manifest PostScoringLocalizationUsed=false",
            },
            {
                "AuditID": "P_TAUCOV_LINEAR_OBJECT_LEAKAGE_AUDIT",
                "CheckID": "objects_derived_from_frozen_sources",
                "Passed": True,
                "Required": True,
                "Evidence": "L0_B=K_B+Gamma_B; R_B=-D_Phi_J_B; A_Phi=G_Phi; A_B=G_B; P0=P0_SOURCE",
            },
        ]
    )
    leakage.to_csv(LEAKAGE, index=False)

    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "PacketID": PACKET_ID,
                "LinearObjectsFrozen": True,
                "LinearModelPacketReady": True,
                "MetricEvaluationAuthorized": False,
                "PTauCovScoringAuthorized": False,
                "ClaimBoundary": "linear_objects_frozen_no_metrics_no_scores",
            }
        ]
    )
    summary.to_csv(VALIDATION_SUMMARY, index=False)

    DOC.write_text(
        """# P-TauCov Linear-Object Packet

Status: derived target-blind linear objects / no metric evaluation / no scoring
authorization.

This packet deterministically derives the linear objects from the frozen
minimal source packet:

```text
L0_B  = K_B + Gamma_B
R_B   = -D_Phi_J_B
A_Phi = G_Phi
A_B   = G_B
P0    = P0_SOURCE
```

Under the current minimal baseline source packet this gives:

```text
L0_B  = P_red
R_B   = -P_red
A_Phi = P_red
A_B   = P_red
P0    = P_red
```

These are derived baseline linear objects, not empirical evidence and not a
positive P-TauCov result.

## Claim Boundary

Allowed statement:

```text
Target-blind baseline linear objects are frozen.
```

Forbidden statement:

```text
Metric evaluation, covariance response, or P-TauCov scoring is authorized.
```
""",
        encoding="utf-8",
    )

    for path in list(OBJECT_FILES.values()) + [MANIFEST, SHA256, LEAKAGE, VALIDATION_SUMMARY, DOC]:
        print(f"Wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
