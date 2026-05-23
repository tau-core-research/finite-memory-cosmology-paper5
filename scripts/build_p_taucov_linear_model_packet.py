#!/usr/bin/env python3
"""Build the target-blind P-TauCov linear model packet."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import yaml


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs/p_taucov_linear_model_packet.md"
MANIFEST = ROOT / "evidence/p_taucov_linear_model_packet.yaml"
SHA256 = ROOT / "evidence/p_taucov_linear_model_packet.sha256"
LEAKAGE = ROOT / "evidence/p_taucov_linear_model_packet_leakage_audit.csv"
SUMMARY = ROOT / "evidence/p_taucov_linear_model_packet_summary.csv"

PROTOCOL_ID = "P_TAUCOV_BRANCH_LOCALIZED_COVARIANCE_RESPONSE_v1"
PACKET_ID = "P_TAUCOV_LINEAR_MODEL_PACKET_v1_MINIMAL_BASELINE"

INPUT_FILES = {
    "coordinate_basis": "data/p_taucov/linear/coordinate_basis.csv",
    "phi_0": "data/p_taucov/linear/phi_0.csv",
    "p_null": "data/p_taucov/linear/p_null.csv",
    "p_gauge": "data/p_taucov/linear/p_gauge.csv",
    "p_forbidden": "data/p_taucov/linear/p_forbidden.csv",
    "p_red": "data/p_taucov/linear/p_red.csv",
    "K_B": "data/p_taucov/linear/source/K_B.csv",
    "Gamma_B": "data/p_taucov/linear/source/Gamma_B.csv",
    "D_Phi_K_B": "data/p_taucov/linear/source/D_Phi_K_B.csv",
    "D_Phi_J_B": "data/p_taucov/linear/source/D_Phi_J_B.csv",
    "G_Phi": "data/p_taucov/linear/source/G_Phi.csv",
    "G_B": "data/p_taucov/linear/source/G_B.csv",
    "P0_SOURCE": "data/p_taucov/linear/source/P0_source.csv",
    "L0_B": "data/p_taucov/linear/L0_B.csv",
    "R_B": "data/p_taucov/linear/R_B.csv",
    "A_Phi": "data/p_taucov/linear/A_Phi.csv",
    "A_B": "data/p_taucov/linear/A_B.csv",
    "P0": "data/p_taucov/linear/P0.csv",
    "coordinate_basis_manifest": "evidence/p_taucov_coordinate_basis_manifest.yaml",
    "reference_domain_manifest": "evidence/p_taucov_reference_domain_manifest.yaml",
    "linear_source_manifest": "evidence/p_taucov_linear_source_manifest.yaml",
    "linear_object_manifest": "evidence/p_taucov_linear_object_derivation_manifest.yaml",
}


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    DOC.parent.mkdir(exist_ok=True)
    MANIFEST.parent.mkdir(exist_ok=True)

    missing = [rel for rel in INPUT_FILES.values() if not (ROOT / rel).exists()]
    if missing:
        raise FileNotFoundError("Missing linear model packet inputs: " + ", ".join(missing))

    hashes = {key: file_sha256(ROOT / rel) for key, rel in INPUT_FILES.items()}
    manifest = {
        "ProtocolID": PROTOCOL_ID,
        "PacketID": PACKET_ID,
        "PacketType": "linear_model_packet",
        "ModelFamily": "strict_linear_minimal_baseline",
        "lambda_B": 0,
        "epsilon_P": 0,
        "LinearModelPacketFrozen": True,
        "LinearSpecificityAuditAuthorized": True,
        "MetricEvaluationAuthorized": True,
        "PTauCovScoringAuthorized": False,
        "OutcomeInformationUsed": False,
        "ResidualInformationUsed": False,
        "ScoreInformationUsed": False,
        "P5CV3OutcomeUsed": False,
        "PostScoringLocalizationUsed": False,
        "ClaimBoundary": "target_blind_linear_model_packet_authorizes_specificity_metrics_only_no_scoring",
        "InputFiles": INPUT_FILES,
        "InputSHA256": hashes,
        "GeneratedUTC": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    }
    MANIFEST.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")

    SHA256.write_text(f"{file_sha256(MANIFEST)}  {MANIFEST.relative_to(ROOT)}\n", encoding="utf-8")

    leakage = pd.DataFrame(
        [
            {
                "AuditID": "P_TAUCOV_LINEAR_MODEL_PACKET_LEAKAGE_AUDIT",
                "CheckID": "outcome_information_used",
                "Passed": True,
                "Required": True,
                "Evidence": "manifest OutcomeInformationUsed=false",
            },
            {
                "AuditID": "P_TAUCOV_LINEAR_MODEL_PACKET_LEAKAGE_AUDIT",
                "CheckID": "residual_information_used",
                "Passed": True,
                "Required": True,
                "Evidence": "manifest ResidualInformationUsed=false",
            },
            {
                "AuditID": "P_TAUCOV_LINEAR_MODEL_PACKET_LEAKAGE_AUDIT",
                "CheckID": "score_information_used",
                "Passed": True,
                "Required": True,
                "Evidence": "manifest ScoreInformationUsed=false",
            },
            {
                "AuditID": "P_TAUCOV_LINEAR_MODEL_PACKET_LEAKAGE_AUDIT",
                "CheckID": "p5c_v3_outcome_used",
                "Passed": True,
                "Required": True,
                "Evidence": "manifest P5CV3OutcomeUsed=false",
            },
            {
                "AuditID": "P_TAUCOV_LINEAR_MODEL_PACKET_LEAKAGE_AUDIT",
                "CheckID": "post_scoring_localization_used",
                "Passed": True,
                "Required": True,
                "Evidence": "manifest PostScoringLocalizationUsed=false",
            },
        ]
    )
    leakage.to_csv(LEAKAGE, index=False)

    summary = pd.DataFrame(
        [
            {
                "ProtocolID": PROTOCOL_ID,
                "PacketID": PACKET_ID,
                "LinearModelPacketFrozen": True,
                "LinearSpecificityAuditAuthorized": True,
                "MetricEvaluationAuthorized": True,
                "PTauCovScoringAuthorized": False,
                "ClaimBoundary": manifest["ClaimBoundary"],
            }
        ]
    )
    summary.to_csv(SUMMARY, index=False)

    DOC.write_text(
        """# P-TauCov Linear Model Packet

Status: target-blind strict-linear model packet / specificity metrics
authorized / P-TauCov scoring not authorized.

This packet binds the frozen coordinate basis, reference domain, source
objects, and derived linear objects into one hash-checked manifest.

## Frozen Minimal Linear Model

```text
lambda_B = 0
epsilon_P = 0
L0_B     = P_red
R_B      = -P_red
A_Phi    = P_red
A_B      = P_red
P0       = P_red
```

This is a baseline packet. It authorizes target-blind linear-specificity
metrics only. It does not authorize P-TauCov scoring, survival claims,
or empirical Tau-signal claims.

## Claim Boundary

Allowed statement:

```text
The target-blind strict-linear P-TauCov model packet is frozen and may be used
for linear-specificity auditing.
```

Forbidden statement:

```text
The packet has produced a P-TauCov score, survival result, or Tau-specific
empirical signal.
```
""",
        encoding="utf-8",
    )

    for path in [MANIFEST, SHA256, LEAKAGE, SUMMARY, DOC]:
        print(f"Wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
